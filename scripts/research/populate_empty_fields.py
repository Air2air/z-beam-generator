#!/usr/bin/env python3
"""
Populate Empty Fields - Phase 2: API Research
Researches and populates missing safety, regulatory, and technical data.

Usage:
    python3 scripts/research/populate_empty_fields.py --domain compounds --field exposure_limits
    python3 scripts/research/populate_empty_fields.py --domain materials --field contamination
    python3 scripts/research/populate_empty_fields.py --domain contaminants --field thermal_properties
    python3 scripts/research/populate_empty_fields.py --all --dry-run
"""

import os
import sys
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.api.client_factory import APIClientFactory

class EmptyFieldResearcher:
    """Researches and populates empty fields using AI."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client = APIClientFactory.create_client(provider='grok')  # Uses Grok client via factory
        self.stats = {
            'researched': 0,
            'populated': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def research_exposure_limits(self, compound_id: str, compound_data: Dict) -> Dict:
        """Research OSHA/NIOSH/ACGIH exposure limits for a compound."""
        compound_name = compound_data.get('title', compound_id)
        cas_number = compound_data.get('cas_number', 'unknown')
        
        prompt = f"""Research workplace exposure limits for {compound_name} (CAS: {cas_number}).

Provide ONLY the following data in valid YAML format:

exposure_limits:
  osha_pel:
    twa_8hr: <value in ppm or mg/m³>
    stel_15min: <value or null if not applicable>
    ceiling: <value or null if not applicable>
  niosh_rel:
    twa_8hr: <value in ppm or mg/m³>
    stel_15min: <value or null if not applicable>
    ceiling: <value or null if not applicable>
  acgih_tlv:
    twa_8hr: <value in ppm or mg/m³>
    stel_15min: <value or null if not applicable>
    ceiling: <value or null if not applicable>

Use null for values that are not defined by the regulatory body.
If no exposure limits exist, return all null values.
"""
        
        try:
            response = self.client.generate_simple(
                prompt=prompt,
                temperature=0.3,  # Low temperature for factual data
                max_tokens=2000,
                system_prompt="You are a chemical safety expert. Provide accurate regulatory data in YAML format."
            )
            
            # Parse YAML response (strip markdown code fences if present)
            content = response.content if hasattr(response, 'content') else response
            # Remove markdown code fences
            if '```' in content:
                content = content.replace('```yaml', '').replace('```', '').strip()
            limits_data = yaml.safe_load(content)
            return limits_data.get('exposure_limits', {})
            
        except Exception as e:
            print(f"   ❌ Error researching exposure limits: {e}")
            return {}
    
    def research_health_effects(self, compound_id: str, compound_data: Dict) -> List[Dict]:
        """Research health effects for a compound."""
        compound_name = compound_data.get('title', compound_id)
        cas_number = compound_data.get('cas_number', 'unknown')
        
        prompt = f"""Research health effects of {compound_name} (CAS: {cas_number}).

Provide 3-5 primary health effects in valid YAML format:

health_effects:
  - route: inhalation
    effect: <specific health effect>
    severity: <low|moderate|high|severe>
    onset: <immediate|short-term|long-term>
  - route: skin_contact
    effect: <specific health effect>
    severity: <low|moderate|high|severe>
    onset: <immediate|short-term|long-term>
  - route: eye_contact
    effect: <specific health effect>
    severity: <low|moderate|high|severe>
    onset: <immediate|short-term|long-term>

Include only the most significant health effects from credible sources.
"""
        
        try:
            response = self.client.generate_simple(
                prompt=prompt,
                temperature=0.3,
                max_tokens=2000,
                system_prompt="You are a toxicology expert. Provide accurate health effect data in YAML format."
            )
            
            content = response.content if hasattr(response, 'content') else response
            if '```' in content:
                content = content.replace('```yaml', '').replace('```', '').strip()
            effects_data = yaml.safe_load(content)
            return effects_data.get('health_effects', [])
            
        except Exception as e:
            print(f"   ❌ Error researching health effects: {e}")
            return []
    
    def research_nfpa_codes(self, compound_id: str, compound_data: Dict) -> Dict:
        """Research NFPA hazard codes for a compound."""
        compound_name = compound_data.get('title', compound_id)
        cas_number = compound_data.get('cas_number', 'unknown')
        
        prompt = f"""Research NFPA 704 hazard diamond codes for {compound_name} (CAS: {cas_number}).

Provide data in valid YAML format:

nfpa_codes:
  health: <0-4>
  flammability: <0-4>
  instability: <0-4>
  special: <OX|W|SA|null>

Where:
- health: 0 (minimal) to 4 (deadly)
- flammability: 0 (will not burn) to 4 (below 73°F)
- instability: 0 (stable) to 4 (explosive)
- special: OX (oxidizer), W (water reactive), SA (simple asphyxiant), or null
"""
        
        try:
            response = self.client.generate_simple(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1000,
                system_prompt="You are a chemical hazard classification expert. Provide accurate NFPA codes in YAML format."
            )
            
            content = response.content if hasattr(response, 'content') else response
            if '```' in content:
                content = content.replace('```yaml', '').replace('```', '').strip()
            nfpa_data = yaml.safe_load(content)
            return nfpa_data.get('nfpa_codes', {})
            
        except Exception as e:
            print(f"   ❌ Error researching NFPA codes: {e}")
            return {}
    
    def research_contamination_rules(self, material_id: str, material_data: Dict) -> Dict:
        """Research conditional and prohibited contamination rules for a material."""
        material_name = material_data.get('title', material_id)
        
        prompt = f"""Research contamination handling rules for {material_name} in laser cleaning context.

Provide data in valid YAML format:

contamination_rules:
  conditional:
    - pattern: <contamination pattern ID>
      conditions: <when this contamination is appropriate>
      considerations: <special handling requirements>
  prohibited:
    - pattern: <contamination pattern ID>
      reason: <why this contamination is prohibited>
      alternative: <recommended alternative>

Focus on laser cleaning safety and effectiveness.
"""
        
        try:
            response = self.client.generate_simple(
                prompt=prompt,
                temperature=0.4,
                max_tokens=2000,
                system_prompt="You are a laser cleaning expert. Provide contamination handling rules in YAML format."
            )
            
            content = response.content if hasattr(response, 'content') else response
            if '```' in content:
                content = content.replace('```yaml', '').replace('```', '').strip()
            rules_data = yaml.safe_load(content)
            return rules_data.get('contamination_rules', {})
            
        except Exception as e:
            print(f"   ❌ Error researching contamination rules: {e}")
            return {}
    
    def research_melting_point(self, contaminant_id: str, contaminant_data: Dict) -> Optional[float]:
        """Research melting point for a contaminant."""
        contaminant_name = contaminant_data.get('contamination_name', contaminant_id)
        
        prompt = f"""What is the melting point of {contaminant_name}?

Provide ONLY a single numeric value in degrees Celsius, or null if not applicable.
For mixtures or variable compositions, provide a typical/average value.

Response format: <number> or null
"""
        
        try:
            response = self.client.generate_simple(
                prompt=prompt,
                temperature=0.2,
                max_tokens=100,
                system_prompt="You are a materials science expert. Provide accurate melting point data."
            )
            
            # Parse numeric response
            response_text = (response.content if hasattr(response, 'content') else response).strip()
            if response_text.lower() == 'null' or response_text.lower() == 'none':
                return None
            return float(response_text)
            
        except Exception as e:
            print(f"   ❌ Error researching melting point: {e}")
            return None
    
    def populate_compounds(self, limit: Optional[int] = None):
        """Populate empty fields in Compounds.yaml."""
        print("\n" + "="*70)
        print("📦 COMPOUNDS - Researching empty fields")
        print("="*70)
        
        with open('data/compounds/Compounds.yaml', 'r') as f:
            data = yaml.safe_load(f)
        
        compounds = list(data['compounds'].items())
        if limit:
            compounds = compounds[:limit]
        
        for compound_id, compound in compounds:
            compound_name = compound.get('title', compound_id)
            print(f"\n🔬 {compound_name}")
            
            modified = False
            
            # Research exposure limits if missing
            if 'relationships' in compound and 'safety' in compound['relationships']:
                safety = compound['relationships']['safety']
                if 'exposure_limits' in safety and 'items' in safety['exposure_limits']:
                    for limit_item in safety['exposure_limits']['items']:
                        if 'workplace_exposure' in limit_item:
                            wp_exp = limit_item['workplace_exposure']
                            
                            # Check if any exposure limits are empty
                            needs_research = False
                            for category in ['osha_pel', 'niosh_rel', 'acgih_tlv']:
                                if category in wp_exp:
                                    for field in ['twa_8hr', 'stel_15min', 'ceiling']:
                                        if not wp_exp[category].get(field):
                                            needs_research = True
                                            break
                            
                            if needs_research:
                                print("   📊 Researching exposure limits...")
                                limits = self.research_exposure_limits(compound_id, compound)
                                if limits and not self.dry_run:
                                    # Merge researched data
                                    for category, values in limits.items():
                                        if category in wp_exp:
                                            wp_exp[category].update(values)
                                    modified = True
                                    self.stats['researched'] += 1
            
            # Research health effects if missing
            if 'relationships' in compound and 'safety' in compound['relationships']:
                he = compound['relationships']['safety'].get('health_effects', {})
                # Handle both dict and list structures
                if isinstance(he, dict):
                    items = he.get('items', [])
                elif isinstance(he, list):
                    items = he
                else:
                    items = []
                # Check if items contain actual health effects data (not just ID references)
                needs_research = not items or all('route' not in item for item in items)
                
                if needs_research:
                    print("   🏥 Researching health effects...")
                    effects = self.research_health_effects(compound_id, compound)
                    if effects and not self.dry_run:
                        # Ensure health_effects structure exists
                        if 'health_effects' not in compound['relationships']['safety']:
                            compound['relationships']['safety']['health_effects'] = {
                                'presentation': 'card',
                                'items': []
                            }
                        # Add researched effects to items array
                        compound['relationships']['safety']['health_effects']['items'] = effects
                        modified = True
                        self.stats['researched'] += 1
            
            # Research NFPA codes if missing
            if 'relationships' in compound and 'safety' in compound['relationships']:
                if 'regulatory_classification' in compound['relationships']['safety']:
                    reg_class = compound['relationships']['safety']['regulatory_classification']
                    if 'items' in reg_class:
                        for item in reg_class['items']:
                            if 'nfpa_codes' in item and not item['nfpa_codes'].get('special'):
                                print("   🔥 Researching NFPA codes...")
                                nfpa = self.research_nfpa_codes(compound_id, compound)
                                if nfpa and not self.dry_run:
                                    item['nfpa_codes'].update(nfpa)
                                    modified = True
                                    self.stats['researched'] += 1
            
            if modified:
                self.stats['populated'] += 1
        
        # Save if not dry run
        if not self.dry_run:
            with open('data/compounds/Compounds.yaml', 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def populate_materials(self, limit: Optional[int] = None):
        """Populate empty fields in Materials.yaml."""
        print("\n" + "="*70)
        print("🔨 MATERIALS - Researching empty fields")
        print("="*70)
        
        with open('data/materials/Materials.yaml', 'r') as f:
            data = yaml.safe_load(f)
        
        materials = list(data['materials'].items())
        if limit:
            materials = materials[:limit]
        
        for material_id, material in materials:
            material_name = material.get('title', material_id)
            
            # Research contamination rules if missing
            if 'contamination' in material:
                if not material['contamination'].get('conditional') or not material['contamination'].get('prohibited'):
                    print(f"\n🔬 {material_name}")
                    print("   🧪 Researching contamination rules...")
                    rules = self.research_contamination_rules(material_id, material)
                    if rules and not self.dry_run:
                        if 'conditional' in rules:
                            material['contamination']['conditional'] = rules['conditional']
                        if 'prohibited' in rules:
                            material['contamination']['prohibited'] = rules['prohibited']
                        self.stats['researched'] += 1
                        self.stats['populated'] += 1
        
        # Save if not dry run
        if not self.dry_run:
            with open('data/materials/Materials.yaml', 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def populate_contaminants(self, limit: Optional[int] = None):
        """Populate empty fields in Contaminants.yaml."""
        print("\n" + "="*70)
        print("🧪 CONTAMINANTS - Researching empty fields")
        print("="*70)
        
        with open('data/contaminants/Contaminants.yaml', 'r') as f:
            data = yaml.safe_load(f)
        
        patterns = list(data['contamination_patterns'].items())
        if limit:
            patterns = patterns[:limit]
        
        for pattern_id, pattern in patterns:
            pattern_name = pattern.get('contamination_name', pattern_id)
            
            # Research melting point if missing
            if 'relationships' in pattern and 'operational' in pattern['relationships']:
                if 'laser_properties' in pattern['relationships']['operational']:
                    laser_props = pattern['relationships']['operational']['laser_properties']
                    if 'items' in laser_props:
                        for item in laser_props['items']:
                            if 'thermal_properties' in item:
                                if not item['thermal_properties'].get('melting_point'):
                                    print(f"\n🔬 {pattern_name}")
                                    print("   🌡️  Researching melting point...")
                                    melting_point = self.research_melting_point(pattern_id, pattern)
                                    if melting_point is not None and not self.dry_run:
                                        item['thermal_properties']['melting_point'] = melting_point
                                        self.stats['researched'] += 1
                                        self.stats['populated'] += 1
        
        # Save if not dry run
        if not self.dry_run:
            with open('data/contaminants/Contaminants.yaml', 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def print_stats(self):
        """Print research statistics."""
        print("\n" + "="*70)
        print("📊 RESEARCH STATISTICS")
        print("="*70)
        print(f"Researched: {self.stats['researched']}")
        print(f"Populated: {self.stats['populated']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No changes saved")


def main():
    parser = argparse.ArgumentParser(description='Populate empty fields with AI research')
    parser.add_argument('--domain', choices=['compounds', 'materials', 'contaminants', 'all'],
                       default='all', help='Domain to research')
    parser.add_argument('--limit', type=int, help='Limit number of items to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be researched without saving')
    
    args = parser.parse_args()
    
    researcher = EmptyFieldResearcher(dry_run=args.dry_run)
    
    print("="*70)
    print("🔬 EMPTY FIELD RESEARCH - PHASE 2")
    print("="*70)
    
    if args.domain in ['compounds', 'all']:
        researcher.populate_compounds(limit=args.limit)
    
    if args.domain in ['materials', 'all']:
        researcher.populate_materials(limit=args.limit)
    
    if args.domain in ['contaminants', 'all']:
        researcher.populate_contaminants(limit=args.limit)
    
    researcher.print_stats()
    
    print("\n✅ Research complete!")


if __name__ == '__main__':
    main()
