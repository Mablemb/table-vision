#!/usr/bin/env python3
"""
Test batch extraction coordinate accumulation fix.

This test verifies that:
1. Coordinates are properly accumulated during batch extraction
2. Deletion works throughout the batch process, not just at the end
3. Both data structures (coordinates_manager and all_extracted_coordinates) stay synchronized
"""

import sys
import os

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

def test_batch_accumulation():
    """Test that batch extraction properly accumulates coordinates."""
    print("🧪 Testing batch extraction coordinate accumulation...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Create main window instance
    main_window = MainWindow()
    
    # Set up mock components
    main_window.viewer = MockViewer()
    main_window.editor = MockEditor()
    main_window.coordinates_manager = TableCoordinates()
    main_window.all_extracted_coordinates = []
    
    print("✅ Main window and components initialized")
    
    # Simulate batch extraction: Page 1
    print("\n📄 Simulating page 1 extraction...")
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
    manager_count_p1 = len(main_window.coordinates_manager.get_all_coordinates())
    extracted_count_p1 = len(main_window.all_extracted_coordinates)
    
    print(f"📊 After page 1: Manager={manager_count_p1}, Extracted={extracted_count_p1}")
    assert manager_count_p1 == 2, f"Expected 2 coordinates in manager, got {manager_count_p1}"
    assert extracted_count_p1 == 2, f"Expected 2 coordinates in extracted list, got {extracted_count_p1}"
    
    # Test deletion during batch process
    print("\n🗑️ Testing deletion after page 1...")
    coord_to_delete = main_window.all_extracted_coordinates[0]['id']
    print(f"Deleting coordinate: {coord_to_delete}")
    
    result = main_window.delete_coordinate(coord_to_delete)
    print(f"Deletion result: {result}")
    
    manager_count_after_del = len(main_window.coordinates_manager.get_all_coordinates())
    extracted_count_after_del = len(main_window.all_extracted_coordinates)
    
    print(f"📊 After deletion: Manager={manager_count_after_del}, Extracted={extracted_count_after_del}")
    assert manager_count_after_del == 1, f"Expected 1 coordinate in manager after deletion, got {manager_count_after_del}"
    assert extracted_count_after_del == 1, f"Expected 1 coordinate in extracted list after deletion, got {extracted_count_after_del}"
    
    # Simulate batch extraction: Page 2
    print("\n📄 Simulating page 2 extraction...")
    page2_coords = [
        {
            'id': 'temp3',
            'page': 2,
            'x1': 500, 'y1': 500, 'x2': 600, 'y2': 600,
            'user_created': False
        }
    ]
    
    main_window.on_page_extraction_completed(2, page2_coords)
    
    # Verify accumulation (should have 1 from page 1 + 1 from page 2)
    manager_count_p2 = len(main_window.coordinates_manager.get_all_coordinates())
    extracted_count_p2 = len(main_window.all_extracted_coordinates)
    
    print(f"📊 After page 2: Manager={manager_count_p2}, Extracted={extracted_count_p2}")
    assert manager_count_p2 == 2, f"Expected 2 coordinates in manager after page 2, got {manager_count_p2}"
    assert extracted_count_p2 == 2, f"Expected 2 coordinates in extracted list after page 2, got {extracted_count_p2}"
    
    # Test deletion during batch process (after accumulating multiple pages)
    print("\n🗑️ Testing deletion after page 2...")
    coord_to_delete_p2 = main_window.all_extracted_coordinates[1]['id']  # Delete the page 2 coordinate
    print(f"Deleting coordinate: {coord_to_delete_p2}")
    
    result = main_window.delete_coordinate(coord_to_delete_p2)
    print(f"Deletion result: {result}")
    
    manager_count_final = len(main_window.coordinates_manager.get_all_coordinates())
    extracted_count_final = len(main_window.all_extracted_coordinates)
    
    print(f"📊 After final deletion: Manager={manager_count_final}, Extracted={extracted_count_final}")
    assert manager_count_final == 1, f"Expected 1 coordinate in manager after final deletion, got {manager_count_final}"
    assert extracted_count_final == 1, f"Expected 1 coordinate in extracted list after final deletion, got {extracted_count_final}"
    
    # Verify the remaining coordinate is from page 1
    remaining_coord = main_window.all_extracted_coordinates[0]
    assert remaining_coord['page'] == 1, f"Expected remaining coordinate to be from page 1, got page {remaining_coord['page']}"
    
    print("✅ All batch accumulation tests passed!")
    
    # Test batch completion (should not affect the accumulated coordinates)
    print("\n🏁 Testing batch completion...")
    all_coords_for_completion = [
        coord.copy() for coord in main_window.all_extracted_coordinates
    ]
    
    main_window.on_batch_extraction_completed(all_coords_for_completion)
    
    final_manager_count = len(main_window.coordinates_manager.get_all_coordinates())
    final_extracted_count = len(main_window.all_extracted_coordinates)
    
    print(f"📊 After batch completion: Manager={final_manager_count}, Extracted={final_extracted_count}")
    assert final_manager_count == 1, f"Expected 1 coordinate in manager after batch completion, got {final_manager_count}"
    assert final_extracted_count == 1, f"Expected 1 coordinate in extracted list after batch completion, got {final_extracted_count}"
    
    print("✅ Batch completion test passed!")
    print("\n🎉 All tests passed! Batch extraction accumulation is working correctly.")
    
    return True

if __name__ == "__main__":
    try:
        test_batch_accumulation()
        print("\n✅ SUCCESS: Batch accumulation fix verified!")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
