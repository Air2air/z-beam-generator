#!/usr/bin/env python3
"""
Generate Linkage Descriptions
==============================

Generates contextual descriptions for domain linkages using the text generation system.
Uses prompts from prompts/{domain}/*_description.txt files.

Usage:
    # Generate for specific domain and linkage field
    python3 scripts/generation/generate_linkage_descriptions.py --domain materials --field produces_compounds --item "Aluminum"
    
    # Generate all linkages for an item
    python3 scripts/generation/generate_linkage_descriptions.py --domain materials --item "Aluminum" --all-linkages
    
    # Batch generate for all items in domain
    python3 scripts/generation/generate_linkage_descriptions.py --domain materials --field produces_compounds --batch
    
    # Dry run to preview
    python3 scripts/generation/generate_linkage_descriptions.py --domain materials --field produces_compounds --item "Aluminum" --dry-run
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.utils.yaml_utils import load_yaml_fast as load_yaml, dump_yaml_fast as save_yaml
from shared.api.client_factory import create_api_client
from domains.materials.coordinator import MaterialsCoordinator


# Domain linkage field mappings
DOMAIN_LINKAGE_FIELDS = {
    'materials': [
        'produces_compounds',
        'removes_contaminants', 
        'related_materials',
        'related_settings'
    ],
    'contaminants': [
        'produces_compounds',
        'related_materials',
        'related_settings'
    ],
    'compounds': [
        'found_in_contaminants',
        'produced_from_materials',
        'related_settings'
    ],
    'settings': [
        'applies_to_materials',
        'effective_against_contaminants',
        'relevant_compounds'
    ]
}

# Data file paths
DATA_FILES = {
    'materials': 'data/materials/Materials.yaml',
    'contaminants': 'data/contaminants/Contaminants.yaml',
    'compounds': 'data/compounds/Compounds.yaml',
    'settings': 'data/settings/Settings.yaml'
}

# Items key in data files
ITEMS_KEYS = {
    'materials': 'materials',
    'contaminants': 'contaminants',
    'compounds': 'compounds',
    'settings': 'settings'
}


class LinkageDescriptionGenerator:
    """Generates contextual descriptions for domain linkages."""
    
    def __init__(self, domain: str, dry_run: bool = False):
        self.domain = domain
        self.dry_run = dry_run
        self.data_file = Path(PROJECT_ROOT / DATA_FILES[domain])
        self.items_key = ITEMS_KEYS[domain]
        
        # Load data
        print(f"📂 Loading {domain} data from {self.data_file}")
        self.data = load_yaml(self.data_file)
        
        # Initialize generator
        print(f"🔧 Initializing text generation system...")
        self.api_client = create_api_client()
        
        # Use domain coordinator for materials domain
        if domain == 'materials':
            self.generator = MaterialsCoordinator(self.api_client)
        else:
            # For other domains, will need similar coordinators
            raise NotImplementedError(f"Domain '{domain}' not yet supported. Only 'materials' is currently implemented.")
        
    def generate_description(
        self, 
        item_name: str, 
        field: str,
        author_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate description for a specific linkage field.
        
        Args:
            item_name: Name of the item (e.g., "Aluminum", "Rust Contamination")
            field: Linkage field (e.g., "produces_compounds")
            author_id: Optional author ID for voice (defaults to item's author)
            
        Returns:
            Generated description text or None if failed
        """
        # Validate field
        if field not in DOMAIN_LINKAGE_FIELDS[self.domain]:
            print(f"❌ Invalid field '{field}' for domain '{self.domain}'")
            print(f"   Valid fields: {', '.join(DOMAIN_LINKAGE_FIELDS[self.domain])}")
            return None
        
        # Get item data
        items = self.data.get(self.items_key, {})
        item_data = items.get(item_name)
        
        if not item_data:
            print(f"❌ Item '{item_name}' not found in {self.domain}")
            return None
        
        # Get author
        if not author_id:
            author_data = item_data.get('author', {})
            author_id = author_data.get('id') if isinstance(author_data, dict) else None
            
        if not author_id:
            print(f"⚠️  No author found for {item_name}, using default")
            author_id = 'todd-dunning'  # Default
        
        # Generate using text generation system
        print(f"\n🎨 Generating {field} description for {item_name}")
        print(f"   Author: {author_id}")
        print(f"   Prompt: prompts/{self.domain}/{field}_description.txt")
        
        try:
            result = self.generator.generate(
                material_name=item_name,  # Generator uses material_name parameter
                component_type=f"{field}_description"
            )
            
            if result and hasattr(result, 'content') and result.content:
                return result.content
            else:
                print("❌ Generation failed or returned empty content")
                
        except Exception as e:
            print(f"❌ Error generating description: {e}")
            return None
    
    def save_description(
        self, 
        item_name: str, 
        field: str, 
        description: str
    ) -> bool:
        """
        Save generated description to data file.
        
        Args:
            item_name: Name of the item
            field: Linkage field
            description: Generated description text
            
        Returns:
            True if saved successfully
        """
        if self.dry_run:
            print(f"🔍 [DRY RUN] Would save to {item_name}.relationships.{field}.description")
            print(f"   Content: {description[:100]}...")
            return True
        
        # Get item
        items = self.data.get(self.items_key, {})
        item_data = items.get(item_name)
        
        if not item_data:
            return False
        
        # Ensure relationships exists
        if 'relationships' not in item_data:
            item_data['relationships'] = {}
        
        # Ensure field exists
        if field not in item_data['relationships']:
            item_data['relationships'][field] = {}
        
        # Save description
        item_data['relationships'][field]['description'] = description
        
        # Save to file
        print(f"💾 Saving to {self.data_file}")
        save_yaml(self.data, self.data_file)
        
        print(f"✅ Saved {field} description for {item_name}")
        return True
    
    def generate_and_save(
        self, 
        item_name: str, 
        field: str,
        author_id: Optional[str] = None
    ) -> bool:
        """Generate and save description in one operation."""
        description = self.generate_description(item_name, field, author_id)
        
        if description:
            return self.save_description(item_name, field, description)
        return False
    
    def generate_all_linkages(
        self, 
        item_name: str,
        author_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Generate descriptions for all linkage fields for an item.
        
        Returns:
            Dict of {field: success_status}
        """
        results = {}
        
        for field in DOMAIN_LINKAGE_FIELDS[self.domain]:
            print(f"\n{'='*80}")
            print(f"Generating: {item_name} → {field}")
            print(f"{'='*80}")
            
            success = self.generate_and_save(item_name, field, author_id)
            results[field] = success
        
        return results
    
    def batch_generate(
        self, 
        field: str,
        limit: Optional[int] = None
    ) -> Dict[str, bool]:
        """
        Generate descriptions for all items in domain for a specific field.
        
        Args:
            field: Linkage field to generate
            limit: Optional limit on number of items to process
            
        Returns:
            Dict of {item_name: success_status}
        """
        items = self.data.get(self.items_key, {})
        results = {}
        
        print(f"\n{'='*80}")
        print(f"BATCH GENERATION: {self.domain}.{field}")
        print(f"Total items: {len(items)}")
        if limit:
            print(f"Limit: {limit}")
        print(f"{'='*80}\n")
        
        for i, item_name in enumerate(items.keys(), 1):
            if limit and i > limit:
                break
            
            print(f"\n[{i}/{len(items) if not limit else limit}] {item_name}")
            print(f"{'-'*80}")
            
            success = self.generate_and_save(item_name, field)
            results[item_name] = success
        
        # Summary
        successful = sum(1 for s in results.values() if s)
        print(f"\n{'='*80}")
        print(f"BATCH COMPLETE: {successful}/{len(results)} successful")
        print(f"{'='*80}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate contextual descriptions for domain linkages"
    )
    
    parser.add_argument(
        '--domain',
        required=True,
        choices=['materials', 'contaminants', 'compounds', 'settings', 'applications'],
        help='Domain to generate linkages for'
    )
    
    parser.add_argument(
        '--field',
        help='Linkage field to generate (e.g., produces_compounds)'
    )
    
    parser.add_argument(
        '--item',
        help='Specific item name to generate for'
    )
    
    parser.add_argument(
        '--all-linkages',
        action='store_true',
        help='Generate all linkage fields for the item'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Generate for all items in domain (requires --field)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of items in batch mode'
    )
    
    parser.add_argument(
        '--author',
        help='Author ID for voice (defaults to item author)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without saving'
    )
    
    args = parser.parse_args()
    
    # Validation
    if args.batch and not args.field:
        parser.error("--batch requires --field")
    
    if args.all_linkages and not args.item:
        parser.error("--all-linkages requires --item")
    
    if not args.batch and not args.item:
        parser.error("Either --item or --batch is required")
    
    # Create generator
    generator = LinkageDescriptionGenerator(args.domain, args.dry_run)
    
    # Execute based on mode
    if args.batch:
        generator.batch_generate(args.field, args.limit)
        
    elif args.all_linkages:
        results = generator.generate_all_linkages(args.item, args.author)
        
        # Summary
        successful = sum(1 for s in results.values() if s)
        print(f"\n{'='*80}")
        print(f"✅ Generated {successful}/{len(results)} linkage descriptions for {args.item}")
        print(f"{'='*80}")
        
    else:
        # Single generation
        success = generator.generate_and_save(args.item, args.field, args.author)
        
        if success:
            print(f"\n✅ Successfully generated {args.field} for {args.item}")
        else:
            print(f"\n❌ Failed to generate {args.field} for {args.item}")
            sys.exit(1)


if __name__ == '__main__':
    main()
