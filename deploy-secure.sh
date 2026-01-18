#!/bin/bash
# Secure Deployment Script for Falcon Security Dashboard

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

echo ""
echo -e "${GREEN}Deploying with environment variables (credentials NOT in code)...${NC}"

# Deploy with environment variables
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --port 8080 \
  --timeout 300 \
  --project $PROJECT_ID \
  --set-env-vars DASHBOARD_USERNAME="$DASHBOARD_USER" \
  --set-env-vars DASHBOARD_PASSWORD="$DASHBOARD_PASS"

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${YELLOW}Your credentials are stored securely as environment variables.${NC}"
echo ""
echo "Get your service URL:"
echo "gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'"
