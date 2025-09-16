#!/bin/bash

# BackboneOS Backend Test Runner
# This script provides various options for running tests with different configurations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
COVERAGE=false
PARALLEL=false
VERBOSE=false
WORKERS=4
FAIL_UNDER=80
HTML_REPORT=false
XML_REPORT=false
KEEP_DB=false
FAILFAST=false
APP=""
PATTERN=""
MARKERS=""
EXCLUDE_MARKERS=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE          Test type: unit, integration, api, performance, smoke, all (default: all)"
    echo "  -c, --coverage           Run tests with coverage"
    echo "  -p, --parallel           Run tests in parallel"
    echo "  -v, --verbose            Verbose output"
    echo "  -w, --workers NUM        Number of parallel workers (default: 4)"
    echo "  -f, --fail-under NUM     Coverage threshold (default: 80)"
    echo "  -h, --html-report        Generate HTML coverage report"
    echo "  -x, --xml-report         Generate XML coverage report"
    echo "  -k, --keep-db            Keep test database after tests"
    echo "  --failfast               Stop on first failure"
    echo "  -a, --app APP            Test specific app"
    echo "  --pattern PATTERN        Test file pattern to match"
    echo "  -m, --markers MARKERS    Pytest markers to include"
    echo "  -e, --exclude MARKERS    Pytest markers to exclude"
    echo "  --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --type unit --coverage"
    echo "  $0 --type api --parallel --workers 8"
    echo "  $0 --app users --coverage --html-report"
    echo "  $0 --markers 'unit or integration' --exclude slow"
    echo "  $0 --pattern 'test_user' --verbose"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -f|--fail-under)
            FAIL_UNDER="$2"
            shift 2
            ;;
        -h|--html-report)
            HTML_REPORT=true
            shift
            ;;
        -x|--xml-report)
            XML_REPORT=true
            shift
            ;;
        -k|--keep-db)
            KEEP_DB=true
            shift
            ;;
        --failfast)
            FAILFAST=true
            shift
            ;;
        -a|--app)
            APP="$2"
            shift 2
            ;;
        --pattern)
            PATTERN="$2"
            shift 2
            ;;
        -m|--markers)
            MARKERS="$2"
            shift 2
            ;;
        -e|--exclude)
            EXCLUDE_MARKERS="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate test type
case $TEST_TYPE in
    unit|integration|api|performance|smoke|all)
        ;;
    *)
        print_error "Invalid test type: $TEST_TYPE"
        print_error "Valid types: unit, integration, api, performance, smoke, all"
        exit 1
        ;;
esac

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Please install it: pip install pytest pytest-django"
    exit 1
fi

# Print configuration
print_status "Test Configuration:"
echo "  Type: $TEST_TYPE"
echo "  Coverage: $COVERAGE"
echo "  Parallel: $PARALLEL"
echo "  Workers: $WORKERS"
echo "  Verbose: $VERBOSE"
echo "  Fail Under: $FAIL_UNDER%"
echo "  HTML Report: $HTML_REPORT"
echo "  XML Report: $XML_REPORT"
echo "  Keep DB: $KEEP_DB"
echo "  Fail Fast: $FAILFAST"
if [ -n "$APP" ]; then
    echo "  App: $APP"
fi
if [ -n "$PATTERN" ]; then
    echo "  Pattern: $PATTERN"
fi
if [ -n "$MARKERS" ]; then
    echo "  Markers: $MARKERS"
fi
if [ -n "$EXCLUDE_MARKERS" ]; then
    echo "  Exclude: $EXCLUDE_MARKERS"
fi
echo ""

# Build pytest command
PYTEST_CMD="python -m pytest"

# Add Django settings
PYTEST_CMD="$PYTEST_CMD --ds=backend.test_settings"

# Add verbosity
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
else
    PYTEST_CMD="$PYTEST_CMD -q"
fi

# Add failfast
if [ "$FAILFAST" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -x"
fi

# Add keep database
if [ "$KEEP_DB" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --reuse-db"
fi

# Add parallel execution
if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n $WORKERS"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=. --cov-report=term-missing"
    
    if [ "$HTML_REPORT" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=html:htmlcov"
    fi
    
    if [ "$XML_REPORT" = true ]; then
        PYTEST_CMD="$PYTEST_CMD --cov-report=xml"
    fi
    
    PYTEST_CMD="$PYTEST_CMD --cov-fail-under=$FAIL_UNDER"
fi

# Add test type markers
case $TEST_TYPE in
    unit)
        PYTEST_CMD="$PYTEST_CMD -m unit"
        ;;
    integration)
        PYTEST_CMD="$PYTEST_CMD -m integration"
        ;;
    api)
        PYTEST_CMD="$PYTEST_CMD -m api"
        ;;
    performance)
        PYTEST_CMD="$PYTEST_CMD -m performance"
        ;;
    smoke)
        PYTEST_CMD="$PYTEST_CMD -m smoke"
        ;;
    all)
        # Exclude slow tests by default unless specifically requested
        if [ -z "$MARKERS" ] || [[ "$MARKERS" != *"slow"* ]]; then
            PYTEST_CMD="$PYTEST_CMD -m 'not slow'"
        fi
        ;;
esac

# Add custom markers
if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m '$MARKERS'"
fi

# Add exclude markers
if [ -n "$EXCLUDE_MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m 'not $EXCLUDE_MARKERS'"
fi

# Add pattern
if [ -n "$PATTERN" ]; then
    PYTEST_CMD="$PYTEST_CMD -k '$PATTERN'"
fi

# Add app filter
if [ -n "$APP" ]; then
    PYTEST_CMD="$PYTEST_CMD $APP/"
fi

# Add timeout for performance tests
if [ "$TEST_TYPE" = "performance" ]; then
    PYTEST_CMD="$PYTEST_CMD --timeout=600"
fi

# Print command
print_status "Executing: $PYTEST_CMD"
echo ""

# Execute the command
start_time=$(date +%s)

if eval $PYTEST_CMD; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    print_success "Tests completed successfully in ${duration}s!"
    
    # Show coverage summary if coverage was enabled
    if [ "$COVERAGE" = true ]; then
        echo ""
        print_status "Coverage Summary:"
        python -m coverage report --show-missing
        
        if [ "$HTML_REPORT" = true ]; then
            print_status "HTML coverage report generated: htmlcov/index.html"
        fi
        
        if [ "$XML_REPORT" = true ]; then
            print_status "XML coverage report generated: coverage.xml"
        fi
    fi
    
    # Show performance summary if performance tests were run
    if [ "$TEST_TYPE" = "performance" ]; then
        echo ""
        print_status "Performance test results available in test output above."
    fi
    
else
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    print_error "Tests failed after ${duration}s!"
    exit 1
fi
