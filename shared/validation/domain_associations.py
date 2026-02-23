"""
Domain Associations Validator
==============================

Validates and manages centralized domain relationships from DomainAssociations.yaml

ARCHITECTURE:
- Single source of truth for all cross-domain relationships
- Automatic bidirectionality
- URL validation against target domains
- Research verification tracking
- Fail-fast on invalid associations

USAGE:
    validator = DomainAssociationsValidator()
    validator.validate_all()  # Raises if any validation fails
    
    # Get bidirectional linkages for export
    contaminant_links = validator.get_contaminants_for_material('aluminum-laser-cleaning')
    compound_links = validator.get_compounds_for_contaminant('rust-oxidation-contamination')
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

from shared.utils.formatters import (
    extract_slug,
    format_display_name,
    format_image_url,
    normalize_taxonomy,
)


@dataclass
class Association:
    """Represents a single domain association"""
    source_id: str
    target_id: str
    frequency: str
    severity: str
    typical_context: str
    verified: bool
    verification_source: Optional[str] = None
    notes: Optional[str] = None


class DomainAssociationsValidator:
    """Validates and provides access to domain associations"""
    
    ALLOWED_FREQUENCIES = {'very_common', 'common', 'occasional', 'rare'}
    ALLOWED_SEVERITIES = {'critical', 'high', 'moderate', 'low'}
    
    def __init__(self, associations_file: Optional[Path] = None):
        """
        Initialize validator
        
        Args:
            associations_file: Path to associations YAML (auto-detected if None)
        """
        if associations_file is None:
            # Use DomainAssociations.yaml (2,730 associations) - primary data source
            associations_file = Path(__file__).parent.parent.parent / 'data' / 'associations' / 'DomainAssociations.yaml'
        
        self.associations_file = Path(associations_file)
        self.data: Optional[Dict] = None
        self.materials_data: Optional[Dict] = None
        self.contaminants_data: Optional[Dict] = None
        self.compounds_data: Optional[Dict] = None
        self.settings_data: Optional[Dict] = None
        
        # Cache for validation
        self._valid_material_ids: Optional[Set[str]] = None
        self._valid_contaminant_ids: Optional[Set[str]] = None
        self._valid_compound_ids: Optional[Set[str]] = None
        self._valid_settings_ids: Optional[Set[str]] = None
    
    def load(self) -> None:
        """Load associations and domain data files"""
        if not self.associations_file.exists():
            raise FileNotFoundError(
                f"Associations file not found: {self.associations_file}\n"
                f"Create this file to define cross-domain relationships."
            )
        
        with open(self.associations_file, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
        
        # Load domain data for validation
        data_dir = Path(__file__).parent.parent.parent / 'data'
        
        materials_file = data_dir / 'materials' / 'Materials.yaml'
        if materials_file.exists():
            with open(materials_file, 'r', encoding='utf-8') as f:
                self.materials_data = yaml.safe_load(f)
        
        contaminants_file = data_dir / 'contaminants' / 'Contaminants.yaml'
        if contaminants_file.exists():
            with open(contaminants_file, 'r', encoding='utf-8') as f:
                self.contaminants_data = yaml.safe_load(f)
        
        compounds_file = data_dir / 'compounds' / 'Compounds.yaml'
        if compounds_file.exists():
            with open(compounds_file, 'r', encoding='utf-8') as f:
                self.compounds_data = yaml.safe_load(f)
        
        settings_file = data_dir / 'settings' / 'Settings.yaml'
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                self.settings_data = yaml.safe_load(f)

    @staticmethod
    def _require_dict(container: Dict, key: str, context: str) -> Dict:
        """Require a dictionary key and validate dictionary type."""
        if key not in container:
            raise ValueError(f"{context} missing required key '{key}'")
        value = container[key]
        if not isinstance(value, dict):
            raise ValueError(f"{context}.{key} must be a dictionary")
        return value

    @staticmethod
    def _require_list(container: Dict, key: str, context: str) -> List:
        """Require a list key and validate list type."""
        if key not in container:
            raise ValueError(f"{context} missing required key '{key}'")
        value = container[key]
        if not isinstance(value, list):
            raise ValueError(f"{context}.{key} must be a list")
        return value
    
    def _get_valid_material_ids(self) -> Set[str]:
        """Get set of valid material IDs"""
        if self._valid_material_ids is None:
            if not self.materials_data:
                self._valid_material_ids = set()
            else:
                if 'materials' not in self.materials_data or not isinstance(self.materials_data['materials'], dict):
                    raise ValueError("Materials.yaml missing required 'materials' dictionary")
                materials = self.materials_data['materials']
                # IDs already include -laser-cleaning suffix
                self._valid_material_ids = set(materials.keys())
        return self._valid_material_ids
    
    def _get_valid_contaminant_ids(self) -> Set[str]:
        """Get set of valid contaminant IDs"""
        if self._valid_contaminant_ids is None:
            if not self.contaminants_data:
                self._valid_contaminant_ids = set()
            else:
                if 'contaminants' not in self.contaminants_data or not isinstance(self.contaminants_data['contaminants'], dict):
                    raise ValueError("Contaminants.yaml missing required 'contaminants' dictionary")
                contaminants = self.contaminants_data['contaminants']
                # IDs already include -contamination suffix
                self._valid_contaminant_ids = set(contaminants.keys())
        return self._valid_contaminant_ids
    
    def _get_valid_compound_ids(self) -> Set[str]:
        """Get set of valid compound IDs"""
        if self._valid_compound_ids is None:
            if not self.compounds_data:
                self._valid_compound_ids = set()
            else:
                if 'compounds' not in self.compounds_data or not isinstance(self.compounds_data['compounds'], dict):
                    raise ValueError("Compounds.yaml missing required 'compounds' dictionary")
                compounds = self.compounds_data['compounds']
                # IDs already include -compound suffix
                self._valid_compound_ids = set(compounds.keys())
        return self._valid_compound_ids
    
    def _get_valid_settings_ids(self) -> Set[str]:
        """Get set of valid settings IDs"""
        if self._valid_settings_ids is None:
            if not self.settings_data:
                self._valid_settings_ids = set()
            else:
                if 'settings' not in self.settings_data or not isinstance(self.settings_data['settings'], dict):
                    raise ValueError("Settings.yaml missing required 'settings' dictionary")
                settings = self.settings_data['settings']
                # IDs already include -settings suffix
                self._valid_settings_ids = set(settings.keys())
        return self._valid_settings_ids
    
    def validate_association(self, assoc: Dict, assoc_type: str) -> List[str]:
        """
        Validate a single association
        
        Args:
            assoc: Association dictionary
            assoc_type: Type of association (material_contaminant, contaminant_compound, etc.)
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        if assoc_type == 'material_contaminant':
            if 'material_id' not in assoc:
                errors.append("Missing required field: material_id")
            if 'contaminant_id' not in assoc:
                errors.append("Missing required field: contaminant_id")
        elif assoc_type == 'contaminant_compound':
            if 'contaminant_id' not in assoc:
                errors.append("Missing required field: contaminant_id")
            if 'compound_id' not in assoc:
                errors.append("Missing required field: compound_id")
        
        # Check frequency
        frequency = assoc.get('frequency')
        if not frequency:
            errors.append("Missing required field: frequency")
        elif frequency not in self.ALLOWED_FREQUENCIES:
            errors.append(f"Invalid frequency: {frequency}. Allowed: {self.ALLOWED_FREQUENCIES}")
        
        # Check severity
        severity = assoc.get('severity')
        if not severity:
            errors.append("Missing required field: severity")
        elif severity not in self.ALLOWED_SEVERITIES:
            errors.append(f"Invalid severity: {severity}. Allowed: {self.ALLOWED_SEVERITIES}")
        
        # Check verification
        verified = assoc.get('verified')
        if verified is None:
            errors.append("Missing required field: verified")
        elif verified and not assoc.get('verification_source'):
            errors.append("verified=true requires verification_source")
        
        # Validate IDs exist in domain data
        if assoc_type == 'material_contaminant':
            material_id = assoc.get('material_id')
            if material_id and material_id not in self._get_valid_material_ids():
                errors.append(f"Invalid material_id: {material_id} not found in Materials.yaml")
            
            contaminant_id = assoc.get('contaminant_id')
            if contaminant_id and contaminant_id not in self._get_valid_contaminant_ids():
                errors.append(f"Invalid contaminant_id: {contaminant_id} not found in Contaminants.yaml")
        
        elif assoc_type == 'contaminant_compound':
            contaminant_id = assoc.get('contaminant_id')
            if contaminant_id and contaminant_id not in self._get_valid_contaminant_ids():
                errors.append(f"Invalid contaminant_id: {contaminant_id} not found in Contaminants.yaml")
            
            compound_id = assoc.get('compound_id')
            if compound_id and compound_id not in self._get_valid_compound_ids():
                errors.append(f"Invalid compound_id: {compound_id} not found in Compounds.yaml")
        
        return errors
    
    def validate_all(self) -> None:
        """
        Validate all associations
        
        Raises:
            ValueError: If any validation fails
        """
        if not self.data:
            self.load()
        
        all_errors = []
        
        # Validate material-contaminant associations
        mat_cont_assocs = self.data.get('material_contaminant_associations') or []
        for i, assoc in enumerate(mat_cont_assocs):
            errors = self.validate_association(assoc, 'material_contaminant')
            if errors:
                all_errors.append(f"material_contaminant_associations[{i}]: {', '.join(errors)}")
        
        # Validate contaminant-compound associations
        cont_comp_assocs = self.data.get('contaminant_compound_associations') or []
        for i, assoc in enumerate(cont_comp_assocs):
            errors = self.validate_association(assoc, 'contaminant_compound')
            if errors:
                all_errors.append(f"contaminant_compound_associations[{i}]: {', '.join(errors)}")
        
        if all_errors:
            raise ValueError(
                "Domain associations validation failed:\n" +
                "\n".join(f"  - {err}" for err in all_errors)
            )
    
    def get_contaminants_for_material(self, material_id: str) -> List[Dict]:
        """
        Get all contaminants associated with a material
        
        Args:
            material_id: Material ID (e.g., 'aluminum-laser-cleaning' or 'aluminum')
        
        Returns:
            List of contaminant linkage dictionaries with full metadata
        """
        if not self.data:
            self.load()

        if not isinstance(self.data, dict):
            raise ValueError("Associations data must be a dictionary")
        if not isinstance(self.contaminants_data, dict):
            raise ValueError("Contaminants data must be a dictionary")
        
        # Strip -laser-cleaning suffix if present (lookup index uses base material ID)
        base_material_id = material_id.replace('-laser-cleaning', '')
        
        # Use lookup index for fast access
        material_to_contaminant = self._require_dict(self.data, 'material_to_contaminant', 'Associations data')
        contaminant_ids = material_to_contaminant.get(base_material_id)
        if contaminant_ids is None:
            return []
        if not isinstance(contaminant_ids, list):
            raise ValueError("material_to_contaminant entries must be lists")
        if not contaminant_ids:
            return []

        associations = self._require_list(self.data, 'associations', 'Associations data')
        contamination_patterns = self._require_dict(self.contaminants_data, 'contamination_patterns', 'Contaminants data')
        
        results = []
        
        for contaminant_id in contaminant_ids:
            # Find full association data in associations list
            assoc = None
            for a in associations:
                if (a.get('source_domain') == 'materials' and 
                    a.get('source_id') == base_material_id and
                    a.get('target_domain') == 'contaminants' and
                    a.get('target_id') == contaminant_id and
                    a.get('relationship_type') == 'can_have_contamination'):
                    assoc = a
                    break
            
            # Get contaminant details from Contaminants.yaml
            full_contaminant_id = contaminant_id if contaminant_id.endswith('-contamination') else f"{contaminant_id}-contamination"
            if full_contaminant_id not in contamination_patterns:
                raise ValueError(
                    f"Contaminant '{full_contaminant_id}' referenced in associations but missing from Contaminants.yaml"
                )
            contaminant_data = contamination_patterns[full_contaminant_id]
            if not isinstance(contaminant_data, dict):
                raise ValueError(f"Contaminant '{full_contaminant_id}' data must be a dictionary")
            if 'name' not in contaminant_data or not isinstance(contaminant_data['name'], str) or not contaminant_data['name'].strip():
                raise ValueError(f"Contaminant '{full_contaminant_id}' missing required non-empty 'name'")
            
            # Build linkage per FRONTMATTER_GENERATOR_LINKAGE_SPEC.md
            category, subcategory = normalize_taxonomy(contaminant_data)
            
            # Extract display name and slug using formatters
            display_name = format_display_name(contaminant_id, '-contamination')
            slug = extract_slug(contaminant_id, '-contamination')
            
            results.append({
                'id': full_contaminant_id,
                'title': contaminant_data['name'],
                'url': f"/contaminants/{category}/{subcategory}/{full_contaminant_id}",
                'image': format_image_url('contaminants', slug),
                'category': category,
                'subcategory': subcategory,
                # Default metadata since DomainAssociations doesn't have this yet
                'frequency': 'common',
                'severity': 'moderate',
                'typical_context': ''
            })
        
        return results
    
    def get_materials_for_contaminant(self, contaminant_id: str) -> List[Dict]:
        """
        Get all materials affected by a contaminant (reverse lookup)
        
        Args:
            contaminant_id: Contaminant ID (e.g., 'rust-oxidation-contamination' or 'rust-oxidation')
        
        Returns:
            List of material linkage dictionaries with full metadata
        """
        if not self.data:
            self.load()

        if not isinstance(self.data, dict):
            raise ValueError("Associations data must be a dictionary")
        if not isinstance(self.materials_data, dict):
            raise ValueError("Materials data must be a dictionary")
        
        # Ensure full ID with -contamination suffix (lookup index uses full IDs)
        full_contaminant_id = contaminant_id if contaminant_id.endswith('-contamination') else f"{contaminant_id}-contamination"
        
        # Use lookup index for fast access (uses full ID with suffix)
        contaminant_to_material = self._require_dict(self.data, 'contaminant_to_material', 'Associations data')
        material_ids = contaminant_to_material.get(full_contaminant_id)
        if material_ids is None:
            return []
        if not isinstance(material_ids, list):
            raise ValueError("contaminant_to_material entries must be lists")
        if not material_ids:
            return []

        materials = self._require_dict(self.materials_data, 'materials', 'Materials data')
        
        results = []
        
        for material_id in material_ids:
            # Add -laser-cleaning suffix for Materials.yaml lookup
            full_material_id = material_id if material_id.endswith('-laser-cleaning') else f"{material_id}-laser-cleaning"
            
            # Get material details from Materials.yaml
            if full_material_id not in materials:
                raise ValueError(
                    f"Material '{full_material_id}' referenced in associations but missing from Materials.yaml"
                )
            material_data = materials[full_material_id]
            if not isinstance(material_data, dict):
                raise ValueError(f"Material '{full_material_id}' data must be a dictionary")
            if 'name' not in material_data or not isinstance(material_data['name'], str) or not material_data['name'].strip():
                raise ValueError(f"Material '{full_material_id}' missing required non-empty 'name'")
            
            # Get URL from full_path (single source of truth)
            url = material_data.get('full_path')
            if not url:
                # Fallback: derive from category/subcategory
                category, subcategory = normalize_taxonomy(material_data)
                url = f"/materials/{category}/{subcategory}/{full_material_id}"
            else:
                # Get category/subcategory for linkage metadata
                category, subcategory = normalize_taxonomy(material_data)
            
            # Extract display name using formatters
            display_name = format_display_name(full_material_id, '-laser-cleaning')
            
            results.append({
                'id': full_material_id,
                'title': material_data['name'],
                'url': url,
                'image': format_image_url('materials', full_material_id),
                'category': category,
                'subcategory': subcategory,
                # Default metadata
                'frequency': 'common',
                'severity': 'moderate',
                'typical_context': ''
            })
        
        return results
    
    def get_compounds_for_contaminant(self, contaminant_id: str) -> List[Dict]:
        """
        Get all compounds produced by a contaminant
        
        Args:
            contaminant_id: Contaminant ID (e.g., 'rust-oxidation-contamination' or 'rust-oxidation')
        
        Returns:
            List of compound linkage dictionaries with full metadata
        """
        if not self.data:
            self.load()

        if not isinstance(self.data, dict):
            raise ValueError("Associations data must be a dictionary")
        if not isinstance(self.compounds_data, dict):
            raise ValueError("Compounds data must be a dictionary")
        
        # Strip -contamination suffix if present
        base_contaminant_id = contaminant_id.replace('-contamination', '')
        
        # Find compound associations in associations list
        compound_ids = []
        associations = self._require_list(self.data, 'associations', 'Associations data')
        for assoc in associations:
            if (assoc.get('source_domain') == 'contaminants' and
                assoc.get('source_id') == base_contaminant_id and
                assoc.get('target_domain') == 'compounds' and
                assoc.get('relationship_type') == 'generates_byproduct'):
                compound_ids.append(assoc.get('target_id'))
        
        if not compound_ids:
            return []
        
        results = []
        
        for compound_id in compound_ids:
            # Get compound details from Compounds.yaml (uses slug without suffix as key)
            slug_without_suffix = extract_slug(compound_id, 'compound')
            compounds = self._require_dict(self.compounds_data, 'compounds', 'Compounds data')
            if slug_without_suffix not in compounds:
                raise ValueError(
                    f"Compound '{slug_without_suffix}' referenced in associations but missing from Compounds.yaml"
                )
            compound_data = compounds[slug_without_suffix]
            if not isinstance(compound_data, dict):
                raise ValueError(f"Compound '{slug_without_suffix}' data must be a dictionary")
            
            # Get URL from full_path in compound data (single source of truth)
            url = compound_data.get('full_path')
            if not url:
                # Fallback: derive from category/subcategory
                category, subcategory = normalize_taxonomy(compound_data)
                url = f"/compounds/{category}/{subcategory}/{compound_id}"
            else:
                # Get category/subcategory from compound data for linkage metadata
                category, subcategory = normalize_taxonomy(compound_data)
            
            results.append({
                'id': compound_id,
                'url': url,
                'image': format_image_url('compounds', slug_without_suffix),
                'category': category,
                'subcategory': subcategory,
                # Default metadata
                'frequency': 'common',
                'severity': 'moderate',
                'typical_context': '',
                'exposure_risk': 'moderate'
            })
        
        return results
    
    def get_contaminants_for_compound(self, compound_id: str) -> List[Dict]:
        """
        Get all contaminants that produce a compound (reverse lookup)
        
        Args:
            compound_id: Compound ID (e.g., 'pahs-compound')
        
        Returns:
            List of contaminant linkage dictionaries
        """
        if not self.data:
            self.load()

        if not isinstance(self.data, dict):
            raise ValueError("Associations data must be a dictionary")
        if not isinstance(self.contaminants_data, dict):
            raise ValueError("Contaminants data must be a dictionary")
        
        associations = self._require_list(self.data, 'contaminant_compound_associations', 'Associations data')
        results = []

        contamination_patterns = self._require_dict(self.contaminants_data, 'contamination_patterns', 'Contaminants data')
        
        for assoc in associations:
            if assoc.get('compound_id') == compound_id:
                contaminant_id = assoc['contaminant_id']
                
                # Get contaminant details (associations use shortened ID)
                full_contaminant_id = contaminant_id if contaminant_id.endswith('-contamination') else f"{contaminant_id}-contamination"
                if full_contaminant_id not in contamination_patterns:
                    raise ValueError(
                        f"Contaminant '{full_contaminant_id}' referenced in compound associations but missing from Contaminants.yaml"
                    )
                contaminant_data = contamination_patterns[full_contaminant_id]
                if not isinstance(contaminant_data, dict):
                    raise ValueError(f"Contaminant '{full_contaminant_id}' data must be a dictionary")
                if 'name' not in contaminant_data or not isinstance(contaminant_data['name'], str) or not contaminant_data['name'].strip():
                    raise ValueError(f"Contaminant '{full_contaminant_id}' missing required non-empty 'name'")
                
                # Get URL from full_path (single source of truth)
                url = contaminant_data.get('full_path')
                if not url:
                    # Fallback: derive from category/subcategory
                    category, subcategory = normalize_taxonomy(contaminant_data)
                    url = f"/contaminants/{category}/{subcategory}/{full_contaminant_id}"
                    logger.warning(f"Contaminant '{full_contaminant_id}' missing full_path, using derived URL: {url}")
                else:
                    # Get category/subcategory for linkage metadata
                    category, subcategory = normalize_taxonomy(contaminant_data)
                
                # Extract display name and slug using formatters
                display_name = format_display_name(contaminant_id, '-contamination')
                slug = extract_slug(contaminant_id, '-contamination')
                
                results.append({
                    'id': contaminant_id,
                    'title': contaminant_data['name'],
                    'url': url,
                    'image': format_image_url('contaminants', slug),
                    'category': category,
                    'subcategory': subcategory,
                    'frequency': assoc['frequency'],
                    'severity': assoc['severity'],
                    'typical_context': assoc['typical_context']
                })
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get statistics about associations"""
        if not self.data:
            self.load()
        
        mat_cont = self.data.get('material_contaminant_associations') or []
        cont_comp = self.data.get('contaminant_compound_associations') or []
        mat_comp = self.data.get('material_compound_associations') or []
        
        verified_mat_cont = sum(1 for a in mat_cont if a.get('verified'))
        verified_cont_comp = sum(1 for a in cont_comp if a.get('verified'))
        
        total = len(mat_cont) + len(cont_comp) + len(mat_comp)
        verified_total = verified_mat_cont + verified_cont_comp
        
        return {
            'total_associations': total,
            'material_contaminant': len(mat_cont),
            'contaminant_compound': len(cont_comp),
            'material_compound': len(mat_comp),
            'verified': verified_total,
            'verification_rate': f"{(verified_total / total * 100):.1f}%" if total > 0 else "0%"
        }


def main():
    """CLI for validating domain associations"""
    import sys
    
    validator = DomainAssociationsValidator()
    
    try:
        validator.validate_all()
        stats = validator.get_statistics()
        
        print("✅ Domain associations validation PASSED")
        print("\nStatistics:")
        print(f"  Total associations: {stats['total_associations']}")
        print(f"  Material ↔ Contaminant: {stats['material_contaminant']}")
        print(f"  Contaminant ↔ Compound: {stats['contaminant_compound']}")
        print(f"  Material ↔ Compound: {stats['material_compound']}")
        print(f"  Verified: {stats['verified']} ({stats['verification_rate']})")
        
    except Exception as e:
        print(f"❌ Validation FAILED: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
