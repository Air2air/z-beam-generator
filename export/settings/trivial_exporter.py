#!/usr/bin/env python3
"""
Trivial Settings Frontmatter Exporter

PURPOSE: Export Settings.yaml data to frontmatter YAML files.
DESIGN: Simple YAML-to-YAML copy - NO API, NO validation.

OPERATIONS:
1. Copy settings-specific data from Settings.yaml
2. Enrich with author data from registry
3. Write to frontmatter YAML file

All complex operations (AI generation, validation, quality scoring)
happen on Settings.yaml ONLY. This exporter just copies the complete data.

Performance: Should take SECONDS for all settings, not minutes.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any
from collections import OrderedDict

from export.core.base_trivial_exporter import BaseTrivialExporter

logger = logging.getLogger(__name__)


class TrivialSettingsExporter(BaseTrivialExporter):
    """
    Trivial exporter: Copy Settings.yaml → Frontmatter YAML files.
    
    NO API CLIENT REQUIRED.
    NO VALIDATION REQUIRED (already validated in Settings.yaml).
    NO COMPLETENESS CHECKS REQUIRED (already complete in Settings.yaml).
    NO QUALITY SCORING REQUIRED (already scored in Settings.yaml).
    
    Just simple field mapping and YAML writing.
    """
    
    def __init__(self):
        """Initialize with output directory and load settings data."""
        super().__init__('settings', 'settings')
        
        # Load source data
        self.settings_data = self._load_settings()
        self.materials_data = self._load_materials()  # Need for category/subcategory lookup
        
        self.logger.info(f"✅ Loaded {len(self.settings_data.get('settings', {}))} settings profiles")
    
    def _load_domain_data(self) -> Dict[str, Any]:
        """
        Abstract method implementation: Return settings data for base class.
        
        Returns:
            Dict containing settings and metadata
        """
        return self.settings_data
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load Settings.yaml."""
        settings_path = Path(__file__).resolve().parents[2] / "data" / "settings" / "Settings.yaml"
        
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data or {}
        except Exception as e:
            self.logger.error(f"❌ Failed to load Settings.yaml: {e}")
            return {}
    
    def _load_materials(self) -> Dict[str, Any]:
        """Load Materials.yaml for category/subcategory lookup."""
        materials_path = Path(__file__).resolve().parents[2] / "data" / "materials" / "Materials.yaml"
        
        try:
            with open(materials_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data or {}
        except Exception as e:
            self.logger.error(f"❌ Failed to load Materials.yaml: {e}")
            return {}
    
    def _create_slug(self, material_name: str) -> str:
        """
        Create URL-friendly slug from material name.
        
        MANDATORY SUFFIX: All settings slugs MUST end with '-settings'
        for SEO clarity and URL structure consistency.
        
        Examples:
        - "Aluminum" → "aluminum-settings"
        - "Stainless Steel 316" → "stainless-steel-316-settings"
        """
        # Normalize: lowercase, replace spaces with hyphens
        slug = material_name.lower().replace(' ', '-')
        slug = slug.replace('(', '').replace(')', '')
        # Remove consecutive hyphens
        while '--' in slug:
            slug = slug.replace('--', '-')
        slug = slug.strip('-')
        
        # Add mandatory suffix
        if not slug.endswith('-settings'):
            slug = f"{slug}-settings"
        
        return slug
    
    def _convert_to_plain_dict(self, data):
        """
        Recursively convert OrderedDict to plain dict for clean YAML serialization.
        
        Prevents Python-specific !!python/object tags in output YAML.
        """
        if isinstance(data, OrderedDict) or isinstance(data, dict):
            return {k: self._convert_to_plain_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_plain_dict(item) for item in data]
        else:
            return data
    
    # DEPRECATED: Replaced by centralized DomainLinkagesService
    # def _generate_domain_linkages(self, material_name: str) -> Dict[str, Any]:
    #     """
    #     OLD METHOD - Now using shared/services/domain_linkages_service.py
    #     
    #     This method has been replaced by DomainLinkagesService.generate_linkages()
    #     for consistency across all exporters.
    #     """
    #     pass
    
    def export_all(self, force: bool = True) -> Dict[str, bool]:
        """
        Export all settings to frontmatter YAML files.
        
        Args:
            force: Overwrite existing files
            
        Returns:
            Dict mapping material names to success status
        """
        self.logger.info("🚀 Starting settings frontmatter export (no API, no validation)")
        
        settings = self.settings_data.get('settings', {})
        results = {}
        
        for material_name, setting_data in settings.items():
            try:
                success = self.export_single(material_name, setting_data, force=force)
                results[material_name] = success
            except Exception as e:
                self.logger.error(f"❌ Export failed for {material_name}: {e}")
                results[material_name] = False
        
        success_count = sum(1 for v in results.values() if v)
        self.logger.info(f"✅ Exported {success_count}/{len(results)} settings")
        
        return results
    
    def export_single(self, material_name: str, setting_data: Dict, force: bool = False) -> bool:
        """
        Export single settings profile to frontmatter YAML.
        
        Args:
            material_name: Material name (key in Settings.yaml)
            setting_data: Settings data from Settings.yaml
            force: Overwrite existing file
            
        Returns:
            True if exported successfully
        """
        # Create slug and filename
        slug = self._create_slug(material_name)
        output_file = self.output_dir / f"{slug}.yaml"
        
        if output_file.exists() and not force:
            self.logger.debug(f"Skipping existing file: {output_file}")
            return False
        
        # Build frontmatter
        frontmatter = OrderedDict()
        
        # Basic fields (id, name, slug per schema)
        frontmatter['id'] = slug  # id matches filename/slug
        frontmatter['name'] = material_name
        frontmatter['slug'] = slug
        frontmatter['domain'] = 'settings'
        
        # Lookup category/subcategory from Materials.yaml
        # Convert material_name to materials key format (e.g., "Aluminum" → "aluminum-laser-cleaning")
        material_key = material_name.lower().replace(' ', '-') + '-laser-cleaning'
        materials = self.materials_data.get('materials', {})
        if material_key in materials:
            material_data = materials[material_key]
            frontmatter['category'] = material_data.get('category', 'unknown')
            frontmatter['subcategory'] = material_data.get('subcategory', 'unknown')
        else:
            # Fallback if material not found
            self.logger.warning(f"⚠️ Material {material_name} not found in Materials.yaml, using defaults")
            frontmatter['category'] = 'unknown'
            frontmatter['subcategory'] = 'unknown'
        
        # Add required schema fields per FRONTMATTER_GENERATION_GUIDE_V2.md
        frontmatter['content_type'] = 'unified_settings'
        frontmatter['schema_version'] = '4.0.0'
        
        # Add ISO 8601 timestamps if missing (Schema.org requirement)
        current_timestamp = self.generate_timestamp()
        if 'datePublished' not in frontmatter or not frontmatter['datePublished']:
            frontmatter['datePublished'] = current_timestamp
        if 'dateModified' not in frontmatter or not frontmatter['dateModified']:
            frontmatter['dateModified'] = current_timestamp
        
        # Copy machine settings
        if 'machineSettings' in setting_data:
            frontmatter['machineSettings'] = self.strip_generation_metadata(setting_data['machineSettings'])
        
        # Copy settings description
        if 'settingsDescription' in setting_data:
            frontmatter['settingsDescription'] = setting_data['settingsDescription']
        
        # Copy challenges if present
        if 'challenges' in setting_data:
            frontmatter['challenges'] = self.strip_generation_metadata(setting_data['challenges'])
        
        # Copy author if present
        if 'author' in setting_data:
            frontmatter['author'] = setting_data['author']
        
        # Add breadcrumb navigation
        frontmatter['breadcrumb'] = [
            {'label': 'Home', 'href': '/'},
            {'label': 'Laser Settings', 'href': '/settings'},
            {'label': material_name, 'href': f'/settings/{slug}'}
        ]
        
        # Generate domain_linkages from centralized associations
        material_slug = material_name.lower().replace(' ', '-')
        domain_linkages = self.linkages_service.generate_linkages(material_slug, 'settings')
        if domain_linkages:
            frontmatter['domain_linkages'] = domain_linkages
        
        # Write to file using base class method (handles field ordering + YAML writing)
        filename = f"{slug}.yaml"
        # Convert to plain dict before writing
        plain_frontmatter = self._convert_to_plain_dict(frontmatter)
        self.write_frontmatter_yaml(plain_frontmatter, filename)
        
        self.logger.info(f"✅ Exported settings: {material_name} → {slug}.yaml")
        return True


def main():
    """CLI entry point for settings export."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export Settings.yaml to frontmatter YAML files")
    parser.add_argument('--force', action='store_true', help="Overwrite existing files")
    args = parser.parse_args()
    
    print("=" * 80)
    print("TRIVIAL SETTINGS FRONTMATTER EXPORTER")
    print("=" * 80)
    print()
    print("Design: Simple export, no API calls, no validation")
    print()
    
    exporter = TrivialSettingsExporter()
    results = exporter.export_all(force=args.force)
    
    success_count = sum(1 for v in results.values() if v)
    print()
    print(f"✅ Successfully exported {success_count}/{len(results)} settings profiles")


if __name__ == "__main__":
    main()
