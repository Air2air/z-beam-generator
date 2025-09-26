#!/usr/bin/env python3
"""
Unified Research Interface - Complete Material and Machine Settings Research

This module provides a unified interface that combines PropertyValueResearcher 
(for material properties) and MachineSettingsResearcher (for laser parameters)
into a single, seamless research system.

Key Features:
1. Unified research interface for both material properties and machine settings
2. Intelligent routing to appropriate researcher based on request type
3. Cross-researcher data sharing (machine settings use material properties)
4. Integrated caching and performance monitoring
5. Complete YAML frontmatter generation matching your Zirconia file format

Author: GitHub Copilot
Date: September 25, 2025
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import time

# Import the specialized researchers
from .property_value_researcher import PropertyValueResearcher, ResearchContext, PropertyResult
from .machine_settings_researcher import MachineSettingsResearcher, LaserProcessingContext, MachineSettingResult


@dataclass
class UnifiedResearchResult:
    """Combined result from both material and machine research"""
    material_properties: Dict[str, PropertyResult]
    machine_settings: Dict[str, MachineSettingResult]
    research_time: float
    success_rate: float
    quality_score: float
    
    def to_complete_frontmatter(self) -> Dict[str, Any]:
        """Generate complete frontmatter structure like your Zirconia file"""
        
        frontmatter = {
            'materialProperties': {},
            'machineSettings': {}
        }
        
        # Add material properties
        for prop_name, result in self.material_properties.items():
            if result.is_valid():
                frontmatter['materialProperties'][prop_name] = result.to_property_data_metric()
        
        # Add machine settings  
        for setting_name, result in self.machine_settings.items():
            if result.is_valid():
                frontmatter['machineSettings'][setting_name] = result.to_machine_setting_format()
                
        return frontmatter
    
    def get_quality_assessment(self) -> Dict[str, Any]:
        """Assess overall research quality"""
        
        total_properties = len(self.material_properties) + len(self.machine_settings)
        valid_properties = len([r for r in self.material_properties.values() if r.is_valid()])
        valid_settings = len([r for r in self.machine_settings.values() if r.is_valid()])
        
        total_valid = valid_properties + valid_settings
        
        high_quality_props = len([r for r in self.material_properties.values() if r.is_high_quality()])
        high_quality_settings = len([r for r in self.machine_settings.values() if r.is_high_quality()])
        
        return {
            'total_items_researched': total_properties,
            'valid_results': total_valid,
            'success_rate': (total_valid / total_properties) * 100 if total_properties > 0 else 0,
            'high_quality_results': high_quality_props + high_quality_settings,
            'quality_percentage': ((high_quality_props + high_quality_settings) / total_valid) * 100 if total_valid > 0 else 0,
            'material_properties_found': valid_properties,
            'machine_settings_found': valid_settings,
            'research_time_seconds': self.research_time
        }


class UnifiedMaterialResearcher:
    """
    Unified interface for complete material and machine settings research.
    
    This class orchestrates both PropertyValueResearcher and MachineSettingsResearcher
    to provide comprehensive research capabilities for laser processing content generation.
    
    Core Capabilities:
    1. Research material properties (density, melting point, etc.)
    2. Research machine settings (power, wavelength, pulse duration, etc.)
    3. Cross-reference material properties to optimize machine settings
    4. Generate complete frontmatter structures matching your file format
    5. Quality assessment and content generation recommendations
    """
    
    def __init__(self, 
                 confidence_threshold: int = 50,
                 debug_mode: bool = False):
        """
        Initialize the unified researcher.
        
        Args:
            confidence_threshold: Minimum confidence for valid results
            debug_mode: Enable debug logging
        """
        # Initialize the specialized researchers
        self.property_researcher = PropertyValueResearcher(
            min_confidence_threshold=confidence_threshold,
            debug_mode=debug_mode
        )
        
        self.machine_researcher = MachineSettingsResearcher(
            material_researcher=self.property_researcher,  # Share material researcher
            confidence_threshold=confidence_threshold,
            debug_mode=debug_mode
        )
        
        self.confidence_threshold = confidence_threshold
        self.debug_mode = debug_mode
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        if debug_mode:
            self.logger.setLevel(logging.DEBUG)
            
        # Combined statistics
        self.unified_stats = {
            'total_unified_requests': 0,
            'successful_unified_research': 0,
            'avg_unified_response_time': 0.0
        }
    
    def research_complete_material(self, 
                                 material_name: str,
                                 material_category: str = "unknown",
                                 application_type: str = "cleaning",
                                 laser_wavelength: str = "1064nm") -> UnifiedResearchResult:
        """
        Research complete material profile - THE MAIN OPERATION.
        
        This researches both material properties and optimal machine settings
        for a complete material processing profile.
        
        Args:
            material_name: Name of material (e.g., "Zirconia")
            material_category: Material category (ceramic, metal, polymer)
            application_type: Laser application (cleaning, cutting, marking, welding)
            laser_wavelength: Target wavelength for processing
            
        Returns:
            UnifiedResearchResult with complete material and machine data
            
        Example:
            researcher = UnifiedMaterialResearcher()
            result = researcher.research_complete_material("Zirconia", "ceramic", "cleaning")
            frontmatter = result.to_complete_frontmatter()
        """
        start_time = time.time()
        self.unified_stats['total_unified_requests'] += 1
        
        if self.debug_mode:
            self.logger.info(f"🔬 Starting complete research for {material_name} ({material_category})")
        
        # Setup research contexts
        material_context = ResearchContext(
            material_category=material_category,
            laser_wavelength=laser_wavelength,
            application_type=application_type,
            priority_level=1
        )
        
        processing_context = LaserProcessingContext(
            application_type=application_type,
            target_wavelength=laser_wavelength
        )
        
        # Research material properties
        material_properties = self._research_material_properties(material_name, material_context)
        
        # Research machine settings (using material properties for optimization)
        machine_settings = self._research_machine_settings(material_name, processing_context)
        
        # Calculate performance metrics
        research_time = time.time() - start_time
        self._update_unified_response_time(research_time)
        
        # Calculate success rate
        total_items = len(material_properties) + len(machine_settings) 
        valid_items = len([r for r in material_properties.values() if r.is_valid()]) + \
                     len([r for r in machine_settings.values() if r.is_valid()])
        
        success_rate = (valid_items / total_items) * 100 if total_items > 0 else 0
        
        # Calculate quality score
        high_quality_items = len([r for r in material_properties.values() if r.is_high_quality()]) + \
                           len([r for r in machine_settings.values() if r.is_high_quality()])
        
        quality_score = (high_quality_items / valid_items) * 100 if valid_items > 0 else 0
        
        if success_rate >= 60:
            self.unified_stats['successful_unified_research'] += 1
            
        result = UnifiedResearchResult(
            material_properties=material_properties,
            machine_settings=machine_settings,
            research_time=research_time,
            success_rate=success_rate,
            quality_score=quality_score
        )
        
        if self.debug_mode:
            self.logger.info(f"✅ Complete research finished: {success_rate:.1f}% success rate, {quality_score:.1f}% quality score")
            
        return result
    
    def research_zirconia_example(self) -> UnifiedResearchResult:
        """
        Research your exact Zirconia example for demonstration.
        
        This shows how the unified researcher works with your actual data.
        """
        return self.research_complete_material(
            material_name="Zirconia",
            material_category="ceramic", 
            application_type="cleaning",
            laser_wavelength="1064nm"
        )
    
    def _research_material_properties(self, 
                                    material_name: str,
                                    context: ResearchContext) -> Dict[str, PropertyResult]:
        """Research key material properties"""
        
        # Properties matching your Zirconia file structure
        property_names = [
            'density',
            'meltingPoint', 
            'thermalConductivity',
            'hardness',
            'thermalShockResistance'
        ]
        
        if self.debug_mode:
            self.logger.info(f"🔍 Researching {len(property_names)} material properties")
            
        return self.property_researcher.batch_research_properties(
            material_name, property_names, context
        )
    
    def _research_machine_settings(self, 
                                 material_name: str,
                                 context: LaserProcessingContext) -> Dict[str, MachineSettingResult]:
        """Research optimal machine settings"""
        
        # Machine settings matching your Zirconia file structure
        setting_names = [
            'powerRange',
            'wavelength',
            'pulseDuration', 
            'spotSize',
            'repetitionRate',
            'fluenceRange',
            'ablationThreshold',
            'processingSpeed'
        ]
        
        if self.debug_mode:
            self.logger.info(f"⚙️ Researching {len(setting_names)} machine settings")
            
        return self.machine_researcher.batch_research_machine_settings(
            material_name, setting_names, context
        )
    
    def generate_content_recommendation(self, result: UnifiedResearchResult) -> Dict[str, Any]:
        """
        Generate content generation recommendations based on research results.
        
        This determines whether you have enough data to generate high-quality
        laser processing content.
        """
        quality = result.get_quality_assessment()
        
        # Content generation decision logic
        if quality['success_rate'] >= 80 and quality['quality_percentage'] >= 70:
            recommendation = "🚀 FULL CONTENT GENERATION RECOMMENDED"
            content_quality = "premium"
            confidence_level = "high"
        elif quality['success_rate'] >= 60 and quality['quality_percentage'] >= 50:
            recommendation = "⚡ STANDARD CONTENT GENERATION"
            content_quality = "standard"
            confidence_level = "medium"
        elif quality['success_rate'] >= 40:
            recommendation = "📝 BASIC CONTENT GENERATION"
            content_quality = "basic"
            confidence_level = "low"
        else:
            recommendation = "❌ CONTENT GENERATION NOT RECOMMENDED"
            content_quality = "insufficient"
            confidence_level = "very_low"
            
        return {
            'recommendation': recommendation,
            'content_quality': content_quality,
            'confidence_level': confidence_level,
            'data_completeness': f"{quality['success_rate']:.1f}%",
            'quality_score': f"{quality['quality_percentage']:.1f}%",
            'material_properties_available': quality['material_properties_found'],
            'machine_settings_available': quality['machine_settings_found'],
            'research_duration': f"{quality['research_time_seconds']:.3f}s",
            'next_steps': self._generate_next_steps(quality)
        }
    
    def _generate_next_steps(self, quality: Dict[str, Any]) -> List[str]:
        """Generate recommended next steps based on research quality"""
        steps = []
        
        if quality['material_properties_found'] < 3:
            steps.append("🔍 Research additional material properties for better accuracy")
            
        if quality['machine_settings_found'] < 4:  
            steps.append("⚙️ Research more machine settings for comprehensive processing guide")
            
        if quality['quality_percentage'] < 60:
            steps.append("📊 Verify low-confidence data with additional sources")
            
        if quality['success_rate'] < 50:
            steps.append("🚨 Consider alternative research strategies or data sources")
            
        if not steps:
            steps.append("✅ Research is complete - ready for content generation")
            
        return steps
    
    def _update_unified_response_time(self, response_time: float):
        """Update unified response time statistics"""
        current_avg = self.unified_stats['avg_unified_response_time']
        total_requests = self.unified_stats['total_unified_requests']
        
        if total_requests == 1:
            self.unified_stats['avg_unified_response_time'] = response_time
        else:
            self.unified_stats['avg_unified_response_time'] = (current_avg * 0.9) + (response_time * 0.1)
    
    def get_combined_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all researchers"""
        
        property_stats = self.property_researcher.get_research_statistics()
        machine_stats = self.machine_researcher.get_research_statistics()
        
        return {
            'unified_research': self.unified_stats,
            'property_research': property_stats,
            'machine_research': machine_stats,
            'total_requests': property_stats['total_requests'] + machine_stats['total_requests'],
            'combined_success_rate': self._calculate_combined_success_rate(property_stats, machine_stats)
        }
    
    def _calculate_combined_success_rate(self, prop_stats: Dict, machine_stats: Dict) -> float:
        """Calculate overall success rate across both researchers"""
        
        total_requests = prop_stats['total_requests'] + machine_stats['total_requests']
        total_failures = prop_stats['failures'] + machine_stats['failures']
        
        if total_requests == 0:
            return 0.0
            
        return ((total_requests - total_failures) / total_requests) * 100
    
    # Convenience methods for specific research types
    
    def research_material_properties_only(self, material_name: str, material_category: str = "unknown") -> Dict[str, PropertyResult]:
        """Research only material properties"""
        context = ResearchContext(material_category=material_category)
        return self._research_material_properties(material_name, context)
    
    def research_machine_settings_only(self, material_name: str, application_type: str = "cleaning") -> Dict[str, MachineSettingResult]:
        """Research only machine settings"""
        context = LaserProcessingContext(application_type=application_type)
        return self._research_machine_settings(material_name, context)
    
    def research_single_property(self, material_name: str, property_name: str) -> PropertyResult:
        """Research a single material property"""
        return self.property_researcher.research_property_value(material_name, property_name)
    
    def research_single_machine_setting(self, material_name: str, setting_name: str, application_type: str = "cleaning") -> MachineSettingResult:
        """Research a single machine setting"""
        context = LaserProcessingContext(application_type=application_type)
        return self.machine_researcher.research_machine_setting(material_name, setting_name, context)