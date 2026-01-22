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

## 🔑 Login Credentials
- Username: `admin` (or set via `DASHBOARD_USERNAME` env var)
- Password: Set via `DASHBOARD_PASSWORD` environment variable

⚠️ **Always set credentials via environment variables for security!**

Example deployment with credentials:
```bash
gcloud run deploy falcon-dashboard --source . --region us-central1 \
  --set-env-vars "DASHBOARD_USERNAME=admin,DASHBOARD_PASSWORD=YourSecurePassword"
```

## 📚 Full Guide
See `DEPLOYMENT_GUIDE.md` for complete documentation.

---
**Developed by Izami Ariff © 2025**
