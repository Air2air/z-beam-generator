#!/usr/bin/env python3
"""
Data Integrity Validator

Validates relationships WITHIN source data files (Materials.yaml, Contaminants.yaml, etc.)
Ensures all referenced IDs actually exist in the source data before export.

This is separate from frontmatter path validation - this checks data integrity at source.
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any
from collections import defaultdict

from shared.utils.file_ops.path_manager import PathManager


@dataclass
class DataIssue:
    """Represents a data integrity issue"""
    severity: str  # 'error', 'warning', 'info'
    issue_type: str
    source_file: str
    source_id: str
    source_domain: str
    target_id: str
    target_domain: str
    message: str


@dataclass
class DataValidationReport:
    """Aggregates all validation findings"""
    total_items: int = 0
    total_relationships: int = 0
    broken_references: List[DataIssue] = field(default_factory=list)
    missing_backlinks: List[DataIssue] = field(default_factory=list)
    orphaned_items: List[DataIssue] = field(default_factory=list)
    warnings: List[DataIssue] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        return len(self.broken_references) > 0
    
    @property
    def error_count(self) -> int:
        return len(self.broken_references)
    
    @property
    def warning_count(self) -> int:
        return len(self.missing_backlinks) + len(self.warnings)


class DataIntegrityValidator:
    """Validates relationships within source data files"""
    
    DOMAINS = ['materials', 'contaminants', 'compounds', 'settings', 'applications']
    
    # Valid relationship types per domain
    VALID_RELATIONSHIPS = {
        'materials': ['related_contaminants', 'related_compounds', 'related_settings', 'regulatory_standards'],
        'contaminants': ['related_materials', 'produces_compounds', 'recommended_settings'],
        'compounds': ['produced_by_contaminants', 'related_materials'],
        'settings': ['suitable_materials', 'effective_contaminants'],
        'applications': []
    }

    # Canonical aggregate relationship paths
    CANONICAL_RELATIONSHIPS = {
        'materials': [
            {
                'path': ('relationships', 'interactions', 'contaminatedBy', 'items'),
                'rel_type': 'contaminatedBy',
                'target_domain': 'contaminants',
            },
            {
                'path': ('relationships', 'operational', 'industryApplications', 'items'),
                'rel_type': 'industryApplications',
                'target_domain': 'applications',
            },
        ],
        'contaminants': [
            {
                'path': ('validMaterials',),
                'rel_type': 'validMaterials',
                'target_domain': 'materials',
            },
            {
                'path': ('relationships', 'interactions', 'producesCompounds', 'items'),
                'rel_type': 'producesCompounds',
                'target_domain': 'compounds',
            },
        ],
        'compounds': [
            {
                'path': ('relationships', 'interactions', 'producedFromContaminants', 'items'),
                'rel_type': 'producedFromContaminants',
                'target_domain': 'contaminants',
            },
        ],
        'settings': [
            {
                'path': ('relationships', 'interactions', 'worksOnMaterials', 'items'),
                'rel_type': 'worksOnMaterials',
                'target_domain': 'materials',
            },
            {
                'path': ('relationships', 'interactions', 'removesContaminants', 'items'),
                'rel_type': 'removesContaminants',
                'target_domain': 'contaminants',
            },
        ],
        'applications': [
            {
                'path': ('relationships', 'discovery', 'relatedMaterials', 'items'),
                'rel_type': 'relatedMaterials',
                'target_domain': 'materials',
            },
            {
                'path': ('relationships', 'interactions', 'contaminatedBy', 'items'),
                'rel_type': 'contaminatedBy',
                'target_domain': 'contaminants',
            },
        ],
    }
    
    # Bidirectional relationship mappings
    BIDIRECTIONAL_MAPPINGS = {
        ('materials', 'related_contaminants'): ('contaminants', 'related_materials'),
        ('materials', 'related_compounds'): ('compounds', 'related_materials'),
        ('materials', 'related_settings'): ('settings', 'suitable_materials'),
        ('contaminants', 'produces_compounds'): ('compounds', 'produced_by_contaminants'),
        ('contaminants', 'recommended_settings'): ('settings', 'effective_contaminants'),
    }
    
    # Data file paths
    DATA_FILES = {
        'materials': ('aggregates/Materials.yaml', 'data/materials/Materials.yaml'),
        'contaminants': ('aggregates/contaminants.yaml', 'data/contaminants/contaminants.yaml'),
        'compounds': ('aggregates/Compounds.yaml', 'data/compounds/Compounds.yaml'),
        'settings': ('aggregates/Settings.yaml', 'data/settings/Settings.yaml'),
        'applications': ('aggregates/Applications.yaml', 'data/applications/Applications.yaml'),
    }
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.index: Dict[str, Set[str]] = defaultdict(set)
        self.data: Dict[str, Dict[str, Any]] = {}
        self.report = DataValidationReport()
        self.link_graph = defaultdict(lambda: defaultdict(list))
        self.source_file_display: Dict[str, str] = {}

    def _resolve_data_file(self, domain: str) -> tuple[Path, str]:
        relative_candidates = self.DATA_FILES[domain]
        resolved = PathManager.get_preferred_existing_path(*relative_candidates)
        return resolved, str(resolved.relative_to(self.project_root))
    
    def load_data_files(self):
        """Load all source data files"""
        print("\n🔍 Loading source data files...")
        
        for domain in self.DATA_FILES:
            try:
                full_path, display_path = self._resolve_data_file(domain)
            except FileNotFoundError:
                display_path = self.DATA_FILES[domain][0]
                full_path = self.project_root / display_path

            if not full_path.exists():
                print(f"   ⚠️  File not found: {full_path}")
                self.data[domain] = {}
                continue
            
            try:
                with open(full_path, 'r') as f:
                    content = yaml.safe_load(f)
                self.source_file_display[domain] = display_path
                
                # Handle different YAML structures
                if domain == 'materials' and 'materials' in content:
                    items = content['materials']
                elif domain == 'contaminants' and 'contaminants' in content:
                    items = content['contaminants']
                elif domain == 'contaminants' and 'contamination_patterns' in content:
                    items = content['contamination_patterns']
                elif domain == 'compounds' and 'compounds' in content:
                    items = content['compounds']
                elif domain == 'settings' and 'settings' in content:
                    items = content['settings']
                elif domain == 'applications' and 'applications' in content:
                    items = content['applications']
                else:
                    items = content
                
                self.data[domain] = items if isinstance(items, dict) else {}
                
                # Build index using actual IDs as they appear in the file
                for item_id in self.data[domain].keys():
                    self.index[domain].add(item_id)
                    self.report.total_items += 1
                
                print(f"   ✅ {domain}: {len(self.data[domain])} items loaded from {display_path}")
                
            except Exception as e:
                print(f"   ❌ Error loading {display_path}: {e}")
                self.data[domain] = {}
    
    def validate_all(self) -> DataValidationReport:
        """Run complete data integrity validation"""
        print("\n🔍 Validating data integrity in source files...")
        
        self.load_data_files()
        
        for domain in self.DOMAINS:
            self.validate_domain(domain)
        
        self.check_bidirectional_consistency()
        self.find_orphaned_items()
        
        return self.report
    
    def validate_domain(self, domain: str):
        """Validate all items in a specific domain"""
        if not self.data[domain]:
            return
        
        print(f"\n📂 Validating {domain} data...")
        
        for item_id, item_data in self.data[domain].items():
            self.validate_item(item_id, item_data, domain)
    
    def validate_item(self, item_id: str, item_data: Dict, domain: str):
        """Validate relationships in a single item"""
        if not isinstance(item_data, dict):
            return

        self.validate_canonical_relationships(item_id, item_data, domain)
        
        # Check relationships section
        relationships = item_data.get('relationships', {})
        if not isinstance(relationships, dict):
            return
        
        for rel_type, links in relationships.items():
            if rel_type in self.VALID_RELATIONSHIPS.get(domain, []):
                self.validate_relationship(
                    source_id=item_id,
                    source_domain=domain,
                    rel_type=rel_type,
                    links=links
                )

    def validate_canonical_relationships(self, item_id: str, item_data: Dict[str, Any], domain: str):
        """Validate nested aggregate-era relationship structures."""
        for relation in self.CANONICAL_RELATIONSHIPS.get(domain, []):
            links = self._extract_nested_value(item_data, relation['path'])
            if links is None:
                continue

            self.validate_explicit_relationship(
                source_id=item_id,
                source_domain=domain,
                rel_type=relation['rel_type'],
                target_domain=relation['target_domain'],
                links=links,
            )

    def _extract_nested_value(self, data: Dict[str, Any], path: tuple[str, ...]) -> Any:
        current: Any = data
        for segment in path:
            if not isinstance(current, dict) or segment not in current:
                return None
            current = current[segment]
        return current
    
    def validate_relationship(self, source_id: str, source_domain: str, 
                            rel_type: str, links: Any):
        """Validate a specific relationship type"""
        
        # Check if relationship type is valid for this domain
        if rel_type not in self.VALID_RELATIONSHIPS.get(source_domain, []):
            self.report.warnings.append(DataIssue(
                severity='warning',
                issue_type='invalid_relationship_type',
                source_file=self.DATA_FILES[source_domain],
                source_id=source_id,
                source_domain=source_domain,
                target_id='',
                target_domain='',
                message=f"Unknown relationship type '{rel_type}' for {source_domain} domain"
            ))
            return
        
        # regulatory_standards is special - doesn't link to other items
        if rel_type == 'regulatory_standards':
            return
        
        # Determine target domain
        target_domain = self.get_target_domain(source_domain, rel_type)
        if not target_domain:
            return

        self.validate_explicit_relationship(
            source_id=source_id,
            source_domain=source_domain,
            rel_type=rel_type,
            target_domain=target_domain,
            links=links,
        )

    def validate_explicit_relationship(
        self,
        source_id: str,
        source_domain: str,
        rel_type: str,
        target_domain: str,
        links: Any,
    ):
        """Validate a relationship when the target domain is already known."""

        if rel_type == 'regulatory_standards':
            return
        
        if not isinstance(links, list):
            return
        
        for link in links:
            if isinstance(link, str):
                target_id = link
            elif isinstance(link, dict):
                target_id = link.get('id')
            else:
                continue
            
            if not target_id:
                continue

            target_id = self.normalize_target_id(target_domain, target_id)
            
            self.report.total_relationships += 1
            
            # Check if target exists in source data
            if target_id not in self.index[target_domain]:
                self.report.broken_references.append(DataIssue(
                    severity='error',
                    issue_type='broken_reference',
                    source_file=self.source_file_display.get(source_domain, self.DATA_FILES[source_domain][0]),
                    source_id=source_id,
                    source_domain=source_domain,
                    target_id=target_id,
                    target_domain=target_domain,
                    message=f"References non-existent {target_domain} item '{target_id}'"
                ))
            else:
                # Track link in graph for bidirectional checking
                self.link_graph[f"{source_domain}:{source_id}"][rel_type].append(target_id)

    def normalize_target_id(self, target_domain: str, target_id: str) -> str:
        """Normalize known cross-domain alias patterns before validation."""
        if target_domain == 'applications' and target_id not in self.index[target_domain]:
            canonical_application_id = f"{target_id}-applications"
            if canonical_application_id in self.index[target_domain]:
                return canonical_application_id

        return target_id
    
    def get_target_domain(self, source_domain: str, rel_type: str) -> str:
        """Determine target domain from relationship type"""
        mappings = {
            'related_materials': 'materials',
            'related_contaminants': 'contaminants',
            'related_compounds': 'compounds',
            'related_settings': 'settings',
            'suitable_materials': 'materials',
            'effective_contaminants': 'contaminants',
            'produces_compounds': 'compounds',
            'produced_by_contaminants': 'contaminants',
            'recommended_settings': 'settings'
        }
        return mappings.get(rel_type, '')
    
    def check_bidirectional_consistency(self):
        """Check if bidirectional relationships are consistent"""
        print("\n🔄 Checking bidirectional consistency...")
        
        for (source_domain, source_rel), (target_domain, target_rel) in self.BIDIRECTIONAL_MAPPINGS.items():
            # Iterate over a list copy to avoid dictionary changed during iteration
            for source_key, rels in list(self.link_graph.items()):
                if not source_key.startswith(f"{source_domain}:"):
                    continue
                
                source_id = source_key.split(':', 1)[1]
                
                for target_id in rels.get(source_rel, []):
                    # Check if backlink exists
                    target_key = f"{target_domain}:{target_id}"
                    backlinks = self.link_graph[target_key].get(target_rel, [])
                    
                    if source_id not in backlinks:
                        self.report.missing_backlinks.append(DataIssue(
                            severity='warning',
                            issue_type='missing_backlink',
                            source_file=self.source_file_display.get(source_domain, self.DATA_FILES[source_domain][0]),
                            source_id=source_id,
                            source_domain=source_domain,
                            target_id=target_id,
                            target_domain=target_domain,
                            message=f"{source_domain}:{source_id} links to {target_domain}:{target_id}, but backlink missing"
                        ))
    
    def find_orphaned_items(self):
        """Find items with no incoming or outgoing relationships"""
        print("\n🔍 Finding orphaned items...")
        
        for domain in self.DOMAINS:
            for item_id in self.index[domain]:
                key = f"{domain}:{item_id}"
                has_outgoing = bool(self.link_graph[key])
                
                # Check for incoming links
                has_incoming = False
                for other_key, rels in self.link_graph.items():
                    for rel_targets in rels.values():
                        if item_id in rel_targets:
                            has_incoming = True
                            break
                    if has_incoming:
                        break
                
                if not has_outgoing and not has_incoming:
                    self.report.orphaned_items.append(DataIssue(
                        severity='info',
                        issue_type='orphaned',
                        source_file=self.source_file_display.get(domain, self.DATA_FILES[domain][0]),
                        source_id=item_id,
                        source_domain=domain,
                        target_id='',
                        target_domain='',
                        message=f"No relationships (incoming or outgoing)"
                    ))
    
    def print_report(self):
        """Print validation report to console"""
        print("\n" + "="*80)
        print("📊 DATA INTEGRITY VALIDATION REPORT")
        print("="*80)
        
        print(f"\n📁 Source Files Validated: {len([d for d in self.DOMAINS if self.data[d]])}")
        print(f"📦 Total Items: {self.report.total_items}")
        print(f"🔗 Total Relationships: {self.report.total_relationships}")
        
        if not self.report.has_errors and self.report.warning_count == 0:
            print("\n✅ No issues found! Data integrity is perfect.")
        
        if self.report.has_errors:
            print(f"\n❌ ERRORS: {self.report.error_count}")
            
            if self.report.broken_references:
                print(f"\n🔴 Broken References ({len(self.report.broken_references)}):")
                for issue in self.report.broken_references[:20]:
                    print(f"   • {issue.source_domain}/{issue.source_id} → {issue.target_domain}/{issue.target_id}")
                    print(f"     {issue.message}")
                if len(self.report.broken_references) > 20:
                    print(f"   ... and {len(self.report.broken_references) - 20} more")
        
        if self.report.warning_count > 0:
            print(f"\n⚠️  WARNINGS: {self.report.warning_count}")
            
            if self.report.missing_backlinks:
                print(f"\n🟡 Missing Backlinks ({len(self.report.missing_backlinks)}):")
                for issue in self.report.missing_backlinks[:10]:
                    print(f"   • {issue.source_domain}/{issue.source_id} → {issue.target_domain}/{issue.target_id}")
                if len(self.report.missing_backlinks) > 10:
                    print(f"   ... and {len(self.report.missing_backlinks) - 10} more")
            
            if self.report.orphaned_items:
                print(f"\n🟡 Orphaned Items ({len(self.report.orphaned_items)}):")
                for issue in self.report.orphaned_items[:10]:
                    print(f"   • {issue.source_domain}/{issue.source_id}")
                if len(self.report.orphaned_items) > 10:
                    print(f"   ... and {len(self.report.orphaned_items) - 10} more")
        
        print("\n" + "="*80)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate data integrity in source YAML files')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings', 'applications'],
                       help='Validate only specific domain')
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent.parent
    print(f"📂 Using project root: {project_root.absolute()}")
    
    validator = DataIntegrityValidator(project_root)
    
    if args.domain:
        print(f"\n🎯 Validating {args.domain} domain only...")
        validator.load_data_files()
        validator.validate_domain(args.domain)
    else:
        validator.validate_all()
    
    validator.print_report()
    
    # Return exit code based on errors
    return 1 if validator.report.has_errors else 0


if __name__ == '__main__':
    exit(main())
