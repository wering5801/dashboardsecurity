# 🌐 Custom Domain & Security Guide

Complete guide to secure your dashboard and use a custom domain.

---

## 🔒 Part 1: Secure Credentials (Hide Password)

### Why Secure Credentials?
- ❌ Hardcoded passwords in code can be seen on GitHub
- ❌ Anyone with repo access can see credentials
- ✅ Environment variables keep secrets secure
- ✅ Different passwords for dev/staging/production

### Option A: Deploy with Environment Variables (Recommended)

**PowerShell (Windows):**
```powershell
# Set your secure credentials
$USERNAME = "your_username"
$PASSWORD = "YourVerySecurePassword2026!"

# Deploy with environment variables
gcloud run deploy falcon-dashboard --source . --region us-central1 --set-env-vars "DASHBOARD_USERNAME=$USERNAME,DASHBOARD_PASSWORD=$PASSWORD"
```

**Or use the secure deployment script:**
```powershell
.\deploy-secure.ps1
```

This will prompt you for credentials and deploy securely.

### Option B: Use Google Secret Manager (Most Secure)

1. **Create secrets:**
```bash
# Store password in Secret Manager
echo -n "YourSecurePassword2026!" | gcloud secrets create dashboard-password --data-file=-

# Store username in Secret Manager
echo -n "admin" | gcloud secrets create dashboard-username --data-file=-
```

2. **Update auth.py to use secrets:**
```python
import os
from google.cloud import secretmanager

def get_secret(secret_id):
    """Retrieve secret from Google Secret Manager"""
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except:
        return os.getenv(secret_id.upper().replace("-", "_"))

DEFAULT_USERNAME = get_secret("dashboard-username")
DEFAULT_PASSWORD = get_secret("dashboard-password")
```

3. **Deploy with secret access:**
```bash
gcloud run deploy falcon-dashboard \
  --source . \
  --region us-central1 \
  --set-secrets DASHBOARD_USERNAME=dashboard-username:latest \
  --set-secrets DASHBOARD_PASSWORD=dashboard-password:latest
```

---

## 🌐 Part 2: Custom Domain (Shorter URL)

### Current URL Format:
```
https://falcon-dashboard-1001553963887-us-central1.run.app
```
The long URL includes:
- Service name: `falcon-dashboard`
- Project number: `1001553963887`
- Region: `us-central1`
- Domain: `run.app`

### Option 1: Custom Domain with Your Own Domain

If you own a domain (e.g., `yourdomain.com`), you can map it:

**Step 1: Verify domain ownership**
```bash
gcloud domains verify yourdomain.com
```

**Step 2: Map custom domain**
```bash
gcloud run domain-mappings create \
  --service falcon-dashboard \
  --domain dashboard.yourdomain.com \
  --region us-central1
```

**Step 3: Update DNS records**
Google will provide DNS records to add to your domain registrar.

**Result:** Access at `https://dashboard.yourdomain.com`

### Option 2: Use Shorter Project ID

Create a new project with a short ID:

```bash
# Create project with short, memorable ID
gcloud projects create falconsec --name="Falcon Dashboard"

# Set as active project
gcloud config set project falconsec

# Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Deploy to new project
gcloud run deploy falcon --source . --region us-central1
```

**Result:** `https://falcon-xxxxx-uc.a.run.app` (shorter!)

### Option 3: Use Cloud Load Balancer with Custom Path

Set up a load balancer with a vanity URL:

```bash
# Reserve a static IP
gcloud compute addresses create falcon-ip --global

# Create serverless NEG
gcloud compute network-endpoint-groups create falcon-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=falcon-dashboard

# Create backend service and load balancer
# (Full setup requires multiple steps - see Cloud Run docs)
```

**Result:** Custom domain with your branding

---

## 🔐 Part 3: Additional Security Features

### 1. Restrict Access with Cloud IAM

**Allow only specific users:**
```bash
# Deploy with authentication required
gcloud run deploy falcon-dashboard --no-allow-unauthenticated

# Grant access to specific users
gcloud run services add-iam-policy-binding falcon-dashboard \
  --member='user:user@example.com' \
  --role='roles/run.invoker' \
  --region us-central1
```

Now only authorized Google accounts can access.

### 2. Add IP Restrictions

Use Cloud Armor with Load Balancer to restrict by IP:

```bash
# Create security policy
gcloud compute security-policies create dashboard-policy

# Add IP whitelist rule
gcloud compute security-policies rules create 1000 \
  --security-policy dashboard-policy \
  --src-ip-ranges "1.2.3.4/32,5.6.7.8/32" \
  --action "allow"

# Deny all other IPs
gcloud compute security-policies rules create 2000 \
  --security-policy dashboard-policy \
  --src-ip-ranges "*" \
  --action "deny(403)"
```

### 3. Enable Audit Logging

Track who accesses your dashboard:

```bash
# Enable Cloud Run audit logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

### 4. Set Up Alerts

Get notified of suspicious activity:

```bash
# Create alert for failed login attempts
# (Configure in Cloud Monitoring console)
```

---

## 📝 Quick Reference: Secure Deployment

### For Windows (PowerShell):

```powershell
# Method 1: Quick one-liner
gcloud run deploy falcon-dashboard --source . --region us-central1 --set-env-vars "DASHBOARD_USERNAME=admin,DASHBOARD_PASSWORD=YourSecurePass123!"

# Method 2: Use the script
.\deploy-secure.ps1
```

### Update Credentials Later:

```bash
# Update environment variables without redeploying code
gcloud run services update falcon-dashboard \
  --update-env-vars DASHBOARD_PASSWORD=NewPassword123! \
  --region us-central1
```

### View Current Environment Variables:

```bash
gcloud run services describe falcon-dashboard \
  --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)"
```

---

## ✅ Best Practices Summary

1. ✅ **Never** commit passwords to Git
2. ✅ **Always** use environment variables or Secret Manager
3. ✅ **Consider** using a custom domain for branding
4. ✅ **Enable** Cloud IAM for sensitive deployments
5. ✅ **Monitor** access logs regularly
6. ✅ **Rotate** passwords every 90 days
7. ✅ **Use** strong passwords (12+ characters, mixed case, numbers, symbols)

---

## 🚀 Next Steps

1. Deploy with secure credentials using the script
2. (Optional) Set up custom domain
3. Test login with new credentials
4. Enable monitoring and alerts
5. Document your deployment for team members

---

**Developed by Izami Ariff © 2025**
