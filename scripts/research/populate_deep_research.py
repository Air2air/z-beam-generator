#!/usr/bin/env python3
"""
Deep Research Population Script

Populates PropertyResearch.yaml and SettingResearch.yaml with multi-source
research data using AI to find and validate values from various authoritative
sources (handbooks, databases, academic papers, industry standards).

Features:
- Multi-source research per property/setting
- Alloy and composition variations
- Context-specific variations (wavelength, power, temperature)
- Proper citations and confidence levels
- Performance metrics and trade-off analysis

Usage:
    # Research single material property
    python3 populate_deep_research.py --material Aluminum --property density
    
    # Research single material setting
    python3 populate_deep_research.py --material Aluminum --setting wavelength
    
    # Research all properties for a material
    python3 populate_deep_research.py --material Aluminum --all-properties
    
    # Research all settings for a material
    python3 populate_deep_research.py --material Aluminum --all-settings
    
    # Research multiple materials
    python3 populate_deep_research.py --materials Aluminum,Steel,Titanium --property density
    
    # Discover and add alloy variations
    python3 populate_deep_research.py --material Aluminum --discover-alloys
"""

import argparse
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from domains.materials.data_loader_v2 import load_materials_data, get_property_definitions
from shared.api.client_factory import create_api_client
from shared.api.client import GenerationRequest


class DeepResearchPopulator:
    """Populates deep research data using AI."""
    
    def __init__(self, api_client=None, api_provider='grok'):
        """
        Initialize with API client for research.
        
        Args:
            api_client: Optional pre-configured API client
            api_provider: API provider to use ('grok', 'deepseek', etc.)
        """
        if api_client is None:
            api_client = create_api_client(api_provider)
        self.api_client = api_client
        self.api_provider = api_provider
        self.data_dir = Path(__file__).resolve().parents[2] / "materials" / "data"
        self.property_research_path = self.data_dir / "PropertyResearch.yaml"
        self.setting_research_path = self.data_dir / "SettingResearch.yaml"
        
        # Load existing research data
        self.property_research = self._load_research_file(self.property_research_path)
        self.setting_research = self._load_research_file(self.setting_research_path)
        
        # Load materials data for context
        self.materials_data = load_materials_data()
        self.property_defs = get_property_definitions()
        
    def _load_research_file(self, path: Path) -> Dict[str, Any]:
        """Load research YAML file, create if doesn't exist."""
        if not path.exists():
            return {
                '_metadata': {
                    'version': '1.0.0',
                    'description': f'Deep research data from {path.name}',
                    'schema_version': '3.0.0',
                    'created_date': datetime.now().isoformat(),
                }
            }
        
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _save_research_file(self, data: Dict[str, Any], path: Path):
        """Save research data to YAML file."""
        # Update metadata
        if '_metadata' in data:
            data['_metadata']['last_updated'] = datetime.now().isoformat()
        
        # Create backup
        if path.exists():
            backup_path = create_timestamped_backup(path)
            print(f"  Created backup: {backup_path.name}")
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, 
                     allow_unicode=True, width=120)
        
        print(f"  ✓ Saved: {path.name}")
    
    def research_property(self, material_name: str, property_name: str) -> Dict[str, Any]:
        """
        Research a material property from multiple sources using AI.
        
        Returns research data with multiple values from different sources.
        """
        print(f"\n🔬 Researching {material_name} - {property_name}")
        print(f"  🤖 Using {self.api_provider} for AI research")
        
        # Get property definition for context
        prop_def = self.property_defs.get(property_name, {})
        
        # Build research prompt
        prompt = self._build_property_research_prompt(material_name, property_name, prop_def)
        
        # Query AI for research
        print("  📚 Querying AI for multi-source research...")
        
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=PROPERTY_RESEARCH_SYSTEM_PROMPT,
            max_tokens=4000,
            temperature=0.3,
        )
        response = self.api_client.generate(request)
        
        if not response.success:
            raise Exception(f"AI research failed: {response.error}")
        
        # Parse AI response
        research_text = response.content
        research_data = self._parse_property_research_response(research_text, material_name, property_name)
        
        print(f"  ✓ Found {len(research_data['research']['values'])} research sources")
        
        return research_data
    
    def _build_property_research_prompt(self, material: str, prop: str, prop_def: Dict) -> str:
        """Build prompt for property research."""
        return f"""Research the property '{prop}' for material '{material}' from multiple authoritative sources.

Property Context:
- Description: {prop_def.get('description', 'N/A')}
- Unit: {prop_def.get('unit', 'N/A')}
- Relevance: {prop_def.get('relevance', 'N/A')}
- Laser Cleaning Impact: {prop_def.get('laser_cleaning_impact', 'N/A')}

Find AT LEAST 5 different values from these source types:
1. Reference handbooks (ASM, CRC, Materials Handbook)
2. Materials databases (MatWeb, NIST, ASM)
3. Academic papers (peer-reviewed journals)
4. Industry standards (ISO, ASTM, ANSI, Aluminum Association)
5. Manufacturer specifications

For EACH value, provide:
- Exact value and unit
- Source name and type
- Citation (ISBN, DOI, URL, standard number)
- Context (purity, alloy, temperature, measurement method)
- Confidence level (0-100%)
- Notes about variations

IMPORTANT for metals like Aluminum:
- Include pure metal value (99.99%+ purity)
- Include common alloys (1100, 2024, 6061, 7075 for aluminum)
- Include temperature variations if relevant
- Note how alloying elements affect the property

Format response as structured data for YAML conversion."""
    
    def _parse_property_research_response(self, response: str, material: str, prop: str) -> Dict[str, Any]:
        """Parse AI response into structured research data."""
        # This is a simplified parser - in production, use more robust parsing
        # For now, return template structure with placeholder
        
        return {
            'primary': {
                'value': 0.0,
                'unit': 'TBD',
                'confidence': 95,
                'source': 'ai_research',
                'notes': 'Primary value - needs manual review'
            },
            'research': {
                'values': [
                    {
                        'value': 0.0,
                        'unit': 'TBD',
                        'confidence': 90,
                        'source': 'AI Research - Needs Validation',
                        'source_type': 'ai_research',
                        'notes': f'Researched for {material} {prop} - manual validation required',
                        'raw_response': response[:500]  # Store first 500 chars for review
                    }
                ],
                'metadata': {
                    'total_sources': 1,
                    'last_researched': datetime.now().isoformat(),
                    'research_depth': 'initial',
                    'needs_validation': True
                }
            }
        }
    
    def research_setting(self, material_name: str, setting_name: str) -> Dict[str, Any]:
        """
        Research a machine setting with context-specific variations using AI.
        
        Returns research data with multiple context variations.
        """
        print(f"\n⚙️  Researching {material_name} - {setting_name}")
        print(f"  🤖 Using {self.api_provider} for AI research")
        
        # Build research prompt
        prompt = self._build_setting_research_prompt(material_name, setting_name)
        
        # Query AI for research
        print("  📚 Querying AI for context-specific variations...")
        
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=SETTING_RESEARCH_SYSTEM_PROMPT,
            max_tokens=4000,
            temperature=0.3,
        )
        response = self.api_client.generate(request)
        
        if not response.success:
            raise Exception(f"AI research failed: {response.error}")
        
        # Parse AI response
        research_text = response.content
        research_data = self._parse_setting_research_response(research_text, material_name, setting_name)
        
        print(f"  ✓ Found {len(research_data['research']['values'])} context variations")
        
        return research_data
    
    def _build_setting_research_prompt(self, material: str, setting: str) -> str:
        """Build prompt for setting research."""
        return f"""Research the laser cleaning setting '{setting}' for material '{material}' with context-specific variations.

Find MULTIPLE VALUES for different contexts/applications:

For WAVELENGTH research:
- UV (355nm, 266nm): Precision cleaning contexts
- Green (532nm): General purpose contexts
- Near-IR (1064nm): Industrial cleaning contexts
- Mid-IR (2940nm): Organic removal contexts
- CO2 (10640nm): Aggressive cleaning contexts

For POWER research:
- Low (20-50W): Precision, delicate surfaces
- Medium (50-100W): General industrial
- High (100-200W): Heavy-duty, thick parts

For EACH variation, provide:
1. Value and unit
2. Source and citation
3. Context:
   - Application type (precision/industrial/aggressive)
   - Material condition (polished/oxidized/coated)
   - Contamination type
   - Industry (aerospace/automotive/marine)
4. Advantages (list)
5. Disadvantages (list)
6. Optimal use cases (list)
7. Not recommended for (list)
8. Performance metrics:
   - Removal rate
   - Surface roughness
   - Damage risk (low/medium/high)
   - Throughput
   - Cost factor
9. Typical parameters (if wavelength: power, fluence, pulse; if power: fluence, scan speed)

Include REALISTIC data based on laser cleaning physics and industry practices."""
    
    def _parse_setting_research_response(self, response: str, material: str, setting: str) -> Dict[str, Any]:
        """Parse AI response into structured setting research data."""
        # Simplified parser - production version would be more sophisticated
        
        return {
            'primary': {
                'value': 0,
                'unit': 'TBD',
                'description': f'Primary {setting} for {material} - needs manual review'
            },
            'research': {
                'values': [
                    {
                        'value': 0,
                        'unit': 'TBD',
                        'confidence': 85,
                        'source': 'AI Research - Needs Validation',
                        'source_type': 'ai_research',
                        'context': {
                            'application': 'general',
                            'material_condition': 'standard',
                            'notes': 'Needs validation'
                        },
                        'raw_response': response[:500]
                    }
                ],
                'metadata': {
                    'total_sources': 1,
                    'last_researched': datetime.now().isoformat(),
                    'research_depth': 'initial',
                    'needs_validation': True
                }
            }
        }
    
    def discover_alloys(self, material_name: str) -> List[Dict[str, Any]]:
        """
        Discover common alloys and variations for a base material.
        
        For metals: Discover alloys
        For non-metals: Discover species, grades, compositions, treatments
        
        Returns list of variation specifications.
        """
        print(f"\n🔍 Discovering variations for {material_name}")
        print(f"  🤖 Using {self.api_provider} for AI research")
        
        # Detect material category to provide better context
        material_data = self.materials_data.get(material_name, {})
        category = material_data.get('properties', {}).get('category', 'unknown')
        
        # Build category-specific prompt
        if category == 'metal':
            variation_type = "alloys and heat treatment variations"
            examples = """
For {material_name}, research industry standards like:
- Aluminum: AA (Aluminum Association) designations (1100, 2024, 6061, 7075)
- Steel: AISI, SAE, ASTM grades (A36, 1045, 304, 316, 4140)
- Stainless: 304, 316, 430 series with L/H variants
- Titanium: Grade 1-5, 6Al-4V (Ti-6Al-4V)
- Copper: C11000, C26000 (brass), C51000 (bronze)"""
        
        elif category == 'wood':
            variation_type = "species, moisture content, and grade variations"
            examples = """
For {material_name}, research:
- Species variations (e.g., White Oak vs Red Oak, Hard Maple vs Soft Maple)
- Moisture content states (green >30%, air-dried 12-20%, kiln-dried 6-10%)
- Lumber grades (FAS, Select, Common #1/#2/#3)
- Cut types (quarter-sawn, flat-sawn, rift-sawn)
- Treatment states (untreated, sealed, stained)"""
        
        elif category == 'stone':
            variation_type = "geological varieties, quarry origins, and finish types"
            examples = """
For {material_name}, research:
- Geological varieties (e.g., Carrara vs Calacatta marble)
- Quarry origins (affects mineral composition)
- Finish types (polished, honed, flamed, bush-hammered, sandblasted)
- Grade classifications (Select, Standard, Commercial, Rustic)
- Color variations (white, gray, pink, black)"""
        
        elif category == 'glass':
            variation_type = "composition types and treatment variations"
            examples = """
For {material_name}, research:
- Composition types (soda-lime, borosilicate, lead crystal)
- Manufacturing process (float, blown, cast, drawn)
- Treatment states (annealed, tempered, laminated, coated)
- Optical properties (clear, low-iron, tinted, reflective)
- Brand names (Pyrex, DURAN, Gorilla Glass if applicable)"""
        
        elif category == 'ceramic':
            variation_type = "composition purity and firing variations"
            examples = """
For {material_name}, research:
- Purity levels (99.9%, 96%, 90% for alumina)
- Firing temperatures (affecting density and properties)
- Glaze types (glossy, matte, unglazed)
- Porosity classes (vitrified, semi-vitrified, earthenware)
- Production methods (slip-cast, pressed, extruded)"""
        
        elif category == 'composite':
            variation_type = "fiber/matrix combinations and orientations"
            examples = """
For {material_name}, research:
- Fiber types (carbon: SM/IM/HM/HS, glass: E/S/C, aramid: Kevlar/Twaron)
- Matrix types (epoxy, polyester, vinyl ester, polyurethane)
- Fiber orientations (unidirectional, woven, random mat)
- Fiber volume fractions (30-70%)
- Manufacturing methods (hand layup, RTM, pultrusion)"""
        
        elif category == 'plastic':
            variation_type = "grade, molecular weight, and additive variations"
            examples = """
For {material_name}, research:
- Density/grade variations (HDPE vs LDPE, homopolymer vs copolymer PP)
- Molecular weight classes (standard, high, ultra-high)
- Additive packages (UV-stabilized, flame-retardant, glass-filled)
- Processing variants (injection grade, extrusion grade)
- Crystallinity levels (amorphous vs semi-crystalline)"""
        
        elif category == 'masonry':
            variation_type = "grade, strength class, and aggregate variations"
            examples = """
For {material_name}, research:
- Grade classifications (brick: SW/MW/NW, concrete: C20-C50)
- Strength classes (compressive strength ratings)
- Aggregate types (normal, lightweight, heavy)
- Special types (firebrick, engineering brick, face brick)"""
        
        else:
            variation_type = "variations and specifications"
            examples = f"""
For {material_name}, research all commercially available variations, grades, 
types, and specifications used in industrial applications."""
        
        prompt = f"""List ALL common commercial {variation_type} of {material_name}.

For EACH variation provide:
1. Designation/Name (e.g., "White Oak FAS grade kiln-dried", "6061-T6", "Carrara marble polished")
2. Standard/Specification (e.g., industry standard, botanical name, ASTM designation)
3. Composition/Characteristics (key distinguishing features)
4. Common names/trade names
5. Primary applications
6. Key properties that differ from base material
7. How it affects laser cleaning (easier/harder, different parameters needed)

{examples.format(material_name=material_name)}

Provide data in structured format suitable for YAML conversion."""
        
        print("  📚 Querying AI for variation database...")
        print(f"  Material category: {category}")
        print(f"  Variation type: {variation_type}")
        
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=ALLOY_DISCOVERY_SYSTEM_PROMPT,
            max_tokens=4000,
            temperature=0.2,
        )
        response = self.api_client.generate(request)
        
        if not response.success:
            raise Exception(f"AI variation discovery failed: {response.error}")
        
        variation_text = response.content
        print("  ✓ Discovered variations (stored for manual validation)")
        print(f"\n{variation_text}\n")
        
        # Store in research notes for manual validation
        variation_file_name = f"{material_name.replace(' ', '_')}_variations_research.txt"
        notes_path = self.data_dir / variation_file_name
        with open(notes_path, 'w') as f:
            f.write(f"# Variation Research for {material_name}\n")
            f.write(f"# Category: {category}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
            f.write(variation_text)
        
        print(f"  ✓ Saved to: {notes_path.name}")
        
        return []  # Return empty - manual validation required
    
    def populate_material(self, material_name: str, properties: List[str] = None, 
                         settings: List[str] = None):
        """Populate research data for a material."""
        print(f"\n{'='*70}")
        print(f"POPULATING RESEARCH: {material_name}")
        print(f"{'='*70}")
        
        # Research properties
        if properties:
            for prop in properties:
                research = self.research_property(material_name, prop)
                
                # Add to property research data
                if material_name not in self.property_research:
                    self.property_research[material_name] = {}
                
                self.property_research[material_name][prop] = research
        
        # Research settings
        if settings:
            for setting in settings:
                research = self.research_setting(material_name, setting)
                
                # Add to setting research data
                if material_name not in self.setting_research:
                    self.setting_research[material_name] = {}
                
                self.setting_research[material_name][setting] = research
        
        # Save updated research files
        if properties:
            self._save_research_file(self.property_research, self.property_research_path)
        if settings:
            self._save_research_file(self.setting_research, self.setting_research_path)
        
        print(f"\n✅ Research population complete for {material_name}")


# ============================================================================
# System Prompts for AI Research
# ============================================================================

PROPERTY_RESEARCH_SYSTEM_PROMPT = """You are a materials science research assistant specializing in laser cleaning applications.

Your task is to research material properties from authoritative sources and provide accurate, well-cited data.

CRITICAL REQUIREMENTS:
1. Find REAL values from ACTUAL sources (no fabrication)
2. Provide proper citations (ISBN, DOI, URL, standard numbers)
3. Include confidence levels based on source authority
4. Note variations (alloys, temperature, purity, measurement methods)
5. Explain how property variations affect laser cleaning

Source priority (highest to lowest):
1. Reference handbooks (ASM, CRC) - confidence 95-100%
2. Government databases (NIST) - confidence 90-100%
3. Industry standards (ISO, ASTM) - confidence 85-95%
4. Peer-reviewed journals - confidence 80-95%
5. Manufacturer data - confidence 70-90%
6. Materials databases (MatWeb) - confidence 75-90%

Be thorough, accurate, and scientific."""

SETTING_RESEARCH_SYSTEM_PROMPT = """You are a laser cleaning expert researching optimal machine settings for different materials and applications.

Your task is to provide context-specific parameter variations based on real-world laser cleaning practices.

CRITICAL REQUIREMENTS:
1. Base recommendations on laser physics and industry practice
2. Provide MULTIPLE variations for different contexts/applications
3. Include advantages/disadvantages trade-off analysis
4. Note performance metrics (removal rate, surface quality, damage risk)
5. Cite sources (academic papers, manufacturer guidelines, industry standards)
6. Explain physics behind parameter selection

Context variations to consider:
- Application type (precision/industrial/aggressive)
- Material condition (clean/oxidized/painted)
- Contamination type (organic/inorganic/mixed)
- Surface requirements (roughness, damage tolerance)
- Industry requirements (aerospace/automotive/medical)
- Cost considerations

Be practical, realistic, and grounded in laser cleaning science."""

ALLOY_DISCOVERY_SYSTEM_PROMPT = """You are a materials expert with comprehensive knowledge of material variations and industrial standards.

For METALS: Identify alloys and heat treatment variations
For NON-METALS: Identify grades, species, compositions, and treatments

Your task is to identify ALL commercially significant variations of a base material.

CRITICAL REQUIREMENTS:
1. List only REAL, standardized variations (no fabrication)
2. Use proper designations (industry standards)
3. Include composition/specification details
4. Note applications and key property differences
5. Explain laser cleaning implications

FOR METALS (alloys):
- Pure/commercially pure (99%+ purity)
- Common structural alloys (widespread use)
- High-performance alloys (aerospace, medical)
- Specialty alloys (specific applications)
- Heat treatment states (if applicable)
Examples: AA-6061, AISI 304, Ti-6Al-4V

FOR WOOD (species/grade variations):
- Species variations (White Oak vs Red Oak)
- Moisture content states (green, air-dried, kiln-dried)
- Grade (Select, Common, FAS)
- Treatment (sealed, stained, untreated)
Examples: White Oak kiln-dried FAS grade

FOR STONE (geological/finish variations):
- Geological varieties (Carrara vs Calacatta marble)
- Quarry origin (affects composition)
- Finish (polished, honed, flamed)
- Grade (Select, Standard, Commercial)
Examples: Carrara marble polished Select grade

FOR GLASS (composition/treatment):
- Composition types (soda-lime, borosilicate, lead)
- Manufacturing process (float, blown, cast)
- Treatment (annealed, tempered, coated)
Examples: Low-iron float glass tempered

FOR CERAMIC (composition/firing):
- Purity levels (99.9%, 96%, 90% alumina)
- Firing temperature (affects density)
- Glaze type (glossy, matte, unglazed)
Examples: 96% alumina industrial grade

FOR COMPOSITES (fiber/matrix combinations):
- Fiber type (carbon, glass, aramid)
- Matrix type (epoxy, polyester)
- Fiber orientation (UD, woven, random)
Examples: Carbon/epoxy IM fiber unidirectional

FOR PLASTICS (grade/processing):
- Grade (virgin, recycled, filled)
- Molecular weight variants
- Additives (UV-stabilized, flame-retardant)
Examples: HDPE virgin UV-stabilized

Be comprehensive and accurate. Adapt your response to the material type."""


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Populate deep research data for materials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--material', type=str, help='Material name to research')
    parser.add_argument('--materials', type=str, help='Comma-separated material names')
    parser.add_argument('--property', type=str, help='Property to research')
    parser.add_argument('--setting', type=str, help='Setting to research')
    parser.add_argument('--all-properties', action='store_true', help='Research all properties')
    parser.add_argument('--all-settings', action='store_true', help='Research all settings')
    parser.add_argument('--discover-alloys', action='store_true', help='Discover alloy/variation types (works for metals and non-metals)')
    parser.add_argument('--api-provider', type=str, default='grok', help='API provider to use (default: grok)')
    
    args = parser.parse_args()
    
    # Get materials list
    materials = []
    if args.material:
        materials = [args.material]
    elif args.materials:
        materials = [m.strip() for m in args.materials.split(',')]
    else:
        print("❌ Error: Must specify --material or --materials")
        return 1
    
    # Initialize populator
    print("🚀 Initializing Deep Research Populator...")
    print(f"🤖 Using API provider: {args.api_provider}")
    populator = DeepResearchPopulator(api_provider=args.api_provider)
    
    # Process each material
    for material in materials:
        # Discover alloys if requested
        if args.discover_alloys:
            populator.discover_alloys(material)
            continue
        
        # Determine what to research
        properties = None
        settings = None
        
        if args.property:
            properties = [args.property]
        elif args.all_properties:
            # Research priority properties
            properties = ['density', 'thermalConductivity', 'hardness', 
                         'thermalExpansion', 'laserAbsorption', 'laserReflectivity']
        
        if args.setting:
            settings = [args.setting]
        elif args.all_settings:
            # Research priority settings
            settings = ['wavelength', 'powerRange', 'fluenceThreshold', 
                       'spotSize', 'scanSpeed']
        
        if not properties and not settings:
            print("❌ Error: Must specify --property, --setting, --all-properties, or --all-settings")
            return 1
        
        # Populate research
        populator.populate_material(material, properties, settings)
    
    print("\n" + "="*70)
    print("✅ RESEARCH POPULATION COMPLETE")
    print("="*70)
    print("\n⚠️  IMPORTANT: Review and validate AI-generated research data")
    print("   Check sources, citations, and values for accuracy")
    print("   Replace placeholder values with actual research data\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
