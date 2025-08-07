#!/usr/bin/env python3
"""
Pytest for coordinate synchronization functionality.

This test verifies that:
1. Coordinates stay synchronized between manager and extracted list
2. Batch and regular extraction maintain synchronization
3. User-created coordinates are properly handled
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


class MockEditor:
    """Mock editor for testing."""
    def __init__(self):
        self.coordinates = []
    
    def set_coordinates(self, coordinates):
        self.coordinates = coordinates
    
    def set_current_page(self, page):
        pass


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
class TestCoordinateSynchronization:
    """Test suite for coordinate synchronization."""
    
    def test_regular_extraction_synchronization(self, main_window):
        """Test synchronization after regular extraction."""
        coords = [
            {'id': 'temp1', 'page': 1, 'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'user_created': False},
            {'id': 'temp2', 'page': 1, 'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400, 'user_created': False}
        ]
        
        main_window.on_extraction_finished(coords)
        
        # Verify synchronization
        manager_count = len(main_window.coordinates_manager.get_all_coordinates())
        extracted_count = len(main_window.all_extracted_coordinates)
        
        assert manager_count == extracted_count, f"Counts should match: manager={manager_count}, extracted={extracted_count}"
        assert manager_count == 2, "Should have 2 coordinates after regular extraction"
    
    def test_batch_extraction_synchronization(self, main_window):
        """Test synchronization during batch extraction."""
        # Page 1
        page1_coords = [
            {'id': 'temp1', 'page': 1, 'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'user_created': False}
        ]
        main_window.on_page_extraction_completed(1, page1_coords)
        
        # Verify synchronization after page 1
        manager_count = len(main_window.coordinates_manager.get_all_coordinates())
        extracted_count = len(main_window.all_extracted_coordinates)
        assert manager_count == extracted_count == 1
        
        # Page 2
        page2_coords = [
            {'id': 'temp2', 'page': 2, 'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400, 'user_created': False}
        ]
        main_window.on_page_extraction_completed(2, page2_coords)
        
        # Verify synchronization after page 2
        manager_count = len(main_window.coordinates_manager.get_all_coordinates())
        extracted_count = len(main_window.all_extracted_coordinates)
        assert manager_count == extracted_count == 2
    
    def test_synchronization_after_deletion(self, main_window):
        """Test synchronization is maintained after deletion."""
        # Add coordinates
        coords = [
            {'id': 'temp1', 'page': 1, 'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'user_created': False},
            {'id': 'temp2', 'page': 1, 'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400, 'user_created': False}
        ]
        main_window.on_extraction_finished(coords)
        
        # Delete one coordinate
        coord_to_delete = main_window.all_extracted_coordinates[0]['id']
        main_window.delete_coordinate(coord_to_delete)
        
        # Verify synchronization after deletion
        manager_count = len(main_window.coordinates_manager.get_all_coordinates())
        extracted_count = len(main_window.all_extracted_coordinates)
        
        assert manager_count == extracted_count, f"Counts should match after deletion: manager={manager_count}, extracted={extracted_count}"
        assert manager_count == 1, "Should have 1 coordinate after deletion"
    
    def test_id_consistency(self, main_window):
        """Test that IDs are consistent between data structures."""
        coords = [
            {'id': 'temp1', 'page': 1, 'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'user_created': False}
        ]
        main_window.on_extraction_finished(coords)
        
        # Get coordinates from both structures
        manager_coords = main_window.coordinates_manager.get_all_coordinates()
        extracted_coords = main_window.all_extracted_coordinates
        
        # Verify IDs match
        manager_ids = [coord['id'] for coord in manager_coords]
        extracted_ids = [coord['id'] for coord in extracted_coords]
        
        assert manager_ids == extracted_ids, "IDs should match between data structures"
    
    def test_user_coordinate_preservation(self, main_window):
        """Test that user-created coordinates are preserved during batch processing."""
        # Add user-created coordinate to manager
        user_coord = {
            'page': 1,
            'x1': 500, 'y1': 500, 'x2': 600, 'y2': 600,
            'user_created': True
        }
        user_id = main_window.coordinates_manager.add_coordinate(user_coord)
        user_coord['id'] = user_id
        main_window.all_extracted_coordinates.append(user_coord)
        
        # Simulate batch extraction on same page
        page1_coords = [
            {'id': 'temp1', 'page': 1, 'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'user_created': False}
        ]
        main_window.on_page_extraction_completed(1, page1_coords)
        
        # Verify user coordinate is preserved (ID may change but properties remain)
        user_coords = [coord for coord in main_window.all_extracted_coordinates if coord.get('user_created', False)]
        auto_coords = [coord for coord in main_window.all_extracted_coordinates if not coord.get('user_created', False)]
        
        assert len(user_coords) == 1, "User-created coordinate should be preserved"
        assert len(auto_coords) == 1, "Auto-detected coordinate should be added"
        
        # Verify user coordinate properties are preserved (ID may be reassigned)
        user_coord = user_coords[0]
        assert user_coord['page'] == 1, "User coordinate page should be preserved"
        assert user_coord['x1'] == 500, "User coordinate x1 should be preserved"
        assert user_coord['y1'] == 500, "User coordinate y1 should be preserved"
        assert user_coord['x2'] == 600, "User coordinate x2 should be preserved"
        assert user_coord['y2'] == 600, "User coordinate y2 should be preserved"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
