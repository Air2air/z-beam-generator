#!/usr/bin/env python3
"""
AI Research Pipeline - Research Execution Engine

Executes AI research tasks to fill material property gaps using multiple
sources and validation strategies.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import time

from ai_research.core.bridge_system import PropertyGap, ResearchResult, ResearchStatus, ResearchPriority

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ResearchAgent:
    """Configuration for different research agents"""
    name: str
    description: str
    api_endpoint: Optional[str] = None
    specialties: List[str] = None
    reliability_score: float = 0.8
    cost_per_query: float = 0.01


class ResearchSourceManager:
    """Manages different research sources and their reliability"""
    
    def __init__(self):
        self.sources = {
            'wikipedia': ResearchAgent(
                name='Wikipedia Materials',
                description='Open-source materials database',
                specialties=['basic_properties', 'common_materials'],
                reliability_score=0.7,
                cost_per_query=0.0
            ),
            'matweb': ResearchAgent(
                name='MatWeb Database',
                description='Professional materials property database',
                specialties=['mechanical_properties', 'thermal_properties'],
                reliability_score=0.9,
                cost_per_query=0.0
            ),
            'nist': ResearchAgent(
                name='NIST Database',
                description='National Institute of Standards materials data',
                specialties=['thermal_properties', 'physical_properties'],
                reliability_score=0.95,
                cost_per_query=0.0
            ),
            'asm': ResearchAgent(
                name='ASM Materials Database',
                description='ASM International materials handbook',
                specialties=['mechanical_properties', 'metallurgy'],
                reliability_score=0.92,
                cost_per_query=0.05
            ),
            'ai_general': ResearchAgent(
                name='General AI Research',
                description='AI-powered research across multiple sources',
                specialties=['all_properties'],
                reliability_score=0.8,
                cost_per_query=0.02
            ),
            'laser_literature': ResearchAgent(
                name='Laser Literature Search',
                description='Specialized laser-materials interaction research',
                specialties=['laser_properties', 'ablation_threshold'],
                reliability_score=0.85,
                cost_per_query=0.03
            )
        }
    
    def get_best_sources_for_property(self, property_type: str, priority: ResearchPriority) -> List[str]:
        """Get the best research sources for a property type"""
        # Priority mapping for different property types
        source_priority = {
            'physical': ['nist', 'matweb', 'asm', 'ai_general'],
            'thermal': ['nist', 'matweb', 'asm', 'ai_general'],
            'mechanical': ['asm', 'matweb', 'ai_general', 'nist'],
            'optical': ['nist', 'ai_general', 'laser_literature'],
            'laser': ['laser_literature', 'ai_general', 'nist']
        }
        
        # Get sources for property type
        sources = source_priority.get(property_type, ['ai_general'])
        
        # For critical properties, use more sources
        if priority == ResearchPriority.CRITICAL:
            return sources[:4]  # Use top 4 sources
        elif priority == ResearchPriority.IMPORTANT:
            return sources[:3]  # Use top 3 sources
        else:
            return sources[:2]  # Use top 2 sources
    
    def get_source_info(self, source_name: str) -> Optional[ResearchAgent]:
        """Get information about a research source"""
        return self.sources.get(source_name)


class PropertyValidator:
    """Validates researched property values"""
    
    def __init__(self):
        self.unit_patterns = {
            'g/cm³': r'(\d+\.?\d*)\s*g/cm³?',
            '°C': r'(\d+\.?\d*)\s*°?C',
            'W/m·K': r'(\d+\.?\d*)\s*W/(m·?K)',
            'MPa': r'(\d+\.?\d*)\s*MPa',
            'GPa': r'(\d+\.?\d*)\s*GPa',
            'J/cm²': r'(\d+\.?\d*)\s*J/cm²?',
            '%': r'(\d+\.?\d*)\s*%',
            'HV': r'(\d+\.?\d*)\s*HV',
            'μm/m·K': r'(\d+\.?\d*)\s*(μm|µm)/m·?K'
        }
    
    def validate_value(self, property_gap: PropertyGap, researched_value: str) -> Tuple[bool, float, str]:
        """
        Validate a researched value against expected ranges and formats
        
        Returns:
            (is_valid, confidence_score, validation_notes)
        """
        validation_notes = []
        confidence_score = 1.0
        
        # Extract numerical value
        numeric_value = self._extract_numeric_value(researched_value, property_gap.expected_units)
        
        if numeric_value is None:
            return False, 0.0, "Could not extract numeric value"
        
        # Range validation
        if property_gap.validation_range:
            min_val, max_val = property_gap.validation_range
            if not (min_val <= numeric_value <= max_val):
                validation_notes.append(f"Value {numeric_value} outside expected range {min_val}-{max_val}")
                confidence_score *= 0.3
        
        # Unit validation
        if property_gap.expected_units not in researched_value:
            validation_notes.append(f"Expected units '{property_gap.expected_units}' not found in value")
            confidence_score *= 0.8
        
        # Physical reasonableness checks
        reasonableness_check = self._check_physical_reasonableness(
            property_gap.property_name, 
            numeric_value,
            property_gap.material_name
        )
        
        if not reasonableness_check[0]:
            validation_notes.append(reasonableness_check[1])
            confidence_score *= 0.5
        
        is_valid = confidence_score >= 0.5
        notes = "; ".join(validation_notes) if validation_notes else "Validation passed"
        
        return is_valid, confidence_score, notes
    
    def _extract_numeric_value(self, value_string: str, expected_units: str) -> Optional[float]:
        """Extract numeric value from a string with units"""
        pattern = self.unit_patterns.get(expected_units)
        
        if pattern:
            match = re.search(pattern, value_string)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        
        # Fallback: try to extract any number
        numbers = re.findall(r'(\d+\.?\d*)', value_string)
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        
        return None
    
    def _check_physical_reasonableness(self, property_name: str, value: float, material_name: str) -> Tuple[bool, str]:
        """Check if a value is physically reasonable for the property and material"""
        material_lower = material_name.lower()
        
        # Material-specific checks
        if 'wood' in material_lower:
            if property_name == 'density' and value > 2.0:
                return False, f"Density {value} g/cm³ too high for wood material"
            if property_name == 'melting_point' and value > 1000:
                return False, f"Melting point {value}°C too high for wood (decomposes before melting)"
        
        elif 'metal' in material_lower or any(metal in material_lower for metal in ['aluminum', 'steel', 'copper', 'titanium']):
            if property_name == 'density' and value < 1.0:
                return False, f"Density {value} g/cm³ too low for metal"
            if property_name == 'thermalConductivity' and value < 1:
                return False, f"Thermal conductivity {value} W/m·K too low for typical metal"
        
        elif 'ceramic' in material_lower:
            if property_name == 'thermalConductivity' and value > 200:
                return False, f"Thermal conductivity {value} W/m·K too high for typical ceramic"
        
        # General physical limits
        if property_name == 'density' and value <= 0:
            return False, "Density must be positive"
        
        if property_name == 'reflectance' and not (0 <= value <= 100):
            return False, "Reflectance must be between 0-100%"
        
        if property_name == 'emissivity' and not (0 <= value <= 1):
            return False, "Emissivity must be between 0-1"
        
        return True, "Physically reasonable"


class AIResearchPipeline:
    """Main AI research pipeline for filling property gaps"""
    
    def __init__(self):
        self.source_manager = ResearchSourceManager()
        self.validator = PropertyValidator()
        self.research_results = []
        self.failed_research = []
    
    def research_property_gap(self, property_gap: PropertyGap, max_sources: int = 3) -> Optional[ResearchResult]:
        """Research a single property gap using multiple sources"""
        logger.info(f"Researching {property_gap.property_name} for {property_gap.material_name}")
        
        # Get best sources for this property
        source_names = self.source_manager.get_best_sources_for_property(
            property_gap.property_type,
            property_gap.priority
        )[:max_sources]
        
        research_attempts = []
        
        for source_name in source_names:
            try:
                # Simulate research (in real implementation, this would call actual APIs)
                result = self._simulate_research(property_gap, source_name)
                if result:
                    research_attempts.append(result)
                    
                    # If we get a high-confidence result, we can stop
                    if result.confidence_score >= 0.9:
                        break
                        
            except Exception as e:
                logger.warning(f"Research failed for source {source_name}: {e}")
                continue
        
        if not research_attempts:
            logger.warning(f"No successful research for {property_gap.property_name} on {property_gap.material_name}")
            return None
        
        # Return the best result
        best_result = max(research_attempts, key=lambda r: r.confidence_score)
        
        if best_result.confidence_score >= 0.5:
            self.research_results.append(best_result)
            logger.info(f"Successfully researched {property_gap.property_name} for {property_gap.material_name} "
                       f"(confidence: {best_result.confidence_score:.2f})")
            return best_result
        else:
            self.failed_research.append(property_gap)
            logger.warning(f"Low confidence result for {property_gap.property_name} on {property_gap.material_name}")
            return None
    
    def _simulate_research(self, property_gap: PropertyGap, source_name: str) -> Optional[ResearchResult]:
        """
        Simulate AI research (replace with actual API calls in production)
        This is a placeholder that generates realistic test data
        """
        source_info = self.source_manager.get_source_info(source_name)
        
        # Simulate some delay
        time.sleep(0.1)
        
        # Generate realistic test values based on property type and material
        test_value = self._generate_test_value(property_gap)
        
        if test_value is None:
            return None
        
        # Validate the researched value
        is_valid, confidence, validation_notes = self.validator.validate_value(property_gap, test_value)
        
        if not is_valid:
            return None
        
        # Adjust confidence based on source reliability
        final_confidence = confidence * source_info.reliability_score
        
        result = ResearchResult(
            property_gap=property_gap,
            researched_value=test_value,
            confidence_score=final_confidence,
            sources_used=[source_name],
            research_notes=f"Researched using {source_info.description}",
            validation_status=validation_notes,
            timestamp=datetime.now(),
            researcher_id=f"ai_research_pipeline_{source_name}"
        )
        
        return result
    
    def _generate_test_value(self, property_gap: PropertyGap) -> Optional[str]:
        """Generate realistic test values for different properties and materials"""
        material = property_gap.material_name.lower()
        prop = property_gap.property_name
        units = property_gap.expected_units
        
        # Property-specific value generation
        test_values = {
            'density': {
                'aluminum': f"2.70 {units}",
                'steel': f"7.85 {units}",
                'copper': f"8.96 {units}",
                'titanium': f"4.51 {units}",
                'wood': f"0.6 {units}",
                'default': f"2.5 {units}"
            },
            'melting_point': {
                'aluminum': f"660 {units}",
                'steel': f"1370 {units}",
                'copper': f"1085 {units}",
                'titanium': f"1668 {units}",
                'wood': f"300 {units}",  # Decomposition temperature
                'default': f"800 {units}"
            },
            'thermalConductivity': {
                'aluminum': f"237 {units}",
                'steel': f"50 {units}",
                'copper': f"401 {units}",
                'titanium': f"22 {units}",
                'wood': f"0.12 {units}",
                'default': f"25 {units}"
            },
            'tensileStrength': {
                'aluminum': f"310 {units}",
                'steel': f"400 {units}",
                'copper': f"220 {units}",
                'titanium': f"434 {units}",
                'wood': f"40 {units}",
                'default': f"200 {units}"
            },
            'youngsModulus': {
                'aluminum': f"69 {units}",
                'steel': f"200 {units}",
                'copper': f"110 {units}",
                'titanium': f"116 {units}",
                'wood': f"12 {units}",
                'default': f"70 {units}"
            }
        }
        
        if prop in test_values:
            prop_values = test_values[prop]
            
            # Find matching material
            for mat_key, value in prop_values.items():
                if mat_key in material or mat_key == 'default':
                    return value
        
        return None
    
    def batch_research(self, property_gaps: List[PropertyGap], max_concurrent: int = 5) -> Dict[str, Any]:
        """Research multiple property gaps in batches"""
        logger.info(f"Starting batch research of {len(property_gaps)} property gaps")
        
        successful_research = []
        failed_research = []
        
        # Process in batches to avoid overwhelming APIs
        for i in range(0, len(property_gaps), max_concurrent):
            batch = property_gaps[i:i + max_concurrent]
            logger.info(f"Processing batch {i//max_concurrent + 1} ({len(batch)} items)")
            
            for gap in batch:
                result = self.research_property_gap(gap)
                if result:
                    successful_research.append(result)
                else:
                    failed_research.append(gap)
            
            # Brief pause between batches
            time.sleep(1)
        
        summary = {
            'total_gaps': len(property_gaps),
            'successful_research': len(successful_research),
            'failed_research': len(failed_research),
            'success_rate': len(successful_research) / len(property_gaps) * 100,
            'results': successful_research,
            'failures': failed_research
        }
        
        logger.info(f"Batch research completed: {summary['success_rate']:.1f}% success rate "
                   f"({summary['successful_research']}/{summary['total_gaps']})")
        
        return summary
    
    def generate_research_report(self) -> Dict[str, Any]:
        """Generate comprehensive research report"""
        if not self.research_results:
            return {'error': 'No research results available'}
        
        # Group results by property type
        by_property = {}
        by_material = {}
        
        for result in self.research_results:
            prop_name = result.property_gap.property_name
            material_name = result.property_gap.material_name
            
            if prop_name not in by_property:
                by_property[prop_name] = []
            by_property[prop_name].append(result)
            
            if material_name not in by_material:
                by_material[material_name] = []
            by_material[material_name].append(result)
        
        # Calculate statistics
        confidence_scores = [r.confidence_score for r in self.research_results]
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        
        report = {
            'research_summary': {
                'total_results': len(self.research_results),
                'total_failures': len(self.failed_research),
                'average_confidence': avg_confidence,
                'properties_researched': len(by_property),
                'materials_researched': len(by_material)
            },
            'by_property': {prop: len(results) for prop, results in by_property.items()},
            'by_material': {mat: len(results) for mat, results in by_material.items()},
            'high_confidence_results': [
                r for r in self.research_results if r.confidence_score >= 0.8
            ],
            'low_confidence_results': [
                r for r in self.research_results if r.confidence_score < 0.6
            ]
        }
        
        return report


if __name__ == "__main__":
    # Test the research pipeline
    from .bridge_system import PropertyDefinitions, ResearchDifficulty
    
    # Create test property gap
    test_gap = PropertyGap(
        material_name="Aluminum",
        property_name="density",
        property_type="physical",
        priority=ResearchPriority.CRITICAL,
        difficulty=ResearchDifficulty.EASY,
        sources=["MatWeb", "NIST"],
        research_query="What is the density of Aluminum in g/cm³?",
        expected_units="g/cm³",
        validation_range=(2.0, 3.0)
    )
    
    # Test research pipeline
    pipeline = AIResearchPipeline()
    result = pipeline.research_property_gap(test_gap)
    
    if result:
        print("=== AI RESEARCH PIPELINE TEST ===")
        print(f"Material: {result.property_gap.material_name}")
        print(f"Property: {result.property_gap.property_name}")
        print(f"Researched Value: {result.researched_value}")
        print(f"Confidence: {result.confidence_score:.2f}")
        print(f"Validation: {result.validation_status}")
    else:
        print("Research failed")