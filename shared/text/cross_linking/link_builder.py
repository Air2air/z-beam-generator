"""
Cross-Link Builder

Adds sparse, contextual cross-links to generated text.
Follows strict rules: maximum 1-2 links per 150 words, natural placement only.

Purpose: Connect related content without turning text into a navigation menu.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml

logger = logging.getLogger(__name__)


class CrossLinkBuilder:
    """
    Add sparse cross-links to generated text.
    
    Rules:
    - Maximum 1-2 links per 150 words
    - Natural placement (term must appear in text)
    - No circular references
    - Domain-aware paths
    
    Usage:
        builder = CrossLinkBuilder()
        linked_text = builder.add_links(
            content="Steel requires higher power...",
            current_item="Steel",
            domain="materials"
        )
    """
    
    def __init__(self):
        """Initialize with data paths."""
        self.materials_path = Path("data/materials/Materials.yaml")
        self.contaminants_path = Path("data/contaminants/Contaminants.yaml")
        
        # Lazy-load caches
        self._materials_cache = None
        self._contaminants_cache = None
        
        # Max links per word count
        self.max_links_per_150_words = 2
    
    def _load_materials(self) -> Dict:
        """Load Materials.yaml (cached)."""
        if self._materials_cache is None:
            if self.materials_path.exists():
                with open(self.materials_path, 'r', encoding='utf-8') as f:
                    self._materials_cache = yaml.safe_load(f)
            else:
                self._materials_cache = {'materials': {}}
        return self._materials_cache
    
    def _load_contaminants(self) -> Dict:
        """Load Contaminants.yaml (cached)."""
        if self._contaminants_cache is None:
            if self.contaminants_path.exists():
                with open(self.contaminants_path, 'r', encoding='utf-8') as f:
                    self._contaminants_cache = yaml.safe_load(f)
            else:
                self._contaminants_cache = {'contamination_patterns': {}}
        return self._contaminants_cache
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())
    
    def _calculate_max_links(self, text: str) -> int:
        """Calculate maximum allowed links based on word count."""
        word_count = self._count_words(text)
        # 2 links per 150 words
        return max(1, int((word_count / 150) * self.max_links_per_150_words))
    
    def _find_material_mentions(self, text: str, exclude: str = None) -> List[Tuple[str, int]]:
        """
        Find material names mentioned in text.
        
        Args:
            text: Content to search
            exclude: Current item to exclude
            
        Returns:
            List of (material_name, first_position) tuples
        """
        materials = self._load_materials().get('materials', {})
        mentions = []
        
        for material_name in materials.keys():
            if exclude and material_name.lower() == exclude.lower():
                continue
            
            # Case-insensitive search for material name
            pattern = re.compile(r'\b' + re.escape(material_name) + r'\b', re.IGNORECASE)
            match = pattern.search(text)
            
            if match:
                mentions.append((material_name, match.start()))
        
        # Sort by first occurrence
        mentions.sort(key=lambda x: x[1])
        return mentions
    
    def _find_contaminant_mentions(self, text: str, exclude: str = None) -> List[Tuple[str, str, int]]:
        """
        Find contaminant names mentioned in text.
        
        Args:
            text: Content to search
            exclude: Current item to exclude
            
        Returns:
            List of (contaminant_name, pattern_id, first_position) tuples
        """
        contaminants = self._load_contaminants().get('contamination_patterns', {})
        mentions = []
        
        for pattern_id, pattern_data in contaminants.items():
            pattern_name = pattern_data.get('name', '')
            
            if exclude and pattern_name.lower() == exclude.lower():
                continue
            
            # Search for contaminant name
            pattern = re.compile(r'\b' + re.escape(pattern_name) + r'\b', re.IGNORECASE)
            match = pattern.search(text)
            
            if match:
                mentions.append((pattern_name, pattern_id, match.start()))
        
        # Sort by first occurrence
        mentions.sort(key=lambda x: x[2])
        return mentions
    
    def _make_slug(self, name: str) -> str:
        """Convert name to URL-friendly slug."""
        return name.lower().replace(' ', '-').replace('(', '').replace(')', '')
    
    def add_links(
        self,
        content: str,
        current_item: str,
        domain: str,
        related_items: List[str] = None
    ) -> str:
        """
        Add sparse cross-links to content.
        
        Args:
            content: Generated text
            current_item: Current material/contaminant/setting (to exclude)
            domain: Current domain (materials/contaminants/settings)
            related_items: Optional list of items to prioritize for linking
            
        Returns:
            Content with markdown links added
            
        Rules:
            - Maximum 1-2 links per 150 words
            - Natural placement (term must exist in text)
            - Link first occurrence only
            - No circular references (no linking to current_item)
        """
        max_links = self._calculate_max_links(content)
        
        if max_links == 0:
            logger.debug(f"Text too short for cross-linking ({self._count_words(content)} words)")
            return content
        
        logger.info(f"Adding up to {max_links} cross-links to {self._count_words(content)}-word text")
        
        links_added = 0
        modified_content = content
        
        # Track what we've already linked to avoid duplicates
        linked_items: Set[str] = set()
        
        # Find material mentions (allow all domains, exclude current item only)
        material_mentions = self._find_material_mentions(content, exclude=current_item)
        
        for material_name, position in material_mentions[:max_links]:
            if links_added >= max_links:
                break
            
            if material_name in linked_items:
                continue
            
            # Create link
            slug = self._make_slug(material_name)
            link_path = f"../materials/{slug}.md"
            
            # Replace first occurrence only
            pattern = re.compile(r'\b' + re.escape(material_name) + r'\b', re.IGNORECASE)
            modified_content = pattern.sub(f"[{material_name}]({link_path})", modified_content, count=1)
            
            linked_items.add(material_name)
            links_added += 1
            logger.debug(f"Added link: {material_name} → {link_path}")
        
        # Find contaminant mentions (allow all domains, exclude current item only)
        if links_added < max_links:
            contaminant_mentions = self._find_contaminant_mentions(content, exclude=current_item)
            
            for contaminant_name, pattern_id, position in contaminant_mentions:
                if links_added >= max_links:
                    break
                
                if contaminant_name in linked_items:
                    continue
                
                # Create link only if contaminant_name is valid
                if not contaminant_name or not contaminant_name.strip():
                    continue
                    
                # Use pattern_id with -contamination suffix to match frontmatter slugs
                # Frontmatter: adhesive-residue-contamination.yaml has slug: adhesive-residue-contamination
                link_path = f"../contaminants/{pattern_id}-contamination.md"
                
                # Replace first occurrence only
                pattern = re.compile(r'\b' + re.escape(contaminant_name) + r'\b', re.IGNORECASE)
                modified_content = pattern.sub(f"[{contaminant_name}]({link_path})", modified_content, count=1)
                
                linked_items.add(contaminant_name)
                links_added += 1
                logger.debug(f"Added link: {contaminant_name} → {link_path}")
        
        logger.info(f"Cross-linking complete: {links_added} links added")
        return modified_content
