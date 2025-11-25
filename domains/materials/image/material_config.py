#!/usr/bin/env python3
"""
Material Image Generation Configuration

Configuration dataclass for material before/after laser cleaning images.

Author: AI Assistant
Date: November 24, 2025
"""

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class MaterialImageConfig:
    """Configuration for material before/after image generation."""
    
    material: str
    contamination_level: int = 3  # 1-5: Intensity of contamination
    contamination_uniformity: int = 3  # 1-5: Variety of contaminants (1=single, 5=4+ types)
    view_mode: str = "Contextual"  # "Contextual" or "Isolated"
    environment_wear: int = 3  # 1-5: Background aging (clean but shows wear)
    validate: bool = False  # Whether to validate with Gemini Vision
    
    def __post_init__(self):
        """Validate configuration values."""
        # Validate contamination level
        if not 1 <= self.contamination_level <= 5:
            raise ValueError(f"contamination_level must be 1-5, got {self.contamination_level}")
        
        # Validate uniformity
        if not 1 <= self.contamination_uniformity <= 5:
            raise ValueError(f"contamination_uniformity must be 1-5, got {self.contamination_uniformity}")
        
        # Validate view mode
        valid_modes = ["Contextual", "Isolated"]
        if self.view_mode not in valid_modes:
            raise ValueError(f"view_mode must be one of {valid_modes}, got {self.view_mode}")
        
        # Validate environment wear
        if not 1 <= self.environment_wear <= 5:
            raise ValueError(f"environment_wear must be 1-5, got {self.environment_wear}")
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    @property
    def contamination_intensity_label(self) -> str:
        """Get human-readable contamination intensity label."""
        labels = {
            1: "Minimal",
            2: "Light",
            3: "Moderate",
            4: "Heavy",
            5: "Severe"
        }
        return labels[self.contamination_level]
    
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
