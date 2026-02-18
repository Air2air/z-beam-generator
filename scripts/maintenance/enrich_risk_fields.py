#!/usr/bin/env python3
"""
Enrich Risk Fields in Safety Data

Purpose: Transform thin risk assessment strings into rich structured objects
Applies to: ALL domain SOURCE data (data/materials, data/contaminants, etc.)

Usage:
    python3 scripts/maintenance/enrich_risk_fields.py --dry-run
    python3 scripts/maintenance/enrich_risk_fields.py --apply
    python3 scripts/maintenance/enrich_risk_fields.py --dry-run --domains contaminants

Changes:
    1. fire_explosion_risk: "moderate" → {severity: "moderate", description: "...", mitigation: "..."}
    2. toxic_gas_risk: "high" → {severity: "high", primary_hazards: [...], description: "...", mitigation: "..."}
    3. visibility_hazard: "moderate" → {severity: "moderate", description: "...", source: "...", mitigation: "..."}
    4. Add rationale field to ppe_requirements
    5. Add rationale field to ventilation_requirements

Note: Run --export-all after applying changes to regenerate frontmatter
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configuration
SOURCE_DATA_BASE = Path(__file__).parent.parent.parent / 'data'
AVAILABLE_DOMAINS = ['materials', 'contaminants', 'compounds', 'settings', 'applications']

# Risk descriptions by severity
FIRE_RISK_DESCRIPTIONS = {
    'critical': 'Immediate ignition risk with pyrophoric materials or explosive vapor generation',
    'high': 'Flammable residues or combustible dust with significant fire/explosion potential',
    'moderate': 'Combustible materials present, risk elevated in confined spaces or high-power settings',
    'low': 'Minimal fire risk with standard precautions and adequate ventilation',
    'none': 'No significant fire or explosion risk identified'
}

FIRE_RISK_MITIGATION = {
    'critical': 'Emergency protocols required. Fire extinguisher within 3m, fire watch mandatory, explosion-proof equipment',
    'high': 'Fire extinguisher within 10m, avoid enclosed spaces, monitor for hot spots, spark-resistant tools',
    'moderate': 'Fire extinguisher accessible, adequate ventilation, monitor substrate temperature',
    'low': 'Standard fire safety precautions, extinguisher available within 15m',
    'none': 'Standard workplace fire safety protocols'
}

VISIBILITY_IMPACT_DESCRIPTIONS = {
    'critical': 'Complete visibility loss, dense smoke generation creating evacuation hazard',
    'high': 'Severe visibility reduction (60-80%), dense particulate or smoke generation',
    'moderate': 'Moderate visibility reduction (40-60%), significant particulate haze',
    'low': 'Light haze (20-40% reduction), minimal impact on sight lines',
    'none': 'No significant visibility impact'
}

VISIBILITY_MITIGATION = {
    'critical': 'Emergency evacuation protocols, multiple exits accessible, evacuation lighting required',
    'high': 'Maintain clear evacuation routes, supplemental lighting, restrict operator movement',
    'moderate': 'Ensure clear sight lines, use source extraction, maintain awareness of surroundings',
    'low': 'Standard visibility precautions, adequate lighting',
    'none': 'No special visibility precautions required'
}


def load_yaml_file(filepath: Path) -> Optional[Dict[str, Any]]:
    """Load YAML file safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath.name}: {e}")
        return None


def save_yaml_file(filepath: Path, data: Dict[str, Any]) -> bool:
    """Save YAML file safely"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"❌ Error saving {filepath.name}: {e}")
        return False


def generate_toxic_gas_description(severity: str, primary_hazards: List[Dict]) -> str:
    """Generate description for toxic gas risk based on hazards"""
    if not primary_hazards:
        base_descriptions = {
            'critical': 'Extremely toxic or lethal gas generation requiring immediate evacuation protocols',
            'high': 'Toxic gas generation requiring respiratory protection and continuous monitoring',
            'moderate': 'Irritant gas generation requiring respiratory protection',
            'low': 'Minimal gas generation, nuisance particulates only',
            'none': 'No significant toxic gas generation'
        }
        return base_descriptions.get(severity, 'Unknown toxic gas risk level')
    
    # Build description from hazards
    compound_names = [h['compound'] for h in primary_hazards[:3]]  # Top 3
    
    if len(compound_names) == 1:
        return f"{compound_names[0]} generation detected - {severity} toxicity risk"
    elif len(compound_names) == 2:
        return f"{compound_names[0]} and {compound_names[1]} generation - multiple toxic compounds"
    else:
        return f"Multiple toxic compounds detected: {', '.join(compound_names)} - requires enhanced protection"


def generate_toxic_gas_mitigation(severity: str, primary_hazards: List[Dict]) -> str:
    """Generate mitigation guidance for toxic gas risk"""
    base_mitigation = {
        'critical': 'SCBA or supplied air required, continuous gas monitoring, emergency evacuation plan',
        'high': 'Full-face respirator with appropriate cartridges, gas detection system, medical monitoring',
        'moderate': 'Half-face or full-face respirator with organic vapor/particulate cartridges, adequate ventilation',
        'low': 'N95 or P100 respirator for particulate control, standard ventilation',
        'none': 'Standard respiratory protection for particulate control'
    }
    
    mitigation = base_mitigation.get(severity, 'Consult industrial hygienist')
    
    # Add specific compound warnings if carcinogenic
    carcinogenic = [h for h in primary_hazards if h.get('hazard_class') == 'carcinogenic']
    if carcinogenic:
        compounds = ', '.join([h['compound'] for h in carcinogenic[:2]])
        mitigation += f". WARNING: {compounds} - known carcinogen(s), minimize exposure"
    
    return mitigation


def enrich_fire_explosion_risk(severity: str, safety_data: Dict) -> Dict:
    """Enrich fire_explosion_risk from string to structured object"""
    return {
        'severity': severity,
        'description': FIRE_RISK_DESCRIPTIONS.get(severity, f'Fire risk level: {severity}'),
        'mitigation': FIRE_RISK_MITIGATION.get(severity, 'Consult fire safety professional')
    }


def enrich_toxic_gas_risk(severity: str, fumes_generated: List[Dict]) -> Dict:
    """Enrich toxic_gas_risk from string to structured object"""
    # Extract high-risk compounds
    primary_hazards = []
    
    for fume in fumes_generated:
        if fume.get('hazard_class') in ['carcinogenic', 'highly_toxic', 'toxic']:
            primary_hazards.append({
                'compound': fume.get('compound', 'Unknown'),
                'concentration_mg_m3': fume.get('concentration_mg_m3', 'N/A'),
                'hazard_class': fume.get('hazard_class', 'unknown')
            })
    
    return {
        'severity': severity,
        'primary_hazards': primary_hazards[:5],  # Top 5 most hazardous
        'description': generate_toxic_gas_description(severity, primary_hazards),
        'mitigation': generate_toxic_gas_mitigation(severity, primary_hazards)
    }


def enrich_visibility_hazard(severity: str, respirable_fraction: float) -> Dict:
    """Enrich visibility_hazard from string to structured object"""
    # Calculate percentage
    percentage = int(respirable_fraction * 100)
    
    return {
        'severity': severity,
        'description': VISIBILITY_IMPACT_DESCRIPTIONS.get(severity, f'Visibility hazard: {severity}'),
        'source': f'Respirable fraction: {respirable_fraction:.2f} ({percentage}% of particles <10μm)',
        'mitigation': VISIBILITY_MITIGATION.get(severity, 'Maintain adequate visibility'),
        'related_field': 'particulate_generation.respirable_fraction'
    }


def generate_ppe_rationale(respiratory: str, eye: str, skin: str, toxic_gas_risk: str, fire_risk: str) -> str:
    """Generate rationale for PPE requirements based on risks"""
    protections = []
    
    # Respiratory
    if 'SCBA' in respiratory or 'Supplied Air' in respiratory:
        protections.append('critical toxic gas exposure')
    elif 'Full-Face' in respiratory:
        protections.append('toxic gas and particulate exposure')
    elif 'P100' in respiratory or 'Respirator' in respiratory:
        protections.append('hazardous particulate exposure')
    
    # Eye
    if 'Combination' in eye:
        protections.append('chemical splash and impact hazards')
    elif 'Face Shield' in eye:
        protections.append('splash and thermal hazards')
    elif 'Goggles' in eye:
        protections.append('particulate and vapor exposure')
    
    # Skin
    if 'Chemical-Resistant' in skin:
        protections.append('chemical contact')
    elif 'Full Body' in skin:
        protections.append('extensive contamination risk')
    elif fire_risk in ['critical', 'high']:
        protections.append('thermal hazards')
    
    if not protections:
        return 'Standard protection against workplace hazards'
    
    return f"Protects against {', '.join(protections)}"


def generate_ventilation_rationale(ach: int, velocity: float, filtration: str, 
                                   fire_risk: str, toxic_gas_risk: str, visibility_hazard: str) -> str:
    """Generate rationale for ventilation requirements"""
    max_risk = max([fire_risk, toxic_gas_risk, visibility_hazard], 
                   key=lambda x: ['none', 'low', 'moderate', 'medium', 'high', 'critical'].index(x) if x in ['none', 'low', 'moderate', 'medium', 'high', 'critical'] else 0)
    
    reasons = []
    
    if toxic_gas_risk in ['critical', 'high']:
        reasons.append('toxic gas generation')
    if fire_risk in ['critical', 'high']:
        reasons.append('fire/explosion risk')
    if visibility_hazard in ['high', 'critical']:
        reasons.append('dense particulate generation')
    
    if not reasons:
        return f'Standard industrial ventilation ({ach} ACH) for particulate control'
    
    risk_level = 'Enhanced' if max_risk in ['high', 'critical'] else 'Adequate'
    return f"{risk_level} ventilation required due to {', '.join(reasons)} - {ach} ACH with {filtration}"


def enrich_safety_data(data: Dict[str, Any]) -> tuple[Dict[str, Any], List[str]]:
    """Enrich all risk fields and add rationale to requirements"""
    changes = []
    
    if 'safety_data' not in data:
        return data, changes
    
    safety_data = data['safety_data']
    
    # Get existing values
    fumes_generated = safety_data.get('fumes_generated', [])
    particulate = safety_data.get('particulate_generation', {})
    respirable_fraction = particulate.get('respirable_fraction', 0.5)
    
    # 1. Enrich fire_explosion_risk
    if 'fire_explosion_risk' in safety_data:
        current = safety_data['fire_explosion_risk']
        if isinstance(current, str):  # Only enrich if still a string
            enriched = enrich_fire_explosion_risk(current, safety_data)
            safety_data['fire_explosion_risk'] = enriched
            changes.append(f"Enriched fire_explosion_risk: {current} → structured object")
    
    # 2. Enrich toxic_gas_risk
    if 'toxic_gas_risk' in safety_data:
        current = safety_data['toxic_gas_risk']
        if isinstance(current, str):  # Only enrich if still a string
            enriched = enrich_toxic_gas_risk(current, fumes_generated)
            safety_data['toxic_gas_risk'] = enriched
            changes.append(f"Enriched toxic_gas_risk: {current} → structured object with {len(enriched['primary_hazards'])} hazards")
    
    # 3. Enrich visibility_hazard
    if 'visibility_hazard' in safety_data:
        current = safety_data['visibility_hazard']
        if isinstance(current, str):  # Only enrich if still a string
            enriched = enrich_visibility_hazard(current, respirable_fraction)
            safety_data['visibility_hazard'] = enriched
            changes.append(f"Enriched visibility_hazard: {current} → structured object")
    
    # 4. Add rationale to ppe_requirements
    if 'ppe_requirements' in safety_data:
        ppe = safety_data['ppe_requirements']
        if 'rationale' not in ppe and isinstance(ppe, dict):
            fire_risk = safety_data.get('fire_explosion_risk', {})
            fire_sev = fire_risk.get('severity', 'low') if isinstance(fire_risk, dict) else fire_risk
            
            toxic_risk = safety_data.get('toxic_gas_risk', {})
            toxic_sev = toxic_risk.get('severity', 'low') if isinstance(toxic_risk, dict) else toxic_risk
            
            rationale = generate_ppe_rationale(
                ppe.get('respiratory', 'N/A'),
                ppe.get('eye_protection', 'N/A'),
                ppe.get('skin_protection', 'N/A'),
                toxic_sev,
                fire_sev
            )
            ppe['rationale'] = rationale
            changes.append("Added rationale to ppe_requirements")
    
    # 5. Add rationale to ventilation_requirements
    if 'ventilation_requirements' in safety_data:
        vent = safety_data['ventilation_requirements']
        if 'rationale' not in vent and isinstance(vent, dict):
            fire_risk = safety_data.get('fire_explosion_risk', {})
            fire_sev = fire_risk.get('severity', 'low') if isinstance(fire_risk, dict) else fire_risk
            
            toxic_risk = safety_data.get('toxic_gas_risk', {})
            toxic_sev = toxic_risk.get('severity', 'low') if isinstance(toxic_risk, dict) else toxic_risk
            
            visibility = safety_data.get('visibility_hazard', {})
            vis_sev = visibility.get('severity', 'low') if isinstance(visibility, dict) else visibility
            
            rationale = generate_ventilation_rationale(
                vent.get('minimum_air_changes_per_hour', 10),
                vent.get('exhaust_velocity_m_s', 0.5),
                vent.get('filtration_type', 'Mechanical'),
                fire_sev,
                toxic_sev,
                vis_sev
            )
            vent['rationale'] = rationale
            changes.append("Added rationale to ventilation_requirements")
    
    return data, changes


def process_domain_files(domain: str, dry_run: bool = True) -> Dict[str, Any]:
    """Process all files in a domain directory"""
    domain_dir = SOURCE_DATA_BASE / domain
    
    if not domain_dir.exists():
        print(f"⚠️  Domain directory not found: {domain_dir}")
        return {
            'total': 0,
            'processed': 0,
            'modified': 0,
            'skipped': 0,
            'errors': 0,
            'changes': []
        }
    
    # Find the main data file (Materials.yaml, Contaminants.yaml, etc.)
    yaml_files = []
    
    # Look for domain-specific files
    if domain == 'materials':
        yaml_files = [domain_dir / 'Materials.yaml']
    elif domain == 'contaminants':
        yaml_files = [domain_dir / 'Contaminants.yaml']
    elif domain == 'compounds':
        yaml_files = [domain_dir / 'Compounds.yaml']
    elif domain == 'settings':
        yaml_files = [domain_dir / 'Settings.yaml']
    
    # Filter to only existing files
    yaml_files = [f for f in yaml_files if f.exists()]
    
    stats = {
        'total': len(yaml_files),
        'processed': 0,
        'modified': 0,
        'skipped': 0,
        'errors': 0,
        'changes': []
    }
    
    print(f"📁 Processing {domain.upper()} domain - {stats['total']} files")
    print("=" * 80)
    print()
    
    for yaml_file in yaml_files:
        try:
            data = load_yaml_file(yaml_file)
            if data is None:
                stats['errors'] += 1
                continue
            
            # Process each entry in the data file
            # Materials.yaml has 'materials', Contaminants.yaml has 'contamination_patterns', etc.
            domain_key_map = {
                'materials': 'materials',
                'contaminants': 'contamination_patterns',
                'compounds': 'compounds',
                'settings': 'settings'
            }
            
            domain_key = domain_key_map.get(domain, domain)
            
            if domain_key not in data:
                print(f"⚠️  No '{domain_key}' key found in {yaml_file.name}")
                stats['skipped'] += 1
                continue
            
            entries = data[domain_key]
            modified_entries = 0
            
            for entry_name, entry_data in entries.items():
                # For contaminants, safety_data is nested under laser_properties
                if domain == 'contaminants':
                    if 'laser_properties' not in entry_data:
                        continue
                    target_data = entry_data['laser_properties']
                else:
                    target_data = entry_data
                
                # Skip if no safety_data
                if 'safety_data' not in target_data:
                    continue
                
                stats['processed'] += 1
                
                # Enrich the entry's safety_data
                enriched_data, changes = enrich_safety_data(target_data)
                
                if not changes:
                    continue
                
                modified_entries += 1
                
                # Record changes
                change_entry = {
                    'file': yaml_file.name,
                    'entry': entry_name,
                    'domain': domain,
                    'changes': changes
                }
                stats['changes'].append(change_entry)
                
                # Show changes
                print(f"✏️  [{domain.upper()}] {entry_name}")
                for change in changes:
                    print(f"   • {change}")
                print()
            
            if modified_entries > 0:
                stats['modified'] += 1
                
                # Apply changes if not dry run
                if not dry_run:
                    save_yaml_file(yaml_file, data)
                    print(f"💾 Saved {yaml_file.name} with {modified_entries} enriched entries")
                    print()
            else:
                stats['skipped'] += 1
        
        except Exception as e:
            print(f"❌ Error processing {yaml_file.name}: {e}")
            import traceback
            traceback.print_exc()
            stats['errors'] += 1
    
    print()
    print(f"{domain.upper()} Summary: {stats['modified']}/{stats['total']} files enriched")
    print()
    
    return stats


def process_all_domains(domains: List[str], dry_run: bool = True) -> Dict[str, Any]:
    """Process multiple domains"""
    print(f"🔍 Processing domains: {', '.join(domains)}")
    print()
    
    all_stats = {
        'domains': {},
        'total_files': 0,
        'total_processed': 0,
        'total_modified': 0,
        'total_skipped': 0,
        'total_errors': 0,
        'all_changes': []
    }
    
    for domain in domains:
        print("=" * 80)
        stats = process_domain_files(domain, dry_run)
        all_stats['domains'][domain] = stats
        all_stats['total_files'] += stats['total']
        all_stats['total_processed'] += stats['processed']
        all_stats['total_modified'] += stats['modified']
        all_stats['total_skipped'] += stats['skipped']
        all_stats['total_errors'] += stats['errors']
        all_stats['all_changes'].extend(stats['changes'])
    
    return all_stats


def main():
    parser = argparse.ArgumentParser(description='Enrich risk fields in safety data across all domain frontmatter')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    parser.add_argument('--apply', action='store_true', help='Apply changes to files')
    parser.add_argument('--domains', nargs='+', choices=AVAILABLE_DOMAINS, 
                        help=f'Specific domains to process (default: all). Options: {", ".join(AVAILABLE_DOMAINS)}')
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply:
        print("Please specify --dry-run or --apply")
        return 1
    
    # Default to all domains if not specified
    domains = args.domains if args.domains else AVAILABLE_DOMAINS
    
    mode = "DRY RUN" if args.dry_run else "APPLY CHANGES"
    print("=" * 80)
    print(f"SAFETY DATA ENRICHMENT - {mode}")
    print(f"Domains: {', '.join(domains)}")
    print("=" * 80)
    print()
    
    stats = process_all_domains(domains, dry_run=args.dry_run)
    
    # Print summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    for domain, domain_stats in stats['domains'].items():
        status = "✅" if domain_stats['modified'] > 0 else "⚪"
        print(f"{status} {domain.upper()}:")
        print(f"   Total: {domain_stats['total']}, Enriched: {domain_stats['modified']}, " +
              f"Skipped: {domain_stats['skipped']}, Errors: {domain_stats['errors']}")
    
    print(f"\n📊 TOTALS:")
    print(f"   Files: {stats['total_files']}")
    print(f"   Processed: {stats['total_processed']}")
    print(f"   Enriched: {stats['total_modified']}")
    print(f"   Skipped: {stats['total_skipped']}")
    print(f"   Errors: {stats['total_errors']}")
    print()
    
    if args.dry_run:
        print("✨ Dry run complete. Use --apply to make changes.")
    else:
        print(f"✅ Enrichment complete. {stats['total_modified']} files updated across {len(domains)} domains.")
    
    return 0


if __name__ == '__main__':
    exit(main())
