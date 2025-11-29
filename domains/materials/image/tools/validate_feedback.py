#!/usr/bin/env python3
"""
Feedback Validation Tool

Validates user feedback for contradictions and propagates changes across templates.
Runs automatically during generation or manually via CLI.

Usage:
    python3 domains/materials/image/tools/validate_feedback.py --check
    python3 domains/materials/image/tools/validate_feedback.py --apply
    python3 domains/materials/image/tools/validate_feedback.py --add "New feedback rule here"
"""

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass


@dataclass
class ConflictRule:
    """Defines mutually exclusive terms that indicate contradictions."""
    positive: Set[str]  # Terms that mean "do this"
    negative: Set[str]  # Terms that mean "don't do this"
    description: str


# Define contradiction patterns
CONFLICT_RULES = [
    ConflictRule(
        positive={'thick', 'heavy', 'caked', 'buildup', 'opaque', 'glob'},
        negative={'thin', 'light', 'subtle', 'film', 'patina', 'dusting'},
        description="Contamination thickness"
    ),
    ConflictRule(
        positive={'perfectly clean', '100% clean', 'spotless', 'pristine'},
        negative={'residual', 'traces', 'remnants', 'slight'},
        description="After-side cleanliness"
    ),
    ConflictRule(
        positive={'uniform', 'even', 'consistent'},
        negative={'varied', 'uneven', 'gradient', 'irregular'},
        description="Distribution uniformity"
    ),
    ConflictRule(
        positive={'sharp', 'defined', 'crisp'},
        negative={'feathered', 'gradual', 'soft', 'natural'},
        description="Boundary sharpness"
    ),
]

# Template files to check and update
TEMPLATE_PATHS = {
    'generation': [
        'generation/realism_physics.txt',
        'generation/forbidden_patterns.txt',
        'generation/contamination_rules.txt',
        'generation/micro_scale_details.txt',
        'generation/base_structure.txt',
    ],
    'validation': [
        'validation/physics_checklist.txt',
        'validation/prompt_aware_feedback.txt',
        'validation/red_flags.txt',
    ],
    'feedback': [
        'feedback/user_corrections.txt',
    ],
}


class FeedbackValidator:
    """Validates and propagates user feedback across templates."""
    
    def __init__(self, prompts_dir: Path = None):
        if prompts_dir is None:
            # Default to shared prompts directory
            self.prompts_dir = Path(__file__).parent.parent / 'prompts' / 'shared'
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self.conflicts_found: List[Tuple[str, str, str]] = []  # (file, term, conflict_with)
        self.templates_content: Dict[str, str] = {}
    
    def load_templates(self) -> None:
        """Load all template files."""
        for category, paths in TEMPLATE_PATHS.items():
            for rel_path in paths:
                full_path = self.prompts_dir / rel_path
                if full_path.exists():
                    self.templates_content[rel_path] = full_path.read_text()
    
    def check_text_for_conflicts(self, text: str, source: str) -> List[Tuple[str, str, str, str]]:
        """
        Check text for internal contradictions.
        
        Returns list of (source, term_found, conflicts_with, rule_description)
        """
        conflicts = []
        text_lower = text.lower()
        lines = text_lower.split('\n')
        
        for rule in CONFLICT_RULES:
            # Find which positive and negative terms are present
            pos_found = {t for t in rule.positive if t in text_lower}
            neg_found = {t for t in rule.negative if t in text_lower}
            
            # Check if both positive and negative are present without negation context
            if pos_found and neg_found:
                # Check if the positive terms are actually negated
                for pos_term in pos_found:
                    # Check each line for negation patterns
                    is_negated = False
                    
                    for line in lines:
                        if pos_term not in line:
                            continue
                        
                        # Expanded negation patterns
                        negation_patterns = [
                            f"never {pos_term}",
                            f"no {pos_term}",
                            f"not {pos_term}",
                            f"avoid {pos_term}",
                            f"don't {pos_term}",
                            f"- {pos_term}",  # In prohibition lists
                            f"prohibit {pos_term}",
                            f"reject {pos_term}",
                            f"- no {pos_term}",
                            f"- never {pos_term}",
                            f"must not {pos_term}",
                            f"must never {pos_term}",
                            f"cannot {pos_term}",
                            f"not {pos_term}",
                            f"never appear {pos_term}",
                            "prohibitions",  # If line contains prohibitions header
                            "avoid these",
                            "critical prohibitions",
                            "forbidden",
                            # Specific pattern: "never thick" means thick is forbidden
                            f"thin surface films only - never {pos_term}",
                            f"never {pos_term},",
                            f"{pos_term}, caked",  # Listed as prohibited item
                            f"{pos_term} or",  # "thick or caked"
                            f"or {pos_term}",  # "caked or thick"
                        ]
                        
                        # Also check if line is clearly a prohibition
                        prohibition_line_markers = [
                            line.startswith("- no "),
                            line.startswith("- never"),
                            line.startswith("- ") and "must not" in line,
                            "prohibit" in line,
                            "forbidden" in line,
                            "never appear" in line,
                            "only -" in line and pos_term in line.split("only -")[1] if "only -" in line else False,
                            line.startswith("- thick"),
                            line.startswith("- heavy"),
                            line.startswith("- caked"),
                            "unrealistic" in line and pos_term in line,
                            "= unrealistic" in line,
                        ]
                        
                        if any(p in line for p in negation_patterns) or any(prohibition_line_markers):
                            is_negated = True
                            break
                    
                    if not is_negated:
                        # This might still be a false positive - do a final check
                        # Look for the positive term appearing in a positive/encouraging context
                        positive_context_patterns = [
                            f"should be {pos_term}",
                            f"must be {pos_term}",
                            f"ensure {pos_term}",
                            f"make it {pos_term}",
                            f"add {pos_term}",
                            f"create {pos_term}",
                            f"show {pos_term}",
                        ]
                        
                        # Only flag if found in positive context
                        in_positive_context = any(p in text_lower for p in positive_context_patterns)
                        
                        if in_positive_context:
                            conflicts.append((
                                source,
                                pos_term,
                                ', '.join(neg_found),
                                rule.description
                            ))
        
        return conflicts
    
    def validate_feedback(self, new_feedback: str = None) -> Dict:
        """
        Validate feedback for contradictions.
        
        Args:
            new_feedback: Optional new feedback to validate before adding
            
        Returns:
            Dict with validation results
        """
        self.load_templates()
        
        results = {
            'valid': True,
            'conflicts': [],
            'warnings': [],
            'files_checked': len(self.templates_content),
        }
        
        # Check existing templates for internal conflicts
        for rel_path, content in self.templates_content.items():
            conflicts = self.check_text_for_conflicts(content, rel_path)
            if conflicts:
                results['conflicts'].extend(conflicts)
                results['valid'] = False
        
        # If new feedback provided, check it against existing templates
        if new_feedback:
            # Check new feedback for internal conflicts
            new_conflicts = self.check_text_for_conflicts(new_feedback, "NEW_FEEDBACK")
            if new_conflicts:
                results['conflicts'].extend(new_conflicts)
                results['valid'] = False
            
            # Check new feedback against each template
            for rel_path, content in self.templates_content.items():
                combined = content + "\n" + new_feedback
                cross_conflicts = self.check_text_for_conflicts(combined, f"NEW vs {rel_path}")
                
                # Filter to only show conflicts involving new feedback
                for conflict in cross_conflicts:
                    if conflict not in results['conflicts']:
                        results['conflicts'].append(conflict)
                        results['valid'] = False
        
        return results
    
    def add_feedback(self, new_rule: str, priority: str = "HIGH") -> Dict:
        """
        Add new feedback rule with validation.
        
        Args:
            new_rule: The new feedback rule to add
            priority: Priority level (CRITICAL, HIGH, MEDIUM)
            
        Returns:
            Dict with operation results
        """
        # First validate
        validation = self.validate_feedback(new_rule)
        
        if not validation['valid']:
            return {
                'success': False,
                'message': 'Conflicts detected - feedback not added',
                'conflicts': validation['conflicts'],
            }
        
        # Add to user_corrections.txt
        feedback_path = self.prompts_dir / 'feedback' / 'user_corrections.txt'
        
        if not feedback_path.exists():
            return {
                'success': False,
                'message': f'Feedback file not found: {feedback_path}',
            }
        
        current_content = feedback_path.read_text()
        
        # Format new rule
        new_section = f"\n## New Rule - {priority}\n{new_rule}\n"
        
        # Append to file
        feedback_path.write_text(current_content + new_section)
        
        return {
            'success': True,
            'message': 'Feedback added successfully',
            'file': str(feedback_path),
        }
    
    def propagate_changes(self, dry_run: bool = True) -> Dict:
        """
        Propagate feedback rules to related templates.
        
        This identifies rules in user_corrections.txt and ensures
        they're reflected in generation and validation templates.
        
        Args:
            dry_run: If True, only report what would change
            
        Returns:
            Dict with propagation results
        """
        self.load_templates()
        
        results = {
            'dry_run': dry_run,
            'changes': [],
            'already_consistent': [],
        }
        
        # Load user corrections
        feedback_path = self.prompts_dir / 'feedback' / 'user_corrections.txt'
        if not feedback_path.exists():
            return {'error': 'user_corrections.txt not found'}
        
        feedback_content = feedback_path.read_text()
        
        # Extract key rules from feedback
        key_patterns = self._extract_key_patterns(feedback_content)
        
        # Check each template for consistency
        for rel_path, content in self.templates_content.items():
            if 'feedback' in rel_path:
                continue  # Skip feedback files
            
            missing_patterns = []
            for pattern, description in key_patterns:
                if pattern.lower() not in content.lower():
                    missing_patterns.append((pattern, description))
            
            if missing_patterns:
                results['changes'].append({
                    'file': rel_path,
                    'missing': missing_patterns,
                })
            else:
                results['already_consistent'].append(rel_path)
        
        return results
    
    def _extract_key_patterns(self, feedback_content: str) -> List[Tuple[str, str]]:
        """Extract key enforceable patterns from feedback."""
        patterns = []
        
        # Look for specific enforcement keywords
        enforcement_markers = [
            (r'NEVER\s+([^\.]+)', 'prohibition'),
            (r'MUST\s+([^\.]+)', 'requirement'),
            (r'NO\s+([^\.]+)', 'prohibition'),
            (r'ALWAYS\s+([^\.]+)', 'requirement'),
        ]
        
        for marker_pattern, marker_type in enforcement_markers:
            matches = re.findall(marker_pattern, feedback_content, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                clean_match = match.strip()[:100]  # Limit length
                patterns.append((clean_match, marker_type))
        
        return patterns


def print_validation_results(results: Dict) -> None:
    """Print validation results in a readable format."""
    print("\n" + "=" * 60)
    print("📋 FEEDBACK VALIDATION RESULTS")
    print("=" * 60)
    
    print(f"\n📁 Files checked: {results.get('files_checked', 0)}")
    
    if results.get('valid', True):
        print("\n✅ No contradictions found - feedback is consistent")
    else:
        print(f"\n❌ Found {len(results.get('conflicts', []))} contradiction(s):")
        for source, term, conflicts_with, description in results.get('conflicts', []):
            print(f"\n   🚩 {description}")
            print(f"      File: {source}")
            print(f"      Found: '{term}'")
            print(f"      Conflicts with: '{conflicts_with}'")
    
    if results.get('warnings'):
        print("\n⚠️  Warnings:")
        for warning in results['warnings']:
            print(f"   • {warning}")
    
    print("\n" + "=" * 60)


def print_propagation_results(results: Dict) -> None:
    """Print propagation results."""
    print("\n" + "=" * 60)
    print("📋 FEEDBACK PROPAGATION RESULTS")
    print("=" * 60)
    
    if results.get('dry_run'):
        print("\n🔍 DRY RUN - No changes made")
    
    if results.get('already_consistent'):
        print(f"\n✅ Already consistent ({len(results['already_consistent'])} files):")
        for f in results['already_consistent']:
            print(f"   • {f}")
    
    if results.get('changes'):
        print(f"\n⚠️  Files needing updates ({len(results['changes'])}):")
        for change in results['changes']:
            print(f"\n   📄 {change['file']}")
            for pattern, ptype in change['missing']:
                print(f"      • Missing {ptype}: {pattern[:60]}...")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Validate and propagate user feedback across templates'
    )
    parser.add_argument(
        '--check', 
        action='store_true',
        help='Check for contradictions in existing templates'
    )
    parser.add_argument(
        '--apply',
        action='store_true', 
        help='Propagate feedback to related templates'
    )
    parser.add_argument(
        '--add',
        type=str,
        help='Add new feedback rule (validates first)'
    )
    parser.add_argument(
        '--priority',
        type=str,
        default='HIGH',
        choices=['CRITICAL', 'HIGH', 'MEDIUM'],
        help='Priority for new rule (default: HIGH)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Show what would change without making changes'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Actually apply changes (not dry run)'
    )
    
    args = parser.parse_args()
    
    validator = FeedbackValidator()
    
    if args.add:
        print("\n📝 Adding new feedback rule...")
        result = validator.add_feedback(args.add, args.priority)
        if result['success']:
            print(f"✅ {result['message']}")
            print(f"   File: {result['file']}")
        else:
            print(f"❌ {result['message']}")
            if result.get('conflicts'):
                for conflict in result['conflicts']:
                    print(f"   🚩 {conflict}")
    
    elif args.apply:
        dry_run = not args.force
        results = validator.propagate_changes(dry_run=dry_run)
        print_propagation_results(results)
    
    else:  # Default to --check
        results = validator.validate_feedback()
        print_validation_results(results)


# Integration function for use during generation
def validate_before_generation() -> bool:
    """
    Quick validation check to run before image generation.
    
    Returns:
        True if feedback is consistent, False if conflicts exist
    """
    validator = FeedbackValidator()
    results = validator.validate_feedback()
    
    if not results['valid']:
        print("\n⚠️  FEEDBACK VALIDATION WARNING:")
        print("   Contradictions detected in prompt templates.")
        print("   Run: python3 domains/materials/image/tools/validate_feedback.py --check")
        return False
    
    return True


if __name__ == '__main__':
    main()
