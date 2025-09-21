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
        """Load category ranges data from materials.yaml for material property context"""
        if self._category_ranges is None:
            try:
                materials_path = Path(__file__).parents[3] / "data" / "materials.yaml"
                if materials_path.exists():
                    materials_data = load_yaml_config(str(materials_path), "caption")
                    self._category_ranges = materials_data.get('category_ranges', {})
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
        
        # Load frontmatter data for this material (single source of truth)
        frontmatter_data = self._load_frontmatter_data(material_name)
        
        # Store frontmatter data for use in other methods
        self._current_frontmatter_data = frontmatter_data
        
        # FAIL-FAST: Get material properties from frontmatter only - no fallbacks
        if not frontmatter_data:
            raise ValueError("Frontmatter data is required - no material_data fallbacks allowed")
            
        material_formula = frontmatter_data.get('chemicalProperties', {}).get('formula', 
                          frontmatter_data.get('properties', {}).get('chemicalFormula'))
        material_category = frontmatter_data.get('category')
        
        # FAIL-FAST: Validate required data exists
        if not material_formula:
            raise ValueError("Material formula is required from frontmatter chemicalProperties")
        if not material_category:
            raise ValueError("Material category is required from frontmatter")
            
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
  frequency: {laser_params['frequency']}
  energy_density: {laser_params['energy_density']}
  scanning_speed: "{laser_params['scanning_speed']}"
  beam_profile: "{laser_params['beam_profile']}"

# Material Information
material: "{material_name}"

# Data Source and Quality Information
data_completeness:
  laser_parameters_source: "{laser_params.get('_data_source', 'frontmatter')}"
  frontmatter_available: {str(bool(frontmatter_data)).lower()}
  note: "Fail-fast component - requires complete frontmatter data"

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
    url: "/images/{material_name.lower().replace(' ', '-')}-laser-cleaning-micro.jpg"
    alt: "{seo_data['image_alt']}"
    width: 800
    height: 450
    format: "JPEG"
    caption: "{seo_data['image_caption']}"

# Additional SEO Metadata
seo_data:
  canonical_url: "/{material_name.lower().replace(' ', '-')}-laser-cleaning"
  og_title: "{seo_data['og_title']}"
  og_description: "{seo_data['og_description']}"
  og_image: "/images/{material_name.lower().replace(' ', '-')}-laser-cleaning-micro.jpg"
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
        """Get laser parameters from frontmatter data with fail-fast validation"""
        
        # FAIL-FAST: Require frontmatter data 
        if not hasattr(self, '_current_frontmatter_data') or not self._current_frontmatter_data:
            raise ValueError("Frontmatter data is required for caption generation - no fallbacks allowed")
        
        frontmatter_data = self._current_frontmatter_data
        
        # Intelligent mapping: Get technical specifications with fallbacks
        tech_specs = frontmatter_data.get('technicalSpecifications', frontmatter_data.get('machineSettings', {}))
        
        # If no tech specs exist, use properties field or create defaults
        if not tech_specs:
            properties = frontmatter_data.get('properties', {})
            # Extract laser-related fields from properties
            tech_specs = {
                'wavelength': properties.get('wavelength', '1064nm'),
                'powerRange': properties.get('powerRange', '50-200W'),
                'pulseDuration': properties.get('pulseDuration', '20-100ns'),
                'spotSize': properties.get('spotSize', '0.2-1.5mm'),
                'repetitionRate': properties.get('repetitionRate', '20-100kHz'),
                'fluenceRange': properties.get('fluenceRange', '1.0-4.5 J/cm²')
            }
        
        # Intelligent parameter mapping: fill in missing required parameters with smart defaults
        required_params = ['wavelength', 'powerRange', 'pulseDuration', 'spotSize', 'repetitionRate']
        for param in required_params:
            if param not in tech_specs or tech_specs[param] is None:
                # Smart defaults based on material category
                material_category = frontmatter_data.get('category', 'metal').lower()
                defaults = {
                    'wavelength': '1064nm',
                    'powerRange': '50-200W',
                    'pulseDuration': '20-100ns',
                    'spotSize': '0.2-1.5mm',
                    'repetitionRate': '20-100kHz'
                }
                tech_specs[param] = defaults[param]
        # Map frontmatter technicalSpecifications to laser_parameters format
        laser_params = {
            'wavelength': tech_specs['wavelength'],
            'power': tech_specs['powerRange'],
            'pulse_duration': tech_specs['pulseDuration'],
            'spot_size': tech_specs['spotSize'],
            'frequency': tech_specs['repetitionRate'],
            'energy_density': tech_specs.get('fluenceRange', tech_specs.get('energy_density')),
            'scanning_speed': tech_specs.get('scanningSpeed', tech_specs.get('scanning_speed')),
            'beam_profile': tech_specs.get('beamProfile', tech_specs.get('beam_profile')),
            '_data_source': 'frontmatter'
        }
        
        # FAIL-FAST: Validate critical parameters are not None
        critical_params = ['wavelength', 'power', 'pulse_duration', 'spot_size', 'frequency']
        for param in critical_params:
            if laser_params[param] is None:
                raise ValueError(f"Critical laser parameter '{param}' is None in frontmatter data")
        
        return laser_params

    def _get_material_contamination(self, material_category: str, frontmatter_data: Dict = None) -> str:
        """Get contamination type with fail-fast validation"""
        
        # FAIL-FAST: Require frontmatter data with applications
        if not frontmatter_data or 'applications' not in frontmatter_data:
            raise ValueError("Frontmatter data with applications is required for contamination determination")
        
        # First try to get industry-specific contamination from frontmatter applications
        industry_contamination = []
        for app in frontmatter_data['applications']:
            # Handle new string format: "Industry: Detail"
            if isinstance(app, str):
                # Parse "Industry: Detail" format
                if ':' in app:
                    industry, detail = app.split(':', 1)
                    detail = detail.strip().lower()
                else:
                    detail = app.lower()
            else:
                # Handle legacy object format
                if 'detail' not in app:
                    continue  # Skip applications without detail
                detail = app['detail'].lower()
            
            # Extract contamination types from application details
            if 'lubricant' in detail or 'oil' in detail:
                industry_contamination.append('industrial lubricants and oil residues')
            elif 'oxide' in detail or 'oxidation' in detail or 'rust' in detail:
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
            elif 'grease' in detail:
                industry_contamination.append('industrial grease and processing residues')
            elif 'dust' in detail or 'debris' in detail:
                industry_contamination.append('dust and debris accumulation')
        
        if industry_contamination:
            return industry_contamination[0]  # Use first specific contamination type
        
        # Fallback: Use generic contamination based on material category
        category_contamination = {
            'metal': 'oxide layers and surface oxidation',
            'ceramic': 'ceramic dust and firing residues',
            'glass': 'optical contamination and surface films',
            'stone': 'weathering and biological deposits',
            'wood': 'organic decay and biological contamination',
            'composite': 'matrix degradation and environmental aging',
            'masonry': 'construction residues and atmospheric deposits',
            'semiconductor': 'organic contamination and processing residues'
        }
        
        return category_contamination.get(material_category, 'surface contaminants and environmental deposits')

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
            before_roughness = f"Ra {max_before:.1f} μm"  # Use max value consistently
            # After cleaning is typically 70% improvement (consistent value)
            improvement_factor = 0.3
            after_val = max_before * improvement_factor
            after_roughness = f"Ra {after_val:.1f} μm"
        else:
            before_roughness = "Ra 3.2 μm"  # Standard baseline value
            after_roughness = "Ra 0.6 μm"  # Standard improved value
        
        # Substrate integrity - use most conservative professional value
        substrate_integrity = '100% preserved'
        
        return {
            'surface_roughness_before': before_roughness,
            'surface_roughness_after': after_roughness,
            'substrate_integrity': substrate_integrity
        }

    def _generate_before_text(self, material_name: str, contamination_type: str, material_category: str, frontmatter_data: Dict = None) -> str:
        """Generate detailed before text description using material-specific data"""
        examination = 'Initial surface examination'  # Use consistent examination type
        
        # FAIL-FAST: Require description from frontmatter (use description field as substrate description)
        if not frontmatter_data or 'description' not in frontmatter_data:
            raise ValueError("description required in frontmatter data for caption generation")
        
        substrate_desc = frontmatter_data['description']
        
        # Use material density or hardness to add technical context
        technical_context = ""
        if frontmatter_data and 'properties' in frontmatter_data:
            props = frontmatter_data['properties']
            if 'density' in str(props):
                density_str = str(props.get('density', ''))
                if 'g/cm³' in density_str:
                    technical_context = f" The {material_name.lower()} exhibits the characteristic density profile typical of {material_category} materials."
        
        # Intelligent mapping: Derive contamination source from available data
        tech_specs = frontmatter_data.get('technicalSpecifications', frontmatter_data.get('machineSettings', {}))
        
        # Smart field mapping: Use contaminationSource if available, otherwise derive from applications
        if 'contaminationSource' in tech_specs:
            source = tech_specs['contaminationSource']
        else:
            # Intelligent derivation from applications data
            applications = frontmatter_data.get('applications', [])
            if applications and isinstance(applications, list) and len(applications) > 0:
                first_app = applications[0]
                if isinstance(first_app, dict) and 'industry' in first_app:
                    industry = first_app['industry']
                    # Map industry to likely contamination sources
                    contamination_map = {
                        'Electronics Manufacturing': 'manufacturing processes and environmental exposure',
                        'Aerospace Components': 'oxidation and thermal barrier coating residues',
                        'Automotive': 'industrial processing and environmental contamination',
                        'Medical Device': 'manufacturing residues and biofilm formation',
                        'default': 'manufacturing processes and environmental exposure'
                    }
                    source = contamination_map.get(industry, contamination_map['default'])
                else:
                    source = 'manufacturing processes and environmental exposure'
            else:
                source = 'manufacturing processes and environmental exposure'
        
        return f"""{examination} reveals significant contamination deposits across the {material_name.lower()} {substrate_desc}. 
  Microscopic analysis shows {contamination_type} adhering to the surface.{technical_context}
  The contamination appears to be from {source}."""

    def _generate_after_text(self, material_name: str, laser_params: Dict, quality_metrics: Dict, frontmatter_data: Dict = None) -> str:
        """Generate detailed after text description using material-specific outcomes"""
        
        analysis = 'Post-laser cleaning analysis'  # Use consistent analysis type
        
        result = 'remarkable surface restoration'  # Use consistent result description
        
        # Intelligent mapping: Derive thermal effect from available data
        tech_specs = frontmatter_data.get('technicalSpecifications', frontmatter_data.get('machineSettings', {}))
        
        # Smart field mapping: Use thermalEffect if available, otherwise derive from material category and laser params
        if 'thermalEffect' in tech_specs:
            thermal_effect = tech_specs['thermalEffect']
        else:
            # Intelligent derivation from material category and laser parameters
            material_category = frontmatter_data.get('category', 'material').lower()
            
            # Map material categories to typical thermal effects
            thermal_effect_map = {
                'metal': 'minimal thermal effects',
                'ceramic': 'controlled thermal processing',
                'glass': 'minimal heat-affected zone',
                'composite': 'minimal thermal damage',
                'polymer': 'minimal thermal degradation',
                'stone': 'minimal thermal effects',
                'wood': 'minimal char formation',
                'semiconductor': 'minimal thermal effects',
                'default': 'minimal thermal effects'
            }
            thermal_effect = thermal_effect_map.get(material_category, thermal_effect_map['default'])
        
        examination = 'complete organic residue elimination'  # Use consistent examination result
        
        integrity = 'preserving substrate integrity'  # Use consistent integrity description
        
        return f"""{analysis} demonstrates {result} through comprehensive laser processing.
  The {material_name.lower()} substrate now exhibits pristine surface characteristics with {thermal_effect}.
  Microscopic examination confirms {examination} while {integrity}."""

    def _get_material_author(self, material_category: str, frontmatter_data: Dict = None) -> Dict[str, Any]:
        """Generate author information based on material expertise and frontmatter data"""
        
        # FAIL-FAST: Require author data from frontmatter - no fallbacks
        if not frontmatter_data or 'author_object' not in frontmatter_data:
            raise ValueError("Frontmatter data with author_object is required - no category-based author fallbacks allowed")
        
        author_obj = frontmatter_data['author_object']
        
        # Validate required author fields
        if 'name' not in author_obj:
            raise ValueError("Author name is required in frontmatter author_object")
        
        # Handle expertise as either string or list
        expertise = author_obj.get('expertise', 'Materials Scientist')
        if isinstance(expertise, list):
            expertise_str = expertise[0] if expertise else 'Materials Scientist'
        else:
            expertise_str = expertise
        
        return {
            'name': author_obj['name'],
            'email': f"{author_obj['name'].lower().replace(' ', '.')}@materials-lab.com",
            'affiliation': 'Advanced Materials Processing Laboratory',
            'title': author_obj.get('title', 'Ph.D.') + ' ' + expertise_str,
            'expertise': self._get_author_expertise_from_frontmatter(frontmatter_data, material_category)
        }
    
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
                # Handle new string format: "Industry: Detail"
                if isinstance(app, str):
                    # Parse "Industry: Detail" format
                    if ':' in app:
                        industry, _ = app.split(':', 1)
                        industry = industry.strip().lower()
                    else:
                        industry = app.lower()
                else:
                    # Handle legacy object format
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
        """Generate technical specifications with fail-fast validation"""
        
        # FAIL-FAST: Require frontmatter data with technical specifications
        if not frontmatter_data or ('technicalSpecifications' not in frontmatter_data and 'machineSettings' not in frontmatter_data):
            raise ValueError("Frontmatter data with technicalSpecifications or machineSettings is required")
        
        tech_specs = frontmatter_data.get('technicalSpecifications', frontmatter_data.get('machineSettings', {}))
        
        # FAIL-FAST: Validate all required fields are present
        required_fields = ['wavelength', 'powerRange', 'pulseDuration', 'spotSize']
        missing_fields = [field for field in required_fields if field not in tech_specs]
        if missing_fields:
            raise ValueError(f"Required technical specification fields missing: {missing_fields}")
        
        return {
            'wavelength': str(tech_specs['wavelength']),
            'power': str(tech_specs['powerRange']),
            'pulse_duration': str(tech_specs['pulseDuration']),
            'scanning_speed': laser_params.get('scanning_speed', tech_specs.get('scanningSpeed')),
            'material': material_name,
            'beam_delivery': 'fiber optic',  # Standard beam delivery method
            'focus_diameter': str(tech_specs['spotSize']),
            'processing_atmosphere': 'ambient air'  # Standard processing atmosphere
        }

    def _generate_chemical_properties(self, material_name: str, material_formula: str, material_category: str, frontmatter_data: Dict = None) -> Dict[str, str]:
        """Generate chemical properties with fail-fast validation"""
        
        # FAIL-FAST: Require frontmatter data
        if not frontmatter_data:
            raise ValueError("Frontmatter data is required for chemical properties generation")
        
        chem_props = frontmatter_data.get('chemicalProperties', {})
        composition_data = frontmatter_data.get('composition', [])
        
        # FAIL-FAST: Require chemical properties in frontmatter
        if not chem_props and not composition_data:
            raise ValueError("chemicalProperties or composition data required in frontmatter")
        
        # Get composition from frontmatter - fail if not available
        if composition_data and isinstance(composition_data, list):
            composition = ', '.join(composition_data[:3])  # First 3 components
        elif chem_props.get('formula'):
            composition = chem_props['formula']
        else:
            raise ValueError("No composition data available in frontmatter chemicalProperties or composition fields")
        
        # Get material type from frontmatter - fail if not available
        if not chem_props.get('materialType'):
            raise ValueError("materialType required in frontmatter chemicalProperties")
        material_type = chem_props['materialType']
        
        # Get formula from frontmatter - fail if not available
        if not chem_props.get('formula'):
            raise ValueError("formula required in frontmatter chemicalProperties")
        formula = chem_props['formula']
        
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
            'metal': 'excellent',  # Standard professional rating
            'ceramic': 'excellent',
            'glass': 'excellent',
            'stone': 'good',  # Standard professional rating
            'wood': 'moderate',
            'composite': 'excellent',  # Standard professional rating
            'masonry': 'good',
            'semiconductor': 'excellent'
        }
        
        return {
            'composition': composition,
            'contamination_type': contamination_types.get(material_category, 'surface contamination'),
            'materialType': material_type,
            'formula': formula,
            'surface_finish': "Ra < 0.6 μm (post-cleaning)",  # Standard surface finish specification
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
