#!/usr/bin/env python3
"""
Processing Module Usage Auditor

Analyzes the /processing directory to:
1. Identify all modules
2. Determine which are actively used in the generation chain
3. Flag unused/orphaned modules
4. Verify chain completeness (no accidentally skipped modules)
5. Generate dependency graph
6. Suggest architectural improvements
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict

class ModuleAuditor:
    """Audits processing module usage and chain completeness"""
    
    def __init__(self, processing_dir: Path):
        self.processing_dir = processing_dir
        self.modules = {}  # module_path -> ModuleInfo
        self.dependencies = defaultdict(set)  # module -> set of dependencies
        self.reverse_dependencies = defaultdict(set)  # module -> set of dependents
        self.orchestrator_chain = set()  # Modules used in orchestration
        
    def scan_modules(self):
        """Scan all Python modules in processing directory"""
        print("🔍 Scanning processing modules...")
        
        for py_file in self.processing_dir.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file.name == "__init__.py":
                continue
            
            rel_path = py_file.relative_to(self.processing_dir)
            module_name = str(rel_path).replace("/", ".").replace(".py", "")
            
            self.modules[module_name] = {
                'path': py_file,
                'imports': set(),
                'imported_by': set(),
                'is_test': 'tests' in str(rel_path),
                'size_loc': self._count_loc(py_file)
            }
        
        print(f"✅ Found {len(self.modules)} modules")
    
    def _count_loc(self, file_path: Path) -> int:
        """Count lines of code (excluding blanks and comments)"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            loc = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            return loc
        except:
            return 0
    
    def analyze_dependencies(self):
        """Analyze import dependencies between modules"""
        print("\n🔗 Analyzing dependencies...")
        
        for module_name, module_info in self.modules.items():
            try:
                with open(module_info['path'], 'r') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith('processing.'):
                            imported_module = node.module.replace('processing.', '')
                            module_info['imports'].add(imported_module)
                            self.dependencies[module_name].add(imported_module)
                            self.reverse_dependencies[imported_module].add(module_name)
                    
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith('processing.'):
                                imported_module = alias.name.replace('processing.', '')
                                module_info['imports'].add(imported_module)
                                self.dependencies[module_name].add(imported_module)
                                self.reverse_dependencies[imported_module].add(module_name)
            except Exception as e:
                print(f"⚠️  Failed to parse {module_name}: {e}")
        
        print(f"✅ Analyzed {len(self.dependencies)} dependency relationships")
    
    def identify_orchestrator_chain(self):
        """Identify modules used in orchestration chain"""
        print("\n🎭 Identifying orchestration chain...")
        
        # Start with orchestrators
        orchestrators = [
            'unified_orchestrator',
            'orchestrator', 
            'generator'
        ]
        
        visited = set()
        
        def trace_dependencies(module: str):
            """Recursively trace all dependencies"""
            if module in visited or module not in self.modules:
                return
            
            visited.add(module)
            self.orchestrator_chain.add(module)
            
            # Trace imports
            for imported in self.dependencies.get(module, set()):
                trace_dependencies(imported)
        
        # Trace from each orchestrator
        for orch in orchestrators:
            if orch in self.modules:
                trace_dependencies(orch)
        
        print(f"✅ Orchestrator chain includes {len(self.orchestrator_chain)} modules")
    
    def find_unused_modules(self) -> List[str]:
        """Find modules not in the orchestration chain"""
        unused = []
        
        for module_name, module_info in self.modules.items():
            # Skip tests
            if module_info['is_test']:
                continue
            
            # Skip if in orchestrator chain
            if module_name in self.orchestrator_chain:
                continue
            
            # Skip if imported by non-test modules
            has_non_test_dependents = any(
                dep not in self.modules or not self.modules[dep]['is_test']
                for dep in self.reverse_dependencies.get(module_name, set())
            )
            
            if not has_non_test_dependents:
                unused.append(module_name)
        
        return unused
    
    def find_missing_validations(self) -> List[str]:
        """Find modules that should validate but don't"""
        validation_candidates = []
        
        # Modules that handle data but might not validate
        data_handlers = [
            'adapters.materials_adapter',
            'enrichment.data_enricher',
            'generation.prompt_builder',
        ]
        
        for module in data_handlers:
            if module not in self.modules:
                continue
            
            module_info = self.modules[module]
            try:
                with open(module_info['path'], 'r') as f:
                    content = f.read()
                
                # Check for validation patterns
                has_validation = any(keyword in content for keyword in [
                    'validate(',
                    'ValidationError',
                    'raise ValueError',
                    'assert ',
                    'if not '
                ])
                
                if not has_validation:
                    validation_candidates.append(module)
            except:
                pass
        
        return validation_candidates
    
    def generate_report(self):
        """Generate comprehensive audit report"""
        print("\n" + "=" * 70)
        print("PROCESSING MODULE USAGE AUDIT REPORT")
        print("=" * 70)
        
        # Module statistics
        print("\n📊 MODULE STATISTICS:")
        total_loc = sum(m['size_loc'] for m in self.modules.values() if not m['is_test'])
        test_loc = sum(m['size_loc'] for m in self.modules.values() if m['is_test'])
        print(f"  Total modules: {len(self.modules)}")
        print(f"  Production modules: {len([m for m in self.modules.values() if not m['is_test']])}")
        print(f"  Test modules: {len([m for m in self.modules.values() if m['is_test']])}")
        print(f"  Production LOC: {total_loc}")
        print(f"  Test LOC: {test_loc}")
        
        # Orchestrator chain
        print(f"\n🎭 ORCHESTRATOR CHAIN ({len(self.orchestrator_chain)} modules):")
        chain_by_category = defaultdict(list)
        for module in sorted(self.orchestrator_chain):
            if '.' in module:
                category = module.split('.')[0]
            else:
                category = 'root'
            chain_by_category[category].append(module)
        
        for category, modules in sorted(chain_by_category.items()):
            print(f"\n  {category.upper()}:")
            for module in modules:
                loc = self.modules[module]['size_loc']
                deps = len(self.dependencies.get(module, set()))
                dependents = len(self.reverse_dependencies.get(module, set()))
                print(f"    ✓ {module} ({loc} LOC, {deps} deps, {dependents} dependents)")
        
        # Unused modules
        unused = self.find_unused_modules()
        if unused:
            print(f"\n⚠️  UNUSED MODULES ({len(unused)}):")
            for module in sorted(unused):
                loc = self.modules[module]['size_loc']
                print(f"    ❌ {module} ({loc} LOC) - Not in orchestration chain")
        else:
            print("\n✅ NO UNUSED MODULES - All production modules are in the chain!")
        
        # Dependency analysis
        print("\n🔗 DEPENDENCY COMPLEXITY:")
        high_dep_modules = [(m, len(deps)) for m, deps in self.dependencies.items() 
                           if len(deps) > 5 and not self.modules[m]['is_test']]
        high_dep_modules.sort(key=lambda x: x[1], reverse=True)
        
        if high_dep_modules:
            print("  Modules with high dependency count (potential complexity):")
            for module, dep_count in high_dep_modules[:5]:
                print(f"    ⚠️  {module}: {dep_count} dependencies")
        
        # Find circular dependencies
        print("\n🔄 CIRCULAR DEPENDENCY CHECK:")
        circular = self._find_circular_dependencies()
        if circular:
            print(f"  ⚠️  Found {len(circular)} circular dependency chains:")
            for chain in circular[:3]:
                print(f"    {' → '.join(chain)}")
        else:
            print("  ✅ No circular dependencies detected!")
        
        # Chain completeness verification
        print("\n✅ CHAIN COMPLETENESS VERIFICATION:")
        print("  Checking that no critical modules are accidentally skipped...")
        
        critical_modules = [
            'config.dynamic_config',
            'enrichment.data_enricher',
            'generation.prompt_builder',
            'detection.winston_integration',
            'validation.readability',
            'voice.store',
            'learning.temperature_advisor',
        ]
        
        for module in critical_modules:
            if module in self.orchestrator_chain:
                print(f"    ✓ {module} - IN CHAIN")
            else:
                print(f"    ❌ {module} - MISSING FROM CHAIN!")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        if unused:
            print(f"  1. Consider removing {len(unused)} unused modules to reduce complexity")
        
        if high_dep_modules:
            print(f"  2. Refactor modules with >5 dependencies for better modularity")
        
        if circular:
            print(f"  3. Break {len(circular)} circular dependencies to improve testability")
        
        # Missing validations
        missing_val = self.find_missing_validations()
        if missing_val:
            print(f"  4. Add validation to {len(missing_val)} data-handling modules:")
            for module in missing_val:
                print(f"     - {module}")
        
        print("\n" + "=" * 70)
    
    def _find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependency chains"""
        circular = []
        visited = set()
        rec_stack = set()
        
        def dfs(module: str, path: List[str]):
            if module in rec_stack:
                # Found circular dependency
                cycle_start = path.index(module)
                circular.append(path[cycle_start:] + [module])
                return
            
            if module in visited or module not in self.modules:
                return
            
            visited.add(module)
            rec_stack.add(module)
            
            for dep in self.dependencies.get(module, set()):
                dfs(dep, path + [module])
            
            rec_stack.remove(module)
        
        for module in self.modules:
            if module not in visited and not self.modules[module]['is_test']:
                dfs(module, [])
        
        return circular

def main():
    processing_dir = Path("/Users/todddunning/Desktop/Z-Beam/z-beam-generator/processing")
    
    if not processing_dir.exists():
        print(f"❌ Processing directory not found: {processing_dir}")
        return 1
    
    auditor = ModuleAuditor(processing_dir)
    
    auditor.scan_modules()
    auditor.analyze_dependencies()
    auditor.identify_orchestrator_chain()
    auditor.generate_report()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
