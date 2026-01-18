# 🔐 Authentication Setup - Quick Start Guide

The Falcon Security Dashboard now includes password protection to secure access to sensitive security data.

---

## ✨ Quick Start (3 Steps)

### Step 1: Start the Dashboard
```bash
streamlit run app.py
```

### Step 2: Login
When you open the dashboard, you'll see a login screen:

**Default Credentials:**
- **Username:** `admin`
- **Password:** `FalconSecurity2026`

### Step 3: Change Default Password
⚠️ **IMPORTANT:** Change the default password immediately!

1. Open `auth.py`
2. Change lines 15-16:
   ```python
   DEFAULT_USERNAME = "your_username"
   DEFAULT_PASSWORD = "YourSecurePassword2026"
   ```
3. Save and restart the dashboard

---

## 🎯 Features

### ✅ Secure Login
- Password-protected access to all dashboard pages
- Clean, professional login interface
- Automatic session management

### ⏱️ Session Management
- **60-minute timeout** (configurable)
- Automatic logout on inactivity
- Session duration tracking
- Manual logout button

### 🛡️ Security
- Password hashing (SHA-256)
- Session state protection
- No plaintext password storage

---

## 📚 Full Documentation

For detailed configuration options, see:
- **[AUTH_CONFIG.md](AUTH_CONFIG.md)** - Complete configuration guide
  - Change default credentials
  - Add multiple users
  - Adjust session timeout
  - Customize login page
  - Production best practices

---

## 🔓 Logout

To logout:
1. Click the **"🚪 Logout"** button in the sidebar
2. You'll be redirected to the login page

---

## 🚨 Security Notice

- **Never commit credentials** to version control
- **Change default password** before production use
- **Use strong passwords** (minimum 12 characters)
- **Enable HTTPS** in production environments
- **Monitor access logs** regularly

---

## 🔧 Need Help?

- Configuration issues? → See [AUTH_CONFIG.md](AUTH_CONFIG.md)
- Can't login? → Try clearing browser cache
- Forgot password? → Check/reset in `auth.py`

---

**Developed by Izami Ariff © 2025**
