# 🚀 Deploy to Google Cloud Run - Quick Start

## 📦 Prerequisites
- Google Cloud account with billing enabled
- gcloud CLI installed: https://cloud.google.com/sdk/docs/install

## ⚡ Deploy in 3 Steps

### Step 1: Login
```bash
gcloud auth login
```

### Step 2: Set Project
```bash
# Create new project
gcloud projects create falcon-dashboard-prod
gcloud config set project falcon-dashboard-prod

# Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com
```

### Step 3: Deploy!
```bash
cd "c:\Users\izami\OneDrive\website\VS code"

gcloud run deploy falcon-dashboard \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --port 8080
```

## 🎉 Done!

You'll get a URL like: `https://falcon-dashboard-xxxxx-uc.a.run.app`

## 🔑 Default Login
- Username: `admin`
- Password: `ThisSOCR3port2026`

⚠️ **Change the password in `security-dashboard/auth.py` before deploying!**

## 📚 Full Guide
See `DEPLOYMENT_GUIDE.md` for complete documentation.

---
**Developed by Izami Ariff © 2025**
