import stripe
import boto3
import os
from datetime import datetime

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
dynamodb = boto3.resource('dynamodb')
usage_table = dynamodb.Table(os.getenv('USAGE_TABLE', 'api-usage'))

PRICING_PLANS = {
    "free": {"limit": 100, "price": 0},
    "starter": {"limit": 5000, "price": 29, "price_id": "price_starter"},
    "pro": {"limit": 50000, "price": 99, "price_id": "price_pro"},
    "enterprise": {"limit": 1000000, "price": 499, "price_id": "price_enterprise"}
}

def create_customer(email: str, user_id: str):
    """Create Stripe customer"""
    customer = stripe.Customer.create(email=email, metadata={"user_id": user_id})
    return customer.id

def create_subscription(customer_id: str, plan: str):
    """Create subscription for a plan"""
    price_id = PRICING_PLANS[plan]["price_id"]
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
        metadata={"plan": plan}
    )
    return subscription

def upgrade_plan(user_id: str, new_plan: str):
    """Upgrade user to new plan"""
    usage_table.update_item(
        Key={'user_id': user_id},
        UpdateExpression='SET plan = :plan, #limit = :limit, updated_at = :time',
        ExpressionAttributeNames={'#limit': 'limit'},
        ExpressionAttributeValues={
            ':plan': new_plan,
            ':limit': PRICING_PLANS[new_plan]['limit'],
            ':time': datetime.utcnow().isoformat()
        }
    )

def track_usage(api_key: str, units: int = 1):
    """Track API usage for billing"""
    usage_table.update_item(
        Key={'api_key': api_key},
        UpdateExpression='SET usage = usage + :inc',
        ExpressionAttributeValues={':inc': units}
    )
