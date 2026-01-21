"""
Authentication Module for Falcon Security Dashboard
Provides password protection and session management
Developed by Izami Ariff © 2025
"""

import streamlit as st
import hashlib
import os
from datetime import datetime, timedelta

# ==============================================
# CONFIGURATION
# ==============================================

# Credentials from environment variables (secure!)
# Fallback to defaults only for local development
DEFAULT_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
DEFAULT_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "ThisSOCR3port2026")

# Session timeout (in minutes)
SESSION_TIMEOUT_MINUTES = 60

# Warning threshold (80% of session timeout)
SESSION_WARNING_THRESHOLD = SESSION_TIMEOUT_MINUTES * 0.8  # 48 minutes

# ==============================================
# PASSWORD HASHING
# ==============================================

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(input_password: str, stored_password_hash: str) -> bool:
    """Verify password against stored hash"""
    return hash_password(input_password) == stored_password_hash

# ==============================================
# SESSION MANAGEMENT
# ==============================================

def init_session_state():
    """Initialize session state for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'login_time' not in st.session_state:
        st.session_state['login_time'] = None
    if 'last_activity' not in st.session_state:
        st.session_state['last_activity'] = None

def is_session_valid() -> bool:
    """Check if current session is still valid (not timed out)"""
    if not st.session_state.get('authenticated', False):
        return False

    last_activity = st.session_state.get('last_activity')
    if last_activity is None:
        return False

    # Check if session has timed out
    time_elapsed = datetime.now() - last_activity
    if time_elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        logout()
        return False

    # Update last activity time
    st.session_state['last_activity'] = datetime.now()
    return True

def login(username: str):
    """Log in user and start session"""
    st.session_state['authenticated'] = True
    st.session_state['username'] = username
    st.session_state['login_time'] = datetime.now()
    st.session_state['last_activity'] = datetime.now()

def logout():
    """Log out user and clear session"""
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['login_time'] = None
    st.session_state['last_activity'] = None

# ==============================================
# AUTHENTICATION UI
# ==============================================

def show_login_page():
    """Display login page with styled interface"""

    # Center the login form with purple-bluish background behind it
    st.markdown("""
        <style>
        /* Main page background - clean white */
        .main {
            background-color: #ffffff;
        }

        /* Purple-bluish background for the entire block area */
        .block-container {
            max-width: 700px !important;
            padding: 3rem 4rem !important;
            background: linear-gradient(135deg, #7e57c2 0%, #5c6bc0 50%, #42a5f5 100%) !important;
            border-radius: 20px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
            margin-top: 5rem !important;
        }

        /* Make form elements have white background */
        .stTextInput > div > div > input {
            background-color: #ffffff !important;
        }

        /* Form labels - bright white */
        .stTextInput > label, .stTextInput label {
            color: #ffffff !important;
            font-weight: 500 !important;
        }

        .stButton > button {
            background-color: #5e35b1 !important;
            color: white !important;
        }

        .login-header {
            text-align: center;
            color: #ffffff;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        .login-subheader {
            text-align: center;
            color: #ffffff;
            font-size: 14px;
            margin-bottom: 30px;
        }

        /* Caption text color - bright white */
        .stCaptionContainer, .stCaptionContainer p {
            color: #ffffff !important;
        }

        /* Make divider white */
        hr {
            border-color: rgba(255, 255, 255, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create centered layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-header">🛡️ Falcon Security Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subheader">Please enter your credentials to continue</div>', unsafe_allow_html=True)

        # Login form
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")

            col_a, col_b = st.columns([1, 1])
            with col_a:
                submit_button = st.form_submit_button("🔐 Login", use_container_width=True)

            if submit_button:
                if authenticate_user(username, password):
                    login(username)
                    st.success(f"✅ Welcome, {username}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

        # Information footer
        st.markdown("---")
        st.markdown('<p style="color: #ffffff; font-size: 12px; margin: 5px 0;">🔒 Secure access to security analytics and reporting</p>', unsafe_allow_html=True)
        st.markdown('<p style="color: #ffffff; font-size: 12px; margin: 5px 0;">📧 Contact PIC for this dashboard if you need access</p>', unsafe_allow_html=True)

def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate user credentials

    You can extend this function to:
    - Check against a database
    - Integrate with LDAP/Active Directory
    - Use environment variables for credentials
    """

    # For now, using default credentials
    # In production, use hashed passwords and secure storage
    if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
        return True

    # Example: Add more users
    # USERS = {
    #     "admin": hash_password("FalconSecurity2026"),
    #     "analyst": hash_password("AnalystPass2026"),
    #     "manager": hash_password("ManagerPass2026")
    # }
    # return username in USERS and verify_password(password, USERS[username])

    return False

def show_logout_button():
    """Display logout button in sidebar with session expiration warning"""
    with st.sidebar:
        st.markdown("---")
        user = st.session_state.get('username', 'User')
        login_time = st.session_state.get('login_time')

        if login_time:
            session_duration = datetime.now() - login_time
            session_minutes = int(session_duration.total_seconds() / 60)
            hours, remainder = divmod(int(session_duration.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)

            st.caption(f"👤 Logged in as: **{user}**")
            st.caption(f"⏱️ Session: {hours}h {minutes}m")

            # Show warning when session is near expiration (80% = 48 minutes)
            if session_minutes >= SESSION_WARNING_THRESHOLD:
                time_remaining = SESSION_TIMEOUT_MINUTES - session_minutes
                st.warning(f"⚠️ Session expires in {time_remaining} minute(s)! You will be automatically logged out.", icon="⏰")

        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

# ==============================================
# MAIN AUTHENTICATION CHECKER
# ==============================================

def require_authentication():
    """
    Main function to require authentication for a page
    Call this at the beginning of each dashboard page

    Returns:
        bool: True if authenticated, False otherwise (stops execution)
    """
    init_session_state()

    # Check if session is still valid
    if not is_session_valid():
        show_login_page()
        st.stop()
        return False

    # Show logout button in sidebar
    show_logout_button()

    return True

# ==============================================
# OPTIONAL: ROLE-BASED ACCESS CONTROL
# ==============================================

def check_permission(required_role: str) -> bool:
    """
    Check if current user has required role/permission
    This is a placeholder for future role-based access control

    Args:
        required_role: Role required to access feature (e.g., "admin", "analyst")

    Returns:
        bool: True if user has permission
    """
    # For now, all authenticated users have access
    # You can extend this with role checking:
    # user_role = st.session_state.get('user_role')
    # return user_role == required_role or user_role == 'admin'
    return st.session_state.get('authenticated', False)
