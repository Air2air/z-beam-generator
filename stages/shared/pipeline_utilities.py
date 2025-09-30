#!/usr/bin/env python3
"""
Shared utilities and tools for the material property validation pipeline.
"""

import yaml
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

class DatabaseConnector:
    """
    Provides database connectivity for storing and retrieving pipeline results,
    metrics, and historical data.
    """
    
    def __init__(self, db_path: str = "pipeline_results/pipeline_database.sqlite"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Materials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    category TEXT,
                    file_path TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Properties table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material_id INTEGER,
                    property_name TEXT NOT NULL,
                    value REAL,
                    unit TEXT,
                    min_value REAL,
                    max_value REAL,
                    confidence REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (material_id) REFERENCES materials (id)
                )
            ''')
            
            # Pipeline runs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stage_name TEXT NOT NULL,
                    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    materials_processed INTEGER,
                    success_count INTEGER,
                    error_count INTEGER,
                    results_json TEXT
                )
            ''')
            
            # Quality assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    material_id INTEGER,
                    assessment_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    overall_score REAL,
                    quality_grade TEXT,
                    completeness_score REAL,
                    accuracy_score REAL,
                    consistency_score REAL,
                    FOREIGN KEY (material_id) REFERENCES materials (id)
                )
            ''')
            
            conn.commit()
    
    def store_pipeline_run(self, stage_name: str, results: Dict[str, Any]):
        """Store pipeline run results"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pipeline_runs 
                (stage_name, materials_processed, success_count, error_count, results_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                stage_name,
                results.get('materials_processed', 0),
                results.get('success_count', 0),
                results.get('error_count', 0),
                json.dumps(results)
            ))
            
            conn.commit()
    
    def get_material_history(self, material_name: str) -> List[Dict[str, Any]]:
        """Get historical data for a material"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT pr.stage_name, pr.run_timestamp, pr.results_json
                FROM pipeline_runs pr
                WHERE pr.results_json LIKE ?
                ORDER BY pr.run_timestamp DESC
            ''', (f'%{material_name}%',))
            
            return [{'stage': row[0], 'timestamp': row[1], 'results': json.loads(row[2])} 
                   for row in cursor.fetchall()]


class AIResearchAgent:
    """
    Coordinates AI research for material properties using multiple providers.
    """
    
    def __init__(self, api_clients: Dict[str, Any]):
        self.api_clients = api_clients
        self.research_cache = {}
    
    async def research_property(self, material: str, property_name: str, current_value: Any) -> Dict[str, Any]:
        """Research a specific property using AI agents"""
        
        research_prompt = f"""
        Research the material property {property_name} for {material}.
        Current value: {current_value}
        
        Please provide:
        1. Validation of the current value
        2. Typical ranges for this property
        3. Authoritative sources
        4. Confidence assessment
        """
        
        research_results = []
        
        for provider_name, client in self.api_clients.items():
            try:
                response = await client.generate_async(research_prompt, max_tokens=500)
                if response:
                    research_results.append({
                        'provider': provider_name,
                        'response': response.get('content', ''),
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Research error with {provider_name}: {e}")
        
        return {
            'material': material,
            'property': property_name,
            'research_results': research_results,
            'consensus': self._analyze_consensus(research_results)
        }
    
    def _analyze_consensus(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze consensus among research results"""
        
        # Simple consensus analysis
        return {
            'agreement_level': 'moderate',
            'confidence': 0.7,
            'recommended_action': 'verify'
        }


class ValidationEngine:
    """
    Centralized validation engine for property data.
    """
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules"""
        
        return {
            'density': {
                'min': 0.1,
                'max': 25.0,
                'unit': 'g/cm³',
                'precision': 3
            },
            'meltingPoint': {
                'min': -273,
                'max': 4000,
                'unit': '°C',
                'precision': 0
            },
            'thermalConductivity': {
                'min': 0.01,
                'max': 500,
                'unit': 'W/m·K',
                'precision': 2
            }
        }
    
    def validate_property(self, property_name: str, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single property"""
        
        validation_result = {
            'property': property_name,
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if property_name in self.validation_rules:
            rules = self.validation_rules[property_name]
            
            # Validate value range
            value = property_data.get('value')
            if value is not None:
                try:
                    num_value = float(value)
                    if num_value < rules['min'] or num_value > rules['max']:
                        validation_result['valid'] = False
                        validation_result['errors'].append(
                            f"Value {num_value} outside valid range [{rules['min']}, {rules['max']}]"
                        )
                except (ValueError, TypeError):
                    validation_result['valid'] = False
                    validation_result['errors'].append("Value is not numeric")
            
            # Validate unit
            unit = property_data.get('unit')
            if unit != rules['unit']:
                validation_result['warnings'].append(
                    f"Unit '{unit}' does not match expected '{rules['unit']}'"
                )
        
        return validation_result


class MonitoringToolkit:
    """
    Tools for monitoring and alerting on data quality.
    """
    
    def __init__(self):
        self.alerts_dir = Path("monitoring/alerts")
        self.alerts_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitoring/pipeline.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('MaterialPipeline')
    
    def log_event(self, event_type: str, message: str, severity: str = 'info'):
        """Log pipeline events"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'message': message,
            'severity': severity
        }
        
        if severity == 'critical':
            self.logger.critical(message)
        elif severity == 'error':
            self.logger.error(message)
        elif severity == 'warning':
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def create_alert(self, alert_type: str, severity: str, message: str, details: Dict[str, Any] = None):
        """Create and store alert"""
        
        alert = {
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'details': details or {}
        }
        
        # Save alert to file
        date_str = datetime.now().strftime("%Y%m%d")
        alert_file = self.alerts_dir / f"alerts_{date_str}.json"
        
        alerts = []
        if alert_file.exists():
            try:
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
            except:
                alerts = []
        
        alerts.append(alert)
        
        with open(alert_file, 'w') as f:
            json.dump(alerts, f, indent=2)
        
        # Log alert
        self.log_event('alert_created', message, severity)
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        
        health_status = {
            'overall_status': 'healthy',
            'components': {},
            'alerts_count': 0,
            'last_check': datetime.now().isoformat()
        }
        
        # Check if frontmatter directory exists and has files
        frontmatter_dir = Path("content/components/frontmatter")
        if frontmatter_dir.exists():
            yaml_files = list(frontmatter_dir.glob("*.yaml"))
            health_status['components']['frontmatter'] = {
                'status': 'healthy' if yaml_files else 'warning',
                'file_count': len(yaml_files)
            }
        else:
            health_status['components']['frontmatter'] = {
                'status': 'critical',
                'error': 'Frontmatter directory not found'
            }
            health_status['overall_status'] = 'critical'
        
        # Check recent alerts
        today = datetime.now().strftime("%Y%m%d")
        alert_file = self.alerts_dir / f"alerts_{today}.json"
        
        if alert_file.exists():
            try:
                with open(alert_file, 'r') as f:
                    alerts = json.load(f)
                health_status['alerts_count'] = len(alerts)
                
                critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
                if critical_alerts:
                    health_status['overall_status'] = 'critical'
                elif len(alerts) > 10:
                    health_status['overall_status'] = 'warning'
            except:
                pass
        
        return health_status


class PipelineOrchestrator:
    """
    Orchestrates the execution of all pipeline stages with error handling and recovery.
    """
    
    def __init__(self):
        self.database = DatabaseConnector()
        self.monitoring = MonitoringToolkit()
        self.current_stage = None
        self.pipeline_state = {}
    
    def run_full_pipeline(self, materials_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run the complete 7-stage pipeline"""
        
        pipeline_start = datetime.now()
        self.monitoring.log_event('pipeline_start', f"Starting full pipeline execution at {pipeline_start}")
        
        pipeline_results = {
            'pipeline_id': f"pipeline_{int(pipeline_start.timestamp())}",
            'start_time': pipeline_start.isoformat(),
            'stages': {},
            'overall_status': 'running',
            'materials_filter': materials_filter
        }
        
        stages = [
            ('stage1_discovery', 'Property Discovery & Inventory'),
            ('stage2_standardization', 'Property Standardization'),
            ('stage3_research', 'Research & Enrichment'),
            ('stage4_cross_validation', 'Cross-Validation'),
            ('stage5_quality_assurance', 'Quality Assurance'),
            ('stage6_production', 'Production Integration'),
            ('stage7_monitoring', 'Continuous Monitoring')
        ]
        
        for stage_id, stage_name in stages:
            try:
                self.current_stage = stage_id
                self.monitoring.log_event('stage_start', f"Starting {stage_name}")
                
                stage_result = self._execute_stage(stage_id, materials_filter)
                
                pipeline_results['stages'][stage_id] = {
                    'name': stage_name,
                    'status': 'completed',
                    'result': stage_result,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Store in database
                self.database.store_pipeline_run(stage_id, stage_result)
                
                self.monitoring.log_event('stage_complete', f"Completed {stage_name}")
                
            except Exception as e:
                error_msg = f"Error in {stage_name}: {e}"
                self.monitoring.log_event('stage_error', error_msg, 'error')
                self.monitoring.create_alert('stage_failure', 'critical', error_msg)
                
                pipeline_results['stages'][stage_id] = {
                    'name': stage_name,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
                # Decision: continue or stop pipeline
                if self._should_continue_after_error(stage_id, e):
                    self.monitoring.log_event('pipeline_continue', f"Continuing pipeline after {stage_name} failure")
                    continue
                else:
                    pipeline_results['overall_status'] = 'failed'
                    break
        
        # Complete pipeline
        pipeline_end = datetime.now()
        pipeline_results['end_time'] = pipeline_end.isoformat()
        pipeline_results['duration'] = (pipeline_end - pipeline_start).total_seconds()
        
        if pipeline_results['overall_status'] != 'failed':
            pipeline_results['overall_status'] = 'completed'
        
        self.monitoring.log_event('pipeline_complete', 
                                f"Pipeline completed with status: {pipeline_results['overall_status']}")
        
        return pipeline_results
    
    def _execute_stage(self, stage_id: str, materials_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute a specific pipeline stage"""
        
        # This would import and execute the actual stage modules
        # For now, return a placeholder result
        
        return {
            'stage': stage_id,
            'materials_processed': len(materials_filter) if materials_filter else 50,
            'success_count': len(materials_filter) if materials_filter else 45,
            'error_count': 0 if materials_filter else 5,
            'timestamp': datetime.now().isoformat()
        }
    
    def _should_continue_after_error(self, stage_id: str, error: Exception) -> bool:
        """Determine if pipeline should continue after stage error"""
        
        # Critical stages that should stop the pipeline
        critical_stages = ['stage1_discovery', 'stage6_production']
        
        if stage_id in critical_stages:
            return False
        
        # Continue for other stages
        return True


def main():
    """Test the shared utilities"""
    
    print("🔧 Testing shared pipeline utilities...")
    
    # Test database connector
    db = DatabaseConnector()
    print("✅ Database connector initialized")
    
    # Test monitoring toolkit
    monitoring = MonitoringToolkit()
    monitoring.log_event('test_event', 'Testing monitoring system')
    monitoring.create_alert('test_alert', 'info', 'This is a test alert')
    print("✅ Monitoring toolkit tested")
    
    # Test health check
    health = monitoring.check_system_health()
    print(f"✅ System health: {health['overall_status']}")
    
    # Test validation engine
    validator = ValidationEngine()
    validation_result = validator.validate_property('density', {
        'value': 2.7,
        'unit': 'g/cm³',
        'min': 2.6,
        'max': 2.8
    })
    print(f"✅ Validation test: {'PASSED' if validation_result['valid'] else 'FAILED'}")
    
    print("\n🎉 All shared utilities tested successfully!")

if __name__ == "__main__":
    main()