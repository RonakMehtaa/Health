from sqlalchemy import Column, Integer, Float, String, Date, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class SleepRecord(Base):
    __tablename__ = "sleep_records"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    time_in_bed_minutes = Column(Float)
    time_asleep_minutes = Column(Float)
    awake_minutes = Column(Float)
    rem_minutes = Column(Float)
    core_minutes = Column(Float)
    deep_minutes = Column(Float)
    bedtime = Column(DateTime)
    wake_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class ActivityRecord(Base):
    __tablename__ = "activity_records"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    steps = Column(Integer, default=0)
    move_calories = Column(Float, default=0.0)
    stand_hours = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class VitalsRecord(Base):
    __tablename__ = "vitals_records"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    resting_heart_rate = Column(Float)
    sleeping_heart_rate = Column(Float)
    respiratory_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class DerivedMetric(Base):
    __tablename__ = "derived_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    sleep_consistency_score = Column(Float)
    sleep_fragmentation_index = Column(Float)
    rem_percentage = Column(Float)
    deep_percentage = Column(Float)
    sleep_efficiency = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./healthstats.db")

# Handle SQLite vs PostgreSQL connection arguments
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL or other databases don't need check_same_thread
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
