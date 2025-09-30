#!/usr/bin/env python3
"""
Fix Missing Property Research - Populate Missing mechanicalProperties

This script identifies missing property migrations from mechanicalProperties 
to the main properties section and uses AI research to populate them with 
proper values, units, and confidence scores.

Addresses the issue where flexuralStrength, compressiveStrength, and other 
mechanical properties exist in mechanicalProperties but are missing from 
the main properties section that feeds the frontmatter generation.

Author: GitHub Copilot
Date: September 29, 2025
"""

import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import API clients for research
from api.client_factory import create_api_client
from generators.component_generators import GenerationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MissingPropertyResearcher:
    """Research and populate missing properties from mechanicalProperties to properties section"""
    
    def __init__(self):
        self.materials_file = project_root / "data" / "Materials.yaml"
        self.backup_file = project_root / "data" / "Materials_backup_before_property_research.yaml"
        self.api_client = None
        self.research_results = []
        
    def initialize_api_client(self):
        """Initialize API client for research"""
        try:
            self.api_client = create_api_client('deepseek')
            logger.info("✅ DeepSeek API client initialized for property research")
        except Exception as e:
            raise GenerationError(f"Failed to initialize API client for property research: {e}")
    
    def create_backup(self):
        """Create backup of Materials.yaml before modification"""
        try:
            with open(self.materials_file, 'r') as source:
                with open(self.backup_file, 'w') as backup:
                    backup.write(source.read())
            logger.info(f"📦 Created backup: {self.backup_file}")
        except Exception as e:
            raise Exception(f"Failed to create backup: {e}")
    
    def load_materials_data(self) -> Dict[str, Any]:
        """Load Materials.yaml data"""
        try:
            with open(self.materials_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load Materials.yaml: {e}")
    
    def save_materials_data(self, data: Dict[str, Any]):
        """Save updated Materials.yaml data"""
        try:
            with open(self.materials_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            logger.info("💾 Materials.yaml updated successfully")
        except Exception as e:
            raise Exception(f"Failed to save Materials.yaml: {e}")
    
    def find_missing_properties(self, materials_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find all materials with missing property migrations"""
        missing_migrations = []
        
        for category_name, category_data in materials_data.get('materials', {}).items():
            items = category_data.get('items', [])
            
            for material in items:
                material_name = material.get('name', 'UNNAMED')
                mechanical_props = material.get('mechanicalProperties', {})
                properties = material.get('properties', {})
                
                missing_props = []
                for mech_prop, mech_value in mechanical_props.items():
                    if mech_prop not in properties:
                        missing_props.append({
                            'property': mech_prop,
                            'mechanical_value': mech_value,
                            'status': 'COMPLETELY_MISSING'
                        })
                
                if missing_props:
                    missing_migrations.append({
                        'material': material_name,
                        'category': category_name,
                        'missing_properties': missing_props,
                        'material_ref': material
                    })
        
        return missing_migrations
    
    def research_property_value(self, material_name: str, category: str, property_name: str, mechanical_value: str) -> Optional[Dict[str, Any]]:
        """Research a specific property value using AI"""
        if not self.api_client:
            raise GenerationError("API client not initialized for property research")
        
        # Create research prompt
        research_prompt = f"""You are a materials science expert. Research the property "{property_name}" for the material "{material_name}" in category "{category}".

CONTEXT:
- Material: {material_name}
- Category: {category}
- Property: {property_name}
- Existing mechanical property value: {mechanical_value}

TASK: Provide accurate, specific values for this property based on materials science literature.

Consider:
1. Material composition and structure
2. Standard testing conditions
3. Typical property ranges for this material type
4. Industry-standard measurement methods

Format response as JSON:
{{
    "value": numeric_value,
    "unit": "appropriate_unit", 
    "confidence": confidence_percentage,
    "description": "Brief scientific description of the property for this material",
    "source": "research_methodology",
    "min": minimum_typical_value,
    "max": maximum_typical_value
}}"""

        try:
            logger.info(f"🔬 Researching {property_name} for {material_name}...")
            
            response = self.api_client.generate_simple(
                prompt=research_prompt,
                max_tokens=800,
                temperature=0.1
            )
            
            if response.success and response.content:
                # Parse JSON response
                content = response.content.strip()
                
                # Try direct JSON parsing
                try:
                    research_data = json.loads(content)
                    logger.info(f"✅ Successfully researched {property_name} for {material_name}")
                    return research_data
                except json.JSONDecodeError:
                    # Extract JSON from response
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_content = content[start_idx:end_idx]
                        research_data = json.loads(json_content)
                        logger.info(f"✅ Successfully researched {property_name} for {material_name}")
                        return research_data
                    else:
                        logger.error(f"❌ No valid JSON found in research response for {material_name}.{property_name}")
                        return None
            else:
                logger.error(f"❌ API research failed for {material_name}.{property_name}: {response.error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Research error for {material_name}.{property_name}: {e}")
            return None
    
    def populate_missing_properties(self, materials_data: Dict[str, Any], missing_migrations: List[Dict[str, Any]]) -> int:
        """Populate all missing properties with AI research"""
        populated_count = 0
        
        for migration in missing_migrations:
            material_name = migration['material']
            category = migration['category']
            missing_props = migration['missing_properties']
            material_ref = migration['material_ref']
            
            logger.info(f"\n🎯 Processing {material_name} ({category})...")
            
            # Ensure properties section exists
            if 'properties' not in material_ref:
                material_ref['properties'] = {}
            
            for prop_info in missing_props:
                property_name = prop_info['property']
                mechanical_value = prop_info['mechanical_value']
                
                # Research the property
                research_result = self.research_property_value(
                    material_name, category, property_name, mechanical_value
                )
                
                if research_result:
                    # Add to properties section
                    material_ref['properties'][property_name] = {
                        'value': research_result.get('value'),
                        'unit': research_result.get('unit'),
                        'confidence': research_result.get('confidence', 85) / 100.0,  # Convert percentage to decimal
                        'description': research_result.get('description'),
                        'source': 'ai_research_from_mechanical_properties',
                        'min': research_result.get('min'),
                        'max': research_result.get('max')
                    }
                    
                    # Track result
                    self.research_results.append({
                        'material': material_name,
                        'category': category,
                        'property': property_name,
                        'mechanical_value': mechanical_value,
                        'researched_value': research_result.get('value'),
                        'unit': research_result.get('unit'),
                        'confidence': research_result.get('confidence')
                    })
                    
                    populated_count += 1
                    logger.info(f"   ✅ Added {property_name}: {research_result.get('value')} {research_result.get('unit')}")
                    
                    # Brief pause to avoid rate limiting
                    time.sleep(1)
                else:
                    logger.warning(f"   ⚠️  Failed to research {property_name} for {material_name}")
        
        return populated_count
    
    def generate_report(self, populated_count: int) -> str:
        """Generate completion report"""
        report = f"""
# Missing Property Research Completion Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Properties Populated**: {populated_count}

## Research Results Summary

"""
        for result in self.research_results:
            material = result['material']
            property_name = result['property']
            value = result['researched_value']
            unit = result['unit']
            confidence = result['confidence']
            
            report += f"- **{material}**.{property_name}: {value} {unit} (confidence: {confidence}%)\n"
        
        report += f"""

## Files Modified
- `data/Materials.yaml`: Updated with {populated_count} new property values
- `data/Materials_backup_before_property_research.yaml`: Backup created

## Next Steps
1. Run validation: `python3 hierarchical_validator.py`
2. Test frontmatter generation: `python3 run.py --material "Alumina" --components frontmatter`
3. Verify property propagation to production deployment

## Rollback Instructions
If issues occur, restore from backup:
```bash
cp data/Materials_backup_before_property_research.yaml data/Materials.yaml
```
"""
        return report
    
    def run_property_research(self) -> bool:
        """Execute complete missing property research process"""
        try:
            logger.info("🚀 Starting Missing Property Research Process...")
            
            # Initialize API client
            self.initialize_api_client()
            
            # Create backup
            self.create_backup()
            
            # Load data
            materials_data = self.load_materials_data()
            
            # Find missing properties
            missing_migrations = self.find_missing_properties(materials_data)
            logger.info(f"📊 Found {len(missing_migrations)} materials with missing property migrations")
            
            total_missing = sum(len(m['missing_properties']) for m in missing_migrations)
            logger.info(f"📈 Total missing properties to research: {total_missing}")
            
            if total_missing == 0:
                logger.info("✅ No missing properties found - all mechanicalProperties already migrated")
                return True
            
            # Populate missing properties
            populated_count = self.populate_missing_properties(materials_data, missing_migrations)
            
            # Save updated data
            self.save_materials_data(materials_data)
            
            # Generate report
            report = self.generate_report(populated_count)
            report_file = project_root / "PROPERTY_RESEARCH_COMPLETION_REPORT.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            logger.info(f"✅ Property research completed successfully!")
            logger.info(f"📄 Report saved: {report_file}")
            logger.info(f"🎯 Populated {populated_count} missing properties")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Property research failed: {e}")
            return False

def main():
    """Main execution function"""
    researcher = MissingPropertyResearcher()
    
    success = researcher.run_property_research()
    
    if success:
        print("\n🎉 Missing property research completed successfully!")
        print("📝 Check PROPERTY_RESEARCH_COMPLETION_REPORT.md for details")
        print("\n🔍 Next steps:")
        print("1. Run: python3 hierarchical_validator.py")
        print("2. Test: python3 run.py --material 'Alumina' --components frontmatter")
    else:
        print("\n❌ Property research failed - check logs for details")
        sys.exit(1)

if __name__ == "__main__":
    main()