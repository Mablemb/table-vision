"""
Sample usage examples for the Table Vision application.
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.extractor import TableExtractor
from core.coordinates import TableCoordinates
from visualization.renderer import TableRenderer
from data.models import PDFDocument, TableExtractionSession
from data.storage import StorageManager


def example_basic_extraction():
    """Basic example of table extraction from a PDF."""
    print("=== Basic Table Extraction Example ===")
    
    # Initialize the extractor
    extractor = TableExtractor()
    
    # Example PDF path (replace with your PDF)
    pdf_path = "example_document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        print("Please place a PDF file named 'example_document.pdf' in this directory.")
        return
    
    try:
        # Extract tables
        print(f"Extracting tables from: {pdf_path}")
        tables = extractor.extract_tables(pdf_path)
        print(f"Found {len(tables)} tables")
        
        # Get coordinates
        coordinates = extractor.get_coordinates()
        
        # Print information about each table
        for i, coord in enumerate(coordinates):
            print(f"Table {i+1}:")
            print(f"  Page: {coord['page']}")
            print(f"  Position: ({coord['x1']:.1f}, {coord['y1']:.1f}) to ({coord['x2']:.1f}, {coord['y2']:.1f})")
            print(f"  Size: {coord['width']:.1f} x {coord['height']:.1f}")
            print(f"  Accuracy: {coord['accuracy']:.1f}%")
            print()
        
        # Clean up
        extractor.close_pdf()
        
    except Exception as e:
        print(f"Error during extraction: {e}")


def example_coordinate_management():
    """Example of coordinate management operations."""
    print("=== Coordinate Management Example ===")
    
    # Initialize coordinate manager
    coord_manager = TableCoordinates()
    
    # Add some example coordinates
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
    
    # Add coordinates
    id1 = coord_manager.add_coordinate(coord1)
    id2 = coord_manager.add_coordinate(coord2)
    
    print(f"Added coordinate 1 with ID: {id1}")
    print(f"Added coordinate 2 with ID: {id2}")
    
    # Retrieve coordinates
    all_coords = coord_manager.get_all_coordinates()
    print(f"Total coordinates: {len(all_coords)}")
    
    # Get coordinates for specific page
    page_coords = coord_manager.get_coordinates_for_page(0)
    print(f"Coordinates on page 0: {len(page_coords)}")
    
    # Update a coordinate
    updates = {'x2': 320, 'width': 220}
    coord_manager.update_coordinate(id1, updates)
    print("Updated coordinate 1")
    
    # Create a user coordinate
    user_id = coord_manager.create_user_coordinate(1, 50, 50, 200, 150)
    print(f"Created user coordinate with ID: {user_id}")
    
    # Remove a coordinate
    coord_manager.remove_coordinate(id2)
    print("Removed coordinate 2")
    
    # Final count
    final_coords = coord_manager.get_all_coordinates()
    print(f"Final coordinate count: {len(final_coords)}")


def example_session_management():
    """Example of session management and storage."""
    print("=== Session Management Example ===")
    
    # Initialize storage manager
    storage = StorageManager()
    
    # Create a sample PDF document
    pdf_doc = PDFDocument(
        file_path="example_document.pdf",
        page_count=5,
        file_size=1024000
    )
    
    # Create a session
    session = TableExtractionSession(pdf_document=pdf_doc)
    
    # Add some sample coordinates to the session
    from data.models import TableCoordinate
    from datetime import datetime
    
    coord1 = TableCoordinate(
        id=1, page=0,
        x1=100, y1=100, x2=300, y2=200,
        user_created=False, accuracy=95.5
    )
    
    coord2 = TableCoordinate(
        id=2, page=1,
        x1=150, y1=150, x2=350, y2=250,
        user_created=True, accuracy=100.0
    )
    
    session.add_coordinate(coord1)
    session.add_coordinate(coord2)
    
    print(f"Created session: {session.session_id}")
    print(f"Session has {len(session.coordinates)} coordinates")
    
    # Save the session
    saved_path = storage.save_session(session)
    if saved_path:
        print(f"Session saved to: {saved_path}")
    
    # List all sessions
    sessions = storage.list_sessions()
    print(f"Total sessions: {len(sessions)}")
    
    for s in sessions:
        print(f"  {s['session_id']}: {s['total_tables']} tables")
    
    # Load the session back
    loaded_session = storage.load_session(session.session_id)
    if loaded_session:
        print(f"Loaded session: {loaded_session.session_id}")
        print(f"Loaded {len(loaded_session.coordinates)} coordinates")
    
    # Get statistics
    stats = session.get_statistics()
    print("\nSession Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def example_image_export():
    """Example of exporting table regions as images."""
    print("=== Image Export Example ===")
    
    pdf_path = "example_document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    try:
        # Initialize renderer
        renderer = TableRenderer()
        
        if not renderer.load_pdf(pdf_path):
            print("Failed to load PDF for rendering")
            return
        
        # Sample coordinates
        coordinates = [
            {
                'id': 1, 'page': 0,
                'x1': 100, 'y1': 100, 'x2': 300, 'y2': 200,
                'user_created': False, 'accuracy': 95.5
            },
            {
                'id': 2, 'page': 0,
                'x1': 350, 'y1': 150, 'x2': 500, 'y2': 250,
                'user_created': True, 'accuracy': 100.0
            }
        ]
        
        # Create export directory
        export_dir = "exported_tables"
        os.makedirs(export_dir, exist_ok=True)
        
        # Export all tables
        exported_files = renderer.export_all_tables(
            coordinates, export_dir, "table", "PNG"
        )
        
        print(f"Exported {len(exported_files)} table images:")
        for file_path in exported_files:
            print(f"  {file_path}")
        
        # Get export statistics
        stats = renderer.get_table_statistics(coordinates)
        print("\nExport Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Clean up
        renderer.close_pdf()
        
    except Exception as e:
        print(f"Error during export: {e}")


def main():
    """Run all examples."""
    print("Table Vision - Sample Usage Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_extraction()
    print()
    
    example_coordinate_management()
    print()
    
    example_session_management()
    print()
    
    example_image_export()
    print()
    
    print("Examples completed!")
    print("\nTo run the full GUI application, use:")
    print("python src/app.py")


if __name__ == "__main__":
    main()