"""
Contamination Lookup Helpers (Hybrid Approach)

Fast O(1) lookups in both directions:
- get_materials_for_contaminant(pattern_id) -> List[str]
- get_contaminants_for_material(material_name) -> List[str]

Usage:
    from shared.helpers.contamination_lookup import ContaminationLookup
    
    lookup = ContaminationLookup()
    
    # What materials can have rust?
    materials = lookup.get_materials_for_contaminant('rust-oxidation')
    # → ['Steel', 'Iron', 'Cast Iron']
    
    # What contaminants affect Aluminum?
    contaminants = lookup.get_contaminants_for_material('Aluminum')
    # → ['industrial-oil', 'aluminum-oxidation', 'uv-chalking', ...]
    
    # Is combination valid?
    if lookup.is_valid_combination('Aluminum', 'rust-oxidation'):
        print("Can clean rust from aluminum")
    
    # Get full pattern data
    pattern = lookup.get_pattern('rust-oxidation')
    # → Full contamination pattern with laser_parameters, etc.

Author: AI Assistant
Date: November 26, 2025
"""

import yaml
from pathlib import Path
from typing import List, Optional, Dict


class ContaminationLookup:
    """
    Fast bidirectional contamination-material lookup.
    
    Uses hybrid approach:
    - Contaminants.yaml: Source of truth (contamination → materials)
    - Materials.yaml: Cached reverse index (material → contaminations)
    """
    
    def __init__(self, contaminants_file: Optional[Path] = None, materials_file: Optional[Path] = None):
        """
        Initialize lookup helper.
        
        Args:
            contaminants_file: Path to Contaminants.yaml (auto-detected if None)
            materials_file: Path to Materials.yaml (auto-detected if None)
        """
        # Auto-detect file paths
        if contaminants_file is None:
            project_root = Path(__file__).parent.parent.parent
            contaminants_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
        
        if materials_file is None:
            project_root = Path(__file__).parent.parent.parent
            materials_file = project_root / 'data' / 'materials' / 'Materials.yaml'
        
        self.contaminants_file = contaminants_file
        self.materials_file = materials_file
        
        # Load data (cached)
        self._contaminants_data = None
        self._materials_data = None
    
    @property
    def contaminants_data(self) -> dict:
        """Lazy load Contaminants.yaml (cached)."""
        if self._contaminants_data is None:
            with open(self.contaminants_file, 'r', encoding='utf-8') as f:
                self._contaminants_data = yaml.safe_load(f)
        return self._contaminants_data
    
    @property
    def materials_data(self) -> dict:
        """Lazy load Materials.yaml (cached)."""
        if self._materials_data is None:
            with open(self.materials_file, 'r', encoding='utf-8') as f:
                self._materials_data = yaml.safe_load(f)
        return self._materials_data
    
    def get_materials_for_contaminant(self, pattern_id: str) -> List[str]:
        """
        Get list of materials that can have this contamination.
        
        Fast O(1) lookup from Contaminants.yaml.
        
        Args:
            pattern_id: Contamination pattern ID (e.g., 'rust-oxidation')
        
        Returns:
            List of material names, or empty list if pattern not found
        
        Example:
            >>> lookup.get_materials_for_contaminant('rust-oxidation')
            ['Steel', 'Iron', 'Cast Iron']
        """
        patterns = self.contaminants_data.get('contamination_patterns', {})
        pattern = patterns.get(pattern_id, {})
        return pattern.get('valid_materials', [])
    
    def get_contaminants_for_material(self, material_name: str) -> List[str]:
        """
        Get list of contaminations that can occur on this material.
        
        Fast O(1) lookup from cached common_contaminants field in Materials.yaml.
        
        Args:
            material_name: Material name (e.g., 'Aluminum')
        
        Returns:
            List of contamination pattern IDs, or empty list if material not found
        
        Example:
            >>> lookup.get_contaminants_for_material('Aluminum')
            ['industrial-oil', 'aluminum-oxidation', 'uv-chalking', ...]
        """
        materials = self.materials_data.get('materials', {})
        material = materials.get(material_name, {})
        return material.get('common_contaminants', [])
    
    def is_valid_combination(self, material_name: str, pattern_id: str) -> bool:
        """
        Check if contamination can occur on material.
        
        Args:
            material_name: Material name (e.g., 'Aluminum')
            pattern_id: Contamination pattern ID (e.g., 'rust-oxidation')
        
        Returns:
            True if combination is valid, False otherwise
        
        Example:
            >>> lookup.is_valid_combination('Aluminum', 'rust-oxidation')
            False  # Aluminum doesn't rust
            
            >>> lookup.is_valid_combination('Steel', 'rust-oxidation')
            True  # Steel can rust
        """
        valid_materials = self.get_materials_for_contaminant(pattern_id)
        return material_name in valid_materials
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict]:
        """
        Get full contamination pattern data.
        
        Args:
            pattern_id: Contamination pattern ID (e.g., 'rust-oxidation')
        
        Returns:
            Full pattern dict with laser_parameters, visual_appearance, etc.
            None if pattern not found
        
        Example:
            >>> pattern = lookup.get_pattern('rust-oxidation')
            >>> pattern['laser_parameters']['fluence_range']
            {'min_j_cm2': 0.8, 'max_j_cm2': 1.4, 'recommended_j_cm2': 1.1}
        """
        patterns = self.contaminants_data.get('contamination_patterns', {})
        return patterns.get(pattern_id)
    
    def get_material(self, material_name: str) -> Optional[Dict]:
        """
        Get full material data.
        
        Args:
            material_name: Material name (e.g., 'Aluminum')
        
        Returns:
            Full material dict with properties, common_contaminants, etc.
            None if material not found
        """
        materials = self.materials_data.get('materials', {})
        return materials.get(material_name)
    
    def get_pattern_name(self, pattern_id: str) -> Optional[str]:
        """
        Get human-readable pattern name.
        
        Args:
            pattern_id: Contamination pattern ID (e.g., 'rust-oxidation')
        
        Returns:
            Pattern name (e.g., 'Rust / Iron Oxide Formation')
            None if pattern not found
        """
        pattern = self.get_pattern(pattern_id)
        return pattern.get('name') if pattern else None
    
    def search_patterns(self, query: str) -> List[Dict]:
        """
        Search contamination patterns by name or ID.
        
        Args:
            query: Search string (case-insensitive)
        
        Returns:
            List of matching patterns with id, name, description
        
        Example:
            >>> results = lookup.search_patterns('rust')
            >>> for r in results:
            ...     print(f"{r['id']}: {r['name']}")
            rust-oxidation: Rust / Iron Oxide Formation
        """
        patterns = self.contaminants_data.get('contamination_patterns', {})
        query_lower = query.lower()
        
        results = []
        for pattern_id, pattern_data in patterns.items():
            name = pattern_data.get('name', '').lower()
            description = pattern_data.get('description', '').lower()
            
            if (query_lower in pattern_id.lower() or 
                query_lower in name or 
                query_lower in description):
                
                results.append({
                    'id': pattern_id,
                    'name': pattern_data.get('name'),
                    'description': pattern_data.get('description')
                })
        
        return results
    
    def get_all_patterns(self) -> List[str]:
        """Get list of all contamination pattern IDs."""
        patterns = self.contaminants_data.get('contamination_patterns', {})
        return list(patterns.keys())
    
    def get_all_materials(self) -> List[str]:
        """Get list of all material names."""
        materials = self.materials_data.get('materials', {})
        return list(materials.keys())
    
    def get_statistics(self) -> Dict:
        """
        Get contamination-material relationship statistics.
        
        Returns:
            Dict with counts and averages
        """
        patterns = self.contaminants_data.get('contamination_patterns', {})
        materials = self.materials_data.get('materials', {})
        
        total_patterns = len(patterns)
        total_materials = len(materials)
        
        # Count materials with contaminants
        materials_with_contaminants = sum(
            1 for m in materials.values() 
            if m.get('common_contaminants')
        )
        
        # Count total associations
        total_associations = sum(
            len(m.get('common_contaminants', [])) 
            for m in materials.values()
        )
        
        # Average materials per pattern
        materials_per_pattern = sum(
            len(p.get('valid_materials', [])) 
            for p in patterns.values()
        ) / total_patterns if total_patterns else 0
        
        # Average contaminants per material
        contaminants_per_material = (
            total_associations / materials_with_contaminants 
            if materials_with_contaminants else 0
        )
        
        return {
            'total_patterns': total_patterns,
            'total_materials': total_materials,
            'materials_with_contaminants': materials_with_contaminants,
            'total_associations': total_associations,
            'avg_materials_per_pattern': round(materials_per_pattern, 1),
            'avg_contaminants_per_material': round(contaminants_per_material, 1)
        }


# Convenience functions for quick imports
_global_lookup = None

def get_lookup() -> ContaminationLookup:
    """Get singleton ContaminationLookup instance."""
    global _global_lookup
    if _global_lookup is None:
        _global_lookup = ContaminationLookup()
    return _global_lookup


def get_materials_for_contaminant(pattern_id: str) -> List[str]:
    """Convenience function: Get materials for contamination pattern."""
    return get_lookup().get_materials_for_contaminant(pattern_id)


def get_contaminants_for_material(material_name: str) -> List[str]:
    """Convenience function: Get contaminants for material."""
    return get_lookup().get_contaminants_for_material(material_name)


def is_valid_combination(material_name: str, pattern_id: str) -> bool:
    """Convenience function: Check if material-contaminant combo is valid."""
    return get_lookup().is_valid_combination(material_name, pattern_id)


# Example usage
if __name__ == '__main__':
    """Demo the lookup helper."""
    print('🔍 Contamination Lookup Helper Demo')
    print('=' * 80)
    print()
    
    lookup = ContaminationLookup()
    
    # Example 1: What materials can have rust?
    print('1️⃣  What materials can have rust?')
    materials = lookup.get_materials_for_contaminant('rust-oxidation')
    print(f'   rust-oxidation affects: {", ".join(materials[:5])}')
    if len(materials) > 5:
        print(f'   ... and {len(materials) - 5} more')
    print()
    
    # Example 2: What contaminants affect Aluminum?
    print('2️⃣  What contaminants affect Aluminum?')
    contaminants = lookup.get_contaminants_for_material('Aluminum')
    print(f'   Aluminum can have: {len(contaminants)} different contaminants')
    for c in contaminants[:5]:
        name = lookup.get_pattern_name(c)
        print(f'      • {c}: {name}')
    if len(contaminants) > 5:
        print(f'      ... and {len(contaminants) - 5} more')
    print()
    
    # Example 3: Validate combinations
    print('3️⃣  Is combination valid?')
    print(f'   Aluminum + rust-oxidation: {lookup.is_valid_combination("Aluminum", "rust-oxidation")} ❌')
    print(f'   Steel + rust-oxidation: {lookup.is_valid_combination("Steel", "rust-oxidation")} ✅')
    print()
    
    # Example 4: Statistics
    print('4️⃣  Statistics:')
    stats = lookup.get_statistics()
    print(f'   Total patterns: {stats["total_patterns"]}')
    print(f'   Total materials: {stats["total_materials"]}')
    print(f'   Materials with contaminants: {stats["materials_with_contaminants"]}')
    print(f'   Avg contaminants per material: {stats["avg_contaminants_per_material"]}')
    print()
