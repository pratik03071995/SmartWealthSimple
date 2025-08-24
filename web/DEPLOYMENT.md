# Frontend Deployment Guide

## Issue
The frontend is currently hardcoded to use `http://127.0.0.1:5001` for API calls, which only works locally.

## Solution
The frontend now uses environment-based configuration:

1. **Development**: Uses `http://127.0.0.1:5001` (localhost)
2. **Production**: Uses `VITE_API_URL` environment variable

## Steps to Deploy

### 1. Deploy Backend First
Deploy your Flask backend to a hosting service (Vercel, Railway, Heroku, etc.)

### 2. Set Environment Variable in Vercel
In your Vercel dashboard for the frontend project:

1. Go to Settings → Environment Variables
2. Add a new variable:
   - **Name**: `VITE_API_URL`
   - **Value**: Your deployed backend URL (e.g., `https://your-backend.vercel.app`)
   - **Environment**: Production (and Preview if needed)

### 3. Redeploy Frontend
After setting the environment variable, redeploy your frontend on Vercel.

## Current Configuration
- ✅ API calls now use environment-based URLs
- ✅ Development still works with localhost
- ✅ Production will use the deployed backend URL

## Testing
- **Local**: Should work as before
- **Production**: Will connect to your deployed backend
