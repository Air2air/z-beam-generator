#!/usr/bin/env python3
"""
Property Validation Pipeline Orchestrator
Main controller for the 7-stage material property validation assembly line.
"""

import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class StageStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PropertyRecord:
    """Represents a material property throughout the pipeline"""
    material_name: str
    category: str
    property_name: str
    original_value: Any
    standardized_value: Optional[Any] = None
    researched_value: Optional[Any] = None
    validated_value: Optional[Any] = None
    final_value: Optional[Any] = None
    confidence_score: float = 0.0
    sources: List[str] = None
    validation_status: str = "pending"
    stage_history: List[Dict] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.stage_history is None:
            self.stage_history = []

class PropertyValidationPipeline:
    """
    Main orchestrator for the 7-stage property validation pipeline
    """
    
    def __init__(self, config_path: str = "config/pipeline_config.yaml"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.results_dir = Path("pipeline_results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Pipeline stages
        self.stages = {
            1: "Discovery & Inventory",
            2: "Standardization",
            3: "Research & Enrichment", 
            4: "Cross-Validation",
            5: "Quality Assurance",
            6: "Production Integration",
            7: "Continuous Monitoring"
        }
        
        self.stage_status = {i: StageStatus.PENDING for i in range(1, 8)}
        self.property_records: List[PropertyRecord] = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load pipeline configuration"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                "quality_thresholds": {
                    "completeness": 0.95,
                    "accuracy": 0.90,
                    "consistency": 0.85
                },
                "research_providers": ["deepseek", "claude"],
                "validation_rules": {
                    "min_sources": 2,
                    "confidence_threshold": 0.7
                },
                "monitoring": {
                    "enabled": True,
                    "alert_threshold": 0.5
                }
            }
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the pipeline"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'pipeline_results/pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def run_pipeline(self, materials_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute the complete 7-stage validation pipeline
        
        Args:
            materials_filter: Optional list of specific materials to process
            
        Returns:
            Complete pipeline results and statistics
        """
        
        self.logger.info("🚀 Starting Material Property Validation Pipeline")
        self.logger.info("=" * 60)
        
        pipeline_start = datetime.now()
        results = {
            "pipeline_start": pipeline_start.isoformat(),
            "stages_completed": [],
            "total_properties_processed": 0,
            "success_rate": 0.0,
            "quality_metrics": {},
            "errors": []
        }
        
        try:
            # Stage 1: Discovery & Inventory
            self._run_stage(1, self._stage1_discovery, materials_filter)
            
            # Stage 2: Standardization  
            self._run_stage(2, self._stage2_standardization)
            
            # Stage 3: Research & Enrichment
            self._run_stage(3, self._stage3_research)
            
            # Stage 4: Cross-Validation
            self._run_stage(4, self._stage4_validation)
            
            # Stage 5: Quality Assurance
            self._run_stage(5, self._stage5_quality_assurance)
            
            # Stage 6: Production Integration
            self._run_stage(6, self._stage6_production_integration)
            
            # Stage 7: Continuous Monitoring Setup
            self._run_stage(7, self._stage7_monitoring_setup)
            
            # Calculate final results
            results.update(self._calculate_final_results())
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            results["errors"].append(str(e))
            
        finally:
            pipeline_end = datetime.now()
            results["pipeline_end"] = pipeline_end.isoformat()
            results["total_duration"] = str(pipeline_end - pipeline_start)
            
            # Save results
            self._save_pipeline_results(results)
            
        self.logger.info("✅ Pipeline execution completed")
        return results
    
    def _run_stage(self, stage_num: int, stage_function, *args, **kwargs):
        """Execute a single pipeline stage with error handling"""
        
        stage_name = self.stages[stage_num]
        self.logger.info(f"\n📋 STAGE {stage_num}: {stage_name}")
        self.logger.info("-" * 50)
        
        self.stage_status[stage_num] = StageStatus.IN_PROGRESS
        
        try:
            stage_result = stage_function(*args, **kwargs)
            self.stage_status[stage_num] = StageStatus.COMPLETED
            self.logger.info(f"✅ Stage {stage_num} completed successfully")
            return stage_result
            
        except Exception as e:
            self.stage_status[stage_num] = StageStatus.FAILED
            self.logger.error(f"❌ Stage {stage_num} failed: {e}")
            raise
    
    def _stage1_discovery(self, materials_filter: Optional[List[str]] = None):
        """Stage 1: Discovery & Inventory"""
        
        from stages.stage1_discovery.discover_properties import PropertyDiscoverer
        
        discoverer = PropertyDiscoverer()
        
        # Scan all frontmatter files
        frontmatter_properties = discoverer.scan_frontmatter_files(materials_filter)
        
        # Analyze Categories.yaml
        category_definitions = discoverer.analyze_category_definitions()
        
        # Generate property inventory
        property_inventory = discoverer.create_property_inventory(
            frontmatter_properties, 
            category_definitions
        )
        
        # Create processing queue with priorities
        processing_queue = discoverer.prioritize_properties(property_inventory)
        
        # Initialize property records
        self.property_records = [
            PropertyRecord(
                material_name=item['material'],
                category=item['category'],
                property_name=item['property'],
                original_value=item['value']
            )
            for item in processing_queue
        ]
        
        self.logger.info(f"📊 Discovered {len(self.property_records)} properties across {len(set(r.material_name for r in self.property_records))} materials")
        
        # Save stage results
        stage1_results = {
            "properties_discovered": len(self.property_records),
            "materials_processed": len(set(r.material_name for r in self.property_records)),
            "categories_covered": len(set(r.category for r in self.property_records)),
            "property_inventory": property_inventory,
            "processing_queue": processing_queue
        }
        
        self._save_stage_results(1, stage1_results)
        return stage1_results
    
    def _stage2_standardization(self):
        """Stage 2: Standardization"""
        
        from stages.stage2_standardization.property_standardizer import PropertyStandardizer
        
        standardizer = PropertyStandardizer(self.config.get('standardization_rules', {}))
        
        standardized_count = 0
        
        for record in self.property_records:
            try:
                # Standardize units, naming, and format
                standardized_result = standardizer.standardize_property(
                    record.property_name,
                    record.original_value,
                    record.category
                )
                
                record.standardized_value = standardized_result['value']
                record.stage_history.append({
                    'stage': 2,
                    'action': 'standardized',
                    'details': standardized_result,
                    'timestamp': datetime.now().isoformat()
                })
                
                standardized_count += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to standardize {record.material_name}.{record.property_name}: {e}")
                record.stage_history.append({
                    'stage': 2,
                    'action': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        self.logger.info(f"🔧 Standardized {standardized_count}/{len(self.property_records)} properties")
        
        stage2_results = {
            "properties_standardized": standardized_count,
            "standardization_rate": standardized_count / len(self.property_records),
            "failed_standardizations": len(self.property_records) - standardized_count
        }
        
        self._save_stage_results(2, stage2_results)
        return stage2_results
    
    def _stage3_research(self):
        """Stage 3: Research & Enrichment"""
        
        from stages.stage3_research.ai_research_agent import AIResearchAgent
        
        research_agent = AIResearchAgent(self.config.get('research_providers', ['deepseek']))
        
        researched_count = 0
        
        for record in self.property_records:
            # Skip if we already have high-confidence data
            if record.confidence_score > 0.9:
                continue
                
            try:
                # Research property value using AI
                research_result = research_agent.research_property(
                    record.material_name,
                    record.category,
                    record.property_name
                )
                
                record.researched_value = research_result['value']
                record.confidence_score = research_result['confidence']
                record.sources.extend(research_result['sources'])
                record.stage_history.append({
                    'stage': 3,
                    'action': 'researched',
                    'details': research_result,
                    'timestamp': datetime.now().isoformat()
                })
                
                researched_count += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to research {record.material_name}.{record.property_name}: {e}")
                record.stage_history.append({
                    'stage': 3,
                    'action': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        self.logger.info(f"🔬 Researched {researched_count} properties")
        
        stage3_results = {
            "properties_researched": researched_count,
            "average_confidence": sum(r.confidence_score for r in self.property_records) / len(self.property_records),
            "high_confidence_count": len([r for r in self.property_records if r.confidence_score > 0.8])
        }
        
        self._save_stage_results(3, stage3_results)
        return stage3_results
    
    def _stage4_validation(self):
        """Stage 4: Cross-Validation"""
        
        from stages.stage4_validation.cross_validator import CrossValidator
        
        validator = CrossValidator(self.config.get('validation_rules', {}))
        
        validated_count = 0
        
        for record in self.property_records:
            try:
                # Cross-validate against multiple sources
                validation_result = validator.validate_property(
                    record.material_name,
                    record.category,
                    record.property_name,
                    record.researched_value or record.standardized_value,
                    record.sources
                )
                
                record.validated_value = validation_result['validated_value']
                record.confidence_score = max(record.confidence_score, validation_result['confidence'])
                record.validation_status = validation_result['status']
                record.stage_history.append({
                    'stage': 4,
                    'action': 'validated',
                    'details': validation_result,
                    'timestamp': datetime.now().isoformat()
                })
                
                validated_count += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to validate {record.material_name}.{record.property_name}: {e}")
                record.stage_history.append({
                    'stage': 4,
                    'action': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        self.logger.info(f"✅ Validated {validated_count} properties")
        
        stage4_results = {
            "properties_validated": validated_count,
            "validation_rate": validated_count / len(self.property_records),
            "approved_properties": len([r for r in self.property_records if r.validation_status == 'approved']),
            "needs_review": len([r for r in self.property_records if r.validation_status == 'needs_review'])
        }
        
        self._save_stage_results(4, stage4_results)
        return stage4_results
    
    def _stage5_quality_assurance(self):
        """Stage 5: Quality Assurance"""
        
        from stages.stage5_quality_assurance.quality_analyzer import QualityAnalyzer
        
        qa_analyzer = QualityAnalyzer(self.config.get('quality_thresholds', {}))
        
        # Run comprehensive quality analysis
        quality_results = qa_analyzer.analyze_property_quality(self.property_records)
        
        # Apply quality gates
        qa_approved = []
        for record in self.property_records:
            if record.validation_status == 'approved' and record.confidence_score >= 0.7:
                record.final_value = record.validated_value or record.researched_value
                qa_approved.append(record)
        
        self.logger.info(f"📊 QA approved {len(qa_approved)}/{len(self.property_records)} properties")
        
        stage5_results = {
            "qa_approved_count": len(qa_approved),
            "qa_approval_rate": len(qa_approved) / len(self.property_records),
            "quality_metrics": quality_results,
            "failed_qa": len(self.property_records) - len(qa_approved)
        }
        
        self._save_stage_results(5, stage5_results)
        return stage5_results
    
    def _stage6_production_integration(self):
        """Stage 6: Production Integration"""
        
        from stages.stage6_production.production_integrator import ProductionIntegrator
        
        integrator = ProductionIntegrator()
        
        # Get approved properties
        approved_properties = [r for r in self.property_records if r.final_value is not None]
        
        # Create backup before deployment
        backup_info = integrator.create_backup()
        
        try:
            # Deploy to staging first
            staging_results = integrator.deploy_to_staging(approved_properties)
            
            # Run integration tests
            test_results = integrator.run_integration_tests()
            
            if test_results['success']:
                # Deploy to production
                production_results = integrator.deploy_to_production(approved_properties)
                self.logger.info("🚀 Successfully deployed to production")
            else:
                self.logger.error("❌ Integration tests failed, rolling back")
                integrator.rollback(backup_info)
                
        except Exception as e:
            self.logger.error(f"❌ Production deployment failed: {e}")
            integrator.rollback(backup_info)
            raise
        
        stage6_results = {
            "properties_deployed": len(approved_properties),
            "deployment_success": test_results.get('success', False),
            "backup_created": backup_info['backup_id'],
            "deployment_timestamp": datetime.now().isoformat()
        }
        
        self._save_stage_results(6, stage6_results)
        return stage6_results
    
    def _stage7_monitoring_setup(self):
        """Stage 7: Continuous Monitoring Setup"""
        
        from stages.stage7_monitoring.monitoring_setup import MonitoringSetup
        
        monitor = MonitoringSetup(self.config.get('monitoring', {}))
        
        # Set up monitoring dashboards
        dashboard_config = monitor.setup_monitoring_dashboard()
        
        # Configure alerts
        alert_config = monitor.configure_alerts()
        
        # Schedule periodic reviews
        review_schedule = monitor.schedule_reviews()
        
        self.logger.info("📊 Monitoring and alerting configured")
        
        stage7_results = {
            "monitoring_enabled": True,
            "dashboard_configured": dashboard_config['success'],
            "alerts_configured": len(alert_config['alert_rules']),
            "review_schedule_set": review_schedule['success']
        }
        
        self._save_stage_results(7, stage7_results)
        return stage7_results
    
    def _calculate_final_results(self) -> Dict[str, Any]:
        """Calculate final pipeline statistics"""
        
        total_properties = len(self.property_records)
        successful_properties = len([r for r in self.property_records if r.final_value is not None])
        
        return {
            "total_properties_processed": total_properties,
            "successful_properties": successful_properties,
            "success_rate": successful_properties / total_properties if total_properties > 0 else 0,
            "average_confidence": sum(r.confidence_score for r in self.property_records) / total_properties if total_properties > 0 else 0,
            "quality_metrics": {
                "completeness": successful_properties / total_properties if total_properties > 0 else 0,
                "high_confidence_rate": len([r for r in self.property_records if r.confidence_score > 0.8]) / total_properties if total_properties > 0 else 0
            },
            "stages_completed": [i for i, status in self.stage_status.items() if status == StageStatus.COMPLETED]
        }
    
    def _save_stage_results(self, stage_num: int, results: Dict[str, Any]):
        """Save individual stage results"""
        
        results_file = self.results_dir / f"stage_{stage_num}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    def _save_pipeline_results(self, results: Dict[str, Any]):
        """Save complete pipeline results"""
        
        # Save main results
        results_file = self.results_dir / f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save property records
        records_file = self.results_dir / f"property_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(records_file, 'w') as f:
            json.dump([asdict(record) for record in self.property_records], f, indent=2, default=str)

def main():
    """Main entry point for pipeline execution"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Material Property Validation Pipeline")
    parser.add_argument("--config", default="config/pipeline_config.yaml", help="Pipeline configuration file")
    parser.add_argument("--materials", nargs='+', help="Specific materials to process")
    parser.add_argument("--stage", type=int, choices=range(1, 8), help="Run specific stage only")
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = PropertyValidationPipeline(args.config)
    
    if args.stage:
        # Run specific stage only
        print(f"Running Stage {args.stage} only...")
        # Implementation for single stage execution
    else:
        # Run complete pipeline
        results = pipeline.run_pipeline(args.materials)
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 PIPELINE EXECUTION SUMMARY")
        print("="*60)
        print(f"Properties Processed: {results['total_properties_processed']}")
        print(f"Success Rate: {results['success_rate']:.2%}")
        print(f"Stages Completed: {len(results['stages_completed'])}/7")
        print(f"Duration: {results['total_duration']}")
        
        if results['errors']:
            print(f"\n⚠️  Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                print(f"  - {error}")

if __name__ == "__main__":
    main()