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
        self.schema_path = self.schemas_dir / "material-frontmatter.schema.json"
        
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
    
    def validate_material(self, material_name: str, raise_on_error: bool = False):
        """
        Validate a material's frontmatter and return validation results.
        
        Args:
            material_name: Name of the material to validate
            raise_on_error: If True, raise exception on validation errors
            
        Returns:
            Boolean for simple calls, Tuple of (is_valid, list_of_errors) for detailed calls
        """
        # Check if schema exists - if not, validation should fail
        if not self.schema_path.exists():
            error_msg = f"Schema not found at {self.schema_path}"
            if raise_on_error:
                raise FrontmatterValidationError(error_msg)
            # Check if we're being called from get_integrity_report (needs tuple)
            import inspect
            frame = inspect.currentframe().f_back
            if frame and 'get_integrity_report' in frame.f_code.co_name:
                return False, [error_msg]
            return False
            
        try:
            self.load_material(material_name, validate=True)
            # Check if we're being called from get_integrity_report (needs tuple)
            import inspect
            frame = inspect.currentframe().f_back
            if frame and 'get_integrity_report' in frame.f_code.co_name:
                return True, []
            return True
        except (FrontmatterNotFoundError, FrontmatterValidationError) as e:
            if raise_on_error:
                raise e
            # Check if we're being called from get_integrity_report (needs tuple)
            import inspect
            frame = inspect.currentframe().f_back
            if frame and 'get_integrity_report' in frame.f_code.co_name:
                return False, [str(e)]
            return False
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            if raise_on_error:
                raise FrontmatterValidationError(error_msg)
            # Check if we're being called from get_integrity_report (needs tuple)
            import inspect
            frame = inspect.currentframe().f_back
            if frame and 'get_integrity_report' in frame.f_code.co_name:
                return False, [error_msg]
            return False

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
                material_name = file_path.stem  # Keep original filename format
                materials.append(material_name)
        
        # Check legacy location during migration
        legacy_dir = Path("frontmatter/materials")
        if legacy_dir.exists():
            for file_path in legacy_dir.glob("*-laser-cleaning.md"):
                material_name = file_path.stem.replace('-laser-cleaning', '')
                if material_name not in materials:
                    materials.append(material_name)
        
        # Also check current content/components/frontmatter for backward compatibility
        content_frontmatter_dir = Path.cwd() / "content" / "components" / "frontmatter"
        if content_frontmatter_dir.exists():
            for file_path in content_frontmatter_dir.glob("*-laser-cleaning.md"):
                material_name = file_path.stem.replace('-laser-cleaning', '')
                if material_name not in materials:
                    materials.append(material_name)
        
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
        
        valid_count = 0
        validation_results = {}
        completeness_analysis = {}
        errors = []
        
        for material in materials:
            # Validation check (material name is already in file format)
            is_valid, error_messages = self.validate_material(material)
            validation_results[material] = {
                'valid': is_valid,
                'errors': error_messages
            }
            if is_valid:
                valid_count += 1
            else:
                # Add to errors list for legacy test compatibility
                for error_msg in error_messages:
                    errors.append({
                        'file': material,  # Material name is already in file format
                        'error': error_msg
                    })
            
            # Completeness check
            completeness_analysis[material] = self.check_field_completeness(material)
        
        report = {
            'total_files': len(materials),
            'total_materials': len(materials),
            'valid_count': valid_count,
            'invalid_count': len(materials) - valid_count,
            'errors': errors,  # Legacy field for test compatibility
            'validation_results': validation_results,
            'completeness_analysis': completeness_analysis,
            'generated_at': datetime.now().isoformat(),
            'schema_path': str(self.schemas_dir / "material-frontmatter.schema.json"),
            'summary': {
                'valid_materials': valid_count,
                'invalid_materials': len(materials) - valid_count,
                'validation_rate': (valid_count / len(materials)) * 100 if materials else 0
            }
        }
        
        return report
    
    def clear_cache(self):
        """Clear the LRU cache for material loading"""
        self.load_material.cache_clear()
        logger.info("FrontmatterManager cache cleared")

    def material_exists(self, material_name: str) -> bool:
        """Check if a material frontmatter file exists"""
        # Normalize material name (remove spaces, lowercase, add hyphens)
        normalized_name = material_name.lower().replace(' ', '-').replace('_', '-')
        material_file = self.materials_dir / f"{normalized_name}.yaml"
        
        # Also check old location for backward compatibility
        old_location = Path.cwd() / "content" / "components" / "frontmatter" / f"{normalized_name}-laser-cleaning.md"
        
        return material_file.exists() or old_location.exists()

    def get_material_path(self, material_name: str) -> Path:
        """Get the path to a material's frontmatter file"""
        # Normalize material name (remove spaces, lowercase, add hyphens)
        normalized_name = material_name.lower().replace(' ', '-').replace('_', '-')
        material_file = self.materials_dir / f"{normalized_name}.yaml"
        
        # Check if file exists in new location
        if material_file.exists():
            return material_file
            
        # Check old location for backward compatibility
        old_location = Path.cwd() / "content" / "components" / "frontmatter" / f"{normalized_name}-laser-cleaning.md"
        if old_location.exists():
            return old_location
            
        # Return expected new location even if it doesn't exist yet
        return material_file


# Global instance for easy access
frontmatter_manager = FrontmatterManager()

# Convenience functions that use the global instance
def load_material_frontmatter(material_name: str, validate: bool = True) -> Dict:
    """Load material frontmatter using the global manager instance"""
    return frontmatter_manager.load_material(material_name, validate)

def validate_material_frontmatter(material_name: str) -> Tuple[bool, List[str]]:
    """Validate material frontmatter using the global manager instance"""
    return frontmatter_manager.validate_material(material_name)

def list_available_materials() -> List[str]:
    """List available materials using the global manager instance"""
    return frontmatter_manager.list_materials()
