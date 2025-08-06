"""
Renderer module for exporting table regions as images.
"""
import fitz  # PyMuPDF
from PIL import Image
import io
import os
from typing import List, Dict, Optional, Tuple
from core.utils import extract_table_region, ensure_directory_exists


class TableRenderer:
    """Handles rendering and exporting of table regions as images."""
    
    def __init__(self):
        self.pdf_document = None
        self.export_dpi = 300  # High resolution for table extraction
    
    def load_pdf(self, pdf_path: str) -> bool:
        """Load PDF document for rendering."""
        try:
            self.pdf_document = fitz.open(pdf_path)
            return True
        except Exception as e:
            print(f"Error loading PDF for rendering: {e}")
            return False
    
    def render_table_region(self, page_num: int, bbox: Tuple[float, float, float, float], 
                           dpi: int = None) -> Optional[Image.Image]:
        """
        Render a specific table region as an image.
        
        Args:
            page_num: Page number (0-based)
            bbox: Bounding box (x1, y1, x2, y2) in PDF coordinates
            dpi: Resolution for rendering (uses default if None)
            
        Returns:
            PIL Image of the table region or None if rendering fails
        """
        if not self.pdf_document:
            return None
        
        if dpi is None:
            dpi = self.export_dpi
        
        try:
            page = self.pdf_document[page_num]
            
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
            
            return img
            
        except Exception as e:
            print(f"Error rendering table region: {e}")
            return None
    
    def export_table_as_image(self, page_num: int, bbox: Tuple[float, float, float, float], 
                             output_path: str, format: str = 'PNG', dpi: int = None) -> bool:
        """
        Export a table region as an image file.
        
        Args:
            page_num: Page number (0-based)
            bbox: Bounding box (x1, y1, x2, y2) in PDF coordinates
            output_path: Path to save the image
            format: Image format ('PNG', 'JPEG', etc.)
            dpi: Resolution for export
            
        Returns:
            True if export successful, False otherwise
        """
        img = self.render_table_region(page_num, bbox, dpi)
        if img is None:
            return False
        
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not ensure_directory_exists(output_dir):
                return False
            
            # Save the image
            img.save(output_path, format=format, dpi=(dpi or self.export_dpi, dpi or self.export_dpi))
            return True
            
        except Exception as e:
            print(f"Error saving table image: {e}")
            return False
    
    def export_all_tables(self, coordinates: List[Dict], output_dir: str, 
                         filename_prefix: str = 'table', format: str = 'PNG') -> List[str]:
        """
        Export all table coordinates as separate image files.
        
        Args:
            coordinates: List of coordinate dictionaries
            output_dir: Directory to save images
            filename_prefix: Prefix for filenames
            format: Image format
            
        Returns:
            List of successfully exported file paths
        """
        if not self.pdf_document:
            return []
        
        # Ensure output directory exists
        if not ensure_directory_exists(output_dir):
            return []
        
        exported_files = []
        
        for i, coord in enumerate(coordinates):
            try:
                # Generate filename
                coord_id = coord.get('id', i)
                page_num = coord.get('page', 0)
                user_created = coord.get('user_created', False)
                
                suffix = '_user' if user_created else '_auto'
                filename = f"{filename_prefix}_{coord_id}_page{page_num}{suffix}.{format.lower()}"
                output_path = os.path.join(output_dir, filename)
                
                # Extract bbox
                bbox = (coord['x1'], coord['y1'], coord['x2'], coord['y2'])
                
                # Export the table
                if self.export_table_as_image(page_num, bbox, output_path, format):
                    exported_files.append(output_path)
                    print(f"Exported: {output_path}")
                else:
                    print(f"Failed to export table {coord_id}")
                    
            except Exception as e:
                print(f"Error exporting table {coord.get('id', i)}: {e}")
        
        return exported_files
    
    def export_tables_by_page(self, coordinates: List[Dict], output_dir: str, 
                             format: str = 'PNG') -> Dict[int, List[str]]:
        """
        Export tables organized by page.
        
        Args:
            coordinates: List of coordinate dictionaries
            output_dir: Base directory to save images
            format: Image format
            
        Returns:
            Dictionary mapping page numbers to lists of exported file paths
        """
        if not self.pdf_document:
            return {}
        
        # Group coordinates by page
        pages = {}
        for coord in coordinates:
            page_num = coord.get('page', 0)
            if page_num not in pages:
                pages[page_num] = []
            pages[page_num].append(coord)
        
        exported_by_page = {}
        
        for page_num, page_coords in pages.items():
            # Create page-specific directory
            page_dir = os.path.join(output_dir, f"page_{page_num}")
            if not ensure_directory_exists(page_dir):
                continue
            
            # Export tables for this page
            exported_files = self.export_all_tables(
                page_coords, page_dir, f"p{page_num}_table", format
            )
            
            exported_by_page[page_num] = exported_files
        
        return exported_by_page
    
    def create_table_preview(self, coordinates: List[Dict], max_width: int = 800) -> Optional[Image.Image]:
        """
        Create a preview image showing all tables on a page.
        
        Args:
            coordinates: List of coordinate dictionaries for a single page
            max_width: Maximum width for the preview image
            
        Returns:
            PIL Image showing all tables or None if creation fails
        """
        if not coordinates or not self.pdf_document:
            return None
        
        try:
            # Get page number from first coordinate
            page_num = coordinates[0].get('page', 0)
            page = self.pdf_document[page_num]
            
            # Calculate scale to fit max_width
            page_width = page.rect.width
            scale = min(max_width / page_width, 1.0)
            
            # Render full page
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            base_img = Image.open(io.BytesIO(img_data))
            
            # Overlay table regions (this would require additional drawing logic)
            # For now, just return the base image
            return base_img
            
        except Exception as e:
            print(f"Error creating table preview: {e}")
            return None
    
    def get_table_statistics(self, coordinates: List[Dict]) -> Dict:
        """
        Get statistics about the tables to be exported.
        
        Args:
            coordinates: List of coordinate dictionaries
            
        Returns:
            Dictionary containing statistics
        """
        if not coordinates:
            return {
                'total_tables': 0,
                'pages': 0,
                'user_created': 0,
                'auto_detected': 0,
                'avg_accuracy': 0,
                'total_area': 0
            }
        
        pages = set()
        user_created = 0
        auto_detected = 0
        accuracies = []
        total_area = 0
        
        for coord in coordinates:
            pages.add(coord.get('page', 0))
            
            if coord.get('user_created', False):
                user_created += 1
            else:
                auto_detected += 1
                accuracies.append(coord.get('accuracy', 0))
            
            # Calculate area
            width = coord.get('width', coord['x2'] - coord['x1'])
            height = coord.get('height', coord['y2'] - coord['y1'])
            total_area += width * height
        
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        
        return {
            'total_tables': len(coordinates),
            'pages': len(pages),
            'user_created': user_created,
            'auto_detected': auto_detected,
            'avg_accuracy': avg_accuracy,
            'total_area': total_area
        }
    
    def close_pdf(self):
        """Close the PDF document."""
        if self.pdf_document:
            self.pdf_document.close()
            self.pdf_document = None
