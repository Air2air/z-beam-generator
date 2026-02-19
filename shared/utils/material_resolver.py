"""
Smart Material Resolution Utility

Automatically resolves user-friendly material names to correct YAML keys.
Supports multiple input formats and provides helpful error messages.

Created: January 13, 2026
Purpose: Simplify command interface by auto-resolving material names
"""

import difflib
from pathlib import Path

import yaml


class MaterialResolver:
    """Resolves user-friendly material names to correct YAML keys"""
    
    def __init__(self, materials_yaml_path: str | None = None):
        if materials_yaml_path is None:
            materials_yaml_path = "data/materials/Materials.yaml"
        
        self.materials_yaml_path = Path(materials_yaml_path)
        self._material_mappings = None
        
    def _load_material_mappings(self) -> dict[str, dict[str, str]]:
        """Load and cache material mappings from Materials.yaml"""
        if self._material_mappings is not None:
            return self._material_mappings
            
        if not self.materials_yaml_path.exists():
            raise FileNotFoundError(f"Materials.yaml not found: {self.materials_yaml_path}")
            
        with open(self.materials_yaml_path) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise RuntimeError(
                f"Invalid Materials.yaml format in {self.materials_yaml_path}: expected top-level dictionary"
            )
        if 'materials' not in data:
            raise RuntimeError(
                f"Invalid Materials.yaml format in {self.materials_yaml_path}: missing required 'materials' key"
            )

        materials = data['materials']
        if not isinstance(materials, dict):
            raise RuntimeError(
                f"Invalid Materials.yaml format in {self.materials_yaml_path}: 'materials' must be a dictionary"
            )

        mappings = {}
        
        for key, material_data in materials.items():
            if not isinstance(material_data, dict):
                raise RuntimeError(
                    f"Invalid material entry for key '{key}': expected dictionary"
                )

            required_fields = ['name', 'displayName', 'category', 'subcategory']
            missing_fields = [field for field in required_fields if field not in material_data]
            if missing_fields:
                raise RuntimeError(
                    f"Invalid material entry '{key}': missing required fields {missing_fields}"
                )

            name = material_data['name']
            display_name = material_data['displayName']
            category = material_data['category']
            subcategory = material_data['subcategory']

            if not isinstance(name, str) or not name.strip():
                raise RuntimeError(
                    f"Invalid material entry '{key}': 'name' must be a non-empty string"
                )
            if not isinstance(display_name, str) or not display_name.strip():
                raise RuntimeError(
                    f"Invalid material entry '{key}': 'displayName' must be a non-empty string"
                )
            if not isinstance(category, str) or not category.strip():
                raise RuntimeError(
                    f"Invalid material entry '{key}': 'category' must be a non-empty string"
                )
            if not isinstance(subcategory, str) or not subcategory.strip():
                raise RuntimeError(
                    f"Invalid material entry '{key}': 'subcategory' must be a non-empty string"
                )
            
            # Create multiple mapping entries
            mappings[key] = {
                'key': key,
                'name': name,
                'display_name': display_name,
                'category': category,
                'subcategory': subcategory
            }
            
        self._material_mappings = mappings
        return mappings
    
    def resolve_material(self, input_name: str) -> tuple[str | None, str | None]:
        """
        Resolve material name to correct YAML key.
        
        Returns:
            Tuple of (resolved_key, error_message)
            - If successful: (key, None)
            - If failed: (None, error_message)
        """
        mappings = self._load_material_mappings()
        input_lower = input_name.lower().strip()
        
        # Strategy 1: Exact key match
        if input_name in mappings:
            return input_name, None
            
        # Strategy 2: Exact name match (case-insensitive)
        for key, data in mappings.items():
            if data['name'].lower() == input_lower:
                return key, None
                
        # Strategy 3: Display name match
        for key, data in mappings.items():
            if data['display_name'].lower() == input_lower:
                return key, None
                
        # Strategy 4: Smart suffix addition
        # Try adding "-laser-cleaning" suffix
        candidate_key = f"{input_lower.replace(' ', '-')}-laser-cleaning"
        if candidate_key in mappings:
            return candidate_key, None
            
        # Strategy 5: Partial matching for common abbreviations
        partial_matches = []
        for key, data in mappings.items():
            if input_lower in data['name'].lower() or input_lower in key.lower():
                partial_matches.append((key, data))
                
        if len(partial_matches) == 1:
            return partial_matches[0][0], None
        elif len(partial_matches) > 1:
            # Multiple matches - return error with options
            options = [f"  - {key} ({data['name']})" for key, data in partial_matches[:5]]
            return None, f"Multiple materials match '{input_name}':\n" + "\n".join(options)
            
        # Strategy 6: Fuzzy matching with suggestions
        all_names = []
        key_to_name = {}
        for key, data in mappings.items():
            all_names.extend([data['name'], data['display_name']])
            key_to_name[data['name']] = key
            key_to_name[data['display_name']] = key
            
        close_matches = difflib.get_close_matches(input_name, all_names, n=3, cutoff=0.6)
        
        if close_matches:
            suggestions = []
            for match in close_matches:
                if match in key_to_name:
                    key = key_to_name[match]
                    suggestions.append(f"  - {key} ({match})")
                    
            error_msg = f"Material '{input_name}' not found. Did you mean:\n" + "\n".join(suggestions)
            error_msg += f"\n\nTry: python3 run.py --generate '{close_matches[0]}' --field pageDescription"
            return None, error_msg
            
        # No matches found
        available_count = len(mappings)
        error_msg = f"Material '{input_name}' not found in {available_count} available materials.\n"
        error_msg += "Use --list-materials to see all options."
        return None, error_msg
        
    def list_materials(self, category_filter: str | None = None) -> list[dict[str, str]]:
        """List all available materials, optionally filtered by category"""
        mappings = self._load_material_mappings()
        
        materials = []
        for key, data in mappings.items():
            if category_filter and data['category'] != category_filter:
                continue
                
            materials.append({
                'key': key,
                'name': data['name'],
                'category': data['category'],
                'subcategory': data['subcategory']
            })
            
        return sorted(materials, key=lambda x: x['name'])
        
    def suggest_command(self, resolved_key: str, field: str = "pageDescription") -> str:
        """Generate suggested command for resolved material"""
        return f"python3 run.py --generate '{resolved_key}' --field {field}"


# Global instance for easy access
material_resolver = MaterialResolver()
