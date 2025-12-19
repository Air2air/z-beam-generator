#!/usr/bin/env python3
"""
Base Trivial Exporter

Abstract base class for all domain-specific trivial exporters.
Consolidates common initialization, validators, and utility methods.

PURPOSE: 
- Eliminate code duplication across 4 domain exporters
- Centralize validator initialization
- Standardize timestamp generation
- Share field ordering logic

USAGE:
    class TrivialMaterialsExporter(BaseTrivialExporter):
        def __init__(self):
            super().__init__(
                domain_name='materials',
                output_subdir='materials'
            )
            # Domain-specific loading
            self.materials_data = self._load_materials()
        
        def _load_domain_data(self) -> Dict[str, Any]:
            # Implement domain-specific loading
            pass
        
        def export_single(self, item_id: str, item_data: Dict, force: bool = False) -> bool:
            # Implement domain-specific export logic
            pass
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml

from shared.services.relationships_service import DomainLinkagesService
from shared.validation.domain_associations import DomainAssociationsValidator
from shared.validation.field_order import FrontmatterFieldOrderValidator


class BaseTrivialExporter(ABC):
    """
    Abstract base class for trivial YAML-to-YAML exporters.
    
    Provides:
    - Common validator initialization (DomainAssociationsValidator, FrontmatterFieldOrderValidator, DomainLinkagesService)
    - Centralized timestamp generation (ISO 8601)
    - Field ordering utility
    - Logging setup
    - Output directory management
    
    Subclasses must implement:
    - _load_domain_data(): Load domain-specific YAML
    - export_single(): Export single item
    - export_all(): Export all items (optional, default implementation provided)
    """
    
    def __init__(self, domain_name: str, output_subdir: str):
        """
        Initialize base exporter with common services.
        
        Args:
            domain_name: Domain identifier (materials, settings, contaminants, compounds)
            output_subdir: Subdirectory under frontmatter/ (usually same as domain_name)
        """
        self.domain_name = domain_name
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Setup output directory
        self.output_dir = Path(__file__).resolve().parents[2] / "frontmatter" / output_subdir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"✅ Output directory: {self.output_dir}")
        
        # Initialize centralized validators (SHARED ACROSS ALL DOMAINS)
        self._init_validators()
        
        self.logger.info(f"✅ Initialized {domain_name} exporter with shared validators")
    
    def _init_validators(self):
        """Initialize shared validation services (called by __init__)."""
        # Domain associations validator
        self.associations_validator = DomainAssociationsValidator()
        self.associations_validator.load()
        
        # Field order validator
        self.field_order_validator = FrontmatterFieldOrderValidator()
        self.field_order_validator.load_schema()
        
        # Domain linkages service
        self.linkages_service = DomainLinkagesService()
        
        self.logger.info("✅ Validators initialized: DomainAssociationsValidator, FrontmatterFieldOrderValidator, DomainLinkagesService")
    
    # ====================
    # SHARED UTILITIES
    # ====================
    
    def generate_timestamp(self) -> str:
        """
        Generate ISO 8601 timestamp for datePublished/dateModified fields.
        
        Returns:
            ISO 8601 timestamp string (e.g., '2025-12-16T16:14:32.123456')
        
        Usage:
            timestamp = self.generate_timestamp()
            frontmatter['datePublished'] = data.get('datePublished') or timestamp
            frontmatter['dateModified'] = data.get('dateModified') or timestamp
        """
        return datetime.now().isoformat()
    
    def enrich_author_data(self, author_id: str) -> Dict[str, Any]:
        """
        Load full author data from Authors.yaml.
        
        Args:
            author_id: Author identifier (e.g., 'todd-dunning')
        
        Returns:
            Full author dictionary with name, country, bio, etc.
        
        Raises:
            ValueError: If author not found
        
        Usage:
            author_data = self.enrich_author_data(author_id)
            frontmatter['author'] = author_data
        """
        from shared.data.author_loader import get_author
        author_data = get_author(author_id)
        if not author_data:
            raise ValueError(f"Author not found: {author_id}")
        return author_data
    
    def apply_field_order(self, frontmatter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply canonical field ordering per domain schema.
        
        Args:
            frontmatter: Unordered frontmatter dictionary
        
        Returns:
            Ordered frontmatter dictionary per FrontmatterFieldOrder.yaml
        
        Usage:
            ordered = self.apply_field_order(frontmatter)
            yaml.dump(ordered, ...)
        """
        return self.field_order_validator.reorder_fields(frontmatter, self.domain_name)
    
    def strip_generation_metadata(self, data: Any) -> Any:
        """
        Remove generation metadata fields from data structure.
        
        Strips: generated, word_count, character_count, question_count, etc.
        
        Args:
            data: Data to clean (dict, list, or primitive)
        
        Returns:
            Cleaned data with generation metadata removed
        """
        METADATA_FIELDS = {
            'generated', 'word_count', 'word_count_before', 'word_count_after',
            'total_words', 'question_count', 'character_count',
            'author', 'generation_method'  # Redundant fields
        }
        
        if isinstance(data, dict):
            return {
                k: self.strip_generation_metadata(v)
                for k, v in data.items()
                if k not in METADATA_FIELDS
            }
        elif isinstance(data, list):
            return [self.strip_generation_metadata(item) for item in data]
        else:
            return data
    
    def write_frontmatter_yaml(
        self,
        frontmatter: Dict[str, Any],
        filename: str,
        apply_ordering: bool = True
    ):
        """
        Write frontmatter dictionary to YAML file.
        
        Args:
            frontmatter: Data to write
            filename: Output filename (e.g., 'aluminum-laser-cleaning.yaml')
            apply_ordering: Whether to apply field ordering (default: True)
        """
        output_path = self.output_dir / filename
        
        # Apply field ordering if requested
        if apply_ordering:
            frontmatter = self.apply_field_order(frontmatter)
        
        # Write with consistent YAML formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                dict(frontmatter),  # Convert OrderedDict to dict if needed
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=1000
            )
        
        self.logger.info(f"✅ Exported: {filename}")
    
    # ====================
    # ABSTRACT METHODS
    # ====================
    
    @abstractmethod
    def _load_domain_data(self) -> Dict[str, Any]:
        """
        Load domain-specific YAML data.
        
        Returns:
            Domain data dictionary (e.g., Materials.yaml, Settings.yaml)
        
        Implementation example:
            def _load_domain_data(self) -> Dict[str, Any]:
                yaml_path = Path(...) / "data" / "materials" / "Materials.yaml"
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        """
        pass
    
    @abstractmethod
    def export_single(self, item_id: str, item_data: Dict, force: bool = False) -> bool:
        """
        Export single item to frontmatter YAML.
        
        Args:
            item_id: Item identifier (material name, setting name, etc.)
            item_data: Item data from source YAML
            force: Overwrite existing file if True
        
        Returns:
            True if export successful, False otherwise
        
        Implementation must:
        1. Build frontmatter dictionary
        2. Add timestamps: self.generate_timestamp()
        3. Apply field ordering: self.apply_field_order()
        4. Write file: self.write_frontmatter_yaml()
        """
        pass
    
    def export_all(self, force: bool = False) -> Dict[str, bool]:
        """
        Export all items in domain.
        
        Default implementation iterates over domain data and calls export_single().
        Override if domain has different structure.
        
        Args:
            force: Overwrite existing files if True
        
        Returns:
            Dictionary mapping item_id -> success status
        """
        results = {}
        domain_data = self._load_domain_data()
        
        # Assume domain data has structure: {domain_name: {item_id: item_data}}
        items = domain_data.get(self.domain_name, {})
        
        self.logger.info(f"Exporting {len(items)} {self.domain_name}...")
        
        for item_id, item_data in items.items():
            try:
                success = self.export_single(item_id, item_data, force=force)
                results[item_id] = success
            except Exception as e:
                self.logger.error(f"❌ Failed to export {item_id}: {e}")
                results[item_id] = False
        
        success_count = sum(1 for v in results.values() if v)
        self.logger.info(f"✅ Exported {success_count}/{len(results)} {self.domain_name}")
        
        return results
