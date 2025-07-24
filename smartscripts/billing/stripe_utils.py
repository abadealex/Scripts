# billing/stripe_utils.py
import stripe
import os

# Load your Stripe secret key from env
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(customer_id, price_id, success_url, cancel_url):
    return stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=success_url,
        cancel_url=cancel_url,
    )

def get_customer_portal_session(customer_id, return_url):
    return stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )

def retrieve_event(payload, sig_header, endpoint_secret):
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        return event
    except (ValueError, stripe.error.SignatureVerificationError):
        return None
