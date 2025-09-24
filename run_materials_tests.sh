#!/bin/bash
"""
Quick test runner for materials.yaml validation
Usage: ./run_materials_tests.sh
"""

echo "🧪 Running Materials.yaml Comprehensive Test Suite"
echo "=================================================="

# Change to project root
cd "$(dirname "$0")"

# Run the test suite
python3 tests/test_materials_yaml.py

# Capture exit code
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! materials.yaml is production-ready."
else
    echo ""
    echo "❌ Tests failed. Check the output above for specific issues."
fi

exit $exit_code
