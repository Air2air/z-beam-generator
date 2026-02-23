"""
Laser Properties Researcher

Specialized researcher for laser-specific scientific data of contamination patterns.
Researches optical, thermal, and removal characteristics for laser cleaning applications.

Author: AI Assistant
Date: November 25, 2025
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from generation.config.config_loader import ProcessingConfig
from shared.api.client import GenerationRequest
from shared.exceptions import GenerationError

logger = logging.getLogger(__name__)


@dataclass
class ContaminationResearchSpec:
    """Specification for contamination research."""
    pattern_id: str
    research_type: str
    material_context: Optional[str] = None
    context: Optional[Dict] = None


@dataclass
class ContaminationResearchResult:
    """Result from contamination research."""
    pattern_id: str
    data: Dict = field(default_factory=dict)
    confidence: float = 0.0
    source: str = "ai_research"
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    @property
    def success(self) -> bool:
        return self.error is None and bool(self.data)


class LaserPropertiesResearcher:
    """
    Researcher for laser-specific contamination properties.
    
    Researches:
    - Optical properties (absorption, reflectivity, refractive index)
    - Thermal properties (ablation thresholds, decomposition temps, conductivity)
    - Removal characteristics (mechanisms, byproducts, efficiency)
    - Layer properties (thickness ranges, penetration depth, adhesion)
    - Laser parameter recommendations (wavelength, fluence, scan speed)
    - Safety data (fumes, ventilation, PPE requirements)
    - Material-specific selectivity ratios
    
    Usage:
        researcher = LaserPropertiesResearcher(api_client)
        result = researcher.research(
            pattern_id="rust_oxidation",
            research_spec=ContaminationResearchSpec(
                pattern_id="rust_oxidation",
                research_type="optical_properties",
                material_context="Steel"
            )
        )
    """
    
    # Research types supported by this researcher
    SUPPORTED_RESEARCH_TYPES = {
        'optical_properties',        # Absorption, reflectivity, refractive index
        'thermal_properties',        # Ablation thresholds, decomposition temps
        'removal_characteristics',   # Mechanisms, byproducts, efficiency
        'layer_properties',          # Thickness, penetration depth, adhesion
        'laser_parameters',          # Recommended wavelength, fluence, etc.
        'safety_data',               # Fumes, exposure limits, PPE
        'selectivity_ratios',        # Material-specific selectivity
        'complete_profile'           # All laser properties in one call
    }
    
    # Common laser wavelengths (nm)
    COMMON_WAVELENGTHS = [1064, 532, 355, 266, 1550]  # Nd:YAG, doubled, tripled, quadrupled, fiber
    
    def __init__(self, api_client: Any):
        """
        Initialize laser properties researcher.
        
        Args:
            api_client: API client for AI research (Grok, Gemini, etc.)
        
        Raises:
            ValueError: If api_client is None
        """
        if api_client is None:
            raise ValueError("API client required for laser properties research")
        self.api_client = api_client
        from domains.contaminants.data_loader_v2 import PatternDataLoader
        self.loader = PatternDataLoader()
        self.logger = logging.getLogger(__name__)
        self.config = ProcessingConfig()
        self.high_confidence_threshold = float(
            self.config.get_required_config('constants.laser_properties_researcher.high_confidence_threshold')
        )
        self.acceptable_confidence_threshold = float(
            self.config.get_required_config('constants.laser_properties_researcher.acceptable_confidence_threshold')
        )
        self.optical_max_tokens = int(
            self.config.get_required_config('constants.laser_properties_researcher.optical_max_tokens')
        )
        self.thermal_max_tokens = int(
            self.config.get_required_config('constants.laser_properties_researcher.thermal_max_tokens')
        )
        self.removal_max_tokens = int(
            self.config.get_required_config('constants.laser_properties_researcher.removal_max_tokens')
        )
        self.parameters_max_tokens = int(
            self.config.get_required_config('constants.laser_properties_researcher.parameters_max_tokens')
        )
        self.safety_max_tokens = int(
            self.config.get_required_config('constants.laser_properties_researcher.safety_max_tokens')
        )
        self.selectivity_max_tokens = int(
            self.config.get_required_config('constants.laser_properties_researcher.selectivity_max_tokens')
        )
    
    def research(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict] = None
    ) -> ContaminationResearchResult:
        """
        Research laser-specific properties for contamination pattern.
        
        Args:
            pattern_id: Pattern identifier (rust_oxidation, copper_patina, etc.)
            research_spec: Research specification with research_type
            context: Additional context (material, environment, etc.)
        
        Returns:
            ContaminationResearchResult with laser-specific data
        
        Raises:
            GenerationError: If research fails critically
        """
        # Validate inputs
        if not pattern_id:
            raise GenerationError("Pattern ID required for laser properties research")
        
        if research_spec.research_type not in self.SUPPORTED_RESEARCH_TYPES:
            raise GenerationError(
                f"Unsupported research type: {research_spec.research_type}. "
                f"Supported: {self.SUPPORTED_RESEARCH_TYPES}"
            )
        
        self.logger.info(
            f"🔬 Researching {research_spec.research_type} for pattern: {pattern_id}"
        )
        
        # Load existing pattern data from Contaminants.yaml
        existing_pattern = self._load_existing_pattern(pattern_id)
        if not existing_pattern:
            raise GenerationError(
                f"Pattern '{pattern_id}' not found in Contaminants.yaml. "
                "Cannot research undefined pattern."
            )
        
        # Route to specific research method
        if research_spec.research_type == 'complete_profile':
            return self._research_complete_profile(pattern_id, research_spec, context)
        elif research_spec.research_type == 'optical_properties':
            return self._research_optical_properties(pattern_id, research_spec, context)
        elif research_spec.research_type == 'thermal_properties':
            return self._research_thermal_properties(pattern_id, research_spec, context)
        elif research_spec.research_type == 'removal_characteristics':
            return self._research_removal_characteristics(pattern_id, research_spec, context)
        elif research_spec.research_type == 'layer_properties':
            return self._research_layer_properties(pattern_id, research_spec, context)
        elif research_spec.research_type == 'laser_parameters':
            return self._research_laser_parameters(pattern_id, research_spec, context)
        elif research_spec.research_type == 'safety_data':
            return self._research_safety_data(pattern_id, research_spec, context)
        elif research_spec.research_type == 'selectivity_ratios':
            return self._research_selectivity_ratios(pattern_id, research_spec, context)
        else:
            raise GenerationError(f"Research type not implemented: {research_spec.research_type}")
    
    def _research_optical_properties(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict]
    ) -> ContaminationResearchResult:
        """Research optical properties at common laser wavelengths."""
        
        existing_pattern = self._load_existing_pattern(pattern_id)
        
        prompt = f"""You are a laser cleaning scientist researching optical properties of contamination.

CONTAMINATION PATTERN: {existing_pattern['name']}
Scientific Name: {existing_pattern.get('scientific_name', 'N/A')}
Chemical Formula: {existing_pattern.get('chemical_formula', 'N/A')}
Category: {existing_pattern.get('category', 'unknown')}

RESEARCH TASK:
Provide QUANTITATIVE optical properties for laser cleaning applications at common wavelengths.

Required data structure (provide realistic values):
```yaml
absorption_coefficient:  # cm⁻¹ at each wavelength
  wavelength_1064nm: <value>  # Nd:YAG fundamental
  wavelength_532nm: <value>   # Frequency-doubled
  wavelength_355nm: <value>   # Tripled (UV)
reflectivity:  # Fraction (0.0 to 1.0)
  wavelength_1064nm: <value>
  wavelength_532nm: <value>
  wavelength_355nm: <value>
refractive_index:  # At 1064nm (most common)
  real_part: <value>
  imaginary_part: <value>
transmission_depth: <value>  # μm - how deep light penetrates
```

REQUIREMENTS:
1. Base values on known optical properties of {existing_pattern.get('chemical_formula', 'the compound')}
2. Higher absorption = more efficient laser coupling = easier removal
3. UV wavelengths (355nm) typically have higher absorption than IR (1064nm)
4. Reflectivity + absorption + transmission = 1.0 (energy conservation)
5. Provide realistic engineering values (not placeholder zeros)
6. Include brief explanation of wavelength selection for this contaminant

Provide ONLY the YAML structure with realistic numerical values and a 2-sentence recommendation."""

        try:
            from generation.config.dynamic_config import DynamicConfig
            dynamic_config = DynamicConfig()
            
            request = GenerationRequest(
                prompt=prompt,
                temperature=dynamic_config.calculate_temperature('research'),
                max_tokens=self.optical_max_tokens
            )
            response = self.api_client.generate(request)
            
            # Parse YAML response
            data = self._parse_yaml_response(response.content)
            
            # Validate structure
            required_fields = ['absorption_coefficient', 'reflectivity']
            if not all(field in data for field in required_fields):
                raise ValueError(f"Missing required fields: {required_fields}")
            
            # Calculate confidence based on data completeness
            confidence = self._calculate_optical_confidence(data)
            
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data=data,
                confidence=confidence,
                source="ai_research",
                metadata={
                    'research_type': 'optical_properties',
                    'pattern_name': existing_pattern['name'],
                    'chemical_formula': existing_pattern.get('chemical_formula')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to research optical properties: {e}")
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data={},
                confidence=0.0,
                source="ai_research",
                error=str(e)
            )
    
    def _research_thermal_properties(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict]
    ) -> ContaminationResearchResult:
        """Research thermal properties for laser ablation."""
        
        existing_pattern = self._load_existing_pattern(pattern_id)
        material_context = research_spec.material_context or "steel"
        
        prompt = f"""You are a laser cleaning scientist researching thermal ablation properties.

CONTAMINATION PATTERN: {existing_pattern['name']}
Chemical Formula: {existing_pattern.get('chemical_formula', 'N/A')}
Substrate Material: {material_context}

RESEARCH TASK:
Provide QUANTITATIVE thermal properties for laser ablation calculations.

Required data structure:
```yaml
ablation_threshold:  # J/cm² - minimum fluence to remove material
  wavelength_1064nm: <value>
  pulse_duration_10ns: <value>  # Nanosecond regime
  pulse_duration_100ns: <value>  # Longer pulse
decomposition_temperature: <value>  # °C - when material breaks down
vaporization_temperature: <value>  # °C - when material vaporizes
melting_point: <value>  # °C (if applicable)
thermal_conductivity: <value>  # W/m·K - heat transport
specific_heat: <value>  # J/kg·K - energy capacity
thermal_diffusivity: <value>  # mm²/s - heat spreading rate
heat_affected_zone_depth: <value>  # μm - typical HAZ at threshold fluence
```

REQUIREMENTS:
1. Ablation threshold should be ABOVE substrate damage threshold (selective removal)
2. Lower thermal conductivity = more localized heating = easier removal
3. Values should enable selective removal without substrate damage
4. Consider substrate is {material_context} with typical damage threshold 0.5-2 J/cm²
5. Provide realistic engineering values based on {existing_pattern.get('chemical_formula', 'the material')}

Provide ONLY the YAML with realistic values."""

        try:
            from generation.config.dynamic_config import DynamicConfig
            dynamic_config = DynamicConfig()
            
            request = GenerationRequest(
                prompt=prompt,
                temperature=dynamic_config.calculate_temperature('research'),
                max_tokens=self.thermal_max_tokens
            )
            response = self.api_client.generate(request)
            
            data = self._parse_yaml_response(response.content)
            
            # Validate critical fields
            if 'ablation_threshold' not in data:
                raise ValueError("Missing ablation_threshold - critical for process design")
            
            confidence = self._calculate_thermal_confidence(data)
            
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data=data,
                confidence=confidence,
                source="ai_research",
                metadata={
                    'research_type': 'thermal_properties',
                    'material_context': material_context
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to research thermal properties: {e}")
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data={},
                confidence=0.0,
                error=str(e)
            )
    
    def _research_removal_characteristics(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict]
    ) -> ContaminationResearchResult:
        """Research practical removal characteristics."""
        
        existing_pattern = self._load_existing_pattern(pattern_id)
        
        prompt = f"""You are a laser cleaning process engineer researching removal characteristics.

CONTAMINATION: {existing_pattern['name']}
Chemical Formula: {existing_pattern.get('chemical_formula', 'N/A')}

RESEARCH TASK:
Provide PRACTICAL removal data for process planning.

Required structure:
```yaml
primary_mechanism: "<thermal_ablation|photochemical|mechanical_spallation|hybrid>"
secondary_mechanisms:  # List any contributing mechanisms
  - <mechanism>
byproducts:  # What's created during removal
  - compound: "<chemical formula or name>"
    phase: "<gas|liquid|solid|plasma>"
    hazard_level: "<low|moderate|high>"
removal_efficiency:
  single_pass: <0.0-1.0>  # Fraction removed in one pass
  optimal_passes: <integer>  # Passes for complete removal
  diminishing_returns_after: <integer>  # When additional passes stop helping
surface_quality_after_removal:
  roughness_increase: "<none|minimal|moderate|significant>"
  color_change: "<yes|no>"
  residual_stress: "<compressive|tensile|none>"
damage_risk_to_substrate: "<low|medium|high>"
process_speed:
  typical_scan_speed_mm_s: <value>
  area_coverage_rate_cm2_min: <value>
```

REQUIREMENTS:
1. Base on laser-material interaction physics
2. Mechanism should match the contaminant's properties
3. Byproducts affect ventilation requirements
4. Efficiency affects process economics
5. Be realistic about multi-pass requirements

Provide ONLY the YAML with realistic values."""

        try:
            from generation.config.dynamic_config import DynamicConfig
            dynamic_config = DynamicConfig()
            
            request = GenerationRequest(
                prompt=prompt,
                temperature=dynamic_config.calculate_temperature('research'),
                max_tokens=self.removal_max_tokens
            )
            response = self.api_client.generate(request)
            
            data = self._parse_yaml_response(response.content)
            confidence = self._calculate_removal_confidence(data)
            
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data=data,
                confidence=confidence,
                source="ai_research",
                metadata={'research_type': 'removal_characteristics'}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to research removal characteristics: {e}")
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data={},
                confidence=0.0,
                error=str(e)
            )
    
    def _research_laser_parameters(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict]
    ) -> ContaminationResearchResult:
        """Research recommended laser parameters for operators."""
        
        existing_pattern = self._load_existing_pattern(pattern_id)
        material_context = research_spec.material_context or "steel"
        
        prompt = f"""You are a laser cleaning applications engineer creating operator guidance.

CONTAMINATION: {existing_pattern['name']}
Substrate: {material_context}

TASK: Provide START POINT laser parameters for operators.

Required structure:
```yaml
wavelength_preference:  # Ordered by effectiveness
  - <wavelength_nm>  # Primary recommendation
  - <wavelength_nm>  # Alternative
pulse_duration_range:
  min_ns: <value>
  max_ns: <value>
  recommended_ns: <value>
fluence_range:  # J/cm²
  min_j_cm2: <value>  # Below this: insufficient removal
  max_j_cm2: <value>  # Above this: substrate damage risk
  recommended_j_cm2: <value>  # Sweet spot
repetition_rate_khz:
  min: <value>
  max: <value>
  recommended: <value>
scan_speed_mm_s:
  min: <value>
  max: <value>
  recommended: <value>
spot_size_mm:
  min: <value>
  max: <value>
  recommended: <value>
overlap_percentage: <value>  # Pass overlap (0-90%)
beam_profile: "<gaussian|flat_top|donut>"
polarization: "<linear|circular|elliptical|any>"
safety_margin_factor: <value>  # Multiplier below damage threshold (e.g., 0.7 = 70% of damage threshold)
```

REQUIREMENTS:
1. Parameters must enable selective removal (contaminant removed, substrate intact)
2. Safety margin from substrate damage threshold
3. Consider {material_context} damage threshold ~0.5-2 J/cm²
4. Balance removal efficiency with substrate protection
5. Practical values for commercial systems

YAML only, with 1-sentence rationale."""

        try:
            from generation.config.dynamic_config import DynamicConfig
            dynamic_config = DynamicConfig()
            
            request = GenerationRequest(
                prompt=prompt,
                temperature=dynamic_config.calculate_temperature('research'),
                max_tokens=self.parameters_max_tokens
            )
            response = self.api_client.generate(request)
            
            data = self._parse_yaml_response(response.content)
            confidence = self._calculate_parameters_confidence(data)
            
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data=data,
                confidence=confidence,
                source="ai_research",
                metadata={
                    'research_type': 'laser_parameters',
                    'material_context': material_context
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to research laser parameters: {e}")
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data={},
                confidence=0.0,
                error=str(e)
            )
    
    def _research_safety_data(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict]
    ) -> ContaminationResearchResult:
        """Research safety data for laser cleaning operations."""
        
        existing_pattern = self._load_existing_pattern(pattern_id)
        
        prompt = f"""You are an industrial hygienist researching laser cleaning safety.

CONTAMINATION: {existing_pattern['name']}
Chemical Formula: {existing_pattern.get('chemical_formula', 'N/A')}

TASK: Identify safety hazards and controls.

Required structure:
```yaml
fumes_generated:
  - compound: "<chemical name>"
    concentration_mg_m3: <value>  # Typical airborne concentration
    exposure_limit_mg_m3: <value>  # OSHA PEL or ACGIH TLV
    hazard_class: "<irritant|toxic|carcinogenic|corrosive>"
  - compound: "<another compound>"
    concentration_mg_m3: <value>
    exposure_limit_mg_m3: <value>
    hazard_class: "<class>"
particulate_generation:
  size_range_um: [<min>, <max>]
  respirable_fraction: <0.0-1.0>  # Fraction that can reach lungs
ventilation_requirements:
  minimum_air_changes_per_hour: <value>
  exhaust_velocity_m_s: <value>
  filtration_type: "<HEPA|carbon|dual|scrubber>"
visibility_hazard: "<none|low|moderate|high>"  # Smoke/plume obscuration
ppe_requirements:
  respiratory: "<none|dust_mask|half_mask|full_face|PAPR>"
  eye_protection: "<safety_glasses|goggles|face_shield>"
  skin_protection: "<none|gloves|sleeves|full_suit>"
substrate_compatibility_warnings:
  - "<warning text for specific conditions>"
fire_explosion_risk: "<none|low|moderate|high>"
toxic_gas_risk: "<none|low|moderate|high>"
```

REQUIREMENTS:
1. Base on thermal decomposition of {existing_pattern.get('chemical_formula', 'the material')}
2. Consider OSHA and ACGIH exposure limits
3. Realistic hazard assessment
4. Practical PPE and engineering controls

YAML only."""

        try:
            from generation.config.dynamic_config import DynamicConfig
            dynamic_config = DynamicConfig()
            
            request = GenerationRequest(
                prompt=prompt,
                temperature=dynamic_config.calculate_temperature('research'),
                max_tokens=self.safety_max_tokens
            )
            response = self.api_client.generate(request)
            
            data = self._parse_yaml_response(response.content)
            confidence = self._calculate_safety_confidence(data)
            
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data=data,
                confidence=confidence,
                source="ai_research",
                metadata={'research_type': 'safety_data'}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to research safety data: {e}")
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data={},
                confidence=0.0,
                error=str(e)
            )
    
    def _research_selectivity_ratios(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict]
    ) -> ContaminationResearchResult:
        """Research material-specific selectivity ratios."""
        
        existing_pattern = self._load_existing_pattern(pattern_id)
        valid_materials = existing_pattern.get('valid_materials', [])
        
        prompt = f"""You are a laser physicist calculating absorption selectivity.

CONTAMINATION: {existing_pattern['name']}
Valid Substrate Materials: {', '.join(valid_materials[:10])}

TASK: Calculate selectivity ratios (contaminant absorption / substrate absorption).

Required structure:
```yaml
selectivity_ratio:  # At 1064nm wavelength
  # Ratio > 2.0 = safe selective removal
  # Ratio 1.0-2.0 = careful parameter control needed
  # Ratio < 1.0 = substrate absorbs more, high damage risk
  <material_name>: <ratio_value>
  <material_name>: <ratio_value>
  # ... for each valid material
wavelength_1064nm:
  <material_name>: <ratio>
wavelength_532nm:
  <material_name>: <ratio>
wavelength_355nm:
  <material_name>: <ratio>
optimal_wavelength_by_material:
  <material_name>: "<wavelength> nm"  # Best wavelength for this pairing
risk_assessment:
  high_risk_materials:  # Ratio < 1.5
    - <material>
  moderate_risk_materials:  # Ratio 1.5-3.0
    - <material>
  safe_materials:  # Ratio > 3.0
    - <material>
```

REQUIREMENTS:
1. Higher ratio = safer selective removal
2. Based on optical absorption coefficients at laser wavelengths
3. Consider substrate damage thresholds
4. Realistic physics-based values

YAML only, with brief risk summary."""

        try:
            from generation.config.dynamic_config import DynamicConfig
            dynamic_config = DynamicConfig()
            
            request = GenerationRequest(
                prompt=prompt,
                temperature=dynamic_config.calculate_temperature('research'),
                max_tokens=self.selectivity_max_tokens
            )
            response = self.api_client.generate(request)
            
            data = self._parse_yaml_response(response.content)
            confidence = self._calculate_selectivity_confidence(data, valid_materials)
            
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data=data,
                confidence=confidence,
                source="ai_research",
                metadata={
                    'research_type': 'selectivity_ratios',
                    'valid_materials_count': len(valid_materials)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to research selectivity ratios: {e}")
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data={},
                confidence=0.0,
                error=str(e)
            )
    
    def _research_complete_profile(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict]
    ) -> ContaminationResearchResult:
        """Research complete laser properties profile (all categories)."""
        
        self.logger.info(f"🔬 Researching complete laser profile for: {pattern_id}")
        
        # Research each category
        results = {}
        confidence_scores = []
        
        research_types = [
            'optical_properties',
            'thermal_properties',
            'removal_characteristics',
            'laser_parameters',
            'safety_data'
        ]
        
        for research_type in research_types:
            spec = ContaminationResearchSpec(
                pattern_id=pattern_id,
                research_type=research_type,
                material_context=research_spec.material_context
            )
            
            result = self.research(pattern_id, spec, context)
            
            if result.success:
                results[research_type] = result.data
                confidence_scores.append(result.confidence)
                self.logger.info(f"   ✅ {research_type}: {result.confidence:.2f} confidence")
            else:
                self.logger.warning(f"   ⚠️  {research_type}: FAILED")
                results[research_type] = {"error": result.error}
                confidence_scores.append(0.0)
        
        # Calculate overall confidence
        overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return ContaminationResearchResult(
            pattern_id=pattern_id,
            data=results,
            confidence=overall_confidence,
            source="ai_research",
            metadata={
                'research_type': 'complete_profile',
                'categories_researched': len(research_types),
                'successful_categories': sum(1 for c in confidence_scores if c > 0.5)
            }
        )
    
    # Helper methods
    
    def _load_existing_pattern(self, pattern_id: str) -> Optional[Dict]:
        """Load existing pattern from Contaminants.yaml"""
        try:
            return self.loader.get_pattern(pattern_id)
        except Exception as e:
            self.logger.error(f"Failed to load pattern {pattern_id}: {e}")
            return None
    
    def _parse_yaml_response(self, response: str) -> Dict:
        """Parse YAML from AI response, handling code blocks."""
        import re

        import yaml

        # Extract YAML from code blocks if present
        yaml_match = re.search(r'```(?:yaml)?\n(.*?)\n```', response, re.DOTALL)
        if yaml_match:
            yaml_text = yaml_match.group(1)
        else:
            yaml_text = response
        
        try:
            data = yaml.safe_load(yaml_text)
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse YAML: {e}")
            return {}
    
    def _calculate_optical_confidence(self, data: Dict) -> float:
        """Calculate confidence for optical properties."""
        score = 0.0
        
        # Check required fields
        if 'absorption_coefficient' in data:
            score += 0.4
            if len(data['absorption_coefficient']) >= 3:  # Multiple wavelengths
                score += 0.1
        
        if 'reflectivity' in data:
            score += 0.3
        
        if 'refractive_index' in data:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_thermal_confidence(self, data: Dict) -> float:
        """Calculate confidence for thermal properties."""
        score = 0.0
        
        if 'ablation_threshold' in data:
            score += 0.5  # Most critical
        
        if 'decomposition_temperature' in data:
            score += 0.2
        
        if 'thermal_conductivity' in data:
            score += 0.15
        
        if 'specific_heat' in data:
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_removal_confidence(self, data: Dict) -> float:
        """Calculate confidence for removal characteristics."""
        score = 0.0
        
        if 'primary_mechanism' in data:
            score += 0.3
        
        if 'removal_efficiency' in data:
            score += 0.4
        
        if 'byproducts' in data:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_parameters_confidence(self, data: Dict) -> float:
        """Calculate confidence for laser parameters."""
        score = 0.0
        
        if 'fluence_range' in data:
            score += 0.4
        
        if 'wavelength_preference' in data:
            score += 0.3
        
        if 'pulse_duration_range' in data:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_safety_confidence(self, data: Dict) -> float:
        """Calculate confidence for safety data."""
        score = 0.0
        
        if 'fumes_generated' in data:
            score += 0.4
        
        if 'ventilation_requirements' in data:
            score += 0.3
        
        if 'ppe_requirements' in data:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_selectivity_confidence(self, data: Dict, valid_materials: List) -> float:
        """Calculate confidence for selectivity ratios."""
        score = 0.0
        
        if 'selectivity_ratio' in data:
            ratio_count = len(data['selectivity_ratio'])
            material_count = len(valid_materials)
            
            if material_count > 0:
                coverage = min(ratio_count / material_count, 1.0)
                score += coverage * 0.7
            else:
                score += 0.5  # Some data better than none
        
        if 'risk_assessment' in data:
            score += 0.3
        
        return min(score, 1.0)
    
    def validate_result(
        self,
        result: ContaminationResearchResult,
        research_spec: ContaminationResearchSpec
    ) -> bool:
        """
        Validate research result meets requirements.
        
        Args:
            result: Research result to validate
            research_spec: Original research specification
        
        Returns:
            True if valid, False otherwise
        """
        if not result.success:
            return False
        
        if not result.data or not isinstance(result.data, dict):
            return False
        
        # Type-specific validation
        research_type = research_spec.research_type
        
        if research_type == 'optical_properties':
            return 'absorption_coefficient' in result.data or 'reflectivity' in result.data
        
        elif research_type == 'thermal_properties':
            return 'ablation_threshold' in result.data
        
        elif research_type == 'removal_characteristics':
            return 'primary_mechanism' in result.data
        
        elif research_type == 'laser_parameters':
            return 'fluence_range' in result.data or 'wavelength_preference' in result.data
        
        elif research_type == 'safety_data':
            return 'fumes_generated' in result.data or 'ventilation_requirements' in result.data
        
        elif research_type == 'selectivity_ratios':
            return 'selectivity_ratio' in result.data
        
        elif research_type == 'complete_profile':
            return len(result.data) >= 3  # At least 3 categories researched
        
        return True
