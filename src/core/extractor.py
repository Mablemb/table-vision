"""
Table extraction module using Camelot library for PDF table detection.
"""
import os
import sys

# Configure Ghostscript path for Camelot BEFORE importing camelot
gs_path = r"C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe"
gs_dir = r"C:\Program Files\gs\gs10.05.1\bin"

# Debug flag - set to False for production
DEBUG_GHOSTSCRIPT = False

if DEBUG_GHOSTSCRIPT:
    print(f"DEBUG: Checking Ghostscript at {gs_path}")
    print(f"DEBUG: Ghostscript exists: {os.path.exists(gs_path)}")

if os.path.exists(gs_path):
    # Set environment variables before importing camelot
    os.environ['GHOSTSCRIPT_BINARY'] = gs_path
    if gs_dir not in os.environ.get('PATH', ''):
        os.environ['PATH'] = os.environ.get('PATH', '') + f';{gs_dir}'
        if DEBUG_GHOSTSCRIPT:
            print(f"DEBUG: Added {gs_dir} to PATH")
    if DEBUG_GHOSTSCRIPT:
        print(f"DEBUG: Set GHOSTSCRIPT_BINARY to {gs_path}")
else:
    if DEBUG_GHOSTSCRIPT:
        print(f"DEBUG: Ghostscript not found at {gs_path}")
    # Try to find it in other common locations
    possible_paths = [
        r"C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe",
        r"C:\Program Files (x86)\gs\gs10.05.1\bin\gswin64c.exe",
        r"C:\gs\gs10.05.1\bin\gswin64c.exe",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            gs_path = path
            gs_dir = os.path.dirname(path)
            os.environ['GHOSTSCRIPT_BINARY'] = gs_path
            os.environ['PATH'] = os.environ.get('PATH', '') + f';{gs_dir}'
            if DEBUG_GHOSTSCRIPT:
                print(f"DEBUG: Found Ghostscript at {path}")
            break

import camelot
import fitz  # PyMuPDF
from typing import List, Dict, Tuple, Optional, Callable
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QThread


class BatchExtractionWorker(QThread):
    """Worker thread for batch table extraction."""
    
    # Signals
    page_completed = pyqtSignal(int, list)  # page_number, coordinates
    batch_completed = pyqtSignal(list)  # all_coordinates
    progress_updated = pyqtSignal(int, int)  # current_page, total_pages
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, pdf_path: str, batch_size: int = 3):
        super().__init__()
        self.pdf_path = pdf_path
        self.batch_size = batch_size
        self.should_stop = False
        self.all_coordinates = []
        
    def run(self):
        """Run batch extraction process."""
        try:
            # Get total page count
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            doc.close()
            
            current_page = 1
            
            while current_page <= total_pages and not self.should_stop:
                # Calculate batch end page
                batch_end = min(current_page + self.batch_size - 1, total_pages)
                pages_range = f"{current_page}-{batch_end}" if batch_end > current_page else str(current_page)
                
                try:
                    # Extract tables for this batch
                    tables = camelot.read_pdf(
                        self.pdf_path,
                        pages=pages_range,
                        flavor='lattice',
                        strip_text='\n'
                    )
                    
                    # Process each page in the batch
                    for page_num in range(current_page, batch_end + 1):
                        if self.should_stop:
                            break
                            
                        page_tables = [t for t in tables if t.page == page_num]
                        page_coordinates = self._extract_coordinates_for_page(page_tables, page_num)
                        
                        self.all_coordinates.extend(page_coordinates)
                        self.page_completed.emit(page_num, page_coordinates)
                        self.progress_updated.emit(page_num, total_pages)
                    
                except Exception as e:
                    self.error_occurred.emit(f"Error processing pages {pages_range}: {str(e)}")
                
                current_page = batch_end + 1
            
            if not self.should_stop:
                self.batch_completed.emit(self.all_coordinates)
                
        except Exception as e:
            self.error_occurred.emit(f"Batch extraction error: {str(e)}")
    
    def stop(self):
        """Stop the extraction process."""
        self.should_stop = True
    
    def _extract_coordinates_for_page(self, tables: List, page_num: int) -> List[Dict]:
        """Extract coordinates from tables for a specific page."""
        coordinates = []
        
        # Initialize global ID counter if not exists
        if not hasattr(self, '_global_id_counter'):
            self._global_id_counter = 1000  # Start with high number to avoid conflicts with user IDs
        
        for i, table in enumerate(tables):
            try:
                bbox = table._bbox
                
                coordinate = {
                    'id': self._global_id_counter,
                    'page': page_num - 1,  # Convert to 0-based indexing
                    'x1': float(bbox[0]),
                    'y1': float(bbox[1]),
                    'x2': float(bbox[2]),
                    'y2': float(bbox[3]),
                    'width': float(bbox[2] - bbox[0]),
                    'height': float(bbox[3] - bbox[1]),
                    'accuracy': getattr(table, 'accuracy', 0.0),
                    'whitespace': getattr(table, 'whitespace', 0.0),
                    'user_created': False
                }
                
                # DEBUG: Print Camelot coordinates (disabled for cleaner output)
                debug_extraction = False  # Set to True for debugging extraction issues
                if debug_extraction:
                    print(f"DEBUG - Camelot detected table on page {page_num} (0-based: {page_num-1}):")
                    print(f"  ID: {self._global_id_counter}")
                    print(f"  Bbox: {bbox}")
                    print(f"  Final coordinate: {coordinate}")
                
                coordinates.append(coordinate)
                self._global_id_counter += 1
                
            except Exception as e:
                print(f"Error extracting coordinate from table {i} on page {page_num}: {e}")
        
        return coordinates


class TableExtractor:
    """Handles table extraction from PDF files using Camelot lattice method."""
    
    def __init__(self):
        self.pdf_document = None
        self.tables = []
        self.coordinates = []
        self.batch_worker: Optional[BatchExtractionWorker] = None
    
    def load_pdf(self, pdf_path: str) -> bool:
        """Load PDF document for processing."""
        try:
            self.pdf_document = fitz.open(pdf_path)
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    
    def start_batch_extraction(self, pdf_path: str, batch_size: int = 3) -> BatchExtractionWorker:
        """
        Start batch extraction process.
        
        Args:
            pdf_path: Path to the PDF file
            batch_size: Number of pages to process in each batch
            
        Returns:
            BatchExtractionWorker instance for connecting signals
        """
        if self.batch_worker and self.batch_worker.isRunning():
            self.batch_worker.stop()
            self.batch_worker.wait()
        
        self.batch_worker = BatchExtractionWorker(pdf_path, batch_size)
        return self.batch_worker
    
    def stop_extraction(self):
        """Stop any running extraction process."""
        if self.batch_worker and self.batch_worker.isRunning():
            self.batch_worker.stop()
            self.batch_worker.wait()
    
    def extract_tables(self, pdf_path: str, pages: str = 'all') -> List:
        """
        Extract tables from PDF using Camelot lattice method.
        
        Args:
            pdf_path: Path to the PDF file
            pages: Pages to process ('all' or specific pages like '1,2,3')
            
        Returns:
            List of detected tables with their properties
        """
        try:
            # Use lattice method for table detection
            tables = camelot.read_pdf(
                pdf_path, 
                pages=pages, 
                flavor='lattice',
                strip_text='\n'
            )
            
            self.tables = tables
            self.coordinates = self._extract_coordinates(tables)
            
            return tables
            
        except Exception as e:
            print(f"Error extracting tables: {e}")
            return []
    
    def _extract_coordinates(self, tables) -> List[Dict]:
        """Extract coordinate information from detected tables."""
        coordinates = []
        
        # Use a counter that continues across all extractions to ensure unique IDs
        if not hasattr(self, '_global_table_id'):
            self._global_table_id = 0
        
        for i, table in enumerate(tables):
            # Get the bounding box coordinates
            bbox = table._bbox
            
            coord_dict = {
                'id': self._global_table_id,  # Use global ID for uniqueness
                'table_id': i,  # Keep original table index for reference
                'page': table.page - 1,  # Convert from 1-based to 0-based page numbering
                'x1': bbox[0],  # left
                'y1': bbox[1],  # bottom
                'x2': bbox[2],  # right
                'y2': bbox[3],  # top
                'width': bbox[2] - bbox[0],
                'height': bbox[3] - bbox[1],
                'accuracy': table.accuracy,
                'whitespace': table.whitespace,
                'user_created': False  # Mark as Camelot-detected
            }
            
            coordinates.append(coord_dict)
            self._global_table_id += 1
        
        return coordinates
    
    def get_coordinates(self) -> List[Dict]:
        """Return the extracted coordinates."""
        return self.coordinates
    
    def get_page_dimensions(self, page_num: int) -> Tuple[float, float]:
        """Get dimensions of a specific page."""
        if self.pdf_document and page_num < len(self.pdf_document):
            page = self.pdf_document[page_num]
            rect = page.rect
            return rect.width, rect.height
        return 0, 0
    
    def visualize_tables(self, pdf_path: str, page_num: int = 0):
        """
        Visualize tables on a specific page using Camelot's plot method.
        This creates a plot showing the detected table areas.
        """
        try:
            # Extract tables for the specific page
            tables = camelot.read_pdf(
                pdf_path, 
                pages=str(page_num + 1),  # Camelot uses 1-based indexing
                flavor='lattice'
            )
            
            if tables:
                # Use Camelot's built-in visualization
                camelot.plot(tables[0], kind='contour')
                return True
            
        except Exception as e:
            print(f"Error visualizing tables: {e}")
            
        return False
    
    def close_pdf(self):
        """Close the PDF document."""
        if self.pdf_document:
            self.pdf_document.close()
