# Secure Deployment Script for Falcon Security Dashboard (PowerShell)

Write-Host "🔒 Secure Deployment - Falcon Security Dashboard" -ForegroundColor Green
Write-Host ""

# Prompt for credentials
Write-Host "Enter your secure credentials:" -ForegroundColor Yellow
$DASHBOARD_USER = Read-Host "Username"
$DASHBOARD_PASS = Read-Host "Password" -AsSecureString
$DASHBOARD_PASS_TEXT = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($DASHBOARD_PASS))

# Prompt for project details
$PROJECT_ID = Read-Host "Project ID"
$SERVICE_NAME = Read-Host "Service Name [falcon-dashboard]"
if ([string]::IsNullOrWhiteSpace($SERVICE_NAME)) { $SERVICE_NAME = "falcon-dashboard" }

$REGION = Read-Host "Region [us-central1]"
if ([string]::IsNullOrWhiteSpace($REGION)) { $REGION = "us-central1" }

Write-Host ""
Write-Host "Deploying with environment variables (credentials NOT in code)..." -ForegroundColor Green

# Deploy with environment variables
gcloud run deploy $SERVICE_NAME `
  --source . `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 1 `
  --port 8080 `
  --timeout 300 `
  --project $PROJECT_ID `
  --set-env-vars "DASHBOARD_USERNAME=$DASHBOARD_USER,DASHBOARD_PASSWORD=$DASHBOARD_PASS_TEXT"

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "Your credentials are stored securely as environment variables." -ForegroundColor Yellow
Write-Host ""
Write-Host "Get your service URL:"
Write-Host "gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'"
