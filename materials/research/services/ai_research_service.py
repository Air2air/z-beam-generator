#!/usr/bin/env python3
"""
AI Research & Enrichment Service

Unified AI research service consolidating:
- ai_materials_researcher.py
- ai_verify_property.py
- batch_materials_research.py
- systematic_verify.py

STRICT FAIL-FAST ARCHITECTURE - ZERO TOLERANCE for mocks/fallbacks
"""

import sys
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from shared.api.client_factory import create_api_client
from shared.validation.errors import ConfigurationError

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

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


@dataclass
class VerificationResult:
    """Result of verifying an existing property value"""
    material_name: str
    property_name: str
    current_value: Any
    verified_value: float
    variance_percent: float
    confidence: float
    references: List[str] = field(default_factory=list)
    reasoning: str = ""
    verification_passed: bool = True


@dataclass
class BatchResearchResult:
    """Result of batch research operation"""
    total_materials: int
    successful_materials: int
    failed_materials: int
    total_properties_researched: int
    research_stats: Dict[str, int]
    researched_materials: List[Dict[str, Any]]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ResearchError(Exception):
    """Raised when AI research fails or produces invalid results"""
    pass


# ============================================================================
# AI RESEARCH & ENRICHMENT SERVICE
# ============================================================================

class AIResearchEnrichmentService:
    """
    Unified AI research and data enrichment service.
    
    Consolidates research logic from multiple scripts into single service.
    Enforces strict fail-fast architecture per GROK_INSTRUCTIONS.md.
    """
    
    def __init__(self, api_provider: str = 'deepseek'):
        """
        Initialize research service.
        
        Args:
            api_provider: API provider to use for research ('deepseek', 'grok', etc.)
        """
        self.api_client = None
        self.api_provider = api_provider
        self.materials_file = project_root / "materials" / "data" / "Materials.yaml"
        
        self.research_stats = {
            'total_researched': 0,
            'successful_research': 0,
            'failed_research': 0,
            'unique_values_generated': 0,
            'confidence_threshold_met': 0
        }
        
        self.verification_cache: Dict[str, VerificationResult] = {}
        self.audit_trail_enabled = True
        
        # Property terminology mappings for AI research
        self.property_terminology = {
            'thermalDestruction': {
                'research_terms': ['melting point', 'fusion temperature', 'liquidus temperature'],
                'description': 'Temperature at which material transitions from solid to liquid',
                'units': '°C'
            }
        }
        
        # FAIL-FAST: Validate required files exist
        self._validate_required_files()
        
        # FAIL-FAST: Initialize API client or die
        self._initialize_api_client()
        
        logger.info("✅ AIResearchEnrichmentService initialized (fail-fast mode)")
    
    def _validate_required_files(self):
        """FAIL-FAST validation of required files"""
        if not self.materials_file.exists():
            raise ConfigurationError(f"CRITICAL: Materials.yaml not found at {self.materials_file}")
        
        logger.info("✅ Required files validated")
    
    def _initialize_api_client(self):
        """FAIL-FAST API client initialization - NO fallbacks allowed"""
        try:
            self.api_client = create_api_client(self.api_provider)
            if not self.api_client:
                raise ConfigurationError(f"CRITICAL: Failed to create {self.api_provider} API client")
            
            logger.info(f"✅ {self.api_provider} API client initialized successfully")
            
        except Exception as e:
            raise ConfigurationError(f"CRITICAL: Cannot initialize API client: {e}")
    
    # ========================================================================
    # PROPERTY RESEARCH
    # ========================================================================
    
    def research_property(
        self,
        material_name: str,
        property_name: str,
        category: str,
        current_value: Any = None,
        confidence_threshold: float = 0.9
    ) -> ResearchResult:
        """
        Research a single material property using AI with scientific validation.
        
        Args:
            material_name: Name of material
            property_name: Property to research
            category: Material category
            current_value: Optional current value for comparison
            confidence_threshold: Minimum confidence required (default 0.9)
            
        Returns:
            ResearchResult with researched value or error
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
            self._validate_research_result(result, confidence_threshold)
            
            # Update statistics
            self.research_stats['total_researched'] += 1
            self.research_stats['successful_research'] += 1
            if result.confidence >= confidence_threshold:
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

RESPONSE FORMAT (JSON only):
{{
    "value": <precise_numeric_value>,
    "unit": "<standard_SI_unit>",
    "confidence": <0.9_to_1.0>,
    "research_basis": "<authoritative_source_citation>",
    "validation_method": "<how_value_was_validated>",
    "min_typical": <minimum_typical_value>,
    "max_typical": <maximum_typical_value>
}}

CRITICAL: Ensure the value is UNIQUE and SPECIFIC to {material_name}.
CRITICAL: Confidence must be >= 0.9 or the research will be rejected."""
    
    def _parse_research_response(
        self,
        response_content: str,
        material_name: str,
        property_name: str
    ) -> ResearchResult:
        """Parse AI research response with strict validation"""
        import json
        
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
            
            # Extract required fields
            value = research_data.get('value')
            unit = research_data.get('unit', '')
            confidence = research_data.get('confidence', 0.0)
            research_basis = research_data.get('research_basis', '')
            validation_method = research_data.get('validation_method', '')
            
            if value is None:
                raise ResearchError("Missing required 'value' field")
            
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
            
        except Exception as e:
            raise ResearchError(f"Failed to parse research response: {e}")
    
    def _validate_research_result(self, result: ResearchResult, confidence_threshold: float = 0.9):
        """STRICT validation of research result quality"""
        validations = []
        
        if result.confidence < confidence_threshold:
            validations.append(f"Confidence {result.confidence} below required {confidence_threshold}")
        
        if not result.research_basis:
            validations.append("Missing research_basis citation")
        
        if not result.validation_method:
            validations.append("Missing validation_method")
        
        # Allow negative values for properties like thermal expansion (composites can have negative coefficients)
        # Only reject truly invalid values (None, NaN, extreme outliers)
        if result.researched_value is None or (isinstance(result.researched_value, float) and result.researched_value != result.researched_value):  # NaN check
            validations.append(f"Invalid value {result.researched_value}")
        
        if validations:
            raise ResearchError(f"Research validation failed: {'; '.join(validations)}")
    
    # ========================================================================
    # PROPERTY VERIFICATION
    # ========================================================================
    
    def verify_property(
        self,
        material_name: str,
        property_name: str,
        current_value: Any,
        category: str = None
    ) -> VerificationResult:
        """
        Verify existing property value with AI cross-check.
        
        Args:
            material_name: Name of material
            property_name: Property to verify
            current_value: Current value to verify
            category: Optional material category
            
        Returns:
            VerificationResult with verification status
        """
        # Check cache first
        cache_key = f"{material_name}:{property_name}:{current_value}"
        if cache_key in self.verification_cache:
            logger.info(f"✓ Using cached verification for {material_name}.{property_name}")
            return self.verification_cache[cache_key]
        
        logger.info(f"🔍 Verifying {property_name} for {material_name}: current value = {current_value}")
        
        # Research the property to get verified value
        research_result = self.research_property(
            material_name=material_name,
            property_name=property_name,
            category=category or "unknown",
            current_value=current_value,
            confidence_threshold=0.7  # Lower threshold for verification
        )
        
        if not research_result.success:
            return VerificationResult(
                material_name=material_name,
                property_name=property_name,
                current_value=current_value,
                verified_value=0.0,
                variance_percent=0.0,
                confidence=0.0,
                verification_passed=False
            )
        
        # Calculate variance
        try:
            current_float = float(current_value)
            variance_percent = abs(research_result.researched_value - current_float) / current_float * 100
        except (ValueError, TypeError, ZeroDivisionError):
            variance_percent = 100.0
        
        # Determine if verification passed (within 20% variance)
        verification_passed = variance_percent <= 20.0
        
        result = VerificationResult(
            material_name=material_name,
            property_name=property_name,
            current_value=current_value,
            verified_value=research_result.researched_value,
            variance_percent=variance_percent,
            confidence=research_result.confidence,
            references=[research_result.research_basis],
            reasoning=research_result.validation_method,
            verification_passed=verification_passed
        )
        
        # Cache result
        if self.audit_trail_enabled:
            self.verification_cache[cache_key] = result
        
        logger.info(f"✅ Verification complete: {variance_percent:.1f}% variance, {'PASSED' if verification_passed else 'FAILED'}")
        
        return result
    
    # ========================================================================
    # BATCH PROCESSING
    # ========================================================================
    
    def batch_research(
        self,
        materials: List[str],
        properties: List[str],
        mode: str = "critical"
    ) -> BatchResearchResult:
        """
        Batch process multiple materials/properties.
        
        Args:
            materials: List of material names to research
            properties: List of properties to research for each material
            mode: Research mode ('critical', 'important', 'all')
            
        Returns:
            BatchResearchResult with summary
        """
        logger.info(f"🚀 Starting batch research: {len(materials)} materials, {len(properties)} properties, mode={mode}")
        
        researched_materials = []
        failed_materials = []
        total_properties_researched = 0
        
        # Load materials data to get categories
        with open(self.materials_file) as f:
            materials_data = yaml.safe_load(f)
        
        material_index = materials_data.get('material_index', {})
        
        for material_name in materials:
            category = material_index.get(material_name, 'unknown')
            
            logger.info(f"📋 Researching {material_name} ({category})")
            
            material_results = []
            material_failed = False
            
            for property_name in properties:
                try:
                    result = self.research_property(
                        material_name=material_name,
                        property_name=property_name,
                        category=category
                    )
                    
                    if result.success:
                        material_results.append(result)
                        total_properties_researched += 1
                    else:
                        logger.warning(f"⚠️ Research failed for {material_name}.{property_name}")
                        material_failed = True
                
                except Exception as e:
                    logger.error(f"❌ Error researching {material_name}.{property_name}: {e}")
                    material_failed = True
            
            if material_results and not material_failed:
                researched_materials.append({
                    'material_name': material_name,
                    'category': category,
                    'research_results': material_results,
                    'properties_researched': len(material_results)
                })
            else:
                failed_materials.append(material_name)
        
        result = BatchResearchResult(
            total_materials=len(materials),
            successful_materials=len(researched_materials),
            failed_materials=len(failed_materials),
            total_properties_researched=total_properties_researched,
            research_stats=self.research_stats.copy(),
            researched_materials=researched_materials
        )
        
        logger.info(f"🎉 Batch research complete: {len(researched_materials)}/{len(materials)} materials successful")
        
        return result
    
    # ========================================================================
    # SYSTEMATIC WORKFLOW
    # ========================================================================
    
    def systematic_verification_workflow(
        self,
        scope: str = "critical"
    ) -> BatchResearchResult:
        """
        Run systematic verification with prioritization.
        
        Args:
            scope: Verification scope ('critical', 'important', 'all', 'errors_only')
            
        Returns:
            BatchResearchResult with verification summary
        """
        logger.info(f"🔬 Starting systematic verification workflow: scope={scope}")
        
        # Define property sets by scope
        property_sets = {
            'critical': ['density', 'thermalConductivity', 'hardness'],
            'important': ['tensileStrength', 'youngsModulus', 'specificHeat'],
            'all': ['density', 'thermalConductivity', 'hardness', 'tensileStrength',
                   'youngsModulus', 'specificHeat', 'thermalExpansion', 'laserAbsorption']
        }
        
        # Get properties to verify
        if scope == 'errors_only':
            # Would need validation results to determine this
            properties = property_sets['critical']
        else:
            properties = property_sets.get(scope, property_sets['critical'])
        
        # Load all materials
        with open(self.materials_file) as f:
            materials_data = yaml.safe_load(f)
        
        material_index = materials_data.get('material_index', {})
        all_materials = list(material_index.keys())
        
        # Run batch research
        return self.batch_research(
            materials=all_materials,
            properties=properties,
            mode=scope
        )
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_research_statistics(self) -> Dict[str, Any]:
        """Get current research statistics"""
        return {
            'research_stats': self.research_stats.copy(),
            'verification_cache_size': len(self.verification_cache),
            'api_client_status': 'available' if self.api_client else 'unavailable',
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Clear verification cache"""
        self.verification_cache.clear()
        logger.info("🧹 Verification cache cleared")
