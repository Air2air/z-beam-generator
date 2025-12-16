#!/usr/bin/env python3
"""
Compound Metadata Researcher
Systematically researches and populates comprehensive metadata for hazardous compounds.

Uses Gemini API to query authoritative sources:
- NIOSH Pocket Guide
- NIST Chemistry WebBook  
- OSHA Standards (29 CFR 1910)
- DOT Emergency Response Guide
- EPA Databases (CERCLA, SARA, RCRA)
- PubChem / ChemIDplus
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from shared.api.client_factory import APIClientFactory


class CompoundMetadataResearcher:
    """Research and populate comprehensive compound metadata."""
    
    def __init__(self):
        self.compounds_file = project_root / "data" / "compounds" / "Compounds.yaml"
        self.api_client = APIClientFactory.create_client(provider="grok")
        
    def load_compounds(self) -> Dict[str, Any]:
        """Load current compounds data."""
        with open(self.compounds_file, 'r') as f:
            return yaml.safe_load(f)
    
    def save_compounds(self, data: Dict[str, Any]) -> None:
        """Save updated compounds data."""
        with open(self.compounds_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    def build_research_prompt(self, compound_name: str, chemical_formula: str, 
                            cas_number: str, category: str, tier: int = 1) -> str:
        """Build comprehensive research prompt for specified tier."""
        
        base_context = f"""Research the hazardous compound: {compound_name}
Chemical Formula: {chemical_formula}
CAS Number: {cas_number}
Category: {category}

You are researching authoritative safety and regulatory data. Provide ONLY factual, 
verified information from official sources (NIOSH, OSHA, EPA, DOT, NIST).

"""
        
        if tier == 1:
            # TIER 1: Safety Critical
            prompt = base_context + """
Provide the following TIER 1 SAFETY CRITICAL information in structured format:

1. PPE REQUIREMENTS:
   - Respiratory protection (specific type and level)
   - Skin protection (material and coverage)
   - Eye protection (type)
   - Minimum EPA protection level (A/B/C/D)
   - Special notes or conditions

2. PHYSICAL PROPERTIES:
   - Boiling point (°C)
   - Melting point (°C)
   - Vapor pressure (mmHg @ 20°C)
   - Vapor density (Air=1)
   - Specific gravity
   - Flash point (°C, if applicable)
   - Autoignition temperature (°C, if applicable)
   - Explosive limits (LEL/UEL %, if applicable)
   - Physical appearance
   - Odor and odor threshold (ppm)

3. EMERGENCY RESPONSE:
   - Fire hazard description
   - Fire suppression methods
   - Spill procedures (first 3 critical steps)
   - Immediate exposure actions (first 3 critical steps)
   - Environmental hazards
   - Special decomposition hazards

4. STORAGE REQUIREMENTS:
   - Safe temperature range
   - Ventilation requirements (specific cfm or face velocity)
   - Incompatible materials (list 3-5 most critical)
   - Container material specifications
   - Segregation requirements
   - Quantity limits (indoor/outdoor per OSHA)
   - Special storage requirements

Format response as valid YAML structure matching these field names.
Use null for unavailable data. Be precise with units and values.
"""
        
        elif tier == 2:
            # TIER 2: Regulatory Compliance
            prompt = base_context + """
Provide the following TIER 2 REGULATORY information in structured format:

1. REGULATORY CLASSIFICATION:
   - UN number (4 digits)
   - DOT hazard class
   - DOT labels required
   - NFPA health code (0-4)
   - NFPA flammability code (0-4)
   - NFPA reactivity code (0-4)
   - NFPA special hazards (OXY, ACID, etc.)
   - EPA hazard categories (list all that apply)
   - SARA Title III Section 313 listed (true/false)
   - CERCLA Reportable Quantity (pounds)
   - RCRA hazardous waste code (if applicable)

2. WORKPLACE EXPOSURE VALUES (Enhanced):
   - OSHA PEL TWA (8-hour)
   - OSHA PEL STEL (15-minute)
   - OSHA PEL Ceiling
   - NIOSH REL TWA
   - NIOSH REL STEL
   - NIOSH REL Ceiling
   - NIOSH IDLH (immediately dangerous to life/health)
   - ACGIH TLV TWA
   - ACGIH TLV STEL
   - ACGIH TLV Ceiling
   - Biological Exposure Indices (if established):
     * Metabolite measured
     * Specimen type
     * Sampling timing
     * BEI value

3. SYNONYMS AND IDENTIFIERS:
   - Common synonyms (list 5-10)
   - Trade names (if applicable)
   - RTECS number
   - EC number (European Community)
   - PubChem CID

Format response as valid YAML structure. Use null for unavailable data.
"""
        
        else:  # tier == 3
            # TIER 3: Operational Context
            prompt = base_context + """
Provide the following TIER 3 OPERATIONAL information in structured format:

1. REACTIVITY AND COMPATIBILITY:
   - Chemical stability description
   - Polymerization potential
   - Incompatible materials (comprehensive list)
   - Hazardous decomposition products
   - Conditions to avoid (heat, sparks, etc.)
   - Specific reactivity hazard description

2. ENVIRONMENTAL IMPACT:
   - Aquatic toxicity description
   - Biodegradability status
   - Bioaccumulation potential (log Kow)
   - Soil mobility
   - Atmospheric fate (half-life)
   - Ozone depletion potential (true/false)
   - Global warming potential (if applicable)
   - Reportable releases to water (CWA)
   - Reportable releases to air (lbs/day)

3. DETECTION AND MONITORING:
   - Sensor types suitable (list 2-4)
   - Typical detection range (ppm)
   - Alarm setpoints:
     * Low alarm (TWA-based)
     * High alarm (Ceiling-based)
     * Evacuate alarm (IDLH-based)
   - Colorimetric tube options (manufacturer + model)
   - Analytical methods:
     * Method name/number
     * Technique (GC, HPLC, etc.)
     * Detection limit
   - Odor threshold reliability

Format response as valid YAML structure. Use null for unavailable data.
"""
        
        return prompt
    
    def research_compound_tier(self, compound_data: Dict[str, Any], tier: int) -> Optional[Dict[str, Any]]:
        """Research specific tier of metadata for a compound."""
        compound_name = compound_data['name']
        chemical_formula = compound_data['chemical_formula']
        cas_number = compound_data['cas_number']
        category = compound_data['category']
        
        print(f"\n{'='*70}")
        print(f"🔬 Researching TIER {tier} for: {compound_name}")
        print(f"{'='*70}")
        
        prompt = self.build_research_prompt(
            compound_name, chemical_formula, cas_number, category, tier
        )
        
        try:
            from shared.api.client import GenerationRequest
            
            request = GenerationRequest(
                prompt=prompt,
                temperature=0.3,  # Low temperature for factual research
                max_tokens=4096
            )
            api_response = self.api_client.generate(request)
            
            # Extract YAML from response (may be wrapped in code blocks)
            yaml_text = api_response.content.strip()
            if yaml_text.startswith('```yaml'):
                yaml_text = yaml_text.split('```yaml')[1].split('```')[0].strip()
            elif yaml_text.startswith('```'):
                yaml_text = yaml_text.split('```')[1].split('```')[0].strip()
            
            # Parse YAML response
            tier_data = yaml.safe_load(yaml_text)
            
            print(f"✅ TIER {tier} research completed")
            print(f"   Fields retrieved: {len(tier_data)}")
            
            return tier_data
            
        except Exception as e:
            print(f"❌ Error researching TIER {tier}: {e}")
            return None
    
    def research_all_compounds(self, start_tier: int = 1, end_tier: int = 3) -> None:
        """Research all compounds for specified tiers."""
        data = self.load_compounds()
        compounds = data['compounds']
        
        total = len(compounds)
        print(f"\n{'='*70}")
        print(f"🚀 COMPOUND METADATA RESEARCH")
        print(f"{'='*70}")
        print(f"Total compounds: {total}")
        print(f"Tiers to research: {start_tier}-{end_tier}")
        print(f"{'='*70}\n")
        
        for idx, (compound_id, compound_data) in enumerate(compounds.items(), 1):
            compound_name = compound_data['name']
            print(f"\n[{idx}/{total}] Processing: {compound_name} ({compound_id})")
            
            # Research each tier
            for tier in range(start_tier, end_tier + 1):
                tier_data = self.research_compound_tier(compound_data, tier)
                
                if tier_data:
                    # Merge tier data into compound
                    compound_data.update(tier_data)
                    
                    # Save after each tier to avoid data loss
                    data['compounds'][compound_id] = compound_data
                    self.save_compounds(data)
                    print(f"   💾 TIER {tier} data saved")
                else:
                    print(f"   ⚠️  TIER {tier} data unavailable, continuing...")
            
            print(f"✅ {compound_name} complete")
        
        print(f"\n{'='*70}")
        print(f"✅ ALL RESEARCH COMPLETE")
        print(f"{'='*70}\n")
    
    def research_single_compound(self, compound_id: str, tier: int = 1) -> None:
        """Research a single compound for testing."""
        data = self.load_compounds()
        
        if compound_id not in data['compounds']:
            print(f"❌ Compound '{compound_id}' not found")
            return
        
        compound_data = data['compounds'][compound_id]
        tier_data = self.research_compound_tier(compound_data, tier)
        
        if tier_data:
            print(f"\n{'='*70}")
            print(f"📊 TIER {tier} RESEARCH RESULTS")
            print(f"{'='*70}")
            print(yaml.dump(tier_data, default_flow_style=False, allow_unicode=True))
            
            # Ask to save
            response = input(f"\n💾 Save TIER {tier} data to {compound_id}? (y/n): ")
            if response.lower() == 'y':
                compound_data.update(tier_data)
                data['compounds'][compound_id] = compound_data
                self.save_compounds(data)
                print("✅ Data saved")


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Research compound metadata")
    parser.add_argument('--compound', type=str, help='Research single compound by ID')
    parser.add_argument('--tier', type=int, choices=[1,2,3], default=1,
                       help='Tier to research (1=Safety, 2=Regulatory, 3=Operational)')
    parser.add_argument('--all', action='store_true', 
                       help='Research all compounds')
    parser.add_argument('--start-tier', type=int, choices=[1,2,3], default=1,
                       help='Starting tier for --all')
    parser.add_argument('--end-tier', type=int, choices=[1,2,3], default=3,
                       help='Ending tier for --all')
    
    args = parser.parse_args()
    
    researcher = CompoundMetadataResearcher()
    
    if args.compound:
        researcher.research_single_compound(args.compound, args.tier)
    elif args.all:
        researcher.research_all_compounds(args.start_tier, args.end_tier)
    else:
        print("Usage:")
        print("  Test single compound:")
        print("    python3 metadata_researcher.py --compound formaldehyde --tier 1")
        print()
        print("  Research all compounds:")
        print("    python3 metadata_researcher.py --all")
        print("    python3 metadata_researcher.py --all --start-tier 1 --end-tier 1")


if __name__ == '__main__':
    main()
