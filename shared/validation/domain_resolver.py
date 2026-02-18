"""
Domain Data Resolver

Lightweight helper to fetch link information from source data files.
Each generator uses this to get correct URLs, titles, and IDs from other domains.

Usage:
    from shared.validation.domain_resolver import DomainResolver
    
    resolver = DomainResolver()
    
    # Get link info for a contaminant
    link_info = resolver.get_link_info('contaminants', 'rust-contamination')
    # Returns: {
    #   'id': 'rust-contamination',
    #   'name': 'Rust / Iron Oxide',
    #   'url': '/contaminants/oxidation/rust-contamination',
    #   'title': 'Rust / Iron Oxide Contamination',
    #   'exists': True
    # }
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class LinkInfo:
    """Complete link information for a domain item"""
    id: str
    name: str
    url: str
    title: str
    exists: bool
    category: str = ''
    image: str = ''

class DomainResolver:
    """Resolves link information from domain source files"""
    
    DATA_FILES = {
        'materials': 'data/materials/Materials.yaml',
        'contaminants': 'data/contaminants/contaminants.yaml',
        'compounds': 'data/compounds/Compounds.yaml',
        'settings': 'data/settings/Settings.yaml',
        'applications': 'data/applications/Applications.yaml',
    }
    
    DOMAIN_KEYS = {
        'materials': 'materials',
        'contaminants': 'contamination_patterns',
        'compounds': 'compounds',
        'settings': 'settings',
        'applications': 'applications',
    }
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or self._find_project_root()
        self._cache = {}
    
    def _find_project_root(self) -> Path:
        """Find project root from current file location"""
        current = Path(__file__).resolve()
        return current.parent.parent.parent
    
    def _load_domain(self, domain: str) -> Dict:
        """Load domain data from file"""
        if domain in self._cache:
            return self._cache[domain]
        
        file_path = self.DATA_FILES.get(domain)
        if not file_path:
            return {}
        
        full_path = self.project_root / file_path
        if not full_path.exists():
            return {}
        
        try:
            with open(full_path, 'r') as f:
                content = yaml.safe_load(f)
            
            # Get items based on domain structure
            root_key = self.DOMAIN_KEYS.get(domain)
            if root_key and root_key in content:
                items = content[root_key]
            else:
                items = content
            
            self._cache[domain] = items if isinstance(items, dict) else {}
            return self._cache[domain]
            
        except Exception as e:
            print(f"⚠️  Error loading {domain}: {e}")
            return {}
    
    def get_link_info(self, domain: str, item_id: str) -> LinkInfo:
        """
        Get complete link information for an item
        
        Args:
            domain: Target domain (materials, contaminants, compounds, settings)
            item_id: Item ID to look up
            
        Returns:
            LinkInfo with all necessary link data
        """
        items = self._load_domain(domain)
        
        if item_id not in items:
            return LinkInfo(
                id=item_id,
                name=item_id,
                url=f'/{domain}/{item_id}',
                title=item_id,
                exists=False
            )
        
        item = items[item_id]
        
        # Build URL (handle different domain structures)
        url = self._build_url(domain, item_id, item)
        
        return LinkInfo(
            id=item_id,
            name=item.get('name', item_id),
            url=url,
            title=item.get('title', item.get('name', item_id)),
            exists=True,
            category=item.get('category', ''),
            image=self._get_image_url(item)
        )
    
    def _build_url(self, domain: str, item_id: str, item: Dict) -> str:
        """Build URL for an item"""
        # Check if item has explicit URL
        if 'url' in item:
            return item['url']
        
        # Build URL based on domain and category
        category = item.get('category', '')
        subcategory = item.get('subcategory', '')
        
        if domain == 'contaminants':
            # /contaminants/category/subcategory/id
            if subcategory:
                return f'/contaminants/{category}/{subcategory}/{item_id}'
            elif category:
                return f'/contaminants/{category}/{item_id}'
        elif domain == 'materials':
            # /materials/category/id
            if category:
                return f'/materials/{category}/{item_id}'
        elif domain == 'compounds':
            # /compounds/category/id
            if category:
                return f'/compounds/{category}/{item_id}'
        elif domain == 'settings':
            # /settings/laser-type/id
            laser_type = item.get('laser_type', '')
            if laser_type:
                return f'/settings/{laser_type}/{item_id}'
        elif domain == 'applications':
            # /applications/id
            return f'/applications/{item_id}'
        
        # Fallback
        return f'/{domain}/{item_id}'
    
    def _get_image_url(self, item: Dict) -> str:
        """Get primary image URL from item"""
        # Check for images dict
        if 'images' in item and isinstance(item['images'], dict):
            # Try hero first
            if 'hero' in item['images']:
                hero = item['images']['hero']
                if isinstance(hero, dict) and 'url' in hero:
                    return hero['url']
                elif isinstance(hero, str):
                    return hero
            # Try first available
            for img in item['images'].values():
                if isinstance(img, dict) and 'url' in img:
                    return img['url']
                elif isinstance(img, str):
                    return img
        
        # Check for direct image field
        if 'image' in item:
            return item['image']
        
        return ''
    
    def get_relationship_links(self, domain: str, item_id: str, 
                              relationship_field: str) -> List[LinkInfo]:
        """
        Get all link info for a relationship field
        
        Args:
            domain: Source domain
            item_id: Source item ID
            relationship_field: Field name (e.g., 'related_contaminants')
            
        Returns:
            List of LinkInfo for all related items
        """
        items = self._load_domain(domain)
        
        if item_id not in items:
            return []
        
        item = items[item_id]
        
        # Get relationships
        if 'relationships' not in item:
            return []
        
        relationships = item['relationships']
        if relationship_field not in relationships:
            return []
        
        refs = relationships[relationship_field]
        if not isinstance(refs, list):
            return []
        
        # Determine target domain from field name
        target_domain = self._get_target_domain(relationship_field)
        if not target_domain:
            return []
        
        # Get link info for each reference
        link_infos = []
        for ref in refs:
            if isinstance(ref, dict) and 'id' in ref:
                ref_id = ref['id']
                link_info = self.get_link_info(target_domain, ref_id)
                link_infos.append(link_info)
        
        return link_infos
    
    def _get_target_domain(self, relationship_field: str) -> Optional[str]:
        """Map relationship field to target domain"""
        mapping = {
            'related_contaminants': 'contaminants',
            'related_compounds': 'compounds',
            'related_settings': 'settings',
            'related_materials': 'materials',
            'produces_compounds': 'compounds',
            'produced_by_contaminants': 'contaminants',
            'recommended_settings': 'settings',
            'suitable_materials': 'materials',
            'effective_contaminants': 'contaminants',
        }
        return mapping.get(relationship_field)
    
    def validate_reference(self, domain: str, item_id: str) -> bool:
        """Check if a reference exists"""
        items = self._load_domain(domain)
        return item_id in items
    
    def clear_cache(self):
        """Clear cached domain data"""
        self._cache.clear()
