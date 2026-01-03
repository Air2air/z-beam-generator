#!/usr/bin/env python3
"""
Contaminant Removal by Material Enricher

Generates `removal_by_material` field for contaminant frontmatter by:
1. Loading material-contaminant associations from DomainAssociations.yaml
2. Extracting laser parameters from Settings.yaml for each material
3. Transforming into removal_by_material structure per spec
4. Adding compatibility, safety, and optimization metadata

Architecture:
- Input: Contaminant data dict + DomainAssociations + Settings
- Output: Enriched contaminant dict with removal_by_material field
- Spec: docs/CONTAMINANT_REMOVAL_BY_MATERIAL_SPEC.md

Created: December 20, 2025
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RemovalByMaterialEnricher:
    """
    Enriches contaminant frontmatter with material-specific removal parameters.
    
    Maps Settings laser parameters → removal_by_material structure for each
    material-contaminant combination found in DomainAssociations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize enricher with data sources.
        
        Args:
            config: Optional configuration dictionary (for export pipeline compatibility)
        """
        self.project_root = Path(__file__).resolve().parents[3]
        
        # Load associations
        assoc_file = self.project_root / 'data/associations/DomainAssociations.yaml'
        with open(assoc_file) as f:
            assoc_data = yaml.safe_load(f)
            self.material_to_contaminant = assoc_data['material_to_contaminant']
            self.contaminant_to_material = assoc_data['contaminant_to_material']
        
        # Load settings (laser parameters for each material)
        settings_file = self.project_root / 'data/settings/Settings.yaml'
        with open(settings_file) as f:
            self.settings = yaml.safe_load(f)['settings']
        
        # Create slug-to-name mapping for Settings
        self.slug_to_setting_name = self._build_slug_mapping()
        
        logger.info(f"Loaded {len(self.settings)} settings, "
                   f"{len(self.material_to_contaminant)} materials with contaminant associations")
    
    def _build_slug_mapping(self) -> Dict[str, str]:
        """
        Map material slugs (aluminum-laser-cleaning OR aluminum) to Settings names (Aluminum).
        
        Returns:
            Dict mapping slug → setting name
        """
        mapping = {}
        for setting_name in self.settings.keys():
            # Convert "Aluminum" → "aluminum-laser-cleaning"
            slug_with_suffix = setting_name.lower().replace(' ', '-') + '-laser-cleaning'
            slug_without_suffix = setting_name.lower().replace(' ', '-')
            
            # Support both formats
            mapping[slug_with_suffix] = setting_name
            mapping[slug_without_suffix] = setting_name
        return mapping
    
    def enrich(self, contaminant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add removal_by_material field to contaminant data.
        
        Args:
            contaminant_data: Contaminant frontmatter dict (must include 'id' field with slug)
        
        Returns:
            Enriched contaminant data with removal_by_material field
        """
        # Extract slug from data
        contaminant_slug = contaminant_data.get('id')
        if not contaminant_slug:
            logger.warning("Contaminant data missing 'id' field")
            return contaminant_data
        
        # Get materials that can have this contaminant
        applicable_materials = self.contaminant_to_material.get(contaminant_slug, [])
        
        if not applicable_materials:
            logger.warning(f"No material associations for {contaminant_slug}")
            return contaminant_data
        
        removal_by_material = {}
        
        for material_slug in applicable_materials:
            # Get setting name for this material
            setting_name = self.slug_to_setting_name.get(material_slug)
            
            if not setting_name or setting_name not in self.settings:
                logger.debug(f"No setting found for material {material_slug}")
                continue
            
            # Get laser parameters from Settings
            setting = self.settings[setting_name]
            if 'machine_settings' not in setting:
                logger.debug(f"No machine_settings for {setting_name}")
                continue
            
            # Transform to removal_by_material structure
            material_entry = self._transform_setting_to_removal(
                setting['machine_settings'],
                material_slug,
                contaminant_slug
            )
            
            # Use material slug (without -laser-cleaning suffix) as key
            material_key = material_slug.replace('-laser-cleaning', '')
            removal_by_material[material_key] = material_entry
        
        # Add to contaminant data
        if removal_by_material:
            contaminant_data['removal_by_material'] = removal_by_material
            logger.info(f"Added removal_by_material for {contaminant_slug}: "
                       f"{len(removal_by_material)} materials")
        
        return contaminant_data
    
    def _transform_setting_to_removal(
        self,
        machine_settings: Dict[str, Any],
        material_slug: str,
        contaminant_slug: str
    ) -> Dict[str, Any]:
        """
        Transform Settings machine_settings → removal_by_material entry.
        
        Args:
            machine_settings: Settings machine_settings dict
            material_slug: Material slug (e.g., 'aluminum-laser-cleaning')
            contaminant_slug: Contaminant slug
        
        Returns:
            removal_by_material entry dict per spec
        """
        # Extract laser parameters
        laser_params = self._extract_laser_parameters(machine_settings)
        
        # Generate removal characteristics
        removal_chars = self._generate_removal_characteristics(
            laser_params, material_slug, contaminant_slug
        )
        
        # Assess compatibility
        compatibility = self._assess_compatibility(
            material_slug, contaminant_slug, removal_chars
        )
        
        # Generate safety considerations
        safety = self._generate_safety_considerations(
            material_slug, contaminant_slug
        )
        
        # Generate optimization tips
        optimization_tips = self._generate_optimization_tips(
            laser_params, material_slug
        )
        
        # Generate success indicators
        success_indicators = self._generate_success_indicators(
            material_slug, contaminant_slug
        )
        
        return {
            'laser_parameters': laser_params,
            'removal_characteristics': removal_chars,
            'compatibility': compatibility,
            'safety_considerations': safety,
            'optimization_tips': optimization_tips,
            'success_indicators': success_indicators
        }
    
    def _extract_laser_parameters(self, ms: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract laser parameters from Settings machine_settings.
        
        Args:
            ms: machine_settings dict from Settings
        
        Returns:
            laser_parameters dict per spec
        """
        def get_param(key: str, default_unit: str) -> Dict[str, Any]:
            """Extract parameter with value, unit, range."""
            param = ms.get(key, {})
            
            value = param.get('value')
            unit = param.get('unit', default_unit)
            min_val = param.get('min')
            max_val = param.get('max')
            
            result = {'unit': unit}
            
            if value is not None:
                result['value'] = value
                result['recommended'] = value
            
            if min_val is not None and max_val is not None:
                result['range'] = [min_val, max_val]
            
            return result
        
        # Map Settings keys → spec keys
        # PRIORITY: Use new researched parameters (snake_case with ranges) if available,
        # fallback to old camelCase keys for backward compatibility
        return {
            'wavelength': get_param('wavelength', 'nm'),
            'power': get_param('power', 'W') if 'power' in ms and 'min' in ms.get('power', {}) else get_param('powerRange', 'W'),
            'scan_speed': get_param('scan_speed', 'mm/s') if 'scan_speed' in ms and 'min' in ms.get('scan_speed', {}) else get_param('scanSpeed', 'mm/s'),
            'pulse_width': get_param('pulse_width', 'ns') if 'pulse_width' in ms and 'min' in ms.get('pulse_width', {}) else get_param('pulseWidth', 'ns'),
            'repetition_rate': get_param('repetition_rate', 'kHz') if 'repetition_rate' in ms and 'min' in ms.get('repetition_rate', {}) else get_param('repetitionRate', 'kHz'),
            'energy_density': get_param('energy_density', 'J/cm²') if 'energy_density' in ms and 'min' in ms.get('energy_density', {}) else get_param('energyDensity', 'J/cm²'),
            'spot_size': get_param('spot_size', 'μm') if 'spot_size' in ms and 'min' in ms.get('spot_size', {}) else get_param('spotSize', 'μm'),
            'pass_count': get_param('pass_count', '') if 'pass_count' in ms and 'min' in ms.get('pass_count', {}) else get_param('passCount', ''),
            'overlap_ratio': get_param('overlap_ratio', '%') if 'overlap_ratio' in ms and 'min' in ms.get('overlap_ratio', {}) else get_param('overlapRatio', '%')
        }
    
    def _generate_removal_characteristics(
        self,
        laser_params: Dict[str, Any],
        material_slug: str,
        contaminant_slug: str
    ) -> Dict[str, Any]:
        """
        Generate removal_characteristics based on parameters and material/contaminant types.
        
        Args:
            laser_params: Extracted laser parameters
            material_slug: Material slug
            contaminant_slug: Contaminant slug
        
        Returns:
            removal_characteristics dict per spec
        """
        # Determine primary mechanism based on contaminant category
        if any(x in contaminant_slug for x in ['rust', 'oxide', 'scale', 'patina']):
            primary_mechanism = 'thermal_ablation'
            secondary_mechanisms = ['photochemical', 'plasma_formation']
        elif any(x in contaminant_slug for x in ['paint', 'coating', 'residue']):
            primary_mechanism = 'photochemical'
            secondary_mechanisms = ['thermal_ablation']
        elif any(x in contaminant_slug for x in ['dust', 'dirt', 'particulate']):
            primary_mechanism = 'mechanical_stress'
            secondary_mechanisms = ['thermal_ablation']
        else:
            primary_mechanism = 'thermal_ablation'
            secondary_mechanisms = ['photochemical']
        
        # Estimate removal efficiency based on pass count
        pass_count = laser_params['pass_count'].get('value', 2)
        if pass_count == 1:
            single_pass = 0.90
        elif pass_count == 2:
            single_pass = 0.75
        else:
            single_pass = 0.60
        
        optimal_passes = pass_count
        
        # Surface quality based on material type
        if 'metal' in material_slug or any(x in material_slug for x in ['steel', 'aluminum', 'copper', 'brass']):
            roughness_change = 'minimal'
            discoloration_risk = 'low'
            substrate_damage_risk = 'low'
        elif any(x in material_slug for x in ['wood', 'plastic', 'rubber']):
            roughness_change = 'slight'
            discoloration_risk = 'moderate'
            substrate_damage_risk = 'moderate'
        else:
            roughness_change = 'minimal'
            discoloration_risk = 'low'
            substrate_damage_risk = 'low'
        
        return {
            'primary_mechanism': primary_mechanism,
            'secondary_mechanisms': secondary_mechanisms,
            'removal_efficiency': {
                'single_pass': single_pass,
                'optimal_passes': optimal_passes,
                'diminishing_returns_after': optimal_passes + 2,
                'typical_time_per_cm2': round(2.0 / single_pass, 1)
            },
            'surface_quality_after_removal': {
                'roughness_change': roughness_change,
                'discoloration_risk': discoloration_risk,
                'substrate_damage_risk': substrate_damage_risk,
                'residual_contamination': 'none' if single_pass > 0.85 else 'trace'
            }
        }
    
    def _assess_compatibility(
        self,
        material_slug: str,
        contaminant_slug: str,
        removal_chars: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess material-contaminant compatibility.
        
        Args:
            material_slug: Material slug
            contaminant_slug: Contaminant slug
            removal_chars: Removal characteristics
        
        Returns:
            compatibility dict per spec
        """
        # Base assessment: if in associations, it's generally compatible
        recommended = True
        
        # Estimate success rate from single-pass efficiency
        single_pass = removal_chars['removal_efficiency']['single_pass']
        success_rate = min(single_pass + 0.1, 0.98)  # Cap at 98%
        
        # Determine difficulty
        if success_rate > 0.90:
            difficulty = 'easy'
        elif success_rate > 0.75:
            difficulty = 'moderate'
        elif success_rate > 0.60:
            difficulty = 'difficult'
        else:
            difficulty = 'extreme'
        
        # Generate material-specific warnings
        warnings = []
        if any(x in material_slug for x in ['thin', 'foil', 'sheet']):
            warnings.append("Monitor for heat accumulation on thin sections")
        
        if 'plastic' in material_slug or 'polymer' in material_slug:
            warnings.append("Risk of substrate melting - use lower power settings")
        
        limitations = []
        if 'rust' in contaminant_slug and 'aluminum' in material_slug:
            limitations.append("Not effective on heavily pitted surfaces")
        
        return {
            'recommended': recommended,
            'success_rate': success_rate,
            'difficulty': difficulty,
            'substrate_warnings': warnings if warnings else ['Standard precautions apply'],
            'process_limitations': limitations if limitations else ['None identified']
        }
    
    def _generate_safety_considerations(
        self,
        material_slug: str,
        contaminant_slug: str
    ) -> Dict[str, Any]:
        """
        Generate safety considerations for material-contaminant combination.
        
        Args:
            material_slug: Material slug
            contaminant_slug: Contaminant slug
        
        Returns:
            safety_considerations dict per spec
        """
        hazards = []
        
        # Metal-specific hazards
        if any(x in material_slug for x in ['copper', 'brass', 'bronze']):
            hazards.append("Copper vapor release at high power (>100W)")
        if 'beryllium' in material_slug:
            hazards.append("Beryllium alloy requires enhanced PPE - PAPR recommended")
        if 'lead' in contaminant_slug:
            hazards.append("Lead particulates require P100 respirator minimum")
        
        # Coating-specific hazards
        if 'paint' in contaminant_slug or 'coating' in contaminant_slug:
            hazards.append("Organic vapor generation - ensure adequate ventilation")
        
        if not hazards:
            hazards.append("Standard laser cleaning hazards apply")
        
        # Base PPE (from contaminant)
        ppe = {
            'respiratory': 'P100',
            'eye_protection': 'OD7+ at operating wavelength',
            'skin_protection': 'Heat-resistant gloves'
        }
        
        # Base ventilation
        ventilation = {
            'minimum_air_changes_per_hour': 10,
            'extraction_velocity_m_s': 0.5,
            'filtration_notes': 'HEPA filtration recommended for particulate capture'
        }
        
        # Fume warnings
        fume_warnings = []
        if any(x in material_slug for x in ['metal', 'steel', 'aluminum']):
            fume_warnings.append("Metal oxide particulates - monitor air quality")
        if 'wood' in material_slug:
            fume_warnings.append("Organic combustion products - ensure ventilation")
        
        return {
            'material_specific_hazards': hazards,
            'recommended_ppe': ppe,
            'ventilation_requirements': ventilation,
            'fume_warnings': fume_warnings if fume_warnings else ['Standard fume precautions']
        }
    
    def _generate_optimization_tips(
        self,
        laser_params: Dict[str, Any],
        material_slug: str
    ) -> List[str]:
        """
        Generate optimization tips for this material.
        
        Args:
            laser_params: Laser parameters
            material_slug: Material slug
        
        Returns:
            List of optimization tip strings
        """
        tips = []
        
        # Power-based tips
        power = laser_params['power'].get('range', [0, 100])
        if power:
            tips.append(f"Start at lower power ({power[0]}W) and increase gradually to avoid substrate damage")
        
        # Pass-based tips
        pass_count = laser_params['pass_count'].get('value', 2)
        if pass_count > 1:
            tips.append(f"Use {pass_count} passes rather than single high-energy pass for better control")
            tips.append("Allow 2-3 seconds between passes for substrate cooling")
        
        # Material-specific tips
        if any(x in material_slug for x in ['metal', 'steel', 'aluminum', 'copper']):
            tips.append("Check surface temperature with IR thermometer between passes")
        
        if 'wood' in material_slug or 'organic' in material_slug:
            tips.append("Monitor for charring - reduce power if discoloration occurs")
        
        if not tips:
            tips.append("Follow standard laser cleaning best practices")
        
        return tips
    
    def _generate_success_indicators(
        self,
        material_slug: str,
        contaminant_slug: str
    ) -> Dict[str, Any]:
        """
        Generate success indicators for verification.
        
        Args:
            material_slug: Material slug
            contaminant_slug: Contaminant slug
        
        Returns:
            success_indicators dict per spec
        """
        visual = []
        measurement = []
        failure_signs = []
        
        # Visual indicators
        if any(x in material_slug for x in ['metal', 'steel', 'aluminum']):
            visual.append("Restored base metal luster")
            visual.append("Uniform surface appearance")
        else:
            visual.append("Clean, uniform surface")
            visual.append("No visible residue")
        
        visual.append("Original substrate texture visible")
        
        # Measurement indicators
        measurement.append("Surface roughness increase <2.0 μm Ra")
        if 'rust' in contaminant_slug or 'oxide' in contaminant_slug:
            measurement.append("No detectable contamination via XRF/EDS")
        if any(x in material_slug for x in ['metal', 'aluminum', 'steel']):
            measurement.append("Surface reflectance >80% of clean baseline")
        
        # Failure signs
        failure_signs.append("Discoloration (indicates overheating)")
        failure_signs.append("Surface pitting or roughness (excessive energy)")
        failure_signs.append("Incomplete removal after optimal pass count (insufficient energy)")
        
        return {
            'visual': visual,
            'measurement': measurement,
            'failure_signs': failure_signs
        }


def create_enricher():
    """Factory function for enricher registration."""
    return RemovalByMaterialEnricher()
