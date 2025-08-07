#!/usr/bin/env python3
"""
Comprehensive Table Deletion Test Suite

This test suite verifies that table deletion works correctly across all scenarios:
1. Regular extraction followed by deletion
2. Batch extraction with deletion during processing
3. Mixed user-created and auto-detected coordinates
4. Data structure synchronization throughout the process
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
        pass

def test_comprehensive_deletion():
    """Run comprehensive deletion tests."""
    print("🧪 Running Comprehensive Table Deletion Test Suite")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Test 1: Regular Extraction and Deletion
    print("\n📋 Test 1: Regular Extraction and Deletion")
    print("-" * 40)
    
    main_window = MainWindow()
    main_window.viewer = MockViewer()
    main_window.editor = MockEditor()
    main_window.coordinates_manager = TableCoordinates()
    main_window.all_extracted_coordinates = []
    
    # Simulate regular extraction
    regular_coords = [
        {'id': 'temp1', 'page': 1, 'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'user_created': False},
        {'id': 'temp2', 'page': 1, 'x1': 300, 'y1': 300, 'x2': 400, 'y2': 400, 'user_created': False}
    ]
    
    main_window.on_extraction_finished(regular_coords)
    
    assert len(main_window.coordinates_manager.get_all_coordinates()) == 2, "Regular extraction: manager count"
    assert len(main_window.all_extracted_coordinates) == 2, "Regular extraction: extracted count"
    
    # Test deletion after regular extraction
    coord_to_delete = main_window.all_extracted_coordinates[0]['id']
    result = main_window.delete_coordinate(coord_to_delete)
    
    assert len(main_window.coordinates_manager.get_all_coordinates()) == 1, "After deletion: manager count"
    assert len(main_window.all_extracted_coordinates) == 1, "After deletion: extracted count"
    
    print("✅ Regular extraction and deletion test passed!")
    
    # Test 2: Batch Extraction with Real-time Deletion
    print("\n📋 Test 2: Batch Extraction with Real-time Deletion")
    print("-" * 50)
    
    # Reset for batch test
    main_window.coordinates_manager = TableCoordinates()
    main_window.all_extracted_coordinates = []
    
    # Batch extraction page 1
    batch_p1_coords = [
        {'id': 'temp3', 'page': 1, 'x1': 50, 'y1': 50, 'x2': 150, 'y2': 150, 'user_created': False},
        {'id': 'temp4', 'page': 1, 'x1': 250, 'y1': 250, 'x2': 350, 'y2': 350, 'user_created': False}
    ]
    
    main_window.on_page_extraction_completed(1, batch_p1_coords)
    
    assert len(main_window.coordinates_manager.get_all_coordinates()) == 2, "Batch page 1: manager count"
    assert len(main_window.all_extracted_coordinates) == 2, "Batch page 1: extracted count"
    
    # Delete during batch processing
    coord_to_delete = main_window.all_extracted_coordinates[0]['id']
    main_window.delete_coordinate(coord_to_delete)
    
    assert len(main_window.coordinates_manager.get_all_coordinates()) == 1, "Batch deletion: manager count"
    assert len(main_window.all_extracted_coordinates) == 1, "Batch deletion: extracted count"
    
    # Batch extraction page 2 (should accumulate, not replace)
    batch_p2_coords = [
        {'id': 'temp5', 'page': 2, 'x1': 450, 'y1': 450, 'x2': 550, 'y2': 550, 'user_created': False}
    ]
    
    main_window.on_page_extraction_completed(2, batch_p2_coords)
    
    assert len(main_window.coordinates_manager.get_all_coordinates()) == 2, "Batch page 2: manager count"
    assert len(main_window.all_extracted_coordinates) == 2, "Batch page 2: extracted count"
    
    # Verify we still have page 1 coordinate (accumulation worked)
    page_1_coords = [coord for coord in main_window.all_extracted_coordinates if coord['page'] == 1]
    page_2_coords = [coord for coord in main_window.all_extracted_coordinates if coord['page'] == 2]
    
    assert len(page_1_coords) == 1, "Page 1 coordinate preserved"
    assert len(page_2_coords) == 1, "Page 2 coordinate added"
    
    print("✅ Batch extraction with real-time deletion test passed!")
    
    # Test 3: Mixed User and Auto Coordinates
    print("\n📋 Test 3: Mixed User and Auto Coordinates")
    print("-" * 42)
    
    # Add a user-created coordinate
    user_coord = {
        'id': 'user1',
        'page': 1,
        'x1': 600, 'y1': 600, 'x2': 700, 'y2': 700,
        'user_created': True
    }
    
    # Add to both structures
    user_id = main_window.coordinates_manager.add_coordinate(user_coord)
    user_coord['id'] = user_id
    main_window.all_extracted_coordinates.append(user_coord)
    
    total_before = len(main_window.all_extracted_coordinates)
    assert total_before == 3, "After adding user coordinate"
    
    # Delete an auto-detected coordinate
    auto_coord_id = next(coord['id'] for coord in main_window.all_extracted_coordinates if not coord.get('user_created', False))
    main_window.delete_coordinate(auto_coord_id)
    
    remaining_coords = main_window.all_extracted_coordinates
    user_coords = [coord for coord in remaining_coords if coord.get('user_created', False)]
    auto_coords = [coord for coord in remaining_coords if not coord.get('user_created', False)]
    
    assert len(remaining_coords) == 2, "Total after deletion"
    assert len(user_coords) == 1, "User coordinate preserved"
    assert len(auto_coords) == 1, "One auto coordinate remaining"
    
    print("✅ Mixed user and auto coordinates test passed!")
    
    # Test 4: Batch Completion Synchronization
    print("\n📋 Test 4: Batch Completion Synchronization")
    print("-" * 44)
    
    # Simulate batch completion (should not disrupt existing coordinates)
    final_coords = [coord.copy() for coord in main_window.all_extracted_coordinates]
    main_window.on_batch_extraction_completed(final_coords)
    
    manager_final = len(main_window.coordinates_manager.get_all_coordinates())
    extracted_final = len(main_window.all_extracted_coordinates)
    
    assert manager_final == extracted_final, "Final synchronization"
    assert manager_final == 2, "Final count matches expected"
    
    print("✅ Batch completion synchronization test passed!")
    
    # Test 5: Data Structure Consistency
    print("\n📋 Test 5: Data Structure Consistency Check")
    print("-" * 44)
    
    # Verify all coordinates have consistent IDs between structures
    manager_coords = main_window.coordinates_manager.get_all_coordinates()
    extracted_coords = main_window.all_extracted_coordinates
    
    manager_ids = set(coord['id'] for coord in manager_coords)
    extracted_ids = set(coord['id'] for coord in extracted_coords)
    
    assert manager_ids == extracted_ids, "ID consistency between structures"
    
    # Verify all coordinates can be found in both structures
    for coord in extracted_coords:
        coord_id = coord['id']
        manager_coord = main_window.coordinates_manager.get_coordinate(coord_id)
        assert manager_coord is not None, f"Coordinate {coord_id} exists in manager"
    
    print("✅ Data structure consistency test passed!")
    
    print("\n" + "=" * 60)
    print("🎉 ALL COMPREHENSIVE DELETION TESTS PASSED!")
    print("✅ Table deletion functionality is working correctly across all scenarios")
    
    return True

if __name__ == "__main__":
    try:
        test_comprehensive_deletion()
        print("\n✅ SUCCESS: Comprehensive deletion test suite completed!")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
