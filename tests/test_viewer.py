"""
Unit tests for the visualization components.
"""
import unittest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.models import TableCoordinate


class TestTableCoordinate(unittest.TestCase):
    """Test cases for coordinate validation and manipulation."""

    def test_coordinate_validation(self):
        """Test that coordinates are created with valid values."""
        coord = TableCoordinate(
            id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        
        # Check that coordinates are properly ordered
        self.assertLess(coord.x1, coord.x2)
        self.assertLess(coord.y1, coord.y2)
        
        # Check calculated properties
        self.assertEqual(coord.width, 200)
        self.assertEqual(coord.height, 200)

    def test_coordinate_normalization(self):
        """Test coordinate normalization (ensuring x1 < x2, y1 < y2)."""
        # Create coordinate with reversed values
        coord = TableCoordinate(
            id=1,
            page=1,
            x1=300,  # larger than x2
            y1=400,  # larger than y2
            x2=100,
            y2=200
        )
        
        # Width and height should still be positive
        self.assertGreater(coord.width, 0)
        self.assertGreater(coord.height, 0)

    def test_coordinate_area_calculation(self):
        """Test area calculation."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=0,
            y1=0,
            x2=100,
            y2=50
        )
        
        self.assertEqual(coord.area, 5000)

    def test_coordinate_serialization(self):
        """Test coordinate serialization and deserialization."""
        original = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400,
            accuracy=95.5,
            is_manual=True
        )
        
        # Convert to dict and back
        data = original.to_dict()
        restored = TableCoordinate.from_dict(data)
        
        self.assertEqual(original.table_id, restored.table_id)
        self.assertEqual(original.page, restored.page)
        self.assertEqual(original.x1, restored.x1)
        self.assertEqual(original.y1, restored.y1)
        self.assertEqual(original.x2, restored.x2)
        self.assertEqual(original.y2, restored.y2)
        self.assertEqual(original.accuracy, restored.accuracy)
        self.assertEqual(original.is_manual, restored.is_manual)


class TestCoordinateManipulation(unittest.TestCase):
    """Test cases for coordinate manipulation functions."""

    def test_coordinate_scaling(self):
        """Test scaling coordinates by a factor."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        
        # Scale by factor of 2
        scale_factor = 2.0
        scaled_x1 = coord.x1 * scale_factor
        scaled_y1 = coord.y1 * scale_factor
        scaled_x2 = coord.x2 * scale_factor
        scaled_y2 = coord.y2 * scale_factor
        
        self.assertEqual(scaled_x1, 200)
        self.assertEqual(scaled_y1, 400)
        self.assertEqual(scaled_x2, 600)
        self.assertEqual(scaled_y2, 800)

    def test_coordinate_translation(self):
        """Test translating coordinates by an offset."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        
        # Translate by offset
        offset_x, offset_y = 50, 75
        translated_x1 = coord.x1 + offset_x
        translated_y1 = coord.y1 + offset_y
        translated_x2 = coord.x2 + offset_x
        translated_y2 = coord.y2 + offset_y
        
        self.assertEqual(translated_x1, 150)
        self.assertEqual(translated_y1, 275)
        self.assertEqual(translated_x2, 350)
        self.assertEqual(translated_y2, 475)

    def test_coordinate_intersection(self):
        """Test checking if two coordinates intersect."""
        coord1 = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        
        coord2 = TableCoordinate(
            table_id=2,
            page=1,
            x1=250,
            y1=350,
            x2=450,
            y2=550
        )
        
        # These coordinates should intersect
        # Intersection logic would be implemented in the actual viewer
        intersects = (coord1.x1 < coord2.x2 and coord1.x2 > coord2.x1 and
                     coord1.y1 < coord2.y2 and coord1.y2 > coord2.y1)
        
        self.assertTrue(intersects)

    def test_coordinate_contains_point(self):
        """Test checking if a coordinate contains a point."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        
        # Point inside the rectangle
        point_inside = (200, 300)
        contains_inside = (coord.x1 <= point_inside[0] <= coord.x2 and
                          coord.y1 <= point_inside[1] <= coord.y2)
        self.assertTrue(contains_inside)
        
        # Point outside the rectangle
        point_outside = (50, 100)
        contains_outside = (coord.x1 <= point_outside[0] <= coord.x2 and
                           coord.y1 <= point_outside[1] <= coord.y2)
        self.assertFalse(contains_outside)


class TestCoordinateValidation(unittest.TestCase):
    """Test cases for coordinate validation."""

    def test_valid_coordinates(self):
        """Test that valid coordinates are accepted."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        
        # Should not raise any exceptions
        self.assertIsNotNone(coord)

    def test_negative_coordinates(self):
        """Test handling of negative coordinates."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=-50,
            y1=-100,
            x2=50,
            y2=100
        )
        
        # Should still calculate positive width and height
        self.assertGreater(coord.width, 0)
        self.assertGreater(coord.height, 0)

    def test_zero_area_coordinates(self):
        """Test handling of coordinates with zero area."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=100,  # Same as x1
            y2=200   # Same as y1
        )
        
        self.assertEqual(coord.width, 0)
        self.assertEqual(coord.height, 0)
        self.assertEqual(coord.area, 0)


if __name__ == '__main__':
    unittest.main()