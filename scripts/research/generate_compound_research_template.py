#!/usr/bin/env python3
"""
Compound Metadata Research Collector
Systematically researches and populates 10 metadata field categories for all 19 compounds
"""

import yaml
import json
from pathlib import Path

# Load current compounds data
with open('data/compounds/Compounds.yaml', 'r') as f:
    data = yaml.safe_load(f)

compounds = data['compounds']

# Research template for each compound
def generate_research_queries():
    """Generate structured research queries for all compounds"""
    
    queries = []
    
    for comp_id, comp_data in compounds.items():
        query = {
            'compound_id': comp_id,
            'name': comp_data['name'],
            'cas_number': comp_data['cas_number'],
            'formula': comp_data['chemical_formula'],
            'category': comp_data['category'],
            'research_fields': {
                'tier1_ppe_requirements': {
                    'respiratory': None,
                    'skin': None,
                    'eye': None,
                    'minimum_level': None,
                    'special_notes': None
                },
                'tier1_physical_properties': {
                    'boiling_point': None,
                    'melting_point': None,
                    'vapor_pressure': None,
                    'vapor_density': None,
                    'specific_gravity': None,
                    'flash_point': None,
                    'autoignition_temp': None,
                    'explosive_limits': None,
                    'appearance': None,
                    'odor': None
                },
                'tier1_emergency_response': {
                    'fire_hazard': None,
                    'fire_suppression': None,
                    'spill_procedures': None,
                    'exposure_immediate_actions': None,
                    'environmental_hazards': None,
                    'special_hazards': None
                },
                'tier1_storage_requirements': {
                    'temperature_range': None,
                    'ventilation': None,
                    'incompatibilities': [],
                    'container_material': None,
                    'segregation': None,
                    'quantity_limits': None,
                    'special_requirements': None
                },
                'tier2_regulatory_classification': {
                    'un_number': None,
                    'dot_hazard_class': None,
                    'dot_label': None,
                    'nfpa_codes': {
                        'health': None,
                        'flammability': None,
                        'reactivity': None,
                        'special': None
                    },
                    'epa_hazard_categories': [],
                    'sara_title_iii': None,
                    'cercla_rq': None,
                    'rcra_code': None
                },
                'tier2_workplace_exposure': {
                    'osha_pel': {
                        'twa_8hr': None,
                        'stel_15min': None,
                        'ceiling': None
                    },
                    'niosh_rel': {
                        'twa_8hr': None,
                        'stel_15min': None,
                        'ceiling': None,
                        'idlh': None
                    },
                    'acgih_tlv': {
                        'twa_8hr': None,
                        'stel_15min': None,
                        'ceiling': None
                    },
                    'biological_exposure_indices': []
                },
                'tier2_synonyms_identifiers': {
                    'synonyms': [],
                    'common_trade_names': [],
                    'other_identifiers': {
                        'rtecs_number': None,
                        'ec_number': None,
                        'pubchem_cid': None
                    }
                },
                'tier3_reactivity': {
                    'stability': None,
                    'polymerization': None,
                    'incompatible_materials': [],
                    'hazardous_decomposition': [],
                    'conditions_to_avoid': [],
                    'reactivity_hazard': None
                },
                'tier3_environmental_impact': {
                    'aquatic_toxicity': None,
                    'biodegradability': None,
                    'bioaccumulation': None,
                    'soil_mobility': None,
                    'atmospheric_fate': None,
                    'ozone_depletion': False,
                    'global_warming_potential': None,
                    'reportable_releases': {
                        'water': None,
                        'air': None
                    }
                },
                'tier3_detection_monitoring': {
                    'sensor_types': [],
                    'detection_range': None,
                    'alarm_setpoints': {
                        'low': None,
                        'high': None,
                        'evacuate': None
                    },
                    'colorimetric_tubes': [],
                    'analytical_methods': [],
                    'odor_threshold': None
                }
            }
        }
        
        queries.append(query)
    
    return queries

# Generate and save research template
queries = generate_research_queries()

print("=" * 70)
print(f"📋 GENERATED RESEARCH TEMPLATE FOR {len(queries)} COMPOUNDS")
print("=" * 70)
print()

# Save to JSON for easier AI processing
output_file = 'compound_metadata_research_template.json'
with open(output_file, 'w') as f:
    json.dump(queries, f, indent=2)

print(f"✅ Saved research template to: {output_file}")
print()
print("=" * 70)
print("🎯 NEXT STEPS:")
print("=" * 70)
print()
print("1. Use AI (Gemini/GPT-4) to query authoritative sources:")
print("   - NIOSH Pocket Guide to Chemical Hazards")
print("   - NIST Chemistry WebBook")
print("   - PubChem Database")
print("   - DOT Emergency Response Guidebook")
print("   - OSHA Standards (29 CFR 1910)")
print("   - EPA Databases (40 CFR)")
print("   - NFPA 704 Standards")
print()
print("2. Populate the JSON template with researched data")
print()
print("3. Convert populated JSON back to YAML format")
print()
print("4. Merge into Compounds.yaml")
print()
print("=" * 70)
print("📊 RESEARCH SCOPE:")
print("=" * 70)
print(f"  • Total compounds: {len(queries)}")
print(f"  • Fields per compound: 10 major categories")
print(f"  • Sub-fields per compound: ~60 individual data points")
print(f"  • Total data points to research: ~{len(queries) * 60}")
print()
print("Estimated research time with AI assistance: 2-3 hours")
print("=" * 70)
