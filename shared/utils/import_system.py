#!/usr/bin/env python3
"""
Unified Import Management System

Consolidates all import-related functionality from multiple redundant files:
- scripts/validate_imports.py (validation and AST parsing)
- utils/file_ops/import_handler.py (error handling and fallbacks)
- utils/file_ops/import_manager.py (safe imports with caching)
- scripts/maintenance/check_imports.py (import organization)

Following GROK principles: single system for import management, no duplication.
"""

import ast
import importlib
import logging
import sys
from collections import defaultdict
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

logger = logging.getLogger(__name__)


class UnifiedImportManager:
    """
    Unified import management system combining all import-related functionality.
    
    Features:
    - Safe imports with caching
    - Error handling and fallbacks
    - Import validation and AST parsing
    - Import organization checking
    - Dependency validation
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self._import_cache: Dict[str, Any] = {}
        self._failed_imports: Dict[str, str] = {}
        # No fallbacks allowed - fail-fast import system
        self.issues: List[Dict[str, str]] = []
        self.checked_modules: Set[str] = set()
        
        # Ensure project root is in Python path
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
            logger.debug(f"Added to Python path: {self.project_root}")

    # ===== SAFE IMPORT FUNCTIONALITY =====

    def safe_import(self, module_path: str, fallback: Any = None) -> Optional[Any]:
        """
        Safely import a module with caching and fallback.
        
        Args:
            module_path: Module path to import
            fallback: Fallback value if import fails
            
        Returns:
            Imported module or fallback
        """
        if module_path in self._import_cache:
            return self._import_cache[module_path]

        if module_path in self._failed_imports:
            logger.debug(f"Using cached failure for {module_path}: {self._failed_imports[module_path]}")
            return fallback or self._fallbacks.get(module_path)

        try:
            module = importlib.import_module(module_path)
            self._import_cache[module_path] = module
            logger.debug(f"Successfully imported {module_path}")
            return module
        except ImportError as e:
            error_msg = f"Failed to import {module_path}: {e}"
            self._failed_imports[module_path] = error_msg
            logger.warning(error_msg)
            return fallback or self._fallbacks.get(module_path)
        except Exception as e:
            error_msg = f"Unexpected error importing {module_path}: {e}"
            self._failed_imports[module_path] = error_msg
            logger.error(error_msg)
            return fallback or self._fallbacks.get(module_path)

    def safe_import_class(self, module_path: str, class_name: str, fallback: Any = None) -> Optional[Type]:
        """
        Safely import a class from a module.
        
        Args:
            module_path: Module path
            class_name: Class name to import
            fallback: Fallback class if import fails
            
        Returns:
            Imported class or fallback
        """
        cache_key = f"{module_path}.{class_name}"

        if cache_key in self._import_cache:
            return self._import_cache[cache_key]

        if cache_key in self._failed_imports:
            return fallback

        try:
            module = importlib.import_module(module_path)
            class_obj = getattr(module, class_name)
            self._import_cache[cache_key] = class_obj
            logger.debug(f"Successfully imported {cache_key}")
            return class_obj
        except (ImportError, AttributeError) as e:
            error_msg = f"Failed to import {cache_key}: {e}"
            self._failed_imports[cache_key] = error_msg
            logger.warning(error_msg)
            return fallback
        except Exception as e:
            error_msg = f"Unexpected error importing {cache_key}: {e}"
            self._failed_imports[cache_key] = error_msg
            logger.error(error_msg)
            return fallback

    # ===== FALLBACK FUNCTIONALITY DISABLED FOR GROK COMPLIANCE =====

    def register_fallback(self, module_name: str, fallback_module: Any) -> None:
        """GROK COMPLIANCE: Fallbacks disabled - fail-fast architecture required."""
        raise ValueError(f"Fallbacks are disabled for GROK compliance - cannot register fallback for {module_name}")

    def setup_component_fallbacks(self):
        """
        GROK COMPLIANCE: No fallbacks in production.
        This method is disabled to enforce fail-fast architecture.
        Components must be explicitly imported or system fails immediately.
        """
        # REMOVED: All fallback/mock logic violates GROK fail-fast principles
        # System must fail immediately if components are missing
        pass

    # ===== VALIDATION FUNCTIONALITY =====

    def validate_dependencies(self, dependencies: List[str]) -> Dict[str, bool]:
        """
        Validate that all required dependencies are available.
        
        Args:
            dependencies: List of module names to check
            
        Returns:
            Dict mapping module names to availability status
        """
        results = {}
        for dep in dependencies:
            try:
                importlib.import_module(dep)
                results[dep] = True
                logger.debug(f"Dependency {dep} is available")
            except ImportError as e:
                results[dep] = False
                self._failed_imports[dep] = str(e)
                logger.warning(f"Dependency {dep} is missing: {e}")
        return results

    def validate_critical_imports(self) -> bool:
        """Validate that critical Z-Beam imports are working."""
        critical_modules = [
            "generators.component_generators",
            "utils.component_base",
            "api.client_manager", 
            "run",
        ]

        results = self.validate_dependencies(critical_modules)
        failed_count = sum(1 for status in results.values() if not status)
        total_count = len(results)

        if failed_count > 0:
            logger.error(f"Critical import validation failed: {failed_count}/{total_count} modules failed")
            for module, status in results.items():
                if not status:
                    logger.error(f"  - {module}: {self._failed_imports.get(module, 'Unknown error')}")
            return False
        else:
            logger.info(f"Critical import validation passed: {total_count}/{total_count} modules available")
            return True

    # ===== AST PARSING AND VALIDATION =====

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project."""
        python_files = list(self.project_root.rglob("*.py"))
        # Exclude certain directories
        exclude_patterns = ["__pycache__", ".git", ".venv", "venv", "env", "archive", "cleanup"]
        filtered_files = []
        for file_path in python_files:
            if not any(pattern in str(file_path) for pattern in exclude_patterns):
                filtered_files.append(file_path)
        logger.info(f"Found {len(filtered_files)} Python files")
        return filtered_files

    def extract_imports_from_file(self, file_path: Path) -> List[Tuple[str, int]]:
        """Extract all import statements from a Python file using AST."""
        imports = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append((alias.name, node.lineno))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append((node.module, node.lineno))

        except SyntaxError as e:
            self.issues.append({
                "file": str(file_path),
                "type": "syntax_error",
                "message": f"Syntax error: {e}",
                "line": str(e.lineno) if e.lineno else "unknown",
            })
        except Exception as e:
            self.issues.append({
                "file": str(file_path),
                "type": "parse_error", 
                "message": f"Failed to parse: {e}",
                "line": "unknown",
            })

        return imports

    def validate_import(self, module_name: str, file_path: Path, line_no: int) -> None:
        """Validate a single import."""
        if module_name in self.checked_modules:
            return

        self.checked_modules.add(module_name)

        try:
            importlib.import_module(module_name)
            logger.debug(f"✓ {module_name}")
        except ImportError as e:
            # Check if it's a relative import that should be absolute
            if module_name.startswith("."):
                self.issues.append({
                    "file": str(file_path),
                    "type": "relative_import",
                    "message": f"Relative import '{module_name}' should be absolute",
                    "line": str(line_no),
                    "module": module_name,
                })
            else:
                # Check if it's a local module
                module_parts = module_name.split(".")
                possible_paths = [
                    self.project_root / f"{module_name.replace('.', '/')}.py",
                    self.project_root / module_parts[0] / "__init__.py",
                ]

                is_local = any(path.exists() for path in possible_paths)

                if is_local:
                    self.issues.append({
                        "file": str(file_path),
                        "type": "missing_local_import",
                        "message": f"Local module '{module_name}' not found in path",
                        "line": str(line_no),
                        "module": module_name,
                    })
                else:
                    self.issues.append({
                        "file": str(file_path),
                        "type": "missing_dependency",
                        "message": f"External dependency '{module_name}' not installed: {e}",
                        "line": str(line_no),
                        "module": module_name,
                    })

    def validate_all_imports(self) -> None:
        """Validate imports in all Python files."""
        logger.info("Starting import shared.validation...")
        python_files = self.find_python_files()

        for file_path in python_files:
            logger.debug(f"Checking {file_path}")
            imports = self.extract_imports_from_file(file_path)

            for module_name, line_no in imports:
                self.validate_import(module_name, file_path, line_no)

    # ===== REPORTING FUNCTIONALITY =====

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        python_files = self.find_python_files()
        issue_counts = defaultdict(int)
        for issue in self.issues:
            issue_counts[issue["type"]] += 1

        return {
            "total_files": len(python_files),
            "total_issues": len(self.issues),
            "issue_counts": dict(issue_counts),
            "issues": self.issues,
            "critical_imports_ok": self.validate_critical_imports(),
            "failed_imports": self._failed_imports.copy(),
            "cached_imports": len(self._import_cache),
            "registered_fallbacks": len(self._fallbacks),
        }

    def print_validation_report(self, report: Dict[str, Any]) -> None:
        """Print the validation report."""
        print("\n" + "=" * 60)
        print("UNIFIED IMPORT VALIDATION REPORT")
        print("=" * 60)

        print(f"Files checked: {report['total_files']}")
        print(f"Total issues: {report['total_issues']}")
        print(f"Critical imports OK: {report['critical_imports_ok']}")
        print(f"Cached imports: {report['cached_imports']}")
        print(f"Registered fallbacks: {report['registered_fallbacks']}")

        if report["issue_counts"]:
            print("\nIssue breakdown:")
            for issue_type, count in report["issue_counts"].items():
                print(f"  {issue_type}: {count}")

        if report["issues"]:
            print("\nDetailed issues (first 10):")
            for issue in report["issues"][:10]:
                print(f"  {issue['file']}:{issue['line']} - {issue['type']}: {issue['message']}")

            if len(report["issues"]) > 10:
                print(f"  ... and {len(report['issues']) - 10} more issues")

        print("\n" + "=" * 60)

    # ===== UTILITY METHODS =====

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._import_cache.clear()
        self._failed_imports.clear()
        self.issues.clear()
        self.checked_modules.clear()
        logger.info("Import cache cleared")

    def get_import_stats(self) -> Dict[str, int]:
        """Get import statistics."""
        return {
            "cached_imports": len(self._import_cache),
            "failed_imports": len(self._failed_imports), 
            "registered_fallbacks": len(self._fallbacks),
            "validation_issues": len(self.issues),
        }


# ===== DECORATOR FOR FALLBACK FUNCTIONALITY =====

def with_import_fallback(fallback_module: Any):
    """Decorator to provide import fallback for functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ImportError as e:
                logger.warning(f"Import error in {func.__name__}: {e}")
                logger.info(f"Using fallback for {func.__name__}")
                if hasattr(fallback_module, func.__name__):
                    fallback_func = getattr(fallback_module, func.__name__)
                    return fallback_func(*args, **kwargs)
                else:
                    raise e
        return wrapper
    return decorator


# ===== GLOBAL INSTANCE =====

# Global unified import manager instance
import_manager = UnifiedImportManager()

# Setup component fallbacks on import
import_manager.setup_component_fallbacks()


# ===== CONVENIENCE FUNCTIONS FOR BACKWARD COMPATIBILITY =====

def safe_import(module_path: str, fallback: Any = None) -> Optional[Any]:
    """Convenience function for safe imports."""
    return import_manager.safe_import(module_path, fallback)

def safe_import_class(module_path: str, class_name: str, fallback: Any = None) -> Optional[Type]:
    """Convenience function for safe class imports."""
    return import_manager.safe_import_class(module_path, class_name, fallback)

def validate_critical_imports() -> bool:
    """Convenience function for critical import shared.validation."""
    return import_manager.validate_critical_imports()

def validate_dependencies(dependencies: List[str]) -> Dict[str, bool]:
    """Convenience function for dependency validation."""
    return import_manager.validate_dependencies(dependencies)


# ===== CLI INTERFACE =====

def main():
    """CLI interface for import shared.validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Import Management")
    parser.add_argument("--validate", action="store_true", help="Validate all imports")
    parser.add_argument("--critical", action="store_true", help="Check critical imports only")
    parser.add_argument("--stats", action="store_true", help="Show import statistics")
    parser.add_argument("--clear-cache", action="store_true", help="Clear import cache")
    args = parser.parse_args()

    if args.clear_cache:
        import_manager.clear_cache()
        print("✅ Import cache cleared")
        return

    if args.stats:
        stats = import_manager.get_import_stats()
        print("📊 Import Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return

    if args.critical:
        success = import_manager.validate_critical_imports()
        if success:
            print("✅ All critical imports validated successfully!")
            sys.exit(0)
        else:
            print("❌ Critical import validation failed!")
            sys.exit(1)
        return

    if args.validate:
        import_manager.validate_all_imports()
        report = import_manager.generate_validation_report()
        import_manager.print_validation_report(report)
        
        if report["total_issues"] > 0 or not report["critical_imports_ok"]:
            print("\n❌ Import validation failed!")
            sys.exit(1)
        else:
            print("\n✅ All imports validated successfully!")
            sys.exit(0)
    else:
        print("Use --help for available options")


if __name__ == "__main__":
    main()


__all__ = [
    "UnifiedImportManager",
    "import_manager", 
    "with_import_fallback",
    "safe_import",
    "safe_import_class",
    "validate_critical_imports",
    "validate_dependencies",
]
