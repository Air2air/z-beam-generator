#!/bin/bash
"""
Test Error Resolution Runner Script

This script provides a simple way to run the test error resolution workflow
and integrates with the development process.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_MANAGER="$PROJECT_ROOT/test_error_workflow_manager.py"
REPORTS_DIR="$PROJECT_ROOT/test_errors"

# Functions
print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Test Error Resolution Workflow${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

print_step() {
    echo -e "${GREEN}➤ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_dependencies() {
    print_step "Checking dependencies..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi

    if ! python3 -c "import pytest" 2>/dev/null; then
        print_error "pytest is required but not installed."
        exit 1
    fi

    if [ ! -f "$WORKFLOW_MANAGER" ]; then
        print_error "Workflow manager not found: $WORKFLOW_MANAGER"
        exit 1
    fi

    print_success "All dependencies satisfied"
}

run_workflow() {
    print_step "Running test error resolution workflow..."

    cd "$PROJECT_ROOT"

    if python3 "$WORKFLOW_MANAGER"; then
        print_success "Workflow completed successfully"
    else
        print_error "Workflow failed"
        exit 1
    fi
}

show_recent_reports() {
    print_step "Recent resolution reports:"

    if [ -d "$REPORTS_DIR" ]; then
        ls -la "$REPORTS_DIR"/*.md 2>/dev/null | head -5 || echo "No reports found"
    else
        echo "Reports directory not found"
    fi
}

show_help() {
    cat << EOF
Test Error Resolution Workflow Runner

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    -r, --reports       Show recent resolution reports
    -v, --verbose       Enable verbose output

DESCRIPTION:
    This script runs the automated test error resolution workflow that:
    1. Runs the test suite and captures failures
    2. Analyzes errors and suggests fixes
    3. Applies automated fixes where possible
    4. Updates documentation
    5. Improves test cases
    6. Generates comprehensive reports

EXAMPLES:
    $0                    # Run the complete workflow
    $0 --reports          # Show recent reports
    $0 --help             # Show this help

FILES:
    $WORKFLOW_MANAGER     # Main workflow manager script
    $REPORTS_DIR/         # Directory for resolution reports

For more information, see:
    docs/TEST_ERROR_RESOLUTION_WORKFLOW.md

EOF
}

# Main script logic
main() {
    local show_reports=false
    local verbose=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -r|--reports)
                show_reports=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    print_header

    # Show reports if requested
    if [ "$show_reports" = true ]; then
        show_recent_reports
        exit 0
    fi

    # Check dependencies
    check_dependencies

    # Run the workflow
    run_workflow

    # Show recent reports
    echo
    show_recent_reports

    echo
    print_success "Test error resolution workflow completed!"
    echo -e "${BLUE}Check the generated reports for detailed results.${NC}"
}

# Run main function
main "$@"
