#!/usr/bin/env python3
"""
Research Laser Properties for Contamination Patterns

CLI tool to research laser-specific scientific data for contamination patterns
using AI (Grok, Gemini, etc.).

Usage:
    # Research single property type
    python3 scripts/research_laser_properties.py --pattern rust_oxidation --type optical_properties
    
    # Research complete profile (all properties)
    python3 scripts/research_laser_properties.py --pattern rust_oxidation --type complete_profile
    
    # Research for specific material context
    python3 scripts/research_laser_properties.py --pattern rust_oxidation --type thermal_properties --material Steel
    
    # Research all patterns
    python3 scripts/research_laser_properties.py --all-patterns --type optical_properties
    
    # Save results to Contaminants.yaml
    python3 scripts/research_laser_properties.py --pattern rust_oxidation --type complete_profile --save

Author: AI Assistant
Date: November 25, 2025
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from domains.contaminants.research.laser_properties_researcher import LaserPropertiesResearcher
from domains.contaminants.research.base import ContaminationResearchSpec
from domains.contaminants.library import ContaminationLibrary
from shared.api.client_factory import create_api_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def setup_api_client():
    """Setup API client for research."""
    try:
        client = create_api_client()
        logger.info("✅ API client initialized")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize API client: {e}")
        logger.info("💡 Make sure XAI_API_KEY or GROQ_API_KEY is set in environment or .env file")
        sys.exit(1)


def research_pattern(
    researcher: LaserPropertiesResearcher,
    pattern_id: str,
    research_type: str,
    material_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Research laser properties for a single pattern.
    
    Args:
        researcher: LaserPropertiesResearcher instance
        pattern_id: Pattern identifier
        research_type: Type of research to perform
        material_context: Optional material name for context
    
    Returns:
        Dictionary with research results
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"🔬 RESEARCHING: {pattern_id}")
    logger.info(f"📋 Type: {research_type}")
    if material_context:
        logger.info(f"🔧 Material Context: {material_context}")
    logger.info(f"{'='*80}\n")
    
    # Create research spec
    spec = ContaminationResearchSpec(
        pattern_id=pattern_id,
        research_type=research_type,
        material_context=material_context
    )
    
    # Execute research
    result = researcher.research(pattern_id, spec)
    
    # Display results
    if result.success:
        logger.info(f"✅ SUCCESS - Confidence: {result.confidence:.1%}\n")
        logger.info("📊 RESEARCHED DATA:")
        logger.info("─" * 80)
        
        # Pretty print the data
        if research_type == 'complete_profile':
            for category, data in result.data.items():
                logger.info(f"\n🔹 {category.replace('_', ' ').title()}:")
                logger.info(yaml.dump(data, default_flow_style=False, indent=2))
        else:
            logger.info(yaml.dump(result.data, default_flow_style=False, indent=2))
        
        logger.info("─" * 80)
        
        return {
            'success': True,
            'pattern_id': pattern_id,
            'research_type': research_type,
            'data': result.data,
            'confidence': result.confidence,
            'metadata': result.metadata
        }
    else:
        logger.error(f"❌ FAILED: {result.error}\n")
        return {
            'success': False,
            'pattern_id': pattern_id,
            'research_type': research_type,
            'error': result.error
        }


def save_to_contaminants_yaml(pattern_id: str, research_data: Dict[str, Any]):
    """
    Save researched laser properties to Contaminants.yaml.
    
    Args:
        pattern_id: Pattern identifier
        research_data: Researched data to save
    """
    contaminants_path = Path("data/contaminants/Contaminants.yaml")
    
    # Load existing data
    with open(contaminants_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Find pattern
    if pattern_id not in data['contamination_patterns']:
        logger.error(f"❌ Pattern {pattern_id} not found in Contaminants.yaml")
        return False
    
    # Add laser_properties field
    pattern = data['contamination_patterns'][pattern_id]
    
    if 'laser_properties' not in pattern:
        pattern['laser_properties'] = {}
    
    # Merge research data
    for category, category_data in research_data.items():
        if category != 'complete_profile':
            pattern['laser_properties'][category] = category_data
    
    # Save updated data
    with open(contaminants_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    
    logger.info(f"\n💾 Saved laser properties to: {contaminants_path}")
    logger.info(f"   Pattern: {pattern_id}")
    logger.info(f"   Categories: {', '.join(research_data.keys())}")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Research laser-specific properties for contamination patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Research optical properties for rust
  python3 scripts/research_laser_properties.py --pattern rust_oxidation --type optical_properties
  
  # Research complete profile and save
  python3 scripts/research_laser_properties.py --pattern rust_oxidation --type complete_profile --save
  
  # Research with material context
  python3 scripts/research_laser_properties.py --pattern copper_patina --type thermal_properties --material Copper
  
  # Research all patterns (batch mode)
  python3 scripts/research_laser_properties.py --all-patterns --type optical_properties --save
  
Research Types:
  optical_properties       - Absorption, reflectivity, refractive index
  thermal_properties       - Ablation thresholds, decomposition temps
  removal_characteristics  - Mechanisms, byproducts, efficiency
  layer_properties         - Thickness, penetration depth, adhesion
  laser_parameters         - Recommended wavelength, fluence, scan speed
  safety_data              - Fumes, ventilation, PPE requirements
  selectivity_ratios       - Material-specific selectivity
  complete_profile         - All categories in one research session
        """
    )
    
    parser.add_argument(
        '--pattern',
        type=str,
        help='Pattern ID to research (e.g., rust_oxidation, copper_patina)'
    )
    
    parser.add_argument(
        '--all-patterns',
        action='store_true',
        help='Research all patterns in Contaminants.yaml'
    )
    
    parser.add_argument(
        '--type',
        type=str,
        required=True,
        choices=[
            'optical_properties',
            'thermal_properties',
            'removal_characteristics',
            'layer_properties',
            'laser_parameters',
            'safety_data',
            'selectivity_ratios',
            'complete_profile'
        ],
        help='Type of laser properties to research'
    )
    
    parser.add_argument(
        '--material',
        type=str,
        help='Material context for research (e.g., Steel, Aluminum)'
    )
    
    parser.add_argument(
        '--save',
        action='store_true',
        help='Save results to Contaminants.yaml'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Optional output file for results (JSON format)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.pattern and not args.all_patterns:
        parser.error("Must specify either --pattern or --all-patterns")
    
    if args.pattern and args.all_patterns:
        parser.error("Cannot specify both --pattern and --all-patterns")
    
    # Setup
    api_client = setup_api_client()
    researcher = LaserPropertiesResearcher(api_client)
    library = ContaminationLibrary()
    
    # Get patterns to research
    if args.all_patterns:
        all_patterns = library.list_patterns()
        if isinstance(all_patterns, dict):
            patterns = list(all_patterns.keys())
        else:
            patterns = [p.id if hasattr(p, 'id') else str(p) for p in all_patterns]
        logger.info(f"📋 Researching {len(patterns)} patterns")
    else:
        patterns = [args.pattern]
    
    # Research each pattern
    results = []
    for pattern_id in patterns:
        try:
            result = research_pattern(
                researcher,
                pattern_id,
                args.type,
                args.material
            )
            results.append(result)
            
            # Save if requested
            if args.save and result['success']:
                save_to_contaminants_yaml(pattern_id, result['data'])
        
        except Exception as e:
            logger.error(f"❌ Error researching {pattern_id}: {e}")
            results.append({
                'success': False,
                'pattern_id': pattern_id,
                'error': str(e)
            })
    
    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("📊 RESEARCH SUMMARY")
    logger.info(f"{'='*80}")
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    logger.info(f"✅ Successful: {successful}/{len(results)}")
    if failed > 0:
        logger.info(f"❌ Failed: {failed}/{len(results)}")
    
    if successful > 0:
        avg_confidence = sum(r['confidence'] for r in results if r['success']) / successful
        logger.info(f"📈 Average Confidence: {avg_confidence:.1%}")
    
    # Save to output file if requested
    if args.output:
        import json
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        logger.info(f"\n💾 Results saved to: {output_path}")
    
    logger.info(f"{'='*80}\n")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
