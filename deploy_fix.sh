#!/bin/bash

echo "🚀 SmartWealth Simple - Deployment Fix Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -d "app" ] || [ ! -d "web" ]; then
    print_error "Please run this script from the root directory of your project"
    exit 1
fi

echo ""
print_status "Starting deployment process..."

# Step 1: Deploy Backend Changes
echo ""
echo "📦 Step 1: Deploying Backend Changes to Railway"
echo "-----------------------------------------------"

cd app

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_error "Git repository not found in app directory"
    exit 1
fi

# Add all changes
print_status "Adding changes to git..."
git add .

# Commit changes
print_status "Committing changes..."
git commit -m "Fix CORS configuration for Vercel frontend"

# Push to Railway
print_status "Pushing to Railway..."
git push origin main

if [ $? -eq 0 ]; then
    print_status "Backend changes pushed successfully!"
    print_warning "Railway will automatically redeploy in a few minutes"
else
    print_error "Failed to push backend changes"
    exit 1
fi

cd ..

# Step 2: Deploy Frontend Changes
echo ""
echo "🌐 Step 2: Deploying Frontend Changes to Vercel"
echo "-----------------------------------------------"

cd web

# Check if git is initialized
if [ ! -d ".git" ]; then
    print_error "Git repository not found in web directory"
    exit 1
fi

# Add all changes
print_status "Adding changes to git..."
git add .

# Commit changes
print_status "Committing changes..."
git commit -m "Add better API error handling and debugging"

# Push to Vercel
print_status "Pushing to Vercel..."
git push origin main

if [ $? -eq 0 ]; then
    print_status "Frontend changes pushed successfully!"
    print_warning "Vercel will automatically redeploy in a few minutes"
else
    print_error "Failed to push frontend changes"
    exit 1
fi

cd ..

# Step 3: Test the deployment
echo ""
echo "🧪 Step 3: Testing the Deployment"
echo "---------------------------------"

print_status "Waiting 30 seconds for deployments to complete..."
sleep 30

# Test backend health
print_status "Testing backend health..."
if curl -s https://smart-health-ai.up.railway.app/health > /dev/null; then
    print_status "Backend is responding!"
else
    print_warning "Backend might still be deploying..."
fi

# Test sectors API
print_status "Testing sectors API..."
if curl -s https://smart-health-ai.up.railway.app/api/ai/sectors > /dev/null; then
    print_status "Sectors API is working!"
else
    print_warning "Sectors API might still be deploying..."
fi

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
print_status "Your changes have been deployed to both Railway and Vercel"
print_status "Please wait 2-3 minutes for the deployments to fully complete"
echo ""
print_warning "Next steps:"
echo "1. Open https://smart-wealth-simple.vercel.app/ in your browser"
echo "2. Test the Sectors and Earnings pages"
echo "3. Open browser developer tools (F12) to check for any errors"
echo "4. Use test_connection.html to verify all endpoints are working"
echo ""
print_status "If you see any issues, check the troubleshooting guide in DEPLOYMENT_FIX_GUIDE.md"
