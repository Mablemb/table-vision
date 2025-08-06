"""
Test script to verify the coordinate transformation fixes.
Use this to test the coordinate system before running the full app.
"""
import fitz
import camelot
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_coordinate_transformation():
    """Test coordinate transformation between Camelot and PyMuPDF."""
    
    # Test with your PDF
    pdf_path = "test.pdf"
    
    if not os.path.exists(pdf_path):
        print("Please provide a PDF file named 'test.pdf' for testing")
        return
    
    print("=== Testing Coordinate Transformation Fixes ===")
    
    # Open with PyMuPDF to get page dimensions
    doc = fitz.open(pdf_path)
    page = doc[0]
    page_rect = page.rect
    
    print(f"PyMuPDF page dimensions: width={page_rect.width}, height={page_rect.height}")
    
    # Render page at 2x scale (like the app does)
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)
    rendered_width = pix.width
    rendered_height = pix.height
    
    print(f"Rendered dimensions (2x): width={rendered_width}, height={rendered_height}")
    
    # Extract tables with Camelot
    print("\n=== Extracting tables with Camelot ===")
    try:
        tables = camelot.read_pdf(pdf_path, pages='1')
        print(f"Found {len(tables)} tables")
        
        for i, table in enumerate(tables):
            bbox = table._bbox
            print(f"\nTable {i}:")
            print(f"  Camelot bbox: {bbox}")
            print(f"  x1={bbox[0]}, y1={bbox[1]}, x2={bbox[2]}, y2={bbox[3]}")
            print(f"  width={bbox[2]-bbox[0]}, height={bbox[3]-bbox[1]}")
            
            # Test the new coordinate transformation
            print("\n  New coordinate transformation:")
            
            # Simulate the app's transformation
            scale_factor = 1.0  # No additional scaling
            render_scale = 2.0  # PyMuPDF rendering scale
            
            # Convert to screen coordinates (new method)
            screen_x1 = bbox[0] * scale_factor
            screen_x2 = bbox[2] * scale_factor
            
            # Y coordinates with proper handling of PyMuPDF's 2x rendering
            page_height = page_rect.height
            screen_y1 = (page_height * render_scale - bbox[3] * render_scale) / render_scale * scale_factor
            screen_y2 = (page_height * render_scale - bbox[1] * render_scale) / render_scale * scale_factor
            
            print(f"  Screen rect: x1={screen_x1}, y1={screen_y1}, x2={screen_x2}, y2={screen_y2}")
            print(f"  Screen width={screen_x2-screen_x1}, height={screen_y2-screen_y1}")
            
            # Test reverse transformation
            print("\n  Reverse transformation test:")
            pdf_x1 = screen_x1
            pdf_x2 = screen_x2
            pdf_y1 = (page_height * render_scale - screen_y2 * render_scale) / render_scale
            pdf_y2 = (page_height * render_scale - screen_y1 * render_scale) / render_scale
            
            print(f"  Back to PDF: x1={pdf_x1}, y1={pdf_y1}, x2={pdf_x2}, y2={pdf_y2}")
            print(f"  Original:    x1={bbox[0]}, y1={bbox[1]}, x2={bbox[2]}, y2={bbox[3]}")
            
            # Check if transformation is accurate
            tolerance = 0.1
            x1_ok = abs(pdf_x1 - bbox[0]) < tolerance
            y1_ok = abs(pdf_y1 - bbox[1]) < tolerance
            x2_ok = abs(pdf_x2 - bbox[2]) < tolerance
            y2_ok = abs(pdf_y2 - bbox[3]) < tolerance
            
            print(f"  Transformation accuracy: x1={x1_ok}, y1={y1_ok}, x2={x2_ok}, y2={y2_ok}")
            
            if all([x1_ok, y1_ok, x2_ok, y2_ok]):
                print("  ✅ Coordinate transformation is ACCURATE!")
            else:
                print("  ❌ Coordinate transformation has ERRORS!")
    
    except Exception as e:
        print(f"Error extracting tables: {e}")
    
    doc.close()
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_coordinate_transformation()
