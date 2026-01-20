# 🔧 Deployment Troubleshooting Guide

Common issues and solutions for Google Cloud Run deployment.

---

## ❌ Build Failed Error

### Solution 1: Check Build Logs
```bash
gcloud builds list --limit=1
# Copy the build ID, then:
gcloud builds log <BUILD_ID>
```

### Solution 2: Test Docker Build Locally
```bash
docker build -t falcon-dashboard .
docker run -p 8080:8080 falcon-dashboard
```

### Solution 3: Check Requirements.txt
Ensure all dependencies are compatible with Python 3.9

---

## ❌ Memory/Timeout Issues

### Increase Memory
```bash
gcloud run services update falcon-dashboard --memory 4Gi --region us-central1
```

### Increase Timeout
```bash
gcloud run services update falcon-dashboard --timeout 600 --region us-central1
```

---

## ❌ Permission Denied

### Enable APIs
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Check Billing
Ensure billing is enabled for your project in the Cloud Console.

---

## ❌ Application Not Loading

### Check Logs
```bash
gcloud run services logs tail falcon-dashboard --region us-central1
```

### Common Issues:
- Port mismatch (ensure using 8080)
- Missing dependencies
- Python version issues

---

## 🔄 Clean Rebuild

If all else fails, try a clean rebuild:

```bash
# Delete existing service
gcloud run services delete falcon-dashboard --region us-central1

# Redeploy from scratch
gcloud run deploy falcon-dashboard \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --port 8080 \
  --timeout 300
```

---

## 📞 Get Help

Check build logs for specific errors:
```bash
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>
```

---

**Developed by Izami Ariff © 2025**
