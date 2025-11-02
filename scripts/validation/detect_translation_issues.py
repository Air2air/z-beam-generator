#!/usr/bin/env python3
"""
Detect Translation Issues in Materials Frontmatter

Scans all materials frontmatter files to detect:
1. Non-English content (Indonesian, Italian, Chinese)
2. Translation artifacts (reduplication patterns like "very-very")
3. Voice authenticity issues

Usage:
    python3 scripts/validation/detect_translation_issues.py
    python3 scripts/validation/detect_translation_issues.py --material "Gold"
    python3 scripts/validation/detect_translation_issues.py --priority critical
"""

import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.voice.post_processor import VoicePostProcessor
from shared.api.client_factory import APIClientFactory

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class TranslationIssueDetector:
    """Detect translation issues in materials frontmatter"""
    
    def __init__(self):
        self.frontmatter_dir = Path("frontmatter/materials")
        
        # Initialize VoicePostProcessor for analysis
        try:
            api_client = APIClientFactory.create_client('grok')
            self.voice_processor = VoicePostProcessor(api_client)
        except Exception as e:
            logger.warning(f"Could not initialize API client: {e}")
            logger.warning("Will perform language detection only (no API-based validation)")
            self.voice_processor = None
    
    def scan_all_materials(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan all materials frontmatter files for translation issues.
        
        Returns:
            {
                'critical': [...],  # Wrong language
                'high': [...],      # Translation artifacts
                'medium': [...],    # No voice markers
                'good': [...]       # Authentic voice
            }
        """
        results = {
            'critical': [],
            'high': [],
            'medium': [],
            'good': []
        }
        
        if not self.frontmatter_dir.exists():
            logger.error(f"Frontmatter directory not found: {self.frontmatter_dir}")
            return results
        
        yaml_files = list(self.frontmatter_dir.glob("*.yaml"))
        logger.info(f"\n🔍 Scanning {len(yaml_files)} materials frontmatter files...\n")
        
        for yaml_file in sorted(yaml_files):
            material_name = yaml_file.stem.replace('-laser-cleaning', '').replace('-', ' ').title()
            issues = self.analyze_material(yaml_file, material_name)
            
            if issues:
                # Categorize by priority
                if issues['priority'] == 'critical':
                    results['critical'].append(issues)
                elif issues['priority'] == 'high':
                    results['high'].append(issues)
                elif issues['priority'] == 'medium':
                    results['medium'].append(issues)
                else:
                    results['good'].append(issues)
        
        return results
    
    def analyze_material(self, yaml_file: Path, material_name: str) -> Dict[str, Any]:
        """
        Analyze a single material for translation issues.
        
        Returns:
            {
                'material': str,
                'priority': str,
                'issues': List[Dict],
                'text_fields_checked': int
            }
        """
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load {yaml_file}: {e}")
            return None
        
        if not data:
            return None
        
        # Extract author info
        author_info = data.get('author', {})
        author = {
            'name': author_info.get('name', 'Unknown'),
            'country': author_info.get('country', 'Unknown')
        }
        
        issues_found = []
        text_fields_checked = 0
        
        # Check text fields
        text_fields = self._extract_text_fields(data)
        
        for field_path, text in text_fields.items():
            text_fields_checked += 1
            
            if not self.voice_processor:
                # Basic language detection only
                language = self._basic_language_detection(text)
                if language != 'english':
                    issues_found.append({
                        'field': field_path,
                        'issue_type': 'wrong_language',
                        'language': language,
                        'text_preview': text[:100]
                    })
                continue
            
            # Full voice processor analysis
            validation = self.voice_processor.validate_before_enhancement(text, author)
            
            if validation['action_required'] == 'translate':
                issues_found.append({
                    'field': field_path,
                    'issue_type': 'wrong_language',
                    'language': validation['details']['language']['language'],
                    'indicators': validation['details']['language']['indicators'],
                    'text_preview': text[:100]
                })
            elif validation['action_required'] == 'reprocess':
                artifacts = validation['details'].get('artifacts', {})
                issues_found.append({
                    'field': field_path,
                    'issue_type': 'translation_artifacts',
                    'severity': artifacts.get('severity', 'unknown'),
                    'artifacts': artifacts.get('patterns_found', []),
                    'text_preview': text[:100]
                })
            elif validation['action_required'] == 'enhance':
                authenticity = validation['details'].get('authenticity', {})
                if authenticity.get('authenticity_score', 100) < 50:
                    issues_found.append({
                        'field': field_path,
                        'issue_type': 'low_authenticity',
                        'score': authenticity.get('authenticity_score', 0),
                        'issues': authenticity.get('issues', [])
                    })
        
        # Determine priority
        if any(i['issue_type'] == 'wrong_language' for i in issues_found):
            priority = 'critical'
        elif any(i['issue_type'] == 'translation_artifacts' for i in issues_found):
            priority = 'high'
        elif any(i['issue_type'] == 'low_authenticity' for i in issues_found):
            priority = 'medium'
        else:
            priority = 'good'
        
        return {
            'material': material_name,
            'file': str(yaml_file),
            'author': author,
            'priority': priority,
            'issues': issues_found,
            'text_fields_checked': text_fields_checked
        }
    
    def _extract_text_fields(self, data: Dict) -> Dict[str, str]:
        """
        Extract ALL text fields from frontmatter data.
        
        Recursively scans entire YAML structure for string fields >50 characters.
        This ensures no text fields are missed during validation.
        """
        text_fields = {}
        
        def extract_recursive(obj, prefix=''):
            """Recursively find all string fields"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_prefix = f'{prefix}.{key}' if prefix else key
                    extract_recursive(value, new_prefix)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_prefix = f'{prefix}[{i}]'
                    extract_recursive(item, new_prefix)
            elif isinstance(obj, str) and len(obj) > 50:
                # Only include substantial text (>50 chars) - filters out short labels/IDs
                text_fields[prefix] = obj
        
        extract_recursive(data)
        return text_fields
    
    def _basic_language_detection(self, text: str) -> str:
        """Basic language detection without API"""
        indonesian_words = {'yang', 'dengan', 'untuk', 'dari', 'dapat', 'sangat', 'pada', 'adalah'}
        italian_words = {'che', 'con', 'per', 'della', 'questo', 'molto', 'infatti'}
        
        text_lower = text.lower()
        words = set(text_lower.split())
        
        if len(words & indonesian_words) >= 3:
            return 'indonesian'
        elif len(words & italian_words) >= 3:
            return 'italian'
        return 'english'
    
    def print_report(self, results: Dict[str, List[Dict]]):
        """Print formatted report"""
        total = sum(len(v) for v in results.values())
        
        print("\n" + "=" * 80)
        print("TRANSLATION ISSUES DETECTION REPORT")
        print("=" * 80)
        print(f"\nTotal Materials Scanned: {total}")
        print(f"  ❌ CRITICAL (wrong language): {len(results['critical'])}")
        print(f"  ⚠️  HIGH (translation artifacts): {len(results['high'])}")
        print(f"  📝 MEDIUM (low authenticity): {len(results['medium'])}")
        print(f"  ✅ GOOD (authentic voice): {len(results['good'])}")
        
        # Critical issues
        if results['critical']:
            print("\n" + "-" * 80)
            print("❌ CRITICAL ISSUES (Wrong Language)")
            print("-" * 80)
            for item in results['critical']:
                print(f"\n📄 {item['material']}")
                print(f"   Author: {item['author']['name']} ({item['author']['country']})")
                for issue in item['issues']:
                    if issue['issue_type'] == 'wrong_language':
                        print(f"   ❌ {issue['field']}: Text in {issue['language'].upper()}")
                        if 'indicators' in issue:
                            print(f"      Detected words: {', '.join(issue['indicators'][:5])}")
                        print(f"      Preview: {issue['text_preview']}...")
        
        # High priority issues
        if results['high']:
            print("\n" + "-" * 80)
            print("⚠️  HIGH PRIORITY (Translation Artifacts)")
            print("-" * 80)
            for item in results['high'][:10]:  # Show first 10
                print(f"\n📄 {item['material']}")
                for issue in item['issues']:
                    if issue['issue_type'] == 'translation_artifacts':
                        print(f"   ⚠️  {issue['field']}: {issue['severity']} severity")
                        for artifact in issue['artifacts']:
                            print(f"      - {artifact['type']}: {', '.join(str(e) for e in artifact['examples'][:3])}")
            
            if len(results['high']) > 10:
                print(f"\n   ... and {len(results['high']) - 10} more materials with artifacts")
        
        # Summary
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        if results['critical']:
            print(f"\n1. IMMEDIATE ACTION: Translate {len(results['critical'])} materials to English")
            print(f"   Cost estimate: ~${len(results['critical']) * 0.10:.2f}")
        if results['high']:
            print(f"\n2. HIGH PRIORITY: Reprocess {len(results['high'])} materials to remove artifacts")
            print(f"   Cost estimate: ~${len(results['high']) * 0.10:.2f}")
        if results['medium']:
            print(f"\n3. MEDIUM PRIORITY: Enhance {len(results['medium'])} materials with voice markers")
            print(f"   Cost estimate: ~${len(results['medium']) * 0.10:.2f}")
        
        total_cost = (len(results['critical']) + len(results['high']) + len(results['medium'])) * 0.10
        print(f"\nTotal estimated cost: ~${total_cost:.2f}")
        print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Detect translation issues in materials frontmatter')
    parser.add_argument('--material', help='Analyze specific material only')
    parser.add_argument('--priority', choices=['critical', 'high', 'medium', 'good'],
                       help='Show only specific priority level')
    args = parser.parse_args()
    
    detector = TranslationIssueDetector()
    
    if args.material:
        # Analyze single material
        material_slug = args.material.lower().replace(' ', '-')
        yaml_file = Path(f"frontmatter/materials/{material_slug}-laser-cleaning.yaml")
        
        if not yaml_file.exists():
            logger.error(f"Material file not found: {yaml_file}")
            sys.exit(1)
        
        result = detector.analyze_material(yaml_file, args.material)
        if result:
            print(f"\n📄 {result['material']}")
            print(f"   Priority: {result['priority'].upper()}")
            print(f"   Text fields checked: {result['text_fields_checked']}")
            print(f"   Issues found: {len(result['issues'])}")
            
            for issue in result['issues']:
                print(f"\n   {issue['issue_type']}:")
                for key, value in issue.items():
                    if key != 'issue_type':
                        print(f"     {key}: {value}")
    else:
        # Scan all materials
        results = detector.scan_all_materials()
        
        # Filter by priority if specified
        if args.priority:
            filtered_results = {
                'critical': [],
                'high': [],
                'medium': [],
                'good': []
            }
            filtered_results[args.priority] = results[args.priority]
            results = filtered_results
        
        detector.print_report(results)


if __name__ == '__main__':
    main()
