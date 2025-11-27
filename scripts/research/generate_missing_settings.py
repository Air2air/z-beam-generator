#!/usr/bin/env python3
"""
Generate Machine Settings for Missing Materials

This script generates machine settings, material challenges, and settings descriptions
for the 27 materials that exist in Materials.yaml but not in Settings.yaml.
"""

import yaml
from pathlib import Path


# Template settings based on material category
CATEGORY_SETTINGS_TEMPLATES = {
    'ceramic': {
        'powerRange': {'value': 80, 'unit': 'W', 'description': 'Optimal power for ceramic cleaning without thermal shock'},
        'wavelength': {'value': 1064, 'unit': 'nm', 'description': 'Near-IR wavelength for optimal ceramic absorption'},
        'spotSize': {'value': 30, 'unit': 'μm', 'description': 'Focused beam for precise ceramic cleaning'},
        'repetitionRate': {'value': 40, 'unit': 'kHz', 'description': 'Moderate rate for thermal management in ceramics'},
        'energyDensity': {'value': 3.5, 'unit': 'J/cm²', 'description': 'Fluence below ceramic damage threshold'},
        'pulseWidth': {'value': 10, 'unit': 'ns', 'description': 'Nanosecond pulses for controlled material removal'},
        'scanSpeed': {'value': 300, 'unit': 'mm/s', 'description': 'Careful scanning to avoid thermal stress'},
        'passCount': {'value': 2, 'unit': 'passes', 'description': 'Multiple passes for complete cleaning'},
        'overlapRatio': {'value': 60, 'unit': '%', 'description': 'Higher overlap for uniform ceramic cleaning'}
    },
    'metal': {
        'powerRange': {'value': 100, 'unit': 'W', 'description': 'Standard power for metal oxide removal'},
        'wavelength': {'value': 1064, 'unit': 'nm', 'description': 'Near-IR wavelength for metal processing'},
        'spotSize': {'value': 50, 'unit': 'μm', 'description': 'Beam spot for effective metal cleaning'},
        'repetitionRate': {'value': 50, 'unit': 'kHz', 'description': 'High rate for efficient metal cleaning'},
        'energyDensity': {'value': 5.0, 'unit': 'J/cm²', 'description': 'Fluence for oxide removal without melting'},
        'pulseWidth': {'value': 10, 'unit': 'ns', 'description': 'Standard pulse duration for metals'},
        'scanSpeed': {'value': 500, 'unit': 'mm/s', 'description': 'Fast scanning for large metal surfaces'},
        'passCount': {'value': 3, 'unit': 'passes', 'description': 'Multiple passes for thorough cleaning'},
        'overlapRatio': {'value': 50, 'unit': '%', 'description': 'Standard overlap for uniform coverage'}
    },
    'plastic': {
        'powerRange': {'value': 30, 'unit': 'W', 'description': 'Low power to avoid polymer degradation'},
        'wavelength': {'value': 355, 'unit': 'nm', 'description': 'UV wavelength for better polymer absorption'},
        'spotSize': {'value': 40, 'unit': 'μm', 'description': 'Precise beam for delicate polymer cleaning'},
        'repetitionRate': {'value': 20, 'unit': 'kHz', 'description': 'Lower rate to minimize heat accumulation'},
        'energyDensity': {'value': 1.5, 'unit': 'J/cm²', 'description': 'Low fluence to prevent thermal damage'},
        'pulseWidth': {'value': 5, 'unit': 'ns', 'description': 'Short pulses for minimal heat transfer'},
        'scanSpeed': {'value': 800, 'unit': 'mm/s', 'description': 'Fast scanning to minimize dwell time'},
        'passCount': {'value': 1, 'unit': 'passes', 'description': 'Single pass to avoid heat buildup'},
        'overlapRatio': {'value': 40, 'unit': '%', 'description': 'Moderate overlap for efficient cleaning'}
    },
    'semiconductor': {
        'powerRange': {'value': 50, 'unit': 'W', 'description': 'Moderate power for delicate semiconductor cleaning'},
        'wavelength': {'value': 532, 'unit': 'nm', 'description': 'Green wavelength for semiconductor processing'},
        'spotSize': {'value': 20, 'unit': 'μm', 'description': 'Fine spot for precision semiconductor cleaning'},
        'repetitionRate': {'value': 30, 'unit': 'kHz', 'description': 'Controlled rate for thermal management'},
        'energyDensity': {'value': 2.0, 'unit': 'J/cm²', 'description': 'Low fluence to protect semiconductor structure'},
        'pulseWidth': {'value': 8, 'unit': 'ns', 'description': 'Precise pulse duration for minimal damage'},
        'scanSpeed': {'value': 200, 'unit': 'mm/s', 'description': 'Careful scanning for delicate materials'},
        'passCount': {'value': 2, 'unit': 'passes', 'description': 'Gentle multi-pass cleaning'},
        'overlapRatio': {'value': 70, 'unit': '%', 'description': 'High overlap for uniform cleaning'}
    },
    'stone': {
        'powerRange': {'value': 90, 'unit': 'W', 'description': 'High power for effective stone cleaning'},
        'wavelength': {'value': 1064, 'unit': 'nm', 'description': 'Near-IR wavelength for stone contaminant removal'},
        'spotSize': {'value': 60, 'unit': 'μm', 'description': 'Larger spot for stone surface coverage'},
        'repetitionRate': {'value': 45, 'unit': 'kHz', 'description': 'Moderate rate for stone processing'},
        'energyDensity': {'value': 4.0, 'unit': 'J/cm²', 'description': 'Adequate fluence for contaminant removal'},
        'pulseWidth': {'value': 12, 'unit': 'ns', 'description': 'Standard pulses for stone cleaning'},
        'scanSpeed': {'value': 400, 'unit': 'mm/s', 'description': 'Efficient scanning for large stone surfaces'},
        'passCount': {'value': 2, 'unit': 'passes', 'description': 'Multiple passes for thorough cleaning'},
        'overlapRatio': {'value': 55, 'unit': '%', 'description': 'Good overlap for uniform stone cleaning'}
    },
    'glass': {
        'powerRange': {'value': 60, 'unit': 'W', 'description': 'Moderate power for glass surface cleaning'},
        'wavelength': {'value': 355, 'unit': 'nm', 'description': 'UV wavelength for better glass absorption'},
        'spotSize': {'value': 35, 'unit': 'μm', 'description': 'Fine spot for precision glass cleaning'},
        'repetitionRate': {'value': 35, 'unit': 'kHz', 'description': 'Controlled rate to avoid thermal shock'},
        'energyDensity': {'value': 2.5, 'unit': 'J/cm²', 'description': 'Low fluence to prevent glass cracking'},
        'pulseWidth': {'value': 8, 'unit': 'ns', 'description': 'Short pulses for minimal thermal stress'},
        'scanSpeed': {'value': 350, 'unit': 'mm/s', 'description': 'Careful scanning for glass surfaces'},
        'passCount': {'value': 2, 'unit': 'passes', 'description': 'Gentle multi-pass cleaning'},
        'overlapRatio': {'value': 60, 'unit': '%', 'description': 'Good overlap for uniform glass cleaning'}
    },
    'wood': {
        'powerRange': {'value': 40, 'unit': 'W', 'description': 'Low power to avoid charring wood'},
        'wavelength': {'value': 355, 'unit': 'nm', 'description': 'UV wavelength for organic material cleaning'},
        'spotSize': {'value': 45, 'unit': 'μm', 'description': 'Moderate spot for wood surface cleaning'},
        'repetitionRate': {'value': 25, 'unit': 'kHz', 'description': 'Lower rate to minimize heat damage'},
        'energyDensity': {'value': 1.8, 'unit': 'J/cm²', 'description': 'Low fluence to prevent wood burning'},
        'pulseWidth': {'value': 6, 'unit': 'ns', 'description': 'Short pulses for delicate wood cleaning'},
        'scanSpeed': {'value': 600, 'unit': 'mm/s', 'description': 'Fast scanning to avoid heat buildup'},
        'passCount': {'value': 1, 'unit': 'passes', 'description': 'Single pass to preserve wood fibers'},
        'overlapRatio': {'value': 45, 'unit': '%', 'description': 'Moderate overlap for efficient cleaning'}
    }
}


def generate_material_challenges(material_name, category):
    """Generate material-specific challenges based on category"""
    
    challenges_templates = {
        'ceramic': {
            'thermal_management': [
                {
                    'challenge': 'Thermal shock sensitivity',
                    'severity': 'high',
                    'impact': 'Rapid heating can cause cracking in brittle ceramics',
                    'solutions': [
                        'Use lower power settings with multiple passes',
                        'Allow cooling time between passes',
                        'Pre-heat material if possible for temperature-sensitive ceramics'
                    ]
                }
            ],
            'surface_characteristics': [
                {
                    'challenge': 'Variable absorption based on surface finish',
                    'severity': 'medium',
                    'impact': 'Polished vs rough surfaces absorb laser energy differently',
                    'solutions': [
                        'Test parameters on similar surface finish samples',
                        'Adjust power based on surface reflectivity',
                        'Use consistent scanning patterns'
                    ]
                }
            ],
            'contamination_challenges': [
                {
                    'challenge': 'Contaminant adhesion to porous surfaces',
                    'severity': 'medium',
                    'impact': 'Contaminants may penetrate surface pores',
                    'solutions': [
                        'Use multiple passes with increasing power',
                        'Consider mechanical pre-cleaning for deep contamination',
                        'Monitor for surface texture changes'
                    ]
                }
            ]
        },
        'metal': {
            'thermal_management': [
                {
                    'challenge': 'Heat dissipation and thermal conductivity',
                    'severity': 'medium',
                    'impact': 'Heat spreads rapidly causing heat-affected zones',
                    'solutions': [
                        'Use faster scan speeds to minimize dwell time',
                        'Apply cooling between passes for thick sections',
                        'Monitor for discoloration indicating thermal damage'
                    ]
                }
            ],
            'surface_characteristics': [
                {
                    'challenge': 'Surface reflectivity',
                    'severity': 'high',
                    'impact': 'High reflectivity reduces absorption efficiency',
                    'solutions': [
                        'Use appropriate wavelength for material',
                        'Increase power density carefully',
                        'Ensure proper beam containment for safety'
                    ]
                }
            ],
            'contamination_challenges': [
                {
                    'challenge': 'Oxide and corrosion removal',
                    'severity': 'medium',
                    'impact': 'Requires careful power control to avoid substrate damage',
                    'solutions': [
                        'Start with higher power for bulk oxide removal',
                        'Reduce power for final cleaning pass',
                        'Monitor base metal exposure'
                    ]
                }
            ]
        },
        'plastic': {
            'thermal_management': [
                {
                    'challenge': 'Low melting point and thermal degradation',
                    'severity': 'high',
                    'impact': 'Polymer can melt, discolor, or degrade with excessive heat',
                    'solutions': [
                        'Use low power settings',
                        'Fast scanning to minimize heat accumulation',
                        'Single pass cleaning when possible'
                    ]
                }
            ],
            'surface_characteristics': [
                {
                    'challenge': 'Surface sensitivity to UV',
                    'severity': 'medium',
                    'impact': 'Some polymers degrade under UV laser exposure',
                    'solutions': [
                        'Test on sample material first',
                        'Use lowest effective power',
                        'Consider IR wavelength for sensitive polymers'
                    ]
                }
            ],
            'contamination_challenges': [
                {
                    'challenge': 'Contaminant removal without substrate damage',
                    'severity': 'high',
                    'impact': 'Tight margin between cleaning and damaging plastic',
                    'solutions': [
                        'Use defocused beam for gentler cleaning',
                        'Test parameters extensively',
                        'Consider alternative cleaning methods for heavy contamination'
                    ]
                }
            ]
        },
        'semiconductor': {
            'thermal_management': [
                {
                    'challenge': 'Precise thermal control required',
                    'severity': 'high',
                    'impact': 'Thermal damage can alter electrical properties',
                    'solutions': [
                        'Use ultra-short pulses when available',
                        'Minimize power to effective threshold',
                        'Monitor surface temperature during cleaning'
                    ]
                }
            ],
            'surface_characteristics': [
                {
                    'challenge': 'Surface precision requirements',
                    'severity': 'high',
                    'impact': 'Even minor surface changes can affect performance',
                    'solutions': [
                        'Use smallest effective spot size',
                        'Multiple gentle passes instead of single high-power pass',
                        'Validate surface integrity post-cleaning'
                    ]
                }
            ],
            'contamination_challenges': [
                {
                    'challenge': 'Particle contamination sensitivity',
                    'severity': 'high',
                    'impact': 'Microscopic particles can affect semiconductor function',
                    'solutions': [
                        'Use cleanroom environment',
                        'Implement particle extraction during cleaning',
                        'Post-clean validation required'
                    ]
                }
            ]
        },
        'stone': {
            'thermal_management': [
                {
                    'challenge': 'Heterogeneous composition',
                    'severity': 'medium',
                    'impact': 'Different minerals respond differently to laser',
                    'solutions': [
                        'Use conservative power settings',
                        'Test on inconspicuous area first',
                        'Adjust parameters based on stone response'
                    ]
                }
            ],
            'surface_characteristics': [
                {
                    'challenge': 'Natural surface variation',
                    'severity': 'low',
                    'impact': 'Porous vs dense areas clean differently',
                    'solutions': [
                        'Adapt scanning speed to surface characteristics',
                        'Multiple passes for uniform results',
                        'Monitor for differential cleaning rates'
                    ]
                }
            ],
            'contamination_challenges': [
                {
                    'challenge': 'Deep-seated contaminants',
                    'severity': 'medium',
                    'impact': 'Contaminants may penetrate porous stone',
                    'solutions': [
                        'Use multiple passes with increasing power',
                        'Chemical pre-treatment for stubborn stains',
                        'Assess depth of contamination before cleaning'
                    ]
                }
            ]
        },
        'glass': {
            'thermal_management': [
                {
                    'challenge': 'Thermal shock risk',
                    'severity': 'high',
                    'impact': 'Rapid temperature changes can crack glass',
                    'solutions': [
                        'Use moderate power levels',
                        'Ensure uniform heating with proper overlap',
                        'Avoid cold glass surfaces - pre-warm if necessary'
                    ]
                }
            ],
            'surface_characteristics': [
                {
                    'challenge': 'Surface transparency affects cleaning',
                    'severity': 'medium',
                    'impact': 'Laser may pass through clean glass',
                    'solutions': [
                        'Use wavelength with good glass absorption',
                        'Focus on contaminant layer absorption',
                        'Adjust angle for better coupling'
                    ]
                }
            ],
            'contamination_challenges': [
                {
                    'challenge': 'Surface versus embedded contamination',
                    'severity': 'medium',
                    'impact': 'Surface cleaning won't remove embedded contaminants',
                    'solutions': [
                        'Assess contamination depth before cleaning',
                        'Use appropriate wavelength for contaminant type',
                        'Consider polishing for embedded contaminants'
                    ]
                }
            ]
        },
        'wood': {
            'thermal_management': [
                {
                    'challenge': 'Charring and burning risk',
                    'severity': 'high',
                    'impact': 'Wood chars easily with excessive laser energy',
                    'solutions': [
                        'Use lowest effective power',
                        'Fast scanning to minimize heat accumulation',
                        'Single pass cleaning preferred'
                    ]
                }
            ],
            'surface_characteristics': [
                {
                    'challenge': 'Grain direction and density variations',
                    'severity': 'medium',
                    'impact': 'Different grain patterns clean differently',
                    'solutions': [
                        'Follow grain direction when possible',
                        'Adjust speed based on wood density',
                        'Test on sample wood piece first'
                    ]
                }
            ],
            'contamination_challenges': [
                {
                    'challenge': 'Preserving wood patina',
                    'severity': 'medium',
                    'impact': 'Aggressive cleaning can remove desired aged appearance',
                    'solutions': [
                        'Use gentle parameters to preserve patina',
                        'Spot test in inconspicuous area',
                        'Consider manual cleaning for valuable antiques'
                    ]
                }
            ]
        }
    }
    
    return challenges_templates.get(category, challenges_templates['metal'])


def main():
    print("="*80)
    print("GENERATING SETTINGS FOR 27 MISSING MATERIALS")
    print("="*80)
    print()
    
    # Load existing files
    materials_file = Path('data/materials/Materials.yaml')
    settings_file = Path('data/settings/Settings.yaml')
    
    with open(materials_file, 'r') as f:
        materials_data = yaml.safe_load(f)
    
    with open(settings_file, 'r') as f:
        settings_data = yaml.safe_load(f)
    
    materials = materials_data['materials']
    settings = settings_data['settings']
    
    # Find missing materials
    missing = sorted(set(materials.keys()) - set(settings.keys()))
    
    print(f"Found {len(missing)} materials to add")
    print()
    
    # Generate settings for each missing material
    added_count = 0
    
    for mat_name in missing:
        mat = materials[mat_name]
        category = mat.get('category', 'metal')
        
        # Get template settings for this category
        template = CATEGORY_SETTINGS_TEMPLATES.get(category, CATEGORY_SETTINGS_TEMPLATES['metal'])
        
        # Create settings entry
        settings[mat_name] = {
            'machineSettings': template.copy(),
            'material_challenges': generate_material_challenges(mat_name, category),
            'settings_description': f"Laser cleaning {mat_name} requires careful parameter control based on its {category} properties. The settings provided balance cleaning effectiveness with material preservation, accounting for thermal sensitivity and surface characteristics typical of {category} materials."
        }
        
        added_count += 1
        print(f"✅ Added settings for {mat_name} ({category})")
    
    # Save updated Settings.yaml
    with open(settings_file, 'w') as f:
        yaml.dump(settings_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
    
    print()
    print("="*80)
    print(f"✅ COMPLETE: Added {added_count} materials to Settings.yaml")
    print("="*80)
    print()
    print(f"Settings.yaml now has {len(settings)} materials (was {len(settings) - added_count})")
    print(f"Coverage: {len(settings)}/{len(materials)} = {len(settings)/len(materials)*100:.1f}%")


if __name__ == '__main__':
    main()
