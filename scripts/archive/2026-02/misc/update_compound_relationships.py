"""
Update Compound Relationships with Correct full_path URLs

Problem: Compounds.yaml has relationships with old URLs baked in.
Solution: Regenerate relationships using domain_associations.py which now reads from full_path.

Usage:
    python3 scripts/update_compound_relationships.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
import logging
from shared.validation.domain_associations import DomainAssociationsValidator

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def update_compound_relationships():
    """Update all compound relationships with correct URLs from full_path"""
    
    # Load Compounds.yaml
    compounds_file = Path('data/compounds/Compounds.yaml')
    logger.info(f"Loading {compounds_file}...")
    
    with open(compounds_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    compounds = data.get('compounds', {})
    logger.info(f"Found {len(compounds)} compounds")
    
    # Initialize validator
    validator = DomainAssociationsValidator()
    validator.load()
    
    updated_count = 0
    
    # Update each compound
    for compound_id, compound_data in compounds.items():
        logger.info(f"\nProcessing: {compound_id}")
        
        # Get fresh relationships from domain_associations
        # DomainAssociations uses full IDs like "pahs-compound"
        full_compound_id = compound_id if compound_id.endswith('-compound') else f"{compound_id}-compound"
        contaminants = validator.get_contaminants_for_compound(full_compound_id)
        
        if not contaminants:
            logger.info(f"  No contaminants found for {compound_id}")
            continue
        
        # Update relationships
        if 'relationships' not in compound_data:
            compound_data['relationships'] = {}
        
        old_contaminants = compound_data['relationships'].get('produced_by_contaminants', [])
        
        # Show changes
        logger.info(f"  Found {len(contaminants)} contaminants:")
        for cont in contaminants:
            old_url = None
            for old in old_contaminants:
                if old.get('id') == cont['id']:
                    old_url = old.get('url')
                    break
            
            if old_url != cont['url']:
                logger.info(f"    ✏️  {cont['id']}")
                logger.info(f"       OLD: {old_url}")
                logger.info(f"       NEW: {cont['url']}")
            else:
                logger.info(f"    ✅ {cont['id']}: {cont['url']}")
        
        # Update with fresh data
        compound_data['relationships']['produced_by_contaminants'] = contaminants
        updated_count += 1
    
    # Write back to file
    logger.info(f"\n💾 Writing updated Compounds.yaml...")
    logger.info(f"   Updated {updated_count} compounds")
    
    with open(compounds_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    logger.info(f"✅ Complete!")
    logger.info(f"\nNext steps:")
    logger.info(f"1. Re-export compounds: python3 run.py --export --domain compounds")
    logger.info(f"2. Verify fire-damage URL in pahs-compound.yaml")


if __name__ == '__main__':
    update_compound_relationships()
