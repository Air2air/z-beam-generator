"""
Centralized Validation, Fix, and Recovery System for Z-Beam Generator

This module consolidates ALL validation, fixing, and recovery logic into a single, 
authoritative source that dynamically updates instructions each time fixes are authorized.

Replaces:
- run.py validation/fix functions 
- recovery/ package (validator.py, recovery_system.py, recovery_runner.py, cli.py)
- validate.py legacy file
- validation/ scattered files
"""

import yaml
import logging
from typing import Dict, List, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Import slug utilities for consistent naming
try:
    from utils.slug_utils import create_material_slug, create_filename_slug
except ImportError:
    # Fallback to basic slug generation if utils not available
    def create_material_slug(name: str) -> str:
        return name.lower().replace(' ', '-').replace('_', '-').replace('(', '').replace(')', '')
    def create_filename_slug(name: str, suffix: str = "laser-cleaning") -> str:
        slug = create_material_slug(name)
        return f"{slug}-{suffix}" if suffix else slug

logger = logging.getLogger(__name__)

class ComponentStatus(Enum):
    SUCCESS = "success"
    INVALID = "invalid"
    FAILED = "failed"
    EMPTY = "empty"
    MISSING = "missing"

@dataclass
class ValidationResult:
    component: str
    subject: str
    status: ComponentStatus
    file_path: str
    size_bytes: int
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]

class CentralizedValidator:
    """Single source of truth for all validation, fixing, and recovery logic."""
    
    def __init__(self, validators_dir: str = None):
        """Initialize the centralized validator."""
        self.base_path = Path(validators_dir or Path(__file__).parent)
        self.components = ["frontmatter", "caption", "content", "bullets", "table", "jsonld", "metatags", "tags", "propertiestable"]
        
        # Cache for instructions
        self._fix_instructions_cache = None
        self._fix_instructions_timestamp = 0
        
        # Load example formats for validation
        self.examples_dir = self.base_path / "examples"
    
    def validate_material(self, subject: str) -> Dict[str, ValidationResult]:
        """Validate all components for a material."""
        results = {}
        
        for component in self.components:
            file_path = self._get_component_file_path(subject, component)
            results[component] = self._validate_single_component(str(file_path), component)
        
        return results
    
    def _validate_single_component(self, file_path: str, component: str) -> ValidationResult:
        """Validate a single component file."""
        try:
            # Basic file existence check
            path = Path(file_path)
            if not path.exists():
                return ValidationResult(
                    status=ComponentStatus.MISSING,
                    file_path=file_path,
                    errors=[f"File does not exist: {file_path}"]
                )
            
            # Basic content check
            content = path.read_text(encoding='utf-8')
            if not content.strip():
                return ValidationResult(
                    status=ComponentStatus.EMPTY,
                    file_path=file_path,
                    errors=["File is empty"]
                )
            
            # Success
            return ValidationResult(
                status=ComponentStatus.SUCCESS,
                file_path=file_path,
                size_bytes=len(content.encode('utf-8'))
            )
        
        except Exception as e:
            return ValidationResult(
                status=ComponentStatus.ERROR,
                file_path=file_path,
                errors=[str(e)]
            )

    def post_process_generated_content(self, file_path: str, component_type: str) -> bool:
        """
        Apply post-processing cleanup to generated content.
        This should be called immediately after content generation, before validation.
        
        Args:
            file_path: Path to the generated content file
            component_type: Type of component (frontmatter, content, etc.)
            
        Returns:
            bool: True if post-processing was applied and content was modified
        """
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Cannot post-process non-existent file: {file_path}")
            return False
        
        try:
            original_content = path.read_text(encoding='utf-8')
            
            # Apply component-specific post-processing
            if component_type == "frontmatter":
                # For frontmatter components, apply basic cleanup
                processed_content = original_content
            else:
                # For non-frontmatter components, apply basic cleanup
                processed_content = original_content
                # Could add other post-processing here for different component types
            
            # Write back if changes were made
            if processed_content != original_content:
                path.write_text(processed_content, encoding='utf-8')
                logger.info(f"✅ Applied post-processing cleanup to {component_type} component")
                return True
            else:
                logger.debug(f"No post-processing needed for {component_type} component")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during post-processing of {file_path}: {e}")
            return False
    
    def _validate_single_component(self, file_path: str, component: str) -> ValidationResult:
        """Validate a single component file."""
        path = Path(file_path)
        
        if not path.exists():
            return ValidationResult(
                component=component,
                subject="",
                status=ComponentStatus.MISSING,
                file_path=file_path,
                size_bytes=0,
                errors=["File does not exist"],
                warnings=[],
                metrics={}
            )
        
        file_size = path.stat().st_size
        
        if file_size == 0:
            return ValidationResult(
                component=component,
                subject="",
                status=ComponentStatus.EMPTY,
                file_path=file_path,
                size_bytes=0,
                errors=["File is empty"],
                warnings=[],
                metrics={}
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        except Exception as e:
            return ValidationResult(
                component=component,
                subject="",
                status=ComponentStatus.FAILED,
                file_path=file_path,
                size_bytes=file_size,
                errors=[f"Error reading file: {e}"],
                warnings=[],
                metrics={}
            )
        
        # Enhanced validation using example formats
        errors = []
        warnings = []
        
        # Get format rules for this component
        format_rules = self._example_formats.get(component, {})
        
        # Basic content validation
        if len(content) < format_rules.get('min_length', 10):
            errors.append(f"Content too short (minimum {format_rules.get('min_length', 10)} characters)")
        
        # Structure validation based on example format
        if format_rules.get('has_frontmatter', False):
            if not content.startswith('---'):
                errors.append("Missing YAML frontmatter (should start with '---')")
            else:
                # Validate YAML structure
                yaml_errors = self._validate_yaml_structure(content, component, format_rules)
                errors.extend(yaml_errors)
        
        # Component-specific validation
        component_errors = self._validate_component_specific_format(content, component, format_rules)
        errors.extend(component_errors)
        
        # Determine status
        if errors:
            status = ComponentStatus.INVALID
        else:
            status = ComponentStatus.SUCCESS
        
        return ValidationResult(
            component=component,
            subject=path.stem.replace(f'-{component}', ''),
            status=status,
            file_path=file_path,
            size_bytes=file_size,
            errors=errors,
            warnings=warnings,
            metrics={'content_length': len(content)}
        )
    
    def _validate_yaml_structure(self, content: str, component: str, format_rules: Dict[str, Any]) -> List[str]:
        """Validate YAML frontmatter structure against example format."""
        errors = []
        try:
            # Check for multiple opening delimiters
            if content.startswith('---\n---'):
                errors.append("Multiple opening YAML delimiters detected (---)")
            
            # Check for empty object placeholders
            if ': {}' in content:
                errors.append("Empty object placeholders ({}) found in YAML")
            
            # Check for duplicate field patterns
            import re
            duplicate_pattern = r'(\w+):\s*\n\s*\1:\s*(\{\}|$)'
            if re.search(duplicate_pattern, content):
                errors.append("Duplicate field names detected in YAML structure")
            
            yaml_end = content.find('---', 3)
            if yaml_end == -1:
                errors.append("YAML frontmatter not properly closed with '---'")
                return errors
                
            yaml_content = content[3:yaml_end].strip()
            parsed_yaml = yaml.safe_load(yaml_content)
            
            if not parsed_yaml:
                errors.append("Empty or invalid YAML frontmatter")
                return errors
            
            # Check required fields
            required_fields = format_rules.get('required_fields', [])
            for field in required_fields:
                if field not in parsed_yaml:
                    errors.append(f"Missing required field: {field}")
            
            # Component-specific YAML validation
            if component == 'metatags':
                if 'meta_tags' in parsed_yaml and not isinstance(parsed_yaml['meta_tags'], list):
                    errors.append("meta_tags must be a list")
                if 'opengraph' in parsed_yaml and not isinstance(parsed_yaml['opengraph'], list):
                    errors.append("opengraph must be a list")
                    
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML syntax: {e}")
        except Exception as e:
            errors.append(f"Error parsing YAML: {e}")
            
        return errors
    
    def _validate_component_specific_format(self, content: str, component: str, format_rules: Dict[str, Any]) -> List[str]:
        """Validate component-specific format requirements."""
        errors = []
        
        if component == 'caption':
            # Caption should be two lines with bold formatting
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            if len(lines) != 2:
                errors.append("Caption must have exactly 2 lines")
            else:
                for i, line in enumerate(lines):
                    if not line.startswith('**') or '**' not in line[2:]:
                        errors.append(f"Line {i+1} must start with bold formatting (**text**)")
        
        elif component == 'content':
            # Content should be exactly 2 paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            if len(paragraphs) != 2:
                errors.append("Content must have exactly 2 paragraphs")
        
        elif component == 'bullets':
            # Bullets should have bullet points starting with •
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            if not lines:
                errors.append("Bullets component cannot be empty")
            else:
                for line in lines:
                    if not line.startswith('•'):
                        errors.append("All bullet points must start with • character")
                        break
        
        elif component == 'table':
            # Table should have proper markdown table format
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            if not lines:
                errors.append("Table component cannot be empty")
            else:
                has_header = any('|' in line for line in lines[:2])
                has_separator = any('|-' in line or '-|' in line for line in lines[:3])
                if not has_header:
                    errors.append("Table must have header row with | separators")
                if not has_separator:
                    errors.append("Table must have separator row with | and - characters")
        
        elif component == 'content':
            # Content should be properly structured paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            if len(paragraphs) < 2:
                errors.append("Content should have at least 2 paragraphs")
        
        elif component == 'tags':
            # Tags should be a simple list or comma-separated
            if not content.strip():
                errors.append("Tags component cannot be empty")
            elif len(content.split()) < 3:
                errors.append("Tags should contain at least 3 tags")
        
        # Check for placeholder content
        if 'TBD' in content or 'TODO' in content or '[' in content and ']' in content:
            errors.append("Contains placeholder content (TBD, TODO, or [brackets])")
            
        return errors
    
    def _validate_single_component(self, file_path: str, component: str) -> ValidationResult:
        """Validate a single component file and return detailed results."""
        path = Path(file_path)
        errors = []
        warnings = []
        
        # Check if file exists
        if not path.exists():
            return ValidationResult(
                component=component,
                subject="",
                status=ComponentStatus.MISSING,
                file_path=file_path,
                size_bytes=0,
                errors=[f"File does not exist: {file_path}"],
                warnings=[],
                metrics={}
            )
        
        # Check file size
        file_size = path.stat().st_size
        if file_size == 0:
            return ValidationResult(
                component=component,
                subject="",
                status=ComponentStatus.EMPTY,
                file_path=file_path,
                size_bytes=0,
                errors=["File is empty"],
                warnings=[],
                metrics={}
            )
        
        # Read and validate content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        except Exception as e:
            return ValidationResult(
                component=component,
                subject="",
                status=ComponentStatus.INVALID,
                file_path=file_path,
                size_bytes=file_size,
                errors=[f"Could not read file: {e}"],
                warnings=[],
                metrics={}
            )
        
        # Basic content validation
        if not content:
            status = ComponentStatus.EMPTY
            errors.append("File contains no content")
        else:
            # Component-specific validation
            if component == "caption":
                lines = content.split('\n')
                if len(lines) != 2:
                    errors.append("Caption must be exactly 2 lines")
            
            elif component == "frontmatter":
                if 'name:' not in content or '---' not in content:
                    errors.append("Missing required frontmatter fields")
            
            elif component == "propertiestable":
                if '| Property |' not in content:
                    errors.append("Not a valid properties table")
        
        # Determine status
        if errors:
            status = ComponentStatus.INVALID if file_size > 10 else ComponentStatus.EMPTY
        else:
            status = ComponentStatus.SUCCESS
        
        return ValidationResult(
            component=component,
            subject="",
            status=status,
            file_path=file_path,
            size_bytes=file_size,
            errors=errors,
            warnings=warnings,
            metrics={"content_length": len(content)}
        )
    
    def _get_component_file_path(self, subject: str, component: str) -> Path:
        """Get the file path for a component using the same pattern as the main generation."""
        # Clean up subject name to avoid duplication (this matches the template personalization logic)
        clean_subject = subject.replace('-laser-cleaning-laser-cleaning-laser-cleaning', '')
        clean_subject = clean_subject.replace('-laser-cleaning-laser-cleaning', '')
        clean_subject = clean_subject.replace('-laser-cleaning', '').replace('_laser_cleaning', '')
        
        # Use the same filename pattern as main generation (material type uses -laser-cleaning suffix)
        subject_slug = create_material_slug(clean_subject)
        filename = f"{subject_slug}-laser-cleaning.md"
        return Path("content/components") / component / filename
    
    def fix_material(self, subject: str, failed_components: List[str] = None, regenerate_if_needed: bool = True) -> Dict[str, bool]:
        """Fix multiple components for a material."""
        if failed_components is None:
            # Validate all components and identify failures
            validation_report = self.validate_material(subject)
            failed_components = [comp for comp, result in validation_report.items() 
                               if result.status != ComponentStatus.SUCCESS]
        
        results = {}
        for component in failed_components:
            logger.info(f"🔧 Fixing {component} for {subject}...")
            results[component] = self.fix_component(subject, component, regenerate_if_needed)
        
        return results
    
    def fix_component(self, subject: str, component: str, regenerate_if_needed: bool = True) -> bool:
        """Fix a single component."""
        file_path = self._get_component_file_path(subject, component)
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return self._create_component_content(subject, component, file_path)
        
        # Try predefined fixes first
        if self._apply_predefined_fixes(subject, component, file_path):
            return True
        
        # If that doesn't work, regenerate
        if regenerate_if_needed:
            return self._create_component_content(subject, component, file_path)
        
        return False
    
    def _get_unified_generator(self):
        """Get the unified generator module."""
        try:
            from generators.unified_generator import UnifiedDocumentGenerator
            return UnifiedDocumentGenerator
        except ImportError as e:
            logger.error(f"Could not import unified generator: {e}")
            return None
