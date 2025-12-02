#!/usr/bin/env python3
"""
Material Image Generation Configuration

Configuration dataclass for material before/after laser cleaning images.
Uses researched defaults based on material category - no manual settings required.

Author: AI Assistant
Date: November 25, 2025
"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional


# Category-based researched defaults
CATEGORY_DEFAULTS = {
    # Metals - realistic industrial contamination
    # POLICY (Dec 1, 2025): Always 4 patterns (range 3-5)
    "metals_ferrous": {
        "contamination_uniformity": 4,  # 4 pattern types (rust, oil, industrial residue, dust)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "metals_non_ferrous": {
        "contamination_uniformity": 4,  # 4 pattern types (oxidation, grime, fingerprints, dust)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "metals_reactive": {
        "contamination_uniformity": 4,  # 4 pattern types per policy (Dec 1, 2025)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "metals_corrosion_resistant": {
        "contamination_uniformity": 4,  # 4 pattern types per policy (Dec 1, 2025)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Ceramics & Glass - typically environmental contamination
    # POLICY (Dec 1, 2025): Always 4 patterns (range 3-5)
    "ceramics_traditional": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "ceramics_construction": {
        "contamination_uniformity": 4,  # 4 pattern types (weathering, biological, mineral, dust)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "ceramics_glass": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Polymers - chemical and environmental
    # POLICY (Dec 1, 2025): Always 4 patterns (range 3-5)
    "polymers_thermoplastic": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "polymers_engineering": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "polymers_elastomer": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Composites - industrial contamination
    # POLICY (Dec 1, 2025): Always 4 patterns (range 3-5)
    "composites_polymer_matrix": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Wood - organic and environmental
    # POLICY (Dec 1, 2025): Always 4 patterns (range 3-5)
    "wood_hardwood": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "wood_softwood": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "wood_engineered": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Default for unknown categories
    # POLICY (Dec 1, 2025): Always 4 patterns (range 3-5)
    "default": {
        "contamination_uniformity": 4,  # 4 pattern types per policy
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    }
}


@dataclass
class MaterialImageConfig:
    """Configuration for material before/after image generation with researched defaults."""
    
    material: str
    category: Optional[str] = None  # Auto-determined from material
    validate: bool = True  # Validation is MANDATORY - always enabled
    
    # Researched defaults (set automatically based on category)
    # POLICY (Dec 1, 2025): Always 4 patterns (range 3-5)
    contamination_uniformity: int = 4
    view_mode: str = "Contextual"
    guidance_scale: float = 13.0
    
    # Contamination severity: light (<30%), moderate (30-60%), heavy (>60%)
    severity: str = "moderate"  # Options: light, moderate, heavy
    
    # Environmental context: affects pattern selection and severity defaults
    context: str = "outdoor"  # Options: outdoor, indoor, industrial, marine
    
    # Visual weight adjustments (1.0 = default, >1.0 = more visible, <1.0 = less visible)
    aging_weight: Optional[float] = None  # Aging intensity on left (before) side
    contamination_weight: Optional[float] = None  # Contamination intensity on right (after) side
    
    def __post_init__(self):
        """Apply researched defaults based on material category."""
        # If category provided, use it to set researched defaults
        if self.category:
            # Try learned defaults first (from SQLite - single source of truth)
            learned = self._get_learned_defaults(self.category, self.context)
            if learned:
                self.contamination_uniformity = learned.get('contamination_uniformity') or 4  # POLICY: default 4
                self.view_mode = learned.get('view_mode') or "Contextual"
                self.guidance_scale = learned.get('guidance_scale') or 15.0
            else:
                # Auto-seed database from CATEGORY_DEFAULTS on first use
                self._seed_defaults_if_needed()
                # Then try again
                learned = self._get_learned_defaults(self.category, self.context)
                if learned:
                    self.contamination_uniformity = learned.get('contamination_uniformity') or 4  # POLICY: default 4
                    self.view_mode = learned.get('view_mode') or "Contextual"
                    self.guidance_scale = learned.get('guidance_scale') or 15.0
                else:
                    # Ultimate fallback (should rarely happen)
                    defaults = CATEGORY_DEFAULTS.get(self.category, CATEGORY_DEFAULTS["default"])
                    self.contamination_uniformity = defaults["contamination_uniformity"]
                    self.view_mode = defaults["view_mode"]
                    self.guidance_scale = defaults["guidance_scale"]
    
    def _seed_defaults_if_needed(self):
        """Auto-seed database from CATEGORY_DEFAULTS if empty."""
        try:
            from shared.image.learning import create_logger
            logger = create_logger()
            logger.seed_defaults_from_config(CATEGORY_DEFAULTS)
        except Exception:
            pass  # Database unavailable, will use fallback
    
    def _get_learned_defaults(self, category: str, context: str) -> Optional[Dict]:
        """Try to get learned defaults from database."""
        try:
            from shared.image.learning import create_logger
            logger = create_logger()
            return logger.get_learned_defaults(category, context)
        except Exception:
            return None
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_material(
        cls,
        material: str,
        category: str,
        validate: bool = True,
        severity: str = None,
        context: str = "outdoor",
        aging_weight: float = None,
        contamination_weight: float = None
    ) -> "MaterialImageConfig":
        """
        Create configuration with researched defaults for a material.
        
        Args:
            material: Material name (e.g., "Steel", "Aluminum")
            category: Material category (e.g., "metals_ferrous")
            validate: Validation is MANDATORY (default: True, cannot be disabled)
            severity: Contamination severity (light, moderate, heavy) - auto-set by context if None
            context: Environmental context (outdoor, indoor, industrial, marine)
            aging_weight: Visual weight for aging on left (before) side. 0.0-2.0, default 1.0
            contamination_weight: Visual weight for contamination on right (after) side. 0.0-2.0, default 1.0
            
        Returns:
            MaterialImageConfig with researched defaults applied
        """
        config = cls(material=material, category=category, validate=validate)
        config.context = context
        
        # Store weight overrides for prompt building
        config.aging_weight = aging_weight
        config.contamination_weight = contamination_weight
        
        # Auto-set severity based on context if not explicitly provided
        if severity is None:
            severity = config._get_default_severity_for_context(context, category)
        config.severity = severity
        
        return config
    
    def _get_default_severity_for_context(self, context: str, category: str) -> str:
        """
        Get default severity based on context (loaded from Contaminants.yaml).
        
        Indoor = lighter contamination, minimal aging
        Outdoor = heavier aging, moderate contamination
        Industrial = heavy contamination
        Marine = heavy aging + contamination
        """
        # Load from YAML for learning system integration
        try:
            from domains.materials.image.research.contamination_pattern_selector import ContaminationPatternSelector
            selector = ContaminationPatternSelector()
            data = selector._load_data()
            context_settings = data.get('context_settings', {})
            ctx_config = context_settings.get(context, {})
            return ctx_config.get('default_severity', 'moderate')
        except Exception:
            # Fallback if YAML loading fails
            return 'moderate'
    
    @property
    def uniformity_label(self) -> str:
        """Get human-readable uniformity label."""
        labels = {
            1: "Single contaminant type",
            2: "Two contaminant types",
            3: "Three contaminant types",
            4: "Four contaminant types",
            5: "Diverse contamination (4+ types)"
        }
        return labels[self.contamination_uniformity]
    
    @property
    def severity_description(self) -> str:
        """Get severity coverage description."""
        descriptions = {
            "light": "Light contamination (<30% coverage, scattered spots)",
            "moderate": "Moderate contamination (30-60% coverage, connected patches)",
            "heavy": "Extreme contamination (90%+ coverage, surface completely buried under thick crusty buildup, original material barely visible)"
        }
        return descriptions.get(self.severity, descriptions["moderate"])
    
    @property
    def context_description(self) -> str:
        """Get context environment description."""
        descriptions = {
            "indoor": "Indoor environment (minimal UV/weathering, touch-zone contamination)",
            "outdoor": "Outdoor environment (UV aging, weather exposure, biological growth)",
            "industrial": "Industrial environment (heavy contamination, oils, scale, residues)",
            "marine": "Marine environment (salt corrosion, heavy weathering, biological)",
            "laboratory": "Laboratory environment (chemical residues, biological films, sterile process contamination)"
        }
        return descriptions.get(self.context, descriptions["outdoor"])
