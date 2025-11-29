#!/usr/bin/env python3
"""
Contamination Pattern Selector

Selects contamination patterns from Contaminants.yaml based on material compatibility.
NO API calls - uses pre-populated data only.

This is the simplified, single-source-of-truth approach:
- Reads patterns from Contaminants.yaml
- Filters by valid_materials field
- Returns appearance data (16 fields when available, base data otherwise)
- Zero runtime API calls for contamination data

Author: AI Assistant
Date: November 29, 2025
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


class ContaminationPatternSelector:
    """
    Select contamination patterns from Contaminants.yaml for image generation.
    
    ARCHITECTURE:
    - Single source of truth: Contaminants.yaml
    - No API calls for contamination data
    - Pattern selection based on valid_materials field
    - Appearance data from appearance_on_materials or base pattern data
    
    This replaces the complex CategoryContaminationResearcher + fallback architecture
    with a simple, deterministic, zero-API-call approach.
    """
    
    # Common contamination patterns by category (for intelligent selection)
    # These are the most visually interesting patterns per material type
    CATEGORY_PRIORITIES = {
        'metal': ['rust-oxidation', 'industrial-oil', 'environmental-dust', 'welding-spatter', 'scale-buildup'],
        'wood': ['wood-rot', 'mold-mildew', 'environmental-dust', 'algae-growth', 'uv-chalking'],
        'polymer': ['uv-chalking', 'environmental-dust', 'industrial-oil', 'chemical-stains', 'adhesive-residue'],
        'glass': ['environmental-dust', 'hard-water-deposits', 'chemical-stains', 'fingerprints', 'adhesive-residue'],
        'ceramic': ['environmental-dust', 'hard-water-deposits', 'mold-mildew', 'efflorescence', 'algae-growth'],
        'stone': ['environmental-dust', 'algae-growth', 'mold-mildew', 'efflorescence', 'chemical-stains'],
        'composite': ['uv-chalking', 'environmental-dust', 'industrial-oil', 'chemical-stains', 'mold-mildew'],
    }
    
    # Material to category mapping (simplified)
    MATERIAL_CATEGORIES = {
        # Metals
        'aluminum': 'metal', 'steel': 'metal', 'stainless steel': 'metal',
        'iron': 'metal', 'cast iron': 'metal', 'copper': 'metal',
        'brass': 'metal', 'bronze': 'metal', 'zinc': 'metal',
        'titanium': 'metal', 'nickel': 'metal', 'lead': 'metal',
        'tin': 'metal', 'cobalt': 'metal', 'chromium': 'metal',
        'tungsten': 'metal', 'magnesium': 'metal', 'gold': 'metal',
        'silver': 'metal', 'platinum': 'metal',
        # Woods
        'oak': 'wood', 'pine': 'wood', 'cedar': 'wood', 'maple': 'wood',
        'walnut': 'wood', 'cherry': 'wood', 'mahogany': 'wood', 'teak': 'wood',
        'birch': 'wood', 'ash': 'wood', 'beech': 'wood', 'plywood': 'wood',
        'mdf': 'wood', 'bamboo': 'wood',
        # Polymers
        'abs': 'polymer', 'pvc': 'polymer', 'acrylic': 'polymer',
        'polycarbonate': 'polymer', 'polyethylene': 'polymer', 'polypropylene': 'polymer',
        'nylon': 'polymer', 'ptfe': 'polymer', 'peek': 'polymer',
        'hdpe': 'polymer', 'ldpe': 'polymer', 'pet': 'polymer',
        # Glass
        'glass': 'glass', 'borosilicate glass': 'glass', 'float glass': 'glass',
        'crown glass': 'glass', 'aluminosilicate glass': 'glass', 'fused silica': 'glass',
        # Ceramics
        'porcelain': 'ceramic', 'ceramic': 'ceramic', 'terracotta': 'ceramic',
        'stoneware': 'ceramic', 'alumina': 'ceramic', 'zirconia': 'ceramic',
        # Stone
        'granite': 'stone', 'marble': 'stone', 'limestone': 'stone',
        'sandstone': 'stone', 'slate': 'stone', 'travertine': 'stone',
        'quartzite': 'stone', 'basalt': 'stone',
        # Composites
        'carbon fiber': 'composite', 'fiberglass': 'composite', 'pcb': 'composite',
    }
    
    def __init__(self, contaminants_file: Optional[Path] = None):
        """
        Initialize selector with path to Contaminants.yaml.
        
        Args:
            contaminants_file: Optional path to Contaminants.yaml
        """
        self.contaminants_file = contaminants_file or PROJECT_ROOT / 'data' / 'contaminants' / 'Contaminants.yaml'
        self._data: Optional[Dict] = None
        
        if not self.contaminants_file.exists():
            raise FileNotFoundError(f"Contaminants.yaml not found at: {self.contaminants_file}")
        
        logger.info("✅ ContaminationPatternSelector initialized (zero API calls)")
    
    def _load_data(self) -> Dict:
        """Load contaminants data (lazy loading with caching)."""
        if self._data is None:
            with open(self.contaminants_file, 'r', encoding='utf-8') as f:
                self._data = yaml.safe_load(f)
            logger.debug(f"📦 Loaded {len(self._data.get('contamination_patterns', {}))} patterns from YAML")
        return self._data
    
    def get_material_category(self, material_name: str) -> str:
        """Get the category for a material (for pattern prioritization)."""
        material_lower = material_name.lower()
        
        # Direct lookup
        if material_lower in self.MATERIAL_CATEGORIES:
            return self.MATERIAL_CATEGORIES[material_lower]
        
        # Fuzzy matching
        if any(m in material_lower for m in ['steel', 'iron', 'metal']):
            return 'metal'
        if any(m in material_lower for m in ['wood', 'oak', 'pine', 'cedar', 'maple']):
            return 'wood'
        if any(m in material_lower for m in ['plastic', 'polymer', 'vinyl', 'acrylic']):
            return 'polymer'
        if 'glass' in material_lower:
            return 'glass'
        if any(m in material_lower for m in ['ceramic', 'porcelain', 'tile']):
            return 'ceramic'
        if any(m in material_lower for m in ['stone', 'granite', 'marble']):
            return 'stone'
        if any(m in material_lower for m in ['fiber', 'composite']):
            return 'composite'
        
        return 'metal'  # Default fallback
    
    def get_valid_patterns_for_material(self, material_name: str) -> List[str]:
        """
        Get list of pattern IDs that are valid for a material.
        
        Uses the valid_materials field in each pattern to determine compatibility.
        
        Args:
            material_name: Material name (e.g., "Aluminum", "Oak")
            
        Returns:
            List of pattern IDs valid for this material
        """
        data = self._load_data()
        patterns = data.get('contamination_patterns', {})
        material_lower = material_name.lower()
        
        valid_pattern_ids = []
        for pattern_id, pattern in patterns.items():
            valid_materials = pattern.get('valid_materials', [])
            # Check if material is in valid_materials (case-insensitive)
            if any(material_lower == vm.lower() for vm in valid_materials):
                valid_pattern_ids.append(pattern_id)
        
        return valid_pattern_ids
    
    def select_patterns(
        self,
        material_name: str,
        num_patterns: int = 3,
        prefer_with_appearance: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Select contamination patterns for a material.
        
        Selection priority:
        1. Patterns with material-specific appearance data
        2. Category-prioritized patterns (most visually interesting)
        3. Any valid patterns
        
        Args:
            material_name: Material name
            num_patterns: Number of patterns to select (default: 3)
            prefer_with_appearance: Prioritize patterns with appearance_on_materials data
            
        Returns:
            List of pattern data dictionaries ready for image generation
        """
        data = self._load_data()
        patterns = data.get('contamination_patterns', {})
        
        # Get valid patterns for this material
        valid_ids = self.get_valid_patterns_for_material(material_name)
        if not valid_ids:
            logger.warning(f"No valid contamination patterns found for {material_name}")
            return []
        
        # Get material category for prioritization
        category = self.get_material_category(material_name)
        priority_patterns = self.CATEGORY_PRIORITIES.get(category, [])
        
        # Score patterns for selection
        scored_patterns = []
        for pattern_id in valid_ids:
            pattern = patterns.get(pattern_id, {})
            score = 0
            
            # Bonus for having material-specific appearance data
            if prefer_with_appearance:
                appearance = self._get_appearance(pattern, material_name)
                if appearance and 'color_variations' in appearance:
                    score += 100  # Strong preference for rich data
            
            # Bonus for being in category priorities
            if pattern_id in priority_patterns:
                priority_rank = len(priority_patterns) - priority_patterns.index(pattern_id)
                score += priority_rank * 10
            
            scored_patterns.append((score, pattern_id, pattern))
        
        # Sort by score (highest first) and select top N
        scored_patterns.sort(reverse=True, key=lambda x: x[0])
        selected = scored_patterns[:num_patterns]
        
        # Build result dictionaries
        results = []
        for score, pattern_id, pattern in selected:
            result = self._build_pattern_result(pattern_id, pattern, material_name)
            if result:
                results.append(result)
        
        logger.info(f"📋 Selected {len(results)} patterns for {material_name}: {[r['pattern_id'] for r in results]}")
        return results
    
    def _get_appearance(self, pattern: Dict, material_name: str) -> Optional[Dict]:
        """
        Get appearance data for material, with category-level fallback.
        
        Priority:
        1. Material-specific appearance (e.g., appearance_on_materials['aluminum'])
        2. Category-level appearance (e.g., appearance_on_categories['metal'])
        3. None (use base pattern data)
        """
        visual = pattern.get('visual_characteristics', {})
        
        # Try material-specific first
        materials = visual.get('appearance_on_materials', {})
        material_key = material_name.lower().replace(' ', '-')
        for key, data in materials.items():
            if key.lower().replace(' ', '-') == material_key or key.lower() == material_name.lower():
                logger.debug(f"✅ Found material-specific appearance for {material_name}")
                return data
        
        # Fallback to category-level
        categories = visual.get('appearance_on_categories', {})
        material_category = self.get_material_category(material_name)
        if material_category and material_category in categories:
            logger.debug(f"📁 Using category-level appearance ({material_category}) for {material_name}")
            return categories[material_category]
        
        return None
    
    def _build_pattern_result(
        self,
        pattern_id: str,
        pattern: Dict,
        material_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Build pattern result dictionary for image generation.
        
        Uses material-specific appearance if available, otherwise uses base pattern data.
        """
        if not pattern:
            return None
        
        # Get material-specific appearance (16-field rich data)
        appearance = self._get_appearance(pattern, material_name)
        
        # Build visual characteristics
        if appearance:
            # Rich material-specific data available
            visual_chars = {
                'color_range': self._extract_color_summary(appearance.get('color_variations', [])),
                'texture_detail': self._extract_texture_summary(appearance.get('texture_details', '')),
                # Include full rich data
                'description': appearance.get('description', ''),
                'color_variations': appearance.get('color_variations', []),
                'texture_details': appearance.get('texture_details', ''),
                'common_patterns': appearance.get('common_patterns', ''),
                'aged_appearance': appearance.get('aged_appearance', ''),
                'lighting_effects': appearance.get('lighting_effects', ''),
                'thickness_range': appearance.get('thickness_range', ''),
                # Distribution physics
                'distribution_patterns': appearance.get('distribution_patterns', ''),
                'gravity_influence': appearance.get('gravity_influence', ''),
                'geometry_effects': appearance.get('geometry_effects', ''),
                'edge_center_behavior': appearance.get('edge_center_behavior', ''),
                'coverage_ranges': appearance.get('coverage_ranges', ''),
                'buildup_progression': appearance.get('buildup_progression', ''),
            }
            has_rich_data = True
        else:
            # Fallback to base pattern description
            visual_chars = {
                'color_range': 'varied',
                'texture_detail': pattern.get('description', '')[:100],
                'description': pattern.get('description', ''),
            }
            has_rich_data = False
        
        return {
            'pattern_id': pattern_id,
            'pattern_name': pattern.get('name', pattern_id),
            'visual_characteristics': visual_chars,
            'has_rich_appearance_data': has_rich_data,
            'category': pattern.get('category', 'contamination'),
        }
    
    def _extract_color_summary(self, color_variations: Any) -> str:
        """Extract concise color summary from color_variations field."""
        if not color_variations:
            return 'varied'
        
        if isinstance(color_variations, list):
            # Extract color names from entries like "#F5DEB3 'Wheat'"
            colors = []
            for c in color_variations[:3]:
                if isinstance(c, str):
                    if "'" in c:
                        colors.append(c.split("'")[1])
                    elif ' ' in c:
                        colors.append(c.split()[-1])
                    else:
                        colors.append(c)
            return ', '.join(colors) if colors else 'varied'
        
        return str(color_variations)[:50]
    
    def _extract_texture_summary(self, texture_details: str) -> str:
        """Extract concise texture summary."""
        if not texture_details:
            return 'varied surface texture'
        
        # Take first sentence
        if '.' in texture_details:
            return texture_details.split('.')[0]
        
        return texture_details[:100]
    
    def get_patterns_for_image_gen(
        self,
        material_name: str,
        num_patterns: int = 3
    ) -> Dict[str, Any]:
        """
        Get complete contamination data for image generation.
        
        Returns a dictionary compatible with the image generator pipeline.
        
        Args:
            material_name: Material name
            num_patterns: Number of patterns to include
            
        Returns:
            Dictionary with:
            - material: Material name
            - category: Material category
            - selected_patterns: List of pattern data
            - base_appearance: Base material appearance notes
        """
        patterns = self.select_patterns(material_name, num_patterns)
        category = self.get_material_category(material_name)
        
        # Count patterns with rich data
        rich_count = sum(1 for p in patterns if p.get('has_rich_appearance_data'))
        
        logger.info(f"📊 {material_name}: {len(patterns)} patterns selected, {rich_count} with rich appearance data")
        
        return {
            'material': material_name,
            'category': category,
            'selected_patterns': patterns,
            'base_appearance': None,  # Could be populated from Materials.yaml if needed
            'data_source': 'Contaminants.yaml',  # For transparency
            'api_calls_made': 0,  # Zero API calls!
        }


# Module-level convenience function
_selector: Optional[ContaminationPatternSelector] = None


def get_selector() -> ContaminationPatternSelector:
    """Get or create singleton selector instance."""
    global _selector
    if _selector is None:
        _selector = ContaminationPatternSelector()
    return _selector


def select_contamination_patterns(
    material_name: str,
    num_patterns: int = 3
) -> Dict[str, Any]:
    """
    Convenience function to select contamination patterns for image generation.
    
    Args:
        material_name: Material name
        num_patterns: Number of patterns
        
    Returns:
        Dictionary ready for image generation pipeline
    """
    return get_selector().get_patterns_for_image_gen(material_name, num_patterns)
