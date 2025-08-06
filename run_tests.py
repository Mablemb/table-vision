#!/usr/bin/env python3
"""
Test runner for the table-vision project.
This script runs all tests with proper path configuration.
"""
import sys
import os
import unittest

# Add src directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
tests_path = os.path.join(project_root, 'tests')

sys.path.insert(0, src_path)
sys.path.insert(0, tests_path)

def run_all_tests():
    """Run all unit tests in the tests directory."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = tests_path
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

def run_specific_test(test_module):
    """Run tests from a specific module."""
    try:
        # Import the test module
        module = __import__(f'test_{test_module}')
        
        # Load tests from the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
    except ImportError as e:
        print(f"Error importing test module 'test_{test_module}': {e}")
        return 1

if __name__ == '__main__':
    print("Table Vision Test Runner")
    print("=" * 50)
    print(f"Project Root: {project_root}")
    print(f"Source Path: {src_path}")
    print(f"Tests Path: {tests_path}")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Run specific test module
        test_module = sys.argv[1]
        print(f"Running tests for module: {test_module}")
        exit_code = run_specific_test(test_module)
    else:
        # Run all tests
        print("Running all tests...")
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
