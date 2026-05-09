# Secure Deployment Script for Falcon Security Dashboard (PowerShell)
#
# Hashes the password locally with PBKDF2-HMAC-SHA256 and only sends
# DASHBOARD_PASSWORD_HASH (and the salt) to Cloud Run. The plaintext
# password never leaves your machine and is never stored as a Cloud Run
# env var.

$ErrorActionPreference = "Stop"

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

# Salt: must match what auth.py uses (default baked in below).
if (-not $env:DASHBOARD_PASSWORD_SALT) {
    $SALT = "falcon-dashboard-static-salt-v1"
} else {
    $SALT = $env:DASHBOARD_PASSWORD_SALT
}

Write-Host ""
Write-Host "Hashing password locally (PBKDF2-HMAC-SHA256, 200k iterations)..." -ForegroundColor Green

Add-Type -AssemblyName System.Security
$pwBytes   = [System.Text.Encoding]::UTF8.GetBytes($DASHBOARD_PASS_TEXT)
$saltBytes = [System.Text.Encoding]::UTF8.GetBytes($SALT)
$pbkdf2    = New-Object System.Security.Cryptography.Rfc2898DeriveBytes($pwBytes, $saltBytes, 200000, [System.Security.Cryptography.HashAlgorithmName]::SHA256)
$hashBytes = $pbkdf2.GetBytes(32)
$DASHBOARD_PASSWORD_HASH = ($hashBytes | ForEach-Object { $_.ToString("x2") }) -join ""

# Wipe plaintext from memory ASAP
$DASHBOARD_PASS_TEXT = $null
[Array]::Clear($pwBytes, 0, $pwBytes.Length)

Write-Host ""
Write-Host "Deploying to Cloud Run (no plaintext password in env vars)..." -ForegroundColor Green

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
  --set-env-vars "DASHBOARD_USERNAME=$DASHBOARD_USER" `
  --set-env-vars "DASHBOARD_PASSWORD_HASH=$DASHBOARD_PASSWORD_HASH" `
  --set-env-vars "DASHBOARD_PASSWORD_SALT=$SALT" `
  --remove-env-vars "DASHBOARD_PASSWORD"

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "Only the password hash + salt are stored as env vars." -ForegroundColor Yellow
Write-Host ""
Write-Host "Get your service URL:"
Write-Host "gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'"
