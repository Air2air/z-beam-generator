"""
Pattern Researcher

Specialized researcher for contamination pattern data.
Researches detailed information about contamination patterns for dedicated pages.

Mirrors domains.materials.research.property_researcher.PropertyResearcher

Author: AI Assistant
Date: November 25, 2025
"""

import logging
from typing import Any, Dict, Optional
from domains.contaminants.research.base import (
    ContaminationResearcher,
    ContaminationResearchSpec,
    ContaminationResearchResult
)
from domains.contaminants.library import ContaminationLibrary
from shared.validation.errors import GenerationError

logger = logging.getLogger(__name__)


class PatternResearcher(ContaminationResearcher):
    """
    Researcher for contamination pattern data.
    
    Researches:
    - Detailed pattern descriptions
    - Formation conditions and chemistry
    - Visual characteristics and identification
    - Material compatibility and validation
    - Environmental factors and contexts
    
    Usage:
        researcher = PatternResearcher(api_client)
        result = researcher.research(
            pattern_id="rust_oxidation",
            research_spec=ContaminationResearchSpec(
                pattern_id="rust_oxidation",
                research_type="detailed_description",
                material_context="Steel"
            )
        )
    """
    
    # Research types supported by this researcher
    SUPPORTED_RESEARCH_TYPES = {
        'detailed_description',
        'formation_conditions',
        'visual_characteristics',
        'material_compatibility',
        'environmental_factors',
        'chemical_composition',
        'removal_methods'
    }
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.85
    ACCEPTABLE_CONFIDENCE = 0.75
    
    def __init__(self, api_client: Any):
        """
        Initialize pattern researcher.
        
        Args:
            api_client: API client for AI research
        
        Raises:
            ValueError: If api_client is None
        """
        super().__init__(api_client)
        self.library = ContaminationLibrary()
        self.logger = logging.getLogger(__name__)
    
    def research(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict] = None
    ) -> ContaminationResearchResult:
        """
        Research contamination pattern data.
        
        Args:
            pattern_id: Pattern identifier (rust_oxidation, copper_patina, etc.)
            research_spec: Research specification
            context: Additional context
        
        Returns:
            ContaminationResearchResult with discovered data
        
        Raises:
            GenerationError: If research fails critically
        """
        # Validate inputs
        if not pattern_id:
            raise GenerationError("Pattern ID required for contamination research")
        
        if research_spec.research_type not in self.SUPPORTED_RESEARCH_TYPES:
            raise GenerationError(
                f"Unsupported research type: {research_spec.research_type}. "
                f"Supported: {self.SUPPORTED_RESEARCH_TYPES}"
            )
        
        self.logger.info(f"Researching {research_spec.research_type} for pattern: {pattern_id}")
        
        # Load existing pattern data from Contaminants.yaml
        existing_pattern = self._load_existing_pattern(pattern_id)
        if not existing_pattern:
            raise GenerationError(
                f"Pattern '{pattern_id}' not found in Contaminants.yaml. "
                "Cannot research undefined pattern."
            )
        
        # Build research prompt
        prompt = self._build_prompt(pattern_id, research_spec, context)
        
        # Execute AI research
        try:
            response = self.api_client.generate(
                prompt=prompt,
                temperature=0.7,  # Balanced creativity/accuracy
                max_tokens=1000
            )
            
            # Parse response based on research type
            data = self._parse_response(response, research_spec.research_type)
            
            # Calculate confidence
            confidence = self._calculate_confidence(data, research_spec)
            
            # Create result
            result = ContaminationResearchResult(
                pattern_id=pattern_id,
                data=data,
                confidence=confidence,
                source="ai_research",
                metadata={
                    'research_type': research_spec.research_type,
                    'existing_data': existing_pattern,
                    'material_context': research_spec.material_context
                }
            )
            
            # Validate result
            if not self.validate_result(result, research_spec):
                result.error = "Validation failed - result does not meet schema requirements"
                result.confidence = 0.0
            
            return result
            
        except Exception as e:
            self.logger.error(f"Research failed for {pattern_id}: {str(e)}")
            return ContaminationResearchResult(
                pattern_id=pattern_id,
                data=None,
                confidence=0.0,
                source="ai_research",
                error=str(e)
            )
    
    def validate_result(
        self,
        result: ContaminationResearchResult,
        research_spec: ContaminationResearchSpec
    ) -> bool:
        """
        Validate research result meets schema requirements.
        
        Args:
            result: Research result
            research_spec: Research specification
        
        Returns:
            True if valid, False otherwise
        """
        if not result.data:
            return False
        
        # Validate based on research type
        if research_spec.research_type == 'detailed_description':
            # Must be string with minimum length
            return isinstance(result.data, str) and len(result.data) >= 50
        
        elif research_spec.research_type == 'formation_conditions':
            # Must be dict with required keys
            if not isinstance(result.data, dict):
                return False
            required_keys = {'temperature', 'humidity', 'duration'}
            return all(key in result.data for key in required_keys)
        
        elif research_spec.research_type == 'visual_characteristics':
            # Must be dict with color and texture info
            if not isinstance(result.data, dict):
                return False
            return 'color' in result.data and 'texture' in result.data
        
        elif research_spec.research_type == 'material_compatibility':
            # Must be dict with valid/invalid material lists
            if not isinstance(result.data, dict):
                return False
            return 'valid_materials' in result.data or 'invalid_materials' in result.data
        
        # Default validation - data exists and confidence acceptable
        return result.confidence >= self.ACCEPTABLE_CONFIDENCE
    
    def _build_prompt(
        self,
        pattern_id: str,
        research_spec: ContaminationResearchSpec,
        context: Optional[Dict] = None
    ) -> str:
        """
        Build AI research prompt for contamination pattern.
        
        Args:
            pattern_id: Pattern identifier
            research_spec: Research specification
            context: Additional context
        
        Returns:
            Formatted prompt string
        """
        # Load existing pattern for context
        existing_pattern = self._load_existing_pattern(pattern_id)
        
        pattern_name = existing_pattern.get('name', pattern_id) if existing_pattern else pattern_id
        scientific_name = existing_pattern.get('scientific_name', '') if existing_pattern else ''
        
        base_context = f"""
Research contamination pattern: {pattern_name}
Scientific name: {scientific_name}
Research type: {research_spec.research_type}
"""
        
        if research_spec.material_context:
            base_context += f"Material context: {research_spec.material_context}\n"
        
        if research_spec.environment:
            base_context += f"Environment: {research_spec.environment}\n"
        
        # Type-specific prompts
        if research_spec.research_type == 'detailed_description':
            return base_context + """
Provide a detailed technical description of this contamination pattern including:
- Scientific basis and chemical processes
- Formation mechanisms and conditions
- Visual appearance and identification characteristics
- Common occurrence contexts
- Relevance to laser cleaning applications

Keep description factual, technical, and suitable for professionals in the field.
Length: 200-400 words.
"""
        
        elif research_spec.research_type == 'formation_conditions':
            return base_context + """
Describe the formation conditions for this contamination pattern as a JSON object:
{
    "temperature": {"min": X, "max": Y, "unit": "°C", "description": "..."},
    "humidity": {"min": X, "max": Y, "unit": "%", "description": "..."},
    "duration": {"typical": "...", "minimum": "...", "description": "..."},
    "environmental_factors": ["factor1", "factor2", ...],
    "accelerating_conditions": ["condition1", "condition2", ...]
}

Provide realistic ranges based on scientific literature and industrial experience.
"""
        
        elif research_spec.research_type == 'visual_characteristics':
            return base_context + """
Describe the visual characteristics of this contamination as a JSON object:
{
    "color": {"primary": "...", "variations": [...], "description": "..."},
    "texture": {"description": "...", "tactile_properties": [...], "appearance": "..."},
    "thickness": {"typical": "...", "unit": "...", "variation": "..."},
    "pattern": {"distribution": "...", "uniformity": "...", "typical_formations": [...]},
    "identification_markers": ["marker1", "marker2", ...]
}

Focus on observable characteristics useful for identification and assessment.
"""
        
        elif research_spec.research_type == 'material_compatibility':
            return base_context + """
List materials compatible and incompatible with this contamination pattern as JSON:
{
    "valid_materials": {
        "primary": ["material1", "material2", ...],
        "conditional": {"material_name": "condition_description", ...}
    },
    "invalid_materials": ["material1", "material2", ...],
    "compatibility_notes": "...",
    "chemical_basis": "..."
}

Base compatibility on chemical composition and elemental requirements.
"""
        
        else:
            return base_context + f"""
Research and provide detailed information about: {research_spec.research_type}

Format: Provide structured, factual information suitable for technical documentation.
"""
    
    def _parse_response(
        self,
        response: str,
        research_type: str
    ) -> Any:
        """
        Parse AI response based on research type.
        
        Args:
            response: Raw AI response
            research_type: Type of research performed
        
        Returns:
            Parsed data structure
        """
        # For JSON-expected types, attempt JSON parsing
        if research_type in {'formation_conditions', 'visual_characteristics', 'material_compatibility'}:
            import json
            try:
                # Extract JSON from response (may have surrounding text)
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Default: return as string
        return response.strip()
    
    def _calculate_confidence(
        self,
        data: Any,
        research_spec: ContaminationResearchSpec
    ) -> float:
        """
        Calculate confidence score for research result.
        
        Args:
            data: Research result data
            research_spec: Research specification
        
        Returns:
            Confidence score 0.0 to 1.0
        """
        if not data:
            return 0.0
        
        confidence = 0.8  # Base confidence
        
        # Boost confidence for structured data
        if isinstance(data, dict):
            confidence += 0.05
            
            # Check completeness
            if research_spec.research_type == 'formation_conditions':
                required_keys = {'temperature', 'humidity', 'duration'}
                if all(key in data for key in required_keys):
                    confidence += 0.1
            
            elif research_spec.research_type == 'visual_characteristics':
                if 'color' in data and 'texture' in data and 'pattern' in data:
                    confidence += 0.1
            
            elif research_spec.research_type == 'material_compatibility':
                if 'valid_materials' in data and 'invalid_materials' in data:
                    confidence += 0.1
        
        # Boost for length (indicates thoroughness)
        if isinstance(data, str):
            if len(data) >= 200:
                confidence += 0.05
            if len(data) >= 400:
                confidence += 0.05
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def research_pattern_details(
        self,
        pattern_id: str,
        material_context: Optional[str] = None
    ) -> Dict[str, ContaminationResearchResult]:
        """
        Research all details for a contamination pattern.
        
        Convenience method that performs multiple research types.
        
        Args:
            pattern_id: Pattern identifier
            material_context: Optional material context
        
        Returns:
            Dict mapping research_type → ContaminationResearchResult
        """
        results = {}
        
        for research_type in self.SUPPORTED_RESEARCH_TYPES:
            spec = ContaminationResearchSpec(
                pattern_id=pattern_id,
                research_type=research_type,
                material_context=material_context
            )
            
            result = self.research(pattern_id, spec)
            results[research_type] = result
        
        return results
