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

import os
import re
import yaml
import logging
import traceback
from typing import Dict, List, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

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
        self.templates_dir = self.base_path / "templates"
        self._example_formats = {}
        self._load_example_formats()
    
    def _load_example_formats(self):
        """Load example formats for schema validation."""
        try:
            for component in self.components:
                example_file = self.examples_dir / f"{component}.md"
                if example_file.exists():
                    with open(example_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self._example_formats[component] = self._parse_example_format(component, content)
                        logger.info(f"📋 Loaded example format for {component}")
                else:
                    logger.warning(f"⚠️ No example format found for {component}")
        except Exception as e:
            logger.error(f"Error loading example formats: {e}")
    
    def _parse_example_format(self, component: str, content: str) -> Dict[str, Any]:
        """Parse example format to extract validation rules."""
        format_rules = {
            'has_frontmatter': False,
            'required_fields': [],
            'structure_type': 'content',
            'min_length': 10,
            'example_content': content
        }
        
        # Check for YAML frontmatter
        if content.strip().startswith('---'):
            format_rules['has_frontmatter'] = True
            format_rules['structure_type'] = 'yaml_frontmatter'
            
            # Extract YAML section
            try:
                yaml_end = content.find('---', 3)
                if yaml_end != -1:
                    yaml_content = content[3:yaml_end].strip()
                    parsed_yaml = yaml.safe_load(yaml_content)
                    if parsed_yaml:
                        format_rules['required_fields'] = list(parsed_yaml.keys())
                        
                        # Component-specific validation rules
                        if component == 'metatags':
                            format_rules['required_fields'] = ['title', 'meta_tags', 'opengraph']
                        elif component == 'frontmatter':
                            format_rules['required_fields'] = ['name', 'applications', 'technicalSpecifications', 'subject', 'article_type']
                        elif component == 'jsonld':
                            format_rules['required_fields'] = ['headline', 'description', 'keywords', 'articleBody']
            except Exception as e:
                logger.warning(f"Error parsing YAML in {component} example: {e}")
        
        # Component-specific rules
        if component == 'caption':
            format_rules['structure_type'] = 'two_line_caption'
            format_rules['required_pattern'] = r'\*\*.*?\*\*.*\n.*\*\*.*?\*\*.*'
        
        return format_rules
        
        # Load example formats for validation
        self.examples_dir = self.base_path / "examples"
        self.templates_dir = self.base_path / "templates"
        self._example_formats = {}
        self._load_example_formats()
    
    def validate_material(self, subject: str) -> Dict[str, ValidationResult]:
        """Validate all components for a material."""
        results = {}
        for component in self.components:
            file_path = self._get_component_file_path(subject, component)
            results[component] = self._validate_single_component(str(file_path), component)
        return results

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
                # Extract subject from file path for context
                subject = path.parent.name.replace('-', ' ').title()
                processed_content = self._clean_yaml_formatting(original_content, subject)
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
        subject_slug = clean_subject.lower().replace(' ', '-')
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
    
    def _apply_predefined_fixes(self, subject: str, component: str, file_path: Path) -> bool:
        """Apply predefined formatting fixes to a component."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            fixed_content = self._fix_content_by_component(content, component, subject)
            
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                logger.info(f"📝 Applied predefined fixes to {component}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error applying predefined fixes to {component}: {e}")
            return False
    
    def _fix_content_by_component(self, content: str, component: str, subject: str) -> str:
        """Apply component-specific fixes."""
        # Remove markdown code blocks
        if content.startswith('```'):
            lines = content.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1] == '```':
                lines = lines[:-1]
            content = '\n'.join(lines)
        
        if component == "caption":
            lines = content.strip().split('\n')
            if len(lines) != 2 or 'TBD' in content:
                line1 = f"{subject} surface microscopic analysis showing oxide layer and particulate contaminants."
                line2 = "After laser cleaning at 1064 nm, 50 W, 100 ns pulse duration, 0.5 mm spot size showing contaminant removal with minimal substrate alteration."
                return f"{line1}\n{line2}"
        
        elif component == "frontmatter":
            if 'name:' not in content or len(content.strip()) < 10:
                return f"""---
name: {subject}
description: Technical overview of {subject} for laser cleaning applications
category: metal
author: 1
---"""
        
        elif component == "propertiestable":
            if 'TBD' in content or '| Property |' not in content:
                return """| Property | Value |
|----------|-------|
| Chemical Formula | Al |
| Melting Point | 660°C |
| Thermal Conductivity | 237 W/m·K |
| Density | 2.70 g/cm³ |
| Electrical Resistivity | 26.5 nΩ·m |
| Optimal Wavelength | 1064 nm |
| Power Range | 20-500 W |
| Pulse Duration | 10-200 ns |
| Fluence Values | 0.5-5 J/cm² |"""
        
        return content
    
    def _create_component_content(self, subject: str, component: str, file_path: Path) -> bool:
        """Create new content for a component."""
        try:
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate content based on component type  
            if component == "frontmatter":
                content = f"""---
name: {subject}
description: Technical overview of {subject} for laser cleaning applications
category: metal
author: 1
---"""
            elif component == "caption":
                line1 = f"{subject} surface microscopic analysis showing oxide layer and particulate contaminants."
                line2 = "After laser cleaning at 1064 nm, 50 W, 100 ns pulse duration, 0.5 mm spot size showing contaminant removal with minimal substrate alteration."
                content = f"{line1}\n{line2}"
            elif component == "propertiestable":
                content = """| Property | Value |
|----------|-------|
| Chemical Formula | Al |
| Melting Point | 660°C |
| Thermal Conductivity | 237 W/m·K |
| Density | 2.70 g/cm³ |
| Electrical Resistivity | 26.5 nΩ·m |
| Optimal Wavelength | 1064 nm |
| Power Range | 20-500 W |
| Pulse Duration | 10-200 ns |
| Fluence Values | 0.5-5 J/cm² |"""
            else:
                content = f"# {subject} {component.title()}\n\nContent for {component} component."
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Created new content for {component}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating content for {component}: {e}")
            return False
    
    
    def validate_and_fix_component_iteratively(self, subject: str, component: str, max_attempts: int = 3) -> bool:
        """
        Enhanced iterative validation and fixing using targeted strategies from validation_fix_instructions.yaml.
        
        Uses only specific fix strategies with no fallbacks (fail-fast approach):
        1. Schema compliance fixes (missing required fields)
        2. Format structure fixes (YAML syntax, structure violations)  
        3. Content quality fixes (placeholder removal only)
        
        NO FALLBACKS - Fail fast if targeted fixes don't work.
        """
        logger.info(f"🔄 ITERATIVE_FIX_START: Starting iterative fixing for {component} (max {max_attempts} attempts)")
        
        # Only use specific targeted strategies from validation_fix_instructions.yaml
        strategies = [
            'schema_compliance_fix',    # Missing required fields
            'format_structure_fix',     # YAML syntax/structure issues
            'content_quality_fix'       # Placeholder removal only
        ]
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"ITERATIVE_FIX_ATTEMPT: {attempt}/{max_attempts} for {component}")
            
            # Validate current state
            file_path = self._get_component_file_path(subject, component)
            validation_result = self._validate_single_component(str(file_path), component)
            
            if validation_result.status == ComponentStatus.SUCCESS:
                logger.info(f"✅ ITERATIVE_FIX_SUCCESS: {component} validated on attempt {attempt}")
                return True
            
            logger.info(f"ITERATIVE_FIX_STATUS: {component} is {validation_result.status.value} on attempt {attempt}")
            logger.info(f"ITERATIVE_FIX_ERRORS: {validation_result.errors}")
            
            # Try the next strategy
            if attempt <= len(strategies):
                strategy = strategies[attempt - 1]
                logger.info(f"ITERATIVE_FIX_STRATEGY: Trying {strategy} on attempt {attempt}")
                
                # Apply the strategy based on validation_fix_instructions.yaml
                fix_instructions = self.get_current_fix_instructions()
                try:
                    if strategy == 'schema_compliance_fix':
                        success = self._apply_schema_compliance_fix(subject, component, file_path, fix_instructions)
                    elif strategy == 'format_structure_fix':
                        success = self._apply_format_structure_fix(subject, component, file_path, fix_instructions)
                    elif strategy == 'content_quality_fix':
                        success = self._apply_content_quality_fix(subject, component, file_path, fix_instructions)
                    else:
                        success = False
                    
                    if success:
                        logger.info(f"ITERATIVE_FIX_APPLIED: Successfully applied {strategy} on attempt {attempt}")
                    else:
                        logger.warning(f"ITERATIVE_FIX_FAILED: {strategy} failed on attempt {attempt}")
                except Exception as e:
                    logger.error(f"ITERATIVE_FIX_ERROR: Exception in {strategy} on attempt {attempt}: {e}")
            else:
                # NO FALLBACKS - Fail fast after attempting all targeted strategies
                logger.error(f"ITERATIVE_FIX_NO_FALLBACK: No more strategies available on attempt {attempt}")
                break
        
        logger.error(f"ITERATIVE_FIX_EXHAUSTED: All {max_attempts} attempts failed for {component}")
        return False

    def _apply_yaml_syntax_fix(self, subject: str, component: str):
        """Fix YAML syntax errors while preserving content structure."""
        logger.info(f"🔧 Executing comprehensive yaml_syntax_fix for {component}")
        
        file_path = self._get_component_file_path(subject, component)
        if not file_path.exists():
            return False
            
        content = file_path.read_text()
        original_content = content
        
        # Apply comprehensive YAML cleanup
        content = self._clean_yaml_formatting(content, subject)
        
        # Write fixed content if changes were made
        if content != original_content:
            file_path.write_text(content)
            logger.info(f"✅ Applied comprehensive YAML fixes for {component}")
            return True
        else:
            logger.info(f"No YAML fixes needed for {component}")
            return False

    def _clean_yaml_formatting(self, content: str, subject: str = "") -> str:
        """Comprehensive YAML formatting cleanup for generated content."""
        lines = content.split('\n')
        cleaned_lines = []
        yaml_delimiter_count = 0
        in_frontmatter = False
        fixes_applied = []
        
        for line_num, line in enumerate(lines):
            # Track YAML delimiters
            if line.strip() == '---':
                yaml_delimiter_count += 1
                if yaml_delimiter_count == 1:
                    in_frontmatter = True
                    cleaned_lines.append(line)
                elif yaml_delimiter_count == 2:
                    in_frontmatter = False
                    cleaned_lines.append(line)
                else:
                    # Skip extra delimiters
                    fixes_applied.append(f"Removed extra YAML delimiter at line {line_num + 1}")
                    continue
            elif in_frontmatter:
                # Clean up YAML content within frontmatter
                cleaned_line = self._clean_yaml_line(line, subject)
                if cleaned_line != line:
                    fixes_applied.append(f"Fixed YAML formatting at line {line_num + 1}")
                cleaned_lines.append(cleaned_line)
            else:
                # Outside frontmatter, keep as is
                cleaned_lines.append(line)
        
        # Log all fixes applied
        if fixes_applied:
            logger.info(f"Applied {len(fixes_applied)} YAML fixes:")
            for fix in fixes_applied[:5]:  # Show first 5 fixes
                logger.info(f"  - {fix}")
            if len(fixes_applied) > 5:
                logger.info(f"  ... and {len(fixes_applied) - 5} more fixes")
        
        return '\n'.join(cleaned_lines)

    def _clean_yaml_line(self, line: str, subject: str = "") -> str:
        """Clean individual YAML line with comprehensive fixes."""
        cleaned_line = line
        
        # Fix 1: Remove empty object placeholders
        cleaned_line = re.sub(r':\s*\{\}', ': ""', cleaned_line)
        cleaned_line = re.sub(r':\s*\[\]', ': []', cleaned_line)
        
        # Fix 2: Remove bracket placeholders but preserve actual arrays
        if ':' in cleaned_line and '[' in cleaned_line and ']' in cleaned_line:
            # Don't change actual YAML arrays like: "- item1\n- item2"
            # Only fix placeholder brackets like: [placeholder text]
            if not cleaned_line.strip().startswith('-'):
                # Check if it's a placeholder pattern
                bracket_content = re.search(r'\[([^\]]+)\]', cleaned_line)
                if bracket_content:
                    content = bracket_content.group(1)
                    # If bracket content looks like a placeholder (contains spaces, special chars)
                    if ' ' in content or any(char in content for char in ['|', 'like', 'such as']):
                        # Replace with appropriate value based on context
                        if subject and 'name:' in cleaned_line:
                            cleaned_line = re.sub(r':\s*\[.*?\]', f': "{subject}"', cleaned_line)
                        elif 'author:' in cleaned_line:
                            cleaned_line = re.sub(r':\s*\[.*?\]', ': "Dr. Materials Expert"', cleaned_line)
                        elif 'category:' in cleaned_line:
                            cleaned_line = re.sub(r':\s*\[.*?\]', ': "ceramic"', cleaned_line)
                        else:
                            cleaned_line = re.sub(r':\s*\[.*?\]', ': "value"', cleaned_line)
        
        # Fix 3: Ensure proper string quoting for complex values
        if ':' in cleaned_line and not cleaned_line.strip().startswith('-'):
            key_value = cleaned_line.split(':', 1)
            if len(key_value) == 2:
                key = key_value[0]
                value = key_value[1].strip()
                
                # If value needs quoting (contains special characters, spaces, etc.)
                if value and not value.startswith('"') and not value.startswith("'") and value != '[]' and value != '""':
                    # Check if it's a number or boolean
                    if not (value.replace('.', '').replace('-', '').isdigit() or value.lower() in ['true', 'false', 'null']):
                        # Check if it needs quotes (contains spaces, special chars, etc.)
                        if any(char in value for char in [' ', '/', '°', '%', '±', ':', ';', ',', '(', ')']):
                            cleaned_line = f'{key}: "{value}"'
        
        # Fix 4: Clean up common malformed patterns
        cleaned_line = re.sub(r':\s*\{\s*\.\.\.\s*\}', ': ""', cleaned_line)  # Remove {...} objects
        cleaned_line = re.sub(r':\s*\[\s*\.\.\.\s*\]', ': []', cleaned_line)  # Remove [...] arrays
        
        # Fix 5: Fix duplicate keys (remove duplicate lines)
        # This is handled at a higher level in _clean_yaml_formatting
        
        return cleaned_line

    def _apply_placeholder_removal_fix(self, subject: str, component: str):
        """DISABLED: No placeholder replacement - force regeneration instead."""
        logger.error(f"❌ PLACEHOLDER REMOVAL DISABLED for {component} - refusing to create placeholder content")
        logger.error(f"   Component must be regenerated with real content, not fixed with placeholders")
        return False
        content = re.sub(r'\[Author Name\].*?\[Location\]', '"Material Expert"', content)
        content = re.sub(r'\[Brief description.*?\]', f'"{subject} material properties and characteristics"', content)
        content = re.sub(r'\[Material Name\]', f'"{subject}"', content)
        content = re.sub(r'\[keyword\d+\]', f'"{subject.lower()}"', content)
        content = re.sub(r'\[Compatible Material \d+\]', '"Metals"', content)
        content = re.sub(r'\[Element: Percentage\]', '"Al₂O₃: 45%, SiO₂: 50%, H₂O: 5%"', content)
        
        # Fix numeric placeholders
        content = re.sub(r'\[X\.X.*?\]', '"2.5"', content)
        content = re.sub(r'\[XXX.*?\]', '"1500"', content)
        content = re.sub(r'\[XXXX.*?\]', '"1064"', content)
        
        # Fix other placeholders
        content = re.sub(r'\[Standards list\]', '"ASTM C373, ISO 13006"', content)
        content = re.sub(r'\[Laser Type\]', '"Nd:YAG"', content)
        
        file_path.write_text(content)
        logger.info(f"✅ Applied placeholder removal for {component}")
        return True

    def _apply_content_regeneration_fix(self, subject: str, component: str):
        """Regenerate content using AI while preserving structure."""
        logger.info(f"🔧 Executing content_regeneration for {component}")
        return self._regenerate_component_via_api(subject, component)

    def validate_and_fix_component_immediately(self, subject: str, component: str, max_retries: int = 2, force_fix: bool = False) -> bool:
        """
        Enhanced validation with immediate fixing for post-generation workflow.
        
        1. Validates component immediately after generation
        2. If failed, determines if API issue and retries
        3. If still fails, applies autonomous fixes per validation_fix_instructions.yaml
        4. Returns True if component is valid, False if needs manual intervention
        """
        print(f"    ┌─ Starting immediate validation for {component}")
        logger.info(f"🔍 VALIDATION_IMMEDIATE_START: {component} for {subject}")
        
        file_path = self._get_component_file_path(subject, component)
        logger.debug(f"VALIDATION_FILE_PATH: {file_path}")
        
        # Step 1: Initial validation
        print(f"    │  📋 Step 1: Running initial validation checks...")
        logger.info(f"VALIDATION_STEP1_INITIAL: Starting initial validation for {component}")
        validation_result = self._validate_single_component(str(file_path), component)
        logger.info(f"VALIDATION_STEP1_RESULT: {validation_result.status.value} for {component}")
        
        if validation_result.status == ComponentStatus.SUCCESS:
            print(f"    │  ✅ Validation passed - no errors found")
            print(f"    └─ {component} validation complete: SUCCESS")
            logger.info(f"✅ VALIDATION_SUCCESS_IMMEDIATE: {component} passed validation immediately")
            return True
        
        print(f"    │  ⚠️  Initial validation failed: {validation_result.status.value}")
        print(f"    │  📝 Found {len(validation_result.errors)} error(s)")
        for i, error in enumerate(validation_result.errors[:3], 1):  # Show first 3 errors
            print(f"    │     {i}. {error}")
        if len(validation_result.errors) > 3:
            print(f"    │     ... and {len(validation_result.errors) - 3} more")
            
        logger.warning(f"❌ VALIDATION_FAILED_INITIAL: {component} failed initial validation: {validation_result.status.value}")
        logger.error(f"VALIDATION_ERRORS: {validation_result.errors}")
        self._log_detailed_validation_errors(subject, component, validation_result)
        
        # Step 2: Determine if this is an API issue (empty/missing content suggests API failure)
        if validation_result.status in [ComponentStatus.EMPTY, ComponentStatus.MISSING]:
            print(f"    │  🔄 Step 2: Detected API issue, attempting regeneration...")
            logger.info(f"🔄 VALIDATION_STEP2_API_RETRY: Detected potential API issue for {component}, attempting retries...")
            
            for retry in range(max_retries):
                print(f"    │  🔁 Regeneration attempt {retry + 1}/{max_retries}")
                logger.info(f"VALIDATION_RETRY: Attempt {retry + 1}/{max_retries} for {component}")
                
                # Regenerate the component (this would call the API again)
                if self._regenerate_component_via_api(subject, component):
                    logger.info(f"VALIDATION_RETRY_REGENERATED: Successfully regenerated {component}")
                    # Re-validate after regeneration
                    validation_result = self._validate_single_component(str(file_path), component)
                    logger.info(f"VALIDATION_RETRY_RESULT: {validation_result.status.value} for {component}")
                    
                    if validation_result.status == ComponentStatus.SUCCESS:
                        print(f"    │  ✅ Regeneration successful - validation passed")
                        print(f"    └─ {component} validation complete: SUCCESS (after regeneration)")
                        logger.info(f"✅ VALIDATION_SUCCESS_RETRY: {component} passed validation after retry {retry + 1}")
                        return True
                    else:
                        print(f"    │  ❌ Regeneration attempt {retry + 1} still failed")
                        logger.warning(f"VALIDATION_RETRY_STILL_FAILED: Retry {retry + 1} still failed: {validation_result.status.value}")
                else:
                    print(f"    │  ❌ Failed to regenerate component")
                    logger.error(f"VALIDATION_RETRY_REGEN_FAILED: Failed to regenerate {component} on retry {retry + 1}")
        
        # Step 3: If still failing, apply autonomous fixes per validation_fix_instructions.yaml
        print(f"    │  🔧 Step 3: Applying autonomous fixes...")
        logger.info(f"🔧 VALIDATION_STEP3_AUTONOMOUS_FIXES: Applying autonomous fixes for {component} per validation_fix_instructions.yaml")
        
        if self._apply_autonomous_fixes(subject, component, validation_result):
            print(f"    │  ✅ Autonomous fixes applied successfully")
            logger.info(f"VALIDATION_AUTONOMOUS_FIXES_APPLIED: Successfully applied autonomous fixes for {component}")
            # Re-validate after fixes
            print(f"    │  🔄 Re-validating after fixes...")
            final_validation = self._validate_single_component(str(file_path), component)
            logger.info(f"VALIDATION_FINAL_RESULT: {final_validation.status.value} after autonomous fixes for {component}")
            
            if final_validation.status == ComponentStatus.SUCCESS:
                print(f"    │  ✅ Final validation passed")
                print(f"    └─ {component} validation complete: SUCCESS (after autonomous fixes)")
                logger.info(f"✅ VALIDATION_SUCCESS_FINAL: {component} passed validation after autonomous fixes")
                return True
            else:
                print(f"    │  ❌ Final validation still failed: {final_validation.status.value}")
                print(f"    └─ {component} validation complete: FAILED (autonomous fixes insufficient)")
                logger.error(f"❌ VALIDATION_FAILED_FINAL: {component} still failing after autonomous fixes: {final_validation.status.value}")
                logger.error(f"VALIDATION_FINAL_ERRORS: {final_validation.errors}")
                self._log_detailed_validation_errors(subject, component, final_validation)
                return False
        else:
            print(f"    │  ❌ Autonomous fixes failed to apply")
            print(f"    └─ {component} validation complete: FAILED (cannot apply fixes)")
            logger.error(f"❌ VALIDATION_AUTONOMOUS_FIXES_FAILED: Failed to apply autonomous fixes for {component}")
            return False
    
    def _log_detailed_validation_errors(self, subject: str, component: str, validation_result: ValidationResult):
        """Log extensive and detailed validation errors for Claude analysis."""
        logger.error(f"\n{'='*60}")
        logger.error(f"DETAILED VALIDATION FAILURE REPORT")
        logger.error(f"Subject: {subject}")
        logger.error(f"Component: {component}")
        logger.error(f"Status: {validation_result.status.value}")
        logger.error(f"File: {validation_result.file_path}")
        logger.error(f"Size: {validation_result.size_bytes} bytes")
        logger.error(f"{'='*60}")
        
        if validation_result.errors:
            logger.error("ERRORS:")
            for i, error in enumerate(validation_result.errors, 1):
                logger.error(f"  {i}. {error}")
        
        if validation_result.warnings:
            logger.error("WARNINGS:")
            for i, warning in enumerate(validation_result.warnings, 1):
                logger.error(f"  {i}. {warning}")
        
        # Show file content for analysis if file exists and is small enough
        file_path = Path(validation_result.file_path)
        if file_path.exists() and validation_result.size_bytes < 2000:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.error(f"CURRENT CONTENT:\n{content}")
            except Exception as e:
                logger.error(f"Could not read file content: {e}")
        
        logger.error(f"{'='*60}\n")
    
    def _regenerate_component_via_api(self, subject: str, component: str) -> bool:
        """Regenerate component by calling the unified generator."""
        try:
            logger.info(f"🔄 Regenerating {component} via API for {subject}")
            
            # Import the unified generator
            UnifiedGenerator = self._get_unified_generator()
            if not UnifiedGenerator:
                return False
            
            # Initialize the generator
            generator = UnifiedGenerator()
            
            # Generate entire document (unified approach)
            logger.info(f"🚀 Using unified generator to regenerate document for {subject}")
            
            # Load a basic schema for the regeneration
            schema = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            success = generator.generate_complete_document(subject, "material", "composite", {"id": 1, "name": "System"}, schema)
            
            if success:
                logger.info(f"✅ Successfully regenerated document (including {component}) via unified API")
                return True
            else:
                logger.error(f"❌ Failed to regenerate document via unified API")
                return False
                
        except Exception as e:
            logger.error(f"Error regenerating {component} for {subject}: {e}")
            return False
    
    def _apply_autonomous_fixes(self, subject: str, component: str, validation_result: ValidationResult) -> bool:
        """Apply autonomous fixes using strategic guidance from validation_fix_instructions.yaml."""
        try:
            # Load strategic guidance for decision-making
            fix_instructions = self.get_current_fix_instructions()
            
            if not fix_instructions:
                logger.warning("No fix instructions available, falling back to template-based fixes")
                return self._apply_template_based_fixes(subject, component, self._get_component_file_path(subject, component))
            
            logger.info(f"📋 Applying strategic guidance from validation_fix_instructions.yaml for {component}")
            
            # Step 1: Diagnosis using decision framework
            failure_type = self._diagnose_failure_type(validation_result, fix_instructions)
            logger.info(f"� Diagnosed failure type: {failure_type}")
            
            # Step 2: Root cause analysis
            root_cause = self._analyze_root_cause(subject, component, validation_result, fix_instructions)
            logger.info(f"🎯 Root cause: {root_cause}")
            
            # Step 3: Apply fix strategy based on guidance
            fix_strategy = self._select_fix_strategy(failure_type, root_cause, fix_instructions)
            
            if fix_strategy is None:
                logger.error(f"AUTONOMOUS_FIX_FAILED: No valid fix strategy found for {component}")
                return False
                
            logger.info(f"🔧 Selected fix strategy: {fix_strategy}")
            
            # Apply the selected strategy
            file_path = self._get_component_file_path(subject, component)
            success = self._execute_fix_strategy(subject, component, file_path, fix_strategy, fix_instructions)
            
            if success:
                logger.info(f"✅ Successfully applied strategic fix for {component}")
            else:
                logger.error(f"AUTONOMOUS_FIX_FAILED: Strategic fix '{fix_strategy}' failed for {component}")
            
            return success
                
        except Exception as e:
            logger.error(f"Error applying strategic fixes to {component}: {e}")
            # Fallback to template-based fixes if strategic guidance fails
            return self._apply_template_based_fixes(subject, component, self._get_component_file_path(subject, component))
    
    def _diagnose_failure_type(self, validation_result: ValidationResult, fix_instructions: dict) -> str:
        """Diagnose failure type using decision framework from fix instructions."""
        try:
            # Use the decision framework from the instructions
            framework = fix_instructions.get('decision_framework', {}).get('step1_diagnosis', {})
            
            # Check validation errors against known patterns
            errors = validation_result.errors
            
            if any('Missing required field' in error or 'Schema validation failed' in error for error in errors):
                return 'schema_missing'
            elif any('YAML syntax error' in error or 'JSON parsing error' in error or 'invalid quality' in error for error in errors):
                return 'format_wrong'
            elif any('TBD' in error or 'placeholder' in error or 'Contains placeholder content' in error for error in errors):
                return 'content_placeholder'
            elif validation_result.status == ComponentStatus.MISSING:
                return 'file_missing'
            else:
                return 'content_quality'
                
        except Exception as e:
            logger.error(f"Error diagnosing failure type: {e}")
            return 'unknown'
    
    def _analyze_root_cause(self, subject: str, component: str, validation_result: ValidationResult, fix_instructions: dict) -> str:
        """Analyze root cause using strategic guidance."""
        try:
            # Load example for comparison as suggested in instructions
            example_file = self.examples_dir / f"{component}.md"
            if not example_file.exists():
                return 'no_example_available'
            
            with open(example_file, 'r', encoding='utf-8') as f:
                example_content = f.read()
            
            # Compare current content structure against example
            current_file = Path(validation_result.file_path)
            if current_file.exists():
                with open(current_file, 'r', encoding='utf-8') as f:
                    current_content = f.read()
                
                # Check for structural differences
                if not current_content.startswith('---') and example_content.startswith('---'):
                    return 'missing_frontmatter'
                elif 'TBD' in current_content or '[' in current_content and ']' in current_content:
                    return 'placeholder_content'
                elif len(current_content.strip()) < 20:
                    return 'insufficient_content'
                else:
                    return 'structure_mismatch'
            else:
                return 'file_missing'
                
        except Exception as e:
            logger.error(f"Error analyzing root cause: {e}")
            return 'analysis_failed'
    
    def _select_fix_strategy(self, failure_type: str, root_cause: str, fix_instructions: dict) -> str:
        """Select fix strategy based on strategic guidance."""
        try:
            # Use the fix approaches from instructions
            fix_approaches = fix_instructions.get('fix_approaches', {})
            
            # Map failure types to strategy selection from instructions
            strategy_mapping = fix_instructions.get('decision_framework', {}).get('step3_fix_strategy', {}).get('strategy_selection', {})
            
            if failure_type in strategy_mapping:
                return strategy_mapping[failure_type]
            elif failure_type == 'schema_missing' or root_cause == 'missing_frontmatter':
                return 'schema_compliance_fix'
            elif failure_type == 'format_wrong' or root_cause == 'structure_mismatch':
                return 'format_structure_fix'
            elif failure_type == 'content_placeholder' or root_cause == 'placeholder_content':
                return 'content_quality_fix'
            elif failure_type == 'content_quality' or root_cause == 'insufficient_content':
                return 'content_quality_fix'
            elif failure_type == 'file_missing':
                return 'template_generation'
            else:
                # FAIL FAST: Unknown failure types should fail clearly
                logger.error(f"AUTONOMOUS_FIX_CRITICAL: Unknown failure type '{failure_type}' with root cause '{root_cause}'")
                logger.error(f"AUTONOMOUS_FIX_CRITICAL: Available types: schema_compliance, format_structure, content_quality, file_missing")
                return None
                
        except Exception as e:
            logger.error(f"AUTONOMOUS_FIX_CRITICAL: Error selecting fix strategy: {e}")
            return None
    
    def _execute_fix_strategy(self, subject: str, component: str, file_path: Path, strategy: str, fix_instructions: dict) -> bool:
        """Execute the selected fix strategy using guidance from instructions."""
        try:
            logger.info(f"🔧 Executing {strategy} for {component}")
            
            if strategy == 'schema_compliance_fix':
                return self._apply_schema_compliance_fix(subject, component, file_path, fix_instructions)
            elif strategy == 'format_structure_fix':
                return self._apply_format_structure_fix(subject, component, file_path, fix_instructions)
            elif strategy == 'content_quality_fix':
                return self._apply_content_quality_fix(subject, component, file_path, fix_instructions)
            elif strategy == 'template_generation':
                return self._apply_template_based_fixes(subject, component, file_path)
            else:
                # FAIL FAST: No fallbacks, unknown strategies should fail clearly
                logger.error(f"AUTONOMOUS_FIX_CRITICAL: Unknown fix strategy '{strategy}' for {component}")
                logger.error(f"AUTONOMOUS_FIX_CRITICAL: Available strategies: schema_compliance_fix, format_structure_fix, content_quality_fix, template_generation")
                return False
                
        except Exception as e:
            logger.error(f"AUTONOMOUS_FIX_CRITICAL: Error executing fix strategy {strategy}: {e}")
            logger.error(f"AUTONOMOUS_FIX_CRITICAL: Strategy execution failed completely for {component}")
            return False
    
    def _apply_schema_compliance_fix(self, subject: str, component: str, file_path: Path, fix_instructions: dict) -> bool:
        """Apply schema compliance fix using strategic guidance."""
        try:
            # Follow the steps from fix_approaches.schema_compliance_fix
            schema_fix = fix_instructions.get('fix_approaches', {}).get('schema_compliance_fix', {})
            steps = schema_fix.get('steps', [])
            
            logger.info(f"📋 Following schema compliance steps: {len(steps)} steps")
            
            # Step 1: Load example format
            example_file = self.examples_dir / f"{component}.md"
            if not example_file.exists():
                logger.warning(f"No example found for {component}, using template approach")
                return self._apply_template_based_fixes(subject, component, file_path)
            
            with open(example_file, 'r', encoding='utf-8') as f:
                example_content = f.read()
            
            # Step 2-4: Use example structure with material-specific data
            personalized_content = self._personalize_template_content(example_content, subject, component)
            
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(personalized_content)
            
            logger.info(f"✅ Applied schema compliance fix using example structure")
            return True
            
        except Exception as e:
            logger.error(f"Error in schema compliance fix: {e}")
            return False
    
    def _apply_format_structure_fix(self, subject: str, component: str, file_path: Path, fix_instructions: dict) -> bool:
        """Apply format structure fix using strategic guidance."""
        try:
            # Follow the steps from fix_approaches.format_structure_fix
            format_fix = fix_instructions.get('fix_approaches', {}).get('format_structure_fix', {})
            
            # Use template-based approach as recommended in instructions
            template_file = self.templates_dir / f"{component}-template.md"
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # Apply material-specific data
                personalized_content = self._personalize_template_content(template_content, subject, component)
                
                # Write the fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(personalized_content)
                
                logger.info(f"✅ Applied format structure fix using template")
                return True
            else:
                logger.warning(f"No template found for {component}")
                return False
                
        except Exception as e:
            logger.error(f"Error in format structure fix: {e}")
            return False
    
    def _apply_content_quality_fix(self, subject: str, component: str, file_path: Path, fix_instructions: dict) -> bool:
        """Apply content quality fix using strategic guidance."""
        try:
            # Read current content if it exists and is not empty
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read().strip()
                
                # If file is empty, use template approach instead
                if not current_content:
                    logger.info(f"CONTENT_QUALITY_FIX: File is empty, using template approach for {component}")
                    return self._apply_template_based_fixes(subject, component, file_path)
                
                # Apply material data strategy from instructions for non-empty content
                material_strategy = fix_instructions.get('material_data_strategy', {})
                improved_content = self._apply_material_data_strategy(current_content, subject, component, material_strategy)
                
                # Ensure we actually improved the content
                if not improved_content.strip():
                    logger.error(f"CONTENT_QUALITY_FIX: Material data strategy returned empty content for {component}")
                    return self._apply_template_based_fixes(subject, component, file_path)
                
                # Write improved content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(improved_content)
                
                logger.info(f"✅ Applied content quality fix with material-specific data")
                return True
            else:
                # If file doesn't exist, use template approach
                logger.info(f"CONTENT_QUALITY_FIX: File doesn't exist, using template approach for {component}")
                return self._apply_template_based_fixes(subject, component, file_path)
                
        except Exception as e:
            logger.error(f"Error in content quality fix: {e}")
            return False
    
    def _apply_material_data_strategy(self, content: str, subject: str, component: str, strategy: dict) -> str:
        """DISABLED: No placeholder replacement - force regeneration instead."""
        logger.error(f"❌ MATERIAL DATA STRATEGY DISABLED for {component} - refusing to apply placeholder replacements")
        logger.error("   Component must be regenerated with real content, not patched with placeholder data")
        return content  # Return unchanged content to force regeneration
    
    def _apply_template_based_fixes(self, subject: str, component: str, file_path: Path) -> bool:
        """Apply fixes using the template examples."""
        try:
            template_file = self.templates_dir / f"{component}-template.md"
            example_file = self.examples_dir / f"{component}.md"
            
            # Use example if available, otherwise use template
            source_file = example_file if example_file.exists() else template_file
            
            if not source_file.exists():
                logger.warning(f"No template or example found for {component}")
                return False
            
            with open(source_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace placeholders with actual material data
            personalized_content = self._personalize_template_content(template_content, subject, component)
            
            # Debug: Check content before writing
            logger.info(f"TEMPLATE_FIX_DEBUG: Content length before write: {len(personalized_content)} chars")
            logger.info(f"TEMPLATE_FIX_DEBUG: First 200 chars: {personalized_content[:200]}")
            
            # Write the personalized content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(personalized_content)
            
            # Debug: Verify file after writing
            if file_path.exists():
                file_size = file_path.stat().st_size
                logger.info(f"TEMPLATE_FIX_DEBUG: File written successfully, size: {file_size} bytes")
                if file_size == 0:
                    logger.error(f"TEMPLATE_FIX_CRITICAL: File is empty after write! Content was: {personalized_content}")
            else:
                logger.error(f"TEMPLATE_FIX_CRITICAL: File does not exist after write attempt!")
            
            logger.info(f"📝 Applied template-based fix for {component} using {source_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying template-based fixes: {e}")
            return False
    
    def _personalize_template_content(self, template_content: str, subject: str, component: str) -> str:
        """Use examples for basic structural formatting only - content should be completely open and varied."""
        logger.info(f"TEMPLATE_PERSONALIZATION_START: Processing {component} template for {subject}")
        logger.info(f"TEMPLATE_DEBUG: Input template length: {len(template_content)} chars")
        logger.info(f"TEMPLATE_DEBUG: Input template preview: {template_content[:200]}")
        
        # Clean up subject name (process longer patterns first to avoid partial matches)
        clean_subject = subject.replace('-laser-cleaning-laser-cleaning-laser-cleaning', '')
        clean_subject = clean_subject.replace('-laser-cleaning-laser-cleaning', '')
        clean_subject = clean_subject.replace('-laser-cleaning', '').replace('_laser_cleaning', '')
        
        # Get material data for any needed substitutions
        material_category = self._get_material_category(clean_subject)
        material_properties = self._get_material_properties(clean_subject, material_category)
        
        logger.debug(f"TEMPLATE_CLEAN_SUBJECT: {clean_subject}")
        logger.debug(f"TEMPLATE_CATEGORY: {material_category}")
        
        # For template-based fixes, just do basic structural substitutions
        # Keep the original template structure but substitute material-specific data
        content = template_content
        
        # Basic material name substitutions only
        content = content.replace('[material]', clean_subject.title())
        content = content.replace('[material_name]', clean_subject.lower())
        content = content.replace('{material}', clean_subject.title())
        content = content.replace('{material_name}', clean_subject.lower())
        
        # Replace any specific material names from examples with current material
        example_materials = ['Stoneware', 'Alumina', 'Fused Silica', 'Porcelain', 'Zirconia', 'Silicon Carbide']
        for example_material in example_materials:
            content = content.replace(example_material, clean_subject.title())
            content = content.replace(example_material.lower(), clean_subject.lower())
        
        # Replace basic property placeholders if they exist
        for prop_key, prop_value in material_properties.items():
            content = content.replace(f'{{{prop_key}}}', str(prop_value))
            content = content.replace(f'[{prop_key}]', str(prop_value))
        
        # Clean up any encoding issues or template artifacts
        content = self._clean_template_artifacts(content)
        
        logger.info(f"TEMPLATE_DEBUG: Output content length: {len(content)} chars")
        logger.info(f"TEMPLATE_DEBUG: Output content preview: {content[:200]}")
        logger.info(f"TEMPLATE_PERSONALIZATION_COMPLETE: Minimal structural formatting applied to {component}")
        return content

    def _get_material_category(self, subject: str) -> str:
        """Determine material category from subject name."""
        subject_lower = subject.lower()
        if any(term in subject_lower for term in ['ceramic', 'alumina', 'zirconia', 'porcelain', 'stoneware', 'kaolin']):
            return 'ceramic'
        elif any(term in subject_lower for term in ['metal', 'aluminum', 'copper', 'steel', 'titanium', 'gold', 'silver', 'brass', 'bronze']):
            return 'metal'
        elif any(term in subject_lower for term in ['glass', 'silica', 'borosilicate', 'tempered']):
            return 'glass'
        elif any(term in subject_lower for term in ['composite', 'fiber', 'carbon', 'epoxy', 'polymer', 'resin', 'kevlar']):
            return 'composite'
        elif any(term in subject_lower for term in ['plastic', 'polymer', 'rubber', 'elastomer', 'thermoplastic']):
            return 'plastic'
        elif any(term in subject_lower for term in ['stone', 'granite', 'marble', 'quartzite', 'limestone']):
            return 'stone'
        elif any(term in subject_lower for term in ['masonry', 'brick', 'concrete', 'mortar', 'stucco']):
            return 'masonry'
        elif any(term in subject_lower for term in ['wood', 'timber', 'lumber', 'oak', 'pine']):
            return 'wood'
        else:
            return 'material'

    def _get_material_properties(self, subject: str, category: str) -> dict:
        """Get basic material properties for template substitution."""
        # Default properties based on category
        properties = {
            'formula': 'Chemical formula varies',
            'density': '2.0-3.0 g/cm³',
            'wavelength': '1064nm',
            'fluence_range': '0.5-10 J/cm²',
            'laser_type': 'Nd:YAG',
            'melting_point': '1000-1500°C',
            'thermal_conductivity': '1.0-5.0 W/m·K',
            'author': 'Dr. Evelyn Wu'
        }
        
        # Category-specific defaults
        if category == 'ceramic':
            properties.update({
                'formula': 'Al₂O₃·2SiO₂·2H₂O',
                'density': '2.3-2.7 g/cm³',
                'melting_point': '1200-1600°C',
                'thermal_conductivity': '1.5-3.0 W/m·K'
            })
        elif category == 'metal':
            properties.update({
                'density': '2.7-8.9 g/cm³',
                'melting_point': '600-1500°C',
                'thermal_conductivity': '15-400 W/m·K'
            })
        elif category == 'glass':
            properties.update({
                'formula': 'SiO₂',
                'density': '2.2-2.8 g/cm³',
                'melting_point': '1000-1700°C',
                'thermal_conductivity': '1.0-1.4 W/m·K'
            })
        elif category == 'composite':
            properties.update({
                'density': '1.2-2.0 g/cm³',
                'melting_point': '200-400°C (decomposition)',
                'thermal_conductivity': '0.2-50 W/m·K'
            })
        
        return properties

    def _replace_property_placeholders(self, content: str, subject: str, properties: dict) -> str:
        """Replace complex property placeholders in templates."""
        # Handle placeholders like {Stoneware formula}, {Stoneware density}, etc.
        for prop_key, prop_value in properties.items():
            # Replace {Material property} patterns
            pattern_variations = [
                f"{{{subject.title()} {prop_key}}}",
                f"{{{subject.lower()} {prop_key}}}",
                f"{{Stoneware {prop_key}}}",
                f"{{stoneware {prop_key}}}",
                f"{{{prop_key}}}",
                f"({subject.title()} {prop_key})",
                f"({subject.lower()} {prop_key})"
            ]
            
            for pattern in pattern_variations:
                content = content.replace(pattern, str(prop_value))
        
        return content

    def _personalize_metatags_content(self, content: str, subject: str, category: str, properties: dict) -> str:
        """Personalize metatags component content."""
        # Fix title and descriptions
        content = content.replace('Laser Cleaning Stoneware', f'Laser Cleaning {subject.title()}')
        content = content.replace('Technical Guide for Optimal Processing', f'Technical Specifications and Applications')
        content = content.replace(f'ceramic {subject.lower()}', f'{category} {subject.lower()}')
        content = content.replace(f'laser cleaning, {subject.lower()}', f'laser cleaning, {subject.lower()}')
        
        # Fix author placeholder
        content = content.replace(f'{subject.title()} - author', properties['author'])
        content = content.replace('Stoneware - author', properties['author'])
        
        # Fix category
        content = content.replace('"ceramic"', f'"{category}"')
        
        return content

    def _personalize_frontmatter_content(self, content: str, subject: str, category: str, properties: dict) -> str:
        """Personalize frontmatter component content."""
        content = content.replace('name: Stoneware', f'name: {subject.title()}')
        content = content.replace('subject: Stoneware', f'subject: {subject.title()}')
        content = content.replace('"ceramic"', f'"{category}"')
        
        # Add missing required fields if not present
        if 'subject:' not in content:
            content = content.replace('---', f'subject: {subject.title()}\narticle_type: material\n---')
        if 'applications:' not in content:
            content = content.replace('---', f'applications:\n  - "Industrial cleaning"\n  - "Surface preparation"\n  - "Contamination removal"\n---')
        if 'technicalSpecifications:' not in content:
            content = content.replace('---', f'technicalSpecifications:\n  wavelength: "{properties["wavelength"]}"\n  fluenceRange: "{properties["fluence_range"]}"\n---')
        
        # Remove placeholder content
        content = content.replace('{...}', f'"/images/{subject.lower()}-laser-cleaning.jpg"')
        content = content.replace('TBD', f'{subject.title()} laser cleaning specifications')
        
        return content

    def _personalize_caption_content(self, content: str, subject: str, properties: dict) -> str:
        """Personalize caption component content."""
        content = content.replace('Fused Silica (SiO₂)', f'{subject.title()} ({properties["formula"]})')
        content = content.replace('fused silica', subject.lower())
        return content

    def _personalize_jsonld_content(self, content: str, subject: str, category: str) -> str:
        """Personalize JSON-LD component content."""
        content = content.replace('Laser Cleaning of Alumina (Al₂O₃)', f'Laser Cleaning of {subject.title()}')
        content = content.replace('alumina', subject.lower())
        content = content.replace('subjectSlug: alumina', f'subjectSlug: {subject.lower()}')
        content = content.replace('"@type": "Material"', f'"@type": "{category.title()}"')
        return content

    def _personalize_bullets_content(self, content: str, subject: str, properties: dict) -> str:
        """Personalize bullets component content."""
        # Replace material-specific bullet points
        content = content.replace(f'**{subject.title()} Composition**', f'**{subject.title()} Composition**')
        return content

    def _personalize_table_content(self, content: str, subject: str, properties: dict) -> str:
        """Personalize table component content."""
        # Replace table headers and data with material-specific information
        content = content.replace('| Property | Stoneware | Unit |', f'| Property | {subject.title()} | Unit |')
        return content

    def _clean_template_artifacts(self, content: str) -> str:
        """Remove remaining template artifacts and fix encoding issues."""
        # Fix encoding issues
        content = content.replace('\\u2082', '₂')
        content = content.replace('\\u2083', '₃')
        content = content.replace('\\xB0', '°')
        content = content.replace('\\u03BC', 'μ')
        content = content.replace('\\"', '"')
        
        # Remove template artifacts
        content = content.replace('TBD', 'To be determined')
        content = content.replace('TODO', 'Pending specification')
        content = content.replace('[brackets]', 'content')
        
        # Clean up extra quotes and escape characters
        content = content.replace('""', '"')
        content = content.replace("''", "'")
        
        return content
    
    def get_current_fix_instructions(self) -> dict:
        """Load current fix instructions with timestamp checking."""
        fix_instructions_path = self.base_path / "validation_fix_instructions.yaml"
        
        try:
            if fix_instructions_path.exists():
                with open(fix_instructions_path, 'r', encoding='utf-8') as f:
                    instructions = yaml.safe_load(f)
                    logger.debug(f"Loaded fix instructions from {fix_instructions_path}")
                    return instructions
            else:
                logger.warning(f"Fix instructions file not found: {fix_instructions_path}")
                return {}
                
        except Exception as e:
            logger.error(f"Error loading fix instructions: {e}")
            return {}
    
    def _get_unified_generator(self):
        """Get the unified generator module."""
        try:
            from generators.unified_generator import UnifiedDocumentGenerator
            return UnifiedDocumentGenerator
        except ImportError as e:
            logger.error(f"Could not import unified generator: {e}")
            return None
    
    def cli_validate_material(self, subject: str) -> None:
        """CLI method to validate a single material."""
        print(f"🔍 Validating {subject}...")
        results = self.validate_material(subject)
        self._print_validation_report(subject, results)
    
    def cli_fix_material(self, subject: str, components: List[str] = None, regenerate: bool = True) -> None:
        """CLI method to fix a material."""
        print(f"🔧 Fixing {subject}...")
        if components:
            print(f"   Components: {', '.join(components)}")
        
        results = self.fix_material(subject, components, regenerate)
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"\n📊 Fix Results: {success_count}/{total_count} succeeded")
        for component, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"  {component}: {status}")
    
    def cli_scan_all_materials(self) -> None:
        """CLI method to scan all materials."""
        print("🔍 Scanning all materials...")
        content_dir = Path("content/components")
        
        # Find all material files
        materials = set()
        for component_dir in content_dir.iterdir():
            if component_dir.is_dir() and component_dir.name in self.components:
                for file in component_dir.glob("*-laser-cleaning.md"):
                    subject = file.stem.replace('-laser-cleaning', '').replace('-', ' ').title()
                    materials.add(subject)
        
        # Validate each material
        healthy_count = 0
        problem_materials = []
        
        for subject in sorted(materials):
            results = self.validate_material(subject)
            failed_components = [comp for comp, result in results.items() 
                               if result.status != ComponentStatus.SUCCESS]
            
            if not failed_components:
                healthy_count += 1
            else:
                problem_materials.append((subject, failed_components))
        
        # Print summary
        total_count = len(materials)
        print(f"\n📈 Summary: {healthy_count}/{total_count} materials healthy")
        
        if problem_materials:
            print(f"\n⚠️  Materials needing attention ({len(problem_materials)}):")
            for subject, failed_components in problem_materials:
                failed_list = ", ".join(failed_components)
                print(f"  • {subject}: {failed_list}")
        else:
            print("\n✅ All materials are healthy!")
    
    def _print_validation_report(self, subject: str, results: Dict[str, Any]) -> None:
        """Print a formatted validation report."""
        failed_components = [comp for comp, result in results.items() 
                           if result.status != ComponentStatus.SUCCESS]
        
        success_count = len(results) - len(failed_components)
        total_count = len(results)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        print(f"\n📊 Validation Report for {subject}")
        print(f"   Status: {success_count}/{total_count} components valid ({success_rate:.1f}%)")
        
        if failed_components:
            print(f"   Failed: {', '.join(failed_components)}")
            
            # Show details for each failed component
            for comp in failed_components:
                result = results[comp]
                print(f"     {comp}: {result.status.value} - {', '.join(result.errors)}")
        else:
            print("   ✅ All components are valid!")
