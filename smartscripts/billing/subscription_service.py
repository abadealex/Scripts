# billing/subscription_service.py
from billing.stripe_utils import retrieve_event
from flask import current_app
import logging

# Simulated local DB (replace with actual persistence)
subscriptions = {}

def handle_webhook_event(payload, sig_header, endpoint_secret):
    event = retrieve_event(payload, sig_header, endpoint_secret)
    if not event:
        return None

    event_type = event['type']
    data = event['data']['object']

    if event_type == 'customer.subscription.created':
        subscriptions[data['id']] = {
            'status': data['status'],
            'customer_id': data['customer'],
            'plan': data['items']['data'][0]['price']['id'],
        }
    elif event_type == 'customer.subscription.deleted':
        subscriptions.pop(data['id'], None)
    elif event_type == 'invoice.paid':
        logging.info(f"Invoice paid for {data['customer']}")

    return event_type  # For debugging/logging

def get_subscription_status(customer_id):
    return next((s for s in subscriptions.values() if s['customer_id'] == customer_id), None)
