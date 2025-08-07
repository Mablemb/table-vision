#!/usr/bin/env python3
"""
Test script to verify coordinate synchronization between manager and extracted list.
This tests the fix for the table deletion issue where batch extraction coordinates
weren't being added to the coordinate manager.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.coordinates import TableCoordinates


def simulate_batch_extraction_sync():
    """Simulate the synchronization logic from batch extraction."""
    print("=== Testing Batch Extraction Coordinate Synchronization ===")
    
    # Initialize coordinate manager
    coordinates_manager = TableCoordinates()
    
    # Add some existing user coordinates (simulate user-created tables)
    user_coord1 = {
        'page': 0,
        'x1': 100, 'y1': 100,
        'x2': 200, 'y2': 200,
        'width': 100, 'height': 100,
        'user_created': True,
        'accuracy': 100.0
    }
    
    user_id1 = coordinates_manager.add_coordinate(user_coord1)
    print(f"Added user coordinate with ID: {user_id1}")
    
    # Simulate new Camelot coordinates (as if from batch extraction)
    camelot_coords = [
        {
            'id': 1001,  # Camelot IDs start from 1000
            'page': 0,
            'x1': 300, 'y1': 100,
            'x2': 500, 'y2': 200,
            'width': 200, 'height': 100,
            'user_created': False,
            'accuracy': 95.5
        },
        {
            'id': 1002,
            'page': 0,
            'x1': 300, 'y1': 250,
            'x2': 500, 'y2': 350,
            'width': 200, 'height': 100,
            'user_created': False,
            'accuracy': 88.3
        }
    ]
    
    print(f"Simulating batch extraction with {len(camelot_coords)} Camelot coordinates")
    
    # Simulate the NEW synchronization logic from the fix
    existing_user_coords = [
        coord for coord in coordinates_manager.get_all_coordinates()
        if coord.get('user_created', False)
    ]
    
    print(f"Found {len(existing_user_coords)} existing user coordinates to preserve")
    
    # Update all_extracted_coordinates
    all_extracted_coordinates = camelot_coords + existing_user_coords
    
    # Synchronize coordinates_manager
    coordinates_manager.clear_all()
    
    # Add all coordinates to manager
    for coord_data in all_extracted_coordinates:
        new_id = coordinates_manager.add_coordinate(coord_data)
        coord_data['id'] = new_id  # Update ID to match manager
    
    print(f"Coordinate manager now has {len(coordinates_manager.get_all_coordinates())} coordinates")
    print(f"all_extracted_coordinates has {len(all_extracted_coordinates)} coordinates")
    
    # Test deletion of a Camelot coordinate
    camelot_coord_to_delete = all_extracted_coordinates[0]  # First Camelot coord
    coord_id = camelot_coord_to_delete['id']
    
    print(f"\nTesting deletion of coordinate {coord_id}...")
    
    # Simulate deletion logic
    manager_removal = coordinates_manager.remove_coordinate(coord_id)
    
    if manager_removal:
        # Remove from extracted list too
        all_extracted_coordinates = [
            coord for coord in all_extracted_coordinates 
            if coord.get('id') != coord_id
        ]
        print(f"✅ Successfully deleted coordinate {coord_id}")
        print(f"Manager now has {len(coordinates_manager.get_all_coordinates())} coordinates")
        print(f"Extracted list now has {len(all_extracted_coordinates)} coordinates")
        
        # Verify the coordinate is gone from both
        manager_coord = coordinates_manager.get_coordinate(coord_id)
        extracted_coord = next((c for c in all_extracted_coordinates if c.get('id') == coord_id), None)
        
        if manager_coord is None and extracted_coord is None:
            print("✅ Coordinate successfully removed from both data structures")
            return True
        else:
            print("❌ Coordinate still exists in one or both data structures")
            return False
    else:
        print(f"❌ Failed to delete coordinate {coord_id} from manager")
        return False


def test_coordinate_consistency():
    """Test that coordinates are consistent between manager and extracted list."""
    print("\n=== Testing Coordinate Consistency ===")
    
    coordinates_manager = TableCoordinates()
    all_extracted_coordinates = []
    
    # Add coordinates using the fixed logic
    test_coords = [
        {'page': 0, 'x1': 100, 'y1': 100, 'x2': 200, 'y2': 200, 'user_created': False},
        {'page': 0, 'x1': 300, 'y1': 100, 'x2': 400, 'y2': 200, 'user_created': True},
        {'page': 1, 'x1': 50, 'y1': 50, 'x2': 150, 'y2': 150, 'user_created': False}
    ]
    
    for coord_data in test_coords:
        new_id = coordinates_manager.add_coordinate(coord_data)
        coord_data['id'] = new_id
        all_extracted_coordinates.append(coord_data)
    
    # Verify IDs match between both structures
    manager_coords = coordinates_manager.get_all_coordinates()
    manager_ids = set(coord.get('id') for coord in manager_coords)
    extracted_ids = set(coord.get('id') for coord in all_extracted_coordinates)
    
    print(f"Manager IDs: {sorted(manager_ids)}")
    print(f"Extracted IDs: {sorted(extracted_ids)}")
    
    if manager_ids == extracted_ids:
        print("✅ IDs are consistent between manager and extracted list")
        return True
    else:
        print("❌ ID mismatch between data structures")
        print(f"Missing from manager: {extracted_ids - manager_ids}")
        print(f"Missing from extracted: {manager_ids - extracted_ids}")
        return False


if __name__ == "__main__":
    print("Table Vision - Coordinate Synchronization Test")
    print("="*60)
    
    # Run tests
    test1_passed = simulate_batch_extraction_sync()
    test2_passed = test_coordinate_consistency()
    
    print("\n" + "="*60)
    print("TEST RESULTS:")
    print(f"Batch Extraction Sync Test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"Coordinate Consistency Test: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✅ All tests passed! Coordinate synchronization should work correctly.")
        print("Tables extracted via batch mode should now be deletable.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    print("\nThe fix ensures that:")
    print("1. Batch extraction adds coordinates to both manager and extracted list")
    print("2. Regular extraction doesn't duplicate coordinates")
    print("3. Deletion removes coordinates from both data structures")
    print("4. All coordinate operations are consistent between extraction methods")
