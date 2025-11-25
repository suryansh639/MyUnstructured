import streamlit as st
from streamlit_google_auth import Authenticate

def get_authenticator():
    """Initialize and return authenticator"""
    return Authenticate(
        secret_credentials_path=None,
        cookie_name='doc_processor_auth',
        cookie_key='random_key_12345',
        redirect_uri='https://atlas.13-232-91-199.nip.io',
    )

def is_authenticated():
    """Check if user is logged in"""
    authenticator = get_authenticator()
    user_info = authenticator.check_authentification()
    return user_info is not None

def get_user_info():
    """Get current user information"""
    authenticator = get_authenticator()
    return authenticator.check_authentification()

def show_auth_dialog():
    """Show authentication dialog as modal"""
    st.markdown("""
    <style>
    .auth-modal {
        position: fixed;
        z-index: 9999;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.7);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .auth-content {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        max-width: 500px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .auth-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #333;
    }
    .auth-subtitle {
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-content">', unsafe_allow_html=True)
        st.markdown("### Get more done, Everyday.")
        st.markdown("Create your account to get started")
        st.markdown("---")
        
        authenticator = get_authenticator()
        authenticator.login()
        
        st.markdown('</div>', unsafe_allow_html=True)

def logout():
    """Logout current user"""
    authenticator = get_authenticator()
    authenticator.logout()

def show_user_profile_sidebar():
    """Show user profile in sidebar if authenticated"""
    user_info = get_user_info()
    
    if user_info:
        with st.sidebar:
            st.markdown("---")
            if user_info.get('picture'):
                st.image(user_info['picture'], width=60)
            st.markdown(f"**{user_info.get('name', 'User')}**")
            st.caption(user_info.get('email', ''))
            
            if st.button("Logout", use_container_width=True):
                logout()
                st.rerun()
