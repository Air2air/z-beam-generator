"""
Unified Frontmatter Citation Validation

Strict validation that enforces NO FALLBACKS, NO DEFAULTS policy.
Every data point must have explicit citations or be marked needs_research.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class CitationValidator:
    """
    Validates unified frontmatter citations with ZERO TOLERANCE for fallbacks.
    
    VALIDATION RULES:
    - All non-null values MUST have citations
    - All citation IDs MUST exist in research_library
    - No "source: literature" or vague attributions allowed
    - No category-level default ranges allowed
    - Null values MUST have needs_research: true flag
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator.
        
        Args:
            strict_mode: If True, fails immediately on first error.
                        If False, collects all errors before reporting.
        """
        self.strict_mode = strict_mode
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_frontmatter(
        self,
        frontmatter: Dict,
        fail_fast: bool = False
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate complete unified frontmatter structure.
        
        Args:
            frontmatter: Unified frontmatter dictionary
            fail_fast: If True, stops at first error
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        # Validate required top-level fields
        self._validate_required_fields(frontmatter)
        
        # Validate material_properties with citations
        if 'material_properties' in frontmatter:
            self._validate_material_properties(
                frontmatter['material_properties'],
                frontmatter.get('research_library', {})
            )
        
        # Validate machine_settings with citations
        if 'machine_settings' in frontmatter:
            self._validate_machine_settings(
                frontmatter['machine_settings'],
                frontmatter.get('research_library', {})
            )
        
        # Validate research_library completeness
        if 'research_library' in frontmatter:
            self._validate_research_library(frontmatter['research_library'])
        
        # Check for forbidden patterns
        self._check_forbidden_patterns(frontmatter)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_required_fields(self, frontmatter: Dict) -> None:
        """Validate required top-level fields exist."""
        required = [
            'name', 'slug', 'category', 'author',
            'materials_page', 'material_properties',
            'machine_settings', 'research_library'
        ]
        
        for field in required:
            if field not in frontmatter:
                self.errors.append(f"❌ MISSING REQUIRED FIELD: {field}")
    
    def _validate_material_properties(
        self,
        properties: Dict,
        research_library: Dict
    ) -> None:
        """
        Validate material properties have proper citations.
        
        NO FALLBACKS ALLOWED:
        - Non-null values MUST have citations
        - Null values MUST have needs_research flag
        - All citation IDs MUST exist in research_library
        """
        for category_name, category_data in properties.items():
            if not isinstance(category_data, dict):
                continue
            
            for prop_name, prop_data in category_data.items():
                if not isinstance(prop_data, dict):
                    continue
                
                prop_path = f"material_properties.{category_name}.{prop_name}"
                
                # Check if property has value
                value = prop_data.get('value')
                
                if value is not None:
                    # NON-NULL VALUE: MUST have citations
                    if 'citations' not in prop_data:
                        self.errors.append(
                            f"❌ CITATION MISSING: {prop_path} has value '{value}' "
                            f"but NO citations field"
                        )
                        continue
                    
                    citations = prop_data['citations']
                    
                    # Must have primary citation
                    if not citations or 'primary' not in citations:
                        self.errors.append(
                            f"❌ PRIMARY CITATION MISSING: {prop_path} has value "
                            f"but no primary citation"
                        )
                    else:
                        # Validate primary citation exists in library
                        primary_id = citations['primary'].get('id')
                        if not primary_id:
                            self.errors.append(
                                f"❌ PRIMARY CITATION ID MISSING: {prop_path}"
                            )
                        elif primary_id not in research_library:
                            self.errors.append(
                                f"❌ CITATION NOT FOUND: {prop_path} references "
                                f"'{primary_id}' but not in research_library"
                            )
                    
                    # Validate supporting citations
                    for i, support_cite in enumerate(citations.get('supporting', [])):
                        cite_id = support_cite.get('id')
                        if not cite_id:
                            self.errors.append(
                                f"❌ SUPPORTING CITATION #{i+1} ID MISSING: {prop_path}"
                            )
                        elif cite_id not in research_library:
                            self.errors.append(
                                f"❌ CITATION NOT FOUND: {prop_path} supporting "
                                f"citation '{cite_id}' not in research_library"
                            )
                    
                    # Check for vague source attributions (FORBIDDEN)
                    source_summary = prop_data.get('source_summary', {})
                    primary_type = source_summary.get('primary_source_type', '')
                    
                    if primary_type in ['literature', 'estimated', 'typical', 'default']:
                        self.errors.append(
                            f"❌ FORBIDDEN SOURCE TYPE: {prop_path} has vague "
                            f"source_type '{primary_type}' - NO FALLBACKS ALLOWED"
                        )
                
                else:
                    # NULL VALUE: MUST have needs_research flag
                    source_summary = prop_data.get('source_summary', {})
                    needs_research = source_summary.get('needs_research', False)
                    
                    if not needs_research:
                        self.errors.append(
                            f"❌ NULL WITHOUT FLAG: {prop_path} has null value "
                            f"but needs_research not set to true"
                        )
                    
                    # Should have research priority
                    if needs_research and 'research_priority' not in source_summary:
                        self.warnings.append(
                            f"⚠️  {prop_path} needs research but missing priority level"
                        )
    
    def _validate_machine_settings(
        self,
        settings: Dict,
        research_library: Dict
    ) -> None:
        """Validate machine settings have proper citations."""
        
        # Validate basic settings
        if 'basic' in settings:
            for param_name, param_data in settings['basic'].items():
                if not isinstance(param_data, dict):
                    continue
                
                param_path = f"machine_settings.basic.{param_name}"
                
                # Basic settings should have citations
                if 'citations' not in param_data or not param_data['citations']:
                    self.errors.append(
                        f"❌ CITATION MISSING: {param_path} has no citations"
                    )
                else:
                    # Validate citation IDs exist
                    for citation in param_data['citations']:
                        cite_id = citation.get('id')
                        if not cite_id:
                            self.errors.append(
                                f"❌ CITATION ID MISSING: {param_path}"
                            )
                        elif cite_id not in research_library:
                            self.errors.append(
                                f"❌ CITATION NOT FOUND: {param_path} references "
                                f"'{cite_id}' but not in research_library"
                            )
        
        # Validate detailed settings (if present)
        if 'detailed' in settings:
            for param_name, param_data in settings['detailed'].items():
                if not isinstance(param_data, dict):
                    continue
                
                param_path = f"machine_settings.detailed.{param_name}"
                
                # Detailed settings MUST have research citations
                if 'research' not in param_data or not param_data['research']:
                    self.errors.append(
                        f"❌ RESEARCH CITATIONS MISSING: {param_path} has no "
                        f"research citation list"
                    )
                else:
                    # Validate citation IDs
                    for cite_id in param_data['research']:
                        if cite_id not in research_library:
                            self.errors.append(
                                f"❌ CITATION NOT FOUND: {param_path} references "
                                f"'{cite_id}' but not in research_library"
                            )
    
    def _validate_research_library(self, library: Dict) -> None:
        """Validate research_library entries have required fields."""
        for citation_id, citation_data in library.items():
            if not isinstance(citation_data, dict):
                self.errors.append(
                    f"❌ INVALID CITATION: {citation_id} is not a dictionary"
                )
                continue
            
            # Required fields for all citations
            required = ['type', 'source_name', 'confidence']
            for field in required:
                if field not in citation_data:
                    self.errors.append(
                        f"❌ CITATION INCOMPLETE: {citation_id} missing '{field}'"
                    )
            
            # Type-specific validation
            cite_type = citation_data.get('type')
            
            if cite_type == 'ai_research':
                # AI research must have validation_status
                if 'validation_status' not in citation_data:
                    self.errors.append(
                        f"❌ AI CITATION INCOMPLETE: {citation_id} missing "
                        f"validation_status"
                    )
                if 'model' not in citation_data:
                    self.warnings.append(
                        f"⚠️  AI citation {citation_id} missing model name"
                    )
            
            elif cite_type == 'journal_article':
                # Journal articles should have DOI or URL
                if 'doi' not in citation_data and 'url' not in citation_data:
                    self.warnings.append(
                        f"⚠️  Journal article {citation_id} missing DOI and URL"
                    )
            
            elif cite_type == 'industry_standard':
                # Standards should have organization
                if 'organization' not in citation_data:
                    self.warnings.append(
                        f"⚠️  Standard {citation_id} missing organization"
                    )
    
    def _check_forbidden_patterns(self, frontmatter: Dict) -> None:
        """
        Check for forbidden fallback patterns.
        
        FORBIDDEN:
        - "source: literature" (too vague)
        - "source: estimated" (no estimates allowed)
        - "source: typical" (no defaults allowed)
        - Category-level range fallbacks
        """
        # Convert to string for pattern matching
        frontmatter_str = yaml.dump(frontmatter, allow_unicode=True)
        
        forbidden_patterns = [
            ('source: literature', 'Vague "literature" source attribution'),
            ('source: estimated', 'Estimated values not allowed'),
            ('source: typical', 'Typical/default values not allowed'),
            ('source: category_default', 'Category-level defaults not allowed'),
            ('or "default"', 'Default fallback values'),
            ('or {}', 'Empty fallback dictionaries')
        ]
        
        for pattern, description in forbidden_patterns:
            if pattern.lower() in frontmatter_str.lower():
                self.errors.append(
                    f"❌ FORBIDDEN PATTERN: Found '{pattern}' - {description}"
                )
    
    def generate_report(
        self,
        frontmatter_path: Optional[Path] = None
    ) -> str:
        """
        Generate validation report.
        
        Args:
            frontmatter_path: Optional path to frontmatter file
            
        Returns:
            Formatted validation report string
        """
        report = []
        report.append("=" * 80)
        report.append("UNIFIED FRONTMATTER CITATION VALIDATION REPORT")
        report.append("=" * 80)
        
        if frontmatter_path:
            report.append(f"\nFile: {frontmatter_path}")
        
        report.append(f"\nValidation Mode: {'STRICT (fail-fast)' if self.strict_mode else 'COLLECT ALL'}")
        report.append("")
        
        # Summary
        if len(self.errors) == 0 and len(self.warnings) == 0:
            report.append("✅ VALIDATION PASSED")
            report.append("   All citations properly formatted")
            report.append("   No fallback values detected")
            report.append("   No forbidden patterns found")
        else:
            report.append("❌ VALIDATION FAILED")
            report.append(f"   Errors: {len(self.errors)}")
            report.append(f"   Warnings: {len(self.warnings)}")
        
        # Errors
        if self.errors:
            report.append("\n" + "=" * 80)
            report.append(f"ERRORS ({len(self.errors)}):")
            report.append("=" * 80)
            for i, error in enumerate(self.errors, 1):
                report.append(f"\n{i}. {error}")
        
        # Warnings
        if self.warnings:
            report.append("\n" + "=" * 80)
            report.append(f"WARNINGS ({len(self.warnings)}):")
            report.append("=" * 80)
            for i, warning in enumerate(self.warnings, 1):
                report.append(f"\n{i}. {warning}")
        
        report.append("\n" + "=" * 80)
        report.append("POLICY: NO FALLBACKS, NO DEFAULTS, NO EXCEPTIONS")
        report.append("=" * 80)
        
        return "\n".join(report)


def validate_frontmatter_file(
    file_path: str,
    strict_mode: bool = True,
    fail_on_warnings: bool = False
) -> bool:
    """
    Validate a unified frontmatter YAML file.
    
    Args:
        file_path: Path to frontmatter file
        strict_mode: If True, fails immediately on first error
        fail_on_warnings: If True, treats warnings as errors
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If YAML is invalid
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Frontmatter file not found: {path}")
    
    # Load frontmatter
    try:
        with open(path, 'r', encoding='utf-8') as f:
            frontmatter = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to load YAML: {e}")
    
    # Validate
    validator = CitationValidator(strict_mode=strict_mode)
    is_valid, errors, warnings = validator.validate_frontmatter(frontmatter)
    
    # Generate report
    report = validator.generate_report(path)
    print(report)
    
    # Check result
    if not is_valid:
        return False
    
    if fail_on_warnings and warnings:
        return False
    
    return True


if __name__ == "__main__":
    import sys
    
    # Command-line validation
    if len(sys.argv) < 2:
        print("Usage: python citation_validator.py <frontmatter_file.yaml>")
        print("       python citation_validator.py --test")
        sys.exit(1)
    
    if sys.argv[1] == '--test':
        print("Running validation tests...")
        
        # Test with sample data
        test_frontmatter = {
            'name': 'Aluminum',
            'slug': 'aluminum-laser-cleaning',
            'category': 'metal',
            'subcategory': 'non-ferrous',
            'author': {'name': 'Todd Dunning'},
            'materials_page': {},
            'material_properties': {
                'physical': {
                    'density': {
                        'value': 2.7,
                        'unit': 'g/cm³',
                        'citations': {
                            'primary': {
                                'id': 'ASTM_B209_2023',
                                'confidence': 98
                            }
                        },
                        'source_summary': {
                            'total_sources': 1,
                            'needs_research': False
                        }
                    }
                }
            },
            'machine_settings': {
                'basic': {}
            },
            'research_library': {
                'ASTM_B209_2023': {
                    'type': 'industry_standard',
                    'source_name': 'ASTM B209',
                    'confidence': 98
                }
            }
        }
        
        validator = CitationValidator()
        is_valid, errors, warnings = validator.validate_frontmatter(test_frontmatter)
        
        print(validator.generate_report())
        print(f"\nTest result: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    
    else:
        # Validate file
        file_path = sys.argv[1]
        try:
            is_valid = validate_frontmatter_file(file_path, strict_mode=True)
            sys.exit(0 if is_valid else 1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
