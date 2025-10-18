#!/usr/bin/env python3
"""
Pipeline Process Service

Handles pipeline-specific frontmatter sections:
- Environmental impact assessment
- Regulatory standards (universal + material-specific)
- Outcome metrics
- Applications discovery from industry data

These sections represent the "pipeline" of information that flows
through the generation process, building up the complete frontmatter.

Follows fail-fast principles:
- No mocks or fallbacks in production
- Explicit error handling
- Validates required configuration data
"""

import logging
from typing import Dict, List, Optional
from validation.errors import MaterialDataError, ConfigurationError

logger = logging.getLogger(__name__)


class PipelineProcessService:
    """
    Service for handling pipeline-specific frontmatter sections.
    
    Generates environmental impact, regulatory standards, outcome metrics,
    and applications from category and material data.
    """
    
    def __init__(
        self,
        environmental_impact_templates: Dict,
        standard_outcome_metrics: Dict,
        universal_regulatory_standards: List,
        category_enhanced_data: Optional[Dict] = None
    ):
        """
        Initialize pipeline process service.
        
        Args:
            environmental_impact_templates: Templates from Categories.yaml
            standard_outcome_metrics: Standard metrics from Categories.yaml
            universal_regulatory_standards: Universal standards from Categories.yaml
            category_enhanced_data: Enhanced category data for industry applications
            
        Raises:
            ConfigurationError: If required configuration is missing
        """
        if not environmental_impact_templates:
            raise ConfigurationError("Environmental impact templates required")
        
        if not standard_outcome_metrics:
            raise ConfigurationError("Standard outcome metrics required")
        
        if not universal_regulatory_standards:
            raise ConfigurationError("Universal regulatory standards required")
        
        self.environmental_impact_templates = environmental_impact_templates
        self.standard_outcome_metrics = standard_outcome_metrics
        self.universal_regulatory_standards = universal_regulatory_standards
        self.category_enhanced_data = category_enhanced_data or {}
        self.logger = logger
    
    def add_environmental_impact_section(self, frontmatter: Dict, material_data: Dict) -> Dict:
        """
        Add environmental impact section using standardized templates.
        
        Args:
            frontmatter: Current frontmatter dict
            material_data: Material data from Materials.yaml
            
        Returns:
            Updated frontmatter with environmentalImpact section
        """
        try:
            environmental_impact = []
            
            # Apply relevant environmental impact templates
            for impact_type, template in self.environmental_impact_templates.items():
                impact_entry = {
                    'benefit': impact_type.replace('_', ' ').title(),
                    'applicableIndustries': template.get('applicable_industries', [])
                }
                # Zero Null Policy: Only add fields if they have non-empty values
                if template.get('description'):
                    impact_entry['description'] = template['description']
                if template.get('quantified_benefits'):
                    impact_entry['quantifiedBenefits'] = template['quantified_benefits']
                if template.get('sustainability_benefit'):
                    impact_entry['sustainabilityBenefit'] = template['sustainability_benefit']
                environmental_impact.append(impact_entry)
                
            if environmental_impact:
                frontmatter['environmentalImpact'] = environmental_impact
                self.logger.info(f"Added {len(environmental_impact)} environmental impact items")
                
            return frontmatter
            
        except Exception as e:
            self.logger.warning(f"Failed to add environmental impact section: {e}")
            return frontmatter
    
    def add_outcome_metrics_section(self, frontmatter: Dict, material_data: Dict) -> Dict:
        """
        Add outcome metrics section using standardized metrics.
        
        Args:
            frontmatter: Current frontmatter dict
            material_data: Material data from Materials.yaml
            
        Returns:
            Updated frontmatter with outcomeMetrics section
        """
        try:
            outcome_metrics = []
            
            # Apply relevant standard outcome metrics
            for metric_type, metric_def in self.standard_outcome_metrics.items():
                metric_entry = {
                    'metric': metric_type.replace('_', ' ').title(),
                    'measurementMethods': metric_def.get('measurement_methods', []),
                    'factorsAffecting': metric_def.get('factors_affecting', []),
                    'units': metric_def.get('units', [])
                }
                # Zero Null Policy: Only add fields if they have non-empty values
                if metric_def.get('description'):
                    metric_entry['description'] = metric_def['description']
                if metric_def.get('typical_ranges'):
                    metric_entry['typicalRanges'] = metric_def['typical_ranges']
                outcome_metrics.append(metric_entry)
                
            if outcome_metrics:
                frontmatter['outcomeMetrics'] = outcome_metrics
                self.logger.info(f"Added {len(outcome_metrics)} outcome metrics")
                
            return frontmatter
            
        except Exception as e:
            self.logger.error(f"Failed to add outcome metrics: {e}")
            return frontmatter
    
    def add_regulatory_standards_section(self, frontmatter: Dict, material_data: Dict) -> Dict:
        """
        Add regulatory standards combining universal standards with material-specific ones.
        
        Args:
            frontmatter: Current frontmatter dict
            material_data: Material data from Materials.yaml
            
        Returns:
            Updated frontmatter with regulatoryStandards section
        """
        try:
            all_regulatory_standards = []
            
            # Add universal regulatory standards (applies to ALL materials)
            if self.universal_regulatory_standards:
                all_regulatory_standards.extend(self.universal_regulatory_standards)
                self.logger.info(f"Added {len(self.universal_regulatory_standards)} universal regulatory standards")
            
            # Add material-specific regulatory standards from Materials.yaml
            material_specific_standards = []
            
            # Check for standards in material_metadata (optimized structure)
            if 'material_metadata' in material_data and 'regulatoryStandards' in material_data['material_metadata']:
                material_specific_standards = material_data['material_metadata']['regulatoryStandards']
            # Fallback to direct field (legacy structure)
            elif 'regulatoryStandards' in material_data:
                material_specific_standards = material_data['regulatoryStandards']
            
            if material_specific_standards:
                all_regulatory_standards.extend(material_specific_standards)
                self.logger.info(f"Added {len(material_specific_standards)} material-specific regulatory standards")
            
            # Add combined regulatory standards to frontmatter
            if all_regulatory_standards:
                frontmatter['regulatoryStandards'] = all_regulatory_standards
                self.logger.info(f"Total regulatory standards: {len(all_regulatory_standards)} (universal + specific)")
            else:
                # Ensure universal standards are always present
                frontmatter['regulatoryStandards'] = self.universal_regulatory_standards
                
            return frontmatter
            
        except Exception as e:
            self.logger.error(f"Failed to add regulatory standards: {e}")
            # Ensure universal standards are preserved even on error
            frontmatter['regulatoryStandards'] = self.universal_regulatory_standards
            return frontmatter
    
    def generate_applications_from_unified_industry_data(
        self,
        material_name: str,
        material_data: Dict
    ) -> List[str]:
        """
        Generate applications using unified industry data structure.
        
        Combines category primary industries with material-specific industry overrides.
        
        Args:
            material_name: Name of the material
            material_data: Material data from Materials.yaml
            
        Returns:
            List of application/industry strings
            
        Raises:
            MaterialDataError: If material category is missing
        """
        try:
            applications = []
            
            if 'category' not in material_data:
                raise MaterialDataError(
                    f"Material category required for {material_name} - "
                    "no fallbacks allowed per fail-fast principles"
                )
            
            material_category = material_data['category']
            
            # Get category primary industries from Categories.yaml (unified source)
            category_primary_industries = []
            if material_category in self.category_enhanced_data:
                enhanced_data = self.category_enhanced_data[material_category]
                if 'industryTags' in enhanced_data:
                    industry_tags_data = enhanced_data['industryTags']
                    if 'primary_industries' in industry_tags_data:
                        category_primary_industries = industry_tags_data['primary_industries']
            
            # Check for material-specific industry overrides (preserved unique tags)
            material_specific_industries = []
            if 'material_metadata' in material_data and 'industryTags' in material_data['material_metadata']:
                material_specific_industries = material_data['material_metadata']['industryTags']
            
            # Combine category primary + material-specific industries
            all_industries = list(set(category_primary_industries + material_specific_industries))
            
            if all_industries:
                applications = all_industries
                self.logger.info(
                    f"Generated {len(applications)} applications for {material_name} "
                    f"({len(category_primary_industries)} from category, "
                    f"{len(material_specific_industries)} material-specific)"
                )
            else:
                self.logger.warning(f"No applications found for {material_name}")
            
            return applications
            
        except MaterialDataError:
            # Re-raise MaterialDataErrors
            raise
        except Exception as e:
            self.logger.error(f"Failed to generate applications for {material_name}: {e}")
            raise MaterialDataError(f"Application generation failed for {material_name}: {e}")
    
    def validate_pipeline_configuration(self) -> bool:
        """
        Validate that pipeline configuration is complete.
        
        Returns:
            True if configuration appears complete, False otherwise
        """
        issues = []
        
        if not self.environmental_impact_templates:
            issues.append("Missing environmental impact templates")
        
        if not self.standard_outcome_metrics:
            issues.append("Missing standard outcome metrics")
        
        if not self.universal_regulatory_standards:
            issues.append("Missing universal regulatory standards")
        
        if issues:
            self.logger.warning(f"Pipeline configuration issues: {', '.join(issues)}")
            return False
        
        return True
    
    def get_pipeline_statistics(self, frontmatter: Dict) -> Dict[str, int]:
        """
        Get statistics about pipeline sections in frontmatter.
        
        Args:
            frontmatter: Generated frontmatter dict
            
        Returns:
            Dict with counts for each pipeline section
        """
        return {
            'environmental_impact_count': len(frontmatter.get('environmentalImpact', [])),
            'outcome_metrics_count': len(frontmatter.get('outcomeMetrics', [])),
            'regulatory_standards_count': len(frontmatter.get('regulatoryStandards', [])),
            'applications_count': len(frontmatter.get('applications', []))
        }
