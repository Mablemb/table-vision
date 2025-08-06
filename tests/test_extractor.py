"""
Unit tests for the TableExtractor class.
"""
import unittest
import tempfile
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.extractor import TableExtractor


class TestTableExtractor(unittest.TestCase):
    """Test cases for TableExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = TableExtractor()

    def tearDown(self):
        """Clean up after tests."""
        if self.extractor:
            self.extractor.close_pdf()

    def test_extractor_initialization(self):
        """Test that extractor initializes correctly."""
        self.assertIsNotNone(self.extractor)
        self.assertEqual(self.extractor.pdf_document, None)
        self.assertEqual(len(self.extractor.tables), 0)
        self.assertEqual(len(self.extractor.coordinates), 0)

    def test_load_invalid_pdf(self):
        """Test loading an invalid PDF file."""
        result = self.extractor.load_pdf("nonexistent.pdf")
        self.assertFalse(result)

    def test_extract_tables_without_pdf(self):
        """Test extracting tables without loading a PDF."""
        tables = self.extractor.extract_tables("nonexistent.pdf")
        self.assertEqual(len(tables), 0)

    def test_get_coordinates_empty(self):
        """Test getting coordinates when none exist."""
        coordinates = self.extractor.get_coordinates()
        self.assertEqual(len(coordinates), 0)

    def test_get_page_dimensions_without_pdf(self):
        """Test getting page dimensions without a loaded PDF."""
        width, height = self.extractor.get_page_dimensions(0)
        self.assertEqual(width, 0)
        self.assertEqual(height, 0)

    def test_extract_coordinates_empty(self):
        """Test extracting coordinates from empty tables list."""
        coordinates = self.extractor._extract_coordinates([])
        self.assertEqual(len(coordinates), 0)

    # Note: Additional tests would require actual PDF files
    # In a real implementation, you would include sample PDFs for testing


class TestTableExtractorWithMockData(unittest.TestCase):
    """Test cases using mock data."""

    def setUp(self):
        """Set up test fixtures with mock data."""
        self.extractor = TableExtractor()

    def test_extract_coordinates_with_mock_table(self):
        """Test coordinate extraction with mock table data."""
        # Mock table object
        class MockTable:
            def __init__(self, bbox, page, accuracy=95.0, whitespace=0.0):
                self._bbox = bbox
                self.page = page
                self.accuracy = accuracy
                self.whitespace = whitespace

        # Create mock tables
        mock_tables = [
            MockTable((100, 200, 300, 400), 1, 95.5, 0.1),
            MockTable((150, 250, 350, 450), 1, 88.2, 0.2),
        ]

        # Test coordinate extraction
        coordinates = self.extractor._extract_coordinates(mock_tables)
        
        self.assertEqual(len(coordinates), 2)
        
        # Test first coordinate
        coord1 = coordinates[0]
        self.assertEqual(coord1['table_id'], 0)
        self.assertEqual(coord1['page'], 1)
        self.assertEqual(coord1['x1'], 100)
        self.assertEqual(coord1['y1'], 200)
        self.assertEqual(coord1['x2'], 300)
        self.assertEqual(coord1['y2'], 400)
        self.assertEqual(coord1['width'], 200)
        self.assertEqual(coord1['height'], 200)
        self.assertEqual(coord1['accuracy'], 95.5)
        
        # Test second coordinate
        coord2 = coordinates[1]
        self.assertEqual(coord2['table_id'], 1)
        self.assertEqual(coord2['page'], 1)
        self.assertEqual(coord2['accuracy'], 88.2)


if __name__ == '__main__':
    unittest.main()