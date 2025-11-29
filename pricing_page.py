import streamlit as st
import stripe
import os

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def show_pricing_page():
    st.title("💰 Pricing Plans")
    st.markdown("### Transform Your Unstructured Data into AI-Ready Insights")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        ### Free
        **$0/month**
        - 100 documents/month
        - Basic API access
        - JSON output
        - Community support
        """)
        if st.button("Start Free", key="free"):
            st.info("Sign up to get started!")
    
    with col2:
        st.markdown("""
        ### Starter
        **$29/month**
        - 5,000 documents/month
        - Full API access
        - All output formats
        - Email support
        - Embeddings included
        """)
        if st.button("Subscribe", key="starter"):
            create_checkout_session("starter")
    
    with col3:
        st.markdown("""
        ### Pro
        **$99/month**
        - 50,000 documents/month
        - Priority processing
        - Custom chunking
        - Webhook support
        - Priority support
        """)
        if st.button("Subscribe", key="pro"):
            create_checkout_session("pro")
    
    with col4:
        st.markdown("""
        ### Enterprise
        **$499/month**
        - 1M documents/month
        - Dedicated infrastructure
        - Custom integrations
        - SLA guarantee
        - 24/7 support
        """)
        if st.button("Contact Sales", key="enterprise"):
            st.info("Contact: sales@yourdomain.com")

def create_checkout_session(plan: str):
    """Create Stripe checkout session"""
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': f'price_{plan}',
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://yourdomain.com/success',
            cancel_url='https://yourdomain.com/pricing',
        )
        st.markdown(f"[Complete Payment]({checkout_session.url})")
    except Exception as e:
        st.error(f"Error: {e}")
