#!/usr/bin/env python3
"""FAQ Component Generator - Material-Specific Question/Answer Generation with Author Voice"""

import datetime
import json
import logging
import time
import yaml
from pathlib import Path
from typing import Dict, Optional, List
from generators.component_generators import APIComponentGenerator, ComponentResult
from utils.config_loader import load_yaml_config
from voice.orchestrator import VoiceOrchestrator

logger = logging.getLogger(__name__)


class FAQComponentGenerator(APIComponentGenerator):
    """Generate material-specific FAQ with 7-12 questions using author voice"""
    
    def __init__(self):
        super().__init__("faq")
        self.min_questions = 7
        self.max_questions = 12
        self.min_words_per_answer = 150
        self.max_words_per_answer = 300
        
    def _load_frontmatter_data(self, material_name: str) -> Dict:
        """Load frontmatter data for the material - case-insensitive search"""
        content_dir = Path("content/frontmatter")
        
        # Normalize material name for more flexible matching
        normalized_name = material_name.lower().replace('_', ' ').replace(' ', '-')
        
        potential_paths = [
            content_dir / f"{material_name.lower()}.yaml",
            content_dir / f"{material_name.lower().replace(' ', '-')}.yaml",
            content_dir / f"{material_name.lower().replace('_', '-')}.yaml",
            content_dir / f"{normalized_name}.yaml",
            content_dir / f"{material_name.lower().replace(' ', '-')}-laser-cleaning.yaml",
            content_dir / f"{normalized_name}-laser-cleaning.yaml"
        ]
        
        for path in potential_paths:
            if path.exists():
                try:
                    return load_yaml_config(str(path))
                except Exception as e:
                    logger.warning(f"Could not load frontmatter from {path}: {e}")
                    continue
        
        return {}
    
    def _load_materials_data(self) -> Dict:
        """Load Materials.yaml for property lookups"""
        materials_path = Path("data/Materials.yaml")
        if materials_path.exists():
            try:
                return load_yaml_config(str(materials_path))
            except Exception as e:
                logger.warning(f"Could not load Materials.yaml: {e}")
        return {}
    
    def _load_categories_data(self) -> Dict:
        """Load Categories.yaml for range comparisons"""
        categories_path = Path("data/Categories.yaml")
        if categories_path.exists():
            try:
                return load_yaml_config(str(categories_path))
            except Exception as e:
                logger.warning(f"Could not load Categories.yaml: {e}")
        return {}
    
    def _determine_question_count(self, material_data: Dict, category: str) -> int:
        """Determine optimal question count (7-12) based on material complexity
        
        Args:
            material_data: Material data from Materials.yaml
            category: Material category (metal, ceramic, etc.)
            
        Returns:
            Question count between 7 and 12
        """
        complexity_score = 0
        
        # Factor 1: Number of material properties
        props = material_data.get('materialProperties', {})
        prop_count = 0
        for category_key in ['material_characteristics', 'laser_material_interaction']:
            if category_key in props:
                prop_count += len(props[category_key])
        
        if prop_count > 20:
            complexity_score += 3
        elif prop_count > 10:
            complexity_score += 2
        else:
            complexity_score += 1
        
        # Factor 2: Number of applications
        app_count = len(material_data.get('applications', []))
        if app_count > 6:
            complexity_score += 2
        elif app_count > 3:
            complexity_score += 1
        
        # Factor 3: Hazardous/special materials get more questions
        safety_keywords = ['toxic', 'hazard', 'flammable', 'beryllium', 'lead', 'cadmium']
        material_name_lower = material_data.get('name', '').lower()
        if any(keyword in material_name_lower for keyword in safety_keywords):
            complexity_score += 2
        
        # Factor 4: Heritage/rare materials get more questions
        heritage_keywords = ['heritage', 'conservation', 'restoration', 'cultural', 'archaeological']
        applications = [app.lower() for app in material_data.get('applications', [])]
        if any(any(keyword in app for keyword in heritage_keywords) for app in applications):
            complexity_score += 1
        
        # Map complexity score to question count (7-12)
        if complexity_score >= 7:
            return 12
        elif complexity_score >= 5:
            return 10
        elif complexity_score >= 3:
            return 9
        else:
            return 7
    
    def _get_property_value(self, props: Dict, property_name: str) -> Optional[float]:
        """Extract numeric property value from nested structure"""
        for category_key in ['material_characteristics', 'laser_material_interaction']:
            if category_key in props:
                category_data = props[category_key]
                # Check if properties are nested under 'properties' key
                if 'properties' in category_data and isinstance(category_data['properties'], dict):
                    if property_name in category_data['properties']:
                        prop_data = category_data['properties'][property_name]
                        if isinstance(prop_data, dict) and 'value' in prop_data:
                            return prop_data['value']
                # Also check direct property access
                elif property_name in category_data:
                    prop_data = category_data[property_name]
                    if isinstance(prop_data, dict) and 'value' in prop_data:
                        return prop_data['value']
        return None
    
    def _score_thermal_relevance(self, material_data: Dict) -> int:
        """Score thermal category relevance (0-10) - only high for thermally sensitive or extreme conductivity materials"""
        score = 2  # Low baseline - thermal is not relevant for most materials
        props = material_data.get('materialProperties', {})
        category = material_data.get('category', '').lower()
        material_name = material_data.get('name', '').lower()
        
        # Check thermal conductivity for extreme cases
        thermal_cond = self._get_property_value(props, 'thermalConductivity')
        if thermal_cond:
            if thermal_cond < 10:  # Very poor conductors (insulators)
                score += 9  # Heat accumulation is critical
            elif thermal_cond > 300:  # Excellent conductors (copper, aluminum)
                score += 7  # Rapid heat dissipation matters
            elif thermal_cond < 50 or thermal_cond > 150:
                score += 4  # Moderately relevant
        
        # Check melting point for low-temperature materials
        melting_point = self._get_property_value(props, 'meltingPoint')
        if melting_point:
            if melting_point < 500:  # Very low melting point
                score += 10
            elif melting_point < 1000:
                score += 5
        
        # Category-based for known thermally sensitive materials
        if category in ['polymer', 'plastic', 'wood']:
            score += 10  # Highly thermally sensitive
        elif category == 'composite':
            score += 7  # Moderately sensitive
        
        # Known thermally sensitive materials by name
        sensitive_materials = ['plastic', 'polymer', 'wood', 'rubber', 'carbon fiber']
        if any(sens in material_name for sens in sensitive_materials):
            score += 8
        
        return min(score, 10)
    
    def _score_reflectivity_relevance(self, material_data: Dict) -> int:
        """Score reflectivity category relevance (0-10) - only high for highly reflective metals"""
        score = 0
        props = material_data.get('materialProperties', {})
        category = material_data.get('category', '').lower()
        material_name = material_data.get('name', '').lower()
        
        # Check actual reflectivity value
        reflectivity = self._get_property_value(props, 'laserReflectivity')
        if not reflectivity:
            reflectivity = self._get_property_value(props, 'reflectivity')
        
        if reflectivity:
            if reflectivity > 80:
                score = 10  # Extreme challenge (silver, aluminum, polished metals)
            elif reflectivity > 70:
                score = 9  # Major challenge
            elif reflectivity > 50:
                score = 6  # Moderate concern
            else:
                score = 2  # Low reflectivity - not a concern
        else:
            # Known highly reflective metals
            if category == 'metal':
                highly_reflective = ['aluminum', 'aluminium', 'silver', 'copper', 'gold', 'chrome', 'stainless']
                if any(metal in material_name for metal in highly_reflective):
                    score = 9  # Assume high reflectivity
                else:
                    score = 4  # Other metals - moderate
            else:
                score = 0  # Non-metals generally not reflective
        
        return score
    
    def _score_fragility_relevance(self, material_data: Dict) -> int:
        """Score fragility category relevance (0-10) - high only for genuinely fragile materials"""
        score = 0
        props = material_data.get('materialProperties', {})
        category = material_data.get('category', '').lower()
        applications = material_data.get('applications', [])
        material_name = material_data.get('name', '').lower()
        
        # Check actual hardness (Mohs scale)
        hardness = self._get_property_value(props, 'hardness')
        if not hardness:
            hardness = self._get_property_value(props, 'mohs_hardness')
        
        if hardness:
            if hardness < 2.5:  # Very soft (gypsum, talc)
                score = 10  # Extremely fragile
            elif hardness < 4:  # Soft (calcite, fluorite)
                score = 9  # Very fragile
            elif hardness < 6:  # Medium (apatite, feldspar)
                score = 5  # Moderately fragile
            elif hardness > 8.5:  # Very hard (corundum, diamond)
                score = 7  # Hard but can be brittle
            else:
                score = 2  # Medium hardness - not particularly fragile
        else:
            # Category-based estimates
            if category in ['glass', 'ceramic']:
                score = 8  # Brittle materials
            elif category == 'stone':
                # Soft stones
                soft_stones = ['alabaster', 'limestone', 'marble', 'sandstone', 'soapstone']
                if any(stone in material_name for stone in soft_stones):
                    score = 9
                else:
                    score = 5  # Harder stones
            elif category in ['metal']:
                score = 0  # Metals generally not fragile
        
        # Heritage/conservation emphasis
        heritage_keywords = ['heritage', 'conservation', 'restoration', 'cultural', 'art']
        if any(any(kw in app.lower() for kw in heritage_keywords) for app in applications):
            score = min(score + 3, 10)  # Increase score for heritage materials
        
        # Check fracture toughness (low = fragile)
        fracture_toughness = self._get_property_value(props, 'fractureToughness')
        if fracture_toughness and fracture_toughness < 1.0:
            score = min(score + 5, 10)
        
        return score
    
    def _score_contaminant_relevance(self, material_data: Dict) -> int:
        """Score contaminant category relevance (0-10) - high for porous materials and reactive metals"""
        score = 1  # Low baseline
        props = material_data.get('materialProperties', {})
        category = material_data.get('category', '').lower()
        applications = material_data.get('applications', [])
        material_name = material_data.get('name', '').lower()
        
        # Check actual porosity (volume fraction)
        porosity = self._get_property_value(props, 'porosity')
        if porosity:
            # Porosity is typically 0.0-1.0 (volume fraction)
            if porosity > 0.3:  # >30% porous
                score = 10  # Highly porous - contaminants penetrate deeply
            elif porosity > 0.15:  # >15% porous
                score = 8  # Moderately porous
            elif porosity > 0.05:  # >5% porous
                score = 5  # Slightly porous
            else:
                score = 2  # Dense material
        else:
            # Category-based estimates for porous materials
            if category == 'stone':
                porous_stones = ['sandstone', 'limestone', 'travertine', 'alabaster']
                if any(stone in material_name for stone in porous_stones):
                    score = 9
                else:
                    score = 5  # Denser stones like granite
            elif category == 'wood':
                score = 9  # Wood is porous
            elif category == 'concrete':
                score = 8  # Concrete is porous
            elif category == 'ceramic':
                score = 6  # Some ceramics are porous
        
        # Reactive/oxidizing metals (form surface contaminants)
        if category == 'metal':
            highly_reactive = ['copper', 'iron', 'steel', 'bronze', 'brass', 'aluminum', 'aluminium']
            if any(reactive in material_name for reactive in highly_reactive):
                score = max(score, 8)  # Oxidation and corrosion
            else:
                score = max(score, 3)  # Less reactive metals
        
        # Corrosion resistance (low = high contamination)
        corrosion_resistance = self._get_property_value(props, 'corrosionResistance')
        if corrosion_resistance and corrosion_resistance < 5:
            score = min(score + 4, 10)
        
        # Application-based
        harsh_apps = ['marine', 'outdoor', 'industrial', 'chemical', 'automotive']
        if any(any(harsh in app.lower() for harsh in harsh_apps) for app in applications):
            score = min(score + 2, 10)
        
        return score
    
    def _score_unusual_relevance(self, material_data: Dict) -> int:
        """Score unusual behavior category relevance (0-10) - only high for truly rare/exotic materials"""
        score = 0
        category = material_data.get('category', '').lower()
        material_name = material_data.get('name', '').lower()
        applications = material_data.get('applications', [])
        props = material_data.get('materialProperties', {})
        
        # Rare/exotic material categories
        if category in ['rare-earth', 'semiconductor']:
            score = 10
        elif category == 'composite':
            score = 7  # Multiple phases = unusual behavior
        
        # Rare materials by name
        rare_materials = ['beryllium', 'tantalum', 'rhenium', 'iridium', 'osmium', 'rhodium']
        exotic_materials = ['graphene', 'aerogel', 'metamaterial']
        if any(rare in material_name for rare in rare_materials + exotic_materials):
            score = 10
        
        # Common materials should score low
        common_materials = ['steel', 'aluminum', 'aluminium', 'copper', 'iron', 'brass', 'bronze', 
                           'concrete', 'wood', 'plastic', 'glass']
        if any(common in material_name for common in common_materials):
            score = max(score - 5, 0)
        
        # Heritage/archaeological (unusual historical context)
        heritage_keywords = ['heritage', 'archaeological', 'conservation', 'restoration']
        if any(any(kw in app.lower() for kw in heritage_keywords) for app in applications):
            score = min(score + 6, 10)
        
        # Phase change materials or anisotropic materials
        melting_point = self._get_property_value(props, 'meltingPoint')
        if melting_point and melting_point < 200:  # Low melting point = unusual
            score = min(score + 5, 10)
        
        return score
    
    def _score_application_relevance(self, material_data: Dict) -> int:
        """Score application category relevance (0-10)"""
        score = 4  # Baseline - applications somewhat relevant for all materials
        applications = material_data.get('applications', [])
        
        # Critical/specialized applications
        critical_apps = ['aerospace', 'medical', 'nuclear', 'defense']
        if any(any(crit in app.lower() for crit in critical_apps) for app in applications):
            score += 6  # High-stakes applications
        
        # Heritage/art (requires special care)
        heritage_apps = ['heritage', 'art', 'conservation', 'cultural']
        if any(any(her in app.lower() for her in heritage_apps) for app in applications):
            score += 6  # Conservation focus
        
        # Versatility (many applications)
        if len(applications) > 8:
            score += 2  # Very versatile
        elif len(applications) < 3:
            score -= 2  # Limited use case
        
        return max(0, min(score, 10))
    
    def _score_safety_relevance(self, material_data: Dict) -> int:
        """Score safety category relevance (0-10)"""
        score = 5  # Baseline - safety always somewhat relevant
        material_name = material_data.get('name', '').lower()
        category = material_data.get('category', '').lower()
        props = material_data.get('materialProperties', {})
        
        # Toxic materials
        toxic_materials = ['beryllium', 'lead', 'cadmium', 'arsenic', 'chromium']
        if any(toxic in material_name for toxic in toxic_materials):
            score += 10
        
        # High reflectivity (eye hazard)
        reflectivity = self._get_property_value(props, 'laserReflectivity')
        if reflectivity and reflectivity > 70:
            score += 8
        
        # Metal fumes
        if category == 'metal':
            score += 6
        
        return min(score, 10)
    
    def _generate_material_questions(
        self,
        material_name: str,
        material_data: Dict,
        frontmatter_data: Dict,
        categories_data: Dict,
        question_count: int
    ) -> List[Dict]:
        """Generate material-specific questions with intelligent category scoring
        
        Returns:
            List of question dictionaries with 'question', 'category', 'focus_points'
        """
        # Calculate category relevance scores
        category_scores = {
            'thermal': self._score_thermal_relevance(material_data),
            'reflectivity': self._score_reflectivity_relevance(material_data),
            'fragility': self._score_fragility_relevance(material_data),
            'contaminant': self._score_contaminant_relevance(material_data),
            'unusual': self._score_unusual_relevance(material_data),
            'application': self._score_application_relevance(material_data),
            'safety': self._score_safety_relevance(material_data)
        }
        
        # All question templates with category group mappings
        all_templates = [
            # Cost and practical (baseline - moderate scores)
            {
                'template': f"How much does it cost to laser clean {material_name}?",
                'category': 'cost_economics',
                'focus': 'Cost factors, pricing comparison, ROI vs traditional methods',
                'score': 7,  # Baseline - always relevant but not dominant
                'group': 'practical'
            },
            {
                'template': f"What laser power works best for {material_name}?",
                'category': 'machine_settings',
                'focus': 'Optimal power range, effects of too high/low power',
                'score': 6,  # Lower baseline to let material-specific categories dominate
                'group': 'practical'
            },
            
            # Thermal characteristics
            {
                'template': f"How does heat affect {material_name} during laser cleaning?",
                'category': 'heat_effects',
                'focus': 'Thermal sensitivity, heat dissipation, temperature limits',
                'score': category_scores['thermal'],
                'group': 'thermal'
            },
            {
                'template': f"What temperature considerations exist for {material_name}?",
                'category': 'thermal_management',
                'focus': 'Thermal conductivity, cooling requirements, heat accumulation',
                'score': category_scores['thermal'],
                'group': 'thermal'
            },
            
            # Physical properties and optical behavior
            {
                'template': f"Why does {material_name}'s reflectivity matter for laser cleaning?",
                'category': 'reflectivity_challenges',
                'focus': 'Reflectivity values, laser-material interaction, wavelength selection',
                'score': category_scores['reflectivity'],
                'group': 'optical'
            },
            {
                'template': f"What physical properties make {material_name} unique for cleaning?",
                'category': 'unique_properties',
                'focus': 'Density, hardness, absorption, distinctive characteristics',
                'score': category_scores['unusual'],
                'group': 'unusual'
            },
            
            # Material handling and strength
            {
                'template': f"Is {material_name} fragile during laser cleaning?",
                'category': 'fragility_risks',
                'focus': 'Structural integrity, brittleness, handling precautions',
                'score': category_scores['fragility'],
                'group': 'handling'
            },
            {
                'template': f"What strength characteristics affect {material_name} cleaning?",
                'category': 'strength_considerations',
                'focus': 'Mechanical properties, damage resistance, durability',
                'score': category_scores['fragility'] if category_scores['fragility'] >= 7 else max(category_scores['reflectivity'] // 2, 3),
                'group': 'handling'
            },
            
            # Unusual/arcane characteristics
            {
                'template': f"What unusual behaviors does {material_name} exhibit during cleaning?",
                'category': 'rare_behavior',
                'focus': 'Uncommon responses, unexpected reactions, special phenomena',
                'score': category_scores['unusual'],
                'group': 'unusual'
            },
            {
                'template': f"What makes {material_name} different from other materials?",
                'category': 'special_requirements',
                'focus': 'Distinctive features, unique challenges, rare characteristics',
                'score': category_scores['unusual'],
                'group': 'unusual'
            },
            
            # Contaminant effects
            {
                'template': f"Can contaminants damage {material_name}'s surface?",
                'category': 'surface_damage_from_contaminants',
                'focus': 'Contamination impact, surface degradation, physical damage',
                'score': category_scores['contaminant'] if category_scores['contaminant'] >= 7 else 3,
                'group': 'contaminant'
            },
            {
                'template': f"Which contaminants are hardest to remove from {material_name}?",
                'category': 'contaminant_removal_difficulty',
                'focus': 'Stubborn residues, adhesion challenges, removal complexity',
                'score': category_scores['contaminant'],
                'group': 'contaminant'
            },
            {
                'template': f"How does heating affect contaminants on {material_name}?",
                'category': 'heat_induced_contamination',
                'focus': 'Thermal effects on residues, oxidation, heat-related changes',
                'score': min(category_scores['contaminant'], category_scores['thermal']),
                'group': 'contaminant'
            },
            
            # Application focus
            {
                'template': f"Why is {material_name} chosen for its main applications?",
                'category': 'application_advantages',
                'focus': 'Performance benefits, material selection reasons, key strengths',
                'score': category_scores['application'],
                'group': 'application'
            },
            {
                'template': f"What challenges does {material_name} present in use?",
                'category': 'application_challenges',
                'focus': 'Operational difficulties, limitations, problem areas',
                'score': category_scores['application'],
                'group': 'application'
            },
            
            # Safety and damage
            {
                'template': f"Can laser cleaning damage {material_name}?",
                'category': 'damage_risks',
                'focus': 'Potential damage, warning signs, prevention methods',
                'score': max(category_scores['safety'], category_scores['fragility']) if (category_scores['safety'] >= 7 or category_scores['fragility'] >= 7) else 5,
                'group': 'safety'
            },
            {
                'template': f"Is laser cleaning {material_name} safe?",
                'category': 'safety',
                'focus': 'Safety hazards, protective equipment, precautions',
                'score': category_scores['safety'],
                'group': 'safety'
            },
            
            # Efficiency and speed
            {
                'template': f"What's the fastest approach for {material_name}?",
                'category': 'speed_efficiency',
                'focus': 'Scan speed, throughput, productivity optimization',
                'score': 6,  # Moderate baseline
                'group': 'practical'
            },
            {
                'template': f"How long does cleaning {material_name} typically take?",
                'category': 'time_duration',
                'focus': 'Time estimates, factors affecting duration',
                'score': 5,  # Moderate baseline
                'group': 'practical'
            },
            
            # Post-treatment and verification
            {
                'template': f"What care does {material_name} need after cleaning?",
                'category': 'post_treatment',
                'focus': 'Post-cleaning care, protective coatings, storage',
                'score': category_scores['contaminant'] if category_scores['contaminant'] >= 8 else 4,
                'group': 'maintenance'
            },
            {
                'template': f"How can I verify {material_name} was cleaned properly?",
                'category': 'quality_verification',
                'focus': 'Inspection methods, success indicators, testing',
                'score': max(category_scores['application'], category_scores['fragility'], 5),
                'group': 'practical'
            },
        ]
        
        # Filter by score threshold and sort by score (descending)
        scored_templates = [t for t in all_templates if t['score'] >= 5]
        scored_templates.sort(key=lambda x: x['score'], reverse=True)
        
        # Select top-N, ensuring diversity (at least 5 different groups)
        selected = []
        groups_used = set()
        
        # First pass: select highest scoring from each group
        for template in scored_templates:
            if len(selected) >= question_count:
                break
            if template['group'] not in groups_used:
                selected.append(template)
                groups_used.add(template['group'])
        
        # Second pass: fill remaining slots with highest scores
        for template in scored_templates:
            if len(selected) >= question_count:
                break
            if template not in selected:
                selected.append(template)
        
        # Ensure diversity constraint (at least 5 groups)
        if len(groups_used) < 5 and len(scored_templates) > len(selected):
            # Add more templates to increase diversity
            for template in scored_templates:
                if template not in selected and template['group'] not in groups_used:
                    selected.append(template)
                    groups_used.add(template['group'])
                    if len(groups_used) >= 5:
                        break
        
        # Convert to final format
        questions = [
            {
                'template': t['template'],
                'category': t['category'],
                'focus': t['focus']
            }
            for t in selected[:question_count]
        ]
        
        return questions
    
    def _build_faq_answer_prompt(
        self,
        material_name: str,
        question: str,
        focus_points: str,
        frontmatter_data: Dict,
        material_data: Dict,
        categories_data: Dict,
        target_words: int = 250
    ) -> str:
        """Build AI prompt for FAQ answer generation using Voice service
        
        Args:
            material_name: Name of the material
            question: The FAQ question
            focus_points: Key points to address in answer
            frontmatter_data: Frontmatter data dictionary
            material_data: Full material data from Materials.yaml
            categories_data: Category ranges from Categories.yaml
            target_words: Target word count (150-300)
            
        Returns:
            Complete prompt string for answer generation
        """
        # Extract author data
        author_obj = frontmatter_data.get('author', {})
        if not author_obj or not author_obj.get('country'):
            raise ValueError(f"No author data found for {material_name} - required for voice system")
        
        # Get author details
        author_name = author_obj.get('name', 'Unknown')
        author_country = author_obj.get('country', 'Unknown')
        author_expertise = author_obj.get('expertise', 'Laser cleaning technology')
        
        # Initialize VoiceOrchestrator for country-specific voice
        voice = VoiceOrchestrator(country=author_country)
        
        # Extract material properties for context
        material_props = material_data.get('materialProperties', {})
        category = material_data.get('category', 'material')
        applications = material_data.get('applications', [])
        machine_settings = material_data.get('machineSettings', {})
        
        # Build comprehensive material context
        properties_summary = {}
        for category_key in ['material_characteristics', 'laser_material_interaction']:
            if category_key in material_props:
                for prop_name, prop_data in material_props[category_key].items():
                    if isinstance(prop_data, dict) and 'value' in prop_data:
                        properties_summary[prop_name] = {
                            'value': prop_data['value'],
                            'unit': prop_data.get('unit', ''),
                            'min': prop_data.get('min'),
                            'max': prop_data.get('max')
                        }
        
        settings_summary = {}
        for setting_name, setting_data in machine_settings.items():
            if isinstance(setting_data, dict) and 'value' in setting_data:
                settings_summary[setting_name] = {
                    'value': setting_data['value'],
                    'unit': setting_data.get('unit', ''),
                    'description': setting_data.get('description', '')
                }
        
        # Get category ranges for comparison
        category_ranges = {}
        if category in categories_data.get('categories', {}):
            cat_data = categories_data['categories'][category]
            if 'category_ranges' in cat_data:
                category_ranges = cat_data['category_ranges']
        
        # Build material context dict
        material_context = {
            'material_name': material_name,
            'category': category,
            'applications': ', '.join(applications[:5]) if applications else 'General applications',
            'properties': json.dumps(properties_summary, indent=2),
            'machine_settings': json.dumps(settings_summary, indent=2),
            'category_ranges': json.dumps(category_ranges, indent=2) if category_ranges else 'No category data'
        }
        
        # Build author dict
        author_dict = {
            'name': author_name,
            'country': author_country,
            'expertise': author_expertise
        }
        
        # Call Voice service to generate FAQ answer prompt
        try:
            prompt = voice.get_unified_prompt(
                component_type='technical_faq_answer',
                material_context=material_context,
                author=author_dict,
                question=question,
                focus_points=focus_points,
                target_words=target_words,
                include_property_values=True,
                technical_depth='expert'
            )
            
            # Add word limit enforcement
            tolerance = 20
            prompt += f"\n\nSTRICT WORD LIMIT: Write {target_words} words (±{tolerance} words tolerance).\n"
            prompt += "CRITICAL: Include actual property values from material data in your answer.\n"
            prompt += "REQUIRED: Use author's country-specific voice and technical style.\n"
            prompt += f"MINIMUM: Write at least {self.min_words_per_answer} words for substantive content.\n"
            prompt += f"MAXIMUM: Do NOT exceed {self.max_words_per_answer} words.\n"
            
            logger.info(f"✅ Generated FAQ answer prompt for: {question[:50]}... ({author_country} voice, {target_words}w)")
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to generate FAQ answer prompt via Voice service: {e}")
            raise
    
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate complete FAQ with 7-12 questions for the material
        
        Returns:
            ComponentResult with generated FAQ content in YAML format
        """
        try:
            logger.info(f"🎯 Generating FAQ for {material_name}...")
            
            # Load frontmatter if not provided
            if not frontmatter_data:
                frontmatter_data = self._load_frontmatter_data(material_name)
                if not frontmatter_data:
                    raise ValueError(f"No frontmatter data found for {material_name}")
            
            # Load Materials.yaml and Categories.yaml for context
            materials_yaml = self._load_materials_data()
            categories_yaml = self._load_categories_data()
            
            # Get material data from Materials.yaml
            if 'materials' in materials_yaml and material_name in materials_yaml['materials']:
                full_material_data = materials_yaml['materials'][material_name]
            else:
                full_material_data = material_data
            
            # Determine question count based on complexity
            category = full_material_data.get('category', 'material')
            question_count = self._determine_question_count(full_material_data, category)
            
            logger.info(f"📊 Generating {question_count} questions for {material_name} (category: {category})")
            
            # Generate questions
            questions = self._generate_material_questions(
                material_name,
                full_material_data,
                frontmatter_data,
                categories_yaml,
                question_count
            )
            
            # Generate answers for each question
            faq_items = []
            total_words = 0
            
            for idx, q_dict in enumerate(questions, 1):
                question = q_dict['template']
                category_tag = q_dict['category']
                focus = q_dict['focus']
                
                # Vary word count (20-60 range - concise and accessible)
                if idx <= 2:
                    target_words = 58  # Comprehensive for early questions
                elif idx >= question_count - 1:
                    target_words = 55  # Moderate for late questions
                else:
                    target_words = 45  # Standard middle questions
                
                logger.info(f"  Question {idx}/{question_count}: {question[:60]}...")
                
                # Build prompt
                prompt = self._build_faq_answer_prompt(
                    material_name,
                    question,
                    focus,
                    frontmatter_data,
                    full_material_data,
                    categories_yaml,
                    target_words
                )
                
                # Generate answer via API
                if not api_client:
                    raise ValueError("API client required for FAQ answer generation")
                
                # Calculate max_tokens for target word count (fail-fast: explicit values required)
                # FAQ answers: 150-300 words
                # Token estimation: ~1.3 tokens per word (conservative)
                # Safety margin: 1.5x to prevent truncation
                max_tokens = int(target_words * 1.3 * 1.5)  # Explicit calculation
                
                try:
                    response = api_client.generate_simple(
                        prompt,
                        max_tokens=max_tokens,  # Explicit - no defaults
                        temperature=0.6  # Slightly creative for natural FAQ responses
                    )
                    
                    if not response.success:
                        raise ValueError(f"API generation failed: {response.error}")
                    
                    answer = response.content
                    word_count = len(answer.split())
                    total_words += word_count
                    
                    # Validate word count
                    if word_count < self.min_words_per_answer:
                        logger.warning(f"    ⚠️  Answer too short: {word_count} words (min {self.min_words_per_answer})")
                    elif word_count > self.max_words_per_answer:
                        logger.warning(f"    ⚠️  Answer too long: {word_count} words (max {self.max_words_per_answer})")
                    else:
                        logger.info(f"    ✅ Answer generated: {word_count} words")
                    
                    faq_items.append({
                        'question': question,
                        'answer': answer.strip(),
                        'category': category_tag,
                        'word_count': word_count
                    })
                    
                    # Brief delay between API calls
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"    ❌ Failed to generate answer: {e}")
                    raise
            
            # Build FAQ structure
            author_obj = frontmatter_data.get('author', {})
            faq_structure = {
                'generated': datetime.datetime.now().isoformat() + 'Z',
                'author': author_obj.get('name', 'Unknown'),
                'generation_method': 'web_research_driven',
                'total_questions': len(faq_items),
                'total_words': total_words,
                'questions': faq_items
            }
            
            # Convert to YAML format
            faq_yaml = yaml.dump({'faq': faq_structure}, 
                                default_flow_style=False, 
                                allow_unicode=True,
                                sort_keys=False)
            
            logger.info(f"✅ FAQ generation complete: {len(faq_items)} questions, {total_words} total words")
            
            return self._create_result(faq_yaml, success=True)
            
        except Exception as e:
            logger.error(f"❌ FAQ generation failed for {material_name}: {e}")
            from utils.ai.loud_errors import component_failure
            component_failure(self.component_type, str(e), material=material_name)
            return self._create_result("", success=False, error_message=str(e))
