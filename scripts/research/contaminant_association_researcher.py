#!/usr/bin/env python3
"""
Contaminant-Material Association Researcher

Researches which materials each contaminant commonly appears on using Grok API.
Updates DomainAssociations.yaml with discovered associations.

Usage:
    python3 scripts/research/contaminant_association_researcher.py --all
    python3 scripts/research/contaminant_association_researcher.py --contaminants rust-oxidation-contamination paint-residue-contamination
    python3 scripts/research/contaminant_association_researcher.py --skip-existing
"""

import argparse
import yaml
import sys
from pathlib import Path
from typing import List, Dict, Any, Set
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.api.client_factory import APIClientFactory


class ContaminantAssociationResearcher:
    """Research material associations for contaminants using Grok API."""
    
    def __init__(self):
        """Initialize the researcher with Grok API client."""
        self.client = APIClientFactory.create_client(provider="grok")
        self.contaminants_file = Path('data/contaminants/Contaminants.yaml')
        self.associations_file = Path('data/associations/DomainAssociations.yaml')
        self.materials_file = Path('data/materials/Materials.yaml')
        
        # Load available materials
        with open(self.materials_file, 'r') as f:
            materials_data = yaml.safe_load(f)
            self.available_materials = list(materials_data.get('materials', {}).keys())
        
        print(f"📋 Loaded {len(self.available_materials)} available materials")
    
    def load_contaminants(self) -> Dict[str, Any]:
        """Load all contaminants from Contaminants.yaml."""
        with open(self.contaminants_file, 'r') as f:
            data = yaml.safe_load(f)
        return data.get('contamination_patterns', {})
    
    def load_associations(self) -> Dict[str, Any]:
        """Load existing associations from DomainAssociations.yaml."""
        with open(self.associations_file, 'r') as f:
            return yaml.safe_load(f)
    
    def save_associations(self, associations_data: Dict[str, Any]):
        """Save updated associations to DomainAssociations.yaml."""
        with open(self.associations_file, 'w') as f:
            yaml.dump(associations_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def get_contaminants_needing_associations(self, associations_data: Dict[str, Any]) -> List[str]:
        """Get list of contaminants that have no material associations."""
        material_to_contaminants = associations_data.get('material_to_contaminants', {})
        
        # Find all contaminants that already have associations
        associated_contaminants = set()
        for material, contaminants in material_to_contaminants.items():
            if isinstance(contaminants, list):
                associated_contaminants.update(contaminants)
        
        # Get all contaminants
        all_contaminants = set(self.load_contaminants().keys())
        
        # Return those without associations
        return sorted(list(all_contaminants - associated_contaminants))
    
    def research_material_associations(self, contaminant_id: str, contaminant_data: Dict[str, Any]) -> List[str]:
        """
        Research which materials this contaminant commonly appears on.
        
        Args:
            contaminant_id: Contaminant slug
            contaminant_data: Contaminant metadata
            
        Returns:
            List of material slugs (lowercase) that this contaminant appears on
        """
        contaminant_name = contaminant_data.get('name', contaminant_id)
        category = contaminant_data.get('category', 'unknown')
        description = contaminant_data.get('description', '')
        
        prompt = self._build_research_prompt(contaminant_id, contaminant_name, category, description)
        
        print(f"🔬 Researching associations for: {contaminant_name}")
        
        try:
            response = self.client.generate_simple(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for factual research
                max_tokens=2000
            )
            
            # Parse the response
            materials = self._parse_research_response(response.content)
            
            print(f"   ✅ Found {len(materials)} material associations")
            return materials
            
        except Exception as e:
            print(f"   ❌ Error researching {contaminant_name}: {str(e)}")
            return []
    
    def _build_research_prompt(self, contaminant_id: str, name: str, category: str, description: str) -> str:
        """Build comprehensive research prompt for Grok."""
        
        # Format available materials for prompt
        materials_list = "\n".join([f"- {m}" for m in sorted(self.available_materials)])
        
        prompt = f"""You are a laser cleaning expert researching which materials commonly have specific contaminants.

CONTAMINANT: {name}
ID: {contaminant_id}
CATEGORY: {category}
DESCRIPTION: {description}

TASK: Identify which materials from the list below commonly have this contaminant on their surfaces.

AVAILABLE MATERIALS:
{materials_list}

CRITERIA FOR SELECTION:
1. The contaminant must COMMONLY appear on the material (industrial, commercial, or environmental)
2. Include materials where this contaminant is a known cleaning challenge
3. Consider both indoor and outdoor applications
4. Include at least 20-30 materials (more if the contaminant is very common)
5. Do NOT include materials where this contaminant would be extremely rare or impossible

EXAMPLES:
- Rust oxidation → steel, iron, carbon steel, cast iron (ferrous metals)
- Paint residue → ALL materials (universal contaminant)
- Salt residue → outdoor materials (steel, aluminum, concrete, stone)
- Brake dust → aluminum, steel, cast iron (automotive/transportation)

OUTPUT FORMAT - Return ONLY a YAML list (no other text):
```yaml
materials:
  - material-slug-1
  - material-slug-2
  - material-slug-3
  [etc - include 20-30+ materials]
```

IMPORTANT: 
- Use EXACT slugs from the available materials list above
- Return lowercase slugs with hyphens (e.g., stainless-steel-316)
- Include both common AND less common but realistic occurrences
- Be comprehensive - more associations = more useful database
"""
        return prompt
    
    def _parse_research_response(self, response: str) -> List[str]:
        """
        Parse Grok response and extract material list.
        
        Args:
            response: Grok API response text
            
        Returns:
            List of material slugs
        """
        # Extract YAML from code blocks
        yaml_content = response
        if '```yaml' in response:
            yaml_content = response.split('```yaml')[1].split('```')[0]
        elif '```' in response:
            yaml_content = response.split('```')[1].split('```')[0]
        
        try:
            data = yaml.safe_load(yaml_content)
            materials = data.get('materials', [])
            
            # Validate materials exist in our database
            valid_materials = []
            for material in materials:
                material_lower = material.lower().strip()
                if material_lower in [m.lower() for m in self.available_materials]:
                    valid_materials.append(material_lower)
                else:
                    print(f"      ⚠️  Skipping invalid material: {material}")
            
            return valid_materials
            
        except yaml.YAMLError as e:
            print(f"   ❌ YAML parsing error: {e}")
            return []
    
    def update_associations_file(self, contaminant_id: str, materials: List[str]):
        """
        Update DomainAssociations.yaml with new material associations.
        
        Args:
            contaminant_id: Contaminant slug
            materials: List of material slugs to associate
        """
        associations_data = self.load_associations()
        material_to_contaminants = associations_data.get('material_to_contaminants', {})
        
        # Add contaminant to each material's list
        for material in materials:
            if material not in material_to_contaminants:
                material_to_contaminants[material] = []
            
            if contaminant_id not in material_to_contaminants[material]:
                material_to_contaminants[material].append(contaminant_id)
        
        associations_data['material_to_contaminants'] = material_to_contaminants
        self.save_associations(associations_data)
    
    def research_all_unmapped_contaminants(self, skip_existing: bool = True):
        """
        Research associations for all contaminants that don't have any.
        
        Args:
            skip_existing: If True, skip contaminants that already have associations
        """
        associations_data = self.load_associations()
        contaminants_data = self.load_contaminants()
        
        # Get contaminants needing associations
        if skip_existing:
            contaminants_to_research = self.get_contaminants_needing_associations(associations_data)
            print(f"📊 Found {len(contaminants_to_research)} contaminants without associations")
        else:
            contaminants_to_research = list(contaminants_data.keys())
            print(f"📊 Researching all {len(contaminants_to_research)} contaminants")
        
        success_count = 0
        failed_count = 0
        skipped_count = 0
        
        for i, contaminant_id in enumerate(contaminants_to_research, 1):
            print(f"\n{'='*70}")
            print(f"📋 CONTAMINANT {i}/{len(contaminants_to_research)}")
            print(f"{'='*70}")
            
            contaminant_data = contaminants_data.get(contaminant_id, {})
            
            # Research associations
            materials = self.research_material_associations(contaminant_id, contaminant_data)
            
            if materials:
                # Update associations file
                self.update_associations_file(contaminant_id, materials)
                success_count += 1
                print(f"   💾 Saved {len(materials)} associations for {contaminant_id}")
            else:
                failed_count += 1
                print(f"   ❌ No associations found for {contaminant_id}")
            
            # Small delay to avoid rate limiting
            if i < len(contaminants_to_research):
                time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"📊 RESEARCH SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Success: {success_count}/{len(contaminants_to_research)}")
        print(f"❌ Failed: {failed_count}/{len(contaminants_to_research)}")
        print(f"⏭️  Skipped: {skipped_count}/{len(contaminants_to_research)}")
        print(f"\n{'='*70}")
        print(f"✅ Association research complete")
        print(f"{'='*70}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Research material associations for contaminants using Grok API'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Research associations for all contaminants without associations'
    )
    parser.add_argument(
        '--contaminants',
        nargs='+',
        help='Specific contaminant IDs to research'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        default=True,
        help='Skip contaminants that already have associations (default: True)'
    )
    
    args = parser.parse_args()
    
    researcher = ContaminantAssociationResearcher()
    
    if args.all:
        researcher.research_all_unmapped_contaminants(skip_existing=args.skip_existing)
    elif args.contaminants:
        # Research specific contaminants
        contaminants_data = researcher.load_contaminants()
        for contaminant_id in args.contaminants:
            if contaminant_id in contaminants_data:
                materials = researcher.research_material_associations(
                    contaminant_id,
                    contaminants_data[contaminant_id]
                )
                if materials:
                    researcher.update_associations_file(contaminant_id, materials)
            else:
                print(f"❌ Contaminant not found: {contaminant_id}")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
