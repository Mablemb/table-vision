"""
Test package for table-vision project.

This package contains unit tests for the table extraction and visualization system.
"""
import sys
import os

# Add src directory to path for test imports
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
src_dir = os.path.join(project_root, 'src')

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Import test modules for discovery
try:
    from . import test_extractor
    from . import test_coordinates
    from . import test_viewer
    __all__ = ['test_extractor', 'test_coordinates', 'test_viewer']
except ImportError:
    # If imports fail, that's ok - tests can still be run individually
    __all__ = []