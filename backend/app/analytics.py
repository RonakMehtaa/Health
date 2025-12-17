from datetime import date, timedelta
from typing import Dict, List, Optional
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import SleepRecord, ActivityRecord, VitalsRecord, DerivedMetric


class HealthAnalytics:
    """Compute derived metrics and analyze health data trends"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def compute_derived_metrics(self, target_date: date) -> Optional[Dict]:
        """Compute derived metrics for a specific date"""
        sleep_record = self.db.query(SleepRecord).filter(
            SleepRecord.date == target_date
        ).first()
        
        if not sleep_record:
            return None
        
        metrics = {}
        
        # Sleep fragmentation index (awake time / time in bed)
        if sleep_record.time_in_bed_minutes and sleep_record.time_in_bed_minutes > 0:
            metrics['sleep_fragmentation_index'] = (
                sleep_record.awake_minutes / sleep_record.time_in_bed_minutes
            ) * 100
        else:
            metrics['sleep_fragmentation_index'] = 0
        
        # REM percentage
        if sleep_record.time_asleep_minutes and sleep_record.time_asleep_minutes > 0:
            metrics['rem_percentage'] = (
                sleep_record.rem_minutes / sleep_record.time_asleep_minutes
            ) * 100
        else:
            metrics['rem_percentage'] = 0
        
        # Deep percentage
        if sleep_record.time_asleep_minutes and sleep_record.time_asleep_minutes > 0:
            metrics['deep_percentage'] = (
                sleep_record.deep_minutes / sleep_record.time_asleep_minutes
            ) * 100
        else:
            metrics['deep_percentage'] = 0
        
        # Sleep efficiency (time asleep / time in bed)
        if sleep_record.time_in_bed_minutes and sleep_record.time_in_bed_minutes > 0:
            metrics['sleep_efficiency'] = (
                sleep_record.time_asleep_minutes / sleep_record.time_in_bed_minutes
            ) * 100
        else:
            metrics['sleep_efficiency'] = 0
        
        # Sleep consistency score (based on bedtime variance)
        metrics['sleep_consistency_score'] = self._calculate_consistency_score(target_date)
        
        return metrics
    
    def _calculate_consistency_score(self, target_date: date, days: int = 7) -> float:
        """Calculate sleep consistency based on bedtime variance"""
        start_date = target_date - timedelta(days=days)
        
        records = self.db.query(SleepRecord).filter(
            and_(
                SleepRecord.date >= start_date,
                SleepRecord.date <= target_date,
                SleepRecord.bedtime.isnot(None)
            )
        ).all()
        
        if len(records) < 2:
            return 100.0
        
        # Extract hour + minute as decimal hours
        bedtimes = []
        for record in records:
            hour = record.bedtime.hour + record.bedtime.minute / 60
            bedtimes.append(hour)
        
        # Calculate standard deviation
        std_dev = np.std(bedtimes)
        
        # Convert to consistency score (0-100, higher is more consistent)
        # std_dev of 0 = 100, std_dev of 3 hours = 0
        consistency = max(0, 100 - (std_dev * 33.33))
        
        return round(consistency, 2)
    
    def get_sleep_summary(self, days: int = 7) -> Optional[Dict]:
        """Get sleep summary for the last N days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        records = self.db.query(SleepRecord).filter(
            and_(
                SleepRecord.date >= start_date,
                SleepRecord.date <= end_date
            )
        ).order_by(SleepRecord.date.desc()).all()
        
        if not records:
            return None
        
        last_night = records[0] if records else None
        
        # Calculate averages
        avg_time_asleep = np.mean([r.time_asleep_minutes for r in records if r.time_asleep_minutes])
        avg_rem = np.mean([r.rem_minutes for r in records if r.rem_minutes])
        avg_deep = np.mean([r.deep_minutes for r in records if r.deep_minutes])
        avg_awake = np.mean([r.awake_minutes for r in records if r.awake_minutes])
        
        total_asleep = sum([r.time_asleep_minutes for r in records if r.time_asleep_minutes])
        
        return {
            'last_night': {
                'date': str(last_night.date) if last_night else None,
                'time_asleep_hours': round(last_night.time_asleep_minutes / 60, 1) if last_night and last_night.time_asleep_minutes else 0,
                'rem_minutes': round(last_night.rem_minutes, 1) if last_night and last_night.rem_minutes else 0,
                'deep_minutes': round(last_night.deep_minutes, 1) if last_night and last_night.deep_minutes else 0,
                'core_minutes': round(last_night.core_minutes, 1) if last_night and last_night.core_minutes else 0,
                'awake_minutes': round(last_night.awake_minutes, 1) if last_night and last_night.awake_minutes else 0,
                'bedtime': last_night.bedtime.strftime('%H:%M') if last_night and last_night.bedtime else None,
                'wake_time': last_night.wake_time.strftime('%H:%M') if last_night and last_night.wake_time else None,
                'rem_percentage': round((last_night.rem_minutes / last_night.time_asleep_minutes * 100), 1) if last_night and last_night.time_asleep_minutes and last_night.rem_minutes else 0,
                'deep_percentage': round((last_night.deep_minutes / last_night.time_asleep_minutes * 100), 1) if last_night and last_night.time_asleep_minutes and last_night.deep_minutes else 0,
            },
            f'{days}_day_average': {
                'time_asleep_hours': round(avg_time_asleep / 60, 1) if avg_time_asleep else 0,
                'rem_minutes': round(avg_rem, 1) if avg_rem else 0,
                'deep_minutes': round(avg_deep, 1) if avg_deep else 0,
                'awake_minutes': round(avg_awake, 1) if avg_awake else 0,
                'rem_percentage': round((avg_rem / avg_time_asleep * 100), 1) if avg_time_asleep and avg_rem else 0,
                'deep_percentage': round((avg_deep / avg_time_asleep * 100), 1) if avg_time_asleep and avg_deep else 0,
            },
            'total_records': len(records)
        }
    
    def get_activity_summary(self, days: int = 7) -> Optional[Dict]:
        """Get activity summary for the last N days"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        records = self.db.query(ActivityRecord).filter(
            and_(
                ActivityRecord.date >= start_date,
                ActivityRecord.date <= end_date
            )
        ).order_by(ActivityRecord.date.desc()).all()
        
        if not records:
            return None
        
        yesterday = records[0] if records else None
        
        avg_steps = np.mean([r.steps for r in records if r.steps])
        avg_calories = np.mean([r.move_calories for r in records if r.move_calories])
        avg_stand_hours = np.mean([r.stand_hours for r in records if r.stand_hours])
        
        return {
            'yesterday': {
                'date': str(yesterday.date) if yesterday else None,
                'steps': yesterday.steps if yesterday else 0,
                'move_calories': round(yesterday.move_calories, 1) if yesterday and yesterday.move_calories else 0,
                'stand_hours': yesterday.stand_hours if yesterday else 0
            },
            f'{days}_day_average': {
                'steps': int(avg_steps) if not np.isnan(avg_steps) else 0,
                'move_calories': round(avg_calories, 1) if not np.isnan(avg_calories) else 0,
                'stand_hours': int(avg_stand_hours) if not np.isnan(avg_stand_hours) else 0
            },
            'total_records': len(records)
        }
    
    def get_notable_patterns(self, days: int = 7) -> List[str]:
        """Identify notable patterns in recent data"""
        patterns = []
        
        sleep_summary = self.get_sleep_summary(days)
        activity_summary = self.get_activity_summary(days)
        
        if not sleep_summary or not activity_summary:
            return patterns
        
        # Sleep duration comparison
        last_night_hours = sleep_summary['last_night']['time_asleep_hours']
        avg_hours = sleep_summary[f'{days}_day_average']['time_asleep_hours']
        
        if last_night_hours and avg_hours:
            diff = last_night_hours - avg_hours
            if abs(diff) > 0.5:
                direction = "increased" if diff > 0 else "decreased"
                patterns.append(
                    f"Sleep duration {direction} by {abs(diff * 60):.0f} minutes compared to {days}-day average"
                )
        
        # REM percentage comparison
        last_rem_pct = sleep_summary['last_night']['rem_percentage']
        avg_rem_pct = sleep_summary[f'{days}_day_average']['rem_percentage']
        
        if last_rem_pct and avg_rem_pct:
            diff = last_rem_pct - avg_rem_pct
            if abs(diff) > 2:
                direction = "increased" if diff > 0 else "decreased"
                patterns.append(
                    f"REM percentage {direction} by {abs(diff):.1f}% compared to {days}-day average"
                )
        
        # Deep sleep comparison
        last_deep_pct = sleep_summary['last_night']['deep_percentage']
        avg_deep_pct = sleep_summary[f'{days}_day_average']['deep_percentage']
        
        if last_deep_pct and avg_deep_pct:
            diff = last_deep_pct - avg_deep_pct
            if abs(diff) > 2:
                direction = "increased" if diff > 0 else "decreased"
                patterns.append(
                    f"Deep sleep percentage {direction} by {abs(diff):.1f}% compared to {days}-day average"
                )
        
        # Activity level comparison
        yesterday_steps = activity_summary['yesterday']['steps']
        avg_steps = activity_summary[f'{days}_day_average']['steps']
        
        if yesterday_steps and avg_steps:
            diff_pct = ((yesterday_steps - avg_steps) / avg_steps) * 100
            if abs(diff_pct) > 10:
                direction = "above" if diff_pct > 0 else "below"
                patterns.append(
                    f"Activity levels {abs(diff_pct):.1f}% {direction} recent average"
                )
        
        return patterns
    
    def get_correlations(self) -> Dict:
        """Calculate correlations between activity and sleep"""
        # Get last 30 days of data
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        sleep_records = self.db.query(SleepRecord).filter(
            and_(
                SleepRecord.date >= start_date,
                SleepRecord.date <= end_date
            )
        ).all()
        
        activity_records = self.db.query(ActivityRecord).filter(
            and_(
                ActivityRecord.date >= start_date,
                ActivityRecord.date <= end_date
            )
        ).all()
        
        # Build date-aligned data
        sleep_dict = {r.date: r for r in sleep_records}
        activity_dict = {r.date: r for r in activity_records}
        
        steps_list = []
        sleep_duration_list = []
        sleep_quality_list = []
        
        for d in [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]:
            if d in sleep_dict and d in activity_dict:
                if sleep_dict[d].time_asleep_minutes and activity_dict[d].steps:
                    steps_list.append(activity_dict[d].steps)
                    sleep_duration_list.append(sleep_dict[d].time_asleep_minutes / 60)
                    
                    # Sleep quality proxy: deep + REM percentage
                    total_sleep = sleep_dict[d].time_asleep_minutes
                    quality = 0
                    if total_sleep > 0:
                        quality = ((sleep_dict[d].deep_minutes or 0) + (sleep_dict[d].rem_minutes or 0)) / total_sleep * 100
                    sleep_quality_list.append(quality)
        
        correlations = {}
        
        if len(steps_list) > 5:
            # Correlation between steps and sleep duration
            corr_duration = np.corrcoef(steps_list, sleep_duration_list)[0, 1]
            correlations['steps_sleep_duration'] = round(float(corr_duration), 3)
            
            # Correlation between steps and sleep quality
            if sleep_quality_list:
                corr_quality = np.corrcoef(steps_list, sleep_quality_list)[0, 1]
                correlations['steps_sleep_quality'] = round(float(corr_quality), 3)
        
        return correlations
