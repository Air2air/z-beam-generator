"""
Fix ALL Contaminant URLs in Compounds.yaml

Updates all contaminant URLs in compound relationships to use correct
full_path from Contaminants.yaml, regardless of whether they're in
DomainAssociations.yaml or not.

Usage:
    python3 scripts/fix_all_contaminant_urls_in_compounds.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def fix_all_contaminant_urls():
    """Fix all contaminant URLs in Compounds.yaml using full_path from Contaminants.yaml"""
    
    # Load Contaminants.yaml to get full_path data
    contaminants_file = Path('data/contaminants/contaminants.yaml')
    logger.info(f"Loading {contaminants_file}...")
    
    with open(contaminants_file, 'r', encoding='utf-8') as f:
        contaminants_data = yaml.safe_load(f)
    
    contamination_patterns = contaminants_data.get('contamination_patterns', {})
    logger.info(f"Loaded {len(contamination_patterns)} contamination patterns")
    
    # Build lookup: ID -> full_path
    contaminant_urls = {}
    for cont_id, cont_data in contamination_patterns.items():
        full_path = cont_data.get('full_path')
        if full_path:
            contaminant_urls[cont_id] = full_path
    
    logger.info(f"Built URL lookup for {len(contaminant_urls)} contaminants")
    
    # Load Compounds.yaml
    compounds_file = Path('data/compounds/Compounds.yaml')
    logger.info(f"\nLoading {compounds_file}...")
    
    with open(compounds_file, 'r', encoding='utf-8') as f:
        compounds_data = yaml.safe_load(f)
    
    compounds = compounds_data.get('compounds', {})
    logger.info(f"Found {len(compounds)} compounds\n")
    
    total_updated = 0
    total_fixed = 0
    
    # Fix each compound's relationships
    for compound_id, compound_data in compounds.items():
        if 'relationships' not in compound_data:
            continue
        
        relationships = compound_data['relationships']
        if 'produced_by_contaminants' not in relationships:
            continue
        
        contaminants = relationships['produced_by_contaminants']
        if not contaminants:
            continue
        
        logger.info(f"Processing: {compound_id} ({len(contaminants)} contaminants)")
        
        fixed_in_compound = 0
        
        for contaminant in contaminants:
            cont_id = contaminant.get('id')
            old_url = contaminant.get('url', '')
            
            if not cont_id:
                continue
            
            # Get correct URL from full_path
            correct_url = contaminant_urls.get(cont_id)
            
            if not correct_url:
                logger.warning(f"  ⚠️  No full_path found for: {cont_id}")
                continue
            
            # Check if URL needs updating
            if old_url != correct_url:
                contaminant['url'] = correct_url
                logger.info(f"  ✏️  {cont_id}")
                logger.info(f"     OLD: {old_url}")
                logger.info(f"     NEW: {correct_url}")
                fixed_in_compound += 1
                total_fixed += 1
        
        if fixed_in_compound > 0:
            total_updated += 1
    
    # Write back to file
    logger.info(f"\n💾 Writing updated Compounds.yaml...")
    logger.info(f"   Updated {total_updated} compounds")
    logger.info(f"   Fixed {total_fixed} contaminant URLs")
    
    with open(compounds_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(compounds_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    logger.info(f"✅ Complete!")
    logger.info(f"\nNext steps:")
    logger.info(f"1. Re-export compounds: python3 run.py --export --domain compounds")
    logger.info(f"2. Verify all contaminant URLs end with -contamination")


if __name__ == '__main__':
    fix_all_contaminant_urls()
