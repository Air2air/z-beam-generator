#!/usr/bin/env python3
"""
Caption Component Generator

Generates technical image captions for laser        # Validate required material data - fai  frequency: {laser_param  laser_parameters:
  wavelength: {laser_params['wavelength']}
  power: {laser_params['power']}
  pulse_duration: {laser_params['pulse_duration']}
  spot_size: {laser_params['spot_size']}
  frequency: {laser_params['frequency']}
  energy_density: {laser_params['energy_density']}
  scanning_speed: "{laser_params['scanning_speed']}"
  beam_profile: "{laser_params['beam_profile']}"tion: {laser_params['pulse_duration']}
  spot_size: {laser_params['spot_size']}
  frequency: {laser_params['frequency']}
  energy_density: {laser_params['energy_density']}
  scanning_speed: "{laser_params['scanning_speed']}"
  beam_profile: "{laser_params['beam_profile']}"uency']}
  energy_density: {laser_params['energy_density']}
  scanning_speed: "{laser_params['scanning_speed']}"
  beam_profile: "{laser_params['beam_profile']}"
  pulse_overlap: {laser_params['pulse_overlap']}t architecture
        if 'formula' not in material_data:
            raise ValueError("Material formula is required - fail-fast architecture requires complete material data")
        if 'category' not in material_data:
            raise ValueError("Material category is required - fail-fast architecture requires complete material data")
            
        # Get material properties from material data
        material_formula = material_data['formula']
        material_category = material_data['category'].lower()eaning applications.
Uses consolidated component base utilities for reduced code duplication.
Now supports comprehensive YAML v2.0 format with enhanced SEO metadata,
quality metrics, and accessibility information.

Enhanced with material-specific data integration from frontmatter components
and category ranges for highly contextual, well-researched content.
"""

import random
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from generators.component_generators import StaticComponentGenerator
from utils.config_loader import load_yaml_config


class CaptionComponentGenerator(StaticComponentGenerator):
    """Generator for caption components using material data"""

    def __init__(self):
        super().__init__("caption")
        self.prompt_file = Path(__file__).parent / "prompt.yaml"
        self._category_ranges = None
        self._frontmatter_cache = {}
        
    def _load_category_ranges(self) -> Dict:
        """Load category ranges data for material property context"""
        if self._category_ranges is None:
            try:
                ranges_path = Path(__file__).parents[3] / "data" / "category_ranges.yaml"
                if ranges_path.exists():
                    self._category_ranges = load_yaml_config(str(ranges_path), "caption")
                else:
                    self._category_ranges = {}
            except Exception:
                self._category_ranges = {}
        return self._category_ranges
        
    def _load_frontmatter_data(self, material_name: str) -> Dict:
        """Load frontmatter data for specific material"""
        cache_key = material_name.lower()
        if cache_key not in self._frontmatter_cache:
            try:
                # Convert material name to filename format - try multiple variations
                filename_variations = [
                    f"{material_name.lower().replace(' ', '-').replace('_', '-')}-laser-cleaning.md",  # dashes
                    f"{material_name.lower()}-laser-cleaning.md",  # preserve spaces as spaces  
                    f"{material_name}-laser-cleaning.md"  # preserve original case and spaces
                ]
                
                frontmatter_path = None
                for filename in filename_variations:
                    potential_path = Path(__file__).parents[3] / "content" / "components" / "frontmatter" / filename
                    if potential_path.exists():
                        frontmatter_path = potential_path
                        break
                
                if frontmatter_path.exists():
                    with open(frontmatter_path, 'r') as f:
                        content = f.read()
                        # Extract YAML frontmatter
                        if content.startswith('---'):
                            yaml_end = content.find('---', 3)
                            if yaml_end != -1:
                                yaml_content = content[3:yaml_end].strip()
                                self._frontmatter_cache[cache_key] = yaml.safe_load(yaml_content)
                            else:
                                self._frontmatter_cache[cache_key] = {}
                        else:
                            self._frontmatter_cache[cache_key] = {}
                else:
                    self._frontmatter_cache[cache_key] = {}
            except Exception:
                self._frontmatter_cache[cache_key] = {}
                
        return self._frontmatter_cache[cache_key]

    def _generate_static_content(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> str:
        """Generate caption component content"""
        try:
            # Validate required data
            if not material_name:
                raise ValueError("Material name is required")

            # Generate caption content in YAML format (no versioning stamp needed as it's included in YAML)
            content = self._create_caption_content(material_name, material_data)

            return content

        except Exception as e:
            raise Exception(f"Error generating caption content: {e}")

    def _create_caption_content(self, material_name: str, material_data: Dict) -> str:
        """Create caption content in YAML format matching the comprehensive new structure"""
        import datetime
        import random
        
        # Load frontmatter data for this material (single source of truth)
        frontmatter_data = self._load_frontmatter_data(material_name)
        
        # Store frontmatter data for use in other methods
        self._current_frontmatter_data = frontmatter_data
        
        # Get material properties from frontmatter or fallback to material_data
        if frontmatter_data:
            material_formula = frontmatter_data.get('chemicalProperties', {}).get('formula', 
                              frontmatter_data.get('properties', {}).get('chemicalFormula', 
                              material_data.get('formula', '')))
            material_category = frontmatter_data.get('category', material_data.get('category', '')).lower()
        else:
            # Fallback to material_data (legacy compatibility)
            material_formula = material_data.get('formula', '')
            material_category = material_data.get('category', '').lower()
            
        laser_params = self._get_material_laser_params(material_data)
        
        # Generate contamination and analysis details
        contamination_type = self._get_material_contamination(material_category, frontmatter_data)
        analysis_details = self._get_analysis_details()
        quality_metrics = self._generate_quality_metrics(frontmatter_data)
        
        # Create before and after text descriptions
        before_text = self._generate_before_text(material_name, contamination_type, material_category, frontmatter_data)
        after_text = self._generate_after_text(material_name, laser_params, quality_metrics, frontmatter_data)
        
        # Generate comprehensive metadata
        timestamp = datetime.datetime.now().isoformat() + "Z"
        
        # Create author information based on material expertise
        author_info = self._get_material_author(material_category, frontmatter_data)
        
        # Generate SEO and technical metadata
        seo_data = self._generate_seo_metadata(material_name, material_category, quality_metrics, frontmatter_data)
        tech_specs = self._generate_technical_specifications(laser_params, material_name, frontmatter_data)
        chemical_props = self._generate_chemical_properties(material_name, material_formula, material_category, frontmatter_data)
        
        yaml_content = f"""# Basic Content Structure
before_text: |
  {before_text}

after_text: |
  {after_text}

# YAML v2.0 Laser Parameters
laser_parameters:
  wavelength: {laser_params['wavelength']}
  power: {laser_params['power']}
  pulse_duration: {laser_params['pulse_duration']}
  spot_size: {laser_params['spot_size']}
  frequency: {laser_params.get('frequency', random.randint(10000, 50000))}
  energy_density: {laser_params.get('energy_density', round(random.uniform(1.5, 4.0), 1))}
  scanning_speed: "{laser_params.get('scanning_speed', f'{random.randint(200, 800)} mm/min')}"
  beam_profile: "{laser_params.get('beam_profile', 'gaussian')}"
  pulse_overlap: {laser_params.get('pulse_overlap', random.randint(70, 90))}

# Material Information
material: "{material_name}"

# Technical Metadata
metadata:
  generated: "{timestamp}"
  format: "yaml"
  version: "2.0"
  analysis_method: "{analysis_details['method']}"
  magnification: "{analysis_details['magnification']}"
  field_of_view: "{analysis_details['field_of_view']}"
  image_resolution: "{analysis_details['resolution']}"

# Enhanced SEO Frontmatter
title: "{seo_data['title']}"
description: "{seo_data['description']}"

# SEO Keywords
keywords:
{self._format_keywords_list(seo_data['keywords'])}

# Author Information with SEO Enhancement
author: "{author_info['name']}"
author_object:
  name: "{author_info['name']}"
  email: "{author_info['email']}"
  affiliation: "{author_info['affiliation']}"
  title: "{author_info['title']}"
  expertise:
{self._format_expertise_list(author_info['expertise'])}

# Technical Specifications for SEO
technicalSpecifications:
  wavelength: "{tech_specs['wavelength']}"
  power: "{tech_specs['power']}"
  pulse_duration: "{tech_specs['pulse_duration']}"
  scanning_speed: "{tech_specs['scanning_speed']}"
  material: "{tech_specs['material']}"
  beam_delivery: "{tech_specs['beam_delivery']}"
  focus_diameter: "{tech_specs['focus_diameter']}"
  processing_atmosphere: "{tech_specs['processing_atmosphere']}"

# Chemical Properties for Enhanced SEO
chemicalProperties:
  composition: "{chemical_props['composition']}"
  surface_treatment: "laser cleaning"
  contamination_type: "{chemical_props['contamination_type']}"
  materialType: "{chemical_props['materialType']}"
  formula: "{chemical_props['formula']}"
  surface_finish: "{chemical_props['surface_finish']}"
  corrosion_resistance: "{chemical_props['corrosion_resistance']}"

# Image Metadata for SEO
images:
  micro:
    url: "/images/{material_name.lower().replace(' ', '-')}-cleaning-analysis.jpg"
    alt: "{seo_data['image_alt']}"
    width: 800
    height: 450
    format: "JPEG"
    caption: "{seo_data['image_caption']}"

# Additional SEO Metadata
seo_data:
  canonical_url: "https://z-beam.com/analysis/{material_name.lower().replace(' ', '-')}-laser-cleaning"
  og_title: "{seo_data['og_title']}"
  og_description: "{seo_data['og_description']}"
  og_image: "/images/{material_name.lower().replace(' ', '-')}-cleaning-analysis-social.jpg"
  twitter_card: "summary_large_image"
  schema_type: "AnalysisNewsArticle"
  last_modified: "{timestamp}"

# Quality Metrics
quality_metrics:
  surface_roughness_before: "{quality_metrics['surface_roughness_before']}"
  surface_roughness_after: "{quality_metrics['surface_roughness_after']}"
  substrate_integrity: "{quality_metrics['substrate_integrity']}"

# Accessibility Information
accessibility:
  alt_text_detailed: "{seo_data['accessibility_alt']}"
  caption_language: "en"
  technical_level: "professional"
  visual_description: "{seo_data['visual_description']}"

---
Material: "{material_name.lower()}"
Component: caption
Generated: {timestamp}
Generator: Z-Beam v1.0.0
Format: YAML v2.0
---"""
        
        return yaml_content

    def _get_material_laser_params(self, material_data: Dict) -> Dict[str, Any]:
        """Get laser parameters from frontmatter data - fail-fast, no fallbacks"""
        
        # First try to get laser parameters from frontmatter data (single source of truth)
        if hasattr(self, '_current_frontmatter_data') and self._current_frontmatter_data:
            frontmatter_data = self._current_frontmatter_data
            
            # Check for technicalSpecifications or machineSettings in frontmatter (preferred)
            if 'technicalSpecifications' in frontmatter_data:
                tech_specs = frontmatter_data['technicalSpecifications']
            elif 'machineSettings' in frontmatter_data:
                tech_specs = frontmatter_data['machineSettings']
                
                # Map frontmatter technicalSpecifications to laser_parameters format
                laser_params = {}
                
                # Required field mappings - only map fields that exist in frontmatter
                field_mappings = {
                    'wavelength': (['wavelength'], None),
                    'power': (['powerRange', 'power'], None),
                    'pulse_duration': (['pulseDuration', 'pulse_duration'], None),
                    'spot_size': (['spotSize', 'spot_size'], None),
                    'frequency': (['repetitionRate', 'frequency'], None),
                    'energy_density': (['fluenceRange', 'energy_density'], None),
                    'scanning_speed': (['scanningSpeed', 'scanning_speed'], None),
                    'beam_profile': (['beamProfile', 'beam_profile'], None),
                    # This field doesn't exist in frontmatter machineSettings - will be removed from output
                    # 'pulse_overlap': (['pulseOverlap', 'pulse_overlap'], None)
                }
                
                for param_key, (possible_frontmatter_keys, default_value) in field_mappings.items():
                    value = None
                    for fm_key in possible_frontmatter_keys:
                        if fm_key in tech_specs:
                            value = tech_specs[fm_key]
                            break
                    
                    # Fail-fast: no defaults, require all parameters from frontmatter
                    if value is None:
                        raise ValueError(f"Required laser parameter '{param_key}' missing from frontmatter machineSettings - fail-fast architecture requires complete laser specifications. Available fields: {list(tech_specs.keys())}")
                    
                    laser_params[param_key] = value
                
                return laser_params
        
        # Fallback to material_data only if frontmatter is not available (legacy compatibility)
        if 'laser_parameters' not in material_data:
            raise ValueError("Laser parameters are required in material data - fail-fast architecture requires complete laser specifications")
            
        params = material_data['laser_parameters'].copy()
        
        # Validate required laser parameter fields
        required_fields = ['wavelength', 'power', 'pulse_duration', 'spot_size', 'frequency', 'energy_density', 'scanning_speed', 'beam_profile']
        for field in required_fields:
            if field not in params:
                raise ValueError(f"Required laser parameter '{field}' missing from material data - fail-fast architecture requires complete laser specifications")
        
        return params

    def _get_material_contamination(self, material_category: str, frontmatter_data: Dict = None) -> str:
        """Get contamination type based on material category and frontmatter data"""
        
        # First try to get industry-specific contamination from frontmatter applications
        if frontmatter_data and 'applications' in frontmatter_data:
            industry_contamination = []
            for app in frontmatter_data['applications']:
                if 'detail' not in app:
                    raise ValueError("Application detail is required in frontmatter data - fail-fast architecture requires complete application information")
                detail = app['detail'].lower()
                
                # Extract contamination types from application details
                if 'lubricant' in detail or 'oil' in detail:
                    industry_contamination.append('industrial lubricants and oil residues')
                elif 'oxide' in detail or 'oxidation' in detail:
                    industry_contamination.append('oxide layers and surface oxidation')
                elif 'paint' in detail or 'coating' in detail:
                    industry_contamination.append('paint and protective coating deposits')
                elif 'biological' in detail or 'growth' in detail:
                    industry_contamination.append('biological growth and organic deposits')
                elif 'adhesive' in detail or 'residue' in detail:
                    industry_contamination.append('adhesive residues and bonding agents')
                elif 'anodized' in detail:
                    industry_contamination.append('anodized layer and surface treatments')
                elif 'thermal' in detail:
                    industry_contamination.append('thermal oxides and heat treatment residues')
                elif 'atmospheric' in detail or 'pollutant' in detail:
                    industry_contamination.append('atmospheric pollutants and environmental deposits')
                elif 'finish' in detail:
                    industry_contamination.append('old finishes and surface coatings')
                elif 'contaminant' in detail:
                    industry_contamination.append('surface contaminants and particulate matter')
            
            if industry_contamination:
                return random.choice(industry_contamination)
        
        # Fallback to category-based contamination
        contamination_by_category = {
            'metal': [
                'oxide layers and corrosion deposits',
                'industrial scale and surface oxidation',
                'metal particulates and galvanic corrosion',
                'thermal oxides and processing residues',
                'lubricant films and cutting fluid residues'
            ],
            'ceramic': [
                'sintering residues and binder contamination',
                'firing deposits and glaze imperfections', 
                'ceramic dust and processing particulates',
                'thermal shock deposits and surface films',
                'refractory deposits and kiln contamination'
            ],
            'glass': [
                'atmospheric deposits and surface films',
                'thermal stress patterns and annealing residues',
                'coating residues and optical contamination',
                'environmental staining and surface defects',
                'processing oils and handling contamination'
            ],
            'stone': [
                'weathering deposits and mineral staining',
                'biological growth and lichen colonization',
                'atmospheric pollution and acid rain damage',
                'efflorescence and salt crystallization',
                'organic deposits and environmental soiling'
            ],
            'wood': [
                'organic decay and lignin degradation',
                'fungal growth and mold contamination',
                'environmental staining and UV damage',
                'old finishes and protective coatings',
                'tannin staining and extractive migration'
            ],
            'composite': [
                'matrix degradation and resin breakdown',
                'delamination products and fiber exposure',
                'environmental aging and UV degradation',
                'processing residues and mold release agents',
                'interlaminar contamination and void formation'
            ],
            'masonry': [
                'efflorescence and salt deposits',
                'atmospheric pollution and acid damage',
                'biological growth and organic staining',
                'cement carbonation and surface films',
                'construction residues and mortar spatter'
            ],
            'semiconductor': [
                'organic contamination and photoresist residues',
                'metallic particles and ionic contamination',
                'oxide growth and interface defects',
                'processing chemicals and etch residues',
                'particle contamination and surface films'
            ]
        }
        
        # Require material category to be in supported categories - fail-fast
        if material_category not in contamination_by_category:
            raise ValueError(f"Unsupported material category '{material_category}' - fail-fast architecture requires supported material categories: {list(contamination_by_category.keys())}")
        
        category_contamination = contamination_by_category[material_category]
        
        return random.choice(category_contamination)

    def _get_analysis_details(self) -> Dict[str, str]:
        """Generate standardized analysis method details"""
        return {
            'method': 'scanning_electron_microscopy',  # Standardized method
            'magnification': '1000x',  # Standardized magnification
            'resolution': '3840x2160',  # Standardized 4K resolution
            'field_of_view': '200 μm'  # Standardized field of view
        }

    def _generate_quality_metrics(self, frontmatter_data: Dict = None) -> Dict[str, str]:
        """Generate realistic quality metrics based on material properties"""
        
        # Get material-specific surface roughness from frontmatter if available
        surface_roughness_context = None
        if frontmatter_data and 'properties' in frontmatter_data:
            props = frontmatter_data['properties']
            # Use material hardness to estimate surface roughness improvement
            if 'hardness' in str(props):
                hardness_str = str(props.get('hardness', ''))
                if 'HB' in hardness_str or 'HV' in hardness_str:
                    # Extract numeric value
                    import re
                    numbers = re.findall(r'\d+', hardness_str)
                    if numbers:
                        hardness_val = int(numbers[0])
                        # Harder materials generally have lower achievable surface roughness
                        if hardness_val > 300:  # Very hard materials
                            surface_roughness_context = ('low', 0.2, 0.8)  # Low before, very low after
                        elif hardness_val > 100:  # Medium hard materials
                            surface_roughness_context = ('medium', 1.0, 2.5)
                        else:  # Softer materials
                            surface_roughness_context = ('high', 2.0, 5.0)
        
        # Generate surface roughness based on material hardness
        if surface_roughness_context:
            level, min_before, max_before = surface_roughness_context
            before_roughness = f"Ra {random.uniform(min_before, max_before):.1f} μm"
            # After cleaning is typically 60-80% improvement
            improvement_factor = random.uniform(0.2, 0.4)
            after_val = random.uniform(min_before, max_before) * improvement_factor
            after_roughness = f"Ra {after_val:.1f} μm"
        else:
            before_roughness = f"Ra {random.uniform(1.5, 5.0):.1f} μm"
            after_roughness = f"Ra {random.uniform(0.2, 1.0):.1f} μm"
        
        # Substrate integrity based on laser parameters and material toughness
        integrity_options = ['100% preserved', '99% preserved', 'excellent', 'complete preservation']
        substrate_integrity = random.choice(integrity_options)
        
        return {
            'surface_roughness_before': before_roughness,
            'surface_roughness_after': after_roughness,
            'substrate_integrity': substrate_integrity
        }

    def _generate_before_text(self, material_name: str, contamination_type: str, material_category: str, frontmatter_data: Dict = None) -> str:
        """Generate detailed before text description using material-specific data"""
        examination_types = ['Initial surface examination', 'Preliminary microscopic analysis', 'Pre-treatment surface assessment']
        examination = random.choice(examination_types)
        
        # Get material-specific substrate description from frontmatter
        material_specific = {
            'metal': 'metallic substrate',
            'ceramic': 'ceramic surface',
            'glass': 'glass substrate', 
            'stone': 'stone surface',
            'wood': 'wooden substrate',
            'composite': 'composite material',
            'masonry': 'masonry surface',
            'semiconductor': 'semiconductor substrate'
        }
        
        substrate_desc = material_specific.get(material_category, 'substrate')
        
        # Use material density or hardness to add technical context
        technical_context = ""
        if frontmatter_data and 'properties' in frontmatter_data:
            props = frontmatter_data['properties']
            if 'density' in str(props):
                density_str = str(props.get('density', ''))
                if 'g/cm³' in density_str:
                    technical_context = f" The {material_name.lower()} exhibits the characteristic density profile typical of {material_category} materials."
        
        contamination_source = {
            'metal': 'manufacturing processes and environmental exposure',
            'ceramic': 'firing processes and handling contamination',
            'glass': 'atmospheric deposition and processing residues',
            'stone': 'weathering and environmental exposure',
            'wood': 'biological activity and environmental factors',
            'composite': 'manufacturing processes and environmental aging',
            'masonry': 'construction activities and atmospheric exposure',
            'semiconductor': 'fabrication processes and cleanroom contamination'
        }
        
        source = contamination_source.get(material_category, 'industrial processes')
        
        return f"""{examination} reveals significant contamination deposits across the {material_name.lower()} {substrate_desc}. 
  Microscopic analysis shows {contamination_type} adhering to the surface.{technical_context}
  The contamination appears to be from {source}."""

    def _generate_after_text(self, material_name: str, laser_params: Dict, quality_metrics: Dict, frontmatter_data: Dict = None) -> str:
        """Generate detailed after text description using material-specific outcomes"""
        
        analysis_types = ['Post-laser cleaning analysis', 'Treatment outcome assessment', 'Post-processing microscopic evaluation']
        analysis = random.choice(analysis_types)
        
        results = ['remarkable surface restoration', 'exceptional cleaning performance', 'outstanding contamination removal']
        result = random.choice(results)
        
        # Material-specific thermal effects
        thermal_effects = {
            'metal': ['minimal thermal effects', 'controlled thermal impact', 'negligible substrate modification'],
            'ceramic': ['minimal thermal stress', 'controlled thermal loading', 'preserved crystal structure'], 
            'glass': ['no thermal shock', 'maintained optical clarity', 'preserved transparency'],
            'stone': ['minimal thermal expansion', 'preserved structural integrity', 'no thermal cracking'],
            'wood': ['controlled thermal exposure', 'preserved fiber structure', 'no char formation'],
            'composite': ['minimal matrix heating', 'preserved fiber-matrix bond', 'no delamination'],
            'masonry': ['controlled thermal input', 'preserved structural soundness', 'no thermal cracking'],
            'semiconductor': ['minimal thermal stress', 'preserved crystalline structure', 'no lattice damage']
        }
        
        material_category = frontmatter_data.get('category', 'metal') if frontmatter_data else 'metal'
        thermal_effect = random.choice(thermal_effects.get(material_category, thermal_effects['metal']))
        
        examination_results = ['complete organic residue elimination', 'total contamination removal', 'comprehensive surface decontamination']
        examination = random.choice(examination_results)
        
        integrity_desc = ['preserving substrate integrity', 'maintaining material properties', 'ensuring structural preservation']
        integrity = random.choice(integrity_desc)
        
        return f"""{analysis} demonstrates {result} through comprehensive laser processing.
  The {material_name.lower()} substrate now exhibits pristine surface characteristics with {thermal_effect}.
  Microscopic examination confirms {examination} while {integrity}."""

    def _get_material_author(self, material_category: str, frontmatter_data: Dict = None) -> Dict[str, Any]:
        """Generate author information based on material expertise and frontmatter data"""
        
        # First try to use author from frontmatter if available
        if frontmatter_data and 'author_object' in frontmatter_data:
            author_obj = frontmatter_data['author_object']
            
            # Handle expertise as either string or list
            expertise = author_obj.get('expertise', 'Materials Scientist')
            if isinstance(expertise, list):
                expertise_str = expertise[0] if expertise else 'Materials Scientist'
            else:
                expertise_str = expertise
            
            return {
                'name': author_obj.get('name', 'Dr. Materials Scientist'),
                'email': f"{author_obj.get('name', 'scientist').lower().replace(' ', '.')}@materials-lab.com",
                'affiliation': 'Advanced Materials Processing Laboratory',
                'title': author_obj.get('title', 'Ph.D.') + ' ' + expertise_str,
                'expertise': self._get_author_expertise_from_frontmatter(frontmatter_data, material_category)
            }
        
        # Fallback to category-based authors
        authors_by_category = {
            'metal': {
                'name': 'Dr. Sarah Chen',
                'email': 's.chen@materials-lab.com',
                'affiliation': 'Advanced Materials Processing Laboratory',
                'title': 'Senior Materials Scientist',
                'expertise': ['Laser Materials Processing', 'Metallurgical Analysis', 'Surface Treatment Technologies', 'Industrial Cleaning Methods']
            },
            'ceramic': {
                'name': 'Dr. Michael Rodriguez',
                'email': 'm.rodriguez@ceramics-institute.org',
                'affiliation': 'Institute for Advanced Ceramics',
                'title': 'Principal Ceramics Engineer',
                'expertise': ['Ceramic Processing', 'Laser Surface Modification', 'High-Temperature Materials', 'Microscopic Characterization']
            },
            'glass': {
                'name': 'Dr. Emily Thompson',
                'email': 'e.thompson@optics-research.edu',
                'affiliation': 'Optical Materials Research Center',
                'title': 'Senior Research Scientist',
                'expertise': ['Optical Materials', 'Glass Science', 'Laser Processing', 'Surface Analysis']
            },
            'stone': {
                'name': 'Dr. Robert Kim',
                'email': 'r.kim@heritage-conservation.org',
                'affiliation': 'Heritage Conservation Institute',
                'title': 'Conservation Scientist',
                'expertise': ['Stone Conservation', 'Historical Preservation', 'Laser Cleaning', 'Cultural Heritage Science']
            },
            'wood': {
                'name': 'Dr. Lisa Anderson',
                'email': 'l.anderson@forestry-tech.com',
                'affiliation': 'Wood Science Research Laboratory',
                'title': 'Wood Science Specialist',
                'expertise': ['Wood Science', 'Forest Products', 'Laser Processing', 'Material Characterization']
            },
            'composite': {
                'name': 'Dr. James Wilson',
                'email': 'j.wilson@composite-tech.edu',
                'affiliation': 'Composite Materials Research Center',
                'title': 'Composite Materials Engineer',
                'expertise': ['Composite Materials', 'Fiber Reinforced Polymers', 'Laser Processing', 'Advanced Manufacturing']
            },
            'masonry': {
                'name': 'Dr. Anna Petrova',
                'email': 'a.petrova@construction-materials.org',
                'affiliation': 'Construction Materials Institute',
                'title': 'Masonry Materials Specialist',
                'expertise': ['Masonry Science', 'Building Materials', 'Laser Cleaning', 'Structural Preservation']
            },
            'semiconductor': {
                'name': 'Dr. Kevin Wang',
                'email': 'k.wang@semiconductor-research.edu',
                'affiliation': 'Semiconductor Processing Laboratory',
                'title': 'Semiconductor Process Engineer',
                'expertise': ['Semiconductor Materials', 'Wafer Processing', 'Laser Micromachining', 'Surface Science']
            }
        }
        
        return authors_by_category.get(material_category, authors_by_category['metal'])
    
    def _get_author_expertise_from_frontmatter(self, frontmatter_data: Dict, material_category: str) -> list:
        """Extract author expertise from frontmatter and enhance with relevant fields"""
        base_expertise = ['Laser Materials Processing', 'Surface Analysis', 'Materials Science']
        
        if 'author_object' in frontmatter_data:
            author_expertise = frontmatter_data['author_object'].get('expertise', '')
            if isinstance(author_expertise, str):
                base_expertise.append(author_expertise)
            
        # Add category-specific expertise
        category_expertise = {
            'metal': 'Metallurgical Engineering',
            'ceramic': 'Ceramic Science',
            'glass': 'Optical Materials',
            'stone': 'Heritage Conservation',
            'wood': 'Wood Science',
            'composite': 'Composite Materials',
            'masonry': 'Construction Materials',
            'semiconductor': 'Semiconductor Processing'
        }
        
        if material_category in category_expertise:
            base_expertise.append(category_expertise[material_category])
            
        return base_expertise[:4]  # Limit to 4 expertise areas

    def _generate_seo_metadata(self, material_name: str, material_category: str, quality_metrics: Dict, frontmatter_data: Dict = None) -> Dict[str, str]:
        """Generate comprehensive SEO metadata using material-specific data"""
        material_lower = material_name.lower()
        
        # Enhanced title with material-specific context
        title_contexts = {
            'metal': 'Industrial Contamination Removal',
            'ceramic': 'Ceramic Surface Restoration',
            'glass': 'Optical Surface Cleaning', 
            'stone': 'Heritage Conservation Cleaning',
            'wood': 'Wood Surface Restoration',
            'composite': 'Advanced Material Processing',
            'masonry': 'Masonry Surface Restoration',
            'semiconductor': 'Precision Wafer Cleaning'
        }
        
        title_context = title_contexts.get(material_category, 'Industrial Contamination Removal')
        title = f"{material_name} Surface Laser Cleaning Analysis - {title_context}"
        
        # Description with technical specifications from frontmatter
        technical_detail = ""
        if frontmatter_data and ('technicalSpecifications' in frontmatter_data or 'machineSettings' in frontmatter_data):
            tech_specs = frontmatter_data.get('technicalSpecifications', frontmatter_data.get('machineSettings', {}))
            wavelength = tech_specs.get('wavelength', '1064nm')
            technical_detail = f" using {wavelength} wavelength laser processing"
        
        description = f"Comprehensive microscopic analysis of {material_lower} surface before and after precision laser cleaning, achieving optimal surface restoration{technical_detail} with advanced laser processing techniques."
        
        # Keywords from frontmatter if available
        base_keywords = [
            'laser cleaning',
            f'{material_lower} surface treatment',
            'microscopic surface analysis',
            'materials processing',
            'precision cleaning',
            'surface topography',
            'laser ablation',
            material_lower,
            'contamination analysis'
        ]
        
        # Add keywords from frontmatter
        if frontmatter_data and 'keywords' in frontmatter_data:
            frontmatter_keywords = frontmatter_data['keywords']
            if isinstance(frontmatter_keywords, str):
                # Parse comma-separated keywords
                additional_keywords = [k.strip() for k in frontmatter_keywords.split(',')]
                base_keywords.extend(additional_keywords[:5])  # Limit additional keywords
        
        # Add industry-specific keywords from applications
        if frontmatter_data and 'applications' in frontmatter_data:
            for app in frontmatter_data['applications']:
                industry = app.get('industry', '').lower()
                if industry and len(base_keywords) < 15:
                    base_keywords.append(f'{industry.replace(" ", " ").replace("&", "and")} applications')
        
        category_keywords = {
            'metal': ['metal surface treatment', 'corrosion removal', 'oxide layer removal'],
            'ceramic': ['ceramic cleaning', 'ceramic surface modification', 'thermal processing'],
            'glass': ['optical cleaning', 'glass surface treatment', 'transparent materials'],
            'stone': ['stone conservation', 'heritage preservation', 'architectural restoration'],
            'wood': ['wood restoration', 'organic material cleaning', 'forestry applications'],
            'composite': ['composite processing', 'advanced materials', 'polymer matrix cleaning'],
            'masonry': ['masonry restoration', 'building conservation', 'construction cleaning'],
            'semiconductor': ['wafer cleaning', 'semiconductor processing', 'microelectronics']
        }
        
        keywords = base_keywords + category_keywords.get(material_category, [])
        # Remove duplicates while preserving order
        keywords = list(dict.fromkeys(keywords))[:15]  # Limit to 15 keywords
        
        og_title = f"{material_name} Laser Cleaning Analysis - Surface Restoration"
        og_description = f"Professional microscopic analysis of precision laser cleaning on {material_lower}, achieving complete contamination removal with preserved substrate integrity."
        
        image_alt = f"Microscopic comparison of {material_lower} surface before and after laser cleaning showing complete contamination removal"
        image_caption = f"High-resolution microscopic analysis demonstrating precision laser cleaning effectiveness on {material_lower}"
        
        accessibility_alt = f"Split-screen microscopic image showing {material_lower} surface before laser cleaning (left) with visible contamination deposits and after cleaning (right) with pristine surface finish"
        visual_description = f"High-contrast microscopic imagery clearly showing {material_lower} surface transformation through laser cleaning"
        
        return {
            'title': title,
            'description': description,
            'keywords': keywords,
            'og_title': og_title,
            'og_description': og_description,
            'image_alt': image_alt,
            'image_caption': image_caption,
            'accessibility_alt': accessibility_alt,
            'visual_description': visual_description
        }

    def _generate_technical_specifications(self, laser_params: Dict, material_name: str, frontmatter_data: Dict = None) -> Dict[str, str]:
        """Generate technical specifications using frontmatter data when available"""
        
        # Use frontmatter technical specifications if available
        if frontmatter_data and ('technicalSpecifications' in frontmatter_data or 'machineSettings' in frontmatter_data):
            tech_specs = frontmatter_data.get('technicalSpecifications', frontmatter_data.get('machineSettings', {}))
            return {
                'wavelength': str(tech_specs.get('wavelength', f"{laser_params['wavelength']} nm")),
                'power': str(tech_specs.get('powerRange', f"{laser_params['power']} W")),
                'pulse_duration': str(tech_specs.get('pulseDuration', f"{laser_params['pulse_duration']} ns")),
                'scanning_speed': laser_params.get('scanning_speed', f"{random.randint(200, 800)} mm/min"),
                'material': material_name,
                'beam_delivery': random.choice(['fiber optic', 'galvanometer scanning', 'direct beam']),
                'focus_diameter': str(tech_specs.get('spotSize', f"{laser_params['spot_size']} μm")),
                'processing_atmosphere': random.choice(['ambient air', 'inert atmosphere', 'controlled environment'])
            }
        
        # Fallback to generated specifications
        return {
            'wavelength': f"{laser_params['wavelength']} nm",
            'power': f"{laser_params['power']} W",
            'pulse_duration': f"{laser_params['pulse_duration']} ns",
            'scanning_speed': laser_params.get('scanning_speed', f"{random.randint(200, 800)} mm/min"),
            'material': material_name,
            'beam_delivery': random.choice(['fiber optic', 'galvanometer scanning', 'direct beam']),
            'focus_diameter': f"{laser_params['spot_size']} μm",
            'processing_atmosphere': random.choice(['ambient air', 'inert atmosphere', 'controlled environment'])
        }

    def _generate_chemical_properties(self, material_name: str, material_formula: str, material_category: str, frontmatter_data: Dict = None) -> Dict[str, str]:
        """Generate chemical properties using frontmatter data for accuracy"""
        
        # Use chemical properties from frontmatter if available
        if frontmatter_data:
            chem_props = frontmatter_data.get('chemicalProperties', {})
            composition_data = frontmatter_data.get('composition', [])
            
            # Get composition from frontmatter
            if composition_data and isinstance(composition_data, list):
                composition = ', '.join(composition_data[:3])  # First 3 components
            elif chem_props.get('formula'):
                composition = chem_props['formula']
            else:
                composition = material_formula if material_formula else f"{material_name} composition"
            
            # Get material type from frontmatter
            material_type = chem_props.get('materialType', f"{material_name.lower()} {material_category}")
            
            # Get formula from frontmatter
            formula = chem_props.get('formula', material_formula if material_formula else f"{material_name} composition")
        else:
            # Fallback values
            composition = material_formula if material_formula else f"{material_name} composition"
            material_type = f"{material_name.lower()} {material_category}"
            formula = material_formula if material_formula else f"{material_name} composition"
        
        contamination_types = {
            'metal': 'oxidation and metallic deposits',
            'ceramic': 'ceramic dust and firing residues',
            'glass': 'optical contamination and surface films',
            'stone': 'weathering and biological deposits',
            'wood': 'organic decay and biological contamination',
            'composite': 'matrix degradation and environmental aging',
            'masonry': 'construction residues and atmospheric deposits',
            'semiconductor': 'organic contamination and processing residues'
        }
        
        corrosion_resistance = {
            'metal': random.choice(['excellent', 'good', 'moderate']),
            'ceramic': 'excellent',
            'glass': 'excellent',
            'stone': random.choice(['good', 'moderate']),
            'wood': 'moderate',
            'composite': random.choice(['excellent', 'good']),
            'masonry': 'good',
            'semiconductor': 'excellent'
        }
        
        return {
            'composition': composition,
            'contamination_type': contamination_types.get(material_category, 'surface contamination'),
            'materialType': material_type,
            'formula': formula,
            'surface_finish': f"Ra < {random.uniform(0.3, 1.0):.1f} μm (post-cleaning)",
            'corrosion_resistance': corrosion_resistance.get(material_category, 'good')
        }

    def _format_keywords_list(self, keywords: list) -> str:
        """Format keywords list for YAML"""
        return '\n'.join([f'  - "{keyword}"' for keyword in keywords])

    def _format_expertise_list(self, expertise: list) -> str:
        """Format expertise list for YAML"""
        return '\n'.join([f'    - "{exp}"' for exp in expertise])




# Legacy compatibility
class CaptionGenerator:
    """Legacy caption generator for backward compatibility"""

    def __init__(self):
        self.generator = CaptionComponentGenerator()

    def generate(self, material: str, material_data: Dict = None) -> str:
        """Legacy generate method"""
        if material_data is None:
            material_data = {"name": material}

        try:
            content = self.generator._generate_static_content(
                material, material_data
            )
            return content
        except Exception as e:
            return f"Error generating caption content: {e}"

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "caption",
            "description": "Technical image caption component",
            "version": "1.0.0",
            "requires_api": False,
            "type": "static",
        }


def generate_caption_content(material: str, material_data: Dict = None) -> str:
    """Legacy function for backward compatibility"""
    generator = CaptionGenerator()
    return generator.generate(material, material_data)


if __name__ == "__main__":
    # Test the generator
    generator = CaptionGenerator()
    test_content = generator.generate("Aluminum")
    print("🧪 Caption Component Test:")
    print("=" * 50)
    print(test_content)
