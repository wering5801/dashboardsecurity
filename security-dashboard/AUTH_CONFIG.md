# Authentication Configuration Guide

This guide explains how to configure and customize the authentication system for the Falcon Security Dashboard.

---

## 🔐 Default Credentials

**Default Login:**
- **Username:** `admin`
- **Password:** `FalconSecurity2026`

⚠️ **IMPORTANT:** Change these credentials before deploying to production!

---

## 🛠️ How to Change Default Credentials

### Method 1: Edit auth.py Directly

1. Open [`auth.py`](auth.py)
2. Locate these lines (around line 15-16):

```python
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "FalconSecurity2026"
```

3. Change to your desired credentials:

```python
DEFAULT_USERNAME = "your_username"
DEFAULT_PASSWORD = "YourSecurePassword2026"
```

4. Save the file and restart the dashboard

---

## 👥 Adding Multiple Users

To add multiple users with different credentials:

1. Open [`auth.py`](auth.py)
2. Find the `authenticate_user()` function (around line 125)
3. Replace the simple authentication with the commented multi-user example:

```python
def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials"""

    # Define multiple users with hashed passwords
    USERS = {
        "admin": hash_password("FalconSecurity2026"),
        "analyst": hash_password("AnalystPass2026"),
        "manager": hash_password("ManagerPass2026"),
        "security_team": hash_password("SecTeam2026")
    }

    return username in USERS and verify_password(password, USERS[username])
```

4. Add as many users as needed to the `USERS` dictionary

---

## ⏱️ Session Timeout Configuration

By default, sessions expire after **60 minutes** of inactivity.

To change the timeout duration:

1. Open [`auth.py`](auth.py)
2. Find this line (around line 13):

```python
SESSION_TIMEOUT_MINUTES = 60
```

3. Change to your desired timeout (in minutes):

```python
SESSION_TIMEOUT_MINUTES = 120  # 2 hours
SESSION_TIMEOUT_MINUTES = 30   # 30 minutes
SESSION_TIMEOUT_MINUTES = 480  # 8 hours
```

---

## 🔒 Security Features

### Current Features:
- ✅ Password-protected access
- ✅ Session management with timeout
- ✅ Password hashing (SHA-256)
- ✅ Automatic logout on inactivity
- ✅ Session duration tracking
- ✅ Clean login/logout flow

### Future Enhancements (Optional):
- Role-based access control (RBAC)
- Integration with Active Directory/LDAP
- Two-factor authentication (2FA)
- Password strength requirements
- Login attempt limiting
- Audit logging

---

## 🎨 Customizing Login Page

To customize the login page appearance:

1. Open [`auth.py`](auth.py)
2. Find the `show_login_page()` function (around line 85)
3. Modify the CSS styling in the `<style>` section:

```python
st.markdown("""
    <style>
    .login-container {
        background-color: #f8f9fa;  # Change background color
        border-radius: 10px;         # Adjust border radius
        box-shadow: ...              # Modify shadow
    }
    .login-header {
        color: #1f77b4;              # Change header color
        font-size: 28px;             # Adjust font size
    }
    </style>
""", unsafe_allow_html=True)
```

4. Modify the header text:

```python
st.markdown('<div class="login-header">🛡️ Your Company Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="login-subheader">Your custom subtitle here</div>', unsafe_allow_html=True)
```

---

## 🚀 Production Deployment Best Practices

### 1. Use Environment Variables
Instead of hardcoding credentials in `auth.py`, use environment variables:

```python
import os

DEFAULT_USERNAME = os.getenv("DASHBOARD_USERNAME", "admin")
DEFAULT_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "FalconSecurity2026")
```

Then set environment variables:
```bash
export DASHBOARD_USERNAME="your_username"
export DASHBOARD_PASSWORD="your_secure_password"
```

### 2. Use Stronger Password Hashing
For production, consider using bcrypt instead of SHA-256:

```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(input_password: str, stored_hash: bytes) -> bool:
    return bcrypt.checkpw(input_password.encode(), stored_hash)
```

### 3. Store Credentials Securely
- Never commit passwords to version control
- Use a secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)
- Use a configuration file that's excluded from git (.gitignore)

---

## 🔧 Troubleshooting

### Issue: Can't login after changing credentials
**Solution:** Clear your browser cache or use an incognito window to reset the session state.

### Issue: Session expires too quickly
**Solution:** Increase `SESSION_TIMEOUT_MINUTES` in `auth.py`

### Issue: Need to bypass authentication for testing
**Solution:** Temporarily comment out the authentication check in `app.py`:

```python
# if not require_authentication():
#     st.stop()
```

⚠️ **Remember to uncomment before deploying!**

---

## 📞 Support

For questions or issues with authentication:
1. Check this guide first
2. Review the code comments in `auth.py`
3. Contact your system administrator

---

**Developed by Izami Ariff © 2025**
