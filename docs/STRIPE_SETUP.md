# Stripe Payment Integration Setup Guide

Complete guide for setting up Stripe payments in ContentForge AI.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Create Stripe Account](#create-stripe-account)
3. [Configure Test Mode](#configure-test-mode)
4. [Set Up Products and Prices](#set-up-products-and-prices)
5. [Configure Webhooks](#configure-webhooks)
6. [Test Mode vs Live Mode](#test-mode-vs-live-mode)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

1. Create a [Stripe account](https://dashboard.stripe.com/register)
2. Get your API keys from the Stripe Dashboard
3. Set up products and prices
4. Configure webhook endpoint
5. Update environment variables
6. Test with Stripe CLI

---

## Create Stripe Account

### Step 1: Sign Up

1. Go to [https://dashboard.stripe.com/register](https://dashboard.stripe.com/register)
2. Complete the registration process
3. Verify your email address
4. Activate your account (required for live mode)

### Step 2: Get API Keys

1. Go to **Developers** → **API keys** in the Stripe Dashboard
2. You'll see two sets of keys:
   - **Test keys**: For development (safe to use)
   - **Live keys**: For production (real money)

3. Copy the following:
   - `Publishable key` (starts with `pk_test_` or `pk_live_`)
   - `Secret key` (starts with `sk_test_` or `sk_live_`)

**⚠️ SECURITY WARNING**: Never commit secret keys to git or expose them in frontend code.

---

## Configure Test Mode

Test mode allows you to test payments without real money.

### Test Card Numbers

Use these card numbers for testing:

| Card Number | Scenario |
|-------------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Card declined |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0000 0000 9987` | Lost card |
| `4000 0000 0000 9979` | Stolen card |

**Use any:**
- Future expiration date (e.g., 12/30)
- Any 3-digit CVC (e.g., 123)
- Any ZIP code (e.g., 12345)

### Testing 3D Secure

For cards requiring 3D Secure authentication:
- `4000 0025 0000 3155` - Requires authentication, then succeeds
- `4000 0027 6000 3184` - Requires authentication, then fails

---

## Set Up Products and Prices

### Step 1: Create Products

1. Go to **Products** in the Stripe Dashboard
2. Click **+ Add product**
3. Create two products:
   - **Starter Plan**
     - Name: "ContentForge Starter"
     - Description: "Perfect for content creators and small teams"
   - **Pro Plan**
     - Name: "ContentForge Pro"
     - Description: "For growing teams with advanced needs"

### Step 2: Add Prices

For each product, add pricing:

**Starter Plan:**
- Monthly: $19/month
- Yearly: $190/year (17% discount)

**Pro Plan:**
- Monthly: $49/month
- Yearly: $490/year (17% discount)

**Important**: Set billing period to "Recurring" for subscriptions.

### Step 3: Copy Price IDs

After creating prices, copy the Price IDs:
- They look like: `price_1Oxxxxx...`
- You'll need these for environment variables

---

## Configure Webhooks

Webhooks allow Stripe to notify your application of payment events.

### Local Development (with Stripe CLI)

1. **Install Stripe CLI:**
   ```bash
   # macOS
   brew install stripe/stripe-cli/stripe

   # Linux
   wget https://github.com/stripe/stripe-cli/releases/latest/download/stripe_linux_x86_64.tar.gz
   tar -xvf stripe_linux_x86_64.tar.gz
   sudo mv stripe /usr/local/bin/

   # Windows
   # Download from: https://github.com/stripe/stripe-cli/releases
   ```

2. **Login to Stripe:**
   ```bash
   stripe login
   ```

3. **Forward webhooks to your local server:**
   ```bash
   stripe listen --forward-to http://localhost:8000/api/v1/stripe/webhook
   ```

4. **Copy the webhook secret** displayed and add to `.env`:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxx
   ```

### Production Webhooks

1. Go to **Developers** → **Webhooks** in Stripe Dashboard
2. Click **+ Add endpoint**
3. Enter your production URL:
   ```
   https://your-api-domain.com/api/v1/stripe/webhook
   ```
4. Select events to listen for:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`

5. Copy the **Webhook signing secret** and add to production environment variables.

---

## Test Mode vs Live Mode

### Test Mode

**Characteristics:**
- Uses test API keys (`pk_test_`, `sk_test_`)
- No real money is charged
- Use test card numbers
- Shows "Test Mode" banner in application
- Safe for development and testing

**How to switch:**
1. Use test keys in environment variables
2. Stripe dashboard shows "Test mode" toggle (on)

### Live Mode

**Characteristics:**
- Uses live API keys (`pk_live_`, `sk_live_`)
- Real money is charged
- Requires activated Stripe account
- Bank account required for payouts
- Subject to Stripe's fees (2.9% + 30¢ per transaction)

**How to switch:**
1. Activate your Stripe account (requires business verification)
2. Switch to live keys in environment variables
3. Update webhook endpoints to production URL

**⚠️ Before going live:**
1. Test thoroughly in test mode
2. Complete Stripe account activation
3. Configure business details
4. Set up bank account for payouts
5. Review and accept Stripe's terms

---

## Production Deployment

### 1. Set Environment Variables

Add these to your production environment:

```bash
# Stripe Live Keys (after account activation)
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxx
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxx

# Price IDs (from Stripe Dashboard)
STRIPE_PRICE_STARTER_MONTHLY=price_xxxxxxxx
STRIPE_PRICE_STARTER_YEARLY=price_xxxxxxxx
STRIPE_PRICE_PRO_MONTHLY=price_xxxxxxxx
STRIPE_PRICE_PRO_YEARLY=price_xxxxxxxx
```

### 2. Configure Production Webhooks

1. Set up webhook endpoint in Stripe Dashboard
2. Point to: `https://your-api.com/api/v1/stripe/webhook`
3. Select all required events (see Webhooks section)
4. Test webhook delivery

### 3. Verify HTTPS

Stripe requires HTTPS for webhooks and checkout redirects.

### 4. Test Live Mode

Before launching:
1. Make a small test payment with a real card
2. Verify subscription is created
3. Check database updates
4. Test cancellation flow
5. Verify refund capability

---

## Testing the Integration

### Automated Tests

Run the included tests:

```bash
# Backend tests
cd src/backend
python -m pytest tests/test_stripe_webhooks.py -v

# Or run all tests
pytest
```

### Manual Testing Checklist

- [ ] Create checkout session
- [ ] Complete payment with test card
- [ ] Verify subscription created in database
- [ ] Check webhook events received
- [ ] Verify usage limits updated
- [ ] Test subscription cancellation
- [ ] Test failed payment handling
- [ ] Test portal session creation
- [ ] Verify email notifications (if configured)

### Testing Webhooks Locally

```bash
# Terminal 1: Start backend
./run-local.sh

# Terminal 2: Forward webhooks
stripe listen --forward-to http://localhost:8000/api/v1/stripe/webhook

# Terminal 3: Trigger test events
stripe trigger checkout.session.completed
stripe trigger invoice.payment_succeeded
stripe trigger customer.subscription.deleted
```

---

## Troubleshooting

### Common Issues

#### "Invalid API Key"
- Check that keys are correctly copied
- Ensure no extra spaces
- Verify using test keys in development

#### "Webhook signature verification failed"
- Check `STRIPE_WEBHOOK_SECRET` is set correctly
- Ensure webhook secret matches the endpoint
- For local testing, use the secret from `stripe listen`

#### "No such price"
- Verify Price IDs in environment variables
- Check that prices exist in Stripe Dashboard
- Ensure you're using the correct environment (test/live)

#### Checkout session not redirecting
- Check browser console for errors
- Verify `success_url` and `cancel_url` are valid URLs
- Ensure URLs use HTTPS in production

#### Subscription not updating after payment
- Check webhook events are being received
- Verify webhook handler is processing events
- Check server logs for errors
- Test with Stripe CLI: `stripe trigger checkout.session.completed`

### Debug Mode

Enable Stripe debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Support](https://support.stripe.com/)
- [Stripe Discord](https://stripe.com/go/developer-chat)
- Check Stripe Dashboard → Logs for detailed error information

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Rotate keys** periodically
4. **Restrict webhook IPs** to Stripe's IP ranges (optional)
5. **Verify webhook signatures** always
6. **Use HTTPS** for all webhook endpoints
7. **Log and monitor** all payment events

---

## Additional Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/checkout)
- [Stripe Billing Documentation](https://stripe.com/docs/billing)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Testing Stripe Integration](https://stripe.com/docs/testing)

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `STRIPE_SECRET_KEY` | Yes | Server-side secret key |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Yes | Client-side publishable key |
| `STRIPE_WEBHOOK_SECRET` | Yes | Webhook endpoint secret |
| `STRIPE_PRICE_STARTER_MONTHLY` | Yes | Price ID for Starter monthly |
| `STRIPE_PRICE_STARTER_YEARLY` | Yes | Price ID for Starter yearly |
| `STRIPE_PRICE_PRO_MONTHLY` | Yes | Price ID for Pro monthly |
| `STRIPE_PRICE_PRO_YEARLY` | Yes | Price ID for Pro yearly |
