"""
Main application window for Table Vision.
"""
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QFileDialog, QMessageBox,
                           QSplitter, QMenuBar, QMenu, QAction, QStatusBar,
                           QProgressBar, QLabel, QToolBar, QSpinBox, QLineEdit,
                           QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QKeySequence
import sys
import os
from typing import Optional

# Import our modules
from core.extractor import TableExtractor, BatchExtractionWorker
from core.coordinates import TableCoordinates
from core.utils import validate_pdf_path, get_pdf_page_count
from visualization.viewer import TableViewer
from visualization.editor import TableEditor
from visualization.renderer import TableRenderer
from data.models import PDFDocument, TableExtractionSession
from data.storage import StorageManager


class ExtractionWorker(QThread):
    """Worker thread for table extraction to prevent UI freezing."""
    
    finished = pyqtSignal(list)  # Emitted when extraction is complete
    progress = pyqtSignal(str)   # Emitted to update progress text
    error = pyqtSignal(str)      # Emitted when an error occurs
    
    def __init__(self, pdf_path: str, pages: str = 'all'):
        super().__init__()
        self.pdf_path = pdf_path
        self.pages = pages
    
    def run(self):
        """Run the extraction in a separate thread."""
        try:
            self.progress.emit("Initializing table extractor...")
            extractor = TableExtractor()
            
            self.progress.emit("Loading PDF document...")
            if not extractor.load_pdf(self.pdf_path):
                self.error.emit("Failed to load PDF document")
                return
            
            self.progress.emit("Extracting tables with Camelot...")
            tables = extractor.extract_tables(self.pdf_path, self.pages)
            
            self.progress.emit("Processing coordinates...")
            coordinates = extractor.get_coordinates()
            
            self.progress.emit("Extraction complete!")
            self.finished.emit(coordinates)
            
        except Exception as e:
            self.error.emit(f"Extraction error: {str(e)}")


class BatchExtractionWorkerCustom(QThread):
    """Custom batch extraction worker that supports page ranges."""
    
    # Signals
    page_completed = pyqtSignal(int, list)  # page_number, coordinates
    batch_completed = pyqtSignal(list)  # all_coordinates
    progress_updated = pyqtSignal(int, int)  # current_page, total_pages
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, pdf_path: str, batch_size: int = 3, start_page: int = 1, end_page: int = None):
        super().__init__()
        self.pdf_path = pdf_path
        self.batch_size = batch_size
        self.start_page = start_page
        self.end_page = end_page
        self.should_stop = False
        self.all_coordinates = []
        
    def run(self):
        """Run batch extraction process for specified page range."""
        try:
            # Get total page count
            import fitz
            doc = fitz.open(self.pdf_path)
            total_pages = len(doc)
            doc.close()
            
            # Validate and set page range
            if self.end_page is None or self.end_page > total_pages:
                self.end_page = total_pages
            
            if self.start_page < 1:
                self.start_page = 1
                
            if self.start_page > self.end_page:
                self.error_occurred.emit(f"Invalid page range: start page ({self.start_page}) is greater than end page ({self.end_page})")
                return
            
            current_page = self.start_page
            pages_to_process = self.end_page - self.start_page + 1
            
            while current_page <= self.end_page and not self.should_stop:
                # Calculate batch end page
                batch_end = min(current_page + self.batch_size - 1, self.end_page)
                pages_range = f"{current_page}-{batch_end}" if batch_end > current_page else str(current_page)
                
                try:
                    import camelot
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
                        
                        # Calculate progress based on selected range
                        processed_pages = page_num - self.start_page + 1
                        self.progress_updated.emit(processed_pages, pages_to_process)
                    
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
    
    def _extract_coordinates_for_page(self, tables: list, page_num: int) -> list:
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
                
                coordinates.append(coordinate)
                self._global_id_counter += 1
                
            except Exception as e:
                print(f"Error extracting coordinate from table {i} on page {page_num}: {e}")
        
        return coordinates


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table Vision - PDF Table Extraction Tool")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize components
        self.extractor = TableExtractor()
        self.coordinates_manager = TableCoordinates()
        self.renderer = TableRenderer()
        self.storage_manager = StorageManager()
        
        # State variables
        self.current_pdf_path: Optional[str] = None
        self.current_session: Optional[TableExtractionSession] = None
        self.extraction_worker: Optional[ExtractionWorker] = None
        self.batch_worker: Optional[BatchExtractionWorker] = None
        self.custom_batch_worker: Optional[BatchExtractionWorkerCustom] = None
        self.all_extracted_coordinates = []  # Store all coordinates as they're extracted
        self.total_pages = 0  # Store total pages in current PDF
        
        # UI Components
        self.viewer = None
        self.editor = None
        
        self.setup_ui()
        self.connect_signals()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Create viewer and editor
        self.viewer = TableViewer()
        self.editor = TableEditor()
        
        # Add to splitter
        splitter.addWidget(self.viewer)
        splitter.addWidget(self.editor)
        
        # Set splitter proportions (viewer gets more space)
        splitter.setSizes([1000, 400])
        
        main_layout.addWidget(splitter)
        
        # Create status bar
        self.create_status_bar()
        
        # Initial state
        self.update_ui_state()
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open PDF...', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_pdf)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_session_action = QAction('Save Session...', self)
        save_session_action.setShortcut(QKeySequence.Save)
        save_session_action.triggered.connect(self.save_session)
        file_menu.addAction(save_session_action)
        
        load_session_action = QAction('Load Session...', self)
        load_session_action.triggered.connect(self.load_session)
        file_menu.addAction(load_session_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Extract menu
        extract_menu = menubar.addMenu('Extract')
        
        extract_range_action = QAction('Extract Selected Range', self)
        extract_range_action.triggered.connect(self.extract_tables_with_range)
        extract_menu.addAction(extract_range_action)
        
        extract_all_action = QAction('Extract All Pages', self)
        extract_all_action.triggered.connect(self.extract_all_pages_batch)
        extract_menu.addAction(extract_all_action)
        
        extract_current_action = QAction('Extract Current Page', self)
        extract_current_action.triggered.connect(self.extract_current_page)
        extract_menu.addAction(extract_current_action)
        
        # Export menu
        export_menu = menubar.addMenu('Export')
        
        export_images_action = QAction('Export Table Images...', self)
        export_images_action.triggered.connect(self.export_table_images)
        export_menu.addAction(export_images_action)
        
        export_coords_action = QAction('Export Coordinates...', self)
        export_coords_action.triggered.connect(self.export_coordinates)
        export_menu.addAction(export_coords_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the application toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Open PDF
        open_button = QPushButton("Open PDF")
        open_button.clicked.connect(self.open_pdf)
        toolbar.addWidget(open_button)
        
        toolbar.addSeparator()
        
        # Page Range Selection Group
        page_range_group = QGroupBox("Page Range")
        page_range_layout = QHBoxLayout()
        
        # All pages checkbox
        self.all_pages_checkbox = QCheckBox("All Pages")
        self.all_pages_checkbox.setChecked(True)
        self.all_pages_checkbox.toggled.connect(self.on_all_pages_toggled)
        page_range_layout.addWidget(self.all_pages_checkbox)
        
        # Start page
        page_range_layout.addWidget(QLabel("From:"))
        self.start_page_input = QSpinBox()
        self.start_page_input.setMinimum(1)
        self.start_page_input.setMaximum(9999)
        self.start_page_input.setValue(1)
        self.start_page_input.setEnabled(False)
        page_range_layout.addWidget(self.start_page_input)
        
        # End page
        page_range_layout.addWidget(QLabel("To:"))
        self.end_page_input = QSpinBox()
        self.end_page_input.setMinimum(1)
        self.end_page_input.setMaximum(9999)
        self.end_page_input.setValue(1)
        self.end_page_input.setEnabled(False)
        page_range_layout.addWidget(self.end_page_input)
        
        page_range_group.setLayout(page_range_layout)
        toolbar.addWidget(page_range_group)
        
        toolbar.addSeparator()
        
        # Extract tables with batch processing
        self.extract_button = QPushButton("Extract Tables")
        self.extract_button.clicked.connect(self.extract_tables_with_range)
        self.extract_button.setEnabled(False)
        toolbar.addWidget(self.extract_button)
        
        # Batch size control
        toolbar.addWidget(QLabel("Batch Size:"))
        self.batch_size_spinbox = QSpinBox()
        self.batch_size_spinbox.setMinimum(1)
        self.batch_size_spinbox.setMaximum(10)
        self.batch_size_spinbox.setValue(3)
        self.batch_size_spinbox.setToolTip("Number of pages to process in each batch")
        toolbar.addWidget(self.batch_size_spinbox)
        
        # Stop extraction button
        self.stop_button = QPushButton("Stop Extraction")
        self.stop_button.clicked.connect(self.stop_extraction)
        self.stop_button.setVisible(False)
        toolbar.addWidget(self.stop_button)
        
        toolbar.addSeparator()
        
        # Export images
        self.export_button = QPushButton("Export Images")
        self.export_button.clicked.connect(self.export_table_images)
        self.export_button.setEnabled(False)
        toolbar.addWidget(self.export_button)
    
    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # Status labels
        self.pdf_status_label = QLabel("No PDF loaded")
        self.tables_status_label = QLabel("Tables: 0")
        
        self.status_bar.addWidget(self.pdf_status_label)
        self.status_bar.addPermanentWidget(self.tables_status_label)
    
    def connect_signals(self):
        """Connect signals between components."""
        if self.viewer and self.editor:
            # Connect viewer signals to editor
            self.viewer.pdf_label.rectangle_selected.connect(self.editor.select_coordinate)
            self.viewer.pdf_label.new_rectangle_created.connect(self.create_user_coordinate)
            self.viewer.pdf_label.rectangle_deleted.connect(self.delete_coordinate)
            self.viewer.pdf_label.rectangle_moved.connect(self.on_rectangle_moved)
            
            # Connect editor signals to coordinate manager
            self.editor.coordinate_updated.connect(self.update_coordinate)
            self.editor.coordinate_deleted.connect(self.delete_coordinate)
            self.editor.coordinate_created.connect(self.create_coordinate)
            self.editor.coordinate_selected.connect(self.on_coordinate_selected)
            
            # Connect page navigation signals
            self.editor.page_navigation_requested.connect(self.navigate_to_page)
            self.viewer.page_changed.connect(self.on_page_changed)
    
    def open_pdf(self):
        """Open a PDF file."""
        file_dialog = QFileDialog()
        pdf_path, _ = file_dialog.getOpenFileName(
            self, "Open PDF File", "", "PDF Files (*.pdf)"
        )
        
        if pdf_path and validate_pdf_path(pdf_path):
            self.load_pdf(pdf_path)
        elif pdf_path:
            QMessageBox.warning(self, "Error", "Invalid PDF file selected.")
    
    def load_pdf(self, pdf_path: str):
        """Load a PDF file into the application."""
        try:
            # Load PDF in viewer
            if self.viewer.load_pdf(pdf_path):
                self.current_pdf_path = pdf_path
                
                # Create new session
                page_count = get_pdf_page_count(pdf_path)
                self.total_pages = page_count
                pdf_doc = PDFDocument(
                    file_path=pdf_path,
                    page_count=page_count,
                    file_size=os.path.getsize(pdf_path)
                )
                
                self.current_session = TableExtractionSession(pdf_document=pdf_doc)
                
                # Update page range controls
                self.end_page_input.setMaximum(page_count)
                self.end_page_input.setValue(page_count)
                self.start_page_input.setMaximum(page_count)
                
                # Clear previous coordinates
                self.coordinates_manager.clear_all()
                
                self.update_ui_state()
                self.status_bar.showMessage(f"Loaded PDF: {os.path.basename(pdf_path)}")
                
            else:
                QMessageBox.critical(self, "Error", "Failed to load PDF file.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading PDF: {str(e)}")
    
    def on_all_pages_toggled(self, checked: bool):
        """Handle toggling of 'All Pages' checkbox."""
        self.start_page_input.setEnabled(not checked)
        self.end_page_input.setEnabled(not checked)
        
        if checked and self.total_pages > 0:
            self.start_page_input.setValue(1)
            self.end_page_input.setValue(self.total_pages)
    
    def get_page_range(self) -> tuple:
        """Get the selected page range."""
        if self.all_pages_checkbox.isChecked():
            return (1, self.total_pages if self.total_pages > 0 else 1)
        else:
            start_page = self.start_page_input.value()
            end_page = self.end_page_input.value()
            
            # Validate range
            if start_page > end_page:
                start_page, end_page = end_page, start_page
                self.start_page_input.setValue(start_page)
                self.end_page_input.setValue(end_page)
            
            # Ensure we don't exceed total pages
            if self.total_pages > 0:
                end_page = min(end_page, self.total_pages)
                self.end_page_input.setValue(end_page)
            
            return (start_page, end_page)
    
    def extract_tables_with_range(self):
        """Extract tables from selected page range."""
        if not self.current_pdf_path:
            QMessageBox.warning(self, "Warning", "Please open a PDF file first.")
            return
        
        start_page, end_page = self.get_page_range()
        
        # Confirm if user selected a large range
        pages_count = end_page - start_page + 1
        if pages_count > 50:
            reply = QMessageBox.question(
                self, 
                "Large Page Range", 
                f"You've selected {pages_count} pages for extraction. This may take a while. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        self.start_custom_batch_extraction(start_page, end_page)
    
    def start_custom_batch_extraction(self, start_page: int, end_page: int):
        """Start custom batch extraction for specified page range."""
        if self.custom_batch_worker and self.custom_batch_worker.isRunning():
            QMessageBox.information(self, "Info", "Extraction already in progress.")
            return
        
        # Reset coordinates
        self.all_extracted_coordinates = []
        
        # Create custom batch worker
        batch_size = self.batch_size_spinbox.value()
        self.custom_batch_worker = BatchExtractionWorkerCustom(
            self.current_pdf_path, batch_size, start_page, end_page
        )
        
        # Connect signals
        self.custom_batch_worker.page_completed.connect(self.on_page_extraction_completed)
        self.custom_batch_worker.batch_completed.connect(self.on_batch_extraction_completed)
        self.custom_batch_worker.progress_updated.connect(self.on_custom_batch_progress_updated)
        self.custom_batch_worker.error_occurred.connect(self.on_batch_extraction_error)
        
        # Update UI
        self.extract_button.setEnabled(False)
        self.stop_button.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)  # Determinate progress
        
        # Start extraction
        self.custom_batch_worker.start()
        pages_count = end_page - start_page + 1
        self.status_bar.showMessage(f"Starting extraction for pages {start_page}-{end_page} ({pages_count} pages)...")
    
    def on_custom_batch_progress_updated(self, processed_pages: int, total_pages: int):
        """Handle progress updates during custom batch extraction."""
        progress = int((processed_pages / total_pages) * 100)
        self.progress_bar.setValue(progress)
        start_page, end_page = self.get_page_range()
        current_page = start_page + processed_pages - 1
        self.status_bar.showMessage(f"Processing page {current_page} of {start_page}-{end_page} range...")
    
    def extract_all_pages(self):
        """Extract tables from all pages using traditional method."""
        if not self.current_pdf_path:
            QMessageBox.warning(self, "Warning", "Please open a PDF file first.")
            return
        
        self.start_extraction(self.current_pdf_path, 'all')
    
    def extract_all_pages_batch(self):
        """Extract tables from all pages using batch processing."""
        if not self.current_pdf_path:
            QMessageBox.warning(self, "Warning", "Please open a PDF file first.")
            return
        
        self.start_batch_extraction()
    
    def start_batch_extraction(self):
        """Start batch extraction process."""
        if self.batch_worker and self.batch_worker.isRunning():
            QMessageBox.information(self, "Info", "Batch extraction already in progress.")
            return
        
        # Reset coordinates
        self.all_extracted_coordinates = []
        
        # Create batch worker
        batch_size = self.batch_size_spinbox.value()
        self.batch_worker = self.extractor.start_batch_extraction(self.current_pdf_path, batch_size)
        
        # Connect signals
        self.batch_worker.page_completed.connect(self.on_page_extraction_completed)
        self.batch_worker.batch_completed.connect(self.on_batch_extraction_completed)
        self.batch_worker.progress_updated.connect(self.on_batch_progress_updated)
        self.batch_worker.error_occurred.connect(self.on_batch_extraction_error)
        
        # Update UI
        self.extract_button.setEnabled(False)
        self.stop_button.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)  # Determinate progress
        
        # Start extraction
        self.batch_worker.start()
        self.status_bar.showMessage("Starting batch extraction...")
    
    def stop_extraction(self):
        """Stop the current extraction process."""
        if self.custom_batch_worker and self.custom_batch_worker.isRunning():
            self.custom_batch_worker.stop()
            self.custom_batch_worker.wait()
        
        if self.batch_worker and self.batch_worker.isRunning():
            self.batch_worker.stop()
            self.batch_worker.wait()
        
        if self.extraction_worker and self.extraction_worker.isRunning():
            self.extraction_worker.terminate()
            self.extraction_worker.wait()
        
        # Reset UI
        self.extract_button.setEnabled(True)
        self.stop_button.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Extraction stopped")
    
    def on_page_extraction_completed(self, page_number: int, page_coordinates: list):
        """Handle completion of extraction for a single page."""
        print(f"DEBUG - Page {page_number} extraction completed with {len(page_coordinates)} new coordinates")
        
        # Preserve existing user-created coordinates for this page from coordinates_manager
        existing_user_coords_manager = [
            coord for coord in self.coordinates_manager.get_all_coordinates()
            if coord.get('page') == page_number and coord.get('user_created', False)
        ]
        
        # Also preserve from all_extracted_coordinates (for consistency)
        existing_user_coords_extracted = [
            coord for coord in self.all_extracted_coordinates 
            if coord.get('page') == page_number and coord.get('user_created', False)
        ]
        
        # Use the most complete set of user coordinates
        existing_user_coords = existing_user_coords_manager if existing_user_coords_manager else existing_user_coords_extracted
        
        print(f"DEBUG - Preserving {len(existing_user_coords)} user-created coordinates for page {page_number}")
        
        # Remove all coordinates for this page from both data structures
        self.all_extracted_coordinates = [
            coord for coord in self.all_extracted_coordinates 
            if coord.get('page') != page_number
        ]
        
        # Remove page coordinates from manager
        coords_to_remove = [
            coord['id'] for coord in self.coordinates_manager.get_all_coordinates()
            if coord.get('page') == page_number
        ]
        for coord_id in coords_to_remove:
            self.coordinates_manager.remove_coordinate(coord_id)
        
        print(f"DEBUG - Removed {len(coords_to_remove)} old coordinates for page {page_number}")
        
        # Add new Camelot coordinates to both structures
        for coord_data in page_coordinates:
            # Add to manager first to get consistent ID
            manager_id = self.coordinates_manager.add_coordinate(coord_data)
            # Update the coordinate with the manager's ID
            coord_data['id'] = manager_id
            # Add to extracted list
            self.all_extracted_coordinates.append(coord_data)
        
        # Re-add preserved user coordinates to both structures
        for user_coord in existing_user_coords:
            # Add to manager
            manager_id = self.coordinates_manager.add_coordinate(user_coord)
            # Update the coordinate with the manager's ID
            user_coord['id'] = manager_id
            # Add to extracted list
            self.all_extracted_coordinates.append(user_coord)
        
        print(f"DEBUG - Added {len(page_coordinates)} new + {len(existing_user_coords)} preserved = {len(page_coordinates) + len(existing_user_coords)} coordinates")
        print(f"DEBUG - Manager now has {len(self.coordinates_manager.get_all_coordinates())} total coordinates")
        print(f"DEBUG - Extracted list now has {len(self.all_extracted_coordinates)} total coordinates")
        
        # Update viewer with current coordinates (incremental display)
        if self.viewer:
            # Convert coordinates to the format expected by the viewer
            viewer_coordinates = []
            for coord in self.all_extracted_coordinates:
                viewer_coord = {
                    'id': coord['id'],
                    'page': coord['page'],
                    'x1': coord['x1'],
                    'y1': coord['y1'],
                    'x2': coord['x2'],
                    'y2': coord['y2'],
                    'user_created': coord.get('user_created', False)
                }
                viewer_coordinates.append(viewer_coord)
            
            self.viewer.set_coordinates(viewer_coordinates)
        
        # Update editor if available
        if self.editor:
            self.editor.set_coordinates(self.all_extracted_coordinates)
        
        user_count = len(existing_user_coords)
        camelot_count = len(page_coordinates)
        message = f"Completed page {page_number}. Found {camelot_count} tables"
        if user_count > 0:
            message += f" (preserved {user_count} user-created)"
        message += f". Total: {len(self.all_extracted_coordinates)}"
        
        self.status_bar.showMessage(message)
    
    def on_batch_progress_updated(self, current_page: int, total_pages: int):
        """Handle progress updates during batch extraction."""
        progress = int((current_page / total_pages) * 100)
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(f"Processing page {current_page} of {total_pages}...")
    
    def on_batch_extraction_completed(self, all_coordinates: list):
        """Handle completion of batch extraction."""
        print(f"DEBUG - Batch extraction completed. Received {len(all_coordinates)} new coordinates")
        print(f"DEBUG - Manager currently has {len(self.coordinates_manager.get_all_coordinates())} coordinates")
        print(f"DEBUG - Extracted list currently has {len(self.all_extracted_coordinates)} coordinates")
        
        # Since we've been maintaining coordinates incrementally during page completion,
        # we just need to validate synchronization and clean up the UI
        
        manager_count = len(self.coordinates_manager.get_all_coordinates())
        extracted_count = len(self.all_extracted_coordinates)
        
        if manager_count != extracted_count:
            print(f"WARNING - Coordinate count mismatch: manager={manager_count}, extracted={extracted_count}")
            # In case of mismatch, trust the all_extracted_coordinates which should be complete
            print("DEBUG - Resyncing coordinates_manager with all_extracted_coordinates")
            self.coordinates_manager.clear_all()
            for coord_data in self.all_extracted_coordinates:
                new_id = self.coordinates_manager.add_coordinate(coord_data)
                coord_data['id'] = new_id
        
        # Final update to UI components
        if self.viewer:
            viewer_coordinates = []
            for coord in self.all_extracted_coordinates:
                viewer_coord = {
                    'id': coord['id'],
                    'page': coord['page'],
                    'x1': coord['x1'],
                    'y1': coord['y1'],
                    'x2': coord['x2'],
                    'y2': coord['y2'],
                    'user_created': coord.get('user_created', False)
                }
                viewer_coordinates.append(viewer_coord)
            
            self.viewer.set_coordinates(viewer_coordinates)
        
        if self.editor:
            self.editor.set_coordinates(self.all_extracted_coordinates)
        
        # Reset UI
        self.extract_button.setEnabled(True)
        self.stop_button.setVisible(False)
        self.progress_bar.setVisible(False)
        self.export_button.setEnabled(True)
        
        # Show completion message
        total_tables = len(self.all_extracted_coordinates)
        
        # Get page range information
        if hasattr(self, 'custom_batch_worker') and self.custom_batch_worker:
            start_page = self.custom_batch_worker.start_page
            end_page = self.custom_batch_worker.end_page
            pages_info = f" (pages {start_page}-{end_page})"
        else:
            pages_info = " across all pages"
        
        message = f"Batch extraction complete! Found {total_tables} tables{pages_info}."
        
        self.status_bar.showMessage(message)
        
        print(f"DEBUG - Final status: {message}")
        print(f"DEBUG - Final counts - Manager: {len(self.coordinates_manager.get_all_coordinates())}, Extracted: {len(self.all_extracted_coordinates)}")
        
        QMessageBox.information(
            self, 
            "Extraction Complete", 
            f"Batch extraction completed successfully!\n\nFound {total_tables} tables{pages_info}.\n\n" +
            "You can now review and edit the table boundaries before exporting."
        )
    
    def on_batch_extraction_error(self, error_message: str):
        """Handle errors during batch extraction."""
        QMessageBox.critical(self, "Batch Extraction Error", f"Error during batch extraction:\n\n{error_message}")
        
        # Reset UI
        self.extract_button.setEnabled(True)
        self.stop_button.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage("Batch extraction failed")
    
    def extract_current_page(self):
        """Extract tables from the current page."""
        if not self.current_pdf_path or not self.viewer:
            QMessageBox.warning(self, "Warning", "Please open a PDF file first.")
            return
        
        current_page = self.viewer.current_page + 1  # Convert to 1-based
        self.start_extraction(self.current_pdf_path, str(current_page))
    
    def start_extraction(self, pdf_path: str, pages: str):
        """Start table extraction in a worker thread."""
        if self.extraction_worker and self.extraction_worker.isRunning():
            QMessageBox.information(self, "Info", "Extraction already in progress.")
            return
        
        # Create and start worker
        self.extraction_worker = ExtractionWorker(pdf_path, pages)
        self.extraction_worker.finished.connect(self.on_extraction_finished)
        self.extraction_worker.progress.connect(self.on_extraction_progress)
        self.extraction_worker.error.connect(self.on_extraction_error)
        
        # Update UI
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.extract_button.setEnabled(False)
        
        self.extraction_worker.start()
    
    def on_extraction_finished(self, coordinates: list):
        """Handle extraction completion."""
        # Clear existing coordinates and update all_extracted_coordinates
        self.coordinates_manager.clear_all()
        self.all_extracted_coordinates = []
        
        # Add new coordinates to both manager and extracted list
        for coord_data in coordinates:
            coord_id = self.coordinates_manager.add_coordinate(coord_data)
            # Update the coordinate with the assigned ID
            coord_data['id'] = coord_id
            self.all_extracted_coordinates.append(coord_data)
        
        # Update session
        if self.current_session:
            # Convert to TableCoordinate objects
            from data.models import TableCoordinate
            for coord_data in coordinates:
                table_coord = TableCoordinate.from_dict(coord_data)
                self.current_session.add_coordinate(table_coord)
        
        print(f"DEBUG - Regular extraction completed: {len(coordinates)} coordinates added to both manager and extracted list")
        
        # Update UI
        self.update_coordinates_display()
        self.progress_bar.setVisible(False)
        self.extract_button.setEnabled(True)
        
        self.status_bar.showMessage(f"Extraction complete: {len(coordinates)} tables found")
    
    def on_extraction_progress(self, message: str):
        """Handle extraction progress updates."""
        self.status_bar.showMessage(message)
    
    def on_extraction_error(self, error_message: str):
        """Handle extraction errors."""
        self.progress_bar.setVisible(False)
        self.extract_button.setEnabled(True)
        
        QMessageBox.critical(self, "Extraction Error", error_message)
        self.status_bar.showMessage("Extraction failed")
    
    def update_coordinates_display(self):
        """Update the coordinates display in viewer and editor."""
        # Merge coordinates from both the manager and extracted coordinates
        manager_coords = self.coordinates_manager.get_all_coordinates()
        
        # Create a unified list, prioritizing manager coordinates and ensuring no duplicates
        all_coords = []
        coord_ids = set()
        
        # First, add all coordinates from the manager (includes user-created ones)
        for coord in manager_coords:
            coord_id = coord.get('id')
            if coord_id is not None and coord_id not in coord_ids:
                all_coords.append(coord)
                coord_ids.add(coord_id)
        
        # Then add extracted coordinates that aren't already included
        if hasattr(self, 'all_extracted_coordinates') and self.all_extracted_coordinates:
            for coord in self.all_extracted_coordinates:
                coord_id = coord.get('id')
                if coord_id is not None and coord_id not in coord_ids:
                    all_coords.append(coord)
                    coord_ids.add(coord_id)
        
        # Update viewer
        if self.viewer:
            self.viewer.set_coordinates(all_coords)
        
        # Update editor
        if self.editor:
            self.editor.set_coordinates(all_coords)
            if self.viewer:
                self.editor.set_current_page(self.viewer.current_page)
        
        print(f"DEBUG - Updated display with {len(all_coords)} coordinates ({len([c for c in all_coords if c.get('user_created', False)])} user-created)")
    
    def create_user_coordinate(self, x1: float, y1: float, x2: float, y2: float):
        """Create a new user-defined coordinate."""
        if not self.viewer:
            return
        
        current_page = self.viewer.current_page
        
        # DEBUG: Print user-drawn coordinates
        print(f"DEBUG - User drew table on page {current_page}:")
        print(f"  Raw coordinates: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        print(f"  Width: {x2-x1}, Height: {y2-y1}")
        
        # Create coordinate using the coordinates manager
        coord_id = self.coordinates_manager.create_user_coordinate(
            current_page, x1, y1, x2, y2
        )
        
        # NOTE: User coordinates are only stored in coordinates_manager
        # They don't need to be added to all_extracted_coordinates since
        # update_coordinates_display() prioritizes coordinates_manager
        
        # Add to session
        if self.current_session:
            from data.models import TableCoordinate
            coord_data = self.coordinates_manager.get_coordinate(coord_id)
            if coord_data:
                table_coord = TableCoordinate.from_dict(coord_data)
                self.current_session.add_coordinate(table_coord)
        
        # Update the display immediately
        self.update_coordinates_display()
        
        print(f"DEBUG - Created user coordinate with ID {coord_id}")
    
    def create_coordinate(self, coord_data: dict):
        """Create a new coordinate from editor."""
        coord_id = self.coordinates_manager.add_coordinate(coord_data)
        
        # Add to session
        if self.current_session:
            from data.models import TableCoordinate
            coord_data['id'] = coord_id
            table_coord = TableCoordinate.from_dict(coord_data)
            self.current_session.add_coordinate(table_coord)
        
        self.update_coordinates_display()
    
    def update_coordinate(self, coord_id: int, updates: dict):
        """Update an existing coordinate."""
        if self.coordinates_manager.update_coordinate(coord_id, updates):
            self.update_coordinates_display()
    
    def delete_coordinate(self, coord_id: int):
        """Delete a coordinate."""
        print(f"DEBUG - Attempting to delete coordinate {coord_id}")
        
        if self.coordinates_manager.remove_coordinate(coord_id):
            print(f"DEBUG - Removed coordinate {coord_id} from coordinates_manager")
            
            # Remove from session
            if self.current_session:
                self.current_session.remove_coordinate(coord_id)
                print(f"DEBUG - Removed coordinate {coord_id} from current_session")
            
            # Also remove from extracted coordinates list to prevent reappearing
            if hasattr(self, 'all_extracted_coordinates') and self.all_extracted_coordinates:
                original_count = len(self.all_extracted_coordinates)
                self.all_extracted_coordinates = [
                    coord for coord in self.all_extracted_coordinates 
                    if coord.get('id') != coord_id
                ]
                new_count = len(self.all_extracted_coordinates)
                
                if original_count != new_count:
                    print(f"DEBUG - Removed coordinate {coord_id} from all_extracted_coordinates ({original_count} -> {new_count})")
                else:
                    print(f"DEBUG - Coordinate {coord_id} was not found in all_extracted_coordinates")
            else:
                print(f"DEBUG - all_extracted_coordinates is empty or not initialized")
            
            self.update_coordinates_display()
            print(f"DEBUG - Coordinate {coord_id} deletion complete")
        else:
            print(f"DEBUG - Failed to remove coordinate {coord_id} from coordinates_manager")
    
    def on_coordinate_selected(self, coord_id: int):
        """Handle coordinate selection."""
        # This could be used for additional actions when a coordinate is selected
        pass
    
    def on_rectangle_moved(self, coord_id: int, x1: float, y1: float, x2: float, y2: float):
        """Handle rectangle move/resize operations."""
        print(f"DEBUG - Rectangle {coord_id} moved to: x1={x1}, y1={y1}, x2={x2}, y2={y2}")
        
        # Update the coordinate in both the manager and the extracted coordinates list
        updates = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
            'width': x2 - x1,
            'height': y2 - y1
        }
        
        # Update in coordinates manager
        if self.coordinates_manager.update_coordinate(coord_id, updates):
            print(f"DEBUG - Updated coordinate {coord_id} in manager")
        
        # Update in extracted coordinates list
        for coord in self.all_extracted_coordinates:
            if coord.get('id') == coord_id:
                coord.update(updates)
                print(f"DEBUG - Updated coordinate {coord_id} in extracted list")
                break
        
        # Refresh the display
        self.update_coordinates_display()
    
    def export_table_images(self):
        """Export all table regions as images."""
        # Get all coordinates from both the manager and the extracted coordinates
        manager_coords = self.coordinates_manager.get_all_coordinates()
        extracted_coords = self.all_extracted_coordinates or []
        
        # Merge coordinates, avoiding duplicates
        all_coords = []
        coord_ids = set()
        
        # First, add all coordinates from the manager (includes user-created ones)
        for coord in manager_coords:
            coord_id = coord.get('id')
            if coord_id is not None and coord_id not in coord_ids:
                all_coords.append(coord)
                coord_ids.add(coord_id)
        
        # Then add extracted coordinates that aren't already included
        for coord in extracted_coords:
            coord_id = coord.get('id')
            if coord_id is not None and coord_id not in coord_ids:
                all_coords.append(coord)
                coord_ids.add(coord_id)
        
        if not self.current_pdf_path or not all_coords:
            QMessageBox.warning(self, "Warning", 
                              "Please load a PDF and extract tables first.")
            return
        
        # Choose export directory
        export_dir = QFileDialog.getExistingDirectory(
            self, "Choose Export Directory", 
            os.path.join(os.path.dirname(self.current_pdf_path or "."), "table_exports")
        )
        
        if not export_dir:
            return
        
        try:
            # Load renderer
            if not self.renderer.load_pdf(self.current_pdf_path):
                QMessageBox.critical(self, "Error", "Failed to load PDF for rendering.")
                return
            
            # Show export info
            user_created = len([c for c in all_coords if c.get('user_created', False)])
            auto_detected = len(all_coords) - user_created
            
            QMessageBox.information(
                self, "Export Starting", 
                f"Exporting {len(all_coords)} tables:\n"
                f"• {auto_detected} auto-detected tables\n"
                f"• {user_created} user-created tables\n\n"
                f"Export directory: {export_dir}"
            )
            
            # Export
            exported_files = self.renderer.export_all_tables(
                all_coords, export_dir, "table", "PNG"
            )
            
            if exported_files:
                QMessageBox.information(
                    self, "Export Complete", 
                    f"Successfully exported {len(exported_files)} table images to:\n{export_dir}\n\n"
                    f"Files created:\n" + "\n".join([os.path.basename(f) for f in exported_files[:5]]) +
                    (f"\n... and {len(exported_files) - 5} more files" if len(exported_files) > 5 else "")
                )
            else:
                QMessageBox.warning(self, "Export Failed", "No images were exported. Please check the console for error details.")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting images: {str(e)}")
            import traceback
            print(f"Export error traceback: {traceback.format_exc()}")
    
    def export_coordinates(self):
        """Export coordinates to file."""
        if not self.coordinates_manager.get_all_coordinates():
            QMessageBox.warning(self, "Warning", "No coordinates to export.")
            return
        
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Export Coordinates", "", 
            "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            coordinates = self.coordinates_manager.get_all_coordinates()
            
            # Convert to TableCoordinate objects
            from data.models import TableCoordinate
            table_coords = []
            for coord_data in coordinates:
                table_coords.append(TableCoordinate.from_dict(coord_data))
            
            if file_path.endswith('.csv'):
                success = self.storage_manager.save_coordinates_csv(table_coords, file_path)
            else:
                success = self.storage_manager.save_coordinates_json(table_coords, file_path)
            
            if success:
                QMessageBox.information(self, "Export Complete", 
                                      f"Coordinates exported to:\n{file_path}")
            else:
                QMessageBox.critical(self, "Export Failed", "Failed to export coordinates.")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting coordinates: {str(e)}")
    
    def save_session(self):
        """Save the current session."""
        if not self.current_session:
            QMessageBox.warning(self, "Warning", "No session to save.")
            return
        
        try:
            file_path = self.storage_manager.save_session(self.current_session)
            if file_path:
                QMessageBox.information(self, "Session Saved", 
                                      f"Session saved to:\n{file_path}")
            else:
                QMessageBox.critical(self, "Save Failed", "Failed to save session.")
                
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving session: {str(e)}")
    
    def load_session(self):
        """Load a saved session."""
        # Get list of available sessions
        sessions = self.storage_manager.list_sessions()
        
        if not sessions:
            QMessageBox.information(self, "No Sessions", "No saved sessions found.")
            return
        
        # Simple dialog to select session (could be improved with a custom dialog)
        from PyQt5.QtWidgets import QInputDialog
        
        session_names = [f"{s['session_id']} - {os.path.basename(s['pdf_path'])}" 
                        for s in sessions]
        
        session_name, ok = QInputDialog.getItem(
            self, "Load Session", "Select session to load:", 
            session_names, 0, False
        )
        
        if ok and session_name:
            session_id = session_name.split(' - ')[0]
            
            try:
                session = self.storage_manager.load_session(session_id)
                if session:
                    # Load the PDF
                    if os.path.exists(session.pdf_document.file_path):
                        self.load_pdf(session.pdf_document.file_path)
                        
                        # Load coordinates
                        self.coordinates_manager.clear_all()
                        for coord in session.coordinates:
                            self.coordinates_manager.add_coordinate(coord.to_dict())
                        
                        self.current_session = session
                        self.update_coordinates_display()
                        
                        QMessageBox.information(self, "Session Loaded", 
                                              f"Session '{session_id}' loaded successfully.")
                    else:
                        QMessageBox.warning(self, "PDF Not Found", 
                                          f"PDF file not found:\n{session.pdf_document.file_path}")
                else:
                    QMessageBox.critical(self, "Load Failed", "Failed to load session.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Error loading session: {str(e)}")
    
    def navigate_to_page(self, page_num: int):
        """Navigate to a specific page."""
        if self.viewer:
            self.viewer.go_to_page(page_num)
    
    def on_page_changed(self, page_num: int):
        """Handle page change from viewer."""
        if self.editor:
            self.editor.set_current_page(page_num)
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About Table Vision",
            "Table Vision v1.0\n\n"
            "A PDF table extraction and visualization tool using Camelot.\n\n"
            "Features:\n"
            "• Automatic table detection\n"
            "• Interactive table outline editing\n"
            "• Table image export\n"
            "• Session management\n\n"
            "Built with PyQt5 and Camelot-py"
        )
    
    def update_ui_state(self):
        """Update UI state based on current conditions."""
        has_pdf = self.current_pdf_path is not None
        has_coordinates = len(self.coordinates_manager.get_all_coordinates()) > 0
        
        # Update button states
        self.extract_button.setEnabled(has_pdf)
        self.export_button.setEnabled(has_pdf and has_coordinates)
        
        # Update status
        if has_pdf:
            self.pdf_status_label.setText(f"PDF: {os.path.basename(self.current_pdf_path)}")
        else:
            self.pdf_status_label.setText("No PDF loaded")
    
    def update_status(self):
        """Update status bar information."""
        coord_count = len(self.coordinates_manager.get_all_coordinates())
        self.tables_status_label.setText(f"Tables: {coord_count}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Stop extraction worker if running
        if self.extraction_worker and self.extraction_worker.isRunning():
            self.extraction_worker.terminate()
            self.extraction_worker.wait()
        
        # Close PDF documents
        if self.extractor:
            self.extractor.close_pdf()
        if self.renderer:
            self.renderer.close_pdf()
        
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Table Vision")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
