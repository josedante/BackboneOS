#!/usr/bin/env python
"""
Test script for page view flow implementation.

This script tests the complete page view event processing flow with various scenarios.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def run_tests():
    """Run the page view flow tests."""
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Run the page view flow tests
    failures = test_runner.run_tests(["websites.tests.test_page_view_flow"])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
