import streamlit as st
import requests

# AWS Configuration
API_ENDPOINT = "https://i4a8p9jm70.execute-api.us-east-1.amazonaws.com/prod"
USER_POOL_CLIENT_ID = "lq7a32rt0stetm9sfdljnhs3b"
COGNITO_ENDPOINT = "https://cognito-idp.us-east-1.amazonaws.com/"

def cognito_login(email, password):
    """Login with AWS Cognito"""
    try:
        response = requests.post(
            COGNITO_ENDPOINT,
            headers={
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth'
            },
            json={
                'AuthFlow': 'USER_PASSWORD_AUTH',
                'ClientId': USER_POOL_CLIENT_ID,
                'AuthParameters': {
                    'USERNAME': email,
                    'PASSWORD': password
                }
            }
        )
        data = response.json()
        
        if 'AuthenticationResult' in data:
            return data['AuthenticationResult']['IdToken'], None
        else:
            return None, data.get('message', 'Login failed')
    except Exception as e:
        return None, str(e)

def register_user(email, password, name):
    """Register new user"""
    try:
        response = requests.post(
            f"{API_ENDPOINT}/v1/register",
            headers={'Content-Type': 'application/json'},
            json={'email': email, 'password': password, 'name': name}
        )
        data = response.json()
        return data, None if response.ok else data.get('error', 'Registration failed')
    except Exception as e:
        return None, str(e)

def verify_email(email, code):
    """Verify email with code"""
    try:
        response = requests.post(
            COGNITO_ENDPOINT,
            headers={
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target': 'AWSCognitoIdentityProviderService.ConfirmSignUp'
            },
            json={
                'ClientId': USER_POOL_CLIENT_ID,
                'Username': email,
                'ConfirmationCode': code
            }
        )
        return response.status_code == 200, None if response.status_code == 200 else 'Invalid code'
    except Exception as e:
        return False, str(e)

def get_credits(token):
    """Get user credits from API"""
    try:
        response = requests.get(
            f"{API_ENDPOINT}/v1/credits",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        return data.get('credits', 0), data.get('email', ''), data.get('name', '')
    except Exception as e:
        return 0, '', ''

def process_document_with_credit(token, file_content, filename):
    """Process document and automatically deduct credit"""
    try:
        import base64
        base64_file = base64.b64encode(file_content).decode('utf-8')
        response = requests.post(
            f"{API_ENDPOINT}/v1/process",
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={
                'file': base64_file,
                'filename': filename
            }
        )
        data = response.json()
        
        # Update credits in session
        if 'credits_remaining' in data:
            st.session_state.credits = data['credits_remaining']
        
        return data, None
    except Exception as e:
        return None, str(e)

def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def show_auth_dialog():
    """Show login/register/verify dialog"""
    st.markdown('<h1 style="text-align: center; color: #667eea;">🚀 DocuAI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6c757d; font-size: 1.2rem;">Transform Unstructured Documents to AI-Ready Data</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "✉️ Verify Email"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="your@email.com")
            password = st.text_input("🔒 Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if email and password:
                    with st.spinner("Logging in..."):
                        token, error = cognito_login(email, password)
                        if token:
                            st.session_state.authenticated = True
                            st.session_state.token = token
                            st.session_state.user_email = email
                            
                            # Get credits
                            credits, user_email, name = get_credits(token)
                            st.session_state.credits = credits
                            st.session_state.user_name = name
                            
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error(f"❌ {error}")
                else:
                    st.warning("Please enter email and password")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            reg_name = st.text_input("👤 Full Name", placeholder="John Doe")
            reg_email = st.text_input("📧 Email", placeholder="your@email.com")
            reg_password = st.text_input("🔒 Password", type="password", help="Min 8 chars, 1 uppercase, 1 number")
            reg_submit = st.form_submit_button("Register (100 Free Credits)", use_container_width=True)
            
            if reg_submit:
                if reg_name and reg_email and reg_password:
                    with st.spinner("Registering..."):
                        result, error = register_user(reg_email, reg_password, reg_name)
                        if result and not error:
                            st.success("✅ Registration successful! Check your email for verification code.")
                            st.info(f"📧 Verification code sent to: {reg_email}")
                        else:
                            st.error(f"❌ {error}")
                else:
                    st.warning("Please fill all fields")
    
    with tab3:
        st.subheader("Verify Your Email")
        with st.form("verify_form"):
            verify_email_input = st.text_input("📧 Email", placeholder="your@email.com")
            verify_code = st.text_input("🔢 6-Digit Verification Code", placeholder="123456", max_chars=6)
            verify_submit = st.form_submit_button("Verify Email", use_container_width=True)
            
            if verify_submit:
                if verify_email_input and verify_code:
                    with st.spinner("Verifying..."):
                        success, error = verify_email(verify_email_input, verify_code)
                        if success:
                            st.success("✅ Email verified! You can now login.")
                        else:
                            st.error(f"❌ {error}")
                else:
                    st.warning("Please enter email and verification code")

def show_user_profile_sidebar():
    """Show user profile in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 User Profile")
        
        name = st.session_state.get('user_name', 'User')
        email = st.session_state.get('user_email', '')
        credits = st.session_state.get('credits', 0)
        
        st.write(f"**Name:** {name}")
        st.write(f"**Email:** {email}")
        
        # Show different colors based on credit level
        if credits <= 0:
            gradient = "linear-gradient(135deg, #f5576c 0%, #f093fb 100%)"
            warning_msg = "⚠️ No Credits!"
        elif credits <= 2:
            gradient = "linear-gradient(135deg, #ffc107 0%, #ff6f00 100%)"
            warning_msg = "⚠️ Low Credits"
        else:
            gradient = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            warning_msg = ""
        
        st.markdown(f"""
        <div style="background: {gradient}; 
                    color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0;">
            <h3 style="margin: 0;">Credits</h3>
            <h1 style="margin: 0.5rem 0;">{credits}</h1>
            {f'<p style="margin: 0; font-weight: bold;">{warning_msg}</p>' if warning_msg else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Show subscribe button if credits are 0
        if credits <= 0:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
                <h4 style="margin: 0;">💎 Subscribe Now!</h4>
                <p style="margin: 0.5rem 0; font-size: 0.9rem;">Get more credits to continue processing</p>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                token = st.session_state.get('token')
                if token:
                    credits, _, _ = get_credits(token)
                    st.session_state.credits = credits
                    st.rerun()
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.token = None
                st.session_state.credits = 0
                st.session_state.user_email = None
                st.session_state.user_name = None
                st.rerun()
