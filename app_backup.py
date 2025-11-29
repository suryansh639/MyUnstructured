import streamlit as st
import json
import requests
import base64
import boto3
from datetime import datetime

# AWS Configuration
API_ENDPOINT = "https://i4a8p9jm70.execute-api.us-east-1.amazonaws.com/prod"
USER_POOL_CLIENT_ID = "lq7a32rt0stetm9sfdljnhs3b"
COGNITO_ENDPOINT = "https://cognito-idp.us-east-1.amazonaws.com/"

# Page config
st.set_page_config(
    page_title="DocuAI - Document Processing",
    page_icon="🚀",
    layout="wide"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'credits' not in st.session_state:
    st.session_state.credits = 0
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

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
        return response.json()
    except Exception as e:
        return {'error': str(e)}

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
        return response.status_code == 200
    except Exception as e:
        return False

def get_credits(token):
    """Get user credits from API"""
    try:
        response = requests.get(
            f"{API_ENDPOINT}/v1/credits",
            headers={'Authorization': f'Bearer {token}'}
        )
        data = response.json()
        return data.get('credits', 0), data.get('email', '')
    except Exception as e:
        return 0, ''

def process_document(token, file_content, filename):
    """Process document via API"""
    try:
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
        return response.json()
    except Exception as e:
        return {'error': str(e)}

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 10px;
        font-weight: 600;
    }
    .credit-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Main App
if not st.session_state.authenticated:
    # Login/Register Page
    st.markdown('<h1 class="main-header">🚀 DocuAI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #6c757d; font-size: 1.2rem;">Transform Unstructured Documents to AI-Ready Data</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "✉️ Verify Email"])
    
    with tab1:
        st.subheader("Login to Your Account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_btn"):
            if email and password:
                with st.spinner("Logging in..."):
                    token, error = cognito_login(email, password)
                    if token:
                        st.session_state.token = token
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        credits, user_email = get_credits(token)
                        st.session_state.credits = credits
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
            else:
                st.warning("Please enter email and password")
    
    with tab2:
        st.subheader("Create New Account")
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password (min 8 chars, 1 uppercase, 1 number)", type="password", key="reg_password")
        
        if st.button("Register (100 Free Credits)", key="reg_btn"):
            if reg_name and reg_email and reg_password:
                with st.spinner("Registering..."):
                    result = register_user(reg_email, reg_password, reg_name)
                    if 'error' not in result:
                        st.success("✅ Registration successful! Check your email for verification code.")
                        st.info(f"📧 Verification code sent to: {reg_email}")
                    else:
                        st.error(f"❌ {result.get('error', 'Registration failed')}")
            else:
                st.warning("Please fill all fields")
    
    with tab3:
        st.subheader("Verify Your Email")
        verify_email_input = st.text_input("Email", key="verify_email")
        verify_code = st.text_input("6-Digit Verification Code", key="verify_code", max_chars=6)
        
        if st.button("Verify Email", key="verify_btn"):
            if verify_email_input and verify_code:
                with st.spinner("Verifying..."):
                    if verify_email(verify_email_input, verify_code):
                        st.success("✅ Email verified! You can now login.")
                    else:
                        st.error("❌ Invalid verification code")
            else:
                st.warning("Please enter email and verification code")

else:
    # Authenticated - Document Processing Page
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 style="color: #667eea;">👤 User Profile</h2>', unsafe_allow_html=True)
        st.write(f"**Email:** {st.session_state.user_email}")
        
        st.markdown(f"""
        <div class="credit-box">
            <h3 style="margin: 0;">Credits Remaining</h3>
            <h1 style="margin: 0.5rem 0;">{st.session_state.credits}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Credits"):
            credits, _ = get_credits(st.session_state.token)
            st.session_state.credits = credits
            st.rerun()
        
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.token = None
            st.session_state.credits = 0
            st.session_state.user_email = None
            st.rerun()
    
    # Main Content
    st.markdown('<h1 class="main-header">📄 Document Processing Suite</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'txt', 'html', 'xlsx', 'pptx'],
            help="Upload PDF, Word, Excel, PowerPoint, HTML, or Text files"
        )
        
        if uploaded_file:
            st.info(f"📎 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            if st.button("🚀 Process Document", key="process_btn"):
                if st.session_state.credits <= 0:
                    st.error("❌ Insufficient credits! Please upgrade your plan.")
                else:
                    with st.spinner("Processing document..."):
                        file_content = uploaded_file.read()
                        result = process_document(
                            st.session_state.token,
                            file_content,
                            uploaded_file.name
                        )
                        
                        if 'error' not in result:
                            st.success("✅ Document processed successfully!")
                            st.session_state.credits = result.get('credits_remaining', st.session_state.credits)
                            
                            # Display results
                            st.subheader("📊 Processing Results")
                            st.json(result)
                            
                            # Download option
                            result_json = json.dumps(result, indent=2)
                            st.download_button(
                                label="💾 Download Results (JSON)",
                                data=result_json,
                                file_name=f"processed_{uploaded_file.name}.json",
                                mime="application/json"
                            )
                        else:
                            st.error(f"❌ Error: {result.get('error', 'Processing failed')}")
    
    with col2:
        st.subheader("ℹ️ Information")
        st.info("""
        **How it works:**
        1. Upload your document
        2. Click "Process Document"
        3. Get AI-ready structured data
        4. Download results as JSON
        
        **Supported formats:**
        - PDF
        - Word (DOCX)
        - Excel (XLSX)
        - PowerPoint (PPTX)
        - HTML
        - Text (TXT)
        
        **Each processing uses 1 credit**
        """)
        
        st.markdown("---")
        st.subheader("📈 Usage Stats")
        st.metric("Credits Used", 100 - st.session_state.credits)
        st.metric("Credits Remaining", st.session_state.credits)
