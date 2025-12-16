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

from shared.validation.domain_associations import DomainAssociationsValidator
from shared.validation.field_order import FrontmatterFieldOrderValidator

logger = logging.getLogger(__name__)


class TrivialSettingsExporter:
    """
    Trivial exporter: Copy Settings.yaml → Frontmatter YAML files.
    
    NO API CLIENT REQUIRED.
    NO VALIDATION REQUIRED (already validated in Settings.yaml).
    NO COMPLETENESS CHECKS REQUIRED (already complete in Settings.yaml).
    NO QUALITY SCORING REQUIRED (already scored in Settings.yaml).
    
    Just simple field mapping and YAML writing.
    """
    
    def __init__(self):
        """Initialize with output directory."""
        self.output_dir = Path(__file__).resolve().parents[2] / "frontmatter" / "settings"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Load source data
        self.settings_data = self._load_settings()
        
        # Initialize validators for centralized systems
        self.associations_validator = DomainAssociationsValidator()
        self.associations_validator.load()
        self.field_order_validator = FrontmatterFieldOrderValidator()
        self.field_order_validator.load_schema()
        
        self.logger.info(f"✅ Loaded {len(self.settings_data.get('settings', {}))} settings profiles")
    
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
    
    def _strip_generation_metadata(self, data: Dict) -> Dict:
        """
        Remove generation metadata fields from data.
        
        Removes: _generated_at, _generation_id, _model, _temperature, etc.
        Keeps: Core data fields needed for frontmatter
        """
        if not isinstance(data, dict):
            return data
        
        cleaned = OrderedDict()
        for key, value in data.items():
            # Skip generation metadata
            if key.startswith('_generated') or key.startswith('_model') or key.startswith('_temperature'):
                continue
            
            # Recursively clean nested dicts
            if isinstance(value, dict):
                cleaned[key] = self._strip_generation_metadata(value)
            elif isinstance(value, list):
                cleaned[key] = [self._strip_generation_metadata(item) if isinstance(item, dict) else item 
                               for item in value]
            else:
                cleaned[key] = value
        
        return cleaned
    
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
    
    def _generate_domain_linkages(self, material_name: str) -> Dict[str, Any]:
        """
        Generate domain_linkages from centralized associations.
        
        Reads from DomainAssociations.yaml and generates bidirectional linkages.
        """
        linkages = OrderedDict()
        
        # Get material associations (settings are linked to same materials as the material page)
        material_slug = material_name.lower().replace(' ', '-')
        
        # Get contaminants for this material
        contaminants = self.associations_validator.get_contaminants_for_material(material_slug)
        if contaminants:
            linkages['contaminants'] = sorted([c['id'] for c in contaminants])
        
        # Get compounds for contaminants
        all_compounds = set()
        for contaminant in contaminants:
            compounds = self.associations_validator.get_compounds_for_contaminant(contaminant['id'])
            all_compounds.update(c['id'] for c in compounds)
        
        if all_compounds:
            linkages['compounds'] = sorted(all_compounds)
        
        return linkages if linkages else None
    
    def export_all(self, force: bool = False) -> Dict[str, bool]:
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
        
        # Basic fields
        frontmatter['name'] = material_name
        frontmatter['slug'] = slug
        frontmatter['domain'] = 'settings'
        
        # Add ISO 8601 timestamps if missing (Schema.org requirement)
        from datetime import datetime
        current_timestamp = datetime.now().isoformat()
        frontmatter['datePublished'] = setting_data.get('datePublished') or current_timestamp
        frontmatter['dateModified'] = setting_data.get('dateModified') or current_timestamp
        
        # Copy machine settings
        if 'machineSettings' in setting_data:
            frontmatter['machineSettings'] = self._strip_generation_metadata(setting_data['machineSettings'])
        
        # Copy settings description
        if 'settingsDescription' in setting_data:
            frontmatter['settingsDescription'] = setting_data['settingsDescription']
        
        # Copy challenges if present
        if 'challenges' in setting_data:
            frontmatter['challenges'] = self._strip_generation_metadata(setting_data['challenges'])
        
        # Copy author if present
        if 'author' in setting_data:
            frontmatter['author'] = setting_data['author']
        
        # Generate domain_linkages from centralized associations
        domain_linkages = self._generate_domain_linkages(material_name)
        if domain_linkages:
            frontmatter['domain_linkages'] = domain_linkages
        
        # Reorder fields according to specification
        ordered_frontmatter = self.field_order_validator.reorder_fields(frontmatter, 'settings')
        
        # Convert to plain dict to avoid Python-specific YAML tags
        plain_frontmatter = self._convert_to_plain_dict(ordered_frontmatter)
        
        # Write to file with sort_keys=False to preserve field order
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(plain_frontmatter, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
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
