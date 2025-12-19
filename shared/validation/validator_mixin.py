"""
Reference Validator Mixin

Add reference validation capabilities to any generator class.
Integrates with ReferenceRegistry for real-time validation.

Usage:
    from shared.validation.validator_mixin import ReferenceValidatorMixin
    
    class MaterialsGenerator(ReferenceValidatorMixin):
        def __init__(self):
            super().__init__()
            self.init_validator()
        
        def generate(self, material_id):
            # Validate references before saving
            contaminants = [...list of IDs...]
            valid_refs = self.validate_and_fix_references(
                'contaminants', 
                contaminants,
                auto_fix=True
            )
            # Use valid_refs...
"""

from typing import Dict, List, Optional, Set, Tuple

from shared.validation.reference_registry import ReferenceInfo, ReferenceRegistry


class ReferenceValidatorMixin:
    """Mixin to add reference validation to generators"""
    
    def init_validator(self, project_root=None, auto_load: bool = True):
        """
        Initialize the validator
        
        Call this in your generator's __init__
        """
        self._registry = ReferenceRegistry(project_root)
        self._validation_enabled = True
        self._auto_fix = False
        self._validation_stats = {
            'checked': 0,
            'valid': 0,
            'fixed': 0,
            'removed': 0,
        }
        
        if auto_load:
            self._registry.load_all()
    
    def enable_validation(self, enabled: bool = True):
        """Enable or disable validation"""
        self._validation_enabled = enabled
    
    def enable_auto_fix(self, enabled: bool = True):
        """Enable or disable automatic fixing of broken references"""
        self._auto_fix = enabled
    
    def validate_reference(self, domain: str, reference_id: str) -> ReferenceInfo:
        """
        Validate a single reference
        
        Args:
            domain: Target domain (materials, contaminants, etc.)
            reference_id: ID to validate
            
        Returns:
            ReferenceInfo with validation results
        """
        if not self._validation_enabled:
            return ReferenceInfo(domain=domain, id=reference_id, name='', exists=True)
        
        self._validation_stats['checked'] += 1
        info = self._registry.validate_reference(domain, reference_id, auto_fix=self._auto_fix)
        
        if info.exists:
            self._validation_stats['valid'] += 1
        
        return info
    
    def validate_and_fix_references(self, domain: str, reference_ids: List[str],
                                    auto_fix: bool = None,
                                    remove_invalid: bool = True) -> Tuple[List[str], List[ReferenceInfo]]:
        """
        Validate multiple references and optionally fix/remove invalid ones
        
        Args:
            domain: Target domain
            reference_ids: List of IDs to validate
            auto_fix: Override auto_fix setting for this call
            remove_invalid: If True, remove invalid references from list
            
        Returns:
            (valid_ids, invalid_info)
        """
        if not self._validation_enabled:
            return reference_ids, []
        
        use_auto_fix = auto_fix if auto_fix is not None else self._auto_fix
        valid_ids = []
        invalid_info = []
        
        for ref_id in reference_ids:
            info = self.validate_reference(domain, ref_id)
            
            if info.exists:
                valid_ids.append(ref_id)
            elif use_auto_fix and info.suggestions:
                # Use first suggestion
                fixed_id = info.suggestions[0]
                valid_ids.append(fixed_id)
                self._validation_stats['fixed'] += 1
                self._log_fix(domain, ref_id, fixed_id)
            elif not remove_invalid:
                # Keep invalid reference
                valid_ids.append(ref_id)
                invalid_info.append(info)
            else:
                # Remove invalid reference
                invalid_info.append(info)
                self._validation_stats['removed'] += 1
                self._log_removal(domain, ref_id, info.suggestions)
        
        return valid_ids, invalid_info
    
    def validate_relationship_dict(self, relationships: Dict[str, List],
                                   field_to_domain: Dict[str, str],
                                   auto_fix: bool = None) -> Dict[str, List]:
        """
        Validate all references in a relationships dictionary
        
        Args:
            relationships: Dict of relationship_type -> [list of IDs]
            field_to_domain: Map relationship_type to target domain
            auto_fix: Override auto_fix setting
            
        Returns:
            Cleaned relationships dict
        """
        if not self._validation_enabled:
            return relationships
        
        cleaned = {}
        
        for rel_type, ref_ids in relationships.items():
            if rel_type not in field_to_domain:
                cleaned[rel_type] = ref_ids
                continue
            
            domain = field_to_domain[rel_type]
            valid_ids, _ = self.validate_and_fix_references(
                domain, 
                ref_ids,
                auto_fix=auto_fix,
                remove_invalid=True
            )
            cleaned[rel_type] = valid_ids
        
        return cleaned
    
    def get_validation_stats(self) -> Dict[str, int]:
        """Get validation statistics"""
        return self._validation_stats.copy()
    
    def reset_validation_stats(self):
        """Reset validation statistics"""
        self._validation_stats = {
            'checked': 0,
            'valid': 0,
            'fixed': 0,
            'removed': 0,
        }
    
    def _log_fix(self, domain: str, old_id: str, new_id: str):
        """Log a reference fix (override in subclass for custom logging)"""
        print(f"   🔧 Fixed reference: {domain}/{old_id} → {new_id}")
    
    def _log_removal(self, domain: str, ref_id: str, suggestions: List[str]):
        """Log a reference removal (override in subclass for custom logging)"""
        if suggestions:
            print(f"   ⚠️  Removed invalid reference: {domain}/{ref_id} (suggestions: {', '.join(suggestions[:2])})")
        else:
            print(f"   ⚠️  Removed invalid reference: {domain}/{ref_id}")
    
    def reload_registry(self):
        """Reload the reference registry from disk"""
        self._registry.reload()
    
    def get_link_data(self, domain: str, reference_id: str) -> Optional[Dict]:
        """
        Get complete link data for a reference
        
        Returns formatted object ready to use in relationships.
        Handles suffix addition, validation, and URL formatting.
        
        Args:
            domain: Target domain (materials, contaminants, etc.)
            reference_id: ID to get link for (suffix optional)
            
        Returns:
            {'id': '...', 'title': '...', 'url': '...'} or None
            
        Example:
            >>> link = self.get_link_data('contaminants', 'rust')
            >>> # Returns: {'id': 'rust-contamination', 'title': 'Rust', 'url': '/contaminants/rust-contamination'}
        """
        return self._registry.get_link_data(domain, reference_id)
    
    def build_relationships(self, relationship_spec: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
        """
        Build complete relationships from simple ID lists
        
        Converts:
            {'related_contaminants': ['rust', 'paint']}
        To:
            {'related_contaminants': [
                {'id': 'rust-contamination', 'title': 'Rust', 'url': '/contaminants/rust-contamination'},
                {'id': 'paint-contamination', 'title': 'Paint', 'url': '/contaminants/paint-contamination'}
            ]}
        
        Args:
            relationship_spec: Dict of {relationship_type: [id1, id2, ...]}
            
        Returns:
            Dict of {relationship_type: [{id, title, url}, ...]}
        """
        # Note: We don't need source_domain since ValidationSchema maps rel_type to target_domain
        return self._registry.build_relationships(None, relationship_spec)
