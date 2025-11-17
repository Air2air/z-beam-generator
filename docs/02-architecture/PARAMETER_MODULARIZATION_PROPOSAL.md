# Parameter Modularization & Dynamic Prompt Architecture Proposal

**Date**: January 2025  
**Status**: 🎯 Proposed Architecture  
**Goal**: Transform scattered parameter logic into modular, testable, maintainable system

---

## 📋 Executive Summary

### Current State (Scattered)
- **14 parameters** defined in `config.yaml`
- **Parameter mapping** in `dynamic_config.py` (calculate_voice_parameters)
- **Prompt logic** scattered throughout `prompt_builder.py` (610 lines)
- **3-tier conditional logic** embedded inline for each parameter
- **Testing** requires reading entire prompt_builder.py
- **Maintenance** requires finding specific parameter logic among 600+ lines

### Proposed State (Modular)
- **14 parameter modules** in `processing/parameters/` directory
- **Each parameter** is self-contained: config, prompt generation, testing
- **Prompt builder** orchestrates parameter modules (simplified to ~200 lines)
- **Dynamic prompt evaluation** system validates orchestrated output
- **Testing** isolated per parameter
- **Maintenance** one file per parameter

---

## 🏗️ Proposed Architecture

### Directory Structure
```
processing/
├── parameters/
│   ├── __init__.py
│   ├── base.py                          # BaseParameter abstract class
│   ├── registry.py                      # ParameterRegistry for discovery
│   ├── evaluator.py                     # PromptEvaluator for quality validation
│   │
│   ├── voice/                           # Voice & Style Parameters (6)
│   │   ├── __init__.py
│   │   ├── author_voice_intensity.py
│   │   ├── personality_intensity.py
│   │   ├── engagement_style.py
│   │   ├── emotional_intensity.py
│   │   ├── professional_voice.py
│   │   └── jargon_removal.py
│   │
│   ├── technical/                       # Technical Content Parameters (2)
│   │   ├── __init__.py
│   │   ├── technical_language_intensity.py
│   │   └── context_specificity.py
│   │
│   ├── variation/                       # Variation & Imperfection Parameters (4)
│   │   ├── __init__.py
│   │   ├── sentence_rhythm_variation.py
│   │   ├── imperfection_tolerance.py
│   │   ├── structural_predictability.py
│   │   └── length_variation_range.py
│   │
│   └── ai_detection/                    # AI Detection Parameters (2)
│       ├── __init__.py
│       ├── ai_avoidance_intensity.py
│       └── humanness_intensity.py
│
├── generation/
│   ├── prompt_builder.py                # SIMPLIFIED orchestrator (~200 lines)
│   └── prompt_evaluator.py              # Quality validation of orchestrated prompts
│
└── config/
    ├── dynamic_config.py                # SIMPLIFIED parameter loading only
    └── config.yaml                      # Single source of truth for values
```

---

## 🎯 Core Components

### 1. BaseParameter (Abstract Class)

**File**: `processing/parameters/base.py`

```python
"""
Base Parameter Module

All parameters inherit from this to ensure consistent interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from enum import Enum


class ParameterCategory(Enum):
    """Parameter categories for organization"""
    VOICE = "voice"
    TECHNICAL = "technical"
    VARIATION = "variation"
    AI_DETECTION = "ai_detection"


class ParameterTier(Enum):
    """Three-tier system for all parameters"""
    LOW = "low"          # < 0.3
    MODERATE = "moderate"  # 0.3 - 0.7
    HIGH = "high"        # > 0.7


class BaseParameter(ABC):
    """
    Abstract base class for all configuration parameters.
    
    Each parameter must implement:
    1. normalize() - Convert config value (1-10) to 0.0-1.0
    2. get_tier() - Determine low/moderate/high tier
    3. generate_prompt_guidance() - Create prompt text for this parameter
    4. get_metadata() - Return parameter information
    
    This creates a consistent, testable interface for all parameters.
    """
    
    def __init__(self, config_value: int):
        """
        Initialize parameter with config value.
        
        Args:
            config_value: Raw value from config.yaml (typically 1-10)
        """
        self.config_value = config_value
        self.normalized_value = self.normalize(config_value)
        self.tier = self.get_tier(self.normalized_value)
    
    @abstractmethod
    def normalize(self, value: int) -> float:
        """
        Convert config value to normalized 0.0-1.0 scale.
        
        Args:
            value: Raw config value (1-10 or 1-3)
            
        Returns:
            Normalized float between 0.0 and 1.0
        """
        pass
    
    @abstractmethod
    def get_tier(self, normalized: float) -> ParameterTier:
        """
        Determine which tier this normalized value falls into.
        
        Args:
            normalized: Normalized value (0.0-1.0)
            
        Returns:
            ParameterTier (LOW, MODERATE, or HIGH)
        """
        pass
    
    @abstractmethod
    def generate_prompt_guidance(
        self,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate prompt guidance text for this parameter.
        
        Args:
            context: Context dict with keys:
                - length: Target word count
                - component_type: subtitle, caption, etc.
                - voice: Voice profile dict
                - other parameters as needed
                
        Returns:
            Prompt guidance string or None if no guidance needed
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return parameter metadata for documentation and testing.
        
        Returns:
            Dict with:
                - name: Parameter name
                - category: ParameterCategory enum
                - scale: "1-10" or "1-3"
                - description: What this parameter controls
                - maps_to: "voice_params", "enrichment_params", or "direct"
        """
        pass
    
    def get_voice_param_value(self) -> float:
        """
        Get value for voice_params dict.
        Most parameters use normalized_value, override if different.
        """
        return self.normalized_value
    
    def __repr__(self) -> str:
        meta = self.get_metadata()
        return f"{meta['name']}(config={self.config_value}, normalized={self.normalized_value:.3f}, tier={self.tier.value})"


class Scale10Parameter(BaseParameter):
    """Base class for 1-10 scale parameters"""
    
    def normalize(self, value: int) -> float:
        """Map 1-10 to 0.0-1.0"""
        return (value - 1) / 9.0
    
    def get_tier(self, normalized: float) -> ParameterTier:
        """Standard tier thresholds"""
        if normalized < 0.3:
            return ParameterTier.LOW
        elif normalized < 0.7:
            return ParameterTier.MODERATE
        else:
            return ParameterTier.HIGH


class Scale3Parameter(BaseParameter):
    """Base class for 1-3 scale parameters"""
    
    def normalize(self, value: int) -> float:
        """Map 1-3 to 0.0/0.5/1.0"""
        return (value - 1) * 0.5
    
    def get_tier(self, normalized: float) -> ParameterTier:
        """1→LOW, 2→MODERATE, 3→HIGH"""
        if normalized < 0.25:
            return ParameterTier.LOW
        elif normalized < 0.75:
            return ParameterTier.MODERATE
        else:
            return ParameterTier.HIGH
```

---

### 2. Example Parameter Module

**File**: `processing/parameters/variation/sentence_rhythm_variation.py`

```python
"""
Sentence Rhythm Variation Parameter

Controls how much sentence lengths vary within generated content.

- LOW (1-3): Uniform, consistent sentence lengths
- MODERATE (4-7): Mix short and medium sentences
- HIGH (8-10): Dramatic variation in sentence lengths

Mapping:
- Config: 1-10 scale
- Normalized: 0.0-1.0
- Voice params: 'sentence_rhythm_variation'
"""

from typing import Dict, Any, Optional
from processing.parameters.base import Scale10Parameter, ParameterCategory, ParameterTier


class SentenceRhythmVariation(Scale10Parameter):
    """
    Controls sentence length variation in generated content.
    
    Examples:
        LOW (1-3):
            "Maintain uniform sentence lengths (15-20 words)"
            
        MODERATE (4-7):
            "Mix short (5-8 words) and medium (10-14 words) sentences"
            
        HIGH (8-10):
            "WILD variation - mix very short (3-5 words) with 
            much longer (15-20 words); unpredictable rhythm"
    """
    
    def generate_prompt_guidance(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Generate sentence structure guidance based on tier and length.
        
        Args:
            context: Must contain 'length' (target word count)
            
        Returns:
            Prompt guidance string
        """
        length = context.get('length', 50)
        
        if self.tier == ParameterTier.LOW:
            # Uniform, consistent
            if length <= 30:
                return "- Sentence structure: Keep sentences consistent (8-12 words); maintain uniform rhythm"
            elif length <= 100:
                return "- Sentence structure: Use consistent sentence lengths (12-16 words); avoid dramatic variation"
            else:
                return "- Sentence structure: Maintain steady rhythm (14-18 words per sentence); consistent flow"
        
        elif self.tier == ParameterTier.MODERATE:
            # Mix short and medium
            if length <= 30:
                return "- Sentence structure: Mix short (5-8 words) and medium (10-14 words) sentences naturally"
            elif length <= 100:
                return "- Sentence structure: Balance short and medium sentences; vary rhythm naturally"
            else:
                return "- Sentence structure: Mix short, medium, and longer sentences for natural flow"
        
        else:  # HIGH
            # Dramatic variation
            if length <= 30:
                return "- Sentence structure: WILD variation - mix very short (3-5 words) with much longer (15-20 words); unpredictable rhythm"
            elif length <= 100:
                return "- Sentence structure: DRAMATIC variation - alternate between very short (3-6 words) and long (18-25 words); avoid patterns"
            else:
                return "- Sentence structure: EXTREME variation - range from tiny (2-4 words) to extended (25+ words); chaotic, unpredictable rhythm"
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'name': 'sentence_rhythm_variation',
            'category': ParameterCategory.VARIATION,
            'scale': '1-10',
            'description': 'Controls how much sentence lengths vary within generated content',
            'maps_to': 'voice_params',
            'examples': {
                'low': 'Uniform, consistent sentence lengths',
                'moderate': 'Mix short and medium sentences',
                'high': 'Dramatic variation in sentence lengths'
            }
        }
```

---

### 3. Parameter Registry

**File**: `processing/parameters/registry.py`

```python
"""
Parameter Registry

Auto-discovers and manages all parameter modules.
Provides factory pattern for parameter creation.
"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, Type, List, Optional
from processing.parameters.base import BaseParameter, ParameterCategory


class ParameterRegistry:
    """
    Central registry for all parameter modules.
    
    Auto-discovers parameters in processing/parameters/
    Provides factory methods to create parameter instances.
    """
    
    def __init__(self):
        self._parameters: Dict[str, Type[BaseParameter]] = {}
        self._discover_parameters()
    
    def _discover_parameters(self):
        """
        Auto-discover all parameter modules by scanning directories.
        """
        base_path = Path(__file__).parent
        
        # Scan subdirectories: voice/, technical/, variation/, ai_detection/
        for category_dir in ['voice', 'technical', 'variation', 'ai_detection']:
            category_path = base_path / category_dir
            if not category_path.exists():
                continue
            
            # Find all .py files except __init__.py
            for py_file in category_path.glob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                
                # Import module
                module_name = f'processing.parameters.{category_dir}.{py_file.stem}'
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find BaseParameter subclasses
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseParameter) and obj != BaseParameter:
                            # Register by metadata name
                            instance = obj(5)  # Dummy instance to get metadata
                            param_name = instance.get_metadata()['name']
                            self._parameters[param_name] = obj
                except ImportError as e:
                    print(f"Warning: Could not import {module_name}: {e}")
    
    def create_parameter(self, name: str, config_value: int) -> BaseParameter:
        """
        Create parameter instance by name.
        
        Args:
            name: Parameter name (e.g., 'sentence_rhythm_variation')
            config_value: Value from config.yaml
            
        Returns:
            Parameter instance
            
        Raises:
            KeyError: If parameter name not found
        """
        if name not in self._parameters:
            raise KeyError(f"Parameter '{name}' not registered. Available: {list(self._parameters.keys())}")
        
        return self._parameters[name](config_value)
    
    def create_all_parameters(self, config: Dict[str, int]) -> Dict[str, BaseParameter]:
        """
        Create all parameters from config dict.
        
        Args:
            config: Dict mapping parameter names to values
            
        Returns:
            Dict mapping parameter names to instances
        """
        params = {}
        for name, value in config.items():
            if name in self._parameters:
                params[name] = self.create_parameter(name, value)
        return params
    
    def get_by_category(self, category: ParameterCategory) -> List[str]:
        """
        Get all parameter names in a category.
        
        Args:
            category: ParameterCategory enum
            
        Returns:
            List of parameter names
        """
        names = []
        for name, param_class in self._parameters.items():
            instance = param_class(5)  # Dummy instance
            if instance.get_metadata()['category'] == category:
                names.append(name)
        return names
    
    def get_all_names(self) -> List[str]:
        """Get all registered parameter names"""
        return list(self._parameters.keys())
    
    def validate_config(self, config: Dict[str, int]) -> Dict[str, List[str]]:
        """
        Validate config has all required parameters.
        
        Args:
            config: Config dict to validate
            
        Returns:
            Dict with 'missing' and 'extra' keys containing lists of parameter names
        """
        registered = set(self._parameters.keys())
        provided = set(config.keys())
        
        return {
            'missing': list(registered - provided),
            'extra': list(provided - registered)
        }


# Global registry instance
_registry = None

def get_registry() -> ParameterRegistry:
    """Get global parameter registry (singleton)"""
    global _registry
    if _registry is None:
        _registry = ParameterRegistry()
    return _registry
```

---

### 4. Simplified Dynamic Config

**File**: `processing/config/dynamic_config.py` (REFACTORED)

```python
"""
Dynamic Configuration Calculator (Refactored)

Now delegates to parameter modules for all prompt logic.
This file ONLY handles:
1. Loading config values
2. Creating parameter instances via registry
3. Extracting normalized values for voice_params dict
"""

from typing import Dict, Any
from processing.config.config_loader import get_config
from processing.parameters.registry import get_registry


class DynamicConfig:
    """
    Dynamic configuration calculator (refactored).
    
    Delegates all parameter logic to parameter modules.
    Acts as facade for config loading and value extraction.
    """
    
    def __init__(self, base_config=None):
        self.base_config = base_config if base_config is not None else get_config()
        self.registry = get_registry()
        self._parameter_instances = None
    
    def _load_parameter_instances(self) -> Dict[str, Any]:
        """
        Load all parameter instances from config.
        Cached after first call.
        """
        if self._parameter_instances is not None:
            return self._parameter_instances
        
        # Extract all parameter values from config
        config_values = {
            'author_voice_intensity': self.base_config.get_author_voice_intensity(),
            'personality_intensity': self.base_config.get_personality_intensity(),
            'engagement_style': self.base_config.get_engagement_style(),
            'emotional_intensity': self.base_config.get_emotional_intensity(),
            'professional_voice': self.base_config.config.get('professional_voice', 5),
            'jargon_removal': self.base_config.config.get('jargon_removal', 7),
            'technical_language_intensity': self.base_config.get_technical_language_intensity(),
            'context_specificity': self.base_config.get_context_specificity(),
            'sentence_rhythm_variation': self.base_config.get_sentence_rhythm_variation(),
            'imperfection_tolerance': self.base_config.get_imperfection_tolerance(),
            'structural_predictability': self.base_config.get_structural_predictability(),
            'length_variation_range': self.base_config.get_length_variation_range(),
            'ai_avoidance_intensity': self.base_config.config.get('ai_avoidance_intensity', 8),
            'humanness_intensity': self.base_config.config.get('humanness_intensity', 9)
        }
        
        # Create parameter instances
        self._parameter_instances = self.registry.create_all_parameters(config_values)
        
        return self._parameter_instances
    
    def calculate_voice_parameters(self) -> Dict[str, float]:
        """
        Calculate voice_params dict from parameter instances.
        
        Returns normalized values only - no prompt logic here.
        """
        params = self._load_parameter_instances()
        
        # Extract voice param values from instances
        voice_params = {}
        for name, instance in params.items():
            metadata = instance.get_metadata()
            if metadata['maps_to'] == 'voice_params':
                voice_params[name] = instance.get_voice_param_value()
        
        # Add colloquialism_frequency (derived from max of voice and personality)
        author_voice = params['author_voice_intensity'].normalized_value
        personality = params['personality_intensity'].normalized_value
        voice_params['colloquialism_frequency'] = max(author_voice, personality)
        
        return voice_params
    
    def calculate_enrichment_params(self) -> Dict[str, Any]:
        """
        Calculate enrichment_params dict from parameter instances.
        """
        params = self._load_parameter_instances()
        
        # Extract enrichment params
        technical = params['technical_language_intensity']
        context = params['context_specificity']
        engagement = params['engagement_style']
        
        # Determine formatting style
        eng_tier = engagement.tier
        if eng_tier.value == 'low':
            formatting = 'formal'
        elif eng_tier.value == 'moderate':
            formatting = 'balanced'
        else:
            formatting = 'conversational'
        
        return {
            'technical_intensity': technical.config_value,
            'context_detail_level': context.config_value,
            'fact_formatting_style': formatting,
            'engagement_level': engagement.config_value
        }
    
    def get_parameter_instances(self) -> Dict[str, Any]:
        """
        Get all parameter instances for prompt building.
        
        Returns:
            Dict mapping parameter names to instances
        """
        return self._load_parameter_instances()
```

---

### 5. Simplified Prompt Builder

**File**: `processing/generation/prompt_builder.py` (REFACTORED)

```python
"""
Unified Prompt Builder (Refactored)

Orchestrates parameter modules to build prompts.
Dramatically simplified - delegates all parameter logic to modules.

Before: 610 lines with embedded logic
After: ~200 lines of orchestration only
"""

import logging
from typing import Dict, Optional
from processing.parameters.registry import get_registry
from processing.generation.component_specs import ComponentRegistry, DomainContext

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Simplified prompt builder - orchestrates parameter modules.
    
    All parameter-specific logic moved to parameter modules.
    This class ONLY:
    1. Loads parameter instances
    2. Collects prompt guidance from each parameter
    3. Assembles final prompt structure
    """
    
    @staticmethod
    def build_unified_prompt(
        topic: str,
        voice: Dict,
        length: Optional[int] = None,
        facts: str = "",
        context: str = "",
        component_type: str = "subtitle",
        domain: str = "materials",
        voice_params: Optional[Dict[str, float]] = None,
        enrichment_params: Optional[Dict] = None,
        variation_seed: Optional[int] = None,
        parameter_instances: Optional[Dict] = None  # NEW: Pre-created instances
    ) -> str:
        """
        Build unified prompt using parameter modules.
        
        Args:
            topic: Subject matter
            voice: Voice profile dict
            length: Target word count
            facts: Formatted facts
            context: Additional context
            component_type: Component type
            domain: Content domain
            voice_params: Legacy voice params dict (for backwards compatibility)
            enrichment_params: Legacy enrichment params (for backwards compatibility)
            variation_seed: Optional variation seed
            parameter_instances: Pre-created parameter instances (NEW)
            
        Returns:
            Complete prompt string
        """
        # Get component specification
        registry = ComponentRegistry()
        spec = registry.get_component(component_type, domain)
        
        if length is None:
            length = spec.default_length
        
        # Build context dict for parameter modules
        param_context = {
            'length': length,
            'component_type': component_type,
            'domain': domain,
            'voice': voice,
            'facts': facts,
            'context': context,
            'topic': topic
        }
        
        # Collect prompt guidance from all parameters
        prompt_sections = {
            'voice': [],
            'requirements': [],
            'anti_ai': []
        }
        
        if parameter_instances:
            # Use provided instances - collect guidance from each
            for name, instance in parameter_instances.items():
                guidance = instance.generate_prompt_guidance(param_context)
                if guidance:
                    # Determine which section this guidance belongs to
                    metadata = instance.get_metadata()
                    category = metadata['category'].value
                    
                    if category in ['voice', 'variation']:
                        prompt_sections['voice'].append(guidance)
                    elif category == 'technical':
                        prompt_sections['requirements'].append(guidance)
                    elif category == 'ai_detection':
                        prompt_sections['anti_ai'].append(guidance)
        
        # Build TASK section
        task_section = f"""TASK: Write {component_type} about {topic}
- Length: EXACTLY {length} words (critical requirement)"""
        
        if not spec.end_punctuation:
            task_section += "\n- NO period at end"
        
        # Build REQUIREMENTS section
        requirements = ["\nREQUIREMENTS:"]
        requirements.extend(prompt_sections['requirements'])
        requirements_section = "\n".join(requirements) if len(requirements) > 1 else ""
        
        # Build VOICE section
        voice_guidance = [
            f"\nVOICE: {voice.get('author', 'Unknown')} from {voice.get('country', 'Unknown')}",
            f"- Regional patterns: {voice.get('esl_traits', 'Standard')}"
        ]
        voice_guidance.extend(prompt_sections['voice'])
        voice_section = "\n".join(voice_guidance)
        
        # Build ANTI-AI section
        anti_ai_section = ""
        if prompt_sections['anti_ai']:
            anti_ai_section = "\n\nCRITICAL - AI AVOIDANCE:\n" + "\n".join(prompt_sections['anti_ai'])
        
        # Build FACTS section
        facts_section = ""
        if facts.strip():
            facts_section = f"\n\nFACTS:\n{facts}"
        
        # Build CONTEXT section
        context_section = ""
        if context.strip():
            context_section = f"\n\nCONTEXT:\n{context}"
        
        # Assemble final prompt
        prompt = f"""{task_section}
{requirements_section}
{voice_section}
{anti_ai_section}
{facts_section}
{context_section}

Begin writing now. {length} words exactly."""
        
        return prompt.strip()
```

---

### 6. Prompt Quality Evaluator

**File**: `processing/parameters/evaluator.py`

```python
"""
Prompt Quality Evaluator

Validates orchestrated prompts to ensure:
1. All required parameters represented
2. No conflicting guidance
3. Appropriate complexity for content type
4. Clear, actionable instructions for LLM
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum


class PromptQuality(Enum):
    """Prompt quality levels"""
    EXCELLENT = "excellent"  # All checks pass
    GOOD = "good"           # Minor issues
    ACCEPTABLE = "acceptable"  # Some issues but usable
    POOR = "poor"           # Major issues, may fail


class PromptIssue:
    """Represents a quality issue in prompt"""
    
    def __init__(
        self,
        severity: str,  # "error", "warning", "info"
        category: str,  # "missing", "conflict", "clarity", "complexity"
        message: str,
        suggestion: Optional[str] = None
    ):
        self.severity = severity
        self.category = category
        self.message = message
        self.suggestion = suggestion
    
    def __repr__(self) -> str:
        return f"[{self.severity.upper()}] {self.category}: {self.message}"


class PromptEvaluator:
    """
    Evaluates orchestrated prompts for quality.
    
    Checks:
    - Parameter representation (are all expected parameters present?)
    - Guidance conflicts (contradictory instructions)
    - Clarity (ambiguous or vague instructions)
    - Complexity (appropriate for content type)
    - Completeness (all required sections present)
    """
    
    def __init__(self):
        self.required_sections = ['TASK', 'VOICE', 'FACTS']
        self.optional_sections = ['REQUIREMENTS', 'CONTEXT', 'ANTI-AI']
    
    def evaluate(
        self,
        prompt: str,
        expected_parameters: List[str],
        component_type: str,
        length: int
    ) -> Tuple[PromptQuality, List[PromptIssue]]:
        """
        Evaluate prompt quality.
        
        Args:
            prompt: Generated prompt string
            expected_parameters: List of parameter names that should be represented
            component_type: Component type (subtitle, caption, etc.)
            length: Target word count
            
        Returns:
            Tuple of (quality_level, list_of_issues)
        """
        issues = []
        
        # Check 1: Required sections present
        issues.extend(self._check_required_sections(prompt))
        
        # Check 2: Parameter representation
        issues.extend(self._check_parameter_representation(prompt, expected_parameters))
        
        # Check 3: Guidance conflicts
        issues.extend(self._check_conflicts(prompt))
        
        # Check 4: Clarity
        issues.extend(self._check_clarity(prompt))
        
        # Check 5: Complexity appropriate for content type
        issues.extend(self._check_complexity(prompt, component_type, length))
        
        # Check 6: Length specification
        issues.extend(self._check_length_specification(prompt, length))
        
        # Determine quality level based on issues
        quality = self._determine_quality(issues)
        
        return quality, issues
    
    def _check_required_sections(self, prompt: str) -> List[PromptIssue]:
        """Check all required sections present"""
        issues = []
        for section in self.required_sections:
            if section not in prompt:
                issues.append(PromptIssue(
                    severity="error",
                    category="missing",
                    message=f"Required section '{section}' not found in prompt",
                    suggestion=f"Ensure prompt builder includes {section} section"
                ))
        return issues
    
    def _check_parameter_representation(
        self,
        prompt: str,
        expected_parameters: List[str]
    ) -> List[PromptIssue]:
        """Check expected parameters are represented in prompt"""
        issues = []
        
        # Map parameters to search terms
        parameter_indicators = {
            'sentence_rhythm_variation': 'Sentence structure',
            'imperfection_tolerance': 'imperfection',
            'jargon_removal': 'Technical terminology',
            'professional_voice': 'Vocabulary level',
            'structural_predictability': 'AI AVOIDANCE',
            'emotional_intensity': 'EMOTIONAL TONE'
        }
        
        for param in expected_parameters:
            if param in parameter_indicators:
                indicator = parameter_indicators[param]
                if indicator.lower() not in prompt.lower():
                    issues.append(PromptIssue(
                        severity="warning",
                        category="missing",
                        message=f"Parameter '{param}' may not be represented (no '{indicator}' found)",
                        suggestion=f"Check that {param}.generate_prompt_guidance() returns valid text"
                    ))
        
        return issues
    
    def _check_conflicts(self, prompt: str) -> List[PromptIssue]:
        """Check for conflicting guidance"""
        issues = []
        
        # Check for contradictory instructions
        conflicts = [
            (['Perfect grammar', 'imperfection'], 'Grammar guidance conflicts'),
            (['FORMAL', 'CASUAL'], 'Formality guidance conflicts'),
            (['technical terminology', 'AVOID jargon'], 'Jargon guidance conflicts'),
            (['consistent sentence', 'DRAMATIC variation'], 'Sentence structure guidance conflicts')
        ]
        
        for terms, message in conflicts:
            if all(term.lower() in prompt.lower() for term in terms):
                issues.append(PromptIssue(
                    severity="error",
                    category="conflict",
                    message=message,
                    suggestion="Check parameter values - may have conflicting settings"
                ))
        
        return issues
    
    def _check_clarity(self, prompt: str) -> List[PromptIssue]:
        """Check prompt clarity"""
        issues = []
        
        # Check for vague instructions
        vague_terms = ['somewhat', 'maybe', 'might', 'could possibly']
        for term in vague_terms:
            if term in prompt.lower():
                issues.append(PromptIssue(
                    severity="warning",
                    category="clarity",
                    message=f"Vague instruction found: '{term}'",
                    suggestion="Use concrete, specific instructions for LLM"
                ))
        
        return issues
    
    def _check_complexity(
        self,
        prompt: str,
        component_type: str,
        length: int
    ) -> List[PromptIssue]:
        """Check complexity appropriate for content type"""
        issues = []
        
        # Count number of instructions
        instruction_markers = ['-', '•', '*', '1.', '2.', '3.']
        instruction_count = sum(prompt.count(marker) for marker in instruction_markers)
        
        # Expected complexity by component type
        expected_ranges = {
            'subtitle': (3, 8),   # Simple, few instructions
            'caption': (8, 15),   # Moderate complexity
            'faq': (15, 25),      # High complexity
            'description': (20, 35)  # Very high complexity
        }
        
        min_expected, max_expected = expected_ranges.get(component_type, (5, 20))
        
        if instruction_count < min_expected:
            issues.append(PromptIssue(
                severity="warning",
                category="complexity",
                message=f"Prompt may be too simple for {component_type} ({instruction_count} instructions)",
                suggestion=f"Expected {min_expected}-{max_expected} instructions"
            ))
        elif instruction_count > max_expected:
            issues.append(PromptIssue(
                severity="warning",
                category="complexity",
                message=f"Prompt may be too complex for {component_type} ({instruction_count} instructions)",
                suggestion=f"Expected {min_expected}-{max_expected} instructions"
            ))
        
        return issues
    
    def _check_length_specification(self, prompt: str, length: int) -> List[PromptIssue]:
        """Check length is clearly specified"""
        issues = []
        
        if str(length) not in prompt:
            issues.append(PromptIssue(
                severity="error",
                category="missing",
                message=f"Target length ({length} words) not found in prompt",
                suggestion="Ensure TASK section includes exact word count"
            ))
        
        # Check for emphasis on length requirement
        emphasis_terms = ['EXACTLY', 'critical', 'must be']
        if not any(term in prompt for term in emphasis_terms):
            issues.append(PromptIssue(
                severity="info",
                category="clarity",
                message="Length requirement not emphasized",
                suggestion="Consider adding emphasis like 'EXACTLY' or 'critical requirement'"
            ))
        
        return issues
    
    def _determine_quality(self, issues: List[PromptIssue]) -> PromptQuality:
        """Determine overall quality from issues"""
        error_count = sum(1 for i in issues if i.severity == 'error')
        warning_count = sum(1 for i in issues if i.severity == 'warning')
        
        if error_count > 0:
            return PromptQuality.POOR
        elif warning_count > 3:
            return PromptQuality.ACCEPTABLE
        elif warning_count > 0:
            return PromptQuality.GOOD
        else:
            return PromptQuality.EXCELLENT
    
    def print_report(
        self,
        quality: PromptQuality,
        issues: List[PromptIssue],
        verbose: bool = False
    ):
        """
        Print evaluation report.
        
        Args:
            quality: Quality level
            issues: List of issues
            verbose: Show all issues or just errors/warnings
        """
        print("\n" + "=" * 80)
        print("PROMPT QUALITY EVALUATION")
        print("=" * 80)
        
        # Quality indicator
        quality_indicators = {
            PromptQuality.EXCELLENT: "✅ EXCELLENT",
            PromptQuality.GOOD: "✅ GOOD",
            PromptQuality.ACCEPTABLE: "⚠️  ACCEPTABLE",
            PromptQuality.POOR: "❌ POOR"
        }
        print(f"\nOverall Quality: {quality_indicators[quality]}")
        
        # Issue summary
        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']
        info = [i for i in issues if i.severity == 'info']
        
        print(f"\nIssues Found: {len(errors)} errors, {len(warnings)} warnings, {len(info)} info")
        
        # Show issues
        if errors:
            print("\n🔴 ERRORS:")
            for issue in errors:
                print(f"  • {issue.message}")
                if issue.suggestion:
                    print(f"    → {issue.suggestion}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for issue in warnings:
                print(f"  • {issue.message}")
                if issue.suggestion:
                    print(f"    → {issue.suggestion}")
        
        if verbose and info:
            print("\nℹ️  INFO:")
            for issue in info:
                print(f"  • {issue.message}")
                if issue.suggestion:
                    print(f"    → {issue.suggestion}")
        
        print("\n" + "=" * 80)
```

---

## 🎯 Implementation Plan

### Phase 1: Foundation (Week 1)
**Goal**: Create base infrastructure

1. ✅ Create `processing/parameters/` directory structure
2. ✅ Implement `base.py` with BaseParameter abstract class
3. ✅ Implement `registry.py` with parameter discovery
4. ✅ Implement `evaluator.py` with prompt quality validation
5. ✅ Write tests for base infrastructure

### Phase 2: Parameter Migration (Week 2)
**Goal**: Convert 4 fixed parameters to modules

1. ✅ Create `variation/sentence_rhythm_variation.py`
2. ✅ Create `variation/imperfection_tolerance.py`
3. ✅ Create `voice/jargon_removal.py`
4. ✅ Create `voice/professional_voice.py`
5. ✅ Test each module independently
6. ✅ Verify prompt output matches current system

### Phase 3: Remaining Parameters (Week 3)
**Goal**: Migrate all 14 parameters

1. ✅ Migrate voice parameters (6 total)
2. ✅ Migrate technical parameters (2 total)
3. ✅ Migrate variation parameters (remaining 2)
4. ✅ Migrate AI detection parameters (2 total)
5. ✅ Test complete system
6. ✅ Verify all 14 tests passing

### Phase 4: Integration (Week 4)
**Goal**: Refactor prompt builder and dynamic config

1. ✅ Refactor `dynamic_config.py` to use registry
2. ✅ Refactor `prompt_builder.py` to orchestrate modules
3. ✅ Update orchestrator to pass parameter instances
4. ✅ Add evaluator to generation pipeline
5. ✅ Regression testing (ensure output quality maintained)
6. ✅ Update documentation

### Phase 5: Validation & Optimization (Week 5)
**Goal**: Ensure quality and performance

1. ✅ Run full test suite (materials, applications, etc.)
2. ✅ Compare prompts before/after refactor
3. ✅ Validate evaluator catches real issues
4. ✅ Performance profiling
5. ✅ Optimize caching if needed
6. ✅ Final documentation and training

---

## 📊 Benefits of This Architecture

### 1. **Maintainability**
- **Before**: Find parameter logic in 610-line file
- **After**: One 50-line file per parameter

### 2. **Testability**
- **Before**: Test by generating full prompts
- **After**: Test each parameter independently

### 3. **Extensibility**
- **Before**: Add parameter = edit 3 files, find right locations
- **After**: Add parameter = create one new file, auto-discovered

### 4. **Consistency**
- **Before**: Each parameter implemented differently
- **After**: All parameters use same interface

### 5. **Quality Assurance**
- **Before**: No systematic validation of prompts
- **After**: Evaluator validates every prompt

### 6. **Documentation**
- **Before**: Documentation separate from code
- **After**: Each parameter self-documenting via metadata

---

## 🧪 Testing Strategy

### Unit Tests (Per Parameter)
```python
def test_sentence_rhythm_variation_low_tier():
    """Test low tier generates correct guidance"""
    param = SentenceRhythmVariation(2)  # Low value
    assert param.tier == ParameterTier.LOW
    
    guidance = param.generate_prompt_guidance({'length': 50})
    assert 'consistent' in guidance.lower()
    assert 'uniform' in guidance.lower()

def test_sentence_rhythm_variation_high_tier():
    """Test high tier generates correct guidance"""
    param = SentenceRhythmVariation(10)  # High value
    assert param.tier == ParameterTier.HIGH
    
    guidance = param.generate_prompt_guidance({'length': 50})
    assert 'dramatic' in guidance.lower() or 'wild' in guidance.lower()
```

### Integration Tests (Prompt Builder)
```python
def test_prompt_builder_orchestration():
    """Test prompt builder orchestrates parameters correctly"""
    config = {
        'sentence_rhythm_variation': 10,
        'imperfection_tolerance': 10,
        'jargon_removal': 9,
        'professional_voice': 5
    }
    
    registry = get_registry()
    params = registry.create_all_parameters(config)
    
    prompt = PromptBuilder.build_unified_prompt(
        topic='Aluminum',
        voice=test_voice,
        length=50,
        parameter_instances=params
    )
    
    # Verify each parameter represented
    assert 'Sentence structure' in prompt  # rhythm
    assert 'imperfection' in prompt  # imperfection
    assert 'Technical terminology' in prompt  # jargon
    assert 'Vocabulary level' in prompt  # professional
```

### Quality Tests (Evaluator)
```python
def test_evaluator_detects_missing_sections():
    """Test evaluator catches missing sections"""
    incomplete_prompt = "TASK: Write something"  # Missing VOICE, FACTS
    
    evaluator = PromptEvaluator()
    quality, issues = evaluator.evaluate(
        incomplete_prompt,
        expected_parameters=['sentence_rhythm_variation'],
        component_type='caption',
        length=50
    )
    
    assert quality == PromptQuality.POOR
    assert any(i.category == 'missing' for i in issues)
```

---

## 🚀 Migration Path

### Stage 1: Parallel System (No Breaking Changes)
1. Build new parameter system alongside existing
2. Keep current prompt_builder.py working
3. Test new system extensively
4. Compare outputs (new vs old)

### Stage 2: Gradual Cutover
1. Add feature flag: `use_modular_parameters`
2. Route through new system when flag enabled
3. A/B test with real generation
4. Monitor quality metrics

### Stage 3: Full Migration
1. Switch default to new system
2. Deprecate old implementation
3. Remove legacy code after 2-week grace period
4. Update all documentation

### Rollback Plan
- Keep old prompt_builder.py as `prompt_builder_legacy.py`
- Feature flag can instantly revert to legacy
- Maintain parallel for 1 month post-migration

---

## 📈 Success Metrics

### Code Quality
- ✅ Prompt builder reduced from 610 to ~200 lines (67% reduction)
- ✅ Average parameter module: 50-80 lines
- ✅ All parameters testable independently

### Test Coverage
- ✅ 14 unit tests (one per parameter)
- ✅ 6 integration tests (orchestration)
- ✅ 4 quality tests (evaluator)
- ✅ Total: 24 new tests

### Maintainability
- ✅ Time to add new parameter: 1 hour (vs 4 hours previously)
- ✅ Time to find parameter logic: 10 seconds (vs 5 minutes)
- ✅ Lines changed per parameter edit: ~50 (vs ~200)

### Quality
- ✅ 100% of prompts evaluated before generation
- ✅ Automatic detection of parameter conflicts
- ✅ Systematic validation of completeness

---

## 🎓 Documentation Requirements

### For Developers
1. **Parameter Development Guide**: How to create new parameters
2. **Architecture Overview**: System design and flow
3. **Testing Guidelines**: How to test parameters
4. **Migration Guide**: Moving existing parameters

### For AI Assistants
1. **Copilot Instructions**: Updated with new architecture
2. **Parameter Reference**: Metadata for all 14 parameters
3. **Troubleshooting Guide**: Common issues and solutions
4. **Code Examples**: Standard patterns

---

## 💡 Future Enhancements

### Phase 6: Advanced Features
1. **Parameter Presets**: Named configurations ("Conservative", "Creative", "Balanced")
2. **Parameter Relationships**: Automatic adjustment of related parameters
3. **Learning Integration**: Parameters learn optimal values from feedback
4. **Visual Editor**: GUI for configuring parameters with live preview

### Phase 7: Content-Aware Parameters
1. **Material-Specific Tuning**: Different params for metals vs polymers
2. **Component-Specific Defaults**: Captions vs descriptions
3. **Audience Adaptation**: Technical vs general audience params

---

## ❓ FAQ

**Q: Won't this add complexity?**  
A: Initially yes, but long-term maintenance is far simpler. Adding a parameter goes from editing 3 files (finding right spots) to creating 1 file (auto-discovered).

**Q: What about performance?**  
A: Parameter instances are created once and cached. Overhead is negligible (<1ms per generation).

**Q: How do we ensure consistency during migration?**  
A: Feature flag allows parallel running. We compare outputs before cutover. Rollback plan ensures safety.

**Q: What if a parameter needs complex logic?**  
A: BaseParameter is flexible - subclasses can override any method. Complex parameters can have helper methods.

**Q: How does this help with prompt quality?**  
A: Evaluator systematically validates every prompt. Catches conflicts, missing sections, and clarity issues automatically.

---

## 🎯 Recommendation

**Proceed with modularization** using phased approach:

1. **Week 1**: Build foundation (base, registry, evaluator)
2. **Week 2**: Migrate 4 fixed parameters
3. **Week 3**: Migrate remaining 10 parameters
4. **Week 4**: Integrate with prompt builder
5. **Week 5**: Validate and optimize

**Expected ROI**:
- 67% reduction in prompt_builder.py size
- 75% faster parameter development
- 100% prompt quality validation
- Future-proof architecture for growth

**Risk Level**: Low (parallel migration with feature flag and rollback plan)

---

## 📝 Next Steps

1. **Review this proposal** with team
2. **Get approval** for architecture direction
3. **Create Phase 1 branch**: `feature/parameter-modularization`
4. **Start implementation**: Begin with base infrastructure
5. **Iterate**: Adjust based on learnings from first 4 parameters

**Questions? Concerns? Suggestions?** → Document in follow-up discussion.
