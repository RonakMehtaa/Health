# HealthStats - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Prerequisites

#### Install Ollama (Required for AI insights)
```bash
# macOS
brew install ollama

# Or download from: https://ollama.ai
```

#### Install Python 3.10+ and Node.js 18+
Check if already installed:
```bash
python3 --version
node --version
```

### Step 2: Set Up Backend

```bash
# Navigate to project directory
cd HealthStats/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Set Up Frontend

```bash
# Open a new terminal and navigate to frontend
cd HealthStats/frontend

# Install Node dependencies
npm install
```

### Step 4: Start Ollama

```bash
# Open a new terminal
ollama serve

# In another terminal, pull the model (first time only)
ollama pull llama3
```

### Step 5: Start the Application

#### Terminal 1 - Backend:
```bash
cd HealthStats/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 - Frontend:
```bash
cd HealthStats/frontend
npm run dev
```

### Step 6: Access the Application

Open your browser and go to: **http://localhost:5173**

---

## 📱 Export Apple Health Data

1. Open the **Health** app on your iPhone
2. Tap your **profile picture** (top right)
3. Scroll down and tap **"Export All Health Data"**
4. Share the `export.zip` file to your computer (via AirDrop, email, etc.)

---

## 💻 Using the Application

### Upload Data
1. Go to the **Dashboard**
2. Click **"Choose File"**
3. Select your `export.zip` or `export.xml`
4. Wait for processing (may take 1-2 minutes for large files)

### View Sleep Analysis
- Navigate to **Sleep** tab
- View detailed sleep stages, duration, and quality metrics
- Switch between 7, 14, and 30-day views

### Check Activity
- Navigate to **Activity** tab
- View steps, calories, and stand hours
- Compare daily trends

### Generate AI Insights
- Navigate to **Insights** tab
- Ensure Ollama status shows "connected"
- Click **"Generate Insights"**
- Wait 30-60 seconds for AI analysis

---

## 🔧 Troubleshooting

### "Ollama: disconnected"
```bash
# Make sure Ollama is running
ollama serve
```

### Backend won't start
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Upload fails
- Ensure file is valid Apple Health export (.xml or .zip)
- Check backend terminal for error messages
- File should be less than 500MB

---

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🛑 Stopping the Application

1. Press `Ctrl+C` in each terminal window
2. Deactivate virtual environment: `deactivate`
3. Stop Ollama if desired: `Ctrl+C` in Ollama terminal

---

## 📝 Notes

- All data is stored locally in `backend/healthstats.db` (SQLite)
- No data is sent to external services (except local Ollama)
- First AI insight generation may be slower as model initializes
- Ollama models are stored in `~/.ollama/models/`

---

## 🎯 Next Steps

- Upload your Apple Health data
- Explore sleep patterns over different time periods
- Generate AI insights to understand your trends
- Check correlations between activity and sleep quality

Enjoy analyzing your health data! 🏃‍♂️😴📈
