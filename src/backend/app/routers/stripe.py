"""
Stripe payment router for subscription management.
"""
import stripe
from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel
from typing import Optional, Literal

from app.core.config import get_settings
from app.core.supabase import get_supabase_client
from app.routers.auth import get_auth_user

router = APIRouter()
settings = get_settings()

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Price IDs for different plans (test mode by default)
PRICE_IDS = {
    "starter": {
        "monthly": "price_1OExampleStarterMonthly",  # Replace with actual Stripe price ID
        "yearly": "price_1OExampleStarterYearly",   # Replace with actual Stripe price ID
    },
    "pro": {
        "monthly": "price_1OExampleProMonthly",    # Replace with actual Stripe price ID
        "yearly": "price_1OExampleProYearly",      # Replace with actual Stripe price ID
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


def get_or_create_stripe_customer(user_id: str, email: str, full_name: Optional[str] = None) -> str:
    """Get existing Stripe customer or create a new one."""
    supabase = get_supabase_client()
    
    # Check if user already has a Stripe customer ID
    result = supabase.table("profiles").select("stripe_customer_id").eq("id", user_id).single().execute()
    
    if result.data and result.data.get("stripe_customer_id"):
        return result.data["stripe_customer_id"]
    
    # Create new Stripe customer
    customer = stripe.Customer.create(
        email=email,
        name=full_name or email,
        metadata={
            "user_id": user_id,
        }
    )
    
    # Store the customer ID in the database
    supabase.table("profiles").update({
        "stripe_customer_id": customer.id
    }).eq("id", user_id).execute()
    
    return customer.id


@router.post("/stripe/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    user=Depends(get_auth_user)
):
    """Create a Stripe Checkout session for subscription."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured"
        )
    
    try:
        # Get or create Stripe customer
        customer_id = get_or_create_stripe_customer(
            user_id=str(user.id),
            email=user.email,
            full_name=user.user_metadata.get("full_name") if hasattr(user, "user_metadata") else None
        )
        
        # Get price ID for the selected plan
        price_id = PRICE_IDS.get(request.plan, {}).get(request.billing_cycle)
        if not price_id:
            # For testing, create a checkout with a dynamic price
            # In production, use predefined price IDs
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan or billing cycle: {request.plan}/{request.billing_cycle}"
            )
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
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
            }
        )
        
        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.get("/stripe/subscription")
async def get_subscription_status(user=Depends(get_auth_user)):
    """Get current user's subscription status from Stripe."""
    if not settings.STRIPE_SECRET_KEY:
        # Return local subscription info if Stripe not configured
        supabase = get_supabase_client()
        result = supabase.table("profiles").select(
            "subscription_tier, monthly_usage_count, monthly_usage_limit"
        ).eq("id", str(user.id)).single().execute()
        
        if result.data:
            return {
                "status": "active" if result.data.get("subscription_tier") != "free" else "inactive",
                "plan": result.data.get("subscription_tier", "free"),
                "stripe_connected": False,
            }
        return {"status": "inactive", "plan": "free", "stripe_connected": False}
    
    try:
        # Get user's Stripe customer ID
        supabase = get_supabase_client()
        result = supabase.table("profiles").select("stripe_customer_id").eq("id", str(user.id)).single().execute()
        
        customer_id = result.data.get("stripe_customer_id") if result.data else None
        
        if not customer_id:
            return {"status": "inactive", "plan": "free", "stripe_connected": True}
        
        # Get active subscriptions
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status="active",
            limit=1
        )
        
        if subscriptions.data:
            sub = subscriptions.data[0]
            # Get plan name from metadata or price
            plan = sub.metadata.get("plan", "pro")
            
            return {
                "id": sub.id,
                "status": sub.status,
                "plan": plan,
                "current_period_end": sub.current_period_end,
                "cancel_at_period_end": sub.cancel_at_period_end,
                "stripe_connected": True,
            }
        
        return {"status": "inactive", "plan": "free", "stripe_connected": True}
        
    except Exception as e:
        # Fallback to local data
        supabase = get_supabase_client()
        result = supabase.table("profiles").select(
            "subscription_tier"
        ).eq("id", str(user.id)).single().execute()
        
        plan = result.data.get("subscription_tier", "free") if result.data else "free"
        return {"status": "active" if plan != "free" else "inactive", "plan": plan, "stripe_connected": False}


@router.post("/stripe/portal")
async def create_portal_session(request: Request, user=Depends(get_auth_user)):
    """Create a Stripe Customer Portal session for managing subscription."""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe is not configured"
        )
    
    try:
        # Get user's Stripe customer ID
        supabase = get_supabase_client()
        result = supabase.table("profiles").select("stripe_customer_id").eq("id", str(user.id)).single().execute()
        
        customer_id = result.data.get("stripe_customer_id") if result.data else None
        
        if not customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No subscription found"
            )
        
        # Create portal session
        origin = request.headers.get('origin', 'http://localhost:3000')
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{origin}/settings"
        )
        
        return PortalSessionResponse(url=session.url)
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook secret not configured"
        )
    
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
    
    # Handle the event
    supabase = get_supabase_client()
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        plan = session.get("metadata", {}).get("plan", "pro")
        
        if user_id:
            # Update user's subscription tier and status
            supabase.table("profiles").update({
                "subscription_tier": plan,
                "subscription_status": "active",
                "monthly_usage_limit": 1000 if plan == "pro" else 100,  # Adjust limits based on plan
                "updated_at": "now()"
            }).eq("id", user_id).execute()
    
    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        subscription_id = invoice.get("subscription")
        
        if subscription_id:
            # Subscription renewed, ensure status is active
            subscription = stripe.Subscription.retrieve(subscription_id)
            user_id = subscription.metadata.get("user_id")
            plan = subscription.metadata.get("plan", "pro")
            
            if user_id:
                supabase.table("profiles").update({
                    "subscription_tier": plan,
                    "subscription_status": "active",
                    "updated_at": "now()"
                }).eq("id", user_id).execute()
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        user_id = subscription.metadata.get("user_id")
        
        if user_id:
            # Downgrade to free tier and mark as canceled
            supabase.table("profiles").update({
                "subscription_tier": "free",
                "subscription_status": "canceled",
                "monthly_usage_limit": 10,  # Free tier limit
                "updated_at": "now()"
            }).eq("id", user_id).execute()
    
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        user_id = subscription.metadata.get("user_id")
        sub_status = subscription.get("status")
        
        if user_id:
            if sub_status == "canceled":
                # Subscription canceled at period end
                supabase.table("profiles").update({
                    "subscription_status": "canceled",
                    "updated_at": "now()"
                }).eq("id", user_id).execute()
            elif sub_status == "unpaid":
                # Payment failed - mark as past_due
                supabase.table("profiles").update({
                    "subscription_status": "past_due",
                    "updated_at": "now()"
                }).eq("id", user_id).execute()
            elif sub_status == "active":
                plan = subscription.metadata.get("plan", "pro")
                supabase.table("profiles").update({
                    "subscription_tier": plan,
                    "subscription_status": "active",
                    "updated_at": "now()"
                }).eq("id", user_id).execute()
    
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        subscription_id = invoice.get("subscription")
        
        if subscription_id:
            subscription = stripe.Subscription.retrieve(subscription_id)
            user_id = subscription.metadata.get("user_id")
            
            if user_id:
                # Mark subscription as past_due
                supabase.table("profiles").update({
                    "subscription_status": "past_due",
                    "updated_at": "now()"
                }).eq("id", user_id).execute()
    
    return {"status": "success"}


# Test endpoint for verifying Stripe configuration
@router.get("/stripe/config")
async def get_stripe_config():
    """Get Stripe configuration for frontend."""
    publishable_key = settings.STRIPE_SECRET_KEY
    if publishable_key and publishable_key.startswith("sk_"):
        # Convert secret key to publishable key pattern for test mode
        if "test" in publishable_key:
            publishable_key = "pk_test_..."  # Frontend should use NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
        else:
            publishable_key = "pk_live_..."
    
    return {
        "is_configured": bool(settings.STRIPE_SECRET_KEY),
        "test_mode": settings.STRIPE_SECRET_KEY and "test" in settings.STRIPE_SECRET_KEY if settings.STRIPE_SECRET_KEY else True,
    }
