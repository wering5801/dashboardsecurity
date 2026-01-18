"""
Authentication Module for Falcon Security Dashboard
Provides password protection and session management
Developed by Izami Ariff © 2025
"""

import streamlit as st
import hashlib
from datetime import datetime, timedelta

# ==============================================
# CONFIGURATION
# ==============================================

# Default credentials (change these for production!)
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "ThisSOCR3port2026"

# Session timeout (in minutes)
SESSION_TIMEOUT_MINUTES = 60

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

    # Center the login form
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 30px;
            background-color: #f8f9fa;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .login-header {
            text-align: center;
            color: #1f77b4;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .login-subheader {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
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
        st.caption("🔒 Secure access to security analytics and reporting")
        st.caption("📧 Contact your administrator if you need access")

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
    """Display logout button in sidebar"""
    with st.sidebar:
        st.markdown("---")
        user = st.session_state.get('username', 'User')
        login_time = st.session_state.get('login_time')

        if login_time:
            session_duration = datetime.now() - login_time
            hours, remainder = divmod(int(session_duration.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            st.caption(f"👤 Logged in as: **{user}**")
            st.caption(f"⏱️ Session: {hours}h {minutes}m")

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
