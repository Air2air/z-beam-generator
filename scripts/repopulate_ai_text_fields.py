#!/usr/bin/env python3
"""
AI Text Fields Repopulation Script

Repopulates ALL ai_text_fields in Materials.yaml with enhanced content including:
- All existing fields (subtitle, description, technical_notes, etc.)
- New fields: environmental_impact, outcome_metrics

Extracts content from existing nested structures and converts to ai_text_fields format
with proper word counts, character counts, author voice, and timestamps.

Usage:
    python3 scripts/repopulate_ai_text_fields.py [material_name]
    python3 scripts/repopulate_ai_text_fields.py --all
    python3 scripts/repopulate_ai_text_fields.py --help
"""

import argparse
import logging
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple
import sys
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.frontmatter.core.universal_text_enhancer import UniversalTextFieldEnhancer


class AITextFieldsRepopulator:
    """Repopulates all ai_text_fields with enhanced content including environmentalImpact and outcomeMetrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.materials_path = Path("data/materials.yaml")
        self.enhancer = UniversalTextFieldEnhancer()
        
        # All text fields that should be in ai_text_fields
        # Define target fields for AI text generation
        self.target_fields = [
            'applicationDescription',
            'benefitsIntroduction', 
            'benefitsOutline',
            'compatibilityDescription',
            'processOverview',
            'qualityStandards',
            'safetyInformation',
            'technicalSpecifications',
            'usageGuidelines',
            # Caption fields with proper author voice
            'caption_beforeText',
            'caption_afterText',
            # New environmentalImpact text fields
            'environmentalImpact_benefit',
            'environmentalImpact_description', 
            'environmentalImpact_quantifiedBenefits',
            'environmentalImpact_sustainabilityBenefit',
            # New outcomeMetrics text fields
            'outcomeMetrics_metric',
            'outcomeMetrics_description',
            'outcomeMetrics_typicalRanges'
        ]
        
        self.logger.info(f"✅ AITextFieldsRepopulator initialized with {len(self.target_fields)} target fields")

    def extract_environmental_impact_content(self, environmental_impact_data: List[Dict]) -> str:
        """
        Extract text content from nested environmentalImpact structure.
        
        Args:
            environmental_impact_data: List of environmental impact objects
            
        Returns:
            Formatted text content suitable for ai_text_fields
            
        Example input:
        - benefit: Chemical Waste Elimination
          description: Eliminates hazardous chemical waste streams
          quantifiedBenefits: Up to 100% reduction in chemical cleaning agents
          applicableIndustries: [Semiconductor, Electronics, Medical, Nuclear]
        """
        if not environmental_impact_data or not isinstance(environmental_impact_data, list):
            return ""
        
        content_parts = []
        for item in environmental_impact_data:
            if not isinstance(item, dict):
                continue
                
            benefit = item.get('benefit', 'Environmental Benefit')
            description = item.get('description', '')
            quantified = item.get('quantifiedBenefits', '')
            industries = item.get('applicableIndustries', [])
            
            # Format into readable text
            part = f"{benefit}: {description}"
            if quantified:
                part += f" {quantified}"
            if industries and len(industries) > 0:
                part += f" (Industries: {', '.join(industries[:3])})"  # Limit to first 3
            
            content_parts.append(part)
        
        return '. '.join(content_parts) + '.' if content_parts else ""

    def extract_outcome_metrics_content(self, outcome_metrics_data: List[Dict]) -> str:
        """
        Extract text content from nested outcomeMetrics structure.
        
        Args:
            outcome_metrics_data: List of outcome metrics objects
            
        Returns:
            Formatted text content suitable for ai_text_fields
            
        Example input:
        - metric: Contaminant Removal Efficiency
          description: Percentage of target contaminants successfully removed from surface
          measurementMethods: [Before/after microscopy, Chemical analysis]
          factorsAffecting: [Contamination type, Adhesion strength]
          typicalRanges: 95-99.9% depending on application and material
        """
        if not outcome_metrics_data or not isinstance(outcome_metrics_data, list):
            return ""
        
        content_parts = []
        for item in outcome_metrics_data:
            if not isinstance(item, dict):
                continue
                
            metric = item.get('metric', 'Performance Metric')
            description = item.get('description', '')
            methods = item.get('measurementMethods', [])
            ranges = item.get('typicalRanges', '')
            units = item.get('units', [])
            
            # Format into readable text
            part = f"{metric}: {description}"
            if ranges:
                part += f" Typical ranges: {ranges}"
            if methods and len(methods) > 0:
                part += f" (Measured via: {', '.join(methods[:2])})"  # Limit to first 2
            if units and len(units) > 0:
                part += f" Units: {', '.join(units[:2])}"
            
            content_parts.append(part)
        
        return '. '.join(content_parts) + '.' if content_parts else ""

    def generate_ai_text_field_content(
        self, 
        field_name: str, 
        material_name: str, 
        material_data: Dict
    ) -> Tuple[str, int, int]:
        """
        Generate AI content for a specific text field.
        
        Args:
            field_name: Name of the field (e.g., 'environmental_impact')
            material_name: Name of the material
            material_data: Full material data from Materials.yaml
            
        Returns:
            Tuple of (content, word_count, character_count)
        """
        
        # All ai_text_fields are ALWAYS AI generated with author voice integration
        # Never extract from existing nested data - that stays separate
        self.logger.info(f"🤖 Generating AI content for {field_name} with author voice")
        
        # Use the existing enhancer's research method which includes author voice
        content, word_count, char_count = self.enhancer._research_text_field(
            field_name, material_name, material_data
        )
        
        return content, word_count, char_count

    def repopulate_material_ai_text_fields(
        self, 
        material_name: str, 
        force_regenerate: bool = True
    ) -> Dict[str, Any]:
        """
        Repopulate all ai_text_fields for a single material.
        
        Args:
            material_name: Name of the material to process
            force_regenerate: If True, regenerate even existing fields
            
        Returns:
            Dictionary with results
        """
        
        self.logger.info(f"🔬 Repopulating AI text fields for {material_name}")
        self.logger.info("=" * 60)
        
        try:
            # Load Materials.yaml
            with open(self.materials_path, 'r', encoding='utf-8') as f:
                materials_data = yaml.safe_load(f)
            
            if 'materials' not in materials_data:
                raise ValueError("Invalid Materials.yaml structure: missing 'materials' section")
            
            material_data = materials_data['materials'].get(material_name)
            if not material_data:
                raise ValueError(f"Material '{material_name}' not found in Materials.yaml")
            
            # Initialize or get existing ai_text_fields
            if 'ai_text_fields' not in material_data:
                material_data['ai_text_fields'] = {}
            
            ai_text_fields = material_data['ai_text_fields']
            generated_count = 0
            skipped_count = 0
            
            # Process each target field
            for field_name in self.target_fields:
                
                # Check if field exists and force_regenerate setting
                if field_name in ai_text_fields and not force_regenerate:
                    self.logger.info(f"⏭️  Skipping {field_name} (already exists, use --force to regenerate)")
                    skipped_count += 1
                    continue
                
                # Generate content using AI with author voice integration
                try:
                    content, word_count, char_count = self.generate_ai_text_field_content(
                        field_name, material_name, material_data
                    )
                    
                    if content:
                        # Create ai_text_fields entry
                        ai_text_fields[field_name] = {
                            'content': content,
                            'source': 'ai_research',
                            'research_date': datetime.now(timezone.utc).isoformat(),
                            'word_count': word_count,
                            'character_count': char_count
                        }
                        
                        generated_count += 1
                        self.logger.info(f"✅ Generated {field_name}: {word_count} words, {char_count} chars")
                    else:
                        self.logger.warning(f"⚠️  No content generated for {field_name}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Failed to generate {field_name}: {e}")
                    continue
            
            # Save updated Materials.yaml
            if generated_count > 0:
                # Create backup
                backup_path = self.materials_path.with_suffix('.yaml.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                # Save updated version
                with open(self.materials_path, 'w', encoding='utf-8') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                
                self.logger.info(f"💾 Saved Materials.yaml (backup: {backup_path.name})")
            
            self.logger.info(f"✅ Completed {material_name}: {generated_count} generated, {skipped_count} skipped")
            
            return {
                'success': True,
                'material': material_name,
                'generated_count': generated_count,
                'skipped_count': skipped_count,
                'total_fields': len(self.target_fields)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process {material_name}: {e}")
            return {
                'success': False,
                'material': material_name,
                'error': str(e)
            }

    def repopulate_all_materials(self, force_regenerate: bool = True) -> Dict[str, Any]:
        """
        Repopulate ai_text_fields for ALL materials in Materials.yaml.
        
        Args:
            force_regenerate: If True, regenerate even existing fields
            
        Returns:
            Dictionary with overall results
        """
        
        self.logger.info("🚀 REPOPULATING AI TEXT FIELDS FOR ALL MATERIALS")
        self.logger.info("=" * 80)
        
        try:
            # Load Materials.yaml to get all material names
            with open(self.materials_path, 'r', encoding='utf-8') as f:
                materials_data = yaml.safe_load(f)
            
            if 'materials' not in materials_data:
                raise ValueError("Invalid Materials.yaml structure: missing 'materials' section")
            
            material_names = list(materials_data['materials'].keys())
            self.logger.info(f"📋 Found {len(material_names)} materials to process")
            
            results = {
                'success': True,
                'total_materials': len(material_names),
                'processed': 0,
                'failed': 0,
                'total_generated': 0,
                'total_skipped': 0,
                'errors': []
            }
            
            # Process each material
            for i, material_name in enumerate(material_names, 1):
                self.logger.info(f"\n[{i}/{len(material_names)}] Processing {material_name}...")
                
                material_result = self.repopulate_material_ai_text_fields(
                    material_name, force_regenerate
                )
                
                if material_result['success']:
                    results['processed'] += 1
                    results['total_generated'] += material_result['generated_count']
                    results['total_skipped'] += material_result['skipped_count']
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'material': material_name,
                        'error': material_result.get('error', 'Unknown error')
                    })
            
            # Final summary
            self.logger.info("\n" + "=" * 80)
            self.logger.info("🎉 REPOPULATION COMPLETE")
            self.logger.info("📊 Results:")
            self.logger.info(f"   • Total materials: {results['total_materials']}")
            self.logger.info(f"   • Successfully processed: {results['processed']}")
            self.logger.info(f"   • Failed: {results['failed']}")
            self.logger.info(f"   • Total fields generated: {results['total_generated']}")
            self.logger.info(f"   • Total fields skipped: {results['total_skipped']}")
            
            if results['errors']:
                self.logger.info("❌ Errors encountered:")
                for error in results['errors'][:5]:  # Show first 5 errors
                    self.logger.info(f"   • {error['material']}: {error['error']}")
                if len(results['errors']) > 5:
                    self.logger.info(f"   • ... and {len(results['errors']) - 5} more errors")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process all materials: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Repopulate AI text fields in Materials.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/repopulate_ai_text_fields.py Aluminum
  python3 scripts/repopulate_ai_text_fields.py --all --force
  python3 scripts/repopulate_ai_text_fields.py Copper --no-force
        """
    )
    
    parser.add_argument(
        'material',
        nargs='?',
        help='Material name to process (use --all for all materials)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all materials in Materials.yaml'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        default=True,
        help='Regenerate existing ai_text_fields (default: True)'
    )
    
    parser.add_argument(
        '--no-force',
        action='store_true',
        help='Skip existing ai_text_fields'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Validate arguments
    if not args.all and not args.material:
        parser.error("Must specify either a material name or --all")
    
    if args.all and args.material:
        parser.error("Cannot specify both material name and --all")
    
    # Determine force setting
    force_regenerate = args.force and not args.no_force
    
    # Initialize repopulator
    repopulator = AITextFieldsRepopulator()
    
    try:
        if args.all:
            # Process all materials
            results = repopulator.repopulate_all_materials(force_regenerate)
            sys.exit(0 if results['success'] else 1)
        else:
            # Process single material
            results = repopulator.repopulate_material_ai_text_fields(
                args.material, force_regenerate
            )
            sys.exit(0 if results['success'] else 1)
            
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()