#!/usr/bin/env python3
"""
Z-Beam Cleanup Manager

Standalone cleanup system decoupled from test framework.
Provides comprehensive project maintenance and file organization.

Usage:
    from cleanup import CleanupManager
    
    manager = CleanupManager(project_root)
    results = manager.scan()  # Safe dry-run scan
    report = manager.generate_report()  # Detailed report
"""

import json
from pathlib import Path
from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta


class CleanupManager:
    """Standalone cleanup manager for Z-Beam project maintenance"""
    
    def __init__(self, project_root: Path, dry_run: bool = True):
        """Initialize cleanup manager
        
        Args:
            project_root: Path to project root directory
            dry_run: If True, only identify files, don't delete them (RECOMMENDED)
        """
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load cleanup configuration with safety-first defaults"""
        return {
            # Critical system files/directories to NEVER touch
            'exclude_patterns': [
                '.git/',
                '__pycache__/',
                '.env',
                '*.pyc',
                '.DS_Store',
                'node_modules/',
                '.vscode/',
                '.idea/',
                'cleanup/',
                'tests/',
                '.gitignore',
                'requirements.txt',
                'package.json',
                'run.py'
            ],
            
            # Temporary file patterns (safe to identify)
            'temp_file_patterns': [
                '*.tmp',
                '*.temp',
                '*.bak',
                '*.backup',
                '*~',
                '.#*',
                '#*#',
                '*.swp',
                '*.swo'
            ],
            
            # Test files in wrong location
            'misplaced_test_patterns': [
                'test_*.py',
                '*_test.py', 
                'verify_*.py'
            ],
            
            # Documentation files that should be in docs/
            'misplaced_doc_patterns': [
                '*_DOCUMENTATION.md',
                '*_VERIFICATION.md', 
                '*_SUMMARY.md',
                '*_COMPLETE.md',
                'IMPLEMENTATION*.md',
                'TESTING*.md',
                'DYNAMIC*.md',
                'GROK*.md'
            ],
            
            # Core docs that should stay in root
            'keep_in_root_docs': [
                'README.md',
                'LICENSE.md', 
                'CHANGELOG.md',
                'CONTRIBUTING.md'
            ],
            
            # Component file types
            'component_extensions': ['.md', '.yaml', '.yml', '.json'],
            
            # Age threshold for outdated files
            'max_age_days': 30
        }
        
    def scan(self) -> Dict[str, Any]:
        """Perform comprehensive cleanup scan (always dry-run)
        
        Returns:
            Dictionary with scan results by category
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': True,  # Always true for safety
            'categories': {
                'dead_files': self._find_dead_files(),
                'temp_files': self._find_temp_files(),
                'empty_dirs': self._find_empty_dirs(),
                'misplaced_tests': self._find_misplaced_tests(),
                'misplaced_docs': self._find_misplaced_docs(),
                'broken_links': self._find_broken_links(),
                'outdated_content': self._find_outdated_content()
            }
        }
        
        # Calculate totals
        total_items = sum(
            len(items) for items in results['categories'].values()
            if isinstance(items, list)
        )
        results['total_issues'] = total_items
        
        return results
        
    def _find_dead_files(self) -> List[Tuple[str, str]]:
        """Find potentially dead/orphaned files"""
        dead_files = []
        
        # Look for common dead file patterns
        dead_patterns = [
            '*.orig',
            '*.rej', 
            'core.*',
            '*.core',
            '.DS_Store'
        ]
        
        for pattern in dead_patterns:
            for file_path in self.project_root.glob(f"**/{pattern}"):
                if self._is_excluded(file_path):
                    continue
                    
                dead_files.append((
                    str(file_path.relative_to(self.project_root)),
                    f"Dead file pattern: {pattern}"
                ))
                
        return dead_files
        
    def _find_temp_files(self) -> List[Tuple[str, str]]:
        """Find temporary files"""
        temp_files = []
        
        for pattern in self.config['temp_file_patterns']:
            for file_path in self.project_root.glob(f"**/{pattern}"):
                if self._is_excluded(file_path):
                    continue
                    
                temp_files.append((
                    str(file_path.relative_to(self.project_root)),
                    f"Temporary file: {pattern}"
                ))
                
        return temp_files
        
    def _find_empty_dirs(self) -> List[Tuple[str, str]]:
        """Find empty directories (excluding protected ones)"""
        empty_dirs = []
        
        for dir_path in self.project_root.rglob("*"):
            if not dir_path.is_dir():
                continue
                
            if self._is_excluded(dir_path):
                continue
                
            # Check if directory is truly empty
            try:
                if not any(dir_path.iterdir()):
                    empty_dirs.append((
                        str(dir_path.relative_to(self.project_root)),
                        "Empty directory"
                    ))
            except (PermissionError, OSError):
                continue
                
        return empty_dirs
        
    def _find_misplaced_tests(self) -> List[Tuple[str, str]]:
        """Find test files in root that should be in tests/"""
        misplaced = []
        
        for pattern in self.config['misplaced_test_patterns']:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    misplaced.append((
                        str(file_path.relative_to(self.project_root)),
                        "Test file in root - should be in tests/"
                    ))
                    
        return misplaced
        
    def _find_misplaced_docs(self) -> List[Tuple[str, str]]:
        """Find documentation files in root that should be in docs/"""
        misplaced = []
        
        for pattern in self.config['misplaced_doc_patterns']:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    # Skip if it's in the keep-in-root list
                    if file_path.name in self.config['keep_in_root_docs']:
                        continue
                        
                    misplaced.append((
                        str(file_path.relative_to(self.project_root)),
                        "Documentation file in root - should be in docs/"
                    ))
                    
        return misplaced
        
    def _find_broken_links(self) -> List[Tuple[str, str]]:
        """Find broken symbolic links"""
        broken_links = []
        
        for link_path in self.project_root.rglob("*"):
            if link_path.is_symlink() and not link_path.exists():
                if self._is_excluded(link_path):
                    continue
                    
                broken_links.append((
                    str(link_path.relative_to(self.project_root)),
                    "Broken symbolic link"
                ))
                
        return broken_links
        
    def _find_outdated_content(self) -> List[Tuple[str, str]]:
        """Find potentially outdated generated content"""
        outdated = []
        cutoff_date = datetime.now() - timedelta(days=self.config['max_age_days'])
        
        # Look in content directory for old files
        content_dir = self.project_root / "content"
        if content_dir.exists():
            for file_path in content_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                    
                if self._is_excluded(file_path):
                    continue
                    
                try:
                    if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_date:
                        outdated.append((
                            str(file_path.relative_to(self.project_root)),
                            f"Not modified in {self.config['max_age_days']} days"
                        ))
                except (OSError, ValueError):
                    continue
                    
        return outdated
        
    def _is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded from cleanup"""
        path_str = str(path.relative_to(self.project_root))
        
        for pattern in self.config['exclude_patterns']:
            if pattern in path_str or path_str.startswith(pattern.rstrip('/')):
                return True
                
        return False
        
    def generate_report(self, output_file: str = "cleanup_report.json") -> str:
        """Generate detailed cleanup report
        
        Args:
            output_file: Output filename for report (will be saved in cleanup/ directory)
            
        Returns:
            Path to generated report file
        """
        results = self.scan()
        
        # Enhanced report with metadata
        report = {
            'metadata': {
                'generated_at': results['timestamp'],
                'project_root': str(self.project_root),
                'total_issues': results['total_issues'],
                'scan_mode': 'dry_run_only',
                'safety_level': 'maximum'
            },
            'summary': {
                category: len(items) for category, items in results['categories'].items()
            },
            'detailed_results': results['categories'],
            'recommendations': self._generate_recommendations(results)
        }
        
        # Save report in cleanup directory to avoid cluttering root
        cleanup_dir = self.project_root / "cleanup"
        cleanup_dir.mkdir(exist_ok=True)
        report_path = cleanup_dir / output_file
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        return str(report_path)
        
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate safety recommendations based on scan results"""
        recommendations = []
        total = results['total_issues']
        
        if total == 0:
            recommendations.append("✅ Project is clean - no action needed")
        elif total <= 5:
            recommendations.append("🟡 Minor cleanup - review items manually")
        else:
            recommendations.append("🔴 Significant cleanup needed - review carefully")
            
        recommendations.extend([
            "📋 Always review items before taking action",
            "🚫 Never delete files without understanding their purpose", 
            "💾 Consider backing up important files first",
            "🔍 Use git status to check for uncommitted changes"
        ])
        
        return recommendations
        
    def get_summary(self) -> str:
        """Get a quick text summary of cleanup status"""
        results = self.scan()
        total = results['total_issues']
        
        if total == 0:
            return "✅ Project is clean"
        elif total <= 5:
            return f"🟡 {total} minor cleanup opportunities"
        else:
            return f"🔴 {total} cleanup opportunities found"


def main():
    """Command-line interface for cleanup manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Z-Beam Cleanup Manager")
    parser.add_argument("--scan", action="store_true", help="Run cleanup scan")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--summary", action="store_true", help="Show quick summary")
    
    args = parser.parse_args()
    
    manager = CleanupManager(Path.cwd())
    
    if args.summary or (not args.scan and not args.report):
        print(manager.get_summary())
    elif args.scan:
        results = manager.scan()
        print(f"Found {results['total_issues']} cleanup opportunities")
        for category, items in results['categories'].items():
            print(f"  {category}: {len(items)} items")
    elif args.report:
        report_path = manager.generate_report()
        print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
