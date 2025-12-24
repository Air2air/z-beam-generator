#!/usr/bin/env python3
"""
Frontmatter Internal Link Verification System

Validates all internal links within frontmatter files to ensure:
1. Referenced IDs exist in their respective domains
2. URLs are correctly formatted
3. Bidirectional links are consistent
4. Relationship types are valid for each domain
5. No orphaned or broken references

Usage:
    python3 scripts/validation/verify_frontmatter_links.py
    python3 scripts/validation/verify_frontmatter_links.py --domain materials
    python3 scripts/validation/verify_frontmatter_links.py --fix
    python3 scripts/validation/verify_frontmatter_links.py --report links_report.md
"""

import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class LinkIssue:
    """Represents a link validation issue"""
    severity: str  # 'error', 'warning', 'info'
    issue_type: str
    source_file: str
    source_domain: str
    target_id: str
    target_domain: str
    message: str
    line_number: int = 0


@dataclass
class ValidationReport:
    """Complete validation report"""
    total_files: int = 0
    total_links: int = 0
    broken_links: List[LinkIssue] = field(default_factory=list)
    missing_backlinks: List[LinkIssue] = field(default_factory=list)
    invalid_urls: List[LinkIssue] = field(default_factory=list)
    orphaned_items: List[LinkIssue] = field(default_factory=list)
    warnings: List[LinkIssue] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        return len(self.broken_links) > 0 or len(self.invalid_urls) > 0
    
    @property
    def error_count(self) -> int:
        return len(self.broken_links) + len(self.invalid_urls)
    
    @property
    def warning_count(self) -> int:
        return len(self.missing_backlinks) + len(self.orphaned_items) + len(self.warnings)


class FrontmatterLinkValidator:
    """Validates internal links across all frontmatter files"""
    
    DOMAINS = ['materials', 'contaminants', 'compounds', 'settings']
    
    # Valid relationship types for each domain
    VALID_RELATIONSHIPS = {
        'materials': ['related_contaminants', 'related_compounds', 'related_settings', 'regulatory_standards'],
        'contaminants': ['related_materials', 'produces_compounds', 'recommended_settings'],
        'compounds': ['produced_by_contaminants', 'related_materials'],
        'settings': ['suitable_materials', 'effective_contaminants']
    }
    
    # Bidirectional relationship mappings
    BIDIRECTIONAL_MAPPINGS = {
        ('materials', 'related_contaminants'): ('contaminants', 'related_materials'),
        ('materials', 'related_compounds'): ('compounds', 'related_materials'),
        ('materials', 'related_settings'): ('settings', 'suitable_materials'),
        ('contaminants', 'produces_compounds'): ('compounds', 'produced_by_contaminants'),
        ('contaminants', 'recommended_settings'): ('settings', 'effective_contaminants'),
    }
    
    def __init__(self, frontmatter_root: Path):
        self.frontmatter_root = frontmatter_root
        self.index: Dict[str, Set[str]] = {domain: set() for domain in self.DOMAINS}
        self.challenge_library: Dict[str, Any] = {}
        self.link_graph: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
        self.report = ValidationReport()
        self.data_based_items = 0  # Count of data-based items (skipped)
    
    def build_index(self):
        """Build index of all valid IDs across all domains"""
        print("🔍 Building index of all frontmatter files...")
        
        # Load challenge library
        challenge_lib_path = self.frontmatter_root.parent / 'z-beam-generator' / 'data' / 'challenges' / 'ChallengePatterns.yaml'
        if challenge_lib_path.exists():
            try:
                data = yaml.safe_load(challenge_lib_path.read_text())
                if data and 'challenge_patterns' in data:
                    self.challenge_library = data['challenge_patterns']
                    print(f"   ✅ Loaded {len(self.challenge_library)} challenge patterns")
            except Exception as e:
                print(f"   ⚠️  Error loading challenge library: {e}")
        
        for domain in self.DOMAINS:
            domain_path = self.frontmatter_root / domain
            if not domain_path.exists():
                print(f"⚠️  Domain path not found: {domain_path}")
                continue
            
            for file_path in domain_path.glob('*.yaml'):
                try:
                    data = yaml.safe_load(file_path.read_text())
                    item_id = data.get('id')
                    if item_id:
                        self.index[domain].add(item_id)
                        self.report.total_files += 1
                except Exception as e:
                    print(f"❌ Error reading {file_path}: {e}")
        
        for domain, ids in self.index.items():
            print(f"   ✅ {domain}: {len(ids)} items indexed")
    
    def validate_all(self) -> ValidationReport:
        """Run complete validation across all domains"""
        print("\n🔍 Validating all internal links...")
        
        # First check which domain directories exist
        print("\n📁 Checking domain directory structure...")
        missing_domains = []
        for domain in self.DOMAINS:
            domain_path = self.frontmatter_root / domain
            if not domain_path.exists():
                missing_domains.append(domain)
                print(f"   ⚠️  Missing: {domain_path}")
            else:
                file_count = len(list(domain_path.glob('*.yaml')))
                print(f"   ✅ Found: {domain_path} ({file_count} files)")
        
        if missing_domains:
            print(f"\n⚠️  {len(missing_domains)} domain directories missing: {', '.join(missing_domains)}")
            print("   Validation will only check existing domains.")
        
        self.build_index()
        
        for domain in self.DOMAINS:
            self.validate_domain(domain)
        
        # Only check bidirectional consistency if we have multiple domains
        if len([d for d in self.DOMAINS if len(self.index[d]) > 0]) > 1:
            self.check_bidirectional_consistency()
        
        self.find_orphaned_items()
        
        return self.report
    
    def validate_domain(self, domain: str):
        """Validate all links in a specific domain"""
        domain_path = self.frontmatter_root / domain
        if not domain_path.exists():
            return
        
        print(f"\n📂 Validating {domain} domain...")
        
        for file_path in domain_path.glob('*.yaml'):
            self.validate_file(file_path, domain)
    
    def validate_file(self, file_path: Path, domain: str):
        """Validate all links in a single file"""
        try:
            data = yaml.safe_load(file_path.read_text())
            source_id = data.get('id')
            
            if not source_id:
                self.report.warnings.append(LinkIssue(
                    severity='warning',
                    issue_type='missing_id',
                    source_file=str(file_path),
                    source_domain=domain,
                    target_id='',
                    target_domain='',
                    message=f"File has no 'id' field"
                ))
                return
            
            # Check relationships section
            relationships = data.get('relationships', {})
            if not isinstance(relationships, dict):
                return
            
            for rel_type, links in relationships.items():
                self.validate_relationship(
                    source_id=source_id,
                    source_domain=domain,
                    rel_type=rel_type,
                    links=links,
                    file_path=file_path
                )
        
        except Exception as e:
            self.report.warnings.append(LinkIssue(
                severity='error',
                issue_type='parse_error',
                source_file=str(file_path),
                source_domain=domain,
                target_id='',
                target_domain='',
                message=f"Failed to parse file: {e}"
            ))
    
    def validate_relationship(self, source_id: str, source_domain: str, 
                            rel_type: str, links: Any, file_path: Path):
        """Validate a specific relationship type"""
        
        # Check if relationship type is valid for this domain
        if rel_type not in self.VALID_RELATIONSHIPS.get(source_domain, []):
            self.report.warnings.append(LinkIssue(
                severity='warning',
                issue_type='invalid_relationship_type',
                source_file=str(file_path),
                source_domain=source_domain,
                target_id='',
                target_domain='',
                message=f"Unknown relationship type '{rel_type}' for {source_domain} domain"
            ))
            return
        
        # regulatory_standards is special - doesn't link to other items
        if rel_type == 'regulatory_standards':
            self.validate_regulatory_standards(links, file_path, source_domain)
            return
        
        # Determine target domain
        target_domain = self.get_target_domain(source_domain, rel_type)
        if not target_domain:
            return
        
        # Validate each link
        if not isinstance(links, list):
            return
        
        for link in links:
            if not isinstance(link, dict):
                continue
            
            # Skip data-based items (items without 'id' field)
            target_id = link.get('id')
            if not target_id:
                # Data-based item - skip validation
                self.data_based_items += 1
                continue
            
            self.report.total_links += 1
            
            # Handle challenge type references
            link_type = link.get('type')
            if link_type == 'challenge':
                if target_id in self.challenge_library:
                    # Valid challenge reference
                    continue
                else:
                    self.report.broken_links.append(LinkIssue(
                        severity='error',
                        issue_type='missing_challenge_pattern',
                        source_file=str(file_path),
                        source_domain=source_domain,
                        target_id=target_id,
                        target_domain='challenges',
                        message=f"Challenge pattern '{target_id}' not found in ChallengePatterns.yaml"
                    ))
                continue
            
            # Check if target domain directory exists
            target_domain_path = self.frontmatter_root / target_domain
            if not target_domain_path.exists():
                self.report.broken_links.append(LinkIssue(
                    severity='error',
                    issue_type='missing_domain',
                    source_file=str(file_path),
                    source_domain=source_domain,
                    target_id=target_id,
                    target_domain=target_domain,
                    message=f"Target domain directory missing: {target_domain_path}"
                ))
                continue
            
            # Check if target file exists
            expected_file = target_domain_path / f"{target_id}.yaml"
            if not expected_file.exists():
                self.report.broken_links.append(LinkIssue(
                    severity='error',
                    issue_type='broken_link',
                    source_file=str(file_path),
                    source_domain=source_domain,
                    target_id=target_id,
                    target_domain=target_domain,
                    message=f"Target file not found: {expected_file}"
                ))
            
            # Check if target exists in index
            if target_id not in self.index[target_domain]:
                # Only report if file exists but ID not in index (malformed file)
                if expected_file.exists():
                    self.report.broken_links.append(LinkIssue(
                        severity='error',
                        issue_type='malformed_target',
                        source_file=str(file_path),
                        source_domain=source_domain,
                        target_id=target_id,
                        target_domain=target_domain,
                        message=f"Target file exists but ID not found: {expected_file}"
                    ))
            else:
                # Track link in graph for bidirectional checking
                self.link_graph[f"{source_domain}:{source_id}"][rel_type].append(target_id)
            
            # Validate URL format
            url = link.get('url')
            if url:
                self.validate_url(url, target_domain, target_id, file_path, source_domain)
    
    def validate_regulatory_standards(self, standards: Any, file_path: Path, source_domain: str):
        """Validate regulatory_standards structure"""
        if not isinstance(standards, list):
            self.report.warnings.append(LinkIssue(
                severity='warning',
                issue_type='invalid_structure',
                source_file=str(file_path),
                source_domain=source_domain,
                target_id='',
                target_domain='',
                message="regulatory_standards should be a list"
            ))
            return
        
        required_fields = ['name', 'description', 'url']
        for standard in standards:
            if not isinstance(standard, dict):
                continue
            
            for field in required_fields:
                if field not in standard:
                    self.report.warnings.append(LinkIssue(
                        severity='warning',
                        issue_type='missing_field',
                        source_file=str(file_path),
                        source_domain=source_domain,
                        target_id='',
                        target_domain='',
                        message=f"regulatory_standards entry missing '{field}' field"
                    ))
    
    def validate_url(self, url: str, domain: str, item_id: str, 
                    file_path: Path, source_domain: str):
        """Validate URL format matches expected pattern"""
        expected_pattern = f"/{domain}/"
        
        if not url.startswith(expected_pattern):
            self.report.invalid_urls.append(LinkIssue(
                severity='error',
                issue_type='invalid_url_format',
                source_file=str(file_path),
                source_domain=source_domain,
                target_id=item_id,
                target_domain=domain,
                message=f"URL '{url}' doesn't match expected pattern '{expected_pattern}...'"
            ))
    
    def get_target_domain(self, source_domain: str, rel_type: str) -> str:
        """Determine target domain from relationship type"""
        mappings = {
            'related_contaminants': 'contaminants',
            'related_materials': 'materials',
            'related_compounds': 'compounds',
            'related_settings': 'settings',
            'produces_compounds': 'compounds',
            'produced_by_contaminants': 'contaminants',
            'recommended_settings': 'settings',
            'suitable_materials': 'materials',
            'effective_contaminants': 'contaminants'
        }
        return mappings.get(rel_type, '')
    
    def check_bidirectional_consistency(self):
        """Check that bidirectional links are consistent"""
        print("\n🔄 Checking bidirectional link consistency...")
        
        for (source_domain, source_rel), (target_domain, target_rel) in self.BIDIRECTIONAL_MAPPINGS.items():
            for source_key, relationships in self.link_graph.items():
                if not source_key.startswith(f"{source_domain}:"):
                    continue
                
                source_id = source_key.split(':', 1)[1]
                target_ids = relationships.get(source_rel, [])
                
                for target_id in target_ids:
                    target_key = f"{target_domain}:{target_id}"
                    backlinks = self.link_graph.get(target_key, {}).get(target_rel, [])
                    
                    if source_id not in backlinks:
                        self.report.missing_backlinks.append(LinkIssue(
                            severity='warning',
                            issue_type='missing_backlink',
                            source_file=f"{source_domain}/{source_id}",
                            source_domain=source_domain,
                            target_id=target_id,
                            target_domain=target_domain,
                            message=f"{source_domain}:{source_id} links to {target_domain}:{target_id}, but backlink missing"
                        ))
    
    def find_orphaned_items(self):
        """Find items with no incoming or outgoing links"""
        print("\n🔍 Finding orphaned items...")
        
        for domain in self.DOMAINS:
            for item_id in self.index[domain]:
                key = f"{domain}:{item_id}"
                has_outgoing = len(self.link_graph.get(key, {})) > 0
                
                # Check for incoming links
                has_incoming = False
                for other_key, relationships in self.link_graph.items():
                    for rel_type, targets in relationships.items():
                        if item_id in targets:
                            has_incoming = True
                            break
                    if has_incoming:
                        break
                
                if not has_outgoing and not has_incoming:
                    self.report.orphaned_items.append(LinkIssue(
                        severity='info',
                        issue_type='orphaned_item',
                        source_file=f"{domain}/{item_id}",
                        source_domain=domain,
                        target_id=item_id,
                        target_domain=domain,
                        message=f"Item has no relationships (isolated)"
                    ))
    
    def print_report(self):
        """Print validation report to console"""
        print("\n" + "="*80)
        print("📊 FRONTMATTER LINK VALIDATION REPORT")
        print("="*80)
        
        print(f"\n📁 Files Scanned: {self.report.total_files}")
        print(f"🔗 Total Links: {self.report.total_links}")
        
        if self.data_based_items > 0:
            print(f"📋 Data-based items (skipped validation): {self.data_based_items}")
        
        if self.report.has_errors:
            print(f"\n❌ ERRORS: {self.report.error_count}")
            
            if self.report.broken_links:
                print(f"\n🔴 Broken Links ({len(self.report.broken_links)}):")
                for issue in self.report.broken_links[:10]:  # Show first 10
                    print(f"   • {issue.source_file} → {issue.target_domain}/{issue.target_id}")
                    print(f"     {issue.message}")
                if len(self.report.broken_links) > 10:
                    print(f"   ... and {len(self.report.broken_links) - 10} more")
            
            if self.report.invalid_urls:
                print(f"\n🔴 Invalid URLs ({len(self.report.invalid_urls)}):")
                for issue in self.report.invalid_urls[:10]:
                    print(f"   • {issue.source_file}")
                    print(f"     {issue.message}")
                if len(self.report.invalid_urls) > 10:
                    print(f"   ... and {len(self.report.invalid_urls) - 10} more")
        else:
            print("\n✅ No errors found!")
        
        if self.report.warning_count > 0:
            print(f"\n⚠️  WARNINGS: {self.report.warning_count}")
            
            if self.report.missing_backlinks:
                print(f"\n🟡 Missing Backlinks ({len(self.report.missing_backlinks)}):")
                for issue in self.report.missing_backlinks[:5]:
                    print(f"   • {issue.message}")
                if len(self.report.missing_backlinks) > 5:
                    print(f"   ... and {len(self.report.missing_backlinks) - 5} more")
            
            if self.report.orphaned_items:
                print(f"\n🟡 Orphaned Items ({len(self.report.orphaned_items)}):")
                for issue in self.report.orphaned_items[:5]:
                    print(f"   • {issue.source_domain}/{issue.target_id}")
                if len(self.report.orphaned_items) > 5:
                    print(f"   ... and {len(self.report.orphaned_items) - 5} more")
        
        print("\n" + "="*80)
    
    def export_markdown_report(self, output_path: Path):
        """Export detailed report as markdown"""
        with open(output_path, 'w') as f:
            f.write("# Frontmatter Link Validation Report\n\n")
            f.write(f"**Generated**: {Path.cwd()}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Files Scanned: {self.report.total_files}\n")
            f.write(f"- Total Links: {self.report.total_links}\n")
            f.write(f"- Errors: {self.report.error_count}\n")
            f.write(f"- Warnings: {self.report.warning_count}\n\n")
            
            if self.report.broken_links:
                f.write("## Broken Links\n\n")
                for issue in self.report.broken_links:
                    f.write(f"- **{issue.source_file}**\n")
                    f.write(f"  - Target: `{issue.target_domain}/{issue.target_id}`\n")
                    f.write(f"  - {issue.message}\n\n")
            
            if self.report.invalid_urls:
                f.write("## Invalid URLs\n\n")
                for issue in self.report.invalid_urls:
                    f.write(f"- **{issue.source_file}**\n")
                    f.write(f"  - {issue.message}\n\n")
            
            if self.report.missing_backlinks:
                f.write("## Missing Backlinks\n\n")
                for issue in self.report.missing_backlinks:
                    f.write(f"- {issue.message}\n")
            
            if self.report.orphaned_items:
                f.write("\n## Orphaned Items\n\n")
                for issue in self.report.orphaned_items:
                    f.write(f"- `{issue.source_domain}/{issue.target_id}`\n")
        
        print(f"📄 Detailed report exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Validate internal links in frontmatter files')
    parser.add_argument('--domain', choices=['materials', 'contaminants', 'compounds', 'settings'],
                       help='Validate only specific domain')
    parser.add_argument('--report', type=str, help='Export detailed report to markdown file')
    parser.add_argument('--fix', action='store_true', help='Attempt to auto-fix simple issues (not implemented)')
    
    args = parser.parse_args()
    
    # Try multiple possible frontmatter locations
    possible_paths = [
        Path('/Users/todddunning/Desktop/Z-Beam/z-beam/frontmatter'),
        Path('frontmatter'),
        Path('../z-beam/frontmatter'),
        Path(__file__).parent.parent.parent / 'z-beam' / 'frontmatter'
    ]
    
    frontmatter_root = None
    for path in possible_paths:
        if path.exists():
            frontmatter_root = path
            break
    
    if not frontmatter_root:
        print(f"❌ Frontmatter directory not found. Tried:")
        for path in possible_paths:
            print(f"   • {path}")
        return 1
    
    print(f"📂 Using frontmatter directory: {frontmatter_root.absolute()}\n")
    
    validator = FrontmatterLinkValidator(frontmatter_root)
    
    if args.domain:
        validator.build_index()
        validator.validate_domain(args.domain)
    else:
        validator.validate_all()
    
    validator.print_report()
    
    if args.report:
        validator.export_markdown_report(Path(args.report))
    
    # Return exit code based on errors
    return 1 if validator.report.has_errors else 0


if __name__ == '__main__':
    exit(main())
