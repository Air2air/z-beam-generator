#!/usr/bin/env python3
"""
Automatic Voice Fixer

Single command to automatically detect and fix ALL voice issues across
ALL content types (materials, regions, applications, contaminants, thesaurus).

Features:
- Auto-discovers all content types
- Detects all voice issues dynamically
- Fixes issues in priority order (critical → high → medium)
- Works for current and future content types automatically
- Progress tracking and detailed reporting
- Dry-run mode for safety
- Report-only mode for diagnostics
"""

import sys
from pathlib import Path
from typing import Dict, List, Set
import yaml
from dataclasses import dataclass, field
from enum import Enum
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.api.client_factory import APIClientFactory
from shared.api.client import GenerationRequest
from shared.voice.post_processor import VoicePostProcessor
from shared.voice.orchestrator import VoiceOrchestrator


class IssueType(Enum):
    """Types of voice issues that can be detected."""
    INDONESIAN_TEXT = "indonesian_text"
    ITALIAN_TEXT = "italian_text"
    TRANSLATION_ARTIFACT = "translation_artifact"
    LOW_AUTHENTICITY = "low_authenticity"
    NO_VOICE_MARKERS = "no_voice_markers"
    OVER_ENHANCED = "over_enhanced"


class IssueSeverity(Enum):
    """Severity levels for voice issues."""
    CRITICAL = "critical"  # Wrong language
    HIGH = "high"         # Translation artifacts
    MEDIUM = "medium"     # Low authenticity score
    LOW = "low"          # Minor issues


@dataclass
class ContentType:
    """Represents a content type directory."""
    name: str
    path: Path
    file_count: int = 0


@dataclass
class FileStats:
    """Statistics for a single file."""
    file_path: str
    total_fields: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    
    @property
    def total_issues(self) -> int:
        return self.critical_issues + self.high_issues + self.medium_issues + self.low_issues
    
    @property
    def severity_summary(self) -> str:
        parts = []
        if self.critical_issues:
            parts.append(f"critical: {self.critical_issues}")
        if self.high_issues:
            parts.append(f"high: {self.high_issues}")
        if self.medium_issues:
            parts.append(f"medium: {self.medium_issues}")
        if self.low_issues:
            parts.append(f"low: {self.low_issues}")
        return ", ".join(parts) if parts else "clean"


class UniversalVoiceFixer:
    """
    Universal voice fixer that works across ALL content types.
    
    Automatically discovers content directories and applies fixes
    without needing to know specific structure ahead of time.
    """
    
    def __init__(self, dry_run: bool = False, report_only: bool = False, detailed: bool = False):
        """
        Initialize universal fixer.
        
        Args:
            dry_run: Show what would be fixed without actually fixing
            report_only: Generate detailed report without fixing
            detailed: Show file-by-file breakdown in report
        """
        self.dry_run = dry_run
        self.report_only = report_only
        self.detailed = detailed
        self.api_client = APIClientFactory.create_client('grok')
        self.voice_processor = VoicePostProcessor(self.api_client)
        
        # Statistics
        self.stats = {
            'content_types_found': 0,
            'total_files': 0,
            'total_fields': 0,
            'issues_found': 0,
            'issues_fixed': 0,
            'issues_failed': 0,
            'by_action': {},
            'by_severity': {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
        
        # File-level tracking for detailed reports
        self.file_stats: Dict[str, FileStats] = {}
    
    def discover_content_types(self, base_dir: Path) -> List[ContentType]:
        """
        Automatically discover all content type directories.
        
        Looks for directories containing YAML files in frontmatter/.
        Works for current types (materials, regions, etc.) and future types.
        
        Args:
            base_dir: Base directory to search (e.g., frontmatter/)
        
        Returns:
            List of discovered content types
        """
        content_types = []
        
        print("🔍 Discovering content types...")
        
        # Look for subdirectories with YAML files
        for subdir in sorted(base_dir.iterdir()):
            if not subdir.is_dir():
                continue
            
            # Count YAML files
            yaml_files = list(subdir.glob('*.yaml'))
            if yaml_files:
                content_type = ContentType(
                    name=subdir.name,
                    path=subdir,
                    file_count=len(yaml_files)
                )
                content_types.append(content_type)
                print(f"   ✓ Found: {subdir.name} ({len(yaml_files)} files)")
        
        self.stats['content_types_found'] = len(content_types)
        return content_types
    
    def run_full_auto_fix(self, frontmatter_dir: Path):
        """
        Run complete automatic fix process.
        
        1. Discover all content types
        2. Scan all files for issues
        3. Fix issues in priority order (critical → high → medium)
        4. Generate report
        
        Args:
            frontmatter_dir: Base frontmatter directory
        """
        print('='*80)
        print('🤖 AUTOMATIC VOICE FIXER')
        print('='*80)
        
        mode_str = '📊 REPORT ONLY' if self.report_only else ('🔍 DRY RUN (no changes)' if self.dry_run else '✅ LIVE (will fix issues)')
        print(f'Mode: {mode_str}')
        if self.detailed:
            print('Detail: 📋 Full file-by-file breakdown')
        print()
        
        # Step 1: Discover content types
        content_types = self.discover_content_types(frontmatter_dir)
        
        if not content_types:
            print("\n⚠️  No content types found!")
            return
        
        print(f"\n📊 Found {len(content_types)} content type(s)")
        print()
        
        # Step 2: Process each content type
        for content_type in content_types:
            print('─'*80)
            print(f'📁 Processing: {content_type.name.upper()}')
            print('─'*80)
            
            self.process_content_type(content_type)
        
        # Step 3: Final report
        self.print_final_report()
    
    def process_content_type(self, content_type: ContentType):
        """
        Process all files in a content type directory.
        
        Args:
            content_type: Content type to process
        """
        yaml_files = sorted(content_type.path.glob('*.yaml'))
        self.stats['total_files'] += len(yaml_files)
        
        for yaml_file in yaml_files:
            self.process_file(yaml_file, content_type.name)
    
    def process_file(self, file_path: Path, content_type: str):
        """
        Process a single YAML file.
        
        Args:
            file_path: Path to YAML file
            content_type: Type of content (materials, regions, etc.)
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"   ⚠️  Error reading {file_path.name}: {e}")
            return
        
        # Initialize file stats
        file_key = file_path.stem
        file_stats = FileStats(file_path=file_key)
        
        # Get author country for voice validation
        author_country = self._get_author_country(data)
        
        # Extract all text fields
        text_fields = self._extract_text_fields(data)
        file_stats.total_fields = len(text_fields)
        self.stats['total_fields'] += len(text_fields)
        
        # Track if file needs saving
        file_modified = False
        fields_fixed_in_file = 0
        
        # Process each field in priority order
        for field_path, text in text_fields.items():
            # Validate field
            issues = self._detect_issues(text, author_country, file_path.stem)
            
            if not issues:
                continue
            
            # Track file-level stats by severity
            for issue in issues:
                if issue['severity'] == IssueSeverity.CRITICAL:
                    file_stats.critical_issues += 1
                elif issue['severity'] == IssueSeverity.HIGH:
                    file_stats.high_issues += 1
                elif issue['severity'] == IssueSeverity.MEDIUM:
                    file_stats.medium_issues += 1
                else:
                    file_stats.low_issues += 1
            
            self.stats['issues_found'] += len(issues)
            
            # Fix issues by priority: critical → high → medium
            for issue in sorted(issues, key=lambda x: x['priority']):
                action = issue['action']
                
                # Track action statistics
                self.stats['by_action'][action] = self.stats['by_action'].get(action, 0) + 1
                
                # Show what we're doing
                severity_icon = '❌' if issue['priority'] == 0 else '⚠️' if issue['priority'] == 1 else '📝'
                print(f"   {severity_icon} {file_path.stem} / {field_path}")
                print(f"      Issue: {issue['description']}")
                print(f"      Action: {action}")
                
                if self.dry_run:
                    print(f"      [DRY RUN] Would apply fix")
                    self.stats['issues_fixed'] += 1
                else:
                    # Apply fix
                    fixed_text = self._apply_fix(text, issue, author_country, file_path.stem)
                    
                    if fixed_text and fixed_text != text:
                        # Update the data structure
                        self._set_field_value(data, field_path, fixed_text)
                        file_modified = True
                        fields_fixed_in_file += 1
                        self.stats['issues_fixed'] += 1
                        print(f"      ✅ Fixed successfully")
                    else:
                        self.stats['issues_failed'] += 1
                        print(f"      ❌ Fix failed")
        
        # Save file stats
        self.file_stats[file_key] = file_stats
        
        # Save file if modified
        if file_modified and not self.dry_run:
            try:
                with open(file_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
                print(f"   💾 Saved {fields_fixed_in_file} fix(es) to {file_path.name}")
            except Exception as e:
                print(f"   ⚠️  Error saving {file_path.name}: {e}")
    
    def _get_author_country(self, data: Dict) -> str:
        """Extract author country from data."""
        if isinstance(data.get('author'), dict):
            return data['author'].get('country', 'united_states')
        return 'united_states'
    
    def _extract_text_fields(self, data: Dict) -> Dict[str, str]:
        """Recursively extract all text fields."""
        text_fields = {}
        
        def extract_recursive(obj, prefix=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_prefix = f'{prefix}.{key}' if prefix else key
                    extract_recursive(value, new_prefix)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_prefix = f'{prefix}[{i}]'
                    extract_recursive(item, new_prefix)
            elif isinstance(obj, str) and len(obj) > 50:
                text_fields[prefix] = obj
        
        extract_recursive(data)
        return text_fields
    
    def _detect_issues(self, text: str, country: str, material_name: str) -> List[Dict]:
        """
        Detect all issues in text.
        
        Returns list of issues with priority and severity:
        - Priority 0 / CRITICAL: Wrong language
        - Priority 1 / HIGH: Artifacts
        - Priority 2 / MEDIUM: Low authenticity
        """
        issues = []
        
        # 1. Check language (CRITICAL - Priority 0)
        lang_result = self.voice_processor.detect_language(text)
        if lang_result['language'] in ['indonesian', 'italian']:
            issues.append({
                'priority': 0,
                'severity': IssueSeverity.CRITICAL,
                'issue_type': IssueType.INDONESIAN_TEXT if lang_result['language'] == 'indonesian' else IssueType.ITALIAN_TEXT,
                'action': 'translate_to_english',
                'description': f"Text in {lang_result['language'].upper()}",
                'details': lang_result
            })
            self.stats['by_severity']['critical'] += 1
            return issues  # Stop if wrong language
        
        # 2. Check artifacts (HIGH - Priority 1)
        artifact_result = self.voice_processor.detect_translation_artifacts(text)
        if artifact_result['has_artifacts'] and artifact_result['severity'] in ['moderate', 'severe']:
            issues.append({
                'priority': 1,
                'severity': IssueSeverity.HIGH,
                'issue_type': IssueType.TRANSLATION_ARTIFACT,
                'action': 'remove_artifacts',
                'description': f"Translation artifacts ({artifact_result['severity']})",
                'details': artifact_result
            })
            self.stats['by_severity']['high'] += 1
        
        # 3. Check authenticity (MEDIUM - Priority 2)
        try:
            voice_orchestrator = VoiceOrchestrator(country=country)
            voice_indicators = voice_orchestrator.get_signature_phrases()
        except Exception:
            voice_indicators = []
        
        author_dict = {'country': country}
        auth_result = self.voice_processor.score_voice_authenticity(
            text=text,
            author=author_dict,
            voice_indicators=voice_indicators
        )
        
        if auth_result['authenticity_score'] < 70:
            issues.append({
                'priority': 2,
                'severity': IssueSeverity.MEDIUM,
                'issue_type': IssueType.LOW_AUTHENTICITY,
                'action': 'enhance_voice',
                'description': f"Low authenticity score ({auth_result['authenticity_score']:.0f}/100)",
                'details': auth_result
            })
            self.stats['by_severity']['medium'] += 1
        
        return issues
    
    def _apply_fix(self, text: str, issue: Dict, country: str, material_name: str) -> str:
        """
        Apply fix based on issue action.
        
        Args:
            text: Original text
            issue: Issue dictionary with action
            country: Author country
            material_name: Material name for context
        
        Returns:
            Fixed text (or original if fix failed)
        """
        action = issue['action']
        
        if action == 'translate_to_english':
            return self._translate_to_english(text, material_name, country)
        
        elif action == 'remove_artifacts':
            return self._remove_artifacts(text, issue['details'])
        
        elif action == 'enhance_voice':
            return self._enhance_voice(text, country)
        
        return text
    
    def _translate_to_english(self, text: str, material_name: str, country: str) -> str:
        """Translate text to English."""
        prompt = f"""You are translating technical content about laser cleaning from another language to English.

Material: {material_name}

REQUIREMENTS:
1. Translate to natural, fluent English
2. Preserve all technical terms and numerical values exactly
3. Maintain technical accuracy and detail level
4. Use clear, professional language
5. Keep the same structure and flow
6. Do NOT add voice markers - just translate directly

Text to translate:
{text}

Provide ONLY the English translation, nothing else."""

        try:
            request = GenerationRequest(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1000
            )
            
            response = self.api_client.generate(request)
            
            if response.success:
                return response.content.strip()
        except Exception as e:
            print(f"         API error: {e}")
        
        return text
    
    def _remove_artifacts(self, text: str, artifact_details: Dict) -> str:
        """Remove translation artifacts from text."""
        # Get artifact patterns
        patterns = artifact_details.get('patterns_found', [])
        
        # Build description for API
        artifact_list = []
        for pattern in patterns:
            if 'reduplication' in pattern:
                artifact_list.append(f"reduplication: {pattern['reduplication']}")
            if 'excessive_then' in pattern:
                artifact_list.append("excessive use of 'then'")
            if 'excessive_so' in pattern:
                artifact_list.append("excessive use of 'so'")
        
        if not artifact_list:
            return text
        
        prompt = f"""You are editing technical content to remove translation artifacts.

ISSUES TO FIX:
{chr(10).join('- ' + item for item in artifact_list)}

REQUIREMENTS:
1. Remove all reduplication (e.g., "very-very" → "very")
2. Reduce excessive conjunctions "then" and "so"
3. Preserve ALL technical terms and numbers
4. Maintain same meaning and accuracy
5. Use natural, fluent English
6. Do NOT add voice markers - just fix artifacts

Original text:
{text}

Provide ONLY the cleaned text, nothing else."""

        try:
            request = GenerationRequest(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1000
            )
            
            response = self.api_client.generate(request)
            
            if response.success:
                return response.content.strip()
        except Exception as e:
            print(f"         API error: {e}")
        
        return text
    
    def _enhance_voice(self, text: str, country: str) -> str:
        """Enhance text with authentic voice markers."""
        try:
            voice_orchestrator = VoiceOrchestrator(country=country)
            enhanced = self.voice_processor.enhance(text, voice_orchestrator)
            return enhanced
        except Exception as e:
            print(f"         Enhancement error: {e}")
            return text
    
    def _set_field_value(self, data: Dict, path: str, value: str):
        """Set a field value in nested dict using path."""
        parts = re.split(r'\.|\[|\]', path)
        parts = [p for p in parts if p]
        
        current = data
        for i, part in enumerate(parts[:-1]):
            if part.isdigit():
                current = current[int(part)]
            else:
                current = current[part]
        
        final_part = parts[-1]
        if final_part.isdigit():
            current[int(final_part)] = value
        else:
            current[final_part] = value
    
    def print_final_report(self):
        """Print comprehensive final report."""
        print('\n' + '='*80)
        print('📊 FINAL REPORT')
        print('='*80)
        
        print("\n📈 OVERALL STATISTICS:")
        print(f"   Content types processed: {self.stats['content_types_found']}")
        print(f"   Total files processed: {self.stats['total_files']}")
        print(f"   Total text fields checked: {self.stats['total_fields']}")
        print(f"   Issues found: {self.stats['issues_found']}")
        
        # Show severity breakdown
        if any(self.stats['by_severity'].values()):
            print("\n🚨 ISSUES BY SEVERITY:")
            severity_icons = {
                'critical': '❌',
                'high': '⚠️ ',
                'medium': '📝',
                'low': 'ℹ️ '
            }
            for severity, icon in severity_icons.items():
                count = self.stats['by_severity'][severity]
                if count > 0:
                    print(f"   {icon} {severity.upper()}: {count}")
        
        if self.dry_run:
            print("\n🔍 DRY RUN RESULTS:")
            print(f"   Would fix: {self.stats['issues_fixed']} issues")
        else:
            print("\n✅ FIX RESULTS:")
            print(f"   Successfully fixed: {self.stats['issues_fixed']}")
            print(f"   Failed: {self.stats['issues_failed']}")
            
            if self.stats['issues_fixed'] > 0:
                estimated_cost = self.stats['issues_fixed'] * 0.10
                print(f"   Estimated cost: ${estimated_cost:.2f}")
        
        if self.stats['by_action']:
            print("\n🔧 FIXES BY ACTION:")
            for action, count in sorted(self.stats['by_action'].items(), key=lambda x: -x[1]):
                action_label = action.replace('_', ' ').title()
                print(f"   • {action_label}: {count}")
        
        # Detailed file-by-file breakdown (if requested)
        if self.detailed and self.file_stats:
            self._print_detailed_breakdown()
        
        print('\n' + '='*80)
        
        if not self.dry_run and self.stats['issues_fixed'] > 0:
            print('✨ All fixes applied successfully!')
        elif self.dry_run:
            print('💡 Run without --dry-run to apply fixes')
    
    def _print_detailed_breakdown(self):
        """Print detailed file-by-file breakdown."""
        print("\n📋 DETAILED BREAKDOWN BY FILE:")
        
        # Group by severity
        critical_files = []
        high_files = []
        medium_files = []
        clean_files = []
        
        for file_path, stats in sorted(self.file_stats.items()):
            if stats.critical_issues > 0:
                critical_files.append((file_path, stats))
            elif stats.high_issues > 0:
                high_files.append((file_path, stats))
            elif stats.medium_issues > 0:
                medium_files.append((file_path, stats))
            elif stats.total_issues == 0:
                clean_files.append((file_path, stats))
        
        # Show critical files
        if critical_files:
            print(f"\n   ❌ CRITICAL ({len(critical_files)} files):")
            for file_path, stats in sorted(critical_files)[:10]:  # Show top 10
                print(f"      - {file_path}: {stats.severity_summary}")
            if len(critical_files) > 10:
                print(f"      ... and {len(critical_files) - 10} more")
        
        # Show high priority files
        if high_files:
            print(f"\n   ⚠️  HIGH ({len(high_files)} files):")
            for file_path, stats in sorted(high_files)[:10]:
                print(f"      - {file_path}: {stats.severity_summary}")
            if len(high_files) > 10:
                print(f"      ... and {len(high_files) - 10} more")
        
        # Show medium priority files
        if medium_files:
            print(f"\n   📝 MEDIUM ({len(medium_files)} files):")
            for file_path, stats in sorted(medium_files)[:5]:  # Show top 5
                print(f"      - {file_path}: {stats.severity_summary}")
            if len(medium_files) > 5:
                print(f"      ... and {len(medium_files) - 5} more")
        
        # Show clean files summary
        if clean_files:
            print(f"\n   ✅ CLEAN ({len(clean_files)} files with no issues)")
        else:
            print('✅ No issues found - all content has authentic voice!')
        
        print('='*80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automatically fix ALL voice issues across ALL content types',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run - see what would be fixed without making changes
  python3 scripts/voice/auto_voice_fixer.py --dry-run
  
  # Report only - detailed diagnostics without fixes
  python3 scripts/voice/auto_voice_fixer.py --report-only
  
  # Detailed breakdown - show file-by-file issues
  python3 scripts/voice/auto_voice_fixer.py --dry-run --detailed
  
  # Live run - actually fix all issues
  python3 scripts/voice/auto_voice_fixer.py
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be fixed without actually modifying files'
    )
    
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Generate detailed report without fixing (implies --dry-run --detailed)'
    )
    
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed file-by-file breakdown in report'
    )
    
    args = parser.parse_args()
    
    # report-only implies dry-run and detailed
    if args.report_only:
        args.dry_run = True
        args.detailed = True
    
    # Create fixer
    fixer = UniversalVoiceFixer(
        dry_run=args.dry_run,
        report_only=args.report_only,
        detailed=args.detailed
    )
    
    # Run on frontmatter directory
    frontmatter_dir = project_root / 'frontmatter'
    
    if not frontmatter_dir.exists():
        print(f"❌ Frontmatter directory not found: {frontmatter_dir}")
        sys.exit(1)
    
    # Run automatic fix
    fixer.run_full_auto_fix(frontmatter_dir)


if __name__ == '__main__':
    main()
