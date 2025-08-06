"""
Table editor UI for editing table outlines and properties.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
                           QCheckBox, QComboBox, QLabel, QSlider, QColorDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from typing import Dict, Optional


class TableEditorPanel(QWidget):
    """Advanced table editor panel with additional editing tools."""
    
    # Signals
    outline_color_changed = pyqtSignal(QColor)
    outline_width_changed = pyqtSignal(int)
    selection_mode_changed = pyqtSignal(str)
    snap_to_grid_changed = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Selection tools
        selection_group = QGroupBox("Selection Tools")
        selection_layout = QVBoxLayout()
        
        self.selection_mode_combo = QComboBox()
        self.selection_mode_combo.addItems([
            "Single Selection",
            "Multiple Selection",
            "Area Selection"
        ])
        self.selection_mode_combo.currentTextChanged.connect(
            lambda text: self.selection_mode_changed.emit(text)
        )
        
        selection_layout.addWidget(QLabel("Selection Mode:"))
        selection_layout.addWidget(self.selection_mode_combo)
        selection_group.setLayout(selection_layout)
        
        # Drawing tools
        drawing_group = QGroupBox("Drawing Tools")
        drawing_layout = QFormLayout()
        
        # Outline color
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 30)
        self.color_button.setStyleSheet("background-color: red")
        self.color_button.clicked.connect(self.choose_color)
        
        # Outline width
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setRange(1, 10)
        self.width_slider.setValue(2)
        self.width_slider.valueChanged.connect(
            lambda value: self.outline_width_changed.emit(value)
        )
        
        self.width_label = QLabel("2")
        width_layout = QHBoxLayout()
        width_layout.addWidget(self.width_slider)
        width_layout.addWidget(self.width_label)
        
        self.width_slider.valueChanged.connect(
            lambda value: self.width_label.setText(str(value))
        )
        
        # Snap to grid
        self.snap_checkbox = QCheckBox("Snap to Grid")
        self.snap_checkbox.stateChanged.connect(
            lambda state: self.snap_to_grid_changed.emit(state == Qt.Checked)
        )
        
        drawing_layout.addRow("Outline Color:", self.color_button)
        drawing_layout.addRow("Outline Width:", width_layout)
        drawing_layout.addRow(self.snap_checkbox)
        drawing_group.setLayout(drawing_layout)
        
        # Adjustment tools
        adjustment_group = QGroupBox("Fine Adjustments")
        adjustment_layout = QVBoxLayout()
        
        # Nudge controls
        nudge_layout = QHBoxLayout()
        
        self.nudge_up_btn = QPushButton("↑")
        self.nudge_down_btn = QPushButton("↓")
        self.nudge_left_btn = QPushButton("←")
        self.nudge_right_btn = QPushButton("→")
        
        for btn in [self.nudge_up_btn, self.nudge_down_btn, 
                   self.nudge_left_btn, self.nudge_right_btn]:
            btn.setFixedSize(30, 30)
        
        nudge_layout.addWidget(self.nudge_left_btn)
        nudge_layout.addWidget(self.nudge_up_btn)
        nudge_layout.addWidget(self.nudge_down_btn)
        nudge_layout.addWidget(self.nudge_right_btn)
        
        # Nudge amount
        self.nudge_spinbox = QSpinBox()
        self.nudge_spinbox.setRange(1, 50)
        self.nudge_spinbox.setValue(5)
        self.nudge_spinbox.setSuffix(" px")
        
        adjustment_layout.addWidget(QLabel("Nudge Controls:"))
        adjustment_layout.addLayout(nudge_layout)
        adjustment_layout.addWidget(QLabel("Nudge Amount:"))
        adjustment_layout.addWidget(self.nudge_spinbox)
        adjustment_group.setLayout(adjustment_layout)
        
        # Batch operations
        batch_group = QGroupBox("Batch Operations")
        batch_layout = QVBoxLayout()
        
        self.align_left_btn = QPushButton("Align Left")
        self.align_right_btn = QPushButton("Align Right")
        self.align_top_btn = QPushButton("Align Top")
        self.align_bottom_btn = QPushButton("Align Bottom")
        self.distribute_h_btn = QPushButton("Distribute Horizontally")
        self.distribute_v_btn = QPushButton("Distribute Vertically")
        
        batch_layout.addWidget(self.align_left_btn)
        batch_layout.addWidget(self.align_right_btn)
        batch_layout.addWidget(self.align_top_btn)
        batch_layout.addWidget(self.align_bottom_btn)
        batch_layout.addWidget(self.distribute_h_btn)
        batch_layout.addWidget(self.distribute_v_btn)
        batch_group.setLayout(batch_layout)
        
        # Add all groups to main layout
        layout.addWidget(selection_group)
        layout.addWidget(drawing_group)
        layout.addWidget(adjustment_group)
        layout.addWidget(batch_group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def choose_color(self):
        """Open color chooser dialog."""
        color = QColorDialog.getColor(QColor(255, 0, 0), self)
        if color.isValid():
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
            self.outline_color_changed.emit(color)
