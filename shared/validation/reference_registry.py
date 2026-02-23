"""
Central Reference Registry

Maintains an in-memory index of all valid IDs across domains.
Used by generators to validate references before saving.

Usage:
    from shared.validation.reference_registry import ReferenceRegistry
    
    registry = ReferenceRegistry()
    registry.load_all()
    
    # Validate reference
    if registry.is_valid('contaminants', 'rust-contamination'):
        # Use reference
        pass
    
    # Get suggestions for broken reference
    suggestions = registry.suggest_fixes('contaminants', 'rust')
"""

import difflib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml


@dataclass
class ReferenceInfo:
    """Information about a reference"""
    domain: str
    id: str
    name: str
    exists: bool
    suggestions: List[str] = None

class ReferenceRegistry:
    """Central registry of all valid domain IDs"""
    
    # Data file locations
    DATA_FILES = {
        'materials': 'data/materials/Materials.yaml',
        'contaminants': 'data/contaminants/contaminants.yaml',
        'compounds': 'data/compounds/Compounds.yaml',
        'settings': 'data/settings/Settings.yaml',
        'applications': 'data/applications/Applications.yaml',
    }
    
    # Root keys for each domain
    DOMAIN_KEYS = {
        'materials': 'materials',
        'contaminants': 'contamination_patterns',
        'compounds': 'compounds',
        'settings': 'settings',
        'applications': 'applications',
    }
    
    # Suffix rules
    SUFFIX_RULES = {
        'contaminants': '-contamination',
    }
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or self._find_project_root()
        self.index: Dict[str, Set[str]] = defaultdict(set)
        self.metadata: Dict[str, Dict[str, dict]] = defaultdict(dict)
        self._loaded = False

    def _validate_domain(self, domain: str):
        """Validate domain is explicitly configured"""
        if domain not in self.DATA_FILES:
            raise KeyError(f"Unknown domain: {domain}. Valid domains: {list(self.DATA_FILES.keys())}")
    
    def _find_project_root(self) -> Path:
        """Find project root from current file location"""
        current = Path(__file__).resolve()
        # Go up from shared/validation/ to project root
        return current.parent.parent.parent
    
    def load_all(self, force: bool = False):
        """Load all domain data into registry"""
        if self._loaded and not force:
            return
        
        for domain, file_path in self.DATA_FILES.items():
            self.load_domain(domain, file_path)
        
        self._loaded = True
    
    def load_domain(self, domain: str, file_path: str):
        """Load a single domain into registry"""
        self._validate_domain(domain)
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            return
        
        try:
            with open(full_path, 'r') as f:
                content = yaml.safe_load(f)

            if not isinstance(content, dict):
                raise RuntimeError(
                    f"Invalid YAML structure for domain '{domain}': expected dictionary root"
                )
            
            # Get items based on domain structure
            if domain not in self.DOMAIN_KEYS:
                raise KeyError(f"Missing root-key configuration for domain: {domain}")

            root_key = self.DOMAIN_KEYS[domain]
            if root_key not in content:
                raise KeyError(
                    f"Missing required root key '{root_key}' for domain '{domain}' in {full_path}"
                )

            items = content[root_key]
            
            if not isinstance(items, dict):
                raise RuntimeError(
                    f"Invalid items structure for domain '{domain}': root key '{root_key}' must map to dictionary"
                )
            
            # Build index
            for item_id, item_data in items.items():
                self.index[domain].add(item_id)
                
                # Store metadata
                if isinstance(item_data, dict):
                    if 'name' not in item_data or not isinstance(item_data['name'], str) or not item_data['name'].strip():
                        raise KeyError(
                            f"Missing required non-empty 'name' for domain '{domain}' item '{item_id}'"
                        )
                    self.metadata[domain][item_id] = {
                        'name': item_data['name'],
                        'title': item_data['title'] if 'title' in item_data else item_data['name'],
                    }
                else:
                    raise RuntimeError(
                        f"Invalid item structure for domain '{domain}' item '{item_id}': expected dictionary"
                    )
        
        except Exception as e:
            raise RuntimeError(f"Failed loading reference registry domain '{domain}': {e}") from e
    
    def is_valid(self, domain: str, reference_id: str) -> bool:
        """Check if a reference ID is valid"""
        self._validate_domain(domain)
        if not self._loaded:
            self.load_all()
        
        return reference_id in self.index[domain]
    
    def validate_reference(self, domain: str, reference_id: str, 
                          auto_fix: bool = False) -> ReferenceInfo:
        """
        Validate a reference and optionally suggest fixes
        
        Args:
            domain: Target domain (materials, contaminants, etc.)
            reference_id: ID to validate
            auto_fix: If True, attempt to auto-fix common issues
            
        Returns:
            ReferenceInfo with validation results and suggestions
        """
        self._validate_domain(domain)
        if not self._loaded:
            self.load_all()
        
        # Check if valid
        if self.is_valid(domain, reference_id):
            if reference_id not in self.metadata[domain]:
                raise KeyError(
                    f"Metadata missing for valid reference '{reference_id}' in domain '{domain}'"
                )
            return ReferenceInfo(
                domain=domain,
                id=reference_id,
                name=self.metadata[domain][reference_id]['name'],
                exists=True
            )
        
        # Not valid - try to fix
        suggestions = []
        
        # Try adding/removing suffix
        suffix = self.SUFFIX_RULES.get(domain)
        if suffix:
            if not reference_id.endswith(suffix):
                candidate = f"{reference_id}{suffix}"
                if self.is_valid(domain, candidate):
                    suggestions.append(candidate)
            elif reference_id.endswith(suffix):
                candidate = reference_id[:-len(suffix)]
                if self.is_valid(domain, candidate):
                    suggestions.append(candidate)
        
        # Try fuzzy matching
        if domain in self.index:
            close_matches = difflib.get_close_matches(
                reference_id, 
                self.index[domain], 
                n=3, 
                cutoff=0.6
            )
            suggestions.extend(close_matches)
        
        # Remove duplicates while preserving order
        suggestions = list(dict.fromkeys(suggestions))
        
        return ReferenceInfo(
            domain=domain,
            id=reference_id,
            name='',
            exists=False,
            suggestions=suggestions[:3]  # Top 3 suggestions
        )
    
    def validate_references(self, domain: str, reference_ids: List[str],
                           auto_fix: bool = False) -> Tuple[List[str], List[ReferenceInfo]]:
        """
        Validate multiple references at once
        
        Returns:
            (valid_ids, invalid_info)
        """
        valid = []
        invalid = []
        
        for ref_id in reference_ids:
            info = self.validate_reference(domain, ref_id, auto_fix=auto_fix)
            if info.exists:
                valid.append(ref_id)
            else:
                invalid.append(info)
        
        return valid, invalid
    
    def get_all_ids(self, domain: str) -> Set[str]:
        """Get all valid IDs for a domain"""
        self._validate_domain(domain)
        if not self._loaded:
            self.load_all()
        
        return self.index[domain].copy()
    
    def suggest_fixes(self, domain: str, broken_id: str, max_suggestions: int = 3) -> List[str]:
        """Get fix suggestions for a broken reference"""
        self._validate_domain(domain)
        info = self.validate_reference(domain, broken_id)
        return info.suggestions[:max_suggestions] if info.suggestions else []
    
    def get_stats(self) -> Dict[str, int]:
        """Get registry statistics"""
        if not self._loaded:
            self.load_all()
        
        return {
            domain: len(ids)
            for domain, ids in self.index.items()
        }
    
    def get_link_data(self, domain: str, reference_id: str) -> Optional[Dict]:
        """
        Get complete link data for a reference
        
        Returns formatted link object with id, title, url, etc.
        Ready to use in relationships without additional formatting.
        
        Args:
            domain: Target domain
            reference_id: ID to get link for
            
        Returns:
            Dict with {id, title, url, ...} or None if invalid
        """
        self._validate_domain(domain)
        if not self._loaded:
            self.load_all()
        
        # Validate reference exists
        info = self.validate_reference(domain, reference_id, auto_fix=True)
        
        if not info.exists:
            return None
        
        # Use corrected ID if it was fixed
        final_id = info.suggestions[0] if info.suggestions else reference_id
        
        # Get metadata
        if final_id not in self.metadata[domain]:
            return None
        
        meta = self.metadata[domain][final_id]

        if 'name' not in meta:
            raise KeyError(
                f"Metadata for '{final_id}' in domain '{domain}' missing required field 'name'"
            )
        
        # Build link object
        link_data = {
            'id': final_id,
            'title': meta['title'] if 'title' in meta and isinstance(meta['title'], str) and meta['title'].strip() else meta['name'],
        }
        
        # Add URL based on domain
        if domain == 'materials':
            link_data['url'] = f"/materials/{final_id}"
        elif domain == 'contaminants':
            # Contaminants URLs follow pattern: /contaminants/category/subcategory/id
            # For now, use simple pattern (can be enhanced)
            link_data['url'] = f"/contaminants/{final_id}"
        elif domain == 'compounds':
            link_data['url'] = f"/compounds/{final_id}"
        elif domain == 'settings':
            link_data['url'] = f"/settings/{final_id}"
        elif domain == 'applications':
            link_data['url'] = f"/applications/{final_id}"
        
        return link_data
    
    def get_links_batch(self, domain: str, reference_ids: List[str], 
                       skip_invalid: bool = True) -> List[Dict]:
        """
        Get link data for multiple references
        
        Args:
            domain: Target domain
            reference_ids: List of IDs to get links for
            skip_invalid: If True, skip invalid refs; if False, return None entries
            
        Returns:
            List of link data dicts
        """
        links = []
        
        for ref_id in reference_ids:
            link_data = self.get_link_data(domain, ref_id)
            
            if link_data:
                links.append(link_data)
            elif not skip_invalid:
                links.append(None)
        
        return links
    
    def build_relationships(self, source_domain: str, 
                          relationship_spec: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
        """
        Build complete relationships dict from ID lists
        
        Converts simple ID lists to formatted relationship objects.
        
        Args:
            source_domain: The domain these relationships belong to
            relationship_spec: Dict of {relationship_type: [id1, id2, ...]}
            
        Returns:
            Dict of {relationship_type: [{id, title, url}, ...]}
            
        Example:
            >>> registry.build_relationships('materials', {
            ...     'related_contaminants': ['rust', 'paint-residue']
            ... })
            {
                'related_contaminants': [
                    {'id': 'rust-contamination', 'title': 'Rust', 'url': '/contaminants/rust-contamination'},
                    {'id': 'paint-residue-contamination', 'title': 'Paint Residue', 'url': '/contaminants/paint-residue-contamination'}
                ]
            }
        """
        from .validation_schema import ValidationSchema
        
        relationships = {}
        
        for rel_type, ref_ids in relationship_spec.items():
            # Get target domain
            target_domain = ValidationSchema.get_target_domain(rel_type)
            
            if not target_domain:
                # Unknown relationship type, keep as-is
                relationships[rel_type] = ref_ids
                continue
            
            # Get formatted links
            links = self.get_links_batch(target_domain, ref_ids, skip_invalid=True)
            relationships[rel_type] = links
        
        return relationships
    
    def reload(self):
        """Reload all data from disk"""
        self.index.clear()
        self.metadata.clear()
        self._loaded = False
        self.load_all()
