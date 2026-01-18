# 🚀 Deployment Guide - Google Cloud Run

Complete guide to deploy the Falcon Security Dashboard to Google Cloud Run.

---

## 📋 Prerequisites

Before deploying, ensure you have:

1. ✅ **Google Cloud Account** with billing enabled
2. ✅ **Google Cloud SDK** (gcloud CLI) installed
3. ✅ **Docker** installed (optional, for local testing)
4. ✅ **Git** installed

### Install Google Cloud SDK

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

**macOS/Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

---

## 🏗️ Quick Deployment (3 Commands)

```bash
# 1. Login to Google Cloud
gcloud auth login

# 2. Set your project
gcloud config set project YOUR_PROJECT_ID

# 3. Deploy!
gcloud run deploy falcon-dashboard --source . --region us-central1 --allow-unauthenticated
```

---

## 📖 Detailed Step-by-Step Guide

### Step 1: Google Cloud Setup

1. **Initialize gcloud:**
   ```bash
   gcloud init
   ```

2. **Create a new project:**
   ```bash
   gcloud projects create falcon-dashboard-prod
   gcloud config set project falcon-dashboard-prod
   ```

3. **Enable required APIs:**
   ```bash
   gcloud services enable cloudbuild.googleapis.com run.googleapis.com
   ```

### Step 2: Deploy

```bash
gcloud run deploy falcon-dashboard \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --port 8080
```

### Step 3: Access Your Dashboard

After deployment completes, you'll get a URL like:
```
https://falcon-dashboard-xxxxxxxxx-uc.a.run.app
```

---

## 🔒 Security Settings

### Change Default Password

Before deploying, edit `security-dashboard/auth.py`:
```python
DEFAULT_PASSWORD = "YourSecurePassword2026"
```

### Use Environment Variables (Recommended)

```bash
gcloud run deploy falcon-dashboard \
  --set-env-vars DASHBOARD_PASSWORD=YourSecurePassword
```

---

## 📊 Monitoring

View logs:
```bash
gcloud run services logs tail falcon-dashboard --region us-central1
```

---

## 🔄 Update Deployment

```bash
gcloud run deploy falcon-dashboard --source . --region us-central1
```

---

**Developed by Izami Ariff © 2025**
