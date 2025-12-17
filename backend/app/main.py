from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
from typing import List, Optional
import shutil
import os

from app.database import init_db, get_db, SleepRecord, ActivityRecord, VitalsRecord, DerivedMetric
from app.parser import AppleHealthParser
from app.analytics import HealthAnalytics
from app.llm import OllamaClient

app = FastAPI(
    title="HealthStats API",
    description="Apple Health data analytics with local LLM insights",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("Database initialized")

# Initialize Ollama client
ollama_client = OllamaClient()


@app.get("/")
def read_root():
    return {
        "message": "HealthStats API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    ollama_status = await ollama_client.check_connection()
    return {
        "status": "healthy",
        "database": "connected",
        "ollama": "connected" if ollama_status else "disconnected"
    }


@app.post("/api/upload")
async def upload_health_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and parse Apple Health export file (XML or ZIP)"""
    
    # Validate file type
    if not file.filename or not (file.filename.endswith('.xml') or file.filename.endswith('.zip')):
        raise HTTPException(status_code=400, detail="File must be .xml or .zip")
    
    # Save uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse the file
        parser = AppleHealthParser(temp_path)
        parsed_data = parser.parse()
        
        # Store sleep data
        sleep_records_added = 0
        for date_key, sleep_data in parsed_data['sleep'].items():
            existing = db.query(SleepRecord).filter(SleepRecord.date == date_key).first()
            
            if existing:
                # Update existing record
                for key, value in sleep_data.items():
                    setattr(existing, key, value)
            else:
                # Create new record
                record = SleepRecord(date=date_key, **sleep_data)
                db.add(record)
                sleep_records_added += 1
        
        # Store activity data
        activity_records_added = 0
        for date_key, activity_data in parsed_data['activity'].items():
            existing = db.query(ActivityRecord).filter(ActivityRecord.date == date_key).first()
            
            if existing:
                existing.steps = activity_data['steps']
                existing.move_calories = activity_data['calories']
                existing.stand_hours = activity_data['stand_hours']
            else:
                record = ActivityRecord(
                    date=date_key,
                    steps=activity_data['steps'],
                    move_calories=activity_data['calories'],
                    stand_hours=activity_data['stand_hours']
                )
                db.add(record)
                activity_records_added += 1
        
        # Store vitals data
        vitals_records_added = 0
        for date_key, vitals_data in parsed_data['vitals'].items():
            existing = db.query(VitalsRecord).filter(VitalsRecord.date == date_key).first()
            
            if existing:
                for key, value in vitals_data.items():
                    setattr(existing, key, value)
            else:
                record = VitalsRecord(date=date_key, **vitals_data)
                db.add(record)
                vitals_records_added += 1
        
        db.commit()
        
        # Compute derived metrics for all dates
        analytics = HealthAnalytics(db)
        metrics_computed = 0
        
        for date_key in parsed_data['sleep'].keys():
            metrics = analytics.compute_derived_metrics(date_key)
            if metrics:
                existing = db.query(DerivedMetric).filter(DerivedMetric.date == date_key).first()
                if existing:
                    for key, value in metrics.items():
                        setattr(existing, key, value)
                else:
                    metric_record = DerivedMetric(date=date_key, **metrics)
                    db.add(metric_record)
                    metrics_computed += 1
        
        db.commit()
        
        return {
            "message": "Data uploaded successfully",
            "records_added": {
                "sleep": sleep_records_added,
                "activity": activity_records_added,
                "vitals": vitals_records_added,
                "derived_metrics": metrics_computed
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/api/sleep")
def get_sleep_records(days: int = Query(7, ge=1, le=365), db: Session = Depends(get_db)):
    """Get sleep records for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    records = db.query(SleepRecord).filter(
        SleepRecord.date >= start_date,
        SleepRecord.date <= end_date
    ).order_by(SleepRecord.date.desc()).all()
    
    return {
        "records": [
            {
                "date": str(r.date),
                "time_in_bed_minutes": r.time_in_bed_minutes,
                "time_asleep_minutes": r.time_asleep_minutes,
                "awake_minutes": r.awake_minutes,
                "rem_minutes": r.rem_minutes,
                "core_minutes": r.core_minutes,
                "deep_minutes": r.deep_minutes,
                "bedtime": r.bedtime.isoformat() if r.bedtime is not None else None,
                "wake_time": r.wake_time.isoformat() if r.wake_time is not None else None
            }
            for r in records
        ],
        "count": len(records)
    }


@app.get("/api/activity")
def get_activity_records(days: int = Query(7, ge=1, le=365), db: Session = Depends(get_db)):
    """Get activity records for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    records = db.query(ActivityRecord).filter(
        ActivityRecord.date >= start_date,
        ActivityRecord.date <= end_date
    ).order_by(ActivityRecord.date.desc()).all()
    
    return {
        "records": [
            {
                "date": str(r.date),
                "steps": r.steps,
                "move_calories": r.move_calories,
                "stand_hours": r.stand_hours
            }
            for r in records
        ],
        "count": len(records)
    }


@app.get("/api/vitals")
def get_vitals_records(days: int = Query(7, ge=1, le=365), db: Session = Depends(get_db)):
    """Get vitals records for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    records = db.query(VitalsRecord).filter(
        VitalsRecord.date >= start_date,
        VitalsRecord.date <= end_date
    ).order_by(VitalsRecord.date.desc()).all()
    
    return {
        "records": [
            {
                "date": str(r.date),
                "resting_heart_rate": r.resting_heart_rate,
                "sleeping_heart_rate": r.sleeping_heart_rate,
                "respiratory_rate": r.respiratory_rate
            }
            for r in records
        ],
        "count": len(records)
    }


@app.get("/api/metrics/derived")
def get_derived_metrics(days: int = Query(7, ge=1, le=365), db: Session = Depends(get_db)):
    """Get derived metrics for the last N days"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    records = db.query(DerivedMetric).filter(
        DerivedMetric.date >= start_date,
        DerivedMetric.date <= end_date
    ).order_by(DerivedMetric.date.desc()).all()
    
    return {
        "records": [
            {
                "date": str(r.date),
                "sleep_consistency_score": r.sleep_consistency_score,
                "sleep_fragmentation_index": r.sleep_fragmentation_index,
                "rem_percentage": r.rem_percentage,
                "deep_percentage": r.deep_percentage,
                "sleep_efficiency": r.sleep_efficiency
            }
            for r in records
        ],
        "count": len(records)
    }


@app.get("/api/analytics/sleep-summary")
def get_sleep_summary(days: int = Query(7, ge=1, le=365), db: Session = Depends(get_db)):
    """Get sleep analytics summary"""
    analytics = HealthAnalytics(db)
    summary = analytics.get_sleep_summary(days)
    
    if not summary:
        raise HTTPException(status_code=404, detail="No sleep data found")
    
    return summary


@app.get("/api/analytics/activity-summary")
def get_activity_summary(days: int = Query(7, ge=1, le=365), db: Session = Depends(get_db)):
    """Get activity analytics summary"""
    analytics = HealthAnalytics(db)
    summary = analytics.get_activity_summary(days)
    
    if not summary:
        raise HTTPException(status_code=404, detail="No activity data found")
    
    return summary


@app.get("/api/analytics/correlations")
def get_correlations(db: Session = Depends(get_db)):
    """Get correlations between activity and sleep"""
    analytics = HealthAnalytics(db)
    correlations = analytics.get_correlations()
    
    return correlations


@app.post("/api/insights/generate")
async def generate_insights(days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    """Generate AI insights using local LLM"""
    
    analytics = HealthAnalytics(db)
    
    # Gather context
    sleep_summary = analytics.get_sleep_summary(days)
    sleep_summary_30 = analytics.get_sleep_summary(30) if days < 30 else None
    activity_summary = analytics.get_activity_summary(days)
    notable_patterns = analytics.get_notable_patterns(days)
    correlations = analytics.get_correlations()
    
    if not sleep_summary:
        raise HTTPException(status_code=404, detail="Insufficient data for insights")
    
    # Build context for LLM
    context = {
        "sleep_summary": sleep_summary,
        "activity_summary": activity_summary,
        "notable_patterns": notable_patterns,
        "correlations": correlations
    }
    
    # Add 30-day comparison if available
    if sleep_summary_30:
        context["sleep_summary"]["30_day_average"] = sleep_summary_30["30_day_average"]
    
    # Generate insights
    insights = await ollama_client.generate_insights(context)
    
    return {
        **insights,
        "generated_at": datetime.utcnow().isoformat(),
        "context": context
    }


@app.get("/api/stats")
def get_database_stats(db: Session = Depends(get_db)):
    """Get database statistics"""
    sleep_count = db.query(SleepRecord).count()
    activity_count = db.query(ActivityRecord).count()
    vitals_count = db.query(VitalsRecord).count()
    
    # Get date range
    first_sleep = db.query(SleepRecord).order_by(SleepRecord.date.asc()).first()
    last_sleep = db.query(SleepRecord).order_by(SleepRecord.date.desc()).first()
    
    return {
        "total_records": {
            "sleep": sleep_count,
            "activity": activity_count,
            "vitals": vitals_count
        },
        "date_range": {
            "first_date": str(first_sleep.date) if first_sleep else None,
            "last_date": str(last_sleep.date) if last_sleep else None
        }
    }
