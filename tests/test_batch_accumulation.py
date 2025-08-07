#!/usr/bin/env python3
"""
Pytest for batch extraction coordinate accumulation fix.

This test verifies that:
1. Coordinates are properly accumulated during batch extraction
2. Deletion works throughout the batch process, not just at the end
3. Both data structures (coordinates_manager and all_extracted_coordinates) stay synchronized
"""

import sys
import os
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.coordinates import TableCoordinates


class MockViewer:
    """Mock viewer for testing."""
    def __init__(self):
        self.coordinates = []
        self.current_page = 0
    
    def set_coordinates(self, coordinates):
        self.coordinates = coordinates
    
    def get_coordinates(self):
        return self.coordinates


class MockEditor:
    """Mock editor for testing."""
    def __init__(self):
        self.coordinates = []
    
    def set_coordinates(self, coordinates):
        self.coordinates = coordinates
    
    def set_current_page(self, page):
        pass  # Mock implementation


@pytest.fixture
def app():
    """Create QApplication instance for tests."""
    return QApplication.instance() or QApplication([])


@pytest.fixture
def main_window(app):
    """Create MainWindow instance with mock components."""
    main_window = MainWindow()
    main_window.viewer = MockViewer()
    main_window.editor = MockEditor()
    main_window.coordinates_manager = TableCoordinates()
    main_window.all_extracted_coordinates = []
    return main_window


@pytest.mark.gui
class TestBatchAccumulation:
    """Test suite for batch extraction coordinate accumulation."""
    
    def test_page_extraction_completion(self, main_window):
        """Test that page extraction properly adds coordinates to both data structures."""
        # Simulate page 1 extraction
        page1_coords = [
            {
                'id': 'temp1',
                'page': 1,
                'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200,
                'user_created': False
            },
            {
                'id': 'temp2', 
                'page': 1,
                'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400,
                'user_created': False
            }
        ]
        
        main_window.on_page_extraction_completed(1, page1_coords)
        
        # Verify state after page 1
        manager_count = len(main_window.coordinates_manager.get_all_coordinates())
        extracted_count = len(main_window.all_extracted_coordinates)
        
        assert manager_count == 2, f"Expected 2 coordinates in manager, got {manager_count}"
        assert extracted_count == 2, f"Expected 2 coordinates in extracted list, got {extracted_count}"
    
    def test_deletion_during_batch_process(self, main_window):
        """Test that deletion works during batch processing."""
        # Add initial coordinates
        page1_coords = [
            {
                'id': 'temp1',
                'page': 1,
                'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200,
                'user_created': False
            }
        ]
        
        main_window.on_page_extraction_completed(1, page1_coords)
        
        # Test deletion during batch process
        coord_to_delete = main_window.all_extracted_coordinates[0]['id']
        result = main_window.delete_coordinate(coord_to_delete)
        
        assert result is not False, "Deletion should succeed"
        
        manager_count_after_del = len(main_window.coordinates_manager.get_all_coordinates())
        extracted_count_after_del = len(main_window.all_extracted_coordinates)
        
        assert manager_count_after_del == 0, f"Expected 0 coordinates in manager after deletion, got {manager_count_after_del}"
        assert extracted_count_after_del == 0, f"Expected 0 coordinates in extracted list after deletion, got {extracted_count_after_del}"
    
    def test_coordinate_accumulation_across_pages(self, main_window):
        """Test that coordinates properly accumulate across multiple pages."""
        # Page 1
        page1_coords = [
            {
                'id': 'temp1',
                'page': 1,
                'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200,
                'user_created': False
            }
        ]
        main_window.on_page_extraction_completed(1, page1_coords)
        
        # Delete one coordinate to test persistence
        coord_to_delete = main_window.all_extracted_coordinates[0]['id']
        main_window.delete_coordinate(coord_to_delete)
        
        # Add page 1 coordinate back for accumulation test
        page1_coords_remaining = [
            {
                'id': 'temp1b',
                'page': 1,
                'x1': 150, 'y1': 150, 'x2': 250, 'y2': 250,
                'user_created': False
            }
        ]
        main_window.on_page_extraction_completed(1, page1_coords_remaining)
        
        # Page 2
        page2_coords = [
            {
                'id': 'temp2',
                'page': 2,
                'x1': 500, 'y1': 500, 'x2': 600, 'y2': 600,
                'user_created': False
            }
        ]
        main_window.on_page_extraction_completed(2, page2_coords)
        
        # Verify accumulation (should have 1 from page 1 + 1 from page 2)
        manager_count = len(main_window.coordinates_manager.get_all_coordinates())
        extracted_count = len(main_window.all_extracted_coordinates)
        
        assert manager_count == 2, f"Expected 2 coordinates in manager after page 2, got {manager_count}"
        assert extracted_count == 2, f"Expected 2 coordinates in extracted list after page 2, got {extracted_count}"
        
        # Verify we have coordinates from both pages
        pages = [coord['page'] for coord in main_window.all_extracted_coordinates]
        assert 1 in pages, "Should have coordinate from page 1"
        assert 2 in pages, "Should have coordinate from page 2"
    
    def test_deletion_after_accumulation(self, main_window):
        """Test deletion works after accumulating coordinates from multiple pages."""
        # Add coordinates from multiple pages
        page1_coords = [
            {
                'id': 'temp1',
                'page': 1,
                'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200,
                'user_created': False
            }
        ]
        main_window.on_page_extraction_completed(1, page1_coords)
        
        page2_coords = [
            {
                'id': 'temp2',
                'page': 2,
                'x1': 500, 'y1': 500, 'x2': 600, 'y2': 600,
                'user_created': False
            }
        ]
        main_window.on_page_extraction_completed(2, page2_coords)
        
        # Delete page 2 coordinate
        page2_coord = next(coord for coord in main_window.all_extracted_coordinates if coord['page'] == 2)
        result = main_window.delete_coordinate(page2_coord['id'])
        
        assert result is not False, "Deletion should succeed"
        
        # Verify only page 1 coordinate remains
        manager_count = len(main_window.coordinates_manager.get_all_coordinates())
        extracted_count = len(main_window.all_extracted_coordinates)
        
        assert manager_count == 1, f"Expected 1 coordinate in manager after deletion, got {manager_count}"
        assert extracted_count == 1, f"Expected 1 coordinate in extracted list after deletion, got {extracted_count}"
        
        remaining_coord = main_window.all_extracted_coordinates[0]
        assert remaining_coord['page'] == 1, f"Expected remaining coordinate to be from page 1, got page {remaining_coord['page']}"
    
    def test_batch_completion_synchronization(self, main_window):
        """Test that batch completion maintains coordinate synchronization."""
        # Add some coordinates
        page1_coords = [
            {
                'id': 'temp1',
                'page': 1,
                'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200,
                'user_created': False
            }
        ]
        main_window.on_page_extraction_completed(1, page1_coords)
        
        # Simulate batch completion
        all_coords_for_completion = [
            coord.copy() for coord in main_window.all_extracted_coordinates
        ]
        main_window.on_batch_extraction_completed(all_coords_for_completion)
        
        # Verify synchronization is maintained
        manager_count = len(main_window.coordinates_manager.get_all_coordinates())
        extracted_count = len(main_window.all_extracted_coordinates)
        
        assert manager_count == extracted_count, f"Counts should match: manager={manager_count}, extracted={extracted_count}"
        assert manager_count == 1, f"Expected 1 coordinate after batch completion, got {manager_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
