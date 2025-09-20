#!/usr/bin/env python3
"""
Frontmatter Management System
Centralized frontmatter loading, validation, and management for the Z-Beam generator.
"""

import json
import yaml
import jsonschema
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from functools import lru_cache
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FrontmatterValidationError(Exception):
    """Raised when frontmatter validation fails"""
    pass

class FrontmatterNotFoundError(Exception):
    """Raised when frontmatter file is not found"""
    pass

class FrontmatterManager:
    """
    Centralized frontmatter management system with schema validation,
    integrity checking, and automated field management.
    """
    
    def __init__(self, frontmatter_root: Optional[Path] = None):
        """Initialize frontmatter manager with root directory"""
        if frontmatter_root is None:
            # Auto-detect frontmatter root from current working directory
            cwd = Path.cwd()
            if (cwd / "frontmatter").exists():
                frontmatter_root = cwd / "frontmatter"
            else:
                # Fallback to project root detection
                project_root = self._find_project_root()
                frontmatter_root = project_root / "frontmatter"
        
        self.root = Path(frontmatter_root)
        self.materials_dir = self.root / "materials"
        self.schemas_dir = self.root / "schemas"
        
        # Ensure directories exist
        self.materials_dir.mkdir(parents=True, exist_ok=True)
        self.schemas_dir.mkdir(parents=True, exist_ok=True)
        
        # Load schema
        self._schema = self._load_schema()
        
        # Cache for loaded frontmatter
        self._cache = {}
        
        logger.info(f"FrontmatterManager initialized with root: {self.root}")
    
    def _find_project_root(self) -> Path:
        """Find project root by looking for key files"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "run.py").exists() or (current / "requirements.txt").exists():
                return current
            current = current.parent
        return Path.cwd()  # Fallback to current directory
    
    def _load_schema(self) -> Dict:
        """Load JSON schema for frontmatter validation"""
        schema_path = self.schemas_dir / "material-frontmatter.schema.json"
        if not schema_path.exists():
            logger.warning(f"Schema not found at {schema_path}, using minimal validation")
            return {"type": "object"}  # Minimal schema
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            return {"type": "object"}  # Fallback minimal schema
    
    @lru_cache(maxsize=128)
    def load_material(self, material_name: str, validate: bool = True) -> Dict:
        """
        Load and validate frontmatter for a specific material.
        
        Args:
            material_name: Name of the material (case insensitive)
            validate: Whether to perform schema validation
            
        Returns:
            Dictionary containing frontmatter data
            
        Raises:
            FrontmatterNotFoundError: If frontmatter file doesn't exist
            FrontmatterValidationError: If validation fails
        """
        # Normalize material name
        safe_name = material_name.lower().replace(' ', '-').replace('_', '-')
        
        # Try multiple possible file paths
        possible_paths = [
            self.materials_dir / f"{safe_name}.yaml",
            self.materials_dir / f"{safe_name}-laser-cleaning.md",
            self.materials_dir / f"{safe_name}.md",
            # Legacy path support during migration
            Path("frontmatter/materials") / f"{safe_name}-laser-cleaning.md"
        ]
        
        frontmatter_path = None
        for path in possible_paths:
            if path.exists():
                frontmatter_path = path
                break
        
        if not frontmatter_path:
            raise FrontmatterNotFoundError(
                f"Frontmatter not found for material '{material_name}'. "
                f"Searched paths: {[str(p) for p in possible_paths]}"
            )
        
        # Load and parse frontmatter
        try:
            frontmatter_data = self._parse_frontmatter_file(frontmatter_path)
        except Exception as e:
            raise FrontmatterValidationError(
                f"Failed to parse frontmatter for '{material_name}': {e}"
            )
        
        # Validate against schema
        if validate:
            try:
                jsonschema.validate(frontmatter_data, self._schema)
            except jsonschema.ValidationError as e:
                raise FrontmatterValidationError(
                    f"Schema validation failed for '{material_name}': {e.message}\\n"
                    f"Failed at path: {' -> '.join(str(p) for p in e.absolute_path)}"
                )
        
        # Cache the result
        self._cache[material_name.lower()] = frontmatter_data
        
        logger.debug(f"Successfully loaded frontmatter for {material_name}")
        return frontmatter_data
    
    def _parse_frontmatter_file(self, file_path: Path) -> Dict:
        """Parse a frontmatter file and extract YAML data"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Handle pure YAML files
        if file_path.suffix == '.yaml':
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML file: {e}")
        
        # Handle Markdown files with frontmatter
        if not content.startswith('---\\n'):
            raise ValueError("Invalid frontmatter format - must start with '---'")
        
        # Find the end of frontmatter
        lines = content.split('\\n')
        end_line = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_line = i
                break
        
        if end_line == -1:
            # Handle frontmatter-only files
            frontmatter_text = '\\n'.join(lines[1:])
        else:
            frontmatter_text = '\\n'.join(lines[1:end_line])
        
        try:
            return yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in frontmatter: {e}")
    
    def validate_material(self, material_name: str) -> Tuple[bool, List[str]]:
        """
        Validate a material's frontmatter and return validation results.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            self.load_material(material_name, validate=True)
            return True, []
        except (FrontmatterNotFoundError, FrontmatterValidationError) as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]

    def validate_material_data(self, material_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate material data against schema.
        
        Args:
            material_data: Dictionary containing material frontmatter data
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            jsonschema.validate(material_data, self._schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]
        except Exception as e:
            return False, [f"Unexpected validation error: {e}"]
    
    def list_materials(self) -> List[str]:
        """List all available materials"""
        materials = []
        
        # Check new location for YAML files
        if self.materials_dir.exists():
            for file_path in self.materials_dir.glob("*.yaml"):
                material_name = file_path.stem
                materials.append(material_name.replace('-', ' ').title())
        
        # Check legacy location during migration
        legacy_dir = Path("frontmatter/materials")
        if legacy_dir.exists():
            for file_path in legacy_dir.glob("*-laser-cleaning.md"):
                material_name = file_path.stem.replace('-laser-cleaning', '')
                material_title = material_name.replace('-', ' ').title()
                if material_title not in materials:
                    materials.append(material_title)
        
        return sorted(materials)
    
    def validate_all_materials(self) -> Dict[str, Dict]:
        """
        Validate all materials and return comprehensive report.
        
        Returns:
            Dictionary with validation results for each material
        """
        results = {}
        materials = self.list_materials()
        
        for material in materials:
            is_valid, errors = self.validate_material(material)
            results[material] = {
                'valid': is_valid,
                'errors': errors,
                'validated_at': datetime.now().isoformat()
            }
        
        return results
    
    def get_required_fields(self) -> List[str]:
        """Get list of required fields from schema"""
        if 'required' in self._schema:
            return self._schema['required']
        return []
    
    def check_field_completeness(self, material_name: str) -> Dict[str, Any]:
        """
        Check field completeness for a material.
        
        Returns:
            Dictionary with completeness analysis
        """
        try:
            data = self.load_material(material_name, validate=False)
            required_fields = self.get_required_fields()
            
            missing_fields = [field for field in required_fields if field not in data]
            present_fields = [field for field in required_fields if field in data]
            
            return {
                'material': material_name,
                'total_required': len(required_fields),
                'present_count': len(present_fields),
                'missing_count': len(missing_fields),
                'missing_fields': missing_fields,
                'completeness_percent': (len(present_fields) / len(required_fields)) * 100 if required_fields else 100
            }
        except Exception as e:
            return {
                'material': material_name,
                'error': str(e),
                'completeness_percent': 0
            }
    
    def get_integrity_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive integrity report for all frontmatter.
        
        Returns:
            Dictionary with integrity analysis
        """
        materials = self.list_materials()
        
        report = {
            'total_materials': len(materials),
            'validation_results': {},
            'completeness_analysis': {},
            'generated_at': datetime.now().isoformat(),
            'schema_path': str(self.schemas_dir / "material-frontmatter.schema.json")
        }
        
        valid_count = 0
        for material in materials:
            # Validation check
            is_valid, errors = self.validate_material(material)
            report['validation_results'][material] = {
                'valid': is_valid,
                'errors': errors
            }
            if is_valid:
                valid_count += 1
            
            # Completeness check
            completeness = self.check_field_completeness(material)
            report['completeness_analysis'][material] = completeness
        
        report['summary'] = {
            'valid_materials': valid_count,
            'invalid_materials': len(materials) - valid_count,
            'validation_rate': (valid_count / len(materials)) * 100 if materials else 0
        }
        
        return report
    
    def clear_cache(self):
        """Clear the frontmatter cache"""
        self._cache.clear()
        # Also clear the LRU cache
        self.load_material.cache_clear()
        logger.info("Frontmatter cache cleared")

# Global instance for easy import
frontmatter_manager = FrontmatterManager()

# Convenience functions
def load_material_frontmatter(material_name: str, validate: bool = True) -> Dict:
    """Convenience function to load material frontmatter"""
    return frontmatter_manager.load_material(material_name, validate)

def validate_material_frontmatter(material_name: str) -> Tuple[bool, List[str]]:
    """Convenience function to validate material frontmatter"""
    return frontmatter_manager.validate_material(material_name)

def list_available_materials() -> List[str]:
    """Convenience function to list available materials"""
    return frontmatter_manager.list_materials()
