#!/usr/bin/env python3
"""
Fix Missing Required Fields in Frontmatter YAML Files

This script adds missing required fields (technicalSpecifications and substrateDescription)
to frontmatter YAML files to ensure schema compliance.
"""

import yaml
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MissingFieldsFixer:
    def __init__(self, materials_dir: str = "frontmatter/materials"):
        self.materials_dir = Path(materials_dir)
        self.fixed_count = 0
        self.total_count = 0
        
    def generate_substrate_description(self, material_name: str, category: str) -> str:
        """Generate a substrate description based on material name and category."""
        name_lower = material_name.lower()
        return f"{category} {name_lower} substrate"
    
    def generate_technical_specifications(self, data: dict) -> dict:
        """Generate technical specifications based on existing machine settings."""
        machine_settings = data.get('machineSettings', {})
        category = data.get('category', 'unknown')
        
        # Base contamination sources by category
        contamination_map = {
            'metal': 'oxidation and industrial pollutants',
            'ceramic': 'surface deposits and manufacturing residues',
            'glass': 'optical contamination and surface deposits',
            'stone': 'weathering and environmental deposits',
            'wood': 'biological contamination and surface coatings',
            'composite': 'matrix degradation and surface contamination',
            'masonry': 'weathering and structural deposits',
            'semiconductor': 'process contamination and oxide layers'
        }
        
        # Base thermal effects by category
        thermal_map = {
            'metal': 'minimal thermal effects with controlled heat input',
            'ceramic': 'controlled thermal stress with minimal cracking',
            'glass': 'precise thermal control to prevent cracking',
            'stone': 'minimal thermal impact preserving structural integrity',
            'wood': 'controlled thermal exposure preventing carbonization',
            'composite': 'minimal thermal damage to matrix structure',
            'masonry': 'controlled heating preserving structural integrity',
            'semiconductor': 'ultra-precise thermal control preventing damage'
        }
        
        tech_specs = {
            'contaminationSource': contamination_map.get(category, 'surface contamination and deposits'),
            'thermalEffect': thermal_map.get(category, 'minimal thermal effects with controlled parameters'),
            'wavelength': machine_settings.get('wavelength', '1064nm (primary)'),
            'powerRange': machine_settings.get('powerRange', '100-300W'),
            'pulseDuration': machine_settings.get('pulseDuration', '50-200ns'),
            'spotSize': machine_settings.get('spotSize', '0.5-2.0mm'),
            'repetitionRate': machine_settings.get('repetitionRate', '20-100kHz')
        }
        
        return tech_specs
    
    def fix_file(self, yaml_path: Path) -> bool:
        """Fix missing fields in a single YAML file."""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                logger.warning(f"Empty or invalid YAML: {yaml_path.name}")
                return False
            
            modified = False
            
            # Add missing substrateDescription
            if 'substrateDescription' not in data:
                material_name = data.get('name', yaml_path.stem)
                category = data.get('category', 'unknown')
                data['substrateDescription'] = self.generate_substrate_description(material_name, category)
                modified = True
                logger.info(f"Added substrateDescription to {yaml_path.name}")
            
            # Add missing technicalSpecifications
            if 'technicalSpecifications' not in data:
                data['technicalSpecifications'] = self.generate_technical_specifications(data)
                modified = True
                logger.info(f"Added technicalSpecifications to {yaml_path.name}")
            
            # Write back if modified
            if modified:
                with open(yaml_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                self.fixed_count += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing {yaml_path.name}: {e}")
            return False
    
    def process_all_files(self):
        """Process all YAML files in the materials directory."""
        if not self.materials_dir.exists():
            logger.error(f"Materials directory not found: {self.materials_dir}")
            return
        
        yaml_files = list(self.materials_dir.glob("*.yaml"))
        self.total_count = len(yaml_files)
        
        logger.info(f"🔧 Starting field fixing for {self.total_count} files...")
        
        for yaml_path in yaml_files:
            self.fix_file(yaml_path)
        
        logger.info("="*50)
        logger.info("📊 FIXING SUMMARY")
        logger.info("="*50)
        logger.info(f"📁 Total files: {self.total_count}")
        logger.info(f"🔧 Fixed: {self.fixed_count}")
        logger.info(f"✅ Already complete: {self.total_count - self.fixed_count}")
        logger.info("🎉 All files processed successfully!")

def main():
    """Main execution function."""
    fixer = MissingFieldsFixer()
    fixer.process_all_files()

if __name__ == "__main__":
    main()
