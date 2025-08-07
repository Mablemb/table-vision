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
        Render a specific table region as an image using the same coordinate system as visualization.
        
        Args:
            page_num: Page number (0-based)
            bbox: Bounding box (x1, y1, x2, y2) in PDF coordinates
            dpi: Resolution for rendering (uses default if None)
            
        Returns:
            PIL Image of the table region or None if rendering fails
        """
        if not self.pdf_document:
            print(f"      ERROR: No PDF document loaded")
            return None
        
        if dpi is None:
            dpi = self.export_dpi
        
        try:
            print(f"      Accessing page {page_num} (total pages: {len(self.pdf_document)})")
            
            if page_num >= len(self.pdf_document) or page_num < 0:
                print(f"      ERROR: Invalid page number {page_num}")
                return None
                
            page = self.pdf_document[page_num]
            print(f"      Page dimensions: {page.rect}")
            print(f"      Original bbox: {bbox}")
            
            # Extract coordinates
            x1, y1, x2, y2 = bbox
            
            # Normalize bbox coordinates (ensure x1 < x2, y1 < y2)
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # Use the SAME coordinate system as the working visualization:
            # The visualization treats Camelot coordinates as bottom-origin and flips Y-axis
            # We need to do the same transformation for export to match
            print(f"      Using visualization coordinate system (Y-axis flipping)")
            
            # Apply the same Y-axis flip as the visualization
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Flip Y coordinates: (bottom-origin) -> (top-origin)  
            visual_y1 = page_height - y2  # PDF top becomes visual top
            visual_y2 = page_height - y1  # PDF bottom becomes visual bottom
            
            print(f"      Original PDF coords: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
            print(f"      After Y-flip: x1={x1}, y1={visual_y1}, x2={x2}, y2={visual_y2}")
            
            # Use the flipped coordinates
            x1, y1, x2, y2 = x1, visual_y1, x2, visual_y2
            print(f"      Using visualization coordinate system (Y-axis flipping)")
            
            # Ensure coordinates are within page bounds
            page_width = page.rect.width
            page_height = page.rect.height
            
            x1 = max(0, min(x1, page_width))
            x2 = max(x1, min(x2, page_width))
            y1 = max(0, min(y1, page_height))
            y2 = max(y1, min(y2, page_height))
            
            adjusted_bbox = (x1, y1, x2, y2)
            print(f"      Bounds-checked bbox: {adjusted_bbox}")
            
            # Validate bbox has reasonable dimensions
            width = x2 - x1
            height = y2 - y1
            if width < 10 or height < 10:
                print(f"      ERROR: Bbox too small: {width}x{height}")
                return None
            
            # Use full-page rendering with cropping approach to avoid PyMuPDF clipping issues
            print(f"      Using full-page render + PIL crop approach")
            
            # Create transformation matrix for the desired DPI
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            print(f"      Transformation matrix: {mat} (scale: {dpi/72:.2f})")
            
            # Render full page at desired DPI
            full_pix = page.get_pixmap(matrix=mat)
            print(f"      Full page pixmap: {full_pix.width}x{full_pix.height}")
            
            if full_pix.width == 0 or full_pix.height == 0:
                print(f"      ERROR: Full page pixmap has zero dimensions")
                return None
            
            # Convert to PIL Image
            img_data = full_pix.tobytes("ppm")
            full_img = Image.open(io.BytesIO(img_data))
            print(f"      Full page PIL image: {full_img.size}")
            
            # Calculate crop coordinates in the scaled image space
            scale = dpi / 72
            crop_x1 = int(x1 * scale)
            crop_y1 = int(y1 * scale)  # No Y-axis flipping - top-origin
            crop_x2 = int(x2 * scale)
            crop_y2 = int(y2 * scale)  # No Y-axis flipping - top-origin
            
            print(f"      Scale factor: {scale}")
            print(f"      Before padding - X: {crop_x1} to {crop_x2} (width: {crop_x2-crop_x1})")
            print(f"      Before padding - Y: {crop_y1} to {crop_y2} (height: {crop_y2-crop_y1})")
            
            # Add padding
            padding = max(3, int(dpi / 100))
            crop_x1 = max(0, crop_x1 - padding)
            crop_y1 = max(0, crop_y1 - padding)
            crop_x2 = min(full_img.width, crop_x2 + padding)
            crop_y2 = min(full_img.height, crop_y2 + padding)
            
            print(f"      After padding (+{padding}px) - X: {crop_x1} to {crop_x2} (width: {crop_x2-crop_x1})")
            print(f"      After padding (+{padding}px) - Y: {crop_y1} to {crop_y2} (height: {crop_y2-crop_y1})")
            
            crop_box = (crop_x1, crop_y1, crop_x2, crop_y2)
            print(f"      Crop box (with {padding}px padding): {crop_box}")
            
            # Expected dimensions
            expected_width = crop_x2 - crop_x1
            expected_height = crop_y2 - crop_y1
            print(f"      Expected crop dimensions: {expected_width}x{expected_height}")
            print(f"      Expected aspect ratio: {'landscape' if expected_width > expected_height else 'portrait'}")
            
            # Validate crop box
            if (crop_x2 <= crop_x1 or crop_y2 <= crop_y1 or 
                crop_x1 < 0 or crop_y1 < 0 or
                crop_x2 > full_img.width or crop_y2 > full_img.height):
                print(f"      ERROR: Invalid crop box for image size {full_img.size}")
                return None
            
            # Crop the image
            cropped_img = full_img.crop(crop_box)
            print(f"      Cropped image: {cropped_img.size}")
            print(f"      Actual aspect ratio: {'landscape' if cropped_img.width > cropped_img.height else 'portrait'}")
            
            return cropped_img
            
        except Exception as e:
            print(f"      ERROR: Exception in render_table_region: {e}")
            import traceback
            print(f"      Traceback: {traceback.format_exc()}")
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
        print(f"    Rendering table region: page {page_num}, bbox {bbox}")
        img = self.render_table_region(page_num, bbox, dpi)
        if img is None:
            print(f"    ERROR: Failed to render table region")
            return False
        
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not ensure_directory_exists(output_dir):
                print(f"    ERROR: Failed to create directory {output_dir}")
                return False
            
            # Save the image
            img.save(output_path, format=format, dpi=(dpi or self.export_dpi, dpi or self.export_dpi))
            print(f"    Image saved successfully: {output_path} ({img.size[0]}x{img.size[1]})")
            return True
            
        except Exception as e:
            print(f"    ERROR: Failed to save image: {e}")
            import traceback
            print(f"    Traceback: {traceback.format_exc()}")
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
            print("ERROR: No PDF document loaded for export")
            return []
        
        # Ensure output directory exists
        if not ensure_directory_exists(output_dir):
            print(f"ERROR: Failed to create output directory: {output_dir}")
            return []
        
        print(f"Starting export of {len(coordinates)} tables to {output_dir}")
        exported_files = []
        
        for i, coord in enumerate(coordinates):
            try:
                # Generate filename
                coord_id = coord.get('id', i)
                page_num = coord.get('page', 0)
                user_created = coord.get('user_created', False)
                
                suffix = '_user' if user_created else '_auto'
                filename = f"{filename_prefix}_{coord_id}_page{page_num + 1}{suffix}.{format.lower()}"
                output_path = os.path.join(output_dir, filename)
                
                # Extract bbox
                bbox = (coord['x1'], coord['y1'], coord['x2'], coord['y2'])
                
                print(f"Exporting table {coord_id} from page {page_num + 1} (0-based: {page_num})")
                print(f"  Bbox: {bbox}")
                print(f"  Output: {output_path}")
                
                # Export the table
                if self.export_table_as_image(page_num, bbox, output_path, format):
                    exported_files.append(output_path)
                    print(f"  ✓ Successfully exported: {filename}")
                else:
                    print(f"  ✗ Failed to export table {coord_id}")
                    
            except Exception as e:
                print(f"ERROR: Exception exporting table {coord.get('id', i)}: {e}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
        
        print(f"Export complete. {len(exported_files)} out of {len(coordinates)} tables exported successfully.")
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
