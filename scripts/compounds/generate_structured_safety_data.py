#!/usr/bin/env python3
"""
Generate Structured Safety Data for Compounds with Author Voice

This script uses the coordinator's existing infrastructure to generate content.
Uses run.py approach but for structured safety fields.

SIMPLIFIED APPROACH:
- Use existing run.py infrastructure (--compound <name> --generate)
- This script is a wrapper to call multiple component types
- All author voice, quality gates, learning handled by existing system

Usage:
    # For now, use run.py directly:
    python3 run.py --compound carbon-monoxide-compound --generate ppe_requirements
    python3 run.py --compound carbon-monoxide-compound --generate storage_requirements
    
    # This script will automate the above for all compounds
"""

import sys
import subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import argparse
from shared.utils.yaml_utils import load_yaml

print("""
================================================================================
⚠️  NOTE: Structured Safety Data Generation
================================================================================

The proper way to generate safety data with author voice is through run.py:

    python3 run.py --compound <name> --generate <component>

Available components:
  - ppe_requirements
  - storage_requirements  
  - workplace_exposure
  - reactivity
  - environmental_impact

This ensures:
  ✅ Author voice processing (QualityEvaluatedGenerator)
  ✅ Quality gates (Winston, Realism)
  ✅ Voice pattern compliance
  ✅ Learning system integration

================================================================================

For manual structured conversion of existing string data, you'll need a
different approach. The current compounds already have prose safety data -
they need to be reformatted from prose to structured YAML fields.

Recommended approach:
1. Keep existing prose in Compounds.yaml
2. Export generates structured frontmatter from prose during export
3. Use enrichers to format prose → structured during export phase

See: export/enrichers/ for examples of data transformation

================================================================================
""")

def load_compound_data(compound_name: str) -> dict:
    """Load compound data from Compounds.yaml"""
    compounds_path = Path('data/compounds/Compounds.yaml')
    compounds_data = load_yaml(compounds_path)
    compounds = compounds_data.get('compounds', {})
    
    if compound_name not in compounds:
        raise ValueError(f"Compound '{compound_name}' not found in Compounds.yaml")
    
    return compounds[compound_name]


def check_author_enrichment(compound_data: dict, compound_name: str) -> bool:
    """Check if compound has full author metadata"""
    author = compound_data.get('author', {})
    
    if not isinstance(author, dict):
        print(f"⚠️  {compound_name}: No author field")
        return False
    
    if 'name' not in author or 'country' not in author:
        print(f"⚠️  {compound_name}: Author ID {author.get('id', 'Unknown')} needs enrichment")
        print(f"   Run: python3 scripts/data/enrich_author_metadata.py --domain compounds --execute")
        return False
    
    return True


def generate_ppe_requirements(compound_name: str, compound_data: dict, generator: QualityEvaluatedGenerator) -> dict:
    """
    Generate structured PPE requirements using author voice processing.
    
    Architecture: Uses universal text generation pipeline
    - Loads author persona (voice patterns, linguistic markers)
    - Generates content with quality gates (Winston, Realism)
    - Applies humanness optimizer for natural variation
    - Returns structured data ready for YAML storage
    """
    
    # Extract existing prose if available
    existing_text = compound_data.get('ppe_requirements', '')
    
    # Build prompt for structured PPE generation
    prompt = f"""Generate structured PPE requirements for {compound_name}.

Input context (existing prose):
{existing_text}

Output structure (YAML):
respiratory: [Specific respirator type and rating]
eye_protection: [Type of eye protection]
skin_protection: [Gloves, coveralls, specific materials]
minimum_level: [PPE level if applicable - e.g., Level B]
special_notes: [Critical safety considerations]
rationale: [Why this PPE is needed]

Requirements:
- Be specific about equipment (e.g., "NIOSH-approved full-face SCBA" not "respirator")
- Include minimum ratings/certifications where applicable
- Express in your authentic voice (use natural phrasing, avoid formulaic language)
- brief rationale, expressed naturally

Generate ONLY the YAML structure above with specific values."""

    # Generate using pipeline (includes author voice, quality gates)
    result = generator.generate(
        item_name=compound_name,
        component_type='ppe_safety_structured',
        custom_prompt=prompt,
        author_id=compound_data.get('author', {}).get('id')
    )
    
    if not result.success:
        raise Exception(f"Generation failed: {result.error}")
    
    # Parse YAML response
    try:
        structured_data = yaml.safe_load(result.content)
        return {
            'presentation': 'descriptive',
            'items': [structured_data]
        }
    except yaml.YAMLError as e:
        print(f"⚠️  Failed to parse YAML response: {e}")
        print(f"   Raw response: {result.content[:200]}...")
        return None


def generate_storage_requirements(compound_name: str, compound_data: dict, generator: QualityEvaluatedGenerator) -> dict:
    """Generate structured storage requirements with author voice"""
    
    # Build prompt (similar structure to PPE)
    prompt = f"""Generate structured storage requirements for {compound_name}.

Output structure (YAML):
container_type: [Specific container/cylinder type]
temperature_range: [Acceptable temperature range]
humidity_control: [Humidity requirements if any]
segregation: [What to keep away from]
special_handling: [Any special storage notes]

Requirements:
- Be specific about containers, materials, conditions
- Express in your authentic voice (natural phrasing)
- concise text per field

Generate ONLY the YAML structure above."""

    result = generator.generate(
        item_name=compound_name,
        component_type='storage_safety_structured',
        custom_prompt=prompt,
        author_id=compound_data.get('author', {}).get('id')
    )
    
    if not result.success:
        raise Exception(f"Generation failed: {result.error}")
    
    try:
        structured_data = yaml.safe_load(result.content)
        return {
            'presentation': 'descriptive',
            'items': [structured_data]
        }
    except yaml.YAMLError as e:
        print(f"⚠️  Failed to parse YAML response: {e}")
        return None


def generate_workplace_exposure(compound_name: str, compound_data: dict, generator: QualityEvaluatedGenerator) -> dict:
    """Generate structured workplace exposure limits with author voice"""
    
    existing_text = compound_data.get('exposure_guidelines', '')
    
    prompt = f"""Generate structured workplace exposure limits for {compound_name}.

Input context:
{existing_text}

Output structure (YAML):
osha_pel_ppm: [Value or null]
osha_pel_mg_m3: [Value or null]
niosh_rel_ppm: [Value or null]
niosh_rel_mg_m3: [Value or null]
acgih_tlv_ppm: [Value or null]
acgih_tlv_mg_m3: [Value or null]
monitoring_required: [true/false]
monitoring_frequency: [Description if monitoring required]

Requirements:
- Extract numeric limits from existing text
- Use null if not specified
- Express monitoring requirements naturally
- Be precise with units (ppm vs mg/m³)

Generate ONLY the YAML structure above."""

    result = generator.generate(
        item_name=compound_name,
        component_type='exposure_safety_structured',
        custom_prompt=prompt,
        author_id=compound_data.get('author', {}).get('id')
    )
    
    if not result.success:
        raise Exception(f"Generation failed: {result.error}")
    
    try:
        structured_data = yaml.safe_load(result.content)
        return {
            'presentation': 'descriptive',
            'items': [structured_data]
        }
    except yaml.YAMLError as e:
        print(f"⚠️  Failed to parse YAML response: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Generate structured safety data for compounds with author voice'
    )
    parser.add_argument('--compound', type=str, help='Specific compound to process')
    parser.add_argument('--all', action='store_true', help='Process all compounds')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    parser.add_argument('--field', type=str, choices=['ppe', 'storage', 'exposure', 'all'],
                       default='all', help='Which safety field to generate')
    
    args = parser.parse_args()
    
    if not args.compound and not args.all:
        parser.error("Must specify either --compound or --all")
    
    # Load compounds
    compounds_path = Path('data/compounds/Compounds.yaml')
    compounds_data = load_yaml(compounds_path)
    compounds = compounds_data.get('compounds', {})
    
    # Determine which compounds to process
    if args.all:
        compound_names = list(compounds.keys())
    else:
        compound_names = [args.compound]
    
    print(f"\n{'='*80}")
    print(f"🔐 STRUCTURED SAFETY DATA GENERATOR")
    print(f"{'='*80}\n")
    print(f"Processing {len(compound_names)} compound(s)")
    print(f"Fields: {args.field}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'EXECUTE'}\n")
    
    # Initialize generator
    coordinator = CompoundCoordinator()
    generator = QualityEvaluatedGenerator(coordinator=coordinator)
    
    # Process compounds
    results = {
        'success': 0,
        'failed': 0,
        'skipped': 0
    }
    
    for compound_name in compound_names:
        print(f"\n{'─'*80}")
        print(f"📦 {compound_name}")
        print(f"{'─'*80}\n")
        
        try:
            compound_data = load_compound_data(compound_name)
            
            # Check author enrichment
            if not check_author_enrichment(compound_data, compound_name):
                print(f"⏭️  Skipping - needs author enrichment first")
                results['skipped'] += 1
                continue
            
            author = compound_data['author']
            print(f"✅ Author: {author['name']} ({author['country']})\n")
            
            # Generate structured data
            generated_fields = {}
            
            if args.field in ['ppe', 'all']:
                print("🔧 Generating PPE requirements...")
                ppe_data = generate_ppe_requirements(compound_name, compound_data, generator)
                if ppe_data:
                    generated_fields['ppe_requirements'] = ppe_data
                    print("   ✅ Generated")
                else:
                    print("   ❌ Failed")
            
            if args.field in ['storage', 'all']:
                print("🔧 Generating storage requirements...")
                storage_data = generate_storage_requirements(compound_name, compound_data, generator)
                if storage_data:
                    generated_fields['storage_requirements'] = storage_data
                    print("   ✅ Generated")
                else:
                    print("   ❌ Failed")
            
            if args.field in ['exposure', 'all']:
                print("🔧 Generating workplace exposure...")
                exposure_data = generate_workplace_exposure(compound_name, compound_data, generator)
                if exposure_data:
                    generated_fields['workplace_exposure'] = exposure_data
                    print("   ✅ Generated")
                else:
                    print("   ❌ Failed")
            
            # Save to Compounds.yaml (if not dry-run)
            if not args.dry_run and generated_fields:
                # Create relationships.safety structure if doesn't exist
                if 'relationships' not in compound_data:
                    compound_data['relationships'] = {}
                if 'safety' not in compound_data['relationships']:
                    compound_data['relationships']['safety'] = {}
                
                # Update safety fields
                compound_data['relationships']['safety'].update(generated_fields)
                
                # Save
                compounds[compound_name] = compound_data
                compounds_data['compounds'] = compounds
                save_yaml(compounds_path, compounds_data)
                print(f"\n💾 Saved to {compounds_path}")
            
            results['success'] += 1
            
        except Exception as e:
            print(f"\n❌ Error processing {compound_name}: {e}")
            results['failed'] += 1
            continue
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}\n")
    print(f"✅ Success: {results['success']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"⏭️  Skipped: {results['skipped']}")
    print()
    
    if args.dry_run:
        print("ℹ️  DRY RUN MODE - No changes saved")
        print("   Remove --dry-run to save changes\n")


if __name__ == '__main__':
    main()
