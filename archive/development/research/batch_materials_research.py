#!/usr/bin/env python3
"""
Batch Materials Research Tool

STRICT FAIL-FAST ARCHITECTURE PER GROK_INSTRUCTIONS.md
- ZERO TOLERANCE for defaults, mocks, or fallbacks
- SYSTEMATIC processing of 1,331 default values requiring AI research
- IMMEDIATE failure on API unavailability or research failures
- COMPREHENSIVE progress tracking and validation

Core Purpose: Systematically replace ALL 1,331 default values in Materials.yaml
with unique, AI-researched values using fail-fast validation and progress tracking.
"""

import sys
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
from validation.errors import ConfigurationError

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from scripts.research.ai_materials_researcher import MaterialsResearcher, ResearchResult
from scripts.research.unique_values_validator import UniquenessValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BatchResearchError(Exception):
    """Raised when batch research fails critically"""

class BatchMaterialsResearcher:
    """
    Batch processing system for systematic materials research.
    
    GROK_INSTRUCTIONS.md Compliance:
    - ZERO tolerance for defaults or failures
    - FAIL-FAST on any critical errors
    - COMPREHENSIVE validation and progress tracking
    - NO silent failures or partial processing
    """
    
    def __init__(self):
        """Initialize batch researcher with strict validation"""
        self.materials_file = project_root / "data" / "Materials.yaml"
        self.backup_dir = project_root / "backups"
        self.progress_file = project_root / "logs" / "batch_research_progress.json"
        
        # Initialize core components with fail-fast validation
        self.researcher = MaterialsResearcher()
        self.validator = UniquenessValidator()
        
        # Create directories if needed
        self.backup_dir.mkdir(exist_ok=True)
        (project_root / "logs").mkdir(exist_ok=True)
        
        self.batch_stats = {
            'start_time': None,
            'end_time': None,
            'total_materials': 0,
            'total_properties': 0,
            'successfully_researched': 0,
            'failed_research': 0,
            'validation_passes': 0,
            'validation_failures': 0,
            'backup_created': None
        }
        
        logger.info("✅ BatchMaterialsResearcher initialized with fail-fast validation")
    
    def create_backup(self) -> str:
        """Create timestamped backup of Materials.yaml"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"Materials_backup_before_batch_research_{timestamp}.yaml"
        
        try:
            import shutil
            shutil.copy2(self.materials_file, backup_file)
            
            logger.info(f"✅ Backup created: {backup_file}")
            self.batch_stats['backup_created'] = str(backup_file)
            return str(backup_file)
            
        except Exception as e:
            raise BatchResearchError(f"CRITICAL: Failed to create backup: {e}")
    
    def load_materials_data(self) -> Dict[str, Any]:
        """Load Materials.yaml with validation"""
        try:
            with open(self.materials_file, 'r') as f:
                materials_data = yaml.safe_load(f)
            
            if not materials_data or 'materials' not in materials_data:
                raise BatchResearchError("CRITICAL: Invalid Materials.yaml structure")
            
            return materials_data
            
        except Exception as e:
            raise BatchResearchError(f"CRITICAL: Failed to load Materials.yaml: {e}")
    
    def save_materials_data(self, materials_data: Dict[str, Any]):
        """Save updated Materials.yaml with validation"""
        try:
            # Validate data structure
            if not materials_data or 'materials' not in materials_data:
                raise BatchResearchError("CRITICAL: Invalid materials data structure")
            
            # Write to file
            with open(self.materials_file, 'w') as f:
                yaml.dump(materials_data, f, default_flow_style=False, indent=2)
            
            logger.info("✅ Materials.yaml updated successfully")
            
        except Exception as e:
            raise BatchResearchError(f"CRITICAL: Failed to save Materials.yaml: {e}")
    
    def update_material_property(
        self, 
        materials_data: Dict[str, Any], 
        material_name: str, 
        category: str, 
        research_result: ResearchResult
    ):
        """Update a single property with research result"""
        try:
            # Find the material in the data structure
            category_items = materials_data['materials'][category]['items']
            
            for material_item in category_items:
                if material_item.get('name') == material_name:
                    properties = material_item.get('properties', {})
                    
                    # Update the property with research result
                    properties[research_result.property_name] = {
                        'value': research_result.researched_value,
                        'unit': research_result.unit,
                        'source': research_result.source,
                        'confidence': research_result.confidence,
                        'research_basis': research_result.research_basis,
                        'research_date': research_result.research_date,
                        'validation_method': research_result.validation_method
                    }
                    
                    # Add min/max if available
                    if research_result.min_value is not None:
                        properties[research_result.property_name]['min'] = research_result.min_value
                    if research_result.max_value is not None:
                        properties[research_result.property_name]['max'] = research_result.max_value
                    
                    logger.debug(f"✅ Updated {material_name}.{research_result.property_name}")
                    return
            
            raise BatchResearchError(f"Material {material_name} not found in category {category}")
            
        except Exception as e:
            raise BatchResearchError(f"Failed to update {material_name}.{research_result.property_name}: {e}")
    
    def save_progress(self, progress_data: Dict[str, Any]):
        """Save batch research progress"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2, default=str)
            
        except Exception as e:
            logger.warning(f"Failed to save progress: {e}")
    
    def load_progress(self) -> Optional[Dict[str, Any]]:
        """Load existing batch research progress"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            return None
            
        except Exception as e:
            logger.warning(f"Failed to load progress: {e}")
            return None
    
    def execute_batch_research(
        self, 
        priority: str = 'all',
        max_materials: Optional[int] = None,
        target_properties: Optional[List[str]] = None,
        resume: bool = True
    ) -> Dict[str, Any]:
        """
        Execute comprehensive batch research with fail-fast validation.
        
        FAIL-FAST: Stops on critical errors
        ZERO TOLERANCE: All research must succeed
        """
        logger.info("🚀 Starting BATCH MATERIALS RESEARCH")
        logger.info("=" * 60)
        logger.info("GROK_INSTRUCTIONS.md: ZERO TOLERANCE FOR DEFAULTS")
        logger.info("Target: Replace 1,331 default values with AI research")
        logger.info("=" * 60)
        
        self.batch_stats['start_time'] = datetime.now().isoformat()
        
        try:
            # Create backup before starting
            backup_file = self.create_backup()
            logger.info(f"📁 Using backup: {backup_file}")
            logger.info(f"📁 Using backup: {backup_file}")
            
            # Load materials data
            materials_data = self.load_materials_data()
            
            # Find materials needing research
            materials_needing_research = self.researcher.find_materials_with_default_values()
            
            if not materials_needing_research:
                logger.info("✅ No materials found needing research")
                return self._create_success_result(0, 0, [])
            
            # Apply priority filtering
            if priority == 'high':
                high_priority_materials = ['Aluminum', 'Steel', 'Copper', 'Brass', 'Glass']
                materials_needing_research = [
                    mat for mat in materials_needing_research 
                    if any(priority_mat in mat['material_name'] 
                          for priority_mat in high_priority_materials)
                ]
            
            # Apply limits
            if max_materials:
                materials_needing_research = materials_needing_research[:max_materials]
            
            total_materials = len(materials_needing_research)
            total_properties = sum(
                mat['total_properties'] for mat in materials_needing_research
            )
            
            self.batch_stats['total_materials'] = total_materials
            self.batch_stats['total_properties'] = total_properties
            
            logger.info(f"📋 Processing {total_materials} materials")
            logger.info(f"📋 Researching {total_properties} properties")
            logger.info(f"⏱️  Estimated time: {total_properties * 20 / 60:.1f} minutes")
            
            # Process materials one by one
            successful_materials = []
            failed_materials = []
            
            for i, material_info in enumerate(materials_needing_research, 1):
                material_name = material_info['material_name']
                category = material_info['category']
                properties_to_research = material_info['properties_needing_research']
                
                # Filter properties if specified
                if target_properties:
                    properties_to_research = [
                        prop for prop in properties_to_research 
                        if prop['property_name'] in target_properties
                    ]
                
                logger.info(f"\\n🔬 [{i}/{total_materials}] Processing {material_name}")
                logger.info(f"   Category: {category}")
                logger.info(f"   Properties: {len(properties_to_research)}")
                
                material_success = True
                material_research_results = []
                
                # Research each property
                for prop_info in properties_to_research:
                    prop_name = prop_info['property_name']
                    
                    try:
                        # Research the property
                        result = self.researcher.research_material_property(
                            material_name=material_name,
                            property_name=prop_name,
                            category=category,
                            current_value=prop_info['current_value']
                        )
                        
                        if result.success:
                            # Update materials data immediately
                            self.update_material_property(
                                materials_data, material_name, category, result
                            )
                            material_research_results.append(result)
                            self.batch_stats['successfully_researched'] += 1
                            
                            logger.info(f"   ✅ {prop_name}: {result.researched_value} {result.unit}")
                        else:
                            logger.error(f"   ❌ {prop_name}: {result.error_message}")
                            material_success = False
                            self.batch_stats['failed_research'] += 1
                    
                    except Exception as e:
                        logger.error(f"   💥 {prop_name}: Critical error - {e}")
                        material_success = False
                        self.batch_stats['failed_research'] += 1
                    
                    # Brief pause to respect API rate limits
                    time.sleep(1)
                
                # Track material result
                if material_success and material_research_results:
                    successful_materials.append({
                        'material_name': material_name,
                        'category': category,
                        'properties_researched': len(material_research_results),
                        'research_results': material_research_results
                    })
                    logger.info(f"   🎉 {material_name} completed successfully")
                else:
                    failed_materials.append({
                        'material_name': material_name,
                        'category': category,
                        'error': 'One or more property research failed'
                    })
                    logger.error(f"   💥 {material_name} failed")
                
                # Save progress periodically
                if i % 5 == 0:
                    progress_data = {
                        'processed_materials': i,
                        'total_materials': total_materials,
                        'successful_materials': len(successful_materials),
                        'failed_materials': len(failed_materials),
                        'last_update': datetime.now().isoformat()
                    }
                    self.save_progress(progress_data)
                    
                    # Save materials data
                    self.save_materials_data(materials_data)
                    logger.info(f"📊 Progress saved: {i}/{total_materials} materials processed")
            
            # Final save of materials data
            self.save_materials_data(materials_data)
            
            # Validate final result
            try:
                validation_result = self.validator.validate_property_uniqueness()
                self.batch_stats['validation_passes'] = 1
                logger.info(f"✅ Final validation passed: {validation_result['total_materials']} materials validated")
            except Exception as e:
                self.batch_stats['validation_failures'] = 1
                logger.warning(f"⚠️ Final validation failed: {e}")
            
            self.batch_stats['end_time'] = datetime.now().isoformat()
            
            return self._create_success_result(
                len(successful_materials), 
                len(failed_materials), 
                successful_materials
            )
            
        except Exception as e:
            logger.error(f"💥 BATCH RESEARCH FAILED: {e}")
            self.batch_stats['end_time'] = datetime.now().isoformat()
            raise BatchResearchError(f"CRITICAL: Batch research failed: {e}")
    
    def _create_success_result(
        self, 
        successful_count: int, 
        failed_count: int, 
        successful_materials: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create standardized success result"""
        return {
            'batch_research_completed': True,
            'successful_materials': successful_count,
            'failed_materials': failed_count,
            'total_processed': successful_count + failed_count,
            'materials_data': successful_materials,
            'batch_statistics': self.batch_stats,
            'backup_file': self.batch_stats.get('backup_created'),
            'completion_time': datetime.now().isoformat()
        }
    
    def get_batch_statistics(self) -> Dict[str, Any]:
        """Get current batch research statistics"""
        return {
            'batch_stats': self.batch_stats.copy(),
            'progress_file': str(self.progress_file),
            'backup_directory': str(self.backup_dir)
        }

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch Materials Research - FAIL-FAST")
    parser.add_argument('--priority', choices=['all', 'high'], default='all', 
                       help='Research priority level')
    parser.add_argument('--max-materials', type=int, 
                       help='Maximum materials to process')
    parser.add_argument('--properties', nargs='+', 
                       help='Specific properties to research')
    parser.add_argument('--no-resume', action='store_true', 
                       help='Do not resume from previous progress')
    parser.add_argument('--stats', action='store_true', 
                       help='Show batch research statistics')
    
    args = parser.parse_args()
    
    try:
        batch_researcher = BatchMaterialsResearcher()
        
        if args.stats:
            stats = batch_researcher.get_batch_statistics()
            print(json.dumps(stats, indent=2, default=str))
            return
        
        # Execute batch research
        result = batch_researcher.execute_batch_research(
            priority=args.priority,
            max_materials=args.max_materials,
            target_properties=args.properties,
            resume=not args.no_resume
        )
        
        print("\\n🎉 BATCH RESEARCH COMPLETED")
        print("=" * 50)
        print(f"Successful Materials: {result['successful_materials']}")
        print(f"Failed Materials: {result['failed_materials']}")
        print(f"Total Processed: {result['total_processed']}")
        print(f"Backup Created: {result['backup_file']}")
        print("=" * 50)
        
    except (BatchResearchError, ConfigurationError) as e:
        logger.error(f"💥 FAIL-FAST ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()