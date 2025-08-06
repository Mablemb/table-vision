"""
Utility functions for PDF handling and validation.
"""
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
from typing import Tuple, Optional
import os
import io


def validate_pdf_path(pdf_path: str) -> bool:
    """Validate if the PDF path exists and is a valid PDF file."""
    if not os.path.exists(pdf_path):
        return False
    
    try:
        doc = fitz.open(pdf_path)
        doc.close()
        return True
    except:
        return False


def get_pdf_page_count(pdf_path: str) -> int:
    """Get the number of pages in a PDF."""
    try:
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
        return page_count
    except:
        return 0


def pdf_page_to_image(pdf_path: str, page_num: int, dpi: int = 150) -> Optional[Image.Image]:
    """
    Convert a PDF page to PIL Image.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (0-based)
        dpi: Resolution for the conversion
        
    Returns:
        PIL Image or None if conversion fails
    """
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        # Create transformation matrix for the desired DPI
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        
        # Render page to pixmap
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        doc.close()
        return img
        
    except Exception as e:
        print(f"Error converting PDF page to image: {e}")
        return None


def extract_table_region(pdf_path: str, page_num: int, bbox: Tuple[float, float, float, float], 
                         dpi: int = 300) -> Optional[Image.Image]:
    """
    Extract a specific region from a PDF page as an image.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (0-based)
        bbox: Bounding box (x1, y1, x2, y2) in PDF coordinates
        dpi: Resolution for the extraction
        
    Returns:
        PIL Image of the extracted region or None if extraction fails
    """
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        # Create transformation matrix for the desired DPI
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        
        # Convert bbox to the new coordinate system
        rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
        rect = rect * mat
        
        # Render the specific region
        pix = page.get_pixmap(matrix=mat, clip=rect)
        
        # Convert to PIL Image
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        doc.close()
        return img
        
    except Exception as e:
        print(f"Error extracting table region: {e}")
        return None


def get_page_dimensions(pdf_path: str, page_num: int) -> Tuple[float, float]:
    """Get the dimensions of a PDF page."""
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        rect = page.rect
        doc.close()
        return rect.width, rect.height
    except:
        return 0, 0


def normalize_coordinates(bbox: Tuple[float, float, float, float], 
                         page_width: float, page_height: float) -> Tuple[float, float, float, float]:
    """
    Normalize coordinates to 0-1 range based on page dimensions.
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
        page_width: Width of the page
        page_height: Height of the page
        
    Returns:
        Normalized bounding box
    """
    if page_width == 0 or page_height == 0:
        return bbox
    
    return (
        bbox[0] / page_width,
        bbox[1] / page_height,
        bbox[2] / page_width,
        bbox[3] / page_height
    )


def denormalize_coordinates(normalized_bbox: Tuple[float, float, float, float], 
                           page_width: float, page_height: float) -> Tuple[float, float, float, float]:
    """
    Convert normalized coordinates back to absolute coordinates.
    
    Args:
        normalized_bbox: Normalized bounding box (0-1 range)
        page_width: Width of the page
        page_height: Height of the page
        
    Returns:
        Absolute bounding box
    """
    return (
        normalized_bbox[0] * page_width,
        normalized_bbox[1] * page_height,
        normalized_bbox[2] * page_width,
        normalized_bbox[3] * page_height
    )


def convert_camelot_to_fitz_coords(camelot_bbox: Tuple[float, float, float, float], 
                                  page_height: float) -> Tuple[float, float, float, float]:
    """
    Convert Camelot coordinates (bottom-left origin) to PyMuPDF coordinates (top-left origin).
    
    Args:
        camelot_bbox: Camelot bounding box (x1, y1, x2, y2) with bottom-left origin
        page_height: Height of the page
        
    Returns:
        PyMuPDF bounding box (x1, y1, x2, y2) with top-left origin
    """
    x1, y1, x2, y2 = camelot_bbox
    
    # Convert y-coordinates
    new_y1 = page_height - y2  # top becomes page_height - bottom
    new_y2 = page_height - y1  # bottom becomes page_height - top
    
    return (x1, new_y1, x2, new_y2)


def ensure_directory_exists(directory_path: str) -> bool:
    """Ensure that a directory exists, create if it doesn't."""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except:
        return False
