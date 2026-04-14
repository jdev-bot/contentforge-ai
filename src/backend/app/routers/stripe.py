"""
Stripe payment router for subscription management.
"""

import logging
from typing import Literal, Optional

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.supabase import get_supabase_admin_client, get_supabase_client
from app.routers.auth import get_auth_user
from app.tasks.email import send_invoice_receipt_task

router = APIRouter()
settings = get_settings()

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Price IDs for different plans (test mode by default)
# These should be replaced with actual Stripe price IDs from your dashboard
PRICE_IDS = {
    "starter": {
        "monthly": "price_1OExampleStarterMonthly",
        "yearly": "price_1OExampleStarterYearly",
    },
    "pro": {
        "monthly": "price_1OExampleProMonthly",
        "yearly": "price_1OExampleProYearly",
    },
}


class CreateCheckoutRequest(BaseModel):
    plan: Literal["starter", "pro"]
    billing_cycle: Literal["monthly", "yearly"] = "monthly"
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    session_id: str
    url: str


class SubscriptionStatusResponse(BaseModel):
    id: str
    status: str
    plan: str
    current_period_end: Optional[int] = None
    cancel_at_period_end: bool = False


class PortalSessionResponse(BaseModel):
    url: str


def get_or_create_stripe_customer(
    user_id: str, email: str, full_name: Optional[str] = None
) -> str:
    """Get existing Stripe customer or create a new one."""
    supabase = get_supabase_client()

    # Check if user already has a Stripe customer ID
    result = (
        supabase.table("profiles")
        .select("stripe_customer_id")
        .eq("id", user_id)
        .single()
        .execute()
    )

    if result.data and result.data.get("stripe_customer_id"):
        customer_id = result.data["stripe_customer_id"]
        try:
            # Verify customer exists in Stripe
            stripe.Customer.retrieve(customer_id)
            return customer_id
        except stripe.error.InvalidRequestError:
            # Customer was deleted in Stripe, create new one
            pass

    # Create new Stripe customer
    customer = stripe.Customer.create(
        email=email,
        name=full_name or email,
        metadata={
            "user_id": user_id,
        },
    )

    # Store the customer ID in the database
    supabase.table("profiles").update({"stripe_customer_id": customer.id}).eq(
        "id", user_id
    ).execute()

    return customer.id


def get_price_id_for_plan(plan: str, billing_cycle: str) -> Optional[str]:
    """Get the Stripe price ID for a plan."""
    # In production, fetch from environment or database
    # For now, use configured price IDs or return None
    price_id = PRICE_IDS.get(plan, {}).get(billing_cycle)
    if price_id and not price_id.startswith("price_1OExample"):
        return price_id
    return None


def get_plan_from_price_id(price_id: str) -> str:
    """Determine plan from price ID."""
    # Reverse lookup - in production, store mapping in database
    for plan, cycles in PRICE_IDS.items():
        for cycle, pid in cycles.items():
            if pid == price_id:
                return plan
    return "pro"  # Default to pro if unknown


@router.post("/stripe/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest, user=Depends(get_auth_user)
):
    """Create a Stripe Checkout session for subscription."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )

    try:
        # Get or create Stripe customer
        customer_id = get_or_create_stripe_customer(
            user_id=str(user.id),
            email=user.email,
            full_name=(
                user.user_metadata.get("full_name")
                if hasattr(user, "user_metadata")
                else None
            ),
        )

        # Get price ID for the selected plan
        price_id = get_price_id_for_plan(request.plan, request.billing_cycle)

        line_items = []
        if price_id:
            # Use predefined price
            line_items = [
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ]
        else:
            # Create dynamic price for testing/demo
            # In production, you should always use predefined prices
            amount = 1900 if request.plan == "starter" else 4900
            if request.billing_cycle == "yearly":
                amount = amount * 10  # ~17% discount for yearly

            line_items = [
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"ContentForge {request.plan.capitalize()}",
                            "description": f"{request.billing_cycle.capitalize()} subscription",
                        },
                        "unit_amount": amount,
                        "recurring": {
                            "interval": (
                                "year" if request.billing_cycle == "yearly" else "month"
                            )
                        },
                    },
                    "quantity": 1,
                }
            ]

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=line_items,
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                "user_id": str(user.id),
                "plan": request.plan,
            },
            subscription_data={
                "metadata": {
                    "user_id": str(user.id),
                    "plan": request.plan,
                }
            },
            allow_promotion_codes=True,
            automatic_tax={"enabled": True},
            customer_update={
                "address": "auto",
                "name": "auto",
            },
        )

        return CheckoutSessionResponse(session_id=session.id, url=session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}",
        )


@router.get("/stripe/subscription")
async def get_subscription_status(user=Depends(get_auth_user)):
    """Get current user's subscription status from Stripe."""
    if not settings.STRIPE_SECRET_KEY:
        # Return local subscription info if Stripe not configured
        supabase = get_supabase_client()
        result = (
            supabase.table("profiles")
            .select(
                "subscription_tier, subscription_status, monthly_usage_count, monthly_usage_limit, subscription_period_end"
            )
            .eq("id", str(user.id))
            .single()
            .execute()
        )

        if result.data:
            return {
                "status": result.data.get("subscription_status", "inactive"),
                "plan": result.data.get("subscription_tier", "free"),
                "stripe_connected": False,
                "monthly_usage_count": result.data.get("monthly_usage_count", 0),
                "monthly_usage_limit": result.data.get("monthly_usage_limit", 10),
                "subscription_period_end": result.data.get("subscription_period_end"),
            }
        return {
            "status": "inactive",
            "plan": "free",
            "stripe_connected": False,
            "monthly_usage_count": 0,
            "monthly_usage_limit": 10,
        }

    try:
        # Get user's Stripe customer ID
        supabase = get_supabase_client()
        result = (
            supabase.table("profiles")
            .select(
                "stripe_customer_id, subscription_tier, subscription_status, monthly_usage_count, monthly_usage_limit"
            )
            .eq("id", str(user.id))
            .single()
            .execute()
        )

        customer_id = result.data.get("stripe_customer_id") if result.data else None
        local_plan = (
            result.data.get("subscription_tier", "free") if result.data else "free"
        )
        local_status = (
            result.data.get("subscription_status", "inactive")
            if result.data
            else "inactive"
        )

        if not customer_id:
            return {
                "status": local_status,
                "plan": local_plan,
                "stripe_connected": True,
                "monthly_usage_count": (
                    result.data.get("monthly_usage_count", 0) if result.data else 0
                ),
                "monthly_usage_limit": (
                    result.data.get("monthly_usage_limit", 10) if result.data else 10
                ),
            }

        # Get active subscriptions
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="all",  # Get all statuses to handle past_due, etc.
            limit=1,
            expand=["data.default_payment_method"],
        )

        if subscriptions.data:
            sub = subscriptions.data[0]
            # Get plan name from metadata or price
            plan = sub.metadata.get("plan") or get_plan_from_price_id(
                sub.items.data[0].price.id if sub.items.data else ""
            )

            # Map Stripe status to our status
            stripe_status = sub.status
            our_status = "active"
            if stripe_status == "canceled":
                our_status = "canceled"
            elif stripe_status == "past_due":
                our_status = "past_due"
            elif stripe_status == "unpaid":
                our_status = "past_due"
            elif stripe_status in ["incomplete", "incomplete_expired"]:
                our_status = "inactive"

            return {
                "id": sub.id,
                "status": our_status,
                "plan": plan,
                "current_period_end": sub.current_period_end,
                "cancel_at_period_end": sub.cancel_at_period_end,
                "stripe_connected": True,
                "stripe_status": stripe_status,
                "monthly_usage_count": (
                    result.data.get("monthly_usage_count", 0) if result.data else 0
                ),
                "monthly_usage_limit": (
                    100 if plan == "starter" else (1000 if plan == "pro" else 10)
                ),
            }

        # No active subscription found, return free tier
        return {
            "status": local_status if local_status != "active" else "inactive",
            "plan": local_plan if local_plan != "free" else "free",
            "stripe_connected": True,
            "monthly_usage_count": (
                result.data.get("monthly_usage_count", 0) if result.data else 0
            ),
            "monthly_usage_limit": (
                result.data.get("monthly_usage_limit", 10) if result.data else 10
            ),
        }

    except Exception as e:
        logger.error(f"Error fetching subscription: {e}")
        # Fallback to local data
        supabase = get_supabase_client()
        result = (
            supabase.table("profiles")
            .select(
                "subscription_tier, subscription_status, monthly_usage_count, monthly_usage_limit"
            )
            .eq("id", str(user.id))
            .single()
            .execute()
        )

        plan = result.data.get("subscription_tier", "free") if result.data else "free"
        sub_status = (
            result.data.get("subscription_status", "inactive")
            if result.data
            else "inactive"
        )
        return {
            "status": sub_status,
            "plan": plan,
            "stripe_connected": False,
            "monthly_usage_count": (
                result.data.get("monthly_usage_count", 0) if result.data else 0
            ),
            "monthly_usage_limit": (
                result.data.get("monthly_usage_limit", 10) if result.data else 10
            ),
        }


@router.post("/stripe/portal")
async def create_portal_session(request: Request, user=Depends(get_auth_user)):
    """Create a Stripe Customer Portal session for managing subscription."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )

    try:
        # Get user's Stripe customer ID
        supabase = get_supabase_client()
        result = (
            supabase.table("profiles")
            .select("stripe_customer_id")
            .eq("id", str(user.id))
            .single()
            .execute()
        )

        customer_id = result.data.get("stripe_customer_id") if result.data else None

        if not customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No subscription found"
            )

        # Create portal session
        origin = request.headers.get("origin", "http://localhost:3000")
        session = stripe.billing_portal.Session.create(
            customer=customer_id, return_url=f"{origin}/settings?tab=subscription"
        )

        return PortalSessionResponse(url=session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating portal: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("Webhook secret not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook secret not configured",
        )

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        logger.error("Missing stripe-signature header")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing signature header"
        )

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        logger.info(f"Received webhook event: {event['type']}")
    except ValueError as e:
        logger.error(f"Invalid webhook payload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
        )
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid webhook signature: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Webhook error"
        )

    # Handle the event
    supabase = get_supabase_client()

    event_type = event["type"]
    data_object = event["data"]["object"]

    try:
        # ============================================================
        # PAYMENT INTENT EVENTS
        # ============================================================

        if event_type == "payment_intent.succeeded":
            payment_intent = data_object
            user_id = payment_intent.get("metadata", {}).get("user_id")

            if user_id:
                logger.info(f"Payment succeeded for user {user_id}")
                # Payment succeeded - subscription will be handled by subscription events
                # This is mostly for one-time payments

        elif event_type == "payment_intent.payment_failed":
            payment_intent = data_object
            user_id = payment_intent.get("metadata", {}).get("user_id")

            if user_id:
                logger.warning(f"Payment failed for user {user_id}")
                # Payment failed - update status
                supabase.table("profiles").update(
                    {"subscription_status": "past_due", "updated_at": "now()"}
                ).eq("id", user_id).execute()

        # ============================================================
        # CHECKOUT SESSION EVENTS
        # ============================================================

        elif event_type == "checkout.session.completed":
            session = data_object
            user_id = session.get("metadata", {}).get("user_id")
            plan = session.get("metadata", {}).get("plan", "pro")

            if user_id:
                logger.info(f"Checkout completed for user {user_id}, plan: {plan}")
                # Update user's subscription tier and status
                monthly_limit = 100 if plan == "starter" else 1000
                supabase.table("profiles").update(
                    {
                        "subscription_tier": plan,
                        "subscription_status": "active",
                        "monthly_usage_limit": monthly_limit,
                        "stripe_customer_id": session.get("customer"),
                        "updated_at": "now()",
                    }
                ).eq("id", user_id).execute()

        # ============================================================
        # SUBSCRIPTION EVENTS
        # ============================================================

        elif event_type == "customer.subscription.created":
            subscription = data_object
            user_id = subscription.get("metadata", {}).get("user_id")
            plan = subscription.get("metadata", {}).get("plan", "pro")

            if user_id:
                logger.info(f"Subscription created for user {user_id}, plan: {plan}")
                monthly_limit = 100 if plan == "starter" else 1000
                supabase.table("profiles").update(
                    {
                        "subscription_tier": plan,
                        "subscription_status": "active",
                        "monthly_usage_limit": monthly_limit,
                        "stripe_subscription_id": subscription.get("id"),
                        "subscription_period_end": subscription.get(
                            "current_period_end"
                        ),
                        "updated_at": "now()",
                    }
                ).eq("id", user_id).execute()

        elif event_type == "customer.subscription.updated":
            subscription = data_object
            user_id = subscription.get("metadata", {}).get("user_id")
            sub_status = subscription.get("status")

            if user_id:
                logger.info(
                    f"Subscription updated for user {user_id}, status: {sub_status}"
                )

                # Get plan from metadata or items
                plan = subscription.get("metadata", {}).get("plan")
                if not plan and subscription.get("items", {}).get("data"):
                    plan = get_plan_from_price_id(
                        subscription["items"]["data"][0]["price"]["id"]
                    )
                plan = plan or "pro"

                # Map Stripe status to our status
                if sub_status == "canceled":
                    our_status = "canceled"
                elif sub_status == "past_due":
                    our_status = "past_due"
                elif sub_status == "unpaid":
                    our_status = "past_due"
                elif sub_status == "active":
                    our_status = "active"
                else:
                    our_status = "inactive"

                monthly_limit = 100 if plan == "starter" else 1000
                supabase.table("profiles").update(
                    {
                        "subscription_tier": plan if our_status == "active" else "free",
                        "subscription_status": our_status,
                        "monthly_usage_limit": (
                            monthly_limit if our_status == "active" else 10
                        ),
                        "subscription_period_end": subscription.get(
                            "current_period_end"
                        ),
                        "cancel_at_period_end": subscription.get(
                            "cancel_at_period_end", False
                        ),
                        "updated_at": "now()",
                    }
                ).eq("id", user_id).execute()

        elif event_type == "customer.subscription.deleted":
            subscription = data_object
            user_id = subscription.get("metadata", {}).get("user_id")

            if user_id:
                logger.info(f"Subscription deleted for user {user_id}")
                # Downgrade to free tier
                supabase.table("profiles").update(
                    {
                        "subscription_tier": "free",
                        "subscription_status": "canceled",
                        "monthly_usage_limit": 10,
                        "stripe_subscription_id": None,
                        "subscription_period_end": None,
                        "updated_at": "now()",
                    }
                ).eq("id", user_id).execute()

        # ============================================================
        # INVOICE EVENTS
        # ============================================================

        elif event_type == "invoice.payment_succeeded":
            invoice = data_object
            subscription_id = invoice.get("subscription")

            if subscription_id:
                # Get subscription to find user
                subscription = stripe.Subscription.retrieve(subscription_id)
                user_id = subscription.metadata.get("user_id")
                plan = subscription.metadata.get("plan", "pro")

                if user_id:
                    logger.info(f"Invoice payment succeeded for user {user_id}")
                    # Subscription renewed, ensure status is active
                    monthly_limit = 100 if plan == "starter" else 1000
                    supabase.table("profiles").update(
                        {
                            "subscription_tier": plan,
                            "subscription_status": "active",
                            "monthly_usage_limit": monthly_limit,
                            "subscription_period_end": subscription.get(
                                "current_period_end"
                            ),
                            "updated_at": "now()",
                        }
                    ).eq("id", user_id).execute()

        elif event_type == "invoice.payment_failed":
            invoice = data_object
            subscription_id = invoice.get("subscription")

            if subscription_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                user_id = subscription.metadata.get("user_id")

                if user_id:
                    logger.warning(f"Invoice payment failed for user {user_id}")
                    # Mark subscription as past_due
                    supabase.table("profiles").update(
                        {"subscription_status": "past_due", "updated_at": "now()"}
                    ).eq("id", user_id).execute()

        elif event_type == "invoice.paid":
            invoice = data_object
            subscription_id = invoice.get("subscription")

            if subscription_id:
                subscription = stripe.Subscription.retrieve(subscription_id)
                user_id = subscription.metadata.get("user_id")

                if user_id:
                    logger.info(f"Invoice paid for user {user_id}")
                    # Ensure subscription is active
                    supabase.table("profiles").update(
                        {"subscription_status": "active", "updated_at": "now()"}
                    ).eq("id", user_id).execute()

                    # Send invoice receipt email
                    try:
                        # Get user profile for email
                        user_result = (
                            supabase.table("profiles")
                            .select("email, full_name")
                            .eq("id", user_id)
                            .single()
                            .execute()
                        )

                        if user_result.data:
                            user_email = user_result.data.get("email")
                            user_name = user_result.data.get("full_name", "")
                            plan = subscription.metadata.get("plan", "pro")

                            # Format amount
                            amount_cents = invoice.get("amount_paid", 0)
                            amount = f"${amount_cents / 100:.2f}"

                            # Get billing period
                            period_start = invoice.get("period_start")
                            period_end = invoice.get("period_end")
                            billing_period = "Monthly"
                            if period_start and period_end:
                                from datetime import datetime

                                start = datetime.fromtimestamp(period_start)
                                end = datetime.fromtimestamp(period_end)
                                days = (end - start).days
                                if days > 31:
                                    billing_period = "Yearly"

                            send_invoice_receipt_task.delay(
                                user_id=user_id,
                                email=user_email,
                                user_name=user_name,
                                invoice_number=invoice.get("number", "N/A"),
                                amount=amount,
                                plan_name=plan.capitalize(),
                                billing_period=billing_period,
                                stripe_invoice_id=invoice.get("id"),
                            )
                    except Exception as email_err:
                        logger.error(f"Failed to queue invoice receipt: {email_err}")

        # ============================================================
        # CUSTOMER EVENTS
        # ============================================================

        elif event_type == "customer.updated":
            customer = data_object
            # Could update customer info in database if needed
            pass

        elif event_type == "customer.deleted":
            customer = data_object
            # Find user by customer ID and clear their stripe_customer_id
            result = (
                supabase.table("profiles")
                .select("id")
                .eq("stripe_customer_id", customer.get("id"))
                .execute()
            )
            if result.data:
                for row in result.data:
                    supabase.table("profiles").update(
                        {
                            "stripe_customer_id": None,
                            "stripe_subscription_id": None,
                            "subscription_tier": "free",
                            "subscription_status": "inactive",
                            "updated_at": "now()",
                        }
                    ).eq("id", row["id"]).execute()

        else:
            logger.info(f"Unhandled webhook event type: {event_type}")

        return {"status": "success", "event_type": event_type}

    except Exception as e:
        logger.error(f"Error processing webhook {event_type}: {e}")
        # Still return 200 to Stripe so they don't retry indefinitely
        # Log the error for monitoring
        return {"status": "error", "event_type": event_type, "error": str(e)}


# Test endpoint for verifying Stripe configuration
@router.get("/stripe/config")
async def get_stripe_config():
    """Get Stripe configuration for frontend."""
    is_configured = bool(settings.STRIPE_SECRET_KEY)
    test_mode = False

    if is_configured and settings.STRIPE_SECRET_KEY:
        # Check if using test mode keys
        test_mode = settings.STRIPE_SECRET_KEY.startswith("sk_test_")

    return {
        "is_configured": is_configured,
        "test_mode": test_mode,
    }


@router.post("/stripe/sync")
async def sync_subscription(user=Depends(get_auth_user)):
    """Force sync subscription status from Stripe to local database."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured",
        )

    try:
        supabase = get_supabase_client()
        result = (
            supabase.table("profiles")
            .select("stripe_customer_id")
            .eq("id", str(user.id))
            .single()
            .execute()
        )

        customer_id = result.data.get("stripe_customer_id") if result.data else None

        if not customer_id:
            return {"synced": False, "message": "No Stripe customer found"}

        # Get subscriptions from Stripe
        subscriptions = stripe.Subscription.list(
            customer=customer_id, status="all", limit=1
        )

        if subscriptions.data:
            sub = subscriptions.data[0]
            plan = sub.metadata.get("plan", "pro")

            supabase.table("profiles").update(
                {
                    "subscription_tier": plan if sub.status == "active" else "free",
                    "subscription_status": (
                        "active" if sub.status == "active" else sub.status
                    ),
                    "stripe_subscription_id": sub.id,
                    "subscription_period_end": sub.current_period_end,
                    "updated_at": "now()",
                }
            ).eq("id", str(user.id)).execute()

            return {
                "synced": True,
                "subscription": {
                    "id": sub.id,
                    "status": sub.status,
                    "plan": plan,
                    "current_period_end": sub.current_period_end,
                },
            }
        else:
            # No subscription found, reset to free
            supabase.table("profiles").update(
                {
                    "subscription_tier": "free",
                    "subscription_status": "inactive",
                    "stripe_subscription_id": None,
                    "subscription_period_end": None,
                    "updated_at": "now()",
                }
            ).eq("id", str(user.id)).execute()

            return {
                "synced": True,
                "message": "No active subscription found, reset to free",
            }

    except Exception as e:
        logger.error(f"Error syncing subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync subscription: {str(e)}",
        )
