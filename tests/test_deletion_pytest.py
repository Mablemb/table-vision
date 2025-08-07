#!/usr/bin/env python3
"""
Pytest for table deletion functionality.

This test verifies that:
1. Coordinates can be deleted from both data structures
2. Deletion works correctly with different coordinate sources
3. Data structures stay synchronized after deletions
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
class TestDeletionFunctionality:
    """Test suite for table deletion functionality."""
    
    def test_basic_coordinate_deletion(self, main_window):
        """Test basic coordinate deletion from both data structures."""
        # Add coordinate to manager
        coord_data = {
            'page': 1,
            'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200,
            'user_created': False
        }
        coord_id = main_window.coordinates_manager.add_coordinate(coord_data)
        
        # Add to extracted list with same ID
        coord_data['id'] = coord_id
        main_window.all_extracted_coordinates.append(coord_data)
        
        # Verify initial state
        assert len(main_window.coordinates_manager.get_all_coordinates()) == 1
        assert len(main_window.all_extracted_coordinates) == 1
        
        # Delete coordinate
        result = main_window.delete_coordinate(coord_id)
        
        # Verify deletion
        assert result is not False, "Deletion should succeed"
        assert len(main_window.coordinates_manager.get_all_coordinates()) == 0
        assert len(main_window.all_extracted_coordinates) == 0
    
    def test_deletion_with_multiple_coordinates(self, main_window):
        """Test deletion when multiple coordinates exist."""
        coords_data = [
            {'page': 1, 'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'user_created': False},
            {'page': 1, 'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400, 'user_created': False},
            {'page': 2, 'x1': 500, 'y1': 500, 'x2': 600, 'y2': 600, 'user_created': False}
        ]
        
        coord_ids = []
        for coord_data in coords_data:
            coord_id = main_window.coordinates_manager.add_coordinate(coord_data)
            coord_data['id'] = coord_id
            main_window.all_extracted_coordinates.append(coord_data)
            coord_ids.append(coord_id)
        
        # Verify initial state
        assert len(main_window.coordinates_manager.get_all_coordinates()) == 3
        assert len(main_window.all_extracted_coordinates) == 3
        
        # Delete middle coordinate
        result = main_window.delete_coordinate(coord_ids[1])
        
        # Verify selective deletion
        assert result is not False, "Deletion should succeed"
        assert len(main_window.coordinates_manager.get_all_coordinates()) == 2
        assert len(main_window.all_extracted_coordinates) == 2
        
        # Verify correct coordinates remain
        remaining_ids = [coord['id'] for coord in main_window.all_extracted_coordinates]
        assert coord_ids[0] in remaining_ids
        assert coord_ids[1] not in remaining_ids
        assert coord_ids[2] in remaining_ids
    
    def test_deletion_nonexistent_coordinate(self, main_window):
        """Test deletion of non-existent coordinate."""
        # Add one coordinate
        coord_data = {
            'page': 1,
            'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200,
            'user_created': False
        }
        coord_id = main_window.coordinates_manager.add_coordinate(coord_data)
        coord_data['id'] = coord_id
        main_window.all_extracted_coordinates.append(coord_data)
        
        # Try to delete non-existent coordinate
        result = main_window.delete_coordinate(999)
        
        # Verify deletion failed and data unchanged
        assert result is None or result is False, "Deletion should fail for non-existent coordinate"
        assert len(main_window.coordinates_manager.get_all_coordinates()) == 1
        assert len(main_window.all_extracted_coordinates) == 1
    
    def test_deletion_with_user_created_coordinates(self, main_window):
        """Test deletion works with user-created coordinates."""
        # Add auto-detected coordinate
        auto_coord = {
            'page': 1,
            'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200,
            'user_created': False
        }
        auto_id = main_window.coordinates_manager.add_coordinate(auto_coord)
        auto_coord['id'] = auto_id
        main_window.all_extracted_coordinates.append(auto_coord)
        
        # Add user-created coordinate
        user_coord = {
            'page': 1,
            'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400,
            'user_created': True
        }
        user_id = main_window.coordinates_manager.add_coordinate(user_coord)
        user_coord['id'] = user_id
        main_window.all_extracted_coordinates.append(user_coord)
        
        # Verify initial state
        assert len(main_window.coordinates_manager.get_all_coordinates()) == 2
        assert len(main_window.all_extracted_coordinates) == 2
        
        # Delete auto-detected coordinate
        result = main_window.delete_coordinate(auto_id)
        
        # Verify deletion
        assert result is not False, "Deletion should succeed"
        assert len(main_window.coordinates_manager.get_all_coordinates()) == 1
        assert len(main_window.all_extracted_coordinates) == 1
        
        # Verify user-created coordinate remains
        remaining_coord = main_window.all_extracted_coordinates[0]
        assert remaining_coord['user_created'] is True
        assert remaining_coord['id'] == user_id
    
    def test_data_structure_synchronization(self, main_window):
        """Test that both data structures remain synchronized after operations."""
        # Add multiple coordinates
        coords_data = [
            {'page': 1, 'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'user_created': False},
            {'page': 2, 'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400, 'user_created': True}
        ]
        
        for coord_data in coords_data:
            coord_id = main_window.coordinates_manager.add_coordinate(coord_data)
            coord_data['id'] = coord_id
            main_window.all_extracted_coordinates.append(coord_data)
        
        # Verify synchronization
        manager_coords = main_window.coordinates_manager.get_all_coordinates()
        extracted_coords = main_window.all_extracted_coordinates
        
        assert len(manager_coords) == len(extracted_coords), "Data structures should have same count"
        
        # Verify IDs match
        manager_ids = set(coord['id'] for coord in manager_coords)
        extracted_ids = set(coord['id'] for coord in extracted_coords)
        
        assert manager_ids == extracted_ids, "Data structures should have matching IDs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
