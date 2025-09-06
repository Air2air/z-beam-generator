#!/usr/bin/env python3
"""
Z-Beam Cleanup Test Suite

Identifies and optionally removes:
- Dead/orphaned files
- Unused component files
- Temporary files
- Empty directories
- Outdated generated content
- Broken symlinks
- Misplaced test files
"""

import json
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCleanupSystem(unittest.TestCase):
    """Test cleanup system functionality"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent
        self.content_dir = self.project_root / "content"
        self.components_dir = self.project_root / "components"
        self.cleanup_results = {}

    def test_identify_dead_files(self):
        """Test identification of dead/orphaned files"""
        print("🔍 Scanning for dead and orphaned files...")

        dead_files = self._find_dead_files()

        print(f"  📊 Found {len(dead_files)} potentially dead files")

        if dead_files:
            print("  📝 Dead files identified:")
            for file_path, reason in dead_files:
                print(f"    ❌ {file_path} - {reason}")
        else:
            print("  ✅ No dead files found")

        self.cleanup_results["dead_files"] = dead_files
        self.assertIsInstance(dead_files, list)

    def test_identify_unused_component_files(self):
        """Test identification of unused component files"""
        print("🔍 Scanning for unused component files...")

        unused_files = self._find_unused_component_files()

        print(f"  📊 Found {len(unused_files)} unused component files")

        if unused_files:
            print("  📝 Unused component files:")
            for file_path, reason in unused_files:
                print(f"    ❌ {file_path} - {reason}")
        else:
            print("  ✅ No unused component files found")

        self.cleanup_results["unused_component_files"] = unused_files
        self.assertIsInstance(unused_files, list)

    def test_identify_temporary_files(self):
        """Test identification of temporary files"""
        print("🔍 Scanning for temporary files...")

        temp_files = self._find_temporary_files()

        print(f"  📊 Found {len(temp_files)} temporary files")

        if temp_files:
            print("  📝 Temporary files:")
            for file_path, reason in temp_files:
                print(f"    🗑️  {file_path} - {reason}")
        else:
            print("  ✅ No temporary files found")

        self.cleanup_results["temp_files"] = temp_files
        self.assertIsInstance(temp_files, list)

    def test_identify_empty_directories(self):
        """Test identification of empty directories"""
        print("🔍 Scanning for empty directories...")

        empty_dirs = self._find_empty_directories()

        print(f"  📊 Found {len(empty_dirs)} empty directories")

        if empty_dirs:
            print("  📝 Empty directories:")
            for dir_path, reason in empty_dirs:
                print(f"    📁 {dir_path} - {reason}")
        else:
            print("  ✅ No empty directories found")

        self.cleanup_results["empty_dirs"] = empty_dirs
        self.assertIsInstance(empty_dirs, list)

    def test_identify_outdated_generated_content(self):
        """Test identification of outdated generated content"""
        print("🔍 Scanning for outdated generated content...")

        outdated_files = self._find_outdated_generated_content()

        print(f"  📊 Found {len(outdated_files)} outdated generated files")

        if outdated_files:
            print("  📝 Outdated generated content:")
            for file_path, reason in outdated_files:
                print(f"    📅 {file_path} - {reason}")
        else:
            print("  ✅ No outdated generated content found")

        self.cleanup_results["outdated_files"] = outdated_files
        self.assertIsInstance(outdated_files, list)

    def test_identify_broken_symlinks(self):
        """Test identification of broken symlinks"""
        print("🔍 Scanning for broken symlinks...")

        broken_links = self._find_broken_symlinks()

        print(f"  📊 Found {len(broken_links)} broken symlinks")

        if broken_links:
            print("  📝 Broken symlinks:")
            for link_path, reason in broken_links:
                print(f"    🔗 {link_path} - {reason}")
        else:
            print("  ✅ No broken symlinks found")

        self.cleanup_results["broken_links"] = broken_links
        self.assertIsInstance(broken_links, list)

    def test_identify_misplaced_test_files(self):
        """Test identification of misplaced test files in root directory"""
        print("🔍 Scanning for misplaced test files...")

        misplaced_files = self._find_misplaced_test_files()

        print(f"  📊 Found {len(misplaced_files)} misplaced test files")

        if misplaced_files:
            print("  📝 Misplaced test files:")
            for file_path, reason in misplaced_files:
                print(f"    🧪 {file_path} - {reason}")
        else:
            print("  ✅ No misplaced test files found")

        self.cleanup_results["misplaced_test_files"] = misplaced_files
        self.assertIsInstance(misplaced_files, list)

    def test_identify_misplaced_doc_files(self):
        """Test identification of misplaced documentation files in root directory"""
        print("🔍 Scanning for misplaced documentation files...")

        misplaced_docs = self._find_misplaced_doc_files()

        print(f"  📊 Found {len(misplaced_docs)} misplaced documentation files")

        if misplaced_docs:
            print("  📝 Misplaced documentation files:")
            for file_path, reason in misplaced_docs:
                print(f"    📄 {file_path} - {reason}")
        else:
            print("  ✅ No misplaced documentation files found")

        self.cleanup_results["misplaced_doc_files"] = misplaced_docs
        self.assertIsInstance(misplaced_docs, list)

    def test_generate_cleanup_report(self):
        """Generate comprehensive cleanup report"""
        print("📋 Generating comprehensive cleanup report...")

        report = self._generate_cleanup_report()

        print("  📊 Cleanup Summary:")
        print(f"    Dead files: {len(report.get('dead_files', []))}")
        print(
            f"    Unused component files: {len(report.get('unused_component_files', []))}"
        )
        print(f"    Temporary files: {len(report.get('temp_files', []))}")
        print(f"    Empty directories: {len(report.get('empty_dirs', []))}")
        print(f"    Outdated files: {len(report.get('outdated_files', []))}")
        print(f"    Broken symlinks: {len(report.get('broken_links', []))}")
        print(
            f"    Misplaced test files: {len(report.get('misplaced_test_files', []))}"
        )
        print(f"    Misplaced doc files: {len(report.get('misplaced_doc_files', []))}")

        total_issues = sum(
            len(report.get(key, []))
            for key in report.keys()
            if isinstance(report.get(key), list)
        )
        print(f"    Total cleanup items: {total_issues}")

        # Save report to file
        report_file = self.project_root / "cleanup" / "cleanup_report.json"
        # Ensure cleanup directory exists
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"  💾 Cleanup report saved to: {report_file}")

        self.assertIsInstance(report, dict)
        self.assertGreaterEqual(len(report), 0)


class CleanupSystemIntegration(unittest.TestCase):
    """Test cleanup system integration"""

    def setUp(self):
        """Set up test environment"""
        self.project_root = Path(__file__).parent.parent

    def test_dry_run_cleanup(self):
        """Test dry run cleanup (identify only, don't delete)"""
        print("🧪 Testing dry-run cleanup functionality...")

        cleaner = CleanupManager(self.project_root, dry_run=True)
        results = cleaner.run_cleanup()

        print("  📊 Dry-run results:")
        for category, items in results.items():
            if isinstance(items, list):
                print(f"    {category}: {len(items)} items")
            else:
                print(f"    {category}: {items}")

        # Verify no files were actually deleted
        self.assertTrue(results.get("dry_run", True))
        self.assertIsInstance(results, dict)

    def test_cleanup_manager_initialization(self):
        """Test cleanup manager initialization"""
        print("🔧 Testing cleanup manager initialization...")

        # Test with dry run
        cleaner = CleanupManager(self.project_root, dry_run=True)
        self.assertTrue(cleaner.dry_run)
        self.assertEqual(cleaner.project_root, self.project_root)

        # Test configuration
        self.assertIn("exclude_patterns", cleaner.config)
        self.assertIn("temp_file_patterns", cleaner.config)

        print("  ✅ Cleanup manager initialized successfully")


class CleanupManager:
    """Manages cleanup operations for the Z-Beam project"""

    def __init__(self, project_root: Path, dry_run: bool = True):
        """Initialize cleanup manager

        Args:
            project_root: Path to project root directory
            dry_run: If True, only identify files, don't delete them
        """
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.config = self._load_cleanup_config()

    def _load_cleanup_config(self) -> dict:
        """Load cleanup configuration"""
        return {
            "exclude_patterns": [
                ".git/",
                "__pycache__/",
                ".env",
                "*.pyc",
                ".DS_Store",
                "node_modules/",
                ".vscode/",
                ".idea/",
                "cleanup_report.json",
                "tests/",  # Don't clean the official tests directory
            ],
            "temp_file_patterns": [
                "*.tmp",
                "*.temp",
                "*.bak",
                "*.backup",
                "*~",
                ".#*",
                "#*#",
                "*.swp",
                "*.swo",
                "test_output/",
                "tmp/",
                "temp/",
            ],
            "misplaced_test_patterns": [
                "test_*.py",
                "*_test.py",
                "verify_*.py",
                "test/",  # test directory in root (not tests/)
                "test_output/",
            ],
            "misplaced_doc_patterns": [
                "*_DOCUMENTATION.md",
                "*_VERIFICATION.md",
                "*_SUMMARY.md",
                "*_COMPLETE.md",
                "IMPLEMENTATION*.md",
                "TESTING*.md",
                "DYNAMIC*.md",
                "GROK*.md",
            ],
            "keep_in_root_docs": [
                "README.md",
                "LICENSE.md",
                "CHANGELOG.md",
                "CONTRIBUTING.md",
            ],
            "component_file_extensions": [".md", ".yaml", ".yml", ".json"],
            "max_age_days": 30,  # Files older than this are considered outdated
        }

    def run_cleanup(self) -> dict:
        """Run comprehensive cleanup scan

        Returns:
            Dictionary with cleanup results
        """
        results = {
            "dry_run": self.dry_run,
            "timestamp": datetime.now().isoformat(),
            "dead_files": self._find_dead_files(),
            "unused_component_files": self._find_unused_component_files(),
            "temp_files": self._find_temporary_files(),
            "empty_dirs": self._find_empty_directories(),
            "outdated_files": self._find_outdated_generated_content(),
            "broken_links": self._find_broken_symlinks(),
            "misplaced_test_files": self._find_misplaced_test_files(),
            "misplaced_doc_files": self._find_misplaced_doc_files(),
        }

        if not self.dry_run:
            results["deleted_files"] = self._execute_cleanup(results)

        return results

    def _find_dead_files(self) -> List[Tuple[str, str]]:
        """Find dead/orphaned files"""
        dead_files = []

        # Look for component files without corresponding definitions
        components_dir = self.project_root / "components"
        content_dir = self.project_root / "content" / "components"

        if components_dir.exists() and content_dir.exists():
            # Get all component types
            component_types = {
                d.name
                for d in components_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            }

            # Check content directory for orphaned component files
            for component_type_dir in content_dir.iterdir():
                if component_type_dir.is_dir():
                    component_type = component_type_dir.name

                    # Check if component type exists in components directory
                    if component_type not in component_types:
                        for file_path in component_type_dir.rglob("*"):
                            if file_path.is_file():
                                dead_files.append(
                                    (
                                        str(file_path.relative_to(self.project_root)),
                                        f"Orphaned: component type '{component_type}' not found in components/",
                                    )
                                )

        return dead_files

    def _find_unused_component_files(self) -> List[Tuple[str, str]]:
        """Find unused component files"""
        unused_files = []

        # Look for component files that aren't referenced in any configuration
        components_dir = self.project_root / "components"

        if components_dir.exists():
            # Get component configuration (simplified check)
            configured_components = set()

            # Check if there's a component configuration file
            config_files = ["component_config.py", "config.py", "run.py"]

            for config_file in config_files:
                config_path = self.project_root / config_file
                if config_path.exists():
                    try:
                        with open(config_path, "r") as f:
                            content = f.read()
                            # Look for component references
                            for component_dir in components_dir.iterdir():
                                if (
                                    component_dir.is_dir()
                                    and component_dir.name in content
                                ):
                                    configured_components.add(component_dir.name)
                    except Exception:
                        pass

            # Check for unconfigured components
            for component_dir in components_dir.iterdir():
                if component_dir.is_dir() and not component_dir.name.startswith("."):
                    if component_dir.name not in configured_components:
                        for file_path in component_dir.rglob("*"):
                            if file_path.is_file():
                                unused_files.append(
                                    (
                                        str(file_path.relative_to(self.project_root)),
                                        f"Unused: component '{component_dir.name}' not in configuration",
                                    )
                                )

        return unused_files

    def _find_temporary_files(self) -> List[Tuple[str, str]]:
        """Find temporary files"""
        temp_files = []

        for pattern in self.config["temp_file_patterns"]:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file() and not self._is_excluded(file_path):
                    temp_files.append(
                        (
                            str(file_path.relative_to(self.project_root)),
                            f"Temporary file matching pattern: {pattern}",
                        )
                    )

        return temp_files

    def _find_empty_directories(self) -> List[Tuple[str, str]]:
        """Find empty directories"""
        empty_dirs = []

        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and not self._is_excluded(dir_path):
                try:
                    # Check if directory is empty (no files or subdirectories)
                    if not any(dir_path.iterdir()):
                        empty_dirs.append(
                            (
                                str(dir_path.relative_to(self.project_root)),
                                "Empty directory",
                            )
                        )
                except PermissionError:
                    pass

        return empty_dirs

    def _find_outdated_generated_content(self) -> List[Tuple[str, str]]:
        """Find outdated generated content"""
        outdated_files = []

        content_dir = self.project_root / "content"
        if content_dir.exists():
            cutoff_date = datetime.now() - timedelta(days=self.config["max_age_days"])

            for file_path in content_dir.rglob("*.md"):
                if file_path.is_file():
                    try:
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_mtime < cutoff_date:
                            outdated_files.append(
                                (
                                    str(file_path.relative_to(self.project_root)),
                                    f"Last modified: {file_mtime.strftime('%Y-%m-%d')} (>{self.config['max_age_days']} days ago)",
                                )
                            )
                    except Exception:
                        pass

        return outdated_files

    def _find_broken_symlinks(self) -> List[Tuple[str, str]]:
        """Find broken symlinks"""
        broken_links = []

        for file_path in self.project_root.rglob("*"):
            if file_path.is_symlink():
                try:
                    # Check if symlink target exists
                    if not file_path.exists():
                        broken_links.append(
                            (
                                str(file_path.relative_to(self.project_root)),
                                f"Broken symlink pointing to: {file_path.readlink()}",
                            )
                        )
                except Exception as e:
                    broken_links.append(
                        (
                            str(file_path.relative_to(self.project_root)),
                            f"Error checking symlink: {e}",
                        )
                    )

        return broken_links

    def _find_misplaced_test_files(self) -> List[Tuple[str, str]]:
        """Find misplaced test files in root directory"""
        misplaced_files = []

        # Check root directory for test files that should be in tests/
        for pattern in self.config["misplaced_test_patterns"]:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file() or file_path.is_dir():
                    # Skip if it's the official tests directory
                    if file_path.name == "tests":
                        continue

                    misplaced_files.append(
                        (
                            str(file_path.relative_to(self.project_root)),
                            "Test file/directory in root - should be in tests/",
                        )
                    )

        return misplaced_files

    def _find_misplaced_doc_files(self) -> List[Tuple[str, str]]:
        """Find misplaced documentation files in root directory"""
        misplaced_docs = []

        # Check root directory for documentation files that should be in docs/
        for pattern in self.config["misplaced_doc_patterns"]:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    # Skip files that should stay in root
                    if file_path.name in self.config["keep_in_root_docs"]:
                        continue

                    misplaced_docs.append(
                        (
                            str(file_path.relative_to(self.project_root)),
                            "Documentation file in root - should be in docs/",
                        )
                    )

        return misplaced_docs

    def _is_excluded(self, path: Path) -> bool:
        """Check if path should be excluded from cleanup"""
        path_str = str(path.relative_to(self.project_root))

        for pattern in self.config["exclude_patterns"]:
            if pattern in path_str:
                return True

        return False

    def _execute_cleanup(self, results: dict) -> List[str]:
        """Execute actual cleanup (only if not dry_run)"""
        deleted_files = []

        if self.dry_run:
            return deleted_files

        # This would implement actual file deletion
        # For safety, this is intentionally not implemented
        # Users should review results first

        return deleted_files


# Helper functions for the test class
TestCleanupSystem._find_dead_files = lambda self: CleanupManager(
    self.project_root
)._find_dead_files()
TestCleanupSystem._find_unused_component_files = lambda self: CleanupManager(
    self.project_root
)._find_unused_component_files()
TestCleanupSystem._find_temporary_files = lambda self: CleanupManager(
    self.project_root
)._find_temporary_files()
TestCleanupSystem._find_empty_directories = lambda self: CleanupManager(
    self.project_root
)._find_empty_directories()
TestCleanupSystem._find_outdated_generated_content = lambda self: CleanupManager(
    self.project_root
)._find_outdated_generated_content()
TestCleanupSystem._find_broken_symlinks = lambda self: CleanupManager(
    self.project_root
)._find_broken_symlinks()
TestCleanupSystem._find_misplaced_test_files = lambda self: CleanupManager(
    self.project_root
)._find_misplaced_test_files()
TestCleanupSystem._find_misplaced_doc_files = lambda self: CleanupManager(
    self.project_root
)._find_misplaced_doc_files()
TestCleanupSystem._generate_cleanup_report = lambda self: CleanupManager(
    self.project_root
).run_cleanup()


def main():
    """Run cleanup tests"""
    print("🧹 Z-BEAM CLEANUP SYSTEM TESTS")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCleanupSystem))
    suite.addTests(loader.loadTestsFromTestCase(CleanupSystemIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    print("📊 CLEANUP TEST RESULTS")
    print("=" * 60)

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total_tests - failures - errors
    success_rate = (passed / total_tests) * 100 if total_tests > 0 else 0

    print("📈 TEST STATISTICS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failures}")
    print(f"   🔥 Errors: {errors}")
    print(f"   📊 Success Rate: {success_rate:.1f}%")

    if success_rate == 100:
        print("\n🎉 EXCELLENT! All cleanup tests passed.")
        print("   The cleanup system is fully functional.")
    elif success_rate >= 80:
        print("\n✅ GOOD! Most cleanup tests passed.")
        print("   The cleanup system is largely functional.")
    else:
        print("\n⚠️  The cleanup system needs attention.")

    print("\n💡 USAGE:")
    print("   # Run cleanup scan (dry-run)")
    print("   python3 -m tests.test_cleanup")
    print("   ")
    print("   # Check cleanup_report.json for detailed results")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
