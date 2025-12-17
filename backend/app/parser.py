import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Dict, List, Tuple
from collections import defaultdict
import zipfile
import os
from dateutil import parser as date_parser


class AppleHealthParser:
    """Parse Apple Health export XML and extract health data"""
    
    # Apple Health record type identifiers
    SLEEP_ANALYSIS = "HKCategoryTypeIdentifierSleepAnalysis"
    STEP_COUNT = "HKQuantityTypeIdentifierStepCount"
    ACTIVE_ENERGY = "HKQuantityTypeIdentifierActiveEnergyBurned"
    STAND_HOUR = "HKQuantityTypeIdentifierAppleStandHour"
    HEART_RATE = "HKQuantityTypeIdentifierHeartRate"
    RESPIRATORY_RATE = "HKQuantityTypeIdentifierRespiratoryRate"
    
    # Sleep stage values
    SLEEP_STAGES = {
        "HKCategoryValueSleepAnalysisAsleepUnspecified": "asleep",
        "HKCategoryValueSleepAnalysisAsleepCore": "core",
        "HKCategoryValueSleepAnalysisAsleepDeep": "deep",
        "HKCategoryValueSleepAnalysisAsleepREM": "rem",
        "HKCategoryValueSleepAnalysisAwake": "awake",
        "HKCategoryValueSleepAnalysisInBed": "in_bed"
    }
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.is_zip = file_path.endswith('.zip')
        
    def parse(self) -> Dict:
        """Main parsing method"""
        if self.is_zip:
            return self._parse_zip()
        else:
            return self._parse_xml(self.file_path)
    
    def _parse_zip(self) -> Dict:
        """Extract and parse export.xml from zip file"""
        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            # Look for export.xml in the zip
            xml_file = None
            for name in zip_ref.namelist():
                if name.endswith('export.xml'):
                    xml_file = name
                    break
            
            if not xml_file:
                raise ValueError("No export.xml found in zip file")
            
            # Extract to temp location
            temp_path = "/tmp/export_temp.xml"
            with zip_ref.open(xml_file) as source, open(temp_path, 'wb') as target:
                target.write(source.read())
            
            result = self._parse_xml(temp_path)
            
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return result
    
    def _parse_xml(self, xml_path: str) -> Dict:
        """Parse Apple Health XML file"""
        print(f"Parsing XML file: {xml_path}")
        
        sleep_data = []
        activity_data = defaultdict(lambda: {'steps': 0, 'calories': 0, 'stand_hours': 0})
        vitals_data = defaultdict(lambda: {'heart_rates': [], 'respiratory_rates': []})
        
        # Use iterparse for memory efficiency with large files
        context = ET.iterparse(xml_path, events=('start', 'end'))
        context = iter(context)
        
        for event, elem in context:
            if event == 'end':
                if elem.tag == 'Record':
                    record_type = elem.get('type')
                    
                    # Sleep data
                    if record_type == self.SLEEP_ANALYSIS:
                        sleep_data.append(self._parse_sleep_record(elem))
                    
                    # Activity data
                    elif record_type == self.STEP_COUNT:
                        self._parse_steps(elem, activity_data)
                    
                    elif record_type == self.ACTIVE_ENERGY:
                        self._parse_calories(elem, activity_data)
                    
                    elif record_type == self.STAND_HOUR:
                        self._parse_stand_hours(elem, activity_data)
                    
                    # Vitals
                    elif record_type == self.HEART_RATE:
                        self._parse_heart_rate(elem, vitals_data)
                    
                    elif record_type == self.RESPIRATORY_RATE:
                        self._parse_respiratory_rate(elem, vitals_data)
                
                # Clear element to save memory
                elem.clear()
        
        # Aggregate sleep data by date
        aggregated_sleep = self._aggregate_sleep_data(sleep_data)
        
        # Process vitals data
        processed_vitals = self._process_vitals(vitals_data)
        
        return {
            'sleep': aggregated_sleep,
            'activity': dict(activity_data),
            'vitals': processed_vitals
        }
    
    def _parse_sleep_record(self, elem) -> Dict:
        """Parse a single sleep record"""
        start = elem.get('startDate')
        end = elem.get('endDate')
        value = elem.get('value')
        
        start_dt = date_parser.parse(start)
        end_dt = date_parser.parse(end)
        duration_minutes = (end_dt - start_dt).total_seconds() / 60
        
        stage = self.SLEEP_STAGES.get(value, 'unknown')
        
        return {
            'start': start_dt,
            'end': end_dt,
            'duration_minutes': duration_minutes,
            'stage': stage,
            'date': start_dt.date()
        }
    
    def _aggregate_sleep_data(self, sleep_records: List[Dict]) -> Dict:
        """Aggregate sleep records by date"""
        daily_sleep = defaultdict(lambda: {
            'time_in_bed_minutes': 0,
            'time_asleep_minutes': 0,
            'awake_minutes': 0,
            'rem_minutes': 0,
            'core_minutes': 0,
            'deep_minutes': 0,
            'bedtime': None,
            'wake_time': None
        })
        
        for record in sleep_records:
            record_date = record['date']
            stage = record['stage']
            duration = record['duration_minutes']
            
            # Track bedtime and wake time
            if daily_sleep[record_date]['bedtime'] is None or record['start'] < daily_sleep[record_date]['bedtime']:
                daily_sleep[record_date]['bedtime'] = record['start']
            
            if daily_sleep[record_date]['wake_time'] is None or record['end'] > daily_sleep[record_date]['wake_time']:
                daily_sleep[record_date]['wake_time'] = record['end']
            
            # Accumulate durations by stage
            if stage == 'in_bed':
                daily_sleep[record_date]['time_in_bed_minutes'] += duration
            elif stage == 'asleep':
                daily_sleep[record_date]['time_asleep_minutes'] += duration
            elif stage == 'awake':
                daily_sleep[record_date]['awake_minutes'] += duration
            elif stage == 'rem':
                daily_sleep[record_date]['rem_minutes'] += duration
                daily_sleep[record_date]['time_asleep_minutes'] += duration
            elif stage == 'core':
                daily_sleep[record_date]['core_minutes'] += duration
                daily_sleep[record_date]['time_asleep_minutes'] += duration
            elif stage == 'deep':
                daily_sleep[record_date]['deep_minutes'] += duration
                daily_sleep[record_date]['time_asleep_minutes'] += duration
        
        return dict(daily_sleep)
    
    def _parse_steps(self, elem, activity_data):
        """Parse step count"""
        start_date = date_parser.parse(elem.get('startDate')).date()
        value = float(elem.get('value', 0))
        activity_data[start_date]['steps'] += int(value)
    
    def _parse_calories(self, elem, activity_data):
        """Parse active energy burned"""
        start_date = date_parser.parse(elem.get('startDate')).date()
        value = float(elem.get('value', 0))
        activity_data[start_date]['calories'] += value
    
    def _parse_stand_hours(self, elem, activity_data):
        """Parse stand hours"""
        start_date = date_parser.parse(elem.get('startDate')).date()
        value = int(float(elem.get('value', 0)))
        if value > 0:
            activity_data[start_date]['stand_hours'] += 1
    
    def _parse_heart_rate(self, elem, vitals_data):
        """Parse heart rate"""
        start_date = date_parser.parse(elem.get('startDate')).date()
        value = float(elem.get('value', 0))
        vitals_data[start_date]['heart_rates'].append(value)
    
    def _parse_respiratory_rate(self, elem, vitals_data):
        """Parse respiratory rate"""
        start_date = date_parser.parse(elem.get('startDate')).date()
        value = float(elem.get('value', 0))
        vitals_data[start_date]['respiratory_rates'].append(value)
    
    def _process_vitals(self, vitals_data: Dict) -> Dict:
        """Process vitals data to get daily averages"""
        processed = {}
        
        for date_key, data in vitals_data.items():
            processed[date_key] = {}
            
            # Calculate resting heart rate (approximate as lowest daytime HR)
            if data['heart_rates']:
                processed[date_key]['resting_heart_rate'] = min(data['heart_rates'])
                processed[date_key]['sleeping_heart_rate'] = sum(data['heart_rates']) / len(data['heart_rates'])
            
            # Average respiratory rate
            if data['respiratory_rates']:
                processed[date_key]['respiratory_rate'] = sum(data['respiratory_rates']) / len(data['respiratory_rates'])
        
        return processed
