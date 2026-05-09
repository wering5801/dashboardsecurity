#!/bin/bash
# Secure Deployment Script for Falcon Security Dashboard
#
# This script hashes the password locally with PBKDF2-HMAC-SHA256 and only
# sends DASHBOARD_PASSWORD_HASH (and the salt) to Cloud Run. The plaintext
# password never leaves your machine and is never stored as a Cloud Run env
# var.

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔒 Secure Deployment - Falcon Security Dashboard${NC}"
echo ""

# Prompt for credentials
echo -e "${YELLOW}Enter your secure credentials:${NC}"
read -p "Username: " DASHBOARD_USER
read -sp "Password: " DASHBOARD_PASS
echo ""

# Prompt for project details
read -p "Project ID: " PROJECT_ID
read -p "Service Name [falcon-dashboard]: " SERVICE_NAME
SERVICE_NAME=${SERVICE_NAME:-falcon-dashboard}

read -p "Region [us-central1]: " REGION
REGION=${REGION:-us-central1}

# Salt: must match what the running app uses (defaults to the value baked
# into auth.py). Override here AND in DASHBOARD_PASSWORD_SALT below if you
# want a per-deployment salt.
DASHBOARD_PASSWORD_SALT="${DASHBOARD_PASSWORD_SALT:-falcon-dashboard-static-salt-v1}"

echo ""
echo -e "${GREEN}Hashing password locally (PBKDF2-HMAC-SHA256, 200k iterations)...${NC}"
DASHBOARD_PASSWORD_HASH=$(_PW="$DASHBOARD_PASS" _SALT="$DASHBOARD_PASSWORD_SALT" python3 -c '
import hashlib, os
print(hashlib.pbkdf2_hmac("sha256",
    os.environ["_PW"].encode(),
    os.environ["_SALT"].encode(),
    200_000).hex())
')
unset DASHBOARD_PASS

echo ""
echo -e "${GREEN}Deploying to Cloud Run (no plaintext password in env vars)...${NC}"

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --port 8080 \
  --timeout 300 \
  --project "$PROJECT_ID" \
  --set-env-vars "DASHBOARD_USERNAME=$DASHBOARD_USER" \
  --set-env-vars "DASHBOARD_PASSWORD_HASH=$DASHBOARD_PASSWORD_HASH" \
  --set-env-vars "DASHBOARD_PASSWORD_SALT=$DASHBOARD_PASSWORD_SALT" \
  --remove-env-vars "DASHBOARD_PASSWORD" || true

unset DASHBOARD_PASSWORD_HASH

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${YELLOW}Only the password hash + salt are stored as env vars.${NC}"
echo ""
echo "Get your service URL:"
echo "gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'"
