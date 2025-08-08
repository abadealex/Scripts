# api/v1/billing.py
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('billing', __name__, url_prefix='/billing')

@bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    event = request.json
    # Here you'd validate the Stripe webhook signature and process the event
    # Dummy response for demo:
    return jsonify({'message': 'Webhook received', 'event_type': event.get('type')}), 200

@bp.route('/plans', methods=['GET'])
def get_plans():
    # Return dummy plan data
    plans = [
        {'id': 'free', 'name': 'Free Plan', 'price': 0},
        {'id': 'pro', 'name': 'Pro Plan', 'price': 1999},  # price in cents
    ]
    return jsonify(plans)

