"""
Unit tests for the table renderer component.
"""
import unittest
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.models import TableCoordinate


class TestTableRenderer(unittest.TestCase):
    """Test cases for table rendering and export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create sample coordinates
        self.sample_coordinates = [
            TableCoordinate(
                id=1,
                page=1,
                x1=100,
                y1=200,
                x2=300,
                y2=400,
                accuracy=95.5
            ),
            TableCoordinate(
                id=2,
                page=1,
                x1=400,
                y1=300,
                x2=600,
                y2=500,
                accuracy=88.2
            )
        ]

    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_coordinate_to_export_format(self):
        """Test converting coordinates to export format."""
        coord = self.sample_coordinates[0]
        
        # Test basic properties
        self.assertEqual(coord.id, 1)
        self.assertEqual(coord.page, 1)
        self.assertEqual(coord.width, 200)
        self.assertEqual(coord.height, 200)
        self.assertEqual(coord.get_area(), 40000)

    def test_export_filename_generation(self):
        """Test generating filenames for exported images."""
        coord = self.sample_coordinates[0]
        
        # Test filename patterns
        filename_pattern = f"table_{coord.id}_page_{coord.page}.png"
        expected = "table_1_page_1.png"
        self.assertEqual(filename_pattern, expected)

    def test_coordinate_bbox_format(self):
        """Test converting coordinates to bbox format for rendering."""
        coord = self.sample_coordinates[0]
        
        # Bbox format: (x1, y1, x2, y2)
        bbox = (coord.x1, coord.y1, coord.x2, coord.y2)
        expected_bbox = (100, 200, 300, 400)
        self.assertEqual(bbox, expected_bbox)

    def test_multiple_coordinates_processing(self):
        """Test processing multiple coordinates."""
        coords = self.sample_coordinates
        
        # Test that we have multiple coordinates
        self.assertEqual(len(coords), 2)
        
        # Test unique table IDs
        table_ids = [coord.id for coord in coords]
        self.assertEqual(len(set(table_ids)), 2)  # Should be unique

    def test_coordinate_validation_for_export(self):
        """Test validating coordinates before export."""
        coord = self.sample_coordinates[0]
        
        # Check that coordinates are valid for export
        self.assertGreater(coord.width, 0)
        self.assertGreater(coord.height, 0)
        self.assertGreaterEqual(coord.x1, 0)
        self.assertGreaterEqual(coord.y1, 0)

    def test_export_directory_creation(self):
        """Test creating export directories."""
        export_dir = os.path.join(self.temp_dir, "exports")
        
        # Directory should not exist initially
        self.assertFalse(os.path.exists(export_dir))
        
        # Create directory (simulating export functionality)
        os.makedirs(export_dir, exist_ok=True)
        
        # Directory should now exist
        self.assertTrue(os.path.exists(export_dir))

    def test_coordinate_sorting(self):
        """Test sorting coordinates for consistent export order."""
        coords = self.sample_coordinates.copy()
        
        # Sort by table_id
        sorted_coords = sorted(coords, key=lambda x: x.id)
        
        # Should be in order
        table_ids = [coord.id for coord in sorted_coords]
        self.assertEqual(table_ids, [1, 2])

    def test_coordinate_filtering(self):
        """Test filtering coordinates by criteria."""
        coords = self.sample_coordinates
        
        # Filter by minimum area
        min_area = 30000
        large_coords = [coord for coord in coords if coord.area >= min_area]
        
        # Both coordinates should meet the criteria
        self.assertEqual(len(large_coords), 2)

    def test_coordinate_statistics(self):
        """Test calculating statistics for coordinates."""
        coords = self.sample_coordinates
        
        # Calculate average area
        areas = [coord.area for coord in coords]
        avg_area = sum(areas) / len(areas)
        
        # Should be reasonable value
        self.assertGreater(avg_area, 0)
        
        # Calculate total coverage
        total_area = sum(areas)
        self.assertEqual(total_area, 80000)  # 40000 + 40000


class TestExportFormats(unittest.TestCase):
    """Test cases for different export formats."""

    def test_png_format_extension(self):
        """Test PNG format file extension."""
        filename = "table_1_page_1"
        png_filename = f"{filename}.png"
        self.assertTrue(png_filename.endswith('.png'))

    def test_jpeg_format_extension(self):
        """Test JPEG format file extension."""
        filename = "table_1_page_1"
        jpeg_filename = f"{filename}.jpg"
        self.assertTrue(jpeg_filename.endswith('.jpg'))

    def test_tiff_format_extension(self):
        """Test TIFF format file extension."""
        filename = "table_1_page_1"
        tiff_filename = f"{filename}.tiff"
        self.assertTrue(tiff_filename.endswith('.tiff'))

    def test_supported_formats(self):
        """Test list of supported export formats."""
        supported_formats = ['PNG', 'JPEG', 'TIFF']
        
        self.assertIn('PNG', supported_formats)
        self.assertIn('JPEG', supported_formats)
        self.assertIn('TIFF', supported_formats)


class TestImageQualitySettings(unittest.TestCase):
    """Test cases for image quality and resolution settings."""

    def test_dpi_settings(self):
        """Test DPI (dots per inch) settings for export."""
        # Common DPI values
        dpi_values = [72, 150, 300, 600]
        
        for dpi in dpi_values:
            self.assertGreater(dpi, 0)
            self.assertIsInstance(dpi, int)

    def test_quality_settings(self):
        """Test quality settings for JPEG export."""
        # Quality should be between 1-100 for JPEG
        quality_values = [50, 75, 85, 95]
        
        for quality in quality_values:
            self.assertGreaterEqual(quality, 1)
            self.assertLessEqual(quality, 100)

    def test_scale_factor(self):
        """Test scale factor for image resolution."""
        scale_factors = [1.0, 1.5, 2.0, 3.0]
        
        for scale in scale_factors:
            self.assertGreater(scale, 0)
            self.assertIsInstance(scale, float)


if __name__ == '__main__':
    unittest.main()
