"""
Table outline editor for adjusting, creating, and deleting table boundaries.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QListWidget, QListWidgetItem, QLabel, QSpinBox,
                           QDoubleSpinBox, QGroupBox, QCheckBox, QMessageBox,
                           QTreeWidget, QTreeWidgetItem, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Optional


class TableEditor(QWidget):
    """Widget for editing table coordinates and properties."""
    
    # Signals
    coordinate_updated = pyqtSignal(int, dict)  # coordinate_id, updated_data
    coordinate_deleted = pyqtSignal(int)  # coordinate_id
    coordinate_created = pyqtSignal(dict)  # coordinate_data
    coordinate_selected = pyqtSignal(int)  # coordinate_id
    page_navigation_requested = pyqtSignal(int)  # page_number
    
    def __init__(self):
        super().__init__()
        self.coordinates: List[Dict] = []
        self.current_page = 0
        self.selected_coordinate_id: Optional[int] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Create tab widget to organize different views
        tab_widget = QTabWidget()
        
        # Tab 1: Table Navigator
        navigator_tab = self.create_navigator_tab()
        tab_widget.addTab(navigator_tab, "Table Navigator")
        
        # Tab 2: Table Editor
        editor_tab = self.create_editor_tab()
        tab_widget.addTab(editor_tab, "Table Editor")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        
        # Initially disable editor
        self.set_editor_enabled(False)
    
    def create_navigator_tab(self):
        """Create the table navigator tab."""
        navigator_widget = QWidget()
        layout = QVBoxLayout()
        
        # All tables overview
        overview_group = QGroupBox("All Detected Tables")
        overview_layout = QVBoxLayout()
        
        # Tree widget to show tables organized by page
        self.table_tree = QTreeWidget()
        self.table_tree.setHeaderLabels(["Table", "Coordinates", "Type"])
        self.table_tree.itemDoubleClicked.connect(self.on_table_tree_double_click)
        
        overview_layout.addWidget(self.table_tree)
        overview_group.setLayout(overview_layout)
        
        # Quick navigation buttons
        nav_group = QGroupBox("Quick Navigation")
        nav_layout = QVBoxLayout()
        
        self.prev_table_btn = QPushButton("Previous Table")
        self.next_table_btn = QPushButton("Next Table")
        self.go_to_page_btn = QPushButton("Go to Selected Table")
        
        self.prev_table_btn.clicked.connect(self.navigate_previous_table)
        self.next_table_btn.clicked.connect(self.navigate_next_table)
        self.go_to_page_btn.clicked.connect(self.go_to_selected_table)
        
        nav_layout.addWidget(self.prev_table_btn)
        nav_layout.addWidget(self.next_table_btn)
        nav_layout.addWidget(self.go_to_page_btn)
        nav_group.setLayout(nav_layout)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.total_tables_label = QLabel("Total Tables: 0")
        self.pages_with_tables_label = QLabel("Pages with Tables: 0")
        self.auto_detected_label = QLabel("Auto Detected: 0")
        self.user_created_label = QLabel("User Created: 0")
        
        stats_layout.addWidget(self.total_tables_label)
        stats_layout.addWidget(self.pages_with_tables_label)
        stats_layout.addWidget(self.auto_detected_label)
        stats_layout.addWidget(self.user_created_label)
        stats_group.setLayout(stats_layout)
        
        layout.addWidget(overview_group)
        layout.addWidget(nav_group)
        layout.addWidget(stats_group)
        
        navigator_widget.setLayout(layout)
        return navigator_widget
    
    def create_editor_tab(self):
        """Create the table editor tab."""
        editor_widget = QWidget()
        layout = QVBoxLayout()
        
        # Coordinate list for current page
        list_group = QGroupBox("Current Page Table Coordinates")
        list_layout = QVBoxLayout()
        
        self.coordinate_list = QListWidget()
        self.coordinate_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        list_buttons_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setEnabled(False)
        
        self.create_button = QPushButton("Create New")
        self.create_button.clicked.connect(self.create_new_coordinate)
        
        list_buttons_layout.addWidget(self.delete_button)
        list_buttons_layout.addWidget(self.create_button)
        
        list_layout.addWidget(self.coordinate_list)
        list_layout.addLayout(list_buttons_layout)
        list_group.setLayout(list_layout)
        
        # Coordinate editor
        editor_group = QGroupBox("Edit Selected Coordinate")
        editor_layout = QVBoxLayout()
        
        # Position controls
        pos_layout = QHBoxLayout()
        
        pos_layout.addWidget(QLabel("X1:"))
        self.x1_spinbox = QDoubleSpinBox()
        self.x1_spinbox.setRange(0, 9999)
        self.x1_spinbox.setDecimals(2)
        self.x1_spinbox.valueChanged.connect(self.coordinate_value_changed)
        pos_layout.addWidget(self.x1_spinbox)
        
        pos_layout.addWidget(QLabel("Y1:"))
        self.y1_spinbox = QDoubleSpinBox()
        self.y1_spinbox.setRange(0, 9999)
        self.y1_spinbox.setDecimals(2)
        self.y1_spinbox.valueChanged.connect(self.coordinate_value_changed)
        pos_layout.addWidget(self.y1_spinbox)
        
        pos_layout.addWidget(QLabel("X2:"))
        self.x2_spinbox = QDoubleSpinBox()
        self.x2_spinbox.setRange(0, 9999)
        self.x2_spinbox.setDecimals(2)
        self.x2_spinbox.valueChanged.connect(self.coordinate_value_changed)
        pos_layout.addWidget(self.x2_spinbox)
        
        pos_layout.addWidget(QLabel("Y2:"))
        self.y2_spinbox = QDoubleSpinBox()
        self.y2_spinbox.setRange(0, 9999)
        self.y2_spinbox.setDecimals(2)
        self.y2_spinbox.valueChanged.connect(self.coordinate_value_changed)
        pos_layout.addWidget(self.y2_spinbox)
        
        # Size display
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Width:"))
        self.width_label = QLabel("0.00")
        size_layout.addWidget(self.width_label)
        
        size_layout.addWidget(QLabel("Height:"))
        self.height_label = QLabel("0.00")
        size_layout.addWidget(self.height_label)
        
        # Properties
        props_layout = QHBoxLayout()
        props_layout.addWidget(QLabel("Page:"))
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setRange(0, 999)
        self.page_spinbox.valueChanged.connect(self.coordinate_value_changed)
        props_layout.addWidget(self.page_spinbox)
        
        self.user_created_checkbox = QCheckBox("User Created")
        self.user_created_checkbox.stateChanged.connect(self.coordinate_value_changed)
        props_layout.addWidget(self.user_created_checkbox)
        
        # Apply button
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.clicked.connect(self.apply_changes)
        self.apply_button.setEnabled(False)
        
        editor_layout.addLayout(pos_layout)
        editor_layout.addLayout(size_layout)
        editor_layout.addLayout(props_layout)
        editor_layout.addWidget(self.apply_button)
        editor_group.setLayout(editor_layout)
        
        # Page statistics
        page_stats_group = QGroupBox("Current Page Statistics")
        page_stats_layout = QVBoxLayout()
        
        self.current_page_tables_label = QLabel("Current Page Tables: 0")
        page_stats_layout.addWidget(self.current_page_tables_label)
        page_stats_group.setLayout(page_stats_layout)
        
        # Add to main layout
        layout.addWidget(list_group)
        layout.addWidget(editor_group)
        layout.addWidget(page_stats_group)
        
        editor_widget.setLayout(layout)
        return editor_widget
    
    def update_table_tree(self):
        """Update the table tree widget with all detected tables."""
        self.table_tree.clear()
        
        if not self.coordinates:
            return
        
        # Group coordinates by page
        pages_dict = {}
        for coord in self.coordinates:
            page = coord.get('page', 0)
            if page not in pages_dict:
                pages_dict[page] = []
            pages_dict[page].append(coord)
        
        # Create tree items for each page
        for page_num in sorted(pages_dict.keys()):
            page_item = QTreeWidgetItem([f"Page {page_num + 1}", "", ""])  # Display 1-based to user
            page_item.setData(0, Qt.UserRole, {'type': 'page', 'page': page_num})
            
            # Add tables for this page
            for coord in pages_dict[page_num]:
                coord_id = coord.get('id', -1)
                user_created = coord.get('user_created', False)
                accuracy = coord.get('accuracy', 0)
                
                # Create table item
                table_name = f"Table {coord_id}"
                coords_text = f"[{coord['x1']:.1f}, {coord['y1']:.1f}, {coord['x2']:.1f}, {coord['y2']:.1f}]"
                type_text = "User Created" if user_created else f"Auto ({accuracy:.1f}%)"
                
                table_item = QTreeWidgetItem([table_name, coords_text, type_text])
                table_item.setData(0, Qt.UserRole, {
                    'type': 'table', 
                    'coord_id': coord_id, 
                    'page': page_num,
                    'coordinate': coord
                })
                
                page_item.addChild(table_item)
            
            self.table_tree.addTopLevelItem(page_item)
        
        # Expand all items
        self.table_tree.expandAll()
    
    def on_table_tree_double_click(self, item, column):
        """Handle double-click on table tree item."""
        data = item.data(0, Qt.UserRole)
        if data and data.get('type') == 'table':
            page_num = data.get('page', 0)
            self.page_navigation_requested.emit(page_num)
            
            # Also select the coordinate in the editor
            coord_id = data.get('coord_id')
            if coord_id is not None:
                self.selected_coordinate_id = coord_id
                self.coordinate_selected.emit(coord_id)
        elif data and data.get('type') == 'page':
            page_num = data.get('page', 0)
            self.page_navigation_requested.emit(page_num)
    
    def navigate_previous_table(self):
        """Navigate to the previous table."""
        if not self.coordinates:
            return
        
        # Find current table index
        current_index = -1
        for i, coord in enumerate(self.coordinates):
            if coord.get('id') == self.selected_coordinate_id:
                current_index = i
                break
        
        # Move to previous table
        prev_index = (current_index - 1) % len(self.coordinates)
        prev_coord = self.coordinates[prev_index]
        
        # Navigate to the page and select the table
        page_num = prev_coord.get('page', 0)
        self.page_navigation_requested.emit(page_num)
        self.selected_coordinate_id = prev_coord.get('id')
        self.coordinate_selected.emit(self.selected_coordinate_id)
    
    def navigate_next_table(self):
        """Navigate to the next table."""
        if not self.coordinates:
            return
        
        # Find current table index
        current_index = -1
        for i, coord in enumerate(self.coordinates):
            if coord.get('id') == self.selected_coordinate_id:
                current_index = i
                break
        
        # Move to next table
        next_index = (current_index + 1) % len(self.coordinates)
        next_coord = self.coordinates[next_index]
        
        # Navigate to the page and select the table
        page_num = next_coord.get('page', 0)
        self.page_navigation_requested.emit(page_num)
        self.selected_coordinate_id = next_coord.get('id')
        self.coordinate_selected.emit(self.selected_coordinate_id)
    
    def go_to_selected_table(self):
        """Navigate to the currently selected table in the tree."""
        current_item = self.table_tree.currentItem()
        if current_item:
            self.on_table_tree_double_click(current_item, 0)
    
    def set_coordinates(self, coordinates: List[Dict]):
        """Set the coordinates to edit."""
        self.coordinates = coordinates
        self.update_coordinate_list()
        self.update_statistics()
        self.update_table_tree()
    
    def set_current_page(self, page_num: int):
        """Set the current page number."""
        self.current_page = page_num
        self.update_coordinate_list()
        self.update_statistics()
    
    def update_coordinate_list(self):
        """Update the coordinate list widget."""
        self.coordinate_list.clear()
        
        # Filter coordinates for current page
        page_coordinates = [coord for coord in self.coordinates 
                          if coord.get('page', 0) == self.current_page]
        
        for coord in page_coordinates:
            coord_id = coord.get('id', -1)
            user_created = coord.get('user_created', False)
            accuracy = coord.get('accuracy', 0)
            
            # Create display text
            text = f"Table {coord_id}"
            if user_created:
                text += " (User)"
            else:
                text += f" (Auto, {accuracy:.1f}%)"
            
            text += f" [{coord['x1']:.1f}, {coord['y1']:.1f}, {coord['x2']:.1f}, {coord['y2']:.1f}]"
            
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, coord_id)
            self.coordinate_list.addItem(item)
    
    def update_statistics(self):
        """Update the statistics display."""
        total_tables = len(self.coordinates)
        current_page_tables = len([coord for coord in self.coordinates 
                                 if coord.get('page', 0) == self.current_page])
        user_created = len([coord for coord in self.coordinates 
                          if coord.get('user_created', False)])
        auto_detected = total_tables - user_created
        pages_with_tables = len(set(coord.get('page', 0) for coord in self.coordinates))
        
        # Update navigator tab statistics
        self.total_tables_label.setText(f"Total Tables: {total_tables}")
        self.pages_with_tables_label.setText(f"Pages with Tables: {pages_with_tables}")
        self.auto_detected_label.setText(f"Auto Detected: {auto_detected}")
        self.user_created_label.setText(f"User Created: {user_created}")
        
        # Update editor tab statistics
        self.current_page_tables_label.setText(f"Current Page Tables: {current_page_tables}")
        current_page_tables = len([coord for coord in self.coordinates 
                                 if coord.get('page', 0) == self.current_page])
        user_created = len([coord for coord in self.coordinates 
                          if coord.get('user_created', False)])
        
        self.total_tables_label.setText(f"Total Tables: {total_tables}")
        self.current_page_tables_label.setText(f"Current Page Tables: {current_page_tables}")
        self.user_created_label.setText(f"User Created: {user_created}")
    
    def on_selection_changed(self):
        """Handle selection changes in the coordinate list."""
        current_item = self.coordinate_list.currentItem()
        
        if current_item:
            coord_id = current_item.data(Qt.UserRole)
            self.selected_coordinate_id = coord_id
            self.load_coordinate_to_editor(coord_id)
            self.set_editor_enabled(True)
            self.delete_button.setEnabled(True)
            self.coordinate_selected.emit(coord_id)
        else:
            self.selected_coordinate_id = None
            self.set_editor_enabled(False)
            self.delete_button.setEnabled(False)
    
    def load_coordinate_to_editor(self, coord_id: int):
        """Load a coordinate into the editor."""
        coord = self.find_coordinate_by_id(coord_id)
        if not coord:
            return
        
        # Block signals to prevent triggering updates
        self.x1_spinbox.blockSignals(True)
        self.y1_spinbox.blockSignals(True)
        self.x2_spinbox.blockSignals(True)
        self.y2_spinbox.blockSignals(True)
        self.page_spinbox.blockSignals(True)
        self.user_created_checkbox.blockSignals(True)
        
        # Set values
        self.x1_spinbox.setValue(coord['x1'])
        self.y1_spinbox.setValue(coord['y1'])
        self.x2_spinbox.setValue(coord['x2'])
        self.y2_spinbox.setValue(coord['y2'])
        self.page_spinbox.setValue(coord.get('page', 0))
        self.user_created_checkbox.setChecked(coord.get('user_created', False))
        
        # Update size display
        self.update_size_display()
        
        # Unblock signals
        self.x1_spinbox.blockSignals(False)
        self.y1_spinbox.blockSignals(False)
        self.x2_spinbox.blockSignals(False)
        self.y2_spinbox.blockSignals(False)
        self.page_spinbox.blockSignals(False)
        self.user_created_checkbox.blockSignals(False)
        
        self.apply_button.setEnabled(False)
    
    def coordinate_value_changed(self):
        """Handle changes to coordinate values."""
        self.update_size_display()
        self.apply_button.setEnabled(True)
    
    def update_size_display(self):
        """Update the width and height display."""
        width = abs(self.x2_spinbox.value() - self.x1_spinbox.value())
        height = abs(self.y2_spinbox.value() - self.y1_spinbox.value())
        
        self.width_label.setText(f"{width:.2f}")
        self.height_label.setText(f"{height:.2f}")
    
    def apply_changes(self):
        """Apply changes to the selected coordinate."""
        if self.selected_coordinate_id is None:
            return
        
        # Create updated coordinate data
        updated_data = {
            'x1': min(self.x1_spinbox.value(), self.x2_spinbox.value()),
            'y1': min(self.y1_spinbox.value(), self.y2_spinbox.value()),
            'x2': max(self.x1_spinbox.value(), self.x2_spinbox.value()),
            'y2': max(self.y1_spinbox.value(), self.y2_spinbox.value()),
            'page': self.page_spinbox.value(),
            'user_created': self.user_created_checkbox.isChecked(),
        }
        
        # Calculate derived values
        updated_data['width'] = updated_data['x2'] - updated_data['x1']
        updated_data['height'] = updated_data['y2'] - updated_data['y1']
        
        # Emit signal
        self.coordinate_updated.emit(self.selected_coordinate_id, updated_data)
        
        self.apply_button.setEnabled(False)
    
    def delete_selected(self):
        """Delete the selected coordinate."""
        if self.selected_coordinate_id is None:
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            'Confirm Deletion',
            f'Are you sure you want to delete Table {self.selected_coordinate_id}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.coordinate_deleted.emit(self.selected_coordinate_id)
    
    def create_new_coordinate(self):
        """Create a new coordinate."""
        # Create a default coordinate for the current page
        new_coord = {
            'page': self.current_page,
            'x1': 100,
            'y1': 100,
            'x2': 200,
            'y2': 200,
            'width': 100,
            'height': 100,
            'user_created': True,
            'accuracy': 100.0,
            'whitespace': 0.0
        }
        
        self.coordinate_created.emit(new_coord)
    
    def find_coordinate_by_id(self, coord_id: int) -> Optional[Dict]:
        """Find a coordinate by its ID."""
        for coord in self.coordinates:
            if coord.get('id') == coord_id:
                return coord
        return None
    
    def set_editor_enabled(self, enabled: bool):
        """Enable or disable the coordinate editor."""
        self.x1_spinbox.setEnabled(enabled)
        self.y1_spinbox.setEnabled(enabled)
        self.x2_spinbox.setEnabled(enabled)
        self.y2_spinbox.setEnabled(enabled)
        self.page_spinbox.setEnabled(enabled)
        self.user_created_checkbox.setEnabled(enabled)
        self.apply_button.setEnabled(False)
    
    def select_coordinate(self, coord_id: int):
        """Programmatically select a coordinate."""
        for i in range(self.coordinate_list.count()):
            item = self.coordinate_list.item(i)
            if item.data(Qt.UserRole) == coord_id:
                self.coordinate_list.setCurrentItem(item)
                break
