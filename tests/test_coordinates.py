"""
Unit tests for the coordinate management classes.
"""
import unittest
import os
import sys
import tempfile
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.models import TableCoordinate, PDFDocument, TableExtractionSession
from data.storage import StorageManager


class TestTableCoordinate(unittest.TestCase):
    """Test cases for TableCoordinate class."""

    def test_coordinate_creation(self):
        """Test creating a coordinate with valid data."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400,
            accuracy=95.5
        )
        
        self.assertEqual(coord.table_id, 1)
        self.assertEqual(coord.page, 1)
        self.assertEqual(coord.x1, 100)
        self.assertEqual(coord.y1, 200)
        self.assertEqual(coord.x2, 300)
        self.assertEqual(coord.y2, 400)
        self.assertEqual(coord.accuracy, 95.5)

    def test_coordinate_properties(self):
        """Test coordinate calculated properties."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        
        self.assertEqual(coord.width, 200)
        self.assertEqual(coord.height, 200)
        self.assertEqual(coord.area, 40000)

    def test_coordinate_to_dict(self):
        """Test converting coordinate to dictionary."""
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400,
            accuracy=95.5
        )
        
        data = coord.to_dict()
        
        self.assertEqual(data['table_id'], 1)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['x1'], 100)
        self.assertEqual(data['y1'], 200)
        self.assertEqual(data['x2'], 300)
        self.assertEqual(data['y2'], 400)
        self.assertEqual(data['accuracy'], 95.5)

    def test_coordinate_from_dict(self):
        """Test creating coordinate from dictionary."""
        data = {
            'table_id': 1,
            'page': 1,
            'x1': 100,
            'y1': 200,
            'x2': 300,
            'y2': 400,
            'accuracy': 95.5
        }
        
        coord = TableCoordinate.from_dict(data)
        
        self.assertEqual(coord.table_id, 1)
        self.assertEqual(coord.page, 1)
        self.assertEqual(coord.x1, 100)
        self.assertEqual(coord.y1, 200)
        self.assertEqual(coord.x2, 300)
        self.assertEqual(coord.y2, 400)
        self.assertEqual(coord.accuracy, 95.5)


class TestPDFDocument(unittest.TestCase):
    """Test cases for PDFDocument class."""

    def test_pdf_document_creation(self):
        """Test creating a PDF document."""
        doc = PDFDocument(
            file_path="/path/to/document.pdf",
            num_pages=5
        )
        
        self.assertEqual(doc.file_path, "/path/to/document.pdf")
        self.assertEqual(doc.num_pages, 5)
        self.assertIsNotNone(doc.created_at)

    def test_pdf_document_to_dict(self):
        """Test converting PDF document to dictionary."""
        doc = PDFDocument(
            file_path="/path/to/document.pdf",
            num_pages=5
        )
        
        data = doc.to_dict()
        
        self.assertEqual(data['file_path'], "/path/to/document.pdf")
        self.assertEqual(data['num_pages'], 5)
        self.assertIn('created_at', data)

    def test_pdf_document_from_dict(self):
        """Test creating PDF document from dictionary."""
        data = {
            'file_path': "/path/to/document.pdf",
            'num_pages': 5,
            'created_at': '2024-01-01T12:00:00.000000'
        }
        
        doc = PDFDocument.from_dict(data)
        
        self.assertEqual(doc.file_path, "/path/to/document.pdf")
        self.assertEqual(doc.num_pages, 5)


class TestTableExtractionSession(unittest.TestCase):
    """Test cases for TableExtractionSession class."""

    def test_session_creation(self):
        """Test creating an extraction session."""
        session = TableExtractionSession()
        
        self.assertIsNone(session.pdf_document)
        self.assertEqual(len(session.coordinates), 0)
        self.assertIsNotNone(session.created_at)
        self.assertIsNotNone(session.last_modified)

    def test_session_add_coordinate(self):
        """Test adding coordinates to session."""
        session = TableExtractionSession()
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        
        session.add_coordinate(coord)
        
        self.assertEqual(len(session.coordinates), 1)
        self.assertEqual(session.coordinates[0], coord)

    def test_session_remove_coordinate(self):
        """Test removing coordinates from session."""
        session = TableExtractionSession()
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        
        session.add_coordinate(coord)
        session.remove_coordinate(0)
        
        self.assertEqual(len(session.coordinates), 0)


class TestStorageManager(unittest.TestCase):
    """Test cases for StorageManager class."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.storage = StorageManager(base_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load_session(self):
        """Test saving and loading a session."""
        # Create test session
        session = TableExtractionSession()
        session.pdf_document = PDFDocument(
            file_path="/path/to/test.pdf",
            num_pages=3
        )
        
        coord = TableCoordinate(
            table_id=1,
            page=1,
            x1=100,
            y1=200,
            x2=300,
            y2=400
        )
        session.add_coordinate(coord)
        
        # Save session
        session_id = self.storage.save_session(session)
        self.assertIsNotNone(session_id)
        
        # Load session
        loaded_session = self.storage.load_session(session_id)
        self.assertIsNotNone(loaded_session)
        self.assertEqual(loaded_session.pdf_document.file_path, "/path/to/test.pdf")
        self.assertEqual(len(loaded_session.coordinates), 1)

    def test_list_sessions(self):
        """Test listing saved sessions."""
        # Initially should be empty
        sessions = self.storage.list_sessions()
        initial_count = len(sessions)
        
        # Save a session
        session = TableExtractionSession()
        session.pdf_document = PDFDocument(
            file_path="/path/to/test.pdf",
            num_pages=3
        )
        session_id = self.storage.save_session(session)
        
        # Should now have one more session
        sessions = self.storage.list_sessions()
        self.assertEqual(len(sessions), initial_count + 1)
        self.assertIn(session_id, [s['session_id'] for s in sessions])

    def test_delete_session(self):
        """Test deleting a session."""
        # Save a session
        session = TableExtractionSession()
        session_id = self.storage.save_session(session)
        
        # Verify it exists
        self.assertIsNotNone(self.storage.load_session(session_id))
        
        # Delete it
        result = self.storage.delete_session(session_id)
        self.assertTrue(result)
        
        # Verify it's gone
        self.assertIsNone(self.storage.load_session(session_id))


if __name__ == '__main__':
    unittest.main()