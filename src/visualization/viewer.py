"""
PDF viewer with interactive table outline display and editing capabilities.
"""
from PyQt5.QtWidgets import (QWidget, QScrollArea, QLabel, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QSpinBox, QSlider,
                           QFrame, QSizePolicy, QApplication)
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QMouseEvent
import fitz  # PyMuPDF
from PIL import Image
import io
from typing import List, Dict, Optional, Tuple


class InteractivePDFLabel(QLabel):
    """Custom QLabel for displaying PDF with interactive table outlines."""
    
    # Signals
    rectangle_selected = pyqtSignal(int)  # Emitted when a rectangle is selected
    rectangle_moved = pyqtSignal(int, float, float, float, float)  # Emitted when rectangle is moved
    new_rectangle_created = pyqtSignal(float, float, float, float)  # Emitted when new rectangle is drawn
    rectangle_deleted = pyqtSignal(int)  # Emitted when rectangle is deleted
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 600)
        
        # State variables
        self.coordinates: List[Dict] = []
        self.selected_rect_id: Optional[int] = None
        self.scale_factor = 1.0
        self.page_pixmap: Optional[QPixmap] = None
        self.current_page = 0  # Add current_page to this class
        
        # Mouse interaction state
        self.drawing_new_rect = False
        self.moving_rect = False
        self.resizing_rect = False
        self.start_pos = QPoint()
        self.current_pos = QPoint()
        self.resize_handle = None  # 'tl', 'tr', 'bl', 'br', 'l', 'r', 't', 'b'
        
        # Appearance settings
        self.rect_color = QColor(255, 0, 0, 100)  # Semi-transparent red
        self.selected_rect_color = QColor(0, 255, 0, 150)  # Semi-transparent green
        self.handle_size = 8
        
        self.setMouseTracking(True)
    
    def set_coordinates(self, coordinates: List[Dict]):
        """Set the table coordinates to display."""
        self.coordinates = coordinates
        self.update()
    
    def set_current_page(self, page: int):
        """Set the current page number."""
        self.current_page = page
        self.update()
    
    def set_page_image(self, pixmap: QPixmap):
        """Set the PDF page image."""
        self.page_pixmap = pixmap
        self.setPixmap(pixmap)
        self.update()
    
    def set_scale_factor(self, scale: float):
        """Set the scale factor for display."""
        self.scale_factor = scale
        if self.page_pixmap:
            scaled_pixmap = self.page_pixmap.scaled(
                int(self.page_pixmap.width() * scale),
                int(self.page_pixmap.height() * scale),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event to draw rectangles over the PDF."""
        super().paintEvent(event)
        
        if not self.coordinates or not self.page_pixmap:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate offset to center the image
        pixmap = self.pixmap()
        if not pixmap:
            return
            
        x_offset = (self.width() - pixmap.width()) // 2
        y_offset = (self.height() - pixmap.height()) // 2
        
        # Filter coordinates for current page only
        current_page_coords = [coord for coord in self.coordinates if coord.get('page') == self.current_page]
        
        # DEBUG: Show page filtering
        debug = False  # Set to True for debugging page filtering issues
        if debug:
            print(f"DEBUG - Page filtering: current_page={self.current_page}")
            print(f"  Total coordinates: {len(self.coordinates)}")
            print(f"  Current page coordinates: {len(current_page_coords)}")
            for coord in self.coordinates:
                print(f"    Coord page={coord.get('page')}, id={coord.get('id')}, user_created={coord.get('user_created', False)}")
                if coord.get('page') == self.current_page:
                    print(f"      → Will be drawn: {coord}")
        
        # Draw rectangles
        for coord in current_page_coords:
            rect_id = coord.get('id', -1)
            is_selected = rect_id == self.selected_rect_id
            
            # Convert coordinates to screen coordinates
            screen_rect = self._coord_to_screen_rect(coord, x_offset, y_offset)
            
            # Set pen and brush
            if is_selected:
                painter.setPen(QPen(self.selected_rect_color, 2))
                painter.setBrush(self.selected_rect_color)
            else:
                painter.setPen(QPen(self.rect_color, 2))
                painter.setBrush(self.rect_color)
            
            # Draw rectangle
            painter.drawRect(screen_rect)
            
            # Draw resize handles for selected rectangle
            if is_selected:
                self._draw_resize_handles(painter, screen_rect)
            
            # Draw label
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            
            label_text = f"T{rect_id}"
            if coord.get('user_created', False):
                label_text += "*"
                
            painter.drawText(screen_rect.topLeft() + QPoint(5, 15), label_text)
        
        # Draw new rectangle being created
        if self.drawing_new_rect:
            painter.setPen(QPen(QColor(0, 0, 255, 150), 2, Qt.DashLine))
            painter.setBrush(QColor(0, 0, 255, 50))
            
            rect = QRect(self.start_pos, self.current_pos).normalized()
            painter.drawRect(rect)
    
    def _coord_to_screen_rect(self, coord: Dict, x_offset: int, y_offset: int) -> QRect:
        """Convert coordinate dictionary to screen rectangle."""
        if not self.page_pixmap:
            return QRect()
        
        # The pixmap is rendered at 2x for quality, so actual PDF page dimensions are:
        actual_page_width = self.page_pixmap.width() / 2.0
        actual_page_height = self.page_pixmap.height() / 2.0
        
        # DEBUG: Print coordinate conversion details (only if debug enabled)
        debug = False  # Set to True for debugging coordinate transformation issues
        if debug:
            print(f"DEBUG - Converting coordinates to screen:")
            print(f"  Input coord: {coord}")
            print(f"  Pixmap dimensions: {self.page_pixmap.width()} x {self.page_pixmap.height()}")
            print(f"  Actual PDF dimensions: {actual_page_width} x {actual_page_height}")
            print(f"  Scale factor: {self.scale_factor}")
            print(f"  Offset: ({x_offset}, {y_offset})")
        
        # Camelot coordinates are in PDF coordinate system (bottom-left origin)
        # Convert to screen coordinates (top-left origin)
        
        # Scale coordinates from PDF space to pixmap space (accounting for 2x rendering)
        pixmap_x1 = coord['x1'] * 2.0
        pixmap_x2 = coord['x2'] * 2.0
        
        # Y coordinates: flip from PDF (bottom-origin) to screen (top-origin)
        # In PDF: y1 is bottom, y2 is top
        # In screen: we want top-left to bottom-right
        pixmap_y1 = (actual_page_height - coord['y2']) * 2.0  # PDF top becomes screen top
        pixmap_y2 = (actual_page_height - coord['y1']) * 2.0  # PDF bottom becomes screen bottom
        
        # Now apply the viewer's scale factor
        screen_x1 = pixmap_x1 * self.scale_factor
        screen_x2 = pixmap_x2 * self.scale_factor
        screen_y1 = pixmap_y1 * self.scale_factor
        screen_y2 = pixmap_y2 * self.scale_factor
        
        if debug:
            print(f"  Pixmap coordinates: x1={pixmap_x1}, y1={pixmap_y1}, x2={pixmap_x2}, y2={pixmap_y2}")
            print(f"  Screen coordinates: x1={screen_x1}, y1={screen_y1}, x2={screen_x2}, y2={screen_y2}")
            print(f"  Width: {screen_x2-screen_x1}, Height: {screen_y2-screen_y1}")
        
        # Calculate final screen rectangle
        screen_rect = QRect(
            int(screen_x1 + x_offset),
            int(screen_y1 + y_offset),
            int(screen_x2 - screen_x1),
            int(screen_y2 - screen_y1)
        )
        
        if debug:
            print(f"  Final QRect: {screen_rect}")
        
        return screen_rect
    
    def _screen_to_coord_rect(self, screen_rect: QRect, x_offset: int, y_offset: int) -> Dict:
        """Convert screen rectangle to coordinate dictionary."""
        if not self.page_pixmap:
            return {}
        
        # The pixmap is rendered at 2x for quality, so actual PDF page dimensions are:
        actual_page_width = self.page_pixmap.width() / 2.0
        actual_page_height = self.page_pixmap.height() / 2.0
        
        # DEBUG: Print screen to coordinate conversion (only if debug enabled)
        debug = False  # Set to True for debugging
        if debug:
            print(f"DEBUG - Converting screen to coordinates:")
            print(f"  Input screen_rect: {screen_rect}")
            print(f"  Pixmap dimensions: {self.page_pixmap.width()} x {self.page_pixmap.height()}")
            print(f"  Actual PDF dimensions: {actual_page_width} x {actual_page_height}")
            print(f"  Scale factor: {self.scale_factor}")
            print(f"  Offset: ({x_offset}, {y_offset})")
        
        # Remove offset and scale from screen coordinates back to pixmap coordinates
        pixmap_x1 = (screen_rect.x() - x_offset) / self.scale_factor
        pixmap_y1 = (screen_rect.y() - y_offset) / self.scale_factor
        pixmap_x2 = (screen_rect.right() - x_offset) / self.scale_factor
        pixmap_y2 = (screen_rect.bottom() - y_offset) / self.scale_factor
        
        if debug:
            print(f"  Pixmap coords: x1={pixmap_x1}, y1={pixmap_y1}, x2={pixmap_x2}, y2={pixmap_y2}")
        
        # Convert from pixmap coordinates to PDF coordinates (accounting for 2x rendering)
        pdf_x1 = pixmap_x1 / 2.0
        pdf_x2 = pixmap_x2 / 2.0
        
        # Y coordinates need to be flipped back to PDF coordinate system (bottom-left origin)
        # Screen top -> PDF top (y2), Screen bottom -> PDF bottom (y1)
        pdf_y1 = actual_page_height - (pixmap_y2 / 2.0)  # Screen bottom becomes PDF bottom
        pdf_y2 = actual_page_height - (pixmap_y1 / 2.0)  # Screen top becomes PDF top
        
        result = {
            'x1': pdf_x1,
            'y1': pdf_y1,
            'x2': pdf_x2,
            'y2': pdf_y2,
            'width': pdf_x2 - pdf_x1,
            'height': pdf_y2 - pdf_y1,
            'page': self.current_page,
            'user_created': True
        }
        
        if debug:
            print(f"  Final PDF coordinates: {result}")
        
        return result
    
    def _draw_resize_handles(self, painter: QPainter, rect: QRect):
        """Draw resize handles around a rectangle."""
        handle_size = self.handle_size
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setBrush(QColor(0, 255, 0))
        
        # Corner handles
        handles = [
            QRect(rect.left() - handle_size//2, rect.top() - handle_size//2, handle_size, handle_size),  # TL
            QRect(rect.right() - handle_size//2, rect.top() - handle_size//2, handle_size, handle_size),  # TR
            QRect(rect.left() - handle_size//2, rect.bottom() - handle_size//2, handle_size, handle_size),  # BL
            QRect(rect.right() - handle_size//2, rect.bottom() - handle_size//2, handle_size, handle_size),  # BR
        ]
        
        # Side handles
        handles.extend([
            QRect(rect.center().x() - handle_size//2, rect.top() - handle_size//2, handle_size, handle_size),  # T
            QRect(rect.center().x() - handle_size//2, rect.bottom() - handle_size//2, handle_size, handle_size),  # B
            QRect(rect.left() - handle_size//2, rect.center().y() - handle_size//2, handle_size, handle_size),  # L
            QRect(rect.right() - handle_size//2, rect.center().y() - handle_size//2, handle_size, handle_size),  # R
        ])
        
        for handle in handles:
            painter.drawRect(handle)
    
    def _get_resize_handle_at_pos(self, pos: QPoint) -> Optional[str]:
        """Get the resize handle at the given position."""
        if self.selected_rect_id is None:
            return None
        
        # Find selected rectangle
        selected_coord = None
        for coord in self.coordinates:
            if coord.get('id') == self.selected_rect_id:
                selected_coord = coord
                break
        
        if not selected_coord:
            return None
        
        # Calculate offsets
        pixmap = self.pixmap()
        if not pixmap:
            return None
            
        x_offset = (self.width() - pixmap.width()) // 2
        y_offset = (self.height() - pixmap.height()) // 2
        
        screen_rect = self._coord_to_screen_rect(selected_coord, x_offset, y_offset)
        handle_size = self.handle_size
        
        # Check each handle
        handles = {
            'tl': QRect(screen_rect.left() - handle_size//2, screen_rect.top() - handle_size//2, handle_size, handle_size),
            'tr': QRect(screen_rect.right() - handle_size//2, screen_rect.top() - handle_size//2, handle_size, handle_size),
            'bl': QRect(screen_rect.left() - handle_size//2, screen_rect.bottom() - handle_size//2, handle_size, handle_size),
            'br': QRect(screen_rect.right() - handle_size//2, screen_rect.bottom() - handle_size//2, handle_size, handle_size),
            't': QRect(screen_rect.center().x() - handle_size//2, screen_rect.top() - handle_size//2, handle_size, handle_size),
            'b': QRect(screen_rect.center().x() - handle_size//2, screen_rect.bottom() - handle_size//2, handle_size, handle_size),
            'l': QRect(screen_rect.left() - handle_size//2, screen_rect.center().y() - handle_size//2, handle_size, handle_size),
            'r': QRect(screen_rect.right() - handle_size//2, screen_rect.center().y() - handle_size//2, handle_size, handle_size),
        }
        
        for handle_name, handle_rect in handles.items():
            if handle_rect.contains(pos):
                return handle_name
        
        return None
    
    def _get_rect_at_pos(self, pos: QPoint) -> Optional[int]:
        """Get the rectangle ID at the given position."""
        pixmap = self.pixmap()
        if not pixmap:
            return None
            
        x_offset = (self.width() - pixmap.width()) // 2
        y_offset = (self.height() - pixmap.height()) // 2
        
        # Filter coordinates for current page only
        current_page_coords = [coord for coord in self.coordinates if coord.get('page') == self.current_page]
        
        for coord in current_page_coords:
            screen_rect = self._coord_to_screen_rect(coord, x_offset, y_offset)
            if screen_rect.contains(pos):
                return coord.get('id')
        
        return None
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            
            # Check if clicking on a resize handle
            resize_handle = self._get_resize_handle_at_pos(pos)
            if resize_handle:
                self.resizing_rect = True
                self.resize_handle = resize_handle
                self.start_pos = pos
                return
            
            # Check if clicking on a rectangle
            rect_id = self._get_rect_at_pos(pos)
            if rect_id is not None:
                self.selected_rect_id = rect_id
                self.rectangle_selected.emit(rect_id)
                self.moving_rect = True
                self.start_pos = pos
                self.update()
                return
            
            # Start drawing new rectangle
            self.selected_rect_id = None
            self.drawing_new_rect = True
            self.start_pos = pos
            self.current_pos = pos
            self.update()
        
        elif event.button() == Qt.RightButton:
            # Right-click to delete rectangle
            rect_id = self._get_rect_at_pos(event.pos())
            if rect_id is not None:
                self.rectangle_deleted.emit(rect_id)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        pos = event.pos()
        
        if self.drawing_new_rect:
            self.current_pos = pos
            self.update()
        
        elif self.moving_rect and self.selected_rect_id is not None:
            # Move the selected rectangle
            delta = pos - self.start_pos
            
            # Find the selected coordinate and update its position
            for coord in self.coordinates:
                if coord.get('id') == self.selected_rect_id:
                    # Convert delta to PDF coordinates
                    pixmap = self.pixmap()
                    if pixmap:
                        # Convert screen delta to PDF delta
                        delta_pdf_x = delta.x() / (2.0 * self.scale_factor)
                        delta_pdf_y = delta.y() / (2.0 * self.scale_factor)
                        
                        # Update coordinate (but don't exceed PDF bounds)
                        coord['x1'] = max(0, coord['x1'] + delta_pdf_x)
                        coord['x2'] = max(coord['x1'], coord['x2'] + delta_pdf_x)
                        coord['y1'] = max(0, coord['y1'] - delta_pdf_y)  # Y is flipped
                        coord['y2'] = max(coord['y1'], coord['y2'] - delta_pdf_y)
                        
                        coord['width'] = coord['x2'] - coord['x1']
                        coord['height'] = coord['y2'] - coord['y1']
                        
                        self.update()
                    break
            
            self.start_pos = pos
        
        elif self.resizing_rect and self.selected_rect_id is not None:
            # Resize the selected rectangle based on which handle is being dragged
            # Find the selected coordinate
            for coord in self.coordinates:
                if coord.get('id') == self.selected_rect_id:
                    pixmap = self.pixmap()
                    if pixmap:
                        # Convert mouse position to PDF coordinates
                        x_offset = (self.width() - pixmap.width()) // 2
                        y_offset = (self.height() - pixmap.height()) // 2
                        
                        pdf_x = (pos.x() - x_offset) / (2.0 * self.scale_factor)
                        pdf_y = (self.page_pixmap.height() / (2.0 * self.scale_factor)) - ((pos.y() - y_offset) / (2.0 * self.scale_factor))
                        
                        # Update coordinates based on resize handle
                        if self.resize_handle in ['tl', 'l', 'bl']:  # Left handles
                            coord['x1'] = min(pdf_x, coord['x2'] - 10)  # Minimum width
                        if self.resize_handle in ['tr', 'r', 'br']:  # Right handles
                            coord['x2'] = max(pdf_x, coord['x1'] + 10)
                        if self.resize_handle in ['tl', 't', 'tr']:  # Top handles
                            coord['y2'] = max(pdf_y, coord['y1'] + 10)  # Minimum height
                        if self.resize_handle in ['bl', 'b', 'br']:  # Bottom handles
                            coord['y1'] = min(pdf_y, coord['y2'] - 10)
                        
                        coord['width'] = coord['x2'] - coord['x1']
                        coord['height'] = coord['y2'] - coord['y1']
                        
                        self.update()
                    break
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            if self.drawing_new_rect:
                # Finish drawing new rectangle
                pixmap = self.pixmap()
                if pixmap:
                    x_offset = (self.width() - pixmap.width()) // 2
                    y_offset = (self.height() - pixmap.height()) // 2
                    
                    screen_rect = QRect(self.start_pos, self.current_pos).normalized()
                    
                    # Only create if rectangle is large enough
                    if screen_rect.width() > 10 and screen_rect.height() > 10:
                        coord_dict = self._screen_to_coord_rect(screen_rect, x_offset, y_offset)
                        self.new_rectangle_created.emit(
                            coord_dict['x1'], coord_dict['y1'],
                            coord_dict['x2'], coord_dict['y2']
                        )
                
                self.drawing_new_rect = False
                self.update()
            
            elif self.moving_rect:
                # Emit rectangle moved signal
                if self.selected_rect_id is not None:
                    for coord in self.coordinates:
                        if coord.get('id') == self.selected_rect_id:
                            self.rectangle_moved.emit(
                                self.selected_rect_id,
                                coord['x1'], coord['y1'], coord['x2'], coord['y2']
                            )
                            break
                self.moving_rect = False
            
            elif self.resizing_rect:
                # Emit rectangle moved signal (resizing is also a move operation)
                if self.selected_rect_id is not None:
                    for coord in self.coordinates:
                        if coord.get('id') == self.selected_rect_id:
                            self.rectangle_moved.emit(
                                self.selected_rect_id,
                                coord['x1'], coord['y1'], coord['x2'], coord['y2']
                            )
                            break
                self.resizing_rect = False
                self.resize_handle = None


class TableViewer(QWidget):
    """Main PDF viewer widget with table outline visualization."""
    
    # Signals
    page_changed = pyqtSignal(int)  # Emitted when page changes
    
    def __init__(self):
        super().__init__()
        self.pdf_path = None
        self.current_page = 0
        self.coordinates = []
        self.current_zoom = 100  # Persistent zoom level
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("Previous Page")
        self.next_button = QPushButton("Next Page")
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(25, 300)
        self.zoom_slider.setValue(self.current_zoom)  # Use persistent zoom
        self.zoom_label = QLabel(f"{self.current_zoom}%")
        
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.page_spinbox)
        controls_layout.addWidget(self.next_button)
        controls_layout.addStretch()
        controls_layout.addWidget(QLabel("Zoom:"))
        controls_layout.addWidget(self.zoom_slider)
        controls_layout.addWidget(self.zoom_label)
        
        # PDF display area
        self.scroll_area = QScrollArea()
        self.pdf_label = InteractivePDFLabel()
        self.scroll_area.setWidget(self.pdf_label)
        self.scroll_area.setWidgetResizable(True)
        
        layout.addLayout(controls_layout)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
        # Connect signals
        self.prev_button.clicked.connect(self.previous_page)
        self.next_button.clicked.connect(self.next_page)
        self.page_spinbox.valueChanged.connect(self.on_page_spinbox_changed)
        self.zoom_slider.valueChanged.connect(self.zoom_changed)
        
    def load_pdf(self, pdf_path: str) -> bool:
        """Load a PDF file for viewing."""
        try:
            self.pdf_document = fitz.open(pdf_path)
            self.pdf_path = pdf_path
            self.current_page = 0
            
            # Update page controls
            self.page_spinbox.setMaximum(len(self.pdf_document))
            self.page_spinbox.setValue(1)
            
            self.update_page_display()
            return True
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    def update_page_display(self):
        """Update the display for the current page."""
        if not hasattr(self, 'pdf_document') or not self.pdf_document:
            return
        
        try:
            page = self.pdf_document[self.current_page]
            
            # Render page to pixmap
            mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to QPixmap
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Convert PIL to QPixmap
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(img_bytes.getvalue())
            
            # Set the image and preserve zoom
            self.pdf_label.set_page_image(pixmap)
            self.pdf_label.set_scale_factor(self.current_zoom / 100.0)  # Apply persistent zoom
            self.pdf_label.set_current_page(self.current_page)  # Set current page in label
            
            # Update coordinates for current page
            page_coords = [coord for coord in self.coordinates if coord.get('page') == self.current_page]
            self.pdf_label.set_coordinates(page_coords)
            
        except Exception as e:
            print(f"Error updating page display: {e}")
    
    def set_coordinates(self, coordinates: List[Dict]):
        """Set the table coordinates to display."""
        self.coordinates = coordinates
        self.update_page_display()
    
    def previous_page(self):
        """Go to the previous page."""
        if hasattr(self, 'pdf_document') and self.current_page > 0:
            self.current_page -= 1
            self.page_spinbox.setValue(self.current_page + 1)
            self.update_page_display()
            self.page_changed.emit(self.current_page)
    
    def next_page(self):
        """Go to the next page."""
        if hasattr(self, 'pdf_document') and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.page_spinbox.setValue(self.current_page + 1)
            self.update_page_display()
            self.page_changed.emit(self.current_page)
    
    def go_to_page(self, page_num: int):
        """Go to a specific page."""
        if hasattr(self, 'pdf_document') and 0 <= page_num < len(self.pdf_document):
            self.current_page = page_num
            self.page_spinbox.setValue(self.current_page + 1)
            self.update_page_display()
            self.page_changed.emit(self.current_page)
    
    def on_page_spinbox_changed(self, page_num_1_based: int):
        """Handle page spinbox changes (convert from 1-based to 0-based)."""
        page_num_0_based = page_num_1_based - 1
        if hasattr(self, 'pdf_document') and 0 <= page_num_0_based < len(self.pdf_document):
            self.current_page = page_num_0_based
            self.update_page_display()
            self.page_changed.emit(self.current_page)
    
    def zoom_changed(self, value: int):
        """Handle zoom slider changes."""
        self.current_zoom = value  # Persist zoom level
        scale_factor = value / 100.0
        self.pdf_label.set_scale_factor(scale_factor)
        self.zoom_label.setText(f"{value}%")
