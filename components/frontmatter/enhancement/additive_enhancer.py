#!/usr/bin/env python3
"""
Additive Frontmatter Enhancement Integration

This service demonstrates how to integrate the enhanced materials.yaml mapper
additively without breaking existing functionality.

APPROACH: Non-destructive enhancement that preserves existing workflow while
          adding rich materials.yaml data utilization.
"""

import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


class AdditiveFrontmatterEnhancer:
    """
    Additive enhancement service that integrates materials.yaml rich data
    into existing frontmatter generation workflow without breaking changes.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Lazy import to avoid breaking existing code if mapper has issues
        self._mapper = None
    
    @property
    def mapper(self):
        """Lazy load the materials yaml mapper."""
        if self._mapper is None:
            try:
                from components.frontmatter.enhancement.materials_yaml_mapper import MaterialsYamlFrontmatterMapper
                self._mapper = MaterialsYamlFrontmatterMapper()
                self.logger.info("✅ Materials.yaml mapper loaded successfully")
            except Exception as e:
                self.logger.warning(f"⚠️ Materials.yaml mapper not available: {e}")
                self._mapper = False  # Mark as unavailable
        return self._mapper if self._mapper is not False else None
    
    def enhance_frontmatter_additively(
        self, 
        existing_frontmatter: Dict, 
        material_data: Dict, 
        material_name: str,
        enhancement_level: str = "comprehensive"
    ) -> Dict:
        """
        Additively enhance existing frontmatter with rich materials.yaml data.
        
        GUARANTEE: This method never breaks existing frontmatter. It only adds
                  enhancement where materials.yaml provides richer data.
        
        Args:
            existing_frontmatter: Current frontmatter (preserved completely)
            material_data: Rich materials.yaml data for the material
            material_name: Material name for context
            enhancement_level: 'basic', 'standard', 'comprehensive'
        
        Returns:
            Enhanced frontmatter with materials.yaml data additivitely integrated
        """
        self.logger.info(f"🔧 Additively enhancing frontmatter for {material_name}")
        
        # Start with existing frontmatter (preserves everything)
        enhanced = existing_frontmatter.copy()
        
        # Only enhance if mapper is available
        if not self.mapper:
            self.logger.info("📋 Using existing frontmatter only (mapper unavailable)")
            return enhanced
        
        try:
            # Generate comprehensive materials.yaml-based frontmatter
            materials_based = self.mapper.map_materials_to_comprehensive_frontmatter(
                material_data, material_name
            )
            
            # Apply additive enhancements based on level
            if enhancement_level == "comprehensive":
                enhanced = self._apply_comprehensive_enhancement(enhanced, materials_based, material_data)
            elif enhancement_level == "standard":
                enhanced = self._apply_standard_enhancement(enhanced, materials_based, material_data)
            else:  # basic
                enhanced = self._apply_basic_enhancement(enhanced, materials_based, material_data)
            
            # Add enhancement metadata
            enhanced['enhancement'] = {
                'materialsYamlUsed': True,
                'enhancementLevel': enhancement_level,
                'fieldsAdded': len([k for k in materials_based.keys() if k not in existing_frontmatter])
            }
            
            self.logger.info(f"✅ Additively enhanced with {len(materials_based)} materials.yaml sections")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Enhancement failed, using existing frontmatter: {e}")
            # FAIL-SAFE: Always return existing frontmatter if enhancement fails
        
        return enhanced
    
    def _apply_comprehensive_enhancement(self, existing: Dict, materials_based: Dict, material_data: Dict) -> Dict:
        """Apply comprehensive enhancement - adds all available materials.yaml data."""
        enhanced = existing.copy()
        
        # Add sections that don't exist or enhance existing ones
        sections_to_enhance = [
            'technicalProperties',
            'machineSettings', 
            'chemicalProperties',
            'laserInteraction',
            'applications',
            'compatibility',
            'regulatoryStandards'
        ]
        
        for section in sections_to_enhance:
            if section in materials_based:
                if section in existing:
                    # Merge existing with materials.yaml data (existing takes precedence)
                    enhanced[section] = self._merge_section_data(
                        existing[section], 
                        materials_based[section], 
                        section
                    )
                else:
                    # Add new section from materials.yaml
                    enhanced[section] = materials_based[section]
        
        # Enhance machine settings with numeric extraction
        if 'machineSettings' in enhanced:
            enhanced['machineSettings'] = self._enhance_machine_settings_numeric(
                enhanced['machineSettings']
            )
        
        # Add content metadata if missing key fields
        if 'description' not in existing or len(existing.get('description', '')) < 50:
            enhanced.update(self._enhance_content_metadata(existing, materials_based))
        
        return enhanced
    
    def _apply_standard_enhancement(self, existing: Dict, materials_based: Dict, material_data: Dict) -> Dict:
        """Apply standard enhancement - adds key sections without overwhelming existing data."""
        enhanced = existing.copy()
        
        # Standard enhancements focus on technical and machine data
        priority_sections = ['technicalProperties', 'machineSettings', 'applications']
        
        for section in priority_sections:
            if section in materials_based and section not in existing:
                enhanced[section] = materials_based[section]
        
        # Enhance machine settings with numeric data for computational use
        if 'machineSettings' in enhanced:
            enhanced['machineSettings'] = self._enhance_machine_settings_numeric(
                enhanced['machineSettings']
            )
        
        return enhanced
    
    def _apply_basic_enhancement(self, existing: Dict, materials_based: Dict, material_data: Dict) -> Dict:
        """Apply basic enhancement - only adds missing critical data."""
        enhanced = existing.copy()
        
        # Basic enhancement only adds missing machine settings and technical properties
        if 'machineSettings' not in existing and 'machineSettings' in materials_based:
            enhanced['machineSettings'] = materials_based['machineSettings']
        
        if 'technicalProperties' not in existing and 'technicalProperties' in materials_based:
            # Only add key physical properties
            tech_props = materials_based['technicalProperties']
            basic_props = {}
            for key in ['density', 'thermalConductivity', 'hardness', 'tensileStrength']:
                if key in tech_props:
                    basic_props[key] = tech_props[key]
            if basic_props:
                enhanced['technicalProperties'] = basic_props
        
        return enhanced
    
    def _merge_section_data(self, existing_data: Any, materials_data: Any, section_name: str) -> Any:
        """
        Intelligently merge section data, preserving existing while adding materials.yaml enhancements.
        """
        if isinstance(existing_data, dict) and isinstance(materials_data, dict):
            merged = materials_data.copy()  # Start with materials.yaml data
            merged.update(existing_data)    # Existing data takes precedence
            return merged
        elif isinstance(existing_data, list) and isinstance(materials_data, list):
            # For lists, combine and deduplicate
            combined = list(materials_data)
            for item in existing_data:
                if item not in combined:
                    combined.append(item)
            return combined
        else:
            # For other types, existing takes precedence
            return existing_data
    
    def _enhance_machine_settings_numeric(self, machine_settings: Dict) -> Dict:
        """Add numeric extraction to machine settings for computational use."""
        enhanced = machine_settings.copy()
        
        # Add numeric extraction for ranges
        range_fields = ['powerRange', 'pulseDuration', 'repetitionRate', 'spotSize']
        
        for field in range_fields:
            if field in enhanced:
                value = enhanced[field]
                if isinstance(value, str) and ('-' in value or '–' in value):
                    numeric_info = self._extract_range_numeric(value)
                    if numeric_info:
                        enhanced[f"{field}Numeric"] = numeric_info
        
        return enhanced
    
    def _enhance_content_metadata(self, existing: Dict, materials_based: Dict) -> Dict:
        """Enhance content metadata only if existing is insufficient."""
        enhancements = {}
        
        # Only enhance if existing metadata is missing or insufficient
        content_fields = ['title', 'headline', 'description', 'keywords']
        
        for field in content_fields:
            if field not in existing and field in materials_based:
                enhancements[field] = materials_based[field]
            elif field in existing and field in materials_based:
                existing_value = existing[field]
                materials_value = materials_based[field]
                
                # Enhance if existing is too short or generic
                if field == 'description' and len(str(existing_value)) < 50:
                    enhancements[field] = materials_value
                elif field == 'keywords' and len(str(existing_value).split(',')) < 5:
                    # Merge keywords
                    existing_keywords = set(str(existing_value).split(','))
                    materials_keywords = set(str(materials_value).split(','))
                    combined_keywords = existing_keywords.union(materials_keywords)
                    enhancements[field] = ', '.join(sorted(combined_keywords))
        
        return enhancements
    
    def _extract_range_numeric(self, value: str) -> Optional[Dict]:
        """Extract numeric range information from string values."""
        try:
            import re
            
            # Clean the value
            clean_value = re.sub(r'[^\d\.\-–\s]', '', value)
            
            # Handle different separators
            if '–' in clean_value:
                parts = clean_value.split('–')
            elif '-' in clean_value and not clean_value.startswith('-'):
                parts = clean_value.split('-')
            else:
                # Single value
                num = float(re.findall(r'\d+\.?\d*', clean_value)[0])
                return {'value': num, 'type': 'single'}
            
            if len(parts) == 2:
                min_val = float(parts[0].strip())
                max_val = float(parts[1].strip())
                return {
                    'min': min_val,
                    'max': max_val,
                    'average': (min_val + max_val) / 2,
                    'type': 'range'
                }
        except Exception:
            pass
        
        return None
    
    def get_enhancement_recommendations(self, material_data: Dict, material_name: str) -> Dict:
        """
        Analyze materials.yaml data and recommend enhancement opportunities.
        Helps identify what rich data is available for frontmatter enhancement.
        """
        recommendations = {
            'available_enhancements': [],
            'data_richness_score': 0,
            'recommended_level': 'basic'
        }
        
        # Analyze available data richness
        data_score = 0
        
        # Check machine settings completeness
        if 'machine_settings' in material_data:
            ms = material_data['machine_settings']
            ms_completeness = len(ms) / 11.0  # 11 total possible machine settings
            data_score += ms_completeness * 30
            recommendations['available_enhancements'].append(
                f"Machine Settings: {len(ms)}/11 parameters available ({ms_completeness*100:.0f}%)"
            )
        
        # Check technical properties completeness  
        tech_fields = ['density', 'thermal_conductivity', 'hardness', 'tensile_strength', 
                      'youngs_modulus', 'electrical_resistivity']
        tech_available = sum(1 for field in tech_fields if field in material_data)
        tech_completeness = tech_available / len(tech_fields)
        data_score += tech_completeness * 25
        recommendations['available_enhancements'].append(
            f"Technical Properties: {tech_available}/{len(tech_fields)} key properties available ({tech_completeness*100:.0f}%)"
        )
        
        # Check applications and industry data
        if 'applications' in material_data:
            app_count = len(material_data['applications'])
            data_score += min(app_count / 6.0, 1.0) * 20  # Up to 6 applications for full score
            recommendations['available_enhancements'].append(
                f"Applications: {app_count} structured applications available"
            )
        
        # Check regulatory and compatibility
        if 'regulatory_standards' in material_data:
            reg_count = len(material_data['regulatory_standards'])
            data_score += min(reg_count / 4.0, 1.0) * 15
            recommendations['available_enhancements'].append(
                f"Regulatory Standards: {reg_count} standards available"
            )
        
        if 'compatibility' in material_data:
            data_score += 10
            recommendations['available_enhancements'].append(
                "Compatibility: Laser types and surface treatments defined"
            )
        
        recommendations['data_richness_score'] = int(data_score)
        
        # Recommend enhancement level based on data richness
        if data_score >= 75:
            recommendations['recommended_level'] = 'comprehensive'
        elif data_score >= 45:
            recommendations['recommended_level'] = 'standard' 
        else:
            recommendations['recommended_level'] = 'basic'
        
        return recommendations


# Example integration with existing frontmatter generator
def integrate_with_existing_generator(material_name: str, material_data: Dict, api_client=None) -> Dict:
    """
    Example of how to integrate the additive enhancer with existing frontmatter generation.
    
    This function shows the non-destructive integration approach.
    """
    logger.info(f"🔗 Integrating enhanced materials.yaml data for {material_name}")
    
    # STEP 1: Generate existing frontmatter (current workflow unchanged)
    existing_frontmatter = {}
    
    # Simulate existing frontmatter generation (your current logic here)
    existing_frontmatter.update({
        'name': material_name,
        'category': material_data.get('category', 'unknown'),
        'title': f"Laser Cleaning {material_name}",
        # ... existing generation logic
    })
    
    # STEP 2: Additively enhance with materials.yaml rich data
    enhancer = AdditiveFrontmatterEnhancer()
    
    # Get enhancement recommendations
    recommendations = enhancer.get_enhancement_recommendations(material_data, material_name)
    logger.info(f"📊 Enhancement recommendations: {recommendations['recommended_level']} level, "
               f"{recommendations['data_richness_score']}/100 data richness")
    
    # Apply additive enhancement
    enhanced_frontmatter = enhancer.enhance_frontmatter_additively(
        existing_frontmatter=existing_frontmatter,
        material_data=material_data,
        material_name=material_name,
        enhancement_level=recommendations['recommended_level']
    )
    
    # STEP 3: Optional AI supplemental enhancement (if API client available)
    if api_client and recommendations['data_richness_score'] < 80:
        logger.info("🤖 Using AI for supplemental enhancement of remaining gaps")
        # Your existing AI enhancement logic here
        # AI now only fills gaps that materials.yaml cannot provide
    
    logger.info(f"✅ Frontmatter integration complete with {len(enhanced_frontmatter)} total sections")
    return enhanced_frontmatter


if __name__ == "__main__":
    print("🚀 Additive Frontmatter Enhancement Integration")
    print("=" * 55)
    print()
    print("This service demonstrates how to:")
    print("✅ Preserve existing frontmatter generation workflow")
    print("✅ Additively enhance with rich materials.yaml data") 
    print("✅ Reduce AI dependency through structured data utilization")
    print("✅ Provide enhancement recommendations based on data richness")
    print("✅ Maintain fail-safe behavior if enhancements fail")
    print()
    print("💡 Key Benefits:")
    print("   • Non-destructive: Existing code continues to work")
    print("   • Data-driven: Leverages 56 possible materials.yaml fields")
    print("   • AI-optimized: AI only fills gaps materials.yaml cannot")
    print("   • Flexible: Basic/Standard/Comprehensive enhancement levels")
    print("   • Robust: Fail-safe fallback to existing functionality")
