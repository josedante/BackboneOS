"""
Test runner for the touchpoint resolution system.

This script provides a convenient way to run all tests for the touchpoint
resolution system and generate a comprehensive test report.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def run_tests():
    """Run all tests for the touchpoint resolution system."""
    print("🧪 Running Touchpoint Resolution System Tests")
    print("=" * 50)
    
    # Get the test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Define test modules to run
    test_modules = [
        'connectors.tests.test_protocols',
        'connectors.tests.test_resolvers',
        'connectors.tests.test_mapping_providers',
        'connectors.tests.test_models',
    ]
    
    # Run tests
    failures = test_runner.run_tests(test_modules)
    
    # Print summary
    print("\n" + "=" * 50)
    if failures:
        print(f"❌ {failures} test(s) failed")
        return False
    else:
        print("✅ All tests passed!")
        return True

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
