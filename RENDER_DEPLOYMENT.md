# Deploy Backend to Render - Step by Step Guide

## 📋 Prerequisites
- GitHub account with your repository pushed
- Render account (sign up at https://render.com - free tier available)

## 🚀 Deployment Steps

### Step 1: Create Render Account
1. Go to https://render.com
2. Click "Get Started" or "Sign Up"
3. Sign up with your GitHub account (easiest option)
4. Authorize Render to access your GitHub repositories

### Step 2: Create PostgreSQL Database
1. From Render Dashboard, click **"New +"** button
2. Select **"PostgreSQL"**
3. Configure database:
   - **Name**: `healthstats-db`
   - **Database**: `healthstats`
   - **User**: `healthstats_user`
   - **Region**: Choose closest to you (e.g., Oregon)
   - **Plan**: Select **"Free"** ($0/month)
4. Click **"Create Database"**
5. Wait for database to provision (takes ~2 minutes)
6. **Important**: Copy the **"Internal Database URL"** - you'll need this later
   - It looks like: `postgresql://user:pass@hostname/database`

### Step 3: Deploy Backend Web Service
1. From Render Dashboard, click **"New +"** button again
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - Click **"Connect a repository"**
   - Find and select **"RonakMehtaa/Health"**
   - Click **"Connect"**

4. Configure the service:
   - **Name**: `healthstats-backend`
   - **Region**: Same as database (e.g., Oregon)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Select **"Free"** ($0/month)

5. Click **"Advanced"** to add environment variables:
   - Click **"Add Environment Variable"**
   - Add these variables:

   **Variable 1:**
   - Key: `DATABASE_URL`
   - Value: Paste the Internal Database URL you copied in Step 2

   **Variable 2:**
   - Key: `PYTHON_VERSION`
   - Value: `3.13.0`

   **Variable 3:**
   - Key: `OLLAMA_URL`
   - Value: `http://localhost:11434`
   - (Note: Ollama won't work on free tier, but app will still run without AI insights)

6. Click **"Create Web Service"**

### Step 4: Wait for Deployment
1. Render will start building your backend
2. You'll see the build logs in real-time
3. First deployment takes 5-10 minutes
4. Wait until you see: **"Your service is live 🎉"**

### Step 5: Get Your Backend URL
1. Once deployed, you'll see your service URL at the top
2. It will look like: `https://healthstats-backend.onrender.com`
3. **Copy this URL** - you'll need it for Vercel

### Step 6: Test Your Backend
1. Open your backend URL in a browser
2. Add `/docs` to the end: `https://healthstats-backend.onrender.com/docs`
3. You should see the FastAPI interactive documentation
4. Test the `/api/health` endpoint - it should return:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "ollama": "disconnected"
   }
   ```

### Step 7: Update Vercel with Backend URL
1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Click on your **"healthstats"** project
3. Go to **"Settings"** tab
4. Click **"Environment Variables"** in the left sidebar
5. Add a new variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://healthstats-backend.onrender.com/api`
   - **Environment**: Select all (Production, Preview, Development)
6. Click **"Save"**
7. Go to **"Deployments"** tab
8. Click the **3 dots** on the latest deployment
9. Click **"Redeploy"** to apply the new environment variable

### Step 8: Update CORS in Backend (Important!)
1. Your frontend now needs to be allowed to access the backend
2. Go to your Render dashboard
3. Click on your **"healthstats-backend"** service
4. Go to **"Environment"** tab
5. Add a new environment variable:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `https://your-vercel-app.vercel.app`
   - (Replace with your actual Vercel URL)
6. Click **"Save Changes"**
7. Render will automatically redeploy

Alternatively, you can update the CORS settings in your code:
```python
# In backend/app/main.py, update the CORS origins:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://your-vercel-app.vercel.app"  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 9: Test the Full Application
1. Open your Vercel frontend URL
2. Try uploading Apple Health data
3. Check if data appears in Sleep and Activity tabs
4. Everything should work! 🎉

## ⚠️ Important Notes

### Free Tier Limitations:
- **Backend sleeps after 15 minutes of inactivity**
  - First request after sleep takes 30-60 seconds to wake up
  - This is normal for free tier
- **Database**: 1GB storage, 97 hours/month compute time
- **Ollama AI won't work** on free tier (needs 4GB+ RAM, free tier has 512MB)
  - Your app will work, but "Generate Insights" won't function
  - To enable AI: Upgrade to paid plan or self-host Ollama separately

### Database Connection String:
- Render provides two URLs:
  - **Internal Database URL**: Use this in your backend (faster, private network)
  - **External Database URL**: For connecting from your local machine

### Monitoring Your App:
- Check Render dashboard for logs
- Monitor errors in the "Logs" tab of your service
- Set up email alerts in Settings

## 🔧 Troubleshooting

### Build Failed:
- Check the build logs in Render dashboard
- Ensure `requirements.txt` is correct
- Verify Python version is set to 3.13.0

### Database Connection Error:
- Verify `DATABASE_URL` is set correctly
- Make sure you're using the **Internal Database URL**
- Check database is in the same region as web service

### CORS Error in Browser:
- Add your Vercel URL to CORS origins
- Redeploy after updating CORS settings

### Backend is Slow:
- Free tier sleeps after 15 minutes of inactivity
- First request wakes it up (takes 30-60 seconds)
- Upgrade to paid plan for always-on service

## 💰 Cost Breakdown

**Free Tier (What you're using):**
- PostgreSQL Database: $0/month
- Web Service: $0/month
- **Total: $0/month** ✅

**If you upgrade later:**
- PostgreSQL (Starter): $7/month
- Web Service (Starter): $7/month
- **Total: $14/month** for always-on service with more resources

## 🎯 Your URLs After Deployment

- **Frontend (Vercel)**: `https://your-app.vercel.app`
- **Backend (Render)**: `https://healthstats-backend.onrender.com`
- **API Docs**: `https://healthstats-backend.onrender.com/docs`
- **Database**: Managed by Render (internal)

## ✅ Success Checklist

- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Backend web service deployed
- [ ] Backend URL copied
- [ ] `VITE_API_URL` added to Vercel
- [ ] Vercel redeployed
- [ ] CORS updated with Vercel URL
- [ ] Full app tested and working

Congratulations! Your HealthStats app is now live on the internet! 🚀
