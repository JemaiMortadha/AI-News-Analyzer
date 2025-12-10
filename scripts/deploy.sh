#!/bin/bash

# AI News Analyzer - Complete DevOps Deployment Script
# This script automates the entire deployment process

set -e  # Exit on error

echo "🚀 AI News Analyzer - DevOps Deployment"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Build Docker Images
echo -e "${YELLOW}Step 1/5: Building Docker images...${NC}"
docker build -t mortadhajemai/ai-news-backend:latest ./backend
docker build -t mortadhajemai/ai-news-frontend:latest ./frontend
echo -e "${GREEN}✅ Images built successfully${NC}"

# Step 2: Push to DockerHub
echo -e "${YELLOW}Step 2/5: Pushing images to DockerHub...${NC}"
docker push mortadhajemai/ai-news-backend:latest
docker push mortadhajemai/ai-news-frontend:latest
echo -e "${GREEN}✅ Images pushed to DockerHub${NC}"

# Step 3: Initialize Terraform
echo -e "${YELLOW}Step 3/5: Initializing Terraform...${NC}"
cd terraform
terraform init
echo -e "${GREEN}✅ Terraform initialized${NC}"

# Step 4: Plan Terraform deployment
echo -e "${YELLOW}Step 4/5: Planning Terraform deployment...${NC}"
terraform plan
echo -e "${GREEN}✅ Terraform plan completed${NC}"

# Step 5: Apply Terraform
echo -e "${YELLOW}Step 5/5: Deploying to Kubernetes...${NC}"
terraform apply -auto-approve

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Show outputs
terraform output

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Check pod status: kubectl get pods -n ai-news-analyzer"
echo "2. Get service URLs: kubectl get svc -n ai-news-analyzer"
echo "3. View logs: kubectl logs -n ai-news-analyzer -l app=backend"
echo ""
echo -e "${GREEN}Happy analyzing! 🤖${NC}"
