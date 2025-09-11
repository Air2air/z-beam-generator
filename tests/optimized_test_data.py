#!/usr/bin/env python3
"""
Optimized Test Data Factory

Pre-loads and caches commonly used test data to reduce setup overhead
and improve test execution performance.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from functools import lru_cache

from tests.test_framework import TestDataFactory


class OptimizedTestData:
    """
    Optimized test data factory with caching and pre-loading.
    """

    _cache: Dict[str, Any] = {}
    _materials_cache: List[Dict[str, Any]] = []
    _authors_cache: List[Dict[str, Any]] = []
    _configs_cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    @lru_cache(maxsize=1)
    def get_materials(cls, count: int = 10) -> List[Dict[str, Any]]:
        """Get cached materials data."""
        if not cls._materials_cache:
            cls._materials_cache = TestDataFactory.create_test_materials(count)
        return cls._materials_cache[:count]

    @classmethod
    @lru_cache(maxsize=1)
    def get_authors(cls) -> List[Dict[str, Any]]:
        """Get cached authors data."""
        if not cls._authors_cache:
            cls._authors_cache = [
                TestDataFactory.create_test_author_info(i) for i in range(1, 5)
            ]
        return cls._authors_cache

    @classmethod
    @lru_cache(maxsize=1)
    def get_component_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Get cached component configurations."""
        if not cls._configs_cache:
            components = ["frontmatter", "text", "metatags", "bullets", "table", "caption"]
            cls._configs_cache = {
                comp: TestDataFactory.create_test_component_config(comp)
                for comp in components
            }
        return cls._configs_cache

    @classmethod
    def get_single_material_workflow_data(cls) -> Dict[str, Any]:
        """Get pre-configured data for single material workflow tests."""
        return {
            "material": cls.get_materials(1)[0]["name"],
            "components": ["frontmatter", "text", "metatags"],
            "author": cls.get_authors()[0],
            "expected_success_rate": 0.8
        }

    @classmethod
    def get_batch_processing_data(cls) -> Dict[str, Any]:
        """Get pre-configured data for batch processing tests."""
        materials = cls.get_materials(3)
        return {
            "materials": [m["name"] for m in materials],
            "components": ["frontmatter", "text", "table"],
            "author_id": 1,
            "expected_min_components": 6  # 3 materials × 3 components × 0.67 success rate
        }

    @classmethod
    def get_error_recovery_data(cls) -> Dict[str, Any]:
        """Get pre-configured data for error recovery tests."""
        return {
            "material": cls.get_materials(1)[0]["name"],
            "components": ["frontmatter", "text", "metatags"],
            "author": cls.get_authors()[0],
            "error_rate": 0.3,  # 30% failure rate for testing
            "expected_min_success": 1  # At least some components should succeed
        }

    @classmethod
    def get_performance_test_data(cls) -> Dict[str, Any]:
        """Get pre-configured data for performance tests."""
        return {
            "material": cls.get_materials(1)[0]["name"],
            "components": ["frontmatter", "text", "metatags"],
            "author": cls.get_authors()[0],
            "iterations": 3,
            "max_avg_time": 4.0,
            "max_peak_time": 6.0,
            "max_variance": 2.0
        }

    @classmethod
    def clear_cache(cls):
        """Clear all cached data."""
        cls._materials_cache.clear()
        cls._authors_cache.clear()
        cls._configs_cache.clear()
        cls.get_materials.cache_clear()
        cls.get_authors.cache_clear()
        cls.get_component_configs.cache_clear()


# Pre-load common data at module import time for maximum performance
_OPTIMIZED_DATA = {
    "materials": OptimizedTestData.get_materials(),
    "authors": OptimizedTestData.get_authors(),
    "component_configs": OptimizedTestData.get_component_configs(),
    "single_workflow": OptimizedTestData.get_single_material_workflow_data(),
    "batch_data": OptimizedTestData.get_batch_processing_data(),
    "error_data": OptimizedTestData.get_error_recovery_data(),
    "performance_data": OptimizedTestData.get_performance_test_data(),
}


def get_optimized_test_data(key: str) -> Any:
    """Get pre-loaded optimized test data."""
    return _OPTIMIZED_DATA.get(key)


def get_fast_material_list(count: int = 5) -> List[str]:
    """Get fast access to material names only."""
    materials = _OPTIMIZED_DATA["materials"][:count]
    return [m["name"] for m in materials]


def get_fast_author_info(author_id: int = 1) -> Dict[str, Any]:
    """Get fast access to author info."""
    authors = _OPTIMIZED_DATA["authors"]
    return authors[(author_id - 1) % len(authors)]


def get_fast_component_config(component: str) -> Dict[str, Any]:
    """Get fast access to component configuration."""
    return _OPTIMIZED_DATA["component_configs"].get(component, {})
