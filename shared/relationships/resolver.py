"""
Relationship Resolver - Derives full relationship objects from page data

ARCHITECTURE:
A relationship entry is a subset of a page entry. Instead of duplicating
page data (title, url, category) in relationship arrays, we store only:
  1. Reference (id)
  2. Context-specific fields (frequency, severity, typical_context)

This resolver hydrates relationship references with full page data at runtime.

BENEFITS:
- Single source of truth (page data)
- No duplication
- Automatic propagation of changes
- Smaller YAML files
- Impossible to have stale relationship data
"""

import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path


class RelationshipResolver:
    """Resolves relationship IDs to full relationship objects using page data."""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
        self._domain_data_cache = {}
        
    def _load_domain_data(self, domain: str) -> Dict[str, Any]:
        """Load and cache domain data file."""
        if domain in self._domain_data_cache:
            return self._domain_data_cache[domain]
            
        # Map domain to file and key
        domain_map = {
            'materials': ('materials/Materials.yaml', 'materials'),
            'contaminants': ('contaminants/Contaminants.yaml', 'contamination_patterns'),
            'compounds': ('compounds/Compounds.yaml', 'compounds'),
            'settings': ('settings/Settings.yaml', 'settings'),
            'applications': ('applications/Applications.yaml', 'applications')
        }
        
        if domain not in domain_map:
            raise ValueError(f"Unknown domain: {domain}")
            
        file_path, data_key = domain_map[domain]
        full_path = self.data_dir / file_path
        
        with open(full_path) as f:
            data = yaml.safe_load(f)
            
        self._domain_data_cache[domain] = data[data_key]
        return data[data_key]
        
    def resolve_relationship(
        self, 
        ref: Dict[str, Any], 
        target_domain: str
    ) -> Dict[str, Any]:
        """
        Resolve a relationship reference to a full relationship object.
        
        Args:
            ref: Relationship reference (id + context fields)
            target_domain: Domain of the referenced item
            
        Returns:
            Complete relationship object with page data + context
        """
        # Get the reference ID
        ref_id = ref.get('id')
        if not ref_id:
            raise ValueError("Relationship reference missing 'id' field")
            
        # Load target domain data
        domain_data = self._load_domain_data(target_domain)
        
        # Find the referenced page
        if ref_id not in domain_data:
            raise ValueError(f"Referenced {target_domain} '{ref_id}' not found")
            
        page = domain_data[ref_id]
        
        # Extract core fields from page data
        relationship = {
            'id': ref_id,
            'title': self._get_title(page),
            'url': page.get('full_path', f'/{target_domain}/{ref_id}'),
            'category': page.get('category', 'unknown'),
            'subcategory': page.get('subcategory', 'unknown')
        }
        
        # Add image if available
        image = self._get_image(page)
        if image:
            relationship['image'] = image
            
        # Merge context-specific fields from reference
        context_fields = ['frequency', 'severity', 'typical_context', 'notes']
        for field in context_fields:
            if field in ref:
                relationship[field] = ref[field]
                
        return relationship
        
    def resolve_relationships(
        self, 
        refs: List[Dict[str, Any]], 
        target_domain: str
    ) -> List[Dict[str, Any]]:
        """Resolve a list of relationship references."""
        return [self.resolve_relationship(ref, target_domain) for ref in refs]
        
    def _get_title(self, page: Dict[str, Any]) -> str:
        """Extract title from page data (handles different field names)."""
        return (page.get('displayName') or
            page.get('display_name') or 
            page.get('pageTitle') or
                page.get('title') or 
                page.get('name') or 
                'Unknown')
                
    def _get_image(self, page: Dict[str, Any]) -> Optional[str]:
        """Extract image from page data (handles different structures)."""
        # Check visual_characteristics.image
        visual = page.get('visual_characteristics', {})
        if isinstance(visual, dict) and 'image' in visual:
            return visual['image']
            
        # Check images array
        images = page.get('images', [])
        if isinstance(images, dict):
            hero = images.get('hero')
            if isinstance(hero, dict):
                return hero.get('url')
            if isinstance(hero, str):
                return hero
        if images and len(images) > 0:
            return images[0] if isinstance(images[0], str) else images[0].get('src')
            
        # Check direct image field
        if 'image' in page:
            return page['image']
            
        return None


class RelationshipNormalizer:
    """Normalizes existing full relationship objects to reference-only format."""
    
    @staticmethod
    def normalize_relationship(
        full_rel: Dict[str, Any], 
        keep_fields: List[str] = None
    ) -> Dict[str, Any]:
        """
        Convert a full relationship object to reference + context format.
        
        Args:
            full_rel: Full relationship object with duplicated page data
            keep_fields: Context-specific fields to preserve (default: frequency, severity, typical_context)
            
        Returns:
            Normalized relationship reference
        """
        if keep_fields is None:
            keep_fields = ['frequency', 'severity', 'typical_context', 'notes']
            
        # Always keep ID
        normalized = {'id': full_rel['id']}
        
        # Keep context-specific fields
        for field in keep_fields:
            if field in full_rel:
                normalized[field] = full_rel[field]
                
        return normalized
        
    @staticmethod
    def normalize_relationships(
        full_rels: List[Dict[str, Any]], 
        keep_fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Normalize a list of full relationship objects."""
        return [
            RelationshipNormalizer.normalize_relationship(rel, keep_fields) 
            for rel in full_rels
        ]


# Example usage
if __name__ == '__main__':
    # Initialize resolver
    resolver = RelationshipResolver()
    
    # Example: Resolve a minimal reference to full relationship object
    minimal_ref = {
        'id': 'adhesive-residue-contamination',
        'frequency': 'very_common',
        'severity': 'high',
        'typical_context': 'Industrial applications'
    }
    
    full_relationship = resolver.resolve_relationship(minimal_ref, 'contaminants')
    
    print("Minimal reference:")
    print(f"  {minimal_ref}")
    print("\nResolved to full relationship:")
    print(f"  {full_relationship}")
    
    # Example: Normalize existing full relationship to reference
    existing_full = {
        'id': 'rust',
        'title': 'Metal Oxidation / Rust',  # DUPLICATE
        'url': '/contaminants/metal-oxide/rust',  # DUPLICATE
        'category': 'metal-oxide',  # DUPLICATE
        'subcategory': 'oxidation',  # DUPLICATE
        'frequency': 'very_common'  # CONTEXT
    }
    
    normalized = RelationshipNormalizer.normalize_relationship(existing_full)
    
    print("\n" + "="*80)
    print("Existing full relationship:")
    print(f"  {existing_full}")
    print("\nNormalized to reference:")
    print(f"  {normalized}")
