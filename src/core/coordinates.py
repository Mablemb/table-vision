"""
Coordinate management module for handling table coordinates.
"""
from typing import List, Dict, Optional, Tuple
import json
import os


class TableCoordinates:
    """Manages table coordinates including add, remove, update operations."""
    
    def __init__(self):
        self.coordinates: List[Dict] = []
        self.next_id = 1  # Start user IDs from 1, Camelot IDs start from 1000
    
    def add_coordinate(self, coordinate: Dict) -> int:
        """
        Add a new coordinate entry.
        
        Args:
            coordinate: Dictionary containing coordinate information
            
        Returns:
            ID of the added coordinate
        """
        coord_copy = coordinate.copy()
        coord_copy['id'] = self.next_id
        coord_copy['user_created'] = coordinate.get('user_created', False)
        
        self.coordinates.append(coord_copy)
        self.next_id += 1
        
        return coord_copy['id']
    
    def remove_coordinate(self, coord_id: int) -> bool:
        """
        Remove a coordinate by ID.
        
        Args:
            coord_id: ID of the coordinate to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        for i, coord in enumerate(self.coordinates):
            if coord.get('id') == coord_id:
                del self.coordinates[i]
                return True
        return False
    
    def update_coordinate(self, coord_id: int, updates: Dict) -> bool:
        """
        Update an existing coordinate.
        
        Args:
            coord_id: ID of the coordinate to update
            updates: Dictionary of updates to apply
            
        Returns:
            True if updated successfully, False otherwise
        """
        for coord in self.coordinates:
            if coord.get('id') == coord_id:
                coord.update(updates)
                return True
        return False
    
    def get_coordinate(self, coord_id: int) -> Optional[Dict]:
        """Get a specific coordinate by ID."""
        for coord in self.coordinates:
            if coord.get('id') == coord_id:
                return coord
        return None
    
    def get_coordinates_for_page(self, page_num: int) -> List[Dict]:
        """Get all coordinates for a specific page."""
        return [coord for coord in self.coordinates if coord.get('page') == page_num]
    
    def get_all_coordinates(self) -> List[Dict]:
        """Get all coordinates."""
        return self.coordinates.copy()
    
    def create_user_coordinate(self, page: int, x1: float, y1: float, x2: float, y2: float) -> int:
        """
        Create a new user-defined coordinate.
        
        Args:
            page: Page number
            x1, y1: Bottom-left corner
            x2, y2: Top-right corner
            
        Returns:
            ID of the created coordinate
        """
        coordinate = {
            'page': page,
            'x1': min(x1, x2),
            'y1': min(y1, y2),
            'x2': max(x1, x2),
            'y2': max(y1, y2),
            'width': abs(x2 - x1),
            'height': abs(y2 - y1),
            'user_created': True,
            'accuracy': 100.0,  # User-created tables are considered perfect
            'whitespace': 0.0
        }
        
        return self.add_coordinate(coordinate)
    
    def validate_coordinate(self, coordinate: Dict) -> bool:
        """Validate that a coordinate has required fields."""
        required_fields = ['page', 'x1', 'y1', 'x2', 'y2']
        return all(field in coordinate for field in required_fields)
    
    def clear_all(self):
        """Clear all coordinates."""
        self.coordinates.clear()
        self.next_id = 1  # Reset to 1, not 0
    
    def get_bounding_rect(self, coord_id: int) -> Optional[Tuple[float, float, float, float]]:
        """Get bounding rectangle for a coordinate."""
        coord = self.get_coordinate(coord_id)
        if coord:
            return (coord['x1'], coord['y1'], coord['x2'], coord['y2'])
        return None
    
    def is_point_inside(self, coord_id: int, x: float, y: float) -> bool:
        """Check if a point is inside a coordinate rectangle."""
        coord = self.get_coordinate(coord_id)
        if coord:
            return (coord['x1'] <= x <= coord['x2'] and 
                   coord['y1'] <= y <= coord['y2'])
        return False
