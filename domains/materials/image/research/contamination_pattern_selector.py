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

# Use central metal classifier for ferrous/non-ferrous logic
from shared.utils.metal_classifier import get_classifier

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
        'metal': ['rust-oxidation', 'industrial-oil', 'environmental-dust', 'scale-buildup', 'grease-buildup'],
        'wood': ['wood-rot', 'mold-mildew', 'environmental-dust', 'algae-growth', 'uv-chalking'],
        'polymer': ['uv-chalking', 'environmental-dust', 'industrial-oil', 'chemical-stains', 'grease-buildup'],
        'glass': ['environmental-dust', 'hard-water-deposits', 'chemical-stains', 'fingerprints', 'soap-scum'],
        'ceramic': ['environmental-dust', 'hard-water-deposits', 'mold-mildew', 'efflorescence', 'algae-growth'],
        'stone': ['environmental-dust', 'algae-growth', 'mold-mildew', 'efflorescence', 'chemical-stains'],
        'composite': ['uv-chalking', 'environmental-dust', 'industrial-oil', 'chemical-stains', 'mold-mildew'],
    }
    
    # GLOBAL POLICY: Texture normalization - convert thick/3D descriptions to thin film equivalents
    # Contamination must appear as THIN FLAT discoloration/staining in images
    # Instead of filtering out patterns, we normalize their texture descriptions
    TEXTURE_NORMALIZATIONS = {
        'rough': 'slightly textured',
        'crusty': 'thin dried film',
        'chunky': 'varied thin layer',
        'thick': 'thin',
        'caked': 'dried thin film',
        'flaky': 'thin peeling film',
        'scaly': 'thin layered film',
        'buildup': 'accumulation',
        'deposit': 'residue',
        'blob': 'spot',
        'glob': 'patch',
        'clump': 'cluster',
        'lump': 'slight raised area',
        'powdery': 'fine dust film',
        'chalky': 'matte thin film',
    }
    
    # Context-specific pattern priorities (overrides CATEGORY_PRIORITIES)
    CONTEXT_PRIORITIES = {
        'indoor': {
            'wood': ['environmental-dust', 'fingerprints', 'wax-buildup', 'food-residue', 'grease-buildup'],
            'metal': ['fingerprints', 'environmental-dust', 'food-residue', 'grease-buildup', 'scale-buildup'],
            'glass': ['fingerprints', 'environmental-dust', 'hard-water-deposits', 'soap-scum'],
            'polymer': ['environmental-dust', 'fingerprints', 'chemical-stains', 'grease-buildup'],
            'ceramic': ['environmental-dust', 'hard-water-deposits', 'soap-scum', 'food-residue'],
            'stone': ['environmental-dust', 'food-residue', 'hard-water-deposits', 'chemical-stains'],
        },
        'outdoor': {
            'wood': ['natural-weathering', 'mold-mildew', 'algae-growth', 'uv-chalking', 'lichen-growth'],
            'metal': ['rust-oxidation', 'natural-weathering', 'environmental-dust', 'algae-growth', 'scale-buildup'],
            'glass': ['environmental-dust', 'hard-water-deposits', 'algae-growth', 'mineral-deposits'],
            'polymer': ['uv-chalking', 'natural-weathering', 'environmental-dust', 'algae-growth', 'chemical-stains'],
            'ceramic': ['natural-weathering', 'algae-growth', 'mold-mildew', 'efflorescence', 'environmental-dust'],
            'stone': ['natural-weathering', 'algae-growth', 'mold-mildew', 'efflorescence', 'lichen-growth'],
        },
        'industrial': {
            'metal': ['industrial-oil', 'rust-oxidation', 'scale-buildup', 'grease-buildup', 'environmental-dust'],
            'wood': ['industrial-oil', 'environmental-dust', 'chemical-stains', 'paint-residue', 'grease-buildup'],
            'polymer': ['industrial-oil', 'chemical-stains', 'grease-buildup', 'paint-residue', 'environmental-dust'],
            'glass': ['industrial-oil', 'chemical-stains', 'environmental-dust', 'paint-residue'],
            'ceramic': ['industrial-oil', 'chemical-stains', 'environmental-dust', 'scale-buildup'],
            'composite': ['industrial-oil', 'chemical-stains', 'environmental-dust', 'grease-buildup'],
        },
        'marine': {
            # Note: use actual pattern IDs from Contaminants.yaml
            # salt-residue (not salt-deposits), industrial-oil works for most metals
            'metal': ['salt-residue', 'mineral-deposits', 'industrial-oil', 'algae-growth', 'scale-buildup'],
            'wood': ['salt-residue', 'mold-mildew', 'algae-growth', 'environmental-dust', 'biological-stains'],
            'polymer': ['salt-residue', 'uv-chalking', 'algae-growth', 'environmental-dust', 'chemical-stains'],
            'glass': ['salt-residue', 'hard-water-deposits', 'algae-growth', 'environmental-dust'],
            'composite': ['salt-residue', 'uv-chalking', 'algae-growth', 'environmental-dust'],
        },
    }
    
    # Metal classification now uses central MetalClassifier (shared/utils/metal_classifier.py)
    # This ensures consistent ferrous/non-ferrous logic across the entire codebase
    # - Ferrous metals (steel, iron) can rust
    # - Non-ferrous metals (copper, aluminum, bronze) develop patina, NOT rust
    
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
        # Copper alloys (all map to 'metal' but are non-ferrous)
        'aluminum bronze': 'metal', 'phosphor bronze': 'metal',
        'silicon bronze': 'metal', 'naval brass': 'metal',
        # Woods
        'oak': 'wood', 'pine': 'wood', 'cedar': 'wood', 'maple': 'wood',
        'walnut': 'wood', 'cherry': 'wood', 'mahogany': 'wood', 'teak': 'wood',
        'birch': 'wood', 'ash': 'wood', 'beech': 'wood', 'plywood': 'wood',
        'mdf': 'wood', 'bamboo': 'wood', 'hickory': 'wood', 'fir': 'wood',
        'ebony': 'wood', 'poplar': 'wood', 'redwood': 'wood', 'rosewood': 'wood',
        'willow': 'wood',
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
    
    def __init__(self, contaminants_file: Optional[Path] = None, materials_file: Optional[Path] = None):
        """
        Initialize selector with paths to Contaminants.yaml and Materials.yaml.
        
        Args:
            contaminants_file: Optional path to Contaminants.yaml
            materials_file: Optional path to Materials.yaml for contamination rules
        """
        self.contaminants_file = contaminants_file or PROJECT_ROOT / 'data' / 'contaminants' / 'Contaminants.yaml'
        self.materials_file = materials_file or PROJECT_ROOT / 'data' / 'materials' / 'Materials.yaml'
        self._data: Optional[Dict] = None
        self._materials_data: Optional[Dict] = None
        
        if not self.contaminants_file.exists():
            raise FileNotFoundError(f"Contaminants.yaml not found at: {self.contaminants_file}")
        
        if not self.materials_file.exists():
            logger.warning(f"⚠️ Materials.yaml not found at: {self.materials_file} - contamination rules unavailable")
        
        logger.info("✅ ContaminationPatternSelector initialized (zero API calls)")
    
    def _load_data(self) -> Dict:
        """Load contaminants data (lazy loading with caching)."""
        if self._data is None:
            with open(self.contaminants_file, 'r', encoding='utf-8') as f:
                self._data = yaml.safe_load(f)
            logger.debug(f"📦 Loaded {len(self._data.get('contamination_patterns', {}))} patterns from YAML")
        return self._data
    
    def _load_materials_data(self) -> Optional[Dict]:
        """Load materials data (lazy loading with caching)."""
        if self._materials_data is None:
            if self.materials_file.exists():
                with open(self.materials_file, 'r', encoding='utf-8') as f:
                    self._materials_data = yaml.safe_load(f)
                logger.debug(f"📦 Loaded Materials.yaml with {len(self._materials_data.get('materials', {}))} materials")
            else:
                self._materials_data = {}
        return self._materials_data
    
    def _get_material_contamination_rules(self, material_name: str) -> Dict[str, List[str]]:
        """
        Get contamination valid/prohibited rules from Materials.yaml.
        
        Args:
            material_name: Material name (e.g., "Aluminum Bronze")
            
        Returns:
            Dict with 'valid' and 'prohibited' lists of pattern IDs
            Empty lists if material not found or no rules defined
        """
        materials_data = self._load_materials_data()
        if not materials_data:
            return {'valid': [], 'prohibited': []}
        
        materials = materials_data.get('materials', {})
        material_info = materials.get(material_name, {})
        contamination = material_info.get('contamination', {})
        
        valid = contamination.get('valid', [])
        prohibited = contamination.get('prohibited', [])
        
        # Normalize pattern IDs: convert underscores to hyphens (yaml uses underscores, patterns use hyphens)
        valid = [p.replace('_', '-') for p in valid]
        prohibited = [p.replace('_', '-') for p in prohibited]
        
        if valid or prohibited:
            logger.info(f"📋 Material rules for {material_name}: valid={len(valid)}, prohibited={len(prohibited)}")
            if prohibited:
                logger.info(f"   🚫 Prohibited: {prohibited}")
        
        return {'valid': valid, 'prohibited': prohibited}

    def get_material_category(self, material_name: str) -> str:
        """Get the category for a material (for pattern prioritization)."""
        # Check cache first
        if not hasattr(self, '_category_cache'):
            self._category_cache = {}
        if material_name in self._category_cache:
            return self._category_cache[material_name]
        
        material_lower = material_name.lower()
        
        # Direct lookup
        if material_lower in self.MATERIAL_CATEGORIES:
            result = self.MATERIAL_CATEGORIES[material_lower]
            self._category_cache[material_name] = result
            return result
        
        # Fuzzy matching - extended list for better coverage
        if any(m in material_lower for m in ['steel', 'iron', 'metal', 'bronze', 'brass', 'copper', 'aluminum', 'zinc', 'nickel', 'titanium', 'alloy']):
            self._category_cache[material_name] = 'metal'
            return 'metal'
        if any(m in material_lower for m in ['wood', 'oak', 'pine', 'cedar', 'maple', 'hickory', 'walnut', 'birch', 'mahogany', 'teak']):
            self._category_cache[material_name] = 'wood'
            return 'wood'
        if any(m in material_lower for m in ['plastic', 'polymer', 'vinyl', 'acrylic', 'nylon', 'pvc', 'abs', 'hdpe', 'ldpe']):
            self._category_cache[material_name] = 'polymer'
            return 'polymer'
        if 'glass' in material_lower:
            self._category_cache[material_name] = 'glass'
            return 'glass'
        if any(m in material_lower for m in ['ceramic', 'porcelain', 'tile']):
            self._category_cache[material_name] = 'ceramic'
            return 'ceramic'
        if any(m in material_lower for m in ['stone', 'granite', 'marble', 'limestone', 'slate']):
            self._category_cache[material_name] = 'stone'
            return 'stone'
        if any(m in material_lower for m in ['fiber', 'composite', 'carbon', 'fiberglass']):
            self._category_cache[material_name] = 'composite'
            return 'composite'
        
        # Fall back to Materials.yaml lookup (with caching)
        try:
            if not hasattr(self, '_materials_data'):
                materials_file = PROJECT_ROOT / 'data' / 'materials' / 'Materials.yaml'
                if materials_file.exists():
                    logger.info("📦 Loading Materials.yaml for category lookup (one-time)...")
                    with open(materials_file, 'r', encoding='utf-8') as f:
                        self._materials_data = yaml.safe_load(f)
                else:
                    self._materials_data = {}
            
            materials = self._materials_data.get('materials', {})
            if material_name in materials:
                category = materials[material_name].get('category')
                if not category:
                    raise ValueError(
                        f"Material '{material_name}' missing required 'category' field in Materials.yaml. "
                        "NO DEFAULTS - per copilot-instructions.md policy."
                    )
                self._category_cache[material_name] = category
                return category
        except Exception as e:
            raise ValueError(
                f"Failed to get category for material '{material_name}': {e}. "
                "Material must exist in Materials.yaml with a 'category' field."
            )
        
        raise ValueError(
            f"Material '{material_name}' not found in Materials.yaml. "
            "NO FALLBACK to 'metal' - per copilot-instructions.md policy."
        )
    
    def is_ferrous_metal(self, material_name: str) -> bool:
        """
        Check if a material is a ferrous metal (contains iron, can rust).
        
        Uses centralized MetalClassifier for consistent logic across codebase.
        
        Non-ferrous metals like copper, aluminum, bronze, brass develop
        patina/oxidation but NOT rust (iron oxide).
        
        Args:
            material_name: Material name
            
        Returns:
            True if ferrous (can rust), False otherwise
        """
        classifier = get_classifier()
        return classifier.is_ferrous(material_name)
    
    def _normalize_texture_description(self, texture_text: str) -> str:
        """
        GLOBAL POLICY: Normalize texture descriptions to thin film standards.
        
        Instead of filtering out patterns with thick/3D textures, we normalize
        their descriptions to conform to thin flat film appearance standards.
        This allows all patterns to be used while ensuring consistent image output.
        
        Args:
            texture_text: Original texture description (string or dict)
            
        Returns:
            Normalized texture description with thick/3D terms replaced
        """
        if not texture_text:
            return ''
        
        # Handle dict input (some YAML fields are dicts)
        if isinstance(texture_text, dict):
            # Convert dict to string representation
            texture_text = str(texture_text)
        
        normalized = str(texture_text)
        for thick_term, thin_replacement in self.TEXTURE_NORMALIZATIONS.items():
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(thick_term), re.IGNORECASE)
            if pattern.search(normalized):
                normalized = pattern.sub(thin_replacement, normalized)
                logger.debug(f"🔄 Normalized texture: '{thick_term}' → '{thin_replacement}'")
        
        return normalized
    
    def _is_pattern_valid_for_material(self, pattern_id: str, pattern: Dict, material_name: str) -> bool:
        """
        Check if a pattern is chemically/physically valid for a material.
        
        Implements contamination physics rules:
        - Rust only on ferrous metals
        - Copper patina only on copper alloys
        - GLOBAL: No patterns with thick/chunky texture descriptions
        - etc.
        
        Args:
            pattern_id: Pattern identifier
            pattern: Pattern data dict
            material_name: Material name
            
        Returns:
            True if pattern is valid for material
        """
        # NOTE: Texture normalization happens in _build_pattern_result, not here
        # All patterns are allowed; their textures are normalized to thin film standards
        
        # Check invalid_materials list
        invalid_materials = pattern.get('invalid_materials', [])
        material_lower = material_name.lower()
        if any(material_lower == im.lower() for im in invalid_materials):
            return False
        
        # CRITICAL: Rust/iron oxide ONLY on ferrous metals
        if pattern_id in ['rust-oxidation', 'rust', 'iron-oxide']:
            if not self.is_ferrous_metal(material_name):
                logger.debug(f"🚫 Excluding {pattern_id} - {material_name} is non-ferrous")
                return False
        
        # Copper patina ONLY on copper-containing alloys
        if pattern_id in ['copper-patina', 'verdigris']:
            copper_keywords = ['copper', 'bronze', 'brass']
            if not any(kw in material_lower for kw in copper_keywords):
                logger.debug(f"🚫 Excluding {pattern_id} - {material_name} doesn't contain copper")
                return False
        
        return True
    
    def _material_matches_valid_list(self, material_name: str, valid_materials: List[str]) -> bool:
        """
        Check if a material matches any entry in valid_materials list.
        
        Uses intelligent matching to handle:
        - Exact matches: "Titanium" matches "Titanium"
        - Alloy variants: "Titanium Alloy (Ti-6Al-4V)" matches "Titanium"
        - Base material extraction: "Stainless Steel 316" matches "Stainless Steel"
        
        Args:
            material_name: Full material name (e.g., "Titanium Alloy (Ti-6Al-4V)")
            valid_materials: List of valid materials from pattern (e.g., ["Titanium", "Steel"])
            
        Returns:
            True if material matches any entry in valid_materials
        """
        material_lower = material_name.lower()
        
        for vm in valid_materials:
            vm_lower = vm.lower()
            
            # Exact match
            if material_lower == vm_lower:
                return True
            
            # Check if valid_material is a base component of the material name
            # e.g., "Titanium" is in "Titanium Alloy (Ti-6Al-4V)"
            # e.g., "Steel" is in "Stainless Steel 316"
            if vm_lower in material_lower:
                return True
            
            # Check if material name starts with valid_material
            # e.g., "Stainless Steel" matches "Stainless Steel 304"
            if material_lower.startswith(vm_lower):
                return True
            
            # Extract base name (before parenthesis) and check
            # e.g., "Titanium Alloy" from "Titanium Alloy (Ti-6Al-4V)"
            if '(' in material_lower:
                base_name = material_lower.split('(')[0].strip()
                if vm_lower in base_name or base_name.startswith(vm_lower):
                    return True
        
        return False
    
    def get_valid_patterns_for_material(self, material_name: str) -> List[str]:
        """
        Get list of pattern IDs that are valid for a material.
        
        Uses the valid_materials field AND chemical compatibility rules.
        Uses intelligent matching to handle alloy variants and base materials.
        
        Args:
            material_name: Material name (e.g., "Aluminum", "Titanium Alloy (Ti-6Al-4V)")
            
        Returns:
            List of pattern IDs valid for this material
        """
        data = self._load_data()
        patterns = data.get('contamination_patterns', {})
        
        valid_pattern_ids = []
        for pattern_id, pattern in patterns.items():
            # First check chemical compatibility (rust only on ferrous, etc.)
            if not self._is_pattern_valid_for_material(pattern_id, pattern, material_name):
                continue
                
            valid_materials = pattern.get('valid_materials', [])
            # Check if material matches valid_materials (intelligent matching)
            if self._material_matches_valid_list(material_name, valid_materials):
                valid_pattern_ids.append(pattern_id)
        
        return valid_pattern_ids
    
    def _get_category_fallback_patterns(self, category: str, patterns: Dict) -> List[str]:
        """
        Get patterns valid for any material in the same category.
        
        Used as fallback when a material has no direct patterns defined.
        For example, Hickory might use patterns defined for Oak (both wood).
        """
        # Map categories to representative materials that likely have patterns
        category_representatives = {
            'wood': ['Oak', 'Pine', 'Cedar', 'Maple', 'Walnut'],
            'metal': ['Steel', 'Aluminum', 'Iron', 'Copper'],
            'polymer': ['PVC', 'ABS', 'Acrylic', 'Nylon'],
            'glass': ['Glass'],
            'ceramic': ['Ceramic', 'Porcelain'],
            'stone': ['Granite', 'Marble', 'Limestone'],
            'composite': ['Carbon Fiber', 'Fiberglass'],
        }
        
        representatives = category_representatives.get(category, [])
        fallback_ids = set()
        
        for pattern_id, pattern in patterns.items():
            valid_materials = pattern.get('valid_materials', [])
            # Check if any representative material is in valid_materials
            for rep in representatives:
                if any(rep.lower() == vm.lower() for vm in valid_materials):
                    fallback_ids.add(pattern_id)
                    break
        
        return list(fallback_ids)
    
    def select_patterns(
        self,
        material_name: str,
        num_patterns: int = 4,
        prefer_with_appearance: bool = True,
        context: str = "outdoor"
    ) -> List[Dict[str, Any]]:
        """
        Select contamination patterns for a material.
        
        MANDATORY POLICIES (Dec 1, 2025):
        1. Always select 3-5 contaminants (default: 4)
        2. Context is NOT a factor in selection - select most common for material
        3. Priority: patterns with rich appearance data > high commonality score
        
        Selection priority:
        1. Patterns with material-specific appearance data (rich data preferred)
        2. Patterns with high commonality scores (most common for this material)
        3. Any valid patterns for this material
        
        Args:
            material_name: Material name
            num_patterns: Number of patterns to select (default: 4, range: 3-5)
            prefer_with_appearance: Prioritize patterns with appearance_on_materials data
            context: Environment context (passed through but NOT used for selection)
            
        Returns:
            List of pattern data dictionaries ready for image generation
        """
        # POLICY: Enforce 3-5 pattern range
        num_patterns = max(3, min(5, num_patterns))
        data = self._load_data()
        patterns = data.get('contamination_patterns', {})
        
        # Get valid patterns for this material
        valid_ids = self.get_valid_patterns_for_material(material_name)
        
        # Get material category for prioritization
        category = self.get_material_category(material_name)
        
        # CRITICAL: Apply Materials.yaml contamination rules (valid/prohibited lists)
        material_rules = self._get_material_contamination_rules(material_name)
        prohibited_patterns = set(material_rules.get('prohibited', []))
        
        if prohibited_patterns:
            before_count = len(valid_ids)
            valid_ids = [pid for pid in valid_ids if pid not in prohibited_patterns]
            filtered_count = before_count - len(valid_ids)
            if filtered_count > 0:
                logger.info(f"🚫 Filtered {filtered_count} patterns prohibited by Materials.yaml rules")
        
        # FALLBACK: If no direct patterns, use patterns from same category
        if not valid_ids:
            logger.warning(f"No direct contamination patterns for {material_name}, using {category} fallback")
            valid_ids = self._get_category_fallback_patterns(category, patterns)
            
            # Apply prohibited filter to fallback patterns too!
            if prohibited_patterns and valid_ids:
                before_count = len(valid_ids)
                valid_ids = [pid for pid in valid_ids if pid not in prohibited_patterns]
                filtered_count = before_count - len(valid_ids)
                if filtered_count > 0:
                    logger.info(f"🚫 Filtered {filtered_count} fallback patterns prohibited by Materials.yaml rules")
            
            if not valid_ids:
                logger.warning(f"No contamination patterns found for {material_name} or {category} category")
                return []
        
        # POLICY: Context is NOT a factor - select most common patterns for this material
        # We ignore context_priorities and context_weights entirely
        # Priority is based solely on: rich appearance data + commonality score
        
        # POLICY (Dec 1, 2025): Reduce weight of generic/ubiquitous patterns
        # These are too common and less visually interesting - prefer specific contaminants
        GENERIC_PATTERN_PENALTY = {
            'environmental-dust': 0.2,  # Very common, reduce significantly
            'industrial-oil': 0.25,     # Common on machinery, reduce more
            'grease-buildup': 0.25,     # Similar to oil
            'fingerprints': 0.3,        # Too generic
            'water-stain': 0.4,         # Too common
            'general-grime': 0.3,       # Too generic
        }
        
        # POLICY (Dec 1, 2025): Boost aging patterns - more visually interesting
        AGING_PATTERN_BOOST = {
            'uv-chalking': 1.5,         # UV degradation - visual aging
            'thermal-discoloration': 1.4,  # Heat aging
            'oxidation': 1.3,           # Natural aging
            'patina': 1.4,              # Attractive aging
            'weathering': 1.3,          # Natural weathering
            'annealing-scale': 1.3,     # Heat treatment scale
            'surface-crazing': 1.4,     # Polymer aging cracks
        }
        
        # Score patterns for selection - MOST COMMON for material, NOT context-based
        scored_patterns = []
        for pattern_id in valid_ids:
            pattern = patterns.get(pattern_id, {})
            
            # CRITICAL: Filter out chemically incompatible patterns (rust on non-ferrous, etc.)
            if not self._is_pattern_valid_for_material(pattern_id, pattern, material_name):
                logger.info(f"🚫 Filtered out {pattern_id} - incompatible with {material_name}")
                continue
            
            score = 0
            
            # Apply per-pattern commonality_score from Contaminants.yaml
            # This represents how common this contamination is for this material type
            # Higher score = more commonly found on this material
            commonality_score = pattern.get('commonality_score', 50)  # Default: moderate commonality
            score += commonality_score
            
            # Strong bonus for having material-specific appearance data (rich data)
            if prefer_with_appearance:
                appearance = self._get_appearance(pattern, material_name)
                if appearance:
                    if 'color_variations' in appearance:
                        score += 200  # Very strong preference for rich Format B data
                    else:
                        score += 100  # Good preference for Format A data
            
            # Bonus for patterns that explicitly list this material (not just ALL)
            valid_materials = pattern.get('valid_materials', [])
            if 'ALL' not in valid_materials:
                # Material is explicitly listed = more specific/common for this material
                score += 50
            
            # Apply per-pattern priority_weight if specified
            pattern_weight = pattern.get('priority_weight', 1.0)
            score *= pattern_weight
            
            # POLICY: Apply penalty to generic/ubiquitous patterns
            generic_penalty = GENERIC_PATTERN_PENALTY.get(pattern_id, 1.0)
            if generic_penalty < 1.0:
                logger.debug(f"📉 Applying generic penalty {generic_penalty} to {pattern_id}")
            score *= generic_penalty
            
            # POLICY: Apply boost to aging patterns
            aging_boost = AGING_PATTERN_BOOST.get(pattern_id, 1.0)
            if aging_boost > 1.0:
                logger.debug(f"📈 Applying aging boost {aging_boost} to {pattern_id}")
            score *= aging_boost
            
            scored_patterns.append((score, pattern_id, pattern, pattern_weight))
        
        # Sort by score (highest first) and select top N
        scored_patterns.sort(reverse=True, key=lambda x: x[0])
        selected = scored_patterns[:num_patterns]
        
        # MANDATORY TERMINAL OUTPUT: Log ALL evaluated patterns with names and weights
        # POLICY: One line per contaminant showing NAME and WEIGHT
        # This is required by policy - see copilot-instructions.md "Contaminant Appearance Data Policy"
        print(f"\n{'='*70}")
        print(f"🧪 CONTAMINATION PATTERNS FOR: {material_name}")
        print(f"{'='*70}")
        print(f"   Context: {context}")
        print(f"   Patterns requested: {num_patterns}")
        print(f"   Patterns selected: {len(selected)}")
        rich_count = sum(1 for _, _, p, _ in selected if self._get_appearance(p, material_name))
        print(f"   Rich appearance data: {rich_count}/{len(selected)}")
        print(f"\n   📋 SELECTED CONTAMINATION PATTERNS:\n")
        for i, (score, pattern_id, pattern, weight) in enumerate(selected, 1):
            pattern_name = pattern.get('name', pattern_id)
            has_rich = "✅ Rich data" if self._get_appearance(pattern, material_name) else "⚠️ Base data"
            cat = pattern.get('category', 'contamination')
            
            # Get appearance info for display
            appearance = self._get_appearance(pattern, material_name)
            colors = "N/A"
            texture = "N/A"
            if appearance:
                colors = self._extract_colors_from_text(str(appearance.get('color_variations', appearance.get('appearance', ''))))
                texture = self._extract_texture_from_text(str(appearance.get('texture_details', appearance.get('appearance', ''))))[:50]
            
            print(f"   {i}. {pattern_name} ({pattern_id})")
            print(f"      {has_rich} | Category: {cat}")
            print(f"      Colors: {colors}")
            print(f"      Texture: {texture}...")
            realism = pattern.get('realism_notes', '')
            if realism:
                print(f"      Realism: {realism[:60]}...")
            print()
        print(f"{'='*70}\n")
        
        # Build result dictionaries with relevance scores
        results = []
        for score, pattern_id, pattern, weight in selected:
            result = self._build_pattern_result(pattern_id, pattern, material_name)
            if result:
                result['relevance_score'] = score  # Add score for learning
                result['priority_weight'] = weight  # Include weight in result
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
        
        # Category aliases - YAML uses 'plastic' but our system uses 'polymer'
        CATEGORY_ALIASES = {
            'polymer': 'plastic',
            'alloy': 'metal',
        }
        
        if material_category:
            # Try direct match first
            if material_category in categories:
                logger.debug(f"📁 Using category-level appearance ({material_category}) for {material_name}")
                return categories[material_category]
            # Try alias
            alias = CATEGORY_ALIASES.get(material_category)
            if alias and alias in categories:
                logger.debug(f"📁 Using aliased category appearance ({material_category}→{alias}) for {material_name}")
                return categories[alias]
        
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
        
        YAML has TWO structures for appearance_on_categories:
        
        Format A (simple, 3 fields):
        - appearance: Visual description
        - coverage: Coverage description
        - pattern: Pattern description
        
        Format B (rich, 16+ fields):
        - color_variations, texture_details, common_patterns, aged_appearance,
        - lighting_effects, thickness_range, distribution_patterns, etc.
        
        This method handles both formats.
        """
        if not pattern:
            return None
        
        # Get material/category-specific appearance data
        appearance = self._get_appearance(pattern, material_name)
        
        # Build visual characteristics - handle BOTH YAML formats
        if appearance:
            # Detect which format this appearance data uses
            is_rich_format = 'color_variations' in appearance or 'aged_appearance' in appearance
            
            if is_rich_format:
                # Format B: Rich 16-field structure
                # GLOBAL POLICY: Normalize texture descriptions to thin film standards
                raw_texture = appearance.get('texture_details', '')
                normalized_texture = self._normalize_texture_description(raw_texture)
                visual_chars = {
                    'color_range': self._extract_color_summary(appearance.get('color_variations', ''), material_name),
                    'texture_detail': self._normalize_texture_description(self._extract_texture_summary(raw_texture)),
                    'description': appearance.get('aged_appearance', ''),
                    'color_variations': appearance.get('color_variations', ''),
                    'texture_details': normalized_texture,
                    'common_patterns': appearance.get('common_patterns', ''),
                    'aged_appearance': appearance.get('aged_appearance', ''),
                    'lighting_effects': appearance.get('lighting_effects', ''),
                    'thickness_range': appearance.get('thickness_range', ''),
                    'distribution_patterns': appearance.get('distribution_patterns', ''),
                    'gravity_influence': appearance.get('gravity_influence', ''),
                    'geometry_effects': appearance.get('geometry_effects', ''),
                    'edge_center_behavior': appearance.get('edge_center_behavior', ''),
                    'coverage_ranges': appearance.get('coverage_ranges', ''),
                    'buildup_progression': appearance.get('buildup_progression', ''),
                }
                logger.debug(f"✅ Rich format (Format B) appearance data for {material_name}")
            else:
                # Format A: Simple 3-field structure
                # GLOBAL POLICY: Normalize texture descriptions to thin film standards
                raw_appearance = appearance.get('appearance', '')
                normalized_appearance = self._normalize_texture_description(raw_appearance)
                visual_chars = {
                    'description': normalized_appearance,
                    'coverage': appearance.get('coverage', ''),
                    'pattern': appearance.get('pattern', ''),
                    # Extract color/texture info from appearance text
                    'color_range': self._extract_colors_from_text(raw_appearance),
                    'texture_detail': self._normalize_texture_description(self._extract_texture_from_text(raw_appearance)),
                    'distribution_patterns': appearance.get('pattern', ''),
                    'coverage_ranges': appearance.get('coverage', ''),
                }
                logger.debug(f"✅ Simple format (Format A) appearance data for {material_name}")
            
            has_rich_data = True
        else:
            # Fallback to base pattern description
            visual_chars = {
                'color_range': 'varied',
                'texture_detail': pattern.get('description', '')[:100],
                'description': pattern.get('description', ''),
            }
            has_rich_data = False
        
        # Get realism notes (expert knowledge for accurate rendering)
        realism_notes = pattern.get('realism_notes', '')
        
        return {
            'pattern_id': pattern_id,
            'pattern_name': pattern.get('name', pattern_id),
            'visual_characteristics': visual_chars,
            'has_rich_appearance_data': has_rich_data,
            'category': pattern.get('category', 'contamination'),
            # Expert realism notes (NEW - for image accuracy)
            'realism_notes': realism_notes,
            # Include material-specific image generation feedback if available
            'image_generation_feedback': self._get_image_gen_feedback(pattern, material_name),
        }
    
    def _extract_colors_from_text(self, text: str) -> str:
        """Extract color information from appearance description text."""
        if not text:
            return 'varied'
        
        import re
        # Common color words to look for
        color_pattern = r'\b(red|orange|brown|black|white|gray|grey|green|blue|yellow|rust|patina|silver|gold|dark|light|translucent|opaque|yellowish|grayish|greenish|brownish|whitish|golden|copper|bronze|tan|beige|cream|ivory)\b'
        colors = re.findall(color_pattern, text.lower())
        
        if colors:
            # Deduplicate and limit
            unique_colors = list(dict.fromkeys(colors))[:5]
            return ', '.join(unique_colors)
        
        return 'varied'
    
    def _extract_texture_from_text(self, text: str) -> str:
        """Extract texture information from appearance description text."""
        if not text:
            return 'varied surface texture'
        
        import re
        # Common texture words to look for
        texture_pattern = r'\b(rough|smooth|flaky|powdery|granular|porous|glossy|matte|pitted|scaly|sticky|gummy|crusty|filmy|slimy|chalky|crystalline|gritty|tacky|dull|shiny)\b'
        textures = re.findall(texture_pattern, text.lower())
        
        if textures:
            # Deduplicate and limit
            unique_textures = list(dict.fromkeys(textures))[:3]
            return ', '.join(unique_textures) + ' texture'
        
        return 'varied surface texture'
    
    def _extract_color_summary(self, color_variations: Any, material_name: str = '') -> str:
        """Extract concise color summary from color_variations field.
        
        Handles multiple structures:
        - String: Direct color description (Format B prose)
        - List: Color entries like "#F5DEB3 'Wheat'" (Format B list)
        - Dict: Keyed by material name {'aluminum': '...', 'copper': '...'} (Format B nested)
        """
        if not color_variations:
            return 'varied'
        
        # Handle dict keyed by material name
        if isinstance(color_variations, dict):
            # Try to find the specific material's color info
            material_key = material_name.lower().replace(' ', '_')
            for key, value in color_variations.items():
                if key.lower() == material_key or material_key in key.lower():
                    # Found material-specific color data
                    if isinstance(value, str):
                        return self._extract_colors_from_text(value)
            # Fall back to first entry's value
            first_value = next(iter(color_variations.values()), '')
            if isinstance(first_value, str):
                return self._extract_colors_from_text(first_value)
            return 'varied'
        
        # Handle string format (Format B rich structure - color_variations is a prose string)
        if isinstance(color_variations, str):
            # Extract colors from prose description
            return self._extract_colors_from_text(color_variations)
        
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
    
    def _extract_texture_summary(self, texture_details) -> str:
        """Extract concise texture summary.
        
        Handles both Format A (prose string) and Format B (structured) textures.
        """
        if not texture_details:
            return 'varied surface texture'
        
        # Handle dict (appearance_on_materials structure may have nested data)
        if isinstance(texture_details, dict):
            # Try to get a description or convert to string
            texture_details = texture_details.get('description', str(texture_details))
        
        # Ensure it's a string
        texture_details = str(texture_details)
        
        # Extract texture words from prose
        return self._extract_texture_from_text(texture_details)
        
        # Take first sentence
        if '.' in texture_details:
            return texture_details.split('.')[0]
        
        return texture_details[:100]
    
    def _get_image_gen_feedback(self, pattern: Dict, material_name: str) -> str:
        """
        Get material-specific image generation feedback for a pattern.
        
        This feedback is persisted in Contaminants.yaml under image_generation_feedback
        and provides learned guidance for how to render this contamination on this material.
        
        Args:
            pattern: The contamination pattern data
            material_name: The material name
            
        Returns:
            Combined feedback string, or empty string if none available
        """
        feedback_section = pattern.get('image_generation_feedback', {})
        if not feedback_section:
            return ""
        
        # Try exact material match
        material_key = material_name.lower().replace(' ', '_')
        mat_feedback = feedback_section.get(material_key, {})
        
        if not mat_feedback:
            # Try fuzzy match (e.g., "aluminum_bronze" matches "bronze")
            for key, data in feedback_section.items():
                stored_name = data.get('material_name', '').lower()
                if (material_name.lower() in stored_name or 
                    stored_name in material_name.lower() or
                    key.replace('_', ' ') in material_name.lower()):
                    mat_feedback = data
                    break
        
        if not mat_feedback:
            return ""
        
        # Combine all notes into single feedback string
        notes = mat_feedback.get('notes', {})
        if not notes:
            return ""
        
        parts = []
        for category, note in notes.items():
            if note:
                parts.append(f"[{category.upper()}] {note}")
        
        return " | ".join(parts) if parts else ""

    def get_patterns_for_image_gen(
        self,
        material_name: str,
        num_patterns: int = 4,
        context: str = "outdoor"
    ) -> Dict[str, Any]:
        """
        Get complete contamination data for image generation.
        
        MANDATORY POLICIES (Dec 1, 2025):
        - Always returns 3-5 contamination patterns (default: 4)
        - Context is passed through for logging but NOT used for selection
        - Patterns selected by commonality for material, NOT context
        
        Args:
            material_name: Material name
            num_patterns: Number of patterns (default: 4, enforced range: 3-5)
            context: Environment context (for logging only, not selection)
            
        Returns:
            Dictionary with:
            - material: Material name
            - category: Material category
            - context: Environment context
            - selected_patterns: List of pattern data (3-5 most common)
            - base_appearance: Base material appearance notes
        """
        patterns = self.select_patterns(material_name, num_patterns, context=context)
        category = self.get_material_category(material_name)
        
        # Load context settings from YAML (background, severity defaults)
        data = self._load_data()
        context_settings = data.get('context_settings', {})
        ctx_config = context_settings.get(context, {})
        
        # Count patterns with rich data
        rich_count = sum(1 for p in patterns if p.get('has_rich_appearance_data'))
        
        # Log context-aware selection
        aging_patterns = [p for p in patterns if p.get('pattern_id') == 'natural-weathering']
        logger.info(f"📊 {material_name} ({context}): {len(patterns)} patterns selected, {rich_count} with rich data, {len(aging_patterns)} aging patterns")
        
        return {
            'material': material_name,
            'category': category,
            'context': context,
            'context_background': ctx_config.get('background', 'neutral environment'),
            'default_severity': ctx_config.get('default_severity', 'moderate'),
            'context_settings': {
                'aging_weight': ctx_config.get('aging_weight', 1.0),
                'contamination_weight': ctx_config.get('contamination_weight', 1.0),
                'background': ctx_config.get('background', 'neutral environment'),
                'default_severity': ctx_config.get('default_severity', 'moderate')
            },
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
    num_patterns: int = 4,
    context: str = "outdoor"
) -> Dict[str, Any]:
    """
    Convenience function to select contamination patterns for image generation.
    
    MANDATORY POLICIES (Dec 1, 2025):
    - Always returns 3-5 contamination patterns (default: 4)
    - Context NOT used for selection - most common patterns for material
    
    Args:
        material_name: Material name
        num_patterns: Number of patterns (default: 4, range: 3-5)
        context: Environment context (for logging only)
        
    Returns:
        Dictionary ready for image generation pipeline
    """
    return get_selector().get_patterns_for_image_gen(material_name, num_patterns, context=context)
