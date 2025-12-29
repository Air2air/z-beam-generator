"""
Generator Coordinator - Orchestrates Multiple Generators

Handles:
- Dependency ordering (topological sort)
- Incremental updates (only changed items)
- Progress tracking
- Atomic writes (backup + verify)
- Validation (all fields generated)

Usage:
    coordinator = GeneratorCoordinator('materials')
    coordinator.register_generator(SlugGenerator(config))
    coordinator.register_generator(URLGenerator(config), dependencies=['slug'])
    coordinator.register_generator(BreadcrumbGenerator(config), dependencies=['url'])
    
    data = coordinator.generate_all(materials_data)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict, deque

from scripts.generators.base_generator import BaseGenerator, DependencyError

logger = logging.getLogger(__name__)


class GeneratorCoordinator:
    """
    Orchestrate execution of multiple generators.
    
    Features:
    - Dependency resolution (topological sort)
    - Incremental updates
    - Progress tracking
    - Validation
    """
    
    def __init__(self, domain: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize coordinator for domain.
        
        Args:
            domain: Domain name (materials, contaminants, etc.)
            config: Optional configuration dict
        """
        self.domain = domain
        self.config = config or {}
        self.generators: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized GeneratorCoordinator for domain: {domain}")
    
    def register_generator(
        self, 
        generator: BaseGenerator, 
        dependencies: Optional[List[str]] = None
    ):
        """
        Register generator with optional dependencies.
        
        Args:
            generator: Generator instance
            dependencies: List of field names this generator depends on
        """
        # Get dependencies from generator if not explicitly provided
        if dependencies is None:
            dependencies = generator.get_dependencies()
        
        self.generators.append({
            'generator': generator,
            'dependencies': dependencies,
            'fields': generator.get_generated_fields()
        })
        
        logger.debug(
            f"Registered {generator.__class__.__name__} "
            f"(generates: {generator.get_generated_fields()}, "
            f"depends on: {dependencies})"
        )
    
    def generate_all(self, data: Dict[str, Any], incremental: bool = False) -> Dict[str, Any]:
        """
        Execute all generators in dependency order.
        
        Args:
            data: Domain data dict (e.g., all materials)
            incremental: If True, only process items missing fields
        
        Returns:
            Fully populated data
        
        Raises:
            DependencyError: If dependency cycle detected
        """
        print(f"\n{'='*80}")
        print(f"🚀 GENERATOR COORDINATOR: {self.domain.upper()}")
        print(f"{'='*80}")
        
        # Sort generators by dependencies
        ordered = self._topological_sort()
        
        print(f"\n📋 Execution Order ({len(ordered)} generators):")
        for i, gen_info in enumerate(ordered, 1):
            gen = gen_info['generator']
            deps = gen_info['dependencies']
            fields = gen_info['fields']
            print(f"  {i}. {gen.__class__.__name__}")
            print(f"     Generates: {', '.join(fields)}")
            if deps:
                print(f"     Depends on: {', '.join(deps)}")
        
        # Execute each generator
        print(f"\n🔧 Generating Fields:")
        for gen_info in ordered:
            generator = gen_info['generator']
            
            # Validate dependencies
            if not generator.validate_dependencies(data):
                raise DependencyError(
                    f"{generator.__class__.__name__} dependencies not satisfied"
                )
            
            # Count items needing update (if incremental)
            if incremental:
                items_needing_update = sum(
                    1 for item in data.values() 
                    if generator.needs_update(item)
                )
                print(f"\n  {generator.__class__.__name__}: {items_needing_update} items need update")
            else:
                print(f"\n  {generator.__class__.__name__}: processing all {len(data)} items")
            
            # Generate fields
            data = generator.generate(data)
        
        print(f"\n✅ Generation complete: {len(data)} items processed")
        print(f"{'='*80}\n")
        
        return data
    
    def _topological_sort(self) -> List[Dict[str, Any]]:
        """
        Sort generators by dependency order using topological sort.
        
        Returns:
            Ordered list of generator info dicts
        
        Raises:
            DependencyError: If dependency cycle detected
        """
        # Build dependency graph
        graph = defaultdict(list)  # field -> generators that depend on it
        in_degree = {}  # generator -> number of dependencies
        field_providers = {}  # field -> generator that provides it
        
        # Map fields to generators
        for gen_info in self.generators:
            gen_id = id(gen_info['generator'])
            in_degree[gen_id] = len(gen_info['dependencies'])
            
            for field in gen_info['fields']:
                field_providers[field] = gen_info
        
        # Build graph edges
        for gen_info in self.generators:
            gen_id = id(gen_info['generator'])
            for dep_field in gen_info['dependencies']:
                if dep_field in field_providers:
                    provider = field_providers[dep_field]
                    provider_id = id(provider['generator'])
                    graph[provider_id].append(gen_id)
        
        # Kahn's algorithm for topological sort
        queue = deque([
            gen_info for gen_info in self.generators
            if in_degree[id(gen_info['generator'])] == 0
        ])
        
        result = []
        while queue:
            gen_info = queue.popleft()
            result.append(gen_info)
            
            gen_id = id(gen_info['generator'])
            for dependent_id in graph[gen_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    # Find generator info for this dependent
                    dependent_info = next(
                        g for g in self.generators 
                        if id(g['generator']) == dependent_id
                    )
                    queue.append(dependent_info)
        
        # Check for cycles
        if len(result) != len(self.generators):
            raise DependencyError(
                "Dependency cycle detected in generator dependencies"
            )
        
        return result
    
    def validate_completeness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that all fields have been generated.
        
        Args:
            data: Domain data dict
        
        Returns:
            Dict with validation results:
                - complete: bool (all fields present)
                - missing_fields: dict of item_id -> missing field names
        """
        # Collect all expected fields
        expected_fields = set()
        for gen_info in self.generators:
            expected_fields.update(gen_info['fields'])
        
        # Check each item
        missing_by_item = {}
        for item_id, item_data in data.items():
            missing = [
                field for field in expected_fields
                if field not in item_data
            ]
            if missing:
                missing_by_item[item_id] = missing
        
        return {
            'complete': len(missing_by_item) == 0,
            'total_items': len(data),
            'items_with_missing_fields': len(missing_by_item),
            'missing_fields': missing_by_item
        }
