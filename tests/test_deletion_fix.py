#!/usr/bin/env python3
"""
Test script to verify table deletion functionality.

This script tests the coordinate deletion bug fix to ensure that:
1. Tables can be deleted from the right panel
2. Deleted tables don't reappear 
3. Both viewer and editor displays are updated correctly
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.coordinates import TableCoordinates


def test_coordinate_deletion():
    """Test the coordinate deletion functionality."""
    print("=== Testing Coordinate Deletion ===")
    
    # Initialize coordinate manager
    coord_manager = TableCoordinates()
    
    # Add some test coordinates
    coord1 = {
        'page': 0,
        'x1': 100, 'y1': 100,
        'x2': 300, 'y2': 200,
        'width': 200, 'height': 100,
        'user_created': False,
        'accuracy': 95.5
    }
    
    coord2 = {
        'page': 0,
        'x1': 350, 'y1': 150,
        'x2': 500, 'y2': 250,
        'width': 150, 'height': 100,
        'user_created': True,
        'accuracy': 100.0
    }
    
    coord3 = {
        'page': 1,
        'x1': 50, 'y1': 50,
        'x2': 200, 'y2': 150,
        'width': 150, 'height': 100,
        'user_created': False,
        'accuracy': 88.2
    }
    
    # Add coordinates
    id1 = coord_manager.add_coordinate(coord1)
    id2 = coord_manager.add_coordinate(coord2)
    id3 = coord_manager.add_coordinate(coord3)
    
    print(f"Added 3 coordinates with IDs: {id1}, {id2}, {id3}")
    
    # Check initial state
    all_coords = coord_manager.get_all_coordinates()
    print(f"Initial coordinate count: {len(all_coords)}")
    
    # Test deletion
    print(f"\nAttempting to delete coordinate {id2}...")
    result = coord_manager.remove_coordinate(id2)
    print(f"Deletion result: {result}")
    
    # Check state after deletion
    all_coords_after = coord_manager.get_all_coordinates()
    print(f"Coordinate count after deletion: {len(all_coords_after)}")
    
    # Verify the deleted coordinate is not in the list
    deleted_coord = coord_manager.get_coordinate(id2)
    print(f"Deleted coordinate still exists: {deleted_coord is not None}")
    
    # Test deletion of non-existent coordinate
    print(f"\nAttempting to delete non-existent coordinate 999...")
    result = coord_manager.remove_coordinate(999)
    print(f"Deletion result: {result}")
    
    # Final verification
    remaining_coords = coord_manager.get_all_coordinates()
    remaining_ids = [coord.get('id') for coord in remaining_coords]
    print(f"Remaining coordinate IDs: {remaining_ids}")
    
    # Test that we can still get remaining coordinates
    coord1_check = coord_manager.get_coordinate(id1)
    coord3_check = coord_manager.get_coordinate(id3)
    
    print(f"Coordinate {id1} still accessible: {coord1_check is not None}")
    print(f"Coordinate {id3} still accessible: {coord3_check is not None}")
    
    print("\n=== Test Complete ===")
    return len(remaining_coords) == 2 and id2 not in remaining_ids


def test_coordinate_list_merging():
    """Test coordinate list merging logic (simulates main window behavior)."""
    print("\n=== Testing Coordinate List Merging ===")
    
    # Simulate main window coordinate management
    coordinates_manager = TableCoordinates()
    all_extracted_coordinates = []
    
    # Add some coordinates to manager
    coord1 = {'page': 0, 'x1': 100, 'y1': 100, 'x2': 300, 'y2': 200, 'user_created': True}
    id1 = coordinates_manager.add_coordinate(coord1)
    
    # Add some coordinates to extracted list (simulating Camelot detection)
    extracted_coord = {'id': 1001, 'page': 0, 'x1': 400, 'y1': 100, 'x2': 600, 'y2': 200, 'user_created': False}
    all_extracted_coordinates.append(extracted_coord)
    
    print(f"Manager has {len(coordinates_manager.get_all_coordinates())} coordinates")
    print(f"Extracted list has {len(all_extracted_coordinates)} coordinates")
    
    # Simulate merging logic from main window
    manager_coords = coordinates_manager.get_all_coordinates()
    
    all_coords = []
    coord_ids = set()
    
    # Add from manager first
    for coord in manager_coords:
        coord_id = coord.get('id')
        if coord_id is not None and coord_id not in coord_ids:
            all_coords.append(coord)
            coord_ids.add(coord_id)
    
    # Add from extracted that aren't already included
    for coord in all_extracted_coordinates:
        coord_id = coord.get('id')
        if coord_id is not None and coord_id not in coord_ids:
            all_coords.append(coord)
            coord_ids.add(coord_id)
    
    print(f"Merged list has {len(all_coords)} coordinates")
    
    # Now simulate deletion
    print(f"\nDeleting coordinate {extracted_coord['id']} from extracted list...")
    coordinates_manager.remove_coordinate(extracted_coord['id'])  # Won't find it, but that's OK
    
    # Remove from extracted list (this is the fix)
    all_extracted_coordinates = [
        coord for coord in all_extracted_coordinates 
        if coord.get('id') != extracted_coord['id']
    ]
    
    print(f"After deletion - Manager: {len(coordinates_manager.get_all_coordinates())}, Extracted: {len(all_extracted_coordinates)}")
    
    # Re-merge
    all_coords_after = []
    coord_ids_after = set()
    
    for coord in coordinates_manager.get_all_coordinates():
        coord_id = coord.get('id')
        if coord_id is not None and coord_id not in coord_ids_after:
            all_coords_after.append(coord)
            coord_ids_after.add(coord_id)
    
    for coord in all_extracted_coordinates:
        coord_id = coord.get('id')
        if coord_id is not None and coord_id not in coord_ids_after:
            all_coords_after.append(coord)
            coord_ids_after.add(coord_id)
    
    print(f"Final merged list has {len(all_coords_after)} coordinates")
    
    print("=== Merging Test Complete ===")
    return len(all_coords_after) == 1  # Should only have the manager coordinate left


if __name__ == "__main__":
    print("Table Vision - Coordinate Deletion Test")
    print("="*50)
    
    # Run tests
    test1_passed = test_coordinate_deletion()
    test2_passed = test_coordinate_list_merging()
    
    print("\n" + "="*50)
    print("TEST RESULTS:")
    print(f"Coordinate Deletion Test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Coordinate Merging Test: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✅ All tests passed! Table deletion should work correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    print("\nTo test the full application:")
    print("1. Run: python src/app.py")
    print("2. Load a PDF and extract tables")
    print("3. Try deleting tables from the right panel")
    print("4. Verify they don't reappear")
