#!/usr/bin/env python3
"""
Generation Pipeline Manager - 3-Mode System

Consolidates all generation capabilities into three distinct modes:
1. TEXT: Generate text content → Materials.yaml
2. RESEARCH: Research missing properties → Materials.yaml  
3. FRONTMATTER: Generate components → content/components/

Follows GROK fail-fast architecture and data storage policy.
"""

import logging
from enum import Enum
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class GenerationMode(Enum):
    """Enumeration of generation modes."""
    TEXT = "text"
    RESEARCH = "research"
    FRONTMATTER = "frontmatter"

class PipelineManager:
    """
    Main orchestrator for the 3-mode generation pipeline.
    
    This class routes requests to appropriate mode handlers and ensures
    data flow compliance with the storage policy.
    """
    
    def __init__(self):
        self.materials_path = Path("data/Materials.yaml")
        self.categories_path = Path("data/Categories.yaml")
        self.content_path = Path("content/components")
        
        # Mode handlers (initialized on demand)
        self._text_generator = None
        self._data_researcher = None
        self._frontmatter_output = None
    
    def execute(
        self,
        mode: GenerationMode,
        material: str,
        component: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute generation pipeline for specified mode.
        
        Args:
            mode: Generation mode (TEXT, RESEARCH, or FRONTMATTER)
            material: Material name to process
            component: Component type (for FRONTMATTER mode)
            **kwargs: Additional mode-specific parameters
            
        Returns:
            Dict containing execution results and metadata
            
        Raises:
            ValueError: If mode requirements not met
            FileNotFoundError: If required data files missing
        """
        logger.info(f"🚀 Starting {mode.value} generation for {material}")
        
        # Validate prerequisites
        self._validate_prerequisites(mode, material, component)
        
        # Route to appropriate mode handler
        if mode == GenerationMode.TEXT:
            return self._execute_text_generation(material, **kwargs)
        elif mode == GenerationMode.RESEARCH:
            return self._execute_data_research(material, **kwargs)
        elif mode == GenerationMode.FRONTMATTER:
            return self._execute_frontmatter_output(material, component, **kwargs)
        else:
            raise ValueError(f"Unknown generation mode: {mode}")
    
    def _validate_prerequisites(
        self,
        mode: GenerationMode,
        material: str,
        component: Optional[str]
    ) -> None:
        """Validate prerequisites for the specified mode."""
        
        # Common validations
        if not material or not material.strip():
            raise ValueError("Material name is required")
        
        if not self.materials_path.exists():
            raise FileNotFoundError(f"Materials.yaml not found: {self.materials_path}")
        
        # Mode-specific validations
        if mode == GenerationMode.FRONTMATTER:
            if not component:
                raise ValueError("Component type required for FRONTMATTER mode")
            
            if not self.categories_path.exists():
                raise FileNotFoundError(f"Categories.yaml not found: {self.categories_path}")
    
    def _execute_text_generation(self, material: str, **kwargs) -> Dict[str, Any]:
        """Execute Mode 1: Text Generation."""
        from pipeline.modes.text_generator import TextGenerator
        
        if not self._text_generator:
            self._text_generator = TextGenerator()
        
        logger.info(f"📝 Generating text content for {material}")
        return self._text_generator.generate(material, **kwargs)
    
    def _execute_data_research(self, material: str, **kwargs) -> Dict[str, Any]:
        """Execute Mode 2: Data Research."""
        from pipeline.modes.data_researcher import DataResearcher
        
        if not self._data_researcher:
            self._data_researcher = DataResearcher()
        
        logger.info(f"🔬 Researching data for {material}")
        return self._data_researcher.research(material, **kwargs)
    
    def _execute_frontmatter_output(
        self,
        material: str,
        component: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute Mode 3: Frontmatter Output."""
        from pipeline.modes.frontmatter_output import FrontmatterOutput
        
        if not self._frontmatter_output:
            self._frontmatter_output = FrontmatterOutput()
        
        logger.info(f"📋 Generating {component} frontmatter for {material}")
        return self._frontmatter_output.generate(material, component, **kwargs)

# Convenience functions for backward compatibility
def generate_text(material: str, **kwargs) -> Dict[str, Any]:
    """Generate text content for a material."""
    pipeline = PipelineManager()
    return pipeline.execute(GenerationMode.TEXT, material, **kwargs)

def research_data(material: str, **kwargs) -> Dict[str, Any]:
    """Research missing data for a material."""
    pipeline = PipelineManager()
    return pipeline.execute(GenerationMode.RESEARCH, material, **kwargs)

def generate_frontmatter(material: str, component: str, **kwargs) -> Dict[str, Any]:
    """Generate frontmatter for a material and component."""
    pipeline = PipelineManager()
    return pipeline.execute(GenerationMode.FRONTMATTER, material, component, **kwargs)