# HealthStats - Apple Health Data Analytics

A privacy-first, local web application for analyzing Apple Health data with AI-powered insights using Ollama.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  - Dashboard (overview, last night summary, 7-day trends)   │
│  - Sleep Analysis (stages, breakdown, timeline)             │
│  - Activity Tracking (steps, calories, stand hours)         │
│  - AI Insights (LLM-generated trend analysis)               │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                   Backend (FastAPI + Python)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ API Layer                                            │   │
│  │ - Upload endpoint                                    │   │
│  │ - Metrics endpoints                                  │   │
│  │ - Insights endpoint                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Analysis Layer                                       │   │
│  │ - Derived metrics calculator                        │   │
│  │ - Trend analyzer                                     │   │
│  │ - Correlation engine                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Data Layer                                           │   │
│  │ - Apple Health XML parser                           │   │
│  │ - Data normalizer                                    │   │
│  │ - SQLite persistence                                 │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP API
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    Ollama (Local LLM)                        │
│  - Model: llama3 / mistral                                  │
│  - Generates neutral, factual insights                      │
│  - No medical advice or coaching                            │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI (REST API)
- SQLAlchemy (ORM)
- Pandas/NumPy (data analysis)
- SQLite (database)
- python-multipart (file uploads)

**Frontend:**
- React 18
- Recharts (visualization)
- Axios (API client)
- TailwindCSS (styling)

**AI:**
- Ollama (local LLM runtime)
- llama3 or mistral model

## Database Schema

### Tables

**sleep_records**
```sql
id: INTEGER PRIMARY KEY
date: DATE UNIQUE
time_in_bed_minutes: FLOAT
time_asleep_minutes: FLOAT
awake_minutes: FLOAT
rem_minutes: FLOAT
core_minutes: FLOAT
deep_minutes: FLOAT
bedtime: TIMESTAMP
wake_time: TIMESTAMP
```

**activity_records**
```sql
id: INTEGER PRIMARY KEY
date: DATE UNIQUE
steps: INTEGER
move_calories: FLOAT
stand_hours: INTEGER
```

**vitals_records**
```sql
id: INTEGER PRIMARY KEY
date: DATE UNIQUE
resting_heart_rate: FLOAT
sleeping_heart_rate: FLOAT
respiratory_rate: FLOAT
```

**derived_metrics**
```sql
id: INTEGER PRIMARY KEY
date: DATE UNIQUE
sleep_consistency_score: FLOAT
sleep_fragmentation_index: FLOAT
rem_percentage: FLOAT
deep_percentage: FLOAT
sleep_efficiency: FLOAT
```

## Apple Health XML Parsing Strategy

1. **Parse XML structure**: Use ElementTree to parse `export.xml`
2. **Extract Record types**:
   - `HKCategoryTypeIdentifierSleepAnalysis` (sleep stages)
   - `HKQuantityTypeIdentifierStepCount`
   - `HKQuantityTypeIdentifierActiveEnergyBurned`
   - `HKQuantityTypeIdentifierAppleStandHour`
   - `HKQuantityTypeIdentifierHeartRate`
   - `HKQuantityTypeIdentifierRespiratoryRate`
3. **Aggregate by date**: Group overlapping sleep sessions, sum daily activities
4. **Normalize units**: Convert all to consistent units (minutes, steps, bpm)
5. **Store in database**: Batch insert normalized records

## API Endpoints

### Upload
- `POST /api/upload` - Upload Apple Health export (XML or ZIP)

### Data Retrieval
- `GET /api/sleep?days=7` - Get sleep records
- `GET /api/activity?days=7` - Get activity records
- `GET /api/vitals?days=7` - Get vitals records
- `GET /api/metrics/derived?days=7` - Get derived metrics

### Analytics
- `GET /api/analytics/sleep-summary` - Last night + trends
- `GET /api/analytics/activity-summary` - Activity trends
- `GET /api/analytics/correlations` - Activity-sleep correlations

### AI
- `POST /api/insights/generate` - Generate LLM insights

## Example JSON sent to Ollama

```json
{
  "prompt": "Explain patterns and trends in the following sleep and activity metrics using neutral, factual language. Do not provide advice or diagnosis.",
  "context": {
    "sleep_summary": {
      "last_night": {
        "date": "2025-12-16",
        "time_asleep_hours": 7.2,
        "rem_percentage": 22.5,
        "deep_percentage": 18.3,
        "awake_minutes": 15,
        "bedtime": "23:15",
        "wake_time": "06:45"
      },
      "7_day_average": {
        "time_asleep_hours": 7.5,
        "rem_percentage": 21.8,
        "deep_percentage": 19.1
      },
      "30_day_average": {
        "time_asleep_hours": 7.3,
        "rem_percentage": 22.0,
        "deep_percentage": 18.8
      }
    },
    "activity_summary": {
      "yesterday": {
        "steps": 8234,
        "move_calories": 456
      },
      "7_day_average": {
        "steps": 9102,
        "move_calories": 512
      }
    },
    "notable_patterns": [
      "REM percentage increased by 3.2% compared to 7-day average",
      "Sleep duration decreased by 18 minutes compared to 7-day average",
      "Activity levels 9.5% below recent average"
    ]
  }
}
```

## Example LLM Response

```json
{
  "insights": [
    {
      "category": "sleep_duration",
      "observation": "Sleep duration was 7.2 hours, which is 18 minutes below the recent 7-day average of 7.5 hours and close to the 30-day baseline of 7.3 hours."
    },
    {
      "category": "sleep_stages",
      "observation": "REM sleep comprised 22.5% of total sleep time, representing a 3.2% increase from the 7-day average. Deep sleep at 18.3% was slightly below the recent average of 19.1%."
    },
    {
      "category": "activity_correlation",
      "observation": "Daily step count was 9.5% below the 7-day average. Lower physical activity sometimes correlates with altered sleep architecture."
    }
  ],
  "summary": "Recent sleep patterns show minor variation from baseline with increased REM percentage and reduced deep sleep. Total sleep duration remains within typical range."
}
```

## Local Setup Instructions

### Prerequisites
1. **Install Python 3.10+**
2. **Install Node.js 18+**
3. **Install Ollama**: https://ollama.ai
   ```bash
   # macOS
   brew install ollama
   ```

### Backend Setup

```bash
# Navigate to project root
cd HealthStats

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run backend server
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd HealthStats/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### Ollama Setup

```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull llama3

# Test the model
ollama run llama3
```

### Export Apple Health Data

1. Open Health app on iPhone
2. Tap profile picture (top right)
3. Scroll down and tap "Export All Health Data"
4. Share the `export.zip` file to your computer
5. Upload via the web interface at http://localhost:5173

## Usage

1. **Upload Data**: Navigate to Dashboard and upload your `export.zip`
2. **View Dashboard**: See last night summary and 7-day trends
3. **Explore Sleep**: Detailed sleep stage breakdown and patterns
4. **Check Activity**: Steps, calories, and stand hours visualization
5. **Read Insights**: AI-generated neutral observations about your trends

## Privacy & Data

- All data stored locally in SQLite database
- No external API calls except to local Ollama
- No cloud storage or telemetry
- Single-user deployment

## Development

- Backend API docs: http://localhost:8000/docs
- Frontend dev server with hot reload
- SQLite database: `backend/healthstats.db`
