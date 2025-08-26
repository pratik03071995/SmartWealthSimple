# Deployment Guide for SmartWealthSimple

This guide will help you deploy both your Flask backend and React frontend properly.

## Backend Deployment (Railway)

### Step 1: Deploy to Railway

1. **Sign up for Railway** at https://railway.app/
2. **Connect your GitHub repository**
3. **Create a new project** and select your repository
4. **Set the root directory** to `/app` (where your Flask app is located)
5. **Railway will automatically detect** it's a Python app and use the `requirements.txt`

### Step 2: Configure Environment Variables

In Railway dashboard, add these environment variables:
```
FLASK_ENV=production
```

### Step 3: Get Your Backend URL

After deployment, Railway will give you a URL like:
`https://your-app-name.railway.app`

**Save this URL** - you'll need it for the frontend configuration.

## Frontend Deployment (Vercel)

### Step 1: Update Frontend Configuration

1. **Update your Vercel domain** in the backend CORS configuration:
   - Go to `app/app.py`
   - Replace `"https://your-frontend-domain.vercel.app"` with your actual Vercel domain

2. **Set environment variable in Vercel**:
   - Go to your Vercel project dashboard
   - Go to Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-app-name.railway.app`

### Step 2: Redeploy Frontend

Your frontend should automatically redeploy when you push changes to GitHub.

## Alternative Backend Deployment Options

### Option 1: Render
- Similar to Railway
- Free tier available
- Good for Python apps

### Option 2: Heroku
- More established platform
- Requires credit card for verification
- Good documentation

### Option 3: DigitalOcean App Platform
- More control
- Pay-as-you-go pricing
- Good performance

## Testing Your Deployment

1. **Test Backend**: Visit `https://your-backend-url.railway.app/api/health`
2. **Test Frontend**: Visit your Vercel URL and check browser console for API calls
3. **Check CORS**: Ensure no CORS errors in browser console

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Make sure your frontend domain is in the allowed origins list
2. **API Timeout**: Railway has request timeouts - optimize your API calls
3. **Environment Variables**: Double-check all environment variables are set correctly

### Debug Steps:

1. Check Railway logs for backend errors
2. Check Vercel deployment logs
3. Use browser developer tools to see API call details
4. Test API endpoints directly using tools like Postman

## Local Development

For local development, your current setup should work:
- Backend: `python app.py` (runs on port 5000)
- Frontend: `npm run dev` (runs on port 5173)

The frontend will automatically use localhost for API calls in development mode.
