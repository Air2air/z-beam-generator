# Z-Beam Generator Test Suite

This directory contains the comprehensive test suite for the Z-Beam generator system.

## Test Organization

### Current Test Structure (Simplified)
- **Dynamic System Tests** (`test_dynamic_system.py`): Core system functionality and schema loading
- **API Response Tests** (`test_api_comprehensive.py`): Basic API response validation with DeepSeek and Grok
- **Component Configuration Tests** (`test_component_config.py`): Component routing and configuration validation
- **Integration Tests** (`test_integration.py`): End-to-end workflow testing with API response validation
- **Legacy API Provider Tests** (`test_api_providers.py`): Original API provider tests (maintained for compatibility)

### Removed (Performance Tests)
Performance tests have been removed to simplify the test suite and focus on essential functionality validation.

## Usage

### Running Tests

```bash
# Run all tests (simplified - only one option now)
python3 -m tests

# Run with verbose output
python3 -m tests --verbose

# Alternative: Use wrapper scripts
python3 test.py              # From project root
python3 tests/test_all.py    # From tests directory

# Run individual test files directly
python3 tests/test_dynamic_system.py
python3 tests/test_api_comprehensive.py
python3 tests/test_component_config.py
python3 tests/test_integration.py
```

### Command Line Options

- `--verbose`: Enable verbose output
- `--help`: Show help message

**Note**: Performance test options (`--performance`, `--all`) have been removed to simplify the test suite.

## Test Categories

### Core Tests (All Tests)
These tests validate the essential functionality of the Z-Beam system:

- **System Initialization**: Loading schemas, materials, and components
- **API Response Validation**: Basic API testing with DeepSeek and Grok providers
- **Component Routing**: Proper routing of components to API providers
- **Configuration Management**: Component enable/disable and provider assignment
- **End-to-End Workflows**: Complete generation workflows with API response validation
- **Error Handling**: Graceful handling of API failures and invalid inputs

### Removed (Performance Tests)
Performance tests were removed to simplify the test suite:
- ~~API Response Times~~
- ~~Token Generation Rates~~
- ~~Memory Usage Monitoring~~
- ~~Concurrent Performance Testing~~
- ~~Scalability Testing~~

## Test Environment

### Prerequisites
- Python 3.8+
- Required packages: `requests`, `pathlib`, `unittest.mock`
- Optional: `psutil` (for memory monitoring)

### API Keys
For complete testing, set up API keys in `.env` file:
```
DEEPSEEK_API_KEY=your_deepseek_api_key
GROK_API_KEY=your_grok_api_key
```

**Note**: Tests will run in mock mode if API keys are not available, but real API integration tests will be skipped.

## Test Results

### Success Criteria
- **EXCELLENT (100%)**: All tests pass - system ready for production
- **GOOD (80-99%)**: Most tests pass - minor issues to address
- **FAIR (60-79%)**: Some tests pass - core functionality works but needs improvements
- **POOR (<60%)**: Many tests fail - significant issues need resolution

### Output Format
Tests provide comprehensive reporting including:
- Individual test results with timing
- Overall success rates
- Performance metrics (when applicable)
- System assessment and recommendations
- Detailed error information for failed tests

## Error Handling

The test suite includes comprehensive error handling validation:
- **Mock Network Failures**: Tests use mocked network calls to avoid timeouts
- **Invalid Configurations**: Tests validate proper handling of invalid inputs
- **API Error Scenarios**: Tests various API failure modes
- **Resource Exhaustion**: Tests system behavior under resource constraints

## Performance Monitoring

Performance tests provide detailed metrics:
- **Response Time Statistics**: Mean, median, and distribution
- **Throughput Measurements**: Requests per second and tokens per second
- **Resource Usage**: Memory consumption and cleanup
- **Comparative Analysis**: Performance comparison across API providers

## Continuous Integration

The test suite is designed for CI/CD integration:
- **Exit Codes**: Proper exit codes for automation
- **Structured Output**: Machine-readable test results
- **Isolated Tests**: Tests don't interfere with each other
- **Environment Flexibility**: Works with or without API keys

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **Missing API Keys**: Tests will run in mock mode without API keys
3. **Network Timeouts**: Error handling tests use mocks to avoid real network calls
4. **Permission Errors**: Ensure write permissions for temporary test files

### Debug Mode
Add debugging by setting environment variables:
```bash
export DEBUG=1
python3 -m tests --test
```

### Verbose Output
For detailed test output, run individual test files:
```bash
python3 tests/test_dynamic_system.py
python3 tests/test_api_comprehensive.py
```

## Contributing

When adding new tests:
1. Follow the existing test structure and naming conventions
2. Use appropriate test categories (core vs performance)
3. Include comprehensive error handling
4. Add documentation for new test scenarios
5. Ensure tests work both with and without API keys
6. Use mocking for network calls in error scenarios
