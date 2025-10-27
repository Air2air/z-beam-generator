# FAQ Component Configuration

# Question count ranges
MIN_QUESTIONS: 7
MAX_QUESTIONS: 12

# Word count limits per FAQ answer (concise and accessible)
MIN_WORDS_PER_ANSWER = 20
MAX_WORDS_PER_ANSWER = 60

# Quality thresholds
MIN_UNIQUENESS_SCORE: 90  # Questions must be 90%+ material-specific
MIN_UTILITY_SCORE: 85     # Answers must be 85%+ practically useful
REQUIRED_ACCURACY: 100    # 100% technical accuracy (all values traceable)
MIN_VOICE_AUTHENTICITY: 95  # 95%+ author voice match

# Category tags for FAQ organization (internal use)
CATEGORY_TAGS = [
    # Cost and practical considerations
    'cost_economics',
    'time_duration',
    'speed_efficiency',
    
    # Machine operation
    'machine_settings',
    'operator_skills',
    'quality_verification',
    
    # Safety and risks
    'safety',
    'damage_risks',
    'limitations',
    
    # Maintenance and treatment
    'post_treatment',
    'coatings_removal',
    'coverage_area',
    
    # Material thermal characteristics
    'thermal_management',
    'heat_effects',
    'thermal_damage',
    'temperature_sensitivity',
    
    # Physical and optical properties
    'material_density',
    'surface_hardness',
    'reflectivity_challenges',
    'laser_absorption',
    'wavelength_interaction',
    
    # Material handling requirements
    'strength_considerations',
    'fragility_risks',
    'damage_resistance',
    'structural_integrity',
    'delicate_handling',
    
    # Unusual material characteristics
    'unique_properties',
    'rare_behavior',
    'special_requirements',
    'unusual_challenges',
    
    # Contaminant-related
    'surface_damage_from_contaminants',
    'contaminant_removal_difficulty',
    'heat_induced_contamination',
    'oxide_formation',
    'residue_effects',
    
    # Application-specific
    'application_advantages',
    'application_challenges',
    'industry_requirements',
    'performance_characteristics',
]

# Complexity scoring factors
COMPLEXITY_FACTORS = {
    'high_property_count': 3,  # > 20 properties
    'medium_property_count': 2,  # 10-20 properties
    'low_property_count': 1,   # < 10 properties
    'many_applications': 2,    # > 6 applications
    'some_applications': 1,    # 3-6 applications
    'hazardous_material': 2,   # Safety-critical materials
    'heritage_material': 1     # Conservation-critical materials
}

# Question generation settings
QUESTION_GENERATION = {
    'include_material_name': True,  # Always include material name in questions
    'vary_question_styles': True,   # Use Why/How/What/Comparison variations
    'material_specific_only': True, # Reject generic laser cleaning questions
    'web_research_driven': True     # Research unique characteristics before generation
}

# Answer generation settings
ANSWER_GENERATION = {
    'include_property_values': True,        # Always cite actual values from Materials.yaml
    'include_category_comparisons': True,   # Compare to category ranges
    'use_author_voice': True,               # Apply country-specific voice patterns
    'technical_depth': 'expert',            # Expert-level technical content
    'cite_applications': True               # Reference specific application contexts
}
