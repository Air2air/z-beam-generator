"""
Z-Beam Generator Test Suite

This package contains comprehensive tests for the Z-Beam generator system:

Core Tests (--test):
- Dynamic System Tests: Core system functionality and schema loading
- API Provider Tests: Multi-provider API integration testing  
- Component Configuration Tests: Component routing and configuration
- Integration Tests: End-to-end workflow testing

Performance Tests (--performance):
- Performance Monitoring: API response times and system performance
- Memory Usage: Resource utilization analysis
- Concurrent Testing: Multi-threaded performance validation

Usage:
    python3 -m tests           # Run core test suite
    python3 -m tests --test    # Run core test suite  
    python3 -m tests --performance  # Run performance tests only
    python3 -m tests --all     # Run all tests (core + performance)
"""

__version__ = "1.0.0"
__author__ = "Z-Beam Development Team"
