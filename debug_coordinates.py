"""
Debug script to understand coordinate transformation between Camelot and PyMuPDF.
"""
import os
import sys

# Configure Ghostscript BEFORE importing camelot
gs_path = r"C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe"
gs_dir = r"C:\Program Files\gs\gs10.05.1\bin"

print("=== Configuring Ghostscript ===")
print(f"Ghostscript executable: {gs_path}")
print(f"Ghostscript exists: {os.path.exists(gs_path)}")

# Set environment variables before importing camelot
if os.path.exists(gs_path):
    os.environ['GHOSTSCRIPT_BINARY'] = gs_path
    if gs_dir not in os.environ.get('PATH', ''):
        os.environ['PATH'] = os.environ.get('PATH', '') + f';{gs_dir}'
    print(f"Set GHOSTSCRIPT_BINARY to: {gs_path}")
    print(f"Added to PATH: {gs_dir}")
else:
    print("WARNING: Ghostscript not found at expected path!")

import fitz
import camelot

# Test with the specified PDF and page
pdf_path = "Medicina_de_emergencia_abordagem_pratica.pdf"
target_page = 174  # 1-based page number for Camelot

# Check if we have the PDF
if not os.path.exists(pdf_path):
    print(f"Please provide the PDF file '{pdf_path}' for testing")
    print("Make sure the file is in the same directory as this script")
    exit()

print(f"=== Coordinate System Debug (Updated) - Page {target_page} ===")

# Open with PyMuPDF to get page dimensions
doc = fitz.open(pdf_path)

# Check if the page exists
if target_page > len(doc):
    print(f"Error: Page {target_page} does not exist. PDF has {len(doc)} pages.")
    doc.close()
    exit()

page = doc[target_page - 1]  # Convert to 0-based for PyMuPDF
page_rect = page.rect

print(f"PDF: {pdf_path}")
print(f"Testing page: {target_page} (1-based)")
print(f"PyMuPDF page dimensions: width={page_rect.width}, height={page_rect.height}")

# Test with 2x rendering like the app
mat = fitz.Matrix(2, 2)
pix = page.get_pixmap(matrix=mat)
print(f"PyMuPDF rendered at 2x: width={pix.width}, height={pix.height}")

# Extract tables with Camelot
print(f"\n=== Testing Ghostscript configuration ===")
import os
gs_path = r"C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe"
print(f"Ghostscript path exists: {os.path.exists(gs_path)}")
print(f"GHOSTSCRIPT_BINARY env var: {os.environ.get('GHOSTSCRIPT_BINARY', 'Not set')}")
print(f"PATH contains gs dir: {'gs' in os.environ.get('PATH', '').lower()}")

print(f"\n=== Extracting tables with Camelot from page {target_page} ===")
try:
    print(f"Attempting to extract from page {target_page} using Camelot...")
    tables = camelot.read_pdf(pdf_path, pages=str(target_page))
    print(f"Found {len(tables)} tables on page {target_page}")
    
    if len(tables) == 0:
        print("No tables found on this page. Try a different page with tables.")
    
    for i, table in enumerate(tables):
        bbox = table._bbox
        print(f"\nTable {i}:")
        print(f"  Camelot bbox: {bbox}")
        print(f"  x1={bbox[0]}, y1={bbox[1]}, x2={bbox[2]}, y2={bbox[3]}")
        print(f"  width={bbox[2]-bbox[0]}, height={bbox[3]-bbox[1]}")
        print(f"  Accuracy: {table.accuracy}")
        print(f"  Whitespace: {table.whitespace}")
        
        # Test the FIXED coordinate transformation
        print("\n  FIXED Coordinate transformation:")
        print(f"  PDF coordinates: bottom-left=({bbox[0]}, {bbox[1]}), top-right=({bbox[2]}, {bbox[3]})")
        
        # New transformation method (matching the fixed viewer code)
        scale_factor = 1.0
        render_scale = 2.0  # PyMuPDF's 2x rendering
        
        # X coordinates remain the same
        screen_x1 = bbox[0] * scale_factor
        screen_x2 = bbox[2] * scale_factor
        
        # Y coordinates: flip from PDF (bottom-origin) to screen (top-origin)
        # Account for PyMuPDF's 2x rendering scale
        screen_y1 = (page_rect.height * render_scale - bbox[3] * render_scale) / render_scale * scale_factor
        screen_y2 = (page_rect.height * render_scale - bbox[1] * render_scale) / render_scale * scale_factor
        
        print(f"  Screen coordinates: top-left=({screen_x1}, {screen_y1}), bottom-right=({screen_x2}, {screen_y2})")
        print(f"  Screen width={screen_x2-screen_x1}, height={screen_y2-screen_y1}")
        
        # Test reverse transformation
        print(f"\n  Testing reverse transformation:")
        # Convert back from screen to PDF coordinates
        pdf_x1_back = screen_x1
        pdf_x2_back = screen_x2
        pdf_y1_back = (page_rect.height * render_scale - screen_y2 * render_scale) / render_scale
        pdf_y2_back = (page_rect.height * render_scale - screen_y1 * render_scale) / render_scale
        
        print(f"  Back to PDF: x1={pdf_x1_back}, y1={pdf_y1_back}, x2={pdf_x2_back}, y2={pdf_y2_back}")
        print(f"  Original:     x1={bbox[0]}, y1={bbox[1]}, x2={bbox[2]}, y2={bbox[3]}")
        
        # Check accuracy
        tolerance = 0.1
        errors = []
        if abs(pdf_x1_back - bbox[0]) > tolerance:
            errors.append(f"x1 error: {abs(pdf_x1_back - bbox[0])}")
        if abs(pdf_y1_back - bbox[1]) > tolerance:
            errors.append(f"y1 error: {abs(pdf_y1_back - bbox[1])}")
        if abs(pdf_x2_back - bbox[2]) > tolerance:
            errors.append(f"x2 error: {abs(pdf_x2_back - bbox[2])}")
        if abs(pdf_y2_back - bbox[3]) > tolerance:
            errors.append(f"y2 error: {abs(pdf_y2_back - bbox[3])}")
        
        if errors:
            print(f"  ❌ Transformation errors: {', '.join(errors)}")
        else:
            print(f"  ✅ Transformation is accurate!")

except Exception as e:
    print(f"Error extracting tables: {e}")

doc.close()
print(f"\n=== Fixed Coordinate Transformation Test Complete - Page {target_page} ===")
print("\nIf transformations are accurate, the table outlines should now appear correctly in the app!")
