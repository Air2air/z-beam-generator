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
    "metals_ferrous": {
        "contamination_uniformity": 3,  # 3 pattern types (rust, oil, industrial residue)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "metals_non_ferrous": {
        "contamination_uniformity": 3,  # 3 pattern types (oxidation, grime, fingerprints)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "metals_reactive": {
        "contamination_uniformity": 2,  # 2 pattern types (oxidation, residue)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "metals_corrosion_resistant": {
        "contamination_uniformity": 2,  # 2 pattern types (light oxidation, residue)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Ceramics & Glass - typically environmental contamination
    "ceramics_traditional": {
        "contamination_uniformity": 3,  # 3 pattern types (dust, stains, mineral deposits)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "ceramics_construction": {
        "contamination_uniformity": 4,  # 4 pattern types (weathering, biological, mineral, dust)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "ceramics_glass": {
        "contamination_uniformity": 2,  # 2 pattern types (fingerprints, residue)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Polymers - chemical and environmental
    "polymers_thermoplastic": {
        "contamination_uniformity": 2,  # 2 pattern types (residue, discoloration)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "polymers_engineering": {
        "contamination_uniformity": 2,  # 2 pattern types (oil, dust)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "polymers_elastomer": {
        "contamination_uniformity": 3,  # 3 pattern types (dust, oils, residue)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Composites - industrial contamination
    "composites_polymer_matrix": {
        "contamination_uniformity": 3,  # 3 pattern types (resin, dust, oils)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Wood - organic and environmental
    "wood_hardwood": {
        "contamination_uniformity": 3,  # 3 pattern types (dust, oils, mold)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "wood_softwood": {
        "contamination_uniformity": 3,  # 3 pattern types (dust, sap, mold)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    "wood_engineered": {
        "contamination_uniformity": 2,  # 2 pattern types (dust, adhesive residue)
        "view_mode": "Contextual",
        "guidance_scale": 15.0
    },
    
    # Default for unknown categories
    "default": {
        "contamination_uniformity": 3,  # 3 pattern types (moderate variety)
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
    contamination_uniformity: int = 3
    view_mode: str = "Contextual"
    guidance_scale: float = 13.0
    
    def __post_init__(self):
        """Apply researched defaults based on material category."""
        # If category provided, use it to set researched defaults
        if self.category:
            defaults = CATEGORY_DEFAULTS.get(self.category, CATEGORY_DEFAULTS["default"])
            self.contamination_uniformity = defaults["contamination_uniformity"]
            self.view_mode = defaults["view_mode"]
            self.guidance_scale = defaults["guidance_scale"]
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_material(cls, material: str, category: str, validate: bool = True) -> "MaterialImageConfig":
        """
        Create configuration with researched defaults for a material.
        
        Args:
            material: Material name (e.g., "Steel", "Aluminum")
            category: Material category (e.g., "metals_ferrous")
            validate: Validation is MANDATORY (default: True, cannot be disabled)
            
        Returns:
            MaterialImageConfig with researched defaults applied
        """
        return cls(material=material, category=category, validate=validate)
    
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
