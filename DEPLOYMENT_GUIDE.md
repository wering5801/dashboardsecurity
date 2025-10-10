# Streamlit Deployment Guide

## 🚀 Deploy to Streamlit Community Cloud

### Prerequisites
- ✅ Code pushed to GitHub: `https://github.com/wering5801/dashboardsecurity`
- ✅ `requirements.txt` file present
- ✅ GitHub account

### Step-by-Step Deployment

#### 1. Go to Streamlit Community Cloud
Visit: **https://share.streamlit.io**

#### 2. Sign In
- Click **"Sign in with GitHub"**
- Authorize Streamlit to access your GitHub account

#### 3. Deploy New App
- Click **"New app"** button (top right)

#### 4. Configure Deployment
Fill in the following details:

**Repository:**
```
wering5801/dashboardsecurity
```

**Branch:**
```
main
```

**Main file path:**
```
security-dashboard/app.py
```

**App URL (optional):**
Choose a custom subdomain or use auto-generated one:
```
[your-app-name].streamlit.app
```

#### 5. Advanced Settings (Optional)
Click **"Advanced settings"** if you need to:
- Set Python version (default: 3.11)
- Add secrets (for API keys, credentials)
- Set environment variables

**Recommended Python version:**
```
3.11
```

#### 6. Deploy!
- Click **"Deploy!"** button
- Wait 2-5 minutes for initial deployment
- Your app will be live at: `https://[your-app-name].streamlit.app`

---

## 📋 Post-Deployment Checklist

### Verify Deployment
- [ ] App loads successfully
- [ ] All pages are accessible in sidebar
- [ ] Themes are working
- [ ] Data upload functionality works
- [ ] Charts render correctly
- [ ] PDF export layout displays properly

### Share Your App
Your app is now live at:
```
https://[your-app-name].streamlit.app
```

### App Management

#### View Logs
- Go to https://share.streamlit.io
- Click on your app
- Click **"Manage app"**
- View **"Logs"** tab for debugging

#### Reboot App
If the app crashes or needs restart:
- Go to app management
- Click **"Reboot app"**

#### Update App
App auto-updates when you push to GitHub:
```bash
git add .
git commit -m "Update description"
git push origin main
```

The app will automatically redeploy within 1-2 minutes.

---

## 🔧 Alternative Deployment Options

### Option 1: Streamlit Cloud (Paid)
- More resources
- Private apps
- Custom domains
- Priority support

Visit: **https://streamlit.io/cloud**

### Option 2: Self-Hosted (Docker)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY security-dashboard/requirements.txt .
RUN pip install -r requirements.txt

COPY security-dashboard/ .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t falcon-dashboard .
docker run -p 8501:8501 falcon-dashboard
```

### Option 3: Heroku

Create `Procfile`:
```
web: sh setup.sh && streamlit run security-dashboard/app.py
```

Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Option 4: AWS / Azure / GCP
- EC2 / VM instance
- Install Python and dependencies
- Run streamlit on port 8501
- Configure security groups/firewall
- Use nginx as reverse proxy (optional)

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
**Error:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
- Add missing package to `requirements.txt`
- Push to GitHub
- App will auto-redeploy

#### 2. App Crashes on Startup
**Solution:**
- Check logs in Streamlit Cloud dashboard
- Verify all file paths are relative
- Ensure no hardcoded absolute paths

#### 3. PDF Export Not Working
**Solution:**
- PDF export uses browser-side capture (GoFullPage extension)
- No server-side PDF generation needed
- Instruct users to install GoFullPage extension

#### 4. Data Upload Issues
**Solution:**
- Check file size limits (Streamlit Cloud: 200MB default)
- Verify CSV format matches expected structure
- Add error handling in upload logic

#### 5. Charts Not Rendering
**Solution:**
- Verify plotly version in requirements.txt
- Check browser console for errors
- Clear browser cache

---

## 📊 Your Deployed App

### Repository
```
https://github.com/wering5801/dashboardsecurity
```

### Deployment URL
```
https://[your-app-name].streamlit.app
```

### Main Entry Point
```
security-dashboard/app.py
```

---

## 🎯 Next Steps

1. **Test the live app thoroughly**
   - Upload sample data
   - Generate all analyses
   - Test PDF export layout
   - Try all dashboard views

2. **Share with stakeholders**
   - Copy the app URL
   - Create user guide if needed
   - Demonstrate key features

3. **Monitor performance**
   - Check logs regularly
   - Monitor resource usage
   - Optimize if needed

4. **Update as needed**
   - Push updates to GitHub
   - App auto-deploys
   - No downtime required

---

## 📞 Support

### Streamlit Community
- Forum: https://discuss.streamlit.io
- Documentation: https://docs.streamlit.io
- GitHub: https://github.com/streamlit/streamlit

### Your Repository Issues
- https://github.com/wering5801/dashboardsecurity/issues

---

**🎉 Congratulations! Your Falcon Security Dashboard is now live!**
