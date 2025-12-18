# HealthStats Deployment Guide

## ⚠️ Important: Architecture Considerations

This application **cannot be fully deployed on Vercel as-is** because:

1. **SQLite Database**: Local file-based database won't persist on Vercel's serverless environment
2. **Ollama Requirement**: Local AI service cannot run on Vercel
3. **Long-running processes**: Backend needs persistent connection; Vercel has 10-second timeout

## 🚀 Recommended Deployment Strategy

### Option 1: Split Deployment (Easiest)

**Frontend on Vercel + Backend on Railway/Render**

#### Frontend (Vercel):
```bash
# 1. Push to GitHub (already done)
# 2. Connect repository to Vercel
# 3. Set environment variables in Vercel dashboard:
VITE_API_URL=https://your-backend-url.railway.app/api

# Vercel will auto-deploy from main branch
```

#### Backend (Railway.app):
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Create new project
railway init

# 4. Deploy backend
cd backend
railway up

# 5. Add PostgreSQL database in Railway dashboard
# 6. Update database.py to use PostgreSQL instead of SQLite
# 7. Set environment variables:
DATABASE_URL=postgresql://...
OLLAMA_URL=http://your-ollama-instance:11434
```

### Option 2: Full Self-Hosting (Most Control)

**Deploy on VPS (DigitalOcean, AWS EC2, etc.)**

```bash
# 1. SSH into your server
ssh user@your-server.com

# 2. Clone repository
git clone https://github.com/RonakMehtaa/Health.git
cd Health

# 3. Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Install and setup Ollama
curl https://ollama.ai/install.sh | sh
ollama pull llama3

# 5. Start backend with systemd or PM2
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 6. Setup frontend
cd ../frontend
npm install
npm run build

# 7. Setup Nginx to serve frontend and proxy backend
```

### Option 3: Docker Deployment (Containerized)

```bash
# Create docker-compose.yml in root:
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/healthstats.db:/app/healthstats.db
    environment:
      - OLLAMA_URL=http://ollama:11434
  
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000/api
  
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:

# Deploy:
docker-compose up -d
```

## 📝 Database Migration Required

To deploy backend on cloud platforms, you need to migrate from SQLite to PostgreSQL:

1. Update `backend/app/database.py`:
```python
# Change from:
SQLALCHEMY_DATABASE_URL = "sqlite:///./healthstats.db"

# To:
import os
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./healthstats.db"
)
```

2. Add `psycopg2-binary` to `requirements.txt` for PostgreSQL support

3. Update connection arguments in `create_engine()` for PostgreSQL compatibility

## 🔧 Current Setup (Local Only)

What you have now works perfectly for **local development** but needs modifications for cloud deployment.

## ✅ Quick Deploy Checklist

- [ ] Choose deployment platform (Vercel + Railway recommended)
- [ ] Migrate SQLite to PostgreSQL
- [ ] Deploy Ollama separately (or use alternative AI service)
- [ ] Update environment variables
- [ ] Configure CORS for production URLs
- [ ] Add production security measures (rate limiting, auth)
- [ ] Set up monitoring and logging

## 🌐 Alternative: Vercel Frontend Only

If you want to deploy just the frontend on Vercel now:

```bash
# The vercel.json is already configured
# Just connect your GitHub repo to Vercel

# Then run backend locally or on another server
# and set VITE_API_URL in Vercel environment variables
```

## 📚 Resources

- Railway: https://railway.app (Easy backend hosting)
- Render: https://render.com (Free tier available)
- Fly.io: https://fly.io (Good for databases + apps)
- DigitalOcean: https://digitalocean.com (VPS hosting)
