"""
Integration test runner for Touchpoint Resolution System.

This module provides a comprehensive test runner that executes all integration tests
and provides detailed reporting on system functionality.
"""

import unittest
import sys
import os
from django.test import TestCase
from django.core.management import call_command
from django.test.utils import get_runner
from django.conf import settings
from io import StringIO
import time


class IntegrationTestRunner:
    """Comprehensive integration test runner."""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_all_integration_tests(self):
        """Run all integration tests and return results."""
        print("🚀 Starting Touchpoint Resolution System Integration Tests")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Test categories
        test_categories = [
            ('Admin Interface Integration', 'test_admin_integration'),
            ('Management Commands Integration', 'test_management_commands_integration'),
            ('Monitoring System Integration', 'test_monitoring_integration'),
            ('Touchpoint Resolution Integration', 'test_touchpoint_resolution_integration'),
        ]
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        for category_name, test_module in test_categories:
            print(f"\n📋 Running {category_name} Tests...")
            print("-" * 40)
            
            try:
                # Import and run the test module
                module = __import__(f'connectors.tests.{test_module}', fromlist=[''])
                
                # Create test suite
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(module)
                
                # Run tests
                runner = unittest.TextTestRunner(verbosity=2, stream=StringIO())
                result = runner.run(suite)
                
                # Store results
                self.test_results[category_name] = {
                    'tests_run': result.testsRun,
                    'failures': len(result.failures),
                    'errors': len(result.errors),
                    'success': result.wasSuccessful(),
                    'failures_list': result.failures,
                    'errors_list': result.errors
                }
                
                total_tests += result.testsRun
                total_failures += len(result.failures)
                total_errors += len(result.errors)
                
                # Print category results
                if result.wasSuccessful():
                    print(f"✅ {category_name}: {result.testsRun} tests passed")
                else:
                    print(f"❌ {category_name}: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
                    
                    # Print failure details
                    for failure in result.failures:
                        print(f"   FAIL: {failure[0]}")
                        print(f"   {failure[1]}")
                    
                    for error in result.errors:
                        print(f"   ERROR: {error[0]}")
                        print(f"   {error[1]}")
                
            except Exception as e:
                print(f"❌ Error running {category_name}: {str(e)}")
                self.test_results[category_name] = {
                    'tests_run': 0,
                    'failures': 0,
                    'errors': 1,
                    'success': False,
                    'failures_list': [],
                    'errors_list': [('Module Import Error', str(e))]
                }
                total_errors += 1
        
        self.end_time = time.time()
        
        # Print summary
        self.print_test_summary(total_tests, total_failures, total_errors)
        
        return {
            'total_tests': total_tests,
            'total_failures': total_failures,
            'total_errors': total_errors,
            'success': total_failures == 0 and total_errors == 0,
            'test_results': self.test_results,
            'execution_time': self.end_time - self.start_time
        }
    
    def print_test_summary(self, total_tests, total_failures, total_errors):
        """Print comprehensive test summary."""
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        # Overall results
        if total_failures == 0 and total_errors == 0:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
            print(f"✅ {total_tests} tests completed successfully")
        else:
            print("❌ SOME INTEGRATION TESTS FAILED")
            print(f"📊 {total_tests} tests run, {total_failures} failures, {total_errors} errors")
        
        # Execution time
        execution_time = self.end_time - self.start_time
        print(f"⏱️  Total execution time: {execution_time:.2f} seconds")
        
        # Category breakdown
        print("\n📋 Test Category Breakdown:")
        for category, results in self.test_results.items():
            status = "✅" if results['success'] else "❌"
            print(f"   {status} {category}: {results['tests_run']} tests")
            if not results['success']:
                print(f"      - Failures: {results['failures']}")
                print(f"      - Errors: {results['errors']}")
        
        # Performance metrics
        if total_tests > 0:
            avg_time_per_test = execution_time / total_tests
            print(f"\n⚡ Performance Metrics:")
            print(f"   - Average time per test: {avg_time_per_test:.3f} seconds")
            print(f"   - Tests per second: {total_tests / execution_time:.1f}")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if total_failures == 0 and total_errors == 0:
            print("   - All integration tests are passing! 🎉")
            print("   - System is ready for production deployment")
            print("   - Consider adding more edge case tests")
        else:
            print("   - Fix failing tests before deployment")
            print("   - Review error handling and edge cases")
            print("   - Consider adding more robust error recovery")
        
        print("\n" + "=" * 60)
    
    def run_specific_test_category(self, category_name):
        """Run tests for a specific category."""
        category_map = {
            'admin': 'test_admin_integration',
            'commands': 'test_management_commands_integration',
            'monitoring': 'test_monitoring_integration',
            'resolution': 'test_touchpoint_resolution_integration',
        }
        
        if category_name not in category_map:
            print(f"❌ Unknown test category: {category_name}")
            print(f"Available categories: {', '.join(category_map.keys())}")
            return
        
        test_module = category_map[category_name]
        print(f"🚀 Running {category_name} integration tests...")
        
        try:
            module = __import__(f'connectors.tests.{test_module}', fromlist=[''])
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            if result.wasSuccessful():
                print(f"✅ {category_name} tests passed!")
            else:
                print(f"❌ {category_name} tests failed!")
                
        except Exception as e:
            print(f"❌ Error running {category_name} tests: {str(e)}")
    
    def generate_test_report(self, output_file=None):
        """Generate a detailed test report."""
        if not self.test_results:
            print("❌ No test results available. Run tests first.")
            return
        
        report = []
        report.append("# Touchpoint Resolution System - Integration Test Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_tests = sum(r['tests_run'] for r in self.test_results.values())
        total_failures = sum(r['failures'] for r in self.test_results.values())
        total_errors = sum(r['errors'] for r in self.test_results.values())
        
        report.append("## Summary")
        report.append(f"- Total Tests: {total_tests}")
        report.append(f"- Failures: {total_failures}")
        report.append(f"- Errors: {total_errors}")
        report.append(f"- Success Rate: {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%")
        report.append("")
        
        # Category details
        report.append("## Test Categories")
        for category, results in self.test_results.items():
            report.append(f"### {category}")
            report.append(f"- Tests Run: {results['tests_run']}")
            report.append(f"- Failures: {results['failures']}")
            report.append(f"- Errors: {results['errors']}")
            report.append(f"- Status: {'✅ PASSED' if results['success'] else '❌ FAILED'}")
            report.append("")
            
            # Failure details
            if results['failures']:
                report.append("#### Failures:")
                for failure in results['failures']:
                    report.append(f"- {failure[0]}")
                    report.append(f"  ```")
                    report.append(f"  {failure[1]}")
                    report.append(f"  ```")
                report.append("")
            
            # Error details
            if results['errors']:
                report.append("#### Errors:")
                for error in results['errors']:
                    report.append(f"- {error[0]}")
                    report.append(f"  ```")
                    report.append(f"  {error[1]}")
                    report.append(f"  ```")
                report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if total_failures == 0 and total_errors == 0:
            report.append("- ✅ All tests are passing!")
            report.append("- 🚀 System is ready for production")
            report.append("- 📈 Consider adding more edge case tests")
        else:
            report.append("- 🔧 Fix failing tests before deployment")
            report.append("- 🛡️ Review error handling and edge cases")
            report.append("- 🔄 Add more robust error recovery")
        
        # Write report
        report_content = "\n".join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_content)
            print(f"📄 Test report written to: {output_file}")
        else:
            print(report_content)


def run_integration_tests():
    """Main function to run all integration tests."""
    runner = IntegrationTestRunner()
    results = runner.run_all_integration_tests()
    
    # Generate report
    runner.generate_test_report('integration_test_report.md')
    
    return results


def run_specific_tests(category):
    """Run specific test category."""
    runner = IntegrationTestRunner()
    runner.run_specific_test_category(category)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        category = sys.argv[1]
        run_specific_tests(category)
    else:
        run_integration_tests()

