#!/bin/bash

# BackboneOS Backend Docker Test Runner
# This script runs tests within the Docker Compose environment

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
CLEANUP=true
INTERACTIVE=false

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
    echo "  --no-cleanup             Don't cleanup containers after tests"
    echo "  -i, --interactive        Run interactive test session"
    echo "  --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --type unit --coverage"
    echo "  $0 --type api --parallel --workers 8"
    echo "  $0 --app users --coverage --html-report"
    echo "  $0 --interactive"
    echo "  $0 --markers 'unit or integration' --exclude slow"
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
        --no-cleanup)
            CLEANUP=false
            shift
            ;;
        -i|--interactive)
            INTERACTIVE=true
            shift
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
if [ ! -f "docker-compose.test.yml" ]; then
    print_error "docker-compose.test.yml not found. Please run this script from the backend directory."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Print configuration
print_status "Docker Test Configuration:"
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
echo "  Interactive: $INTERACTIVE"
echo "  Cleanup: $CLEANUP"
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

# Function to cleanup containers
cleanup_containers() {
    if [ "$CLEANUP" = true ]; then
        print_status "Cleaning up test containers..."
        docker-compose -f docker-compose.test.yml down -v
        print_success "Test containers cleaned up!"
    fi
}

# Function to run tests in Docker
run_tests_in_docker() {
    print_status "Starting test environment..."
    
    # Start test services
    docker-compose -f docker-compose.test.yml up -d test-db test-redis
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are healthy
    if ! docker-compose -f docker-compose.test.yml ps | grep -q "healthy"; then
        print_warning "Services may not be fully ready, but continuing..."
    fi
    
    if [ "$INTERACTIVE" = true ]; then
        print_status "Starting interactive test session..."
        print_status "You can run tests manually in the container."
        print_status "Example commands:"
        echo "  python manage.py run_tests --type=unit --coverage"
        echo "  pytest tests/test_models.py -v"
        echo "  python manage.py test_coverage --html"
        echo ""
        print_status "Type 'exit' to stop the session."
        
        docker-compose -f docker-compose.test.yml run --rm test-runner bash
    else
        # Build test command
        TEST_CMD="python manage.py run_tests"
        TEST_CMD="$TEST_CMD --type=$TEST_TYPE"
        
        if [ "$COVERAGE" = true ]; then
            TEST_CMD="$TEST_CMD --coverage"
        fi
        
        if [ "$PARALLEL" = true ]; then
            TEST_CMD="$TEST_CMD --parallel --workers=$WORKERS"
        fi
        
        if [ "$VERBOSE" = true ]; then
            TEST_CMD="$TEST_CMD --verbose"
        fi
        
        if [ "$HTML_REPORT" = true ]; then
            TEST_CMD="$TEST_CMD --html-report"
        fi
        
        if [ "$XML_REPORT" = true ]; then
            TEST_CMD="$TEST_CMD --xml-report"
        fi
        
        if [ "$FAILFAST" = true ]; then
            TEST_CMD="$TEST_CMD --failfast"
        fi
        
        if [ -n "$APP" ]; then
            TEST_CMD="$TEST_CMD --app=$APP"
        fi
        
        if [ -n "$PATTERN" ]; then
            TEST_CMD="$TEST_CMD --pattern='$PATTERN'"
        fi
        
        if [ -n "$MARKERS" ]; then
            TEST_CMD="$TEST_CMD --markers='$MARKERS'"
        fi
        
        if [ -n "$EXCLUDE_MARKERS" ]; then
            TEST_CMD="$TEST_CMD --exclude-markers='$EXCLUDE_MARKERS'"
        fi
        
        print_status "Running tests: $TEST_CMD"
        
        # Run tests
        if docker-compose -f docker-compose.test.yml run --rm test-backend $TEST_CMD; then
            print_success "Tests completed successfully!"
            
            # Copy coverage reports if generated
            if [ "$COVERAGE" = true ]; then
                print_status "Copying coverage reports..."
                docker cp $(docker-compose -f docker-compose.test.yml ps -q test-backend):/app/coverage_reports ./coverage_reports 2>/dev/null || true
                docker cp $(docker-compose -f docker-compose.test.yml ps -q test-backend):/app/htmlcov ./htmlcov 2>/dev/null || true
                docker cp $(docker-compose -f docker-compose.test.yml ps -q test-backend):/app/coverage.xml ./coverage.xml 2>/dev/null || true
                
                if [ -d "./coverage_reports" ]; then
                    print_success "Coverage reports copied to ./coverage_reports/"
                fi
                if [ -d "./htmlcov" ]; then
                    print_success "HTML coverage report copied to ./htmlcov/"
                fi
                if [ -f "./coverage.xml" ]; then
                    print_success "XML coverage report copied to ./coverage.xml"
                fi
            fi
        else
            print_error "Tests failed!"
            cleanup_containers
            exit 1
        fi
    fi
}

# Trap to cleanup on exit
trap cleanup_containers EXIT

# Run tests
start_time=$(date +%s)
run_tests_in_docker
end_time=$(date +%s)
duration=$((end_time - start_time))

print_success "Test execution completed in ${duration}s!"

# Show final status
if [ "$CLEANUP" = false ]; then
    print_warning "Test containers are still running. Use 'docker-compose -f docker-compose.test.yml down' to stop them."
else
    print_success "All test containers have been cleaned up."
fi
