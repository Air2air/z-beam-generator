#!/usr/bin/env python3
"""
Component Base Utilities

Shared utilities and base classes for component generators.
Consolidates common patterns and reduces code duplication.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Setup project path
def setup_project_path():
    """Setup the project root path for imports."""
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root

# Setup path on import
PROJECT_ROOT = setup_project_path()

# Import base classes with fallbacks
try:
    from generators.component_generators import (
        APIComponentGenerator,
        FrontmatterComponentGenerator,
        ComponentResult
    )
except ImportError:
    # Fallback classes for standalone operation
    class ComponentResult:
        """Fallback ComponentResult class"""
        def __init__(self, component_type: str, content: str, success: bool, error_message: Optional[str] = None):
            self.component_type = component_type
            self.content = content
            self.success = success
            self.error_message = error_message

    class APIComponentGenerator(ABC):
        """Fallback APIComponentGenerator base class"""
        def __init__(self, component_type: str):
            self.component_type = component_type
            self.logger = logging.getLogger(f"{__name__}.{component_type}")

        @abstractmethod
        def generate(self, *args, **kwargs):
            """Generate component content"""
            pass

    class FrontmatterComponentGenerator(APIComponentGenerator):
        """Fallback FrontmatterComponentGenerator base class"""
        pass


class ComponentGeneratorBase(ABC):
    """Base class for all component generators with common functionality"""

    def __init__(self, component_type: str):
        self.component_type = component_type
        self.logger = logging.getLogger(f"{__name__}.{component_type}")
        self.component_path = Path(__file__).parent.parent / component_type

    def load_component_config(self) -> Dict[str, Any]:
        """Load component configuration from prompt.yaml"""
        from utils.config_utils import load_component_config
        return load_component_config(self.component_type)

    def load_example_file(self, filename: str = "example.md") -> Optional[str]:
        """Load example file content"""
        example_path = self.component_path / f"example_{self.component_type}.md"
        if not example_path.exists():
            example_path = self.component_path / filename

        if example_path.exists():
            try:
                return example_path.read_text(encoding='utf-8')
            except Exception as e:
                self.logger.warning(f"Failed to load example file {example_path}: {e}")
                return None
        return None

    def validate_frontmatter_dependency(self, frontmatter_data: Optional[Dict]) -> bool:
        """Validate that required frontmatter data is available"""
        if not frontmatter_data:
            self.logger.error(f"No frontmatter data available for {self.component_type} generation")
            return False
        return True

    def create_error_result(self, error_message: str) -> ComponentResult:
        """Create a ComponentResult for error cases"""
        return ComponentResult(
            component_type=self.component_type,
            content="",
            success=False,
            error_message=error_message
        )

    def create_success_result(self, content: str) -> ComponentResult:
        """Create a ComponentResult for success cases"""
        return ComponentResult(
            component_type=self.component_type,
            content=content,
            success=True
        )


def get_component_template_path(component_type: str, template_name: str = "prompt.yaml") -> Path:
    """Get the path to a component template file"""
    return Path(__file__).parent.parent / component_type / template_name


def load_component_template(component_type: str, template_name: str = "prompt.yaml") -> Optional[Dict[str, Any]]:
    """Load a component template file"""
    template_path = get_component_template_path(component_type, template_name)
    if template_path.exists():
        try:
            import yaml
            with open(template_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.warning(f"Failed to load template {template_path}: {e}")
    return None


def create_standard_logger(component_type: str) -> logging.Logger:
    """Create a standard logger for a component"""
    return logging.getLogger(f"components.{component_type}")


def handle_generation_error(component_type: str, error: Exception, context: str = "") -> ComponentResult:
    """Standard error handling for component generation"""
    logger = create_standard_logger(component_type)
    error_msg = f"Error generating {component_type} content"
    if context:
        error_msg += f" ({context})"
    error_msg += f": {error}"

    logger.error(error_msg)
    return ComponentResult(
        component_type=component_type,
        content="",
        success=False,
        error_message=str(error)
    )


# Common validation functions
def validate_required_fields(data: Dict, required_fields: list, component_type: str) -> Optional[str]:
    """Validate that required fields are present in data"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)

    if missing_fields:
        return f"Missing required fields for {component_type}: {', '.join(missing_fields)}"
    return None


def sanitize_material_name(material_name: str) -> str:
    """Sanitize material name for file operations"""
    return material_name.lower().replace(' ', '-').replace('/', '-')


def get_component_output_path(component_type: str, material_name: str) -> Path:
    """Get the standard output path for a component"""
    safe_name = sanitize_material_name(material_name)
    return Path("content/components") / component_type / f"{safe_name}-laser-cleaning.md"
