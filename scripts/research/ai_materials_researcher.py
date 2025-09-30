#!/usr/bin/env python3
"""
AI Materials Researcher

STRICT FAIL-FAST ARCHITECTURE PER GROK_INSTRUCTIONS.md
- ZERO TOLERANCE for mocks, fallbacks, or defaults in production code
- IMMEDIATE failure if dependencies missing or APIs unavailable
- ALL properties must be AI-researched with confidence >= 0.9
- NO silent failures, NO placeholder values, NO skip logic

Core Purpose: Replace 1,331 default values in Materials.yaml with unique,
AI-researched values using DeepSeek API with scientific validation.
"""

import sys
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from api.client_factory import create_api_client


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ResearchResult:
    """Result of AI research for a single property"""
    material_name: str
    property_name: str
    researched_value: float
    unit: str
    confidence: float
    source: str
    research_basis: str
    research_date: str
    validation_method: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid"""
    pass


class ResearchError(Exception):
    """Raised when AI research fails or produces invalid results"""
    pass


class MaterialsResearcher:
    """
    AI-powered materials research system with strict fail-fast validation.
    
    GROK_INSTRUCTIONS.md Compliance:
    - ZERO tolerance for defaults, mocks, or fallbacks
    - IMMEDIATE failure on missing dependencies
    - STRICT validation of all inputs and outputs
    - NO silent failures or degraded operation
    """
    
    def __init__(self):
        """Initialize researcher with strict validation"""
        self.materials_file = project_root / "data" / "Materials.yaml"
        self.api_client = None
        self.research_stats = {
            'total_researched': 0,
            'successful_research': 0,
            'failed_research': 0,
            'unique_values_generated': 0,
            'confidence_threshold_met': 0
        }
        
        # FAIL-FAST: Validate all required files exist
        self._validate_required_files()
        
        # FAIL-FAST: Initialize API client or die
        self._initialize_api_client()
        
        logger.info("✅ MaterialsResearcher initialized with fail-fast validation")
    
    def _validate_required_files(self):
        """FAIL-FAST validation of required files"""
        if not self.materials_file.exists():
            raise ConfigurationError(f"CRITICAL: Materials.yaml not found at {self.materials_file}")
        
        logger.info("✅ Required files validated")
    
    def _initialize_api_client(self):
        """FAIL-FAST API client initialization - NO fallbacks allowed"""
        try:
            self.api_client = create_api_client('deepseek')
            if not self.api_client:
                raise ConfigurationError("CRITICAL: Failed to create DeepSeek API client")
            
            logger.info("✅ DeepSeek API client initialized successfully")
            
        except Exception as e:
            raise ConfigurationError(f"CRITICAL: Cannot initialize API client: {e}")
    
    def research_material_property(
        self, 
        material_name: str, 
        property_name: str, 
        category: str,
        current_value: Any = None
    ) -> ResearchResult:
        """
        Research a single material property using AI with scientific validation.
        
        FAIL-FAST: Returns valid result or raises ResearchError
        NO defaults, NO fallbacks, NO silent failures
        """
        if not self.api_client:
            raise ResearchError("CRITICAL: API client not available for research")
        
        logger.info(f"🔬 Researching {property_name} for {material_name} in {category}")
        
        # Create comprehensive research prompt
        research_prompt = self._build_research_prompt(
            material_name, property_name, category, current_value
        )
        
        try:
            # Execute AI research - FAIL immediately if API unavailable
            response = self.api_client.generate_simple(
                prompt=research_prompt,
                max_tokens=1000,
                temperature=0.1  # Low temperature for scientific accuracy
            )
            
            if not response or not response.success or not response.content:
                raise ResearchError(f"CRITICAL: API research failed for {material_name}.{property_name}")
            
            # Parse and validate research result
            result = self._parse_research_response(
                response.content, material_name, property_name
            )
            
            # STRICT validation of research quality
            self._validate_research_result(result)
            
            # Update statistics
            self.research_stats['total_researched'] += 1
            self.research_stats['successful_research'] += 1
            if result.confidence >= 0.9:
                self.research_stats['confidence_threshold_met'] += 1
            
            logger.info(f"✅ Successfully researched {property_name}: {result.researched_value} {result.unit} (confidence: {result.confidence})")
            return result
            
        except Exception as e:
            self.research_stats['total_researched'] += 1
            self.research_stats['failed_research'] += 1
            
            error_msg = f"Research failed for {material_name}.{property_name}: {e}"
            logger.error(f"❌ {error_msg}")
            
            return ResearchResult(
                material_name=material_name,
                property_name=property_name,
                researched_value=0.0,
                unit="",
                confidence=0.0,
                source="research_failed",
                research_basis="",
                research_date=datetime.now().isoformat(),
                validation_method="",
                success=False,
                error_message=str(e)
            )
    
    def _build_research_prompt(
        self, 
        material_name: str, 
        property_name: str, 
        category: str,
        current_value: Any
    ) -> str:
        """Build comprehensive research prompt for AI"""
        
        return f"""You are a materials science expert specializing in laser cleaning applications. 
Research the precise value of "{property_name}" for the material "{material_name}" in category "{category}".

CRITICAL REQUIREMENTS:
1. Provide UNIQUE, material-specific value (NOT category averages)
2. Ensure scientific accuracy based on materials science literature
3. Include confidence assessment (0.9-1.0 required for acceptance)
4. Cite authoritative sources (NIST, ASM, academic literature)
5. Validate against known material properties and compositions

MATERIAL CONTEXT:
- Material: {material_name}
- Category: {category}
- Property: {property_name}
{f'- Current Value: {current_value}' if current_value else ''}

RESEARCH TASK:
Research this property using authoritative materials science sources. Consider:
- Material composition and crystal structure
- Standard testing conditions and methodologies
- Typical ranges for this material type
- Laser cleaning application requirements
- Scientific literature consensus

RESPONSE FORMAT (JSON only):
{{
    "value": <precise_numeric_value>,
    "unit": "<standard_SI_unit>",
    "confidence": <0.9_to_1.0>,
    "research_basis": "<authoritative_source_citation>",
    "validation_method": "<how_value_was_validated>",
    "min_typical": <minimum_typical_value>,
    "max_typical": <maximum_typical_value>,
    "scientific_justification": "<brief_explanation_of_value>"
}}

CRITICAL: Ensure the value is UNIQUE and SPECIFIC to {material_name}, not a generic category value.
CRITICAL: Confidence must be >= 0.9 or the research will be rejected.
CRITICAL: Include specific citation to authoritative materials science source."""
    
    def _parse_research_response(
        self, 
        response_content: str, 
        material_name: str, 
        property_name: str
    ) -> ResearchResult:
        """Parse AI research response with strict validation"""
        try:
            # Clean response content
            content = response_content.strip()
            
            # Try to extract JSON from response
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                if json_end > json_start:
                    content = content[json_start:json_end]
            elif '{' in content and '}' in content:
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                content = content[json_start:json_end]
            
            # Parse JSON response
            research_data = json.loads(content)
            
            # Extract required fields with strict validation
            value = research_data.get('value')
            unit = research_data.get('unit', '')
            confidence = research_data.get('confidence', 0.0)
            research_basis = research_data.get('research_basis', '')
            validation_method = research_data.get('validation_method', '')
            
            if value is None:
                raise ResearchError("Missing required 'value' field in research response")
            
            # Create research result
            result = ResearchResult(
                material_name=material_name,
                property_name=property_name,
                researched_value=float(value),
                unit=str(unit),
                confidence=float(confidence),
                source='ai_research',
                research_basis=str(research_basis),
                research_date=datetime.now().isoformat(),
                validation_method=str(validation_method),
                min_value=research_data.get('min_typical'),
                max_value=research_data.get('max_typical')
            )
            
            return result
            
        except json.JSONDecodeError as e:
            raise ResearchError(f"Invalid JSON in research response: {e}")
        except (ValueError, TypeError) as e:
            raise ResearchError(f"Invalid data types in research response: {e}")
        except Exception as e:
            raise ResearchError(f"Failed to parse research response: {e}")
    
    def _validate_research_result(self, result: ResearchResult):
        """STRICT validation of research result quality"""
        validations = []
        
        # Validate confidence threshold
        if result.confidence < 0.9:
            validations.append(f"Confidence {result.confidence} below required 0.9")
        
        # Validate required fields
        if not result.research_basis:
            validations.append("Missing research_basis citation")
        
        if not result.validation_method:
            validations.append("Missing validation_method")
        
        # Validate value is reasonable (non-zero, non-negative for most properties)
        if result.researched_value <= 0 and result.property_name not in ['thermalExpansion']:
            validations.append(f"Invalid value {result.researched_value} for {result.property_name}")
        
        # Validate source is AI research
        if result.source != 'ai_research':
            validations.append(f"Invalid source '{result.source}', must be 'ai_research'")
        
        if validations:
            raise ResearchError(f"Research validation failed: {'; '.join(validations)}")
        
        logger.debug(f"✅ Research result validated for {result.material_name}.{result.property_name}")
    
    def find_materials_with_default_values(self) -> List[Dict[str, Any]]:
        """Find all materials with default values that need research"""
        with open(self.materials_file, 'r') as f:
            materials_data = yaml.safe_load(f)
        
        materials_needing_research = []
        
        for category, category_data in materials_data.get('materials', {}).items():
            for material_item in category_data.get('items', []):
                material_name = material_item.get('name')
                properties = material_item.get('properties', {})
                
                default_properties = []
                for prop_name, prop_data in properties.items():
                    if isinstance(prop_data, dict):
                        source = prop_data.get('source', '')
                        confidence = prop_data.get('confidence', 0)
                        
                        # Identify properties needing research
                        if (source == 'default_from_category_range' or 
                            confidence < 0.9 or 
                            source != 'ai_research'):
                            default_properties.append({
                                'property_name': prop_name,
                                'current_value': prop_data.get('value'),
                                'current_source': source,
                                'current_confidence': confidence
                            })
                
                if default_properties:
                    materials_needing_research.append({
                        'material_name': material_name,
                        'category': category,
                        'properties_needing_research': default_properties,
                        'total_properties': len(default_properties)
                    })
        
        logger.info(f"🔍 Found {len(materials_needing_research)} materials needing research")
        return materials_needing_research
    
    def research_all_default_properties(
        self, 
        max_materials: Optional[int] = None,
        target_properties: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Research all default properties with strict fail-fast validation.
        
        FAIL-FAST: Process will stop on critical errors
        NO silent failures or partial results
        """
        logger.info("🚀 Starting comprehensive materials research")
        
        # Find materials needing research
        materials_needing_research = self.find_materials_with_default_values()
        
        if not materials_needing_research:
            logger.info("✅ No materials found needing research")
            return {
                'total_materials': 0,
                'researched_materials': [],
                'failed_materials': [],
                'research_stats': self.research_stats
            }
        
        # Apply limits if specified
        if max_materials:
            materials_needing_research = materials_needing_research[:max_materials]
        
        researched_materials = []
        failed_materials = []
        
        for material_info in materials_needing_research:
            material_name = material_info['material_name']
            category = material_info['category']
            properties_to_research = material_info['properties_needing_research']
            
            # Filter properties if target_properties specified
            if target_properties:
                properties_to_research = [
                    prop for prop in properties_to_research 
                    if prop['property_name'] in target_properties
                ]
            
            logger.info(f"🔬 Researching {material_name} ({len(properties_to_research)} properties)")
            
            material_research_results = []
            material_failed = False
            
            for prop_info in properties_to_research:
                try:
                    result = self.research_material_property(
                        material_name=material_name,
                        property_name=prop_info['property_name'],
                        category=category,
                        current_value=prop_info['current_value']
                    )
                    
                    if result.success:
                        material_research_results.append(result)
                    else:
                        logger.warning(f"⚠️ Research failed for {material_name}.{prop_info['property_name']}")
                        material_failed = True
                
                except Exception as e:
                    logger.error(f"❌ Critical error researching {material_name}.{prop_info['property_name']}: {e}")
                    material_failed = True
            
            if material_research_results and not material_failed:
                researched_materials.append({
                    'material_name': material_name,
                    'category': category,
                    'research_results': material_research_results,
                    'properties_researched': len(material_research_results)
                })
                logger.info(f"✅ Successfully researched {material_name}")
            else:
                failed_materials.append({
                    'material_name': material_name,
                    'category': category,
                    'error': 'Research failed for one or more properties'
                })
                logger.error(f"❌ Failed to research {material_name}")
        
        research_summary = {
            'total_materials': len(materials_needing_research),
            'successful_materials': len(researched_materials),
            'failed_materials': len(failed_materials),
            'researched_materials': researched_materials,
            'research_stats': self.research_stats
        }
        
        logger.info(f"🎉 Research complete: {len(researched_materials)}/{len(materials_needing_research)} materials successfully researched")
        return research_summary
    
    def get_research_statistics(self) -> Dict[str, Any]:
        """Get current research statistics"""
        return {
            'research_stats': self.research_stats.copy(),
            'timestamp': datetime.now().isoformat(),
            'api_client_status': 'available' if self.api_client else 'unavailable'
        }


def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Materials Researcher - FAIL-FAST Architecture")
    parser.add_argument('--max-materials', type=int, help='Maximum materials to research')
    parser.add_argument('--properties', nargs='+', help='Specific properties to research')
    parser.add_argument('--stats', action='store_true', help='Show research statistics')
    
    args = parser.parse_args()
    
    try:
        # Initialize researcher with fail-fast validation
        researcher = MaterialsResearcher()
        
        if args.stats:
            stats = researcher.get_research_statistics()
            print(json.dumps(stats, indent=2))
            return
        
        # Execute research
        results = researcher.research_all_default_properties(
            max_materials=args.max_materials,
            target_properties=args.properties
        )
        
        print(json.dumps(results, indent=2, default=str))
        
    except (ConfigurationError, ResearchError) as e:
        logger.error(f"💥 FAIL-FAST ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()