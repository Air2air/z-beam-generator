"""
Parameter Manager for Dynamic Generation Parameters

🔄 REUSABILITY: Calculate parameters for ANY domain/component
🎯 SEPARATION: ONLY calculates parameters, no generation logic
🚀 ADAPTABILITY: Register custom parameter calculators

This module provides dynamic parameter calculation for content generation:
- Calculates temperature, penalties based on component type
- Loads voice parameters from author personas
- Applies humanness adjustments for AI detection avoidance
- Supports custom parameter calculators through registration
- Works across all domains without modification
"""

from typing import Dict, Any, Callable, Optional
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ParameterManager:
    """
    🔄 REUSABLE: Calculate parameters for ANY domain/component
    🎯 SEPARATION: ONLY calculates parameters, no generation logic
    🚀 ADAPTABLE: Register custom parameter calculators
    
    Manages generation parameters with dynamic calculation.
    Calculates temperature, penalties, voice settings.
    
    Usage:
        >>> manager = ParameterManager(dynamic_config, humanness_optimizer)
        >>> 
        >>> params = manager.get_parameters(
        ...     component_type='material_description',
        ...     author_id='todd',
        ...     domain='materials',
        ...     context={'custom_field': 'value'}
        ... )
        >>> # params = {
        >>> #     'temperature': 0.7,
        >>> #     'frequency_penalty': 0.3,
        >>> #     'presence_penalty': 0.1,
        >>> #     'voice': {...},
        >>> #     'humanness': {...}
        >>> # }
    """
    
    def __init__(self, dynamic_config, humanness_optimizer):
        """
        Initialize parameter manager.
        
        Args:
            dynamic_config: DynamicConfig instance for parameter calculation
            humanness_optimizer: HumannessOptimizer for AI detection avoidance
        """
        self.dynamic_config = dynamic_config
        self.humanness_optimizer = humanness_optimizer
        
        # 🚀 ADAPTABILITY: Register custom parameter calculators
        self.custom_calculators: Dict[str, Callable] = {}
        
        # Cache for loaded personas
        self._persona_cache: Dict[str, Dict] = {}
    
    def register_calculator(self, param_name: str, calculator: Callable) -> None:
        """
        🚀 ADAPTABILITY: Add custom parameter types without changing core.
        
        Register a custom parameter calculator.
        
        Args:
            param_name: Name of parameter to calculate
            calculator: Function that takes context dict and returns parameter value
        
        Example:
            >>> def calc_technical_level(context):
            ...     audience = context.get('audience', 'general')
            ...     return {'beginner': 1, 'general': 2, 'expert': 3}[audience]
            >>> 
            >>> manager.register_calculator('technical_level', calc_technical_level)
            >>> 
            >>> params = manager.get_parameters('description', 'todd', context={'audience': 'expert'})
            >>> # params['technical_level'] = 3
        """
        self.custom_calculators[param_name] = calculator
        logger.info(f"Registered custom parameter calculator: {param_name}")
    
    def unregister_calculator(self, param_name: str) -> bool:
        """
        Remove a registered custom calculator.
        
        Args:
            param_name: Name of calculator to remove
        
        Returns:
            True if calculator was found and removed, False otherwise
        """
        if param_name in self.custom_calculators:
            del self.custom_calculators[param_name]
            logger.info(f"Unregistered custom parameter calculator: {param_name}")
            return True
        return False
    
    def get_parameters(
        self, 
        component_type: str, 
        author_id: str,
        domain: str = 'materials',
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        🔄 REUSABLE: Works for ANY domain + component combination.
        
        Calculate all generation parameters dynamically.
        
        Args:
            component_type: Type of content (material_description, micro, faq, etc.)
            author_id: Author persona ID (todd, yi-chun, alessandro, ikmanda)
            domain: Domain name (materials, settings, contaminants, compounds)
            context: Additional context dict with ANY custom fields
        
        Returns:
            Dict with all generation parameters:
            {
                'temperature': float,
                'frequency_penalty': float,
                'presence_penalty': float,
                'voice': Dict (persona data),
                'humanness': Dict (humanness instructions),
                'custom_param': Any (if registered)
            }
        """
        context = context or {}
        params = {}
        
        logger.debug(
            f"Calculating parameters for {domain}/{component_type} "
            f"with author {author_id}"
        )
        
        # 1. Base API parameters from dynamic config (domain-aware)
        try:
            params['temperature'] = self.dynamic_config.calculate_temperature(
                component_type, 
                domain=domain
            )
        except Exception as e:
            logger.warning(f"Failed to calculate temperature, using default: {e}")
            params['temperature'] = 0.7
        
        try:
            penalties = self.dynamic_config.calculate_penalties(
                component_type,
                domain=domain
            )
            params['frequency_penalty'] = penalties.get('frequency_penalty', 0.0)
            params['presence_penalty'] = penalties.get('presence_penalty', 0.0)
        except Exception as e:
            logger.warning(f"Failed to calculate penalties, using defaults: {e}")
            params['frequency_penalty'] = 0.0
            params['presence_penalty'] = 0.0
        
        # 2. Voice parameters (author-specific, domain-agnostic)
        try:
            params['voice'] = self._load_voice_parameters(author_id)
        except Exception as e:
            logger.error(f"Failed to load voice parameters for {author_id}: {e}")
            params['voice'] = {}
        
        # 3. Humanness adjustments (structural variation)
        try:
            params['humanness'] = self.humanness_optimizer.get_humanness_instructions()
        except Exception as e:
            logger.warning(f"Failed to get humanness instructions: {e}")
            params['humanness'] = {}
        
        # 4. 🚀 Run custom parameter calculators
        for param_name, calculator in self.custom_calculators.items():
            try:
                full_context = {
                    **context,
                    'component_type': component_type,
                    'author_id': author_id,
                    'domain': domain
                }
                params[param_name] = calculator(full_context)
                logger.debug(f"Custom parameter {param_name} calculated")
            except Exception as e:
                logger.error(f"Custom calculator {param_name} failed: {e}")
                params[param_name] = None
        
        # Safe logging - handle both real values and mocks in tests
        temp = params['temperature']
        freq = params.get('frequency_penalty', 0)
        if isinstance(temp, (int, float)) and isinstance(freq, (int, float)):
            logger.info(
                f"Parameters calculated: temp={temp:.3f}, "
                f"freq_pen={freq:.3f}"
            )
        else:
            logger.info(f"Parameters calculated: temp={temp}, freq_pen={freq}")
        
        return params
    
    def _load_voice_parameters(self, author_id: str) -> Dict[str, Any]:
        """
        Load author persona from YAML file.
        
        Voice parameters are domain-agnostic (same across all domains).
        
        Args:
            author_id: Author persona ID
        
        Returns:
            Dict with voice parameters from persona file
        """
        # Check cache first
        if author_id in self._persona_cache:
            logger.debug(f"Using cached persona for {author_id}")
            return self._persona_cache[author_id]
        
        # Load from file
        persona_path = Path(f"shared/voice/profiles/{author_id}.yaml")
        
        if not persona_path.exists():
            logger.error(f"Persona file not found: {persona_path}")
            return {}
        
        try:
            with open(persona_path, 'r', encoding='utf-8') as f:
                persona_data = yaml.safe_load(f)
            
            # Cache for future use
            self._persona_cache[author_id] = persona_data
            
            logger.debug(f"Loaded persona for {author_id}")
            return persona_data
            
        except Exception as e:
            logger.error(f"Failed to load persona {author_id}: {e}")
            return {}
    
    def get_available_authors(self) -> list[str]:
        """
        Get list of available author persona IDs.
        
        Returns:
            List of author IDs (file names without .yaml extension)
        """
        persona_dir = Path("shared/voice/profiles")
        
        if not persona_dir.exists():
            return []
        
        authors = []
        for file_path in persona_dir.glob("*.yaml"):
            authors.append(file_path.stem)
        
        return sorted(authors)
    
    def validate_author(self, author_id: str) -> bool:
        """
        Check if author persona exists.
        
        Args:
            author_id: Author persona ID to validate
        
        Returns:
            True if persona file exists, False otherwise
        """
        persona_path = Path(f"shared/voice/profiles/{author_id}.yaml")
        return persona_path.exists()
    
    def clear_cache(self) -> None:
        """Clear cached persona data."""
        self._persona_cache.clear()
        logger.debug("Cleared persona cache")
    
    def get_custom_calculators(self) -> list[str]:
        """
        Get list of registered custom calculator names.
        
        Returns:
            List of custom parameter names
        """
        return list(self.custom_calculators.keys())
    
    def calculate_for_batch(
        self,
        component_type: str,
        author_id: str,
        domain: str,
        items: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Calculate parameters for multiple items efficiently.
        
        Useful for batch generation where base parameters are the same
        but context varies per item.
        
        Args:
            component_type: Type of content
            author_id: Author persona ID
            domain: Domain name
            items: List of context dicts (one per item)
        
        Returns:
            List of parameter dicts (one per item)
        """
        results = []
        
        # Pre-calculate shared parameters (same for all items)
        base_params = {
            'temperature': self.dynamic_config.calculate_temperature(component_type, domain=domain),
            'voice': self._load_voice_parameters(author_id),
            'humanness': self.humanness_optimizer.get_humanness_instructions()
        }
        
        penalties = self.dynamic_config.calculate_penalties(component_type, domain=domain)
        base_params['frequency_penalty'] = penalties.get('frequency_penalty', 0.0)
        base_params['presence_penalty'] = penalties.get('presence_penalty', 0.0)
        
        # Calculate item-specific custom parameters
        for item_context in items:
            item_params = base_params.copy()
            
            # Run custom calculators for this item
            for param_name, calculator in self.custom_calculators.items():
                try:
                    full_context = {
                        **item_context,
                        'component_type': component_type,
                        'author_id': author_id,
                        'domain': domain
                    }
                    item_params[param_name] = calculator(full_context)
                except Exception as e:
                    logger.error(f"Custom calculator {param_name} failed for item: {e}")
                    item_params[param_name] = None
            
            results.append(item_params)
        
        logger.info(f"Calculated parameters for {len(items)} items")
        return results
