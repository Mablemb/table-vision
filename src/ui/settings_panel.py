"""
Settings panel for customizing application behavior.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                           QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox,
                           QLabel, QSlider, QPushButton, QFormLayout,
                           QFileDialog, QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
import json
import os


class SettingsPanel(QWidget):
    """Settings panel for application configuration."""
    
    # Signals
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings = self.load_default_settings()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()
        
        # Extraction settings
        extraction_group = QGroupBox("Extraction Settings")
        extraction_layout = QFormLayout()
        
        # Camelot flavor
        self.flavor_combo = QComboBox()
        self.flavor_combo.addItems(["lattice", "stream"])
        self.flavor_combo.setCurrentText(self.settings.get("extraction_flavor", "lattice"))
        
        # Line scale threshold
        self.line_scale_spinbox = QDoubleSpinBox()
        self.line_scale_spinbox.setRange(0.1, 50.0)
        self.line_scale_spinbox.setValue(self.settings.get("line_scale", 15.0))
        self.line_scale_spinbox.setSingleStep(0.1)
        
        # Copy text
        self.copy_text_checkbox = QCheckBox()
        self.copy_text_checkbox.setChecked(self.settings.get("copy_text", True))
        
        # Split text
        self.split_text_checkbox = QCheckBox()
        self.split_text_checkbox.setChecked(self.settings.get("split_text", False))
        
        # Strip text
        self.strip_text_edit = QLineEdit()
        self.strip_text_edit.setText(self.settings.get("strip_text", "\\n"))
        
        extraction_layout.addRow("Camelot Flavor:", self.flavor_combo)
        extraction_layout.addRow("Line Scale:", self.line_scale_spinbox)
        extraction_layout.addRow("Copy Text:", self.copy_text_checkbox)
        extraction_layout.addRow("Split Text:", self.split_text_checkbox)
        extraction_layout.addRow("Strip Text:", self.strip_text_edit)
        extraction_group.setLayout(extraction_layout)
        
        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout()
        
        # Default zoom
        self.zoom_spinbox = QSpinBox()
        self.zoom_spinbox.setRange(25, 500)
        self.zoom_spinbox.setValue(self.settings.get("default_zoom", 100))
        self.zoom_spinbox.setSuffix("%")
        
        # Auto-fit to window
        self.auto_fit_checkbox = QCheckBox()
        self.auto_fit_checkbox.setChecked(self.settings.get("auto_fit", True))
        
        # Show grid
        self.show_grid_checkbox = QCheckBox()
        self.show_grid_checkbox.setChecked(self.settings.get("show_grid", False))
        
        # Grid size
        self.grid_size_spinbox = QSpinBox()
        self.grid_size_spinbox.setRange(5, 100)
        self.grid_size_spinbox.setValue(self.settings.get("grid_size", 20))
        self.grid_size_spinbox.setSuffix(" px")
        
        display_layout.addRow("Default Zoom:", self.zoom_spinbox)
        display_layout.addRow("Auto-fit to Window:", self.auto_fit_checkbox)
        display_layout.addRow("Show Grid:", self.show_grid_checkbox)
        display_layout.addRow("Grid Size:", self.grid_size_spinbox)
        display_group.setLayout(display_layout)
        
        # Export settings
        export_group = QGroupBox("Export Settings")
        export_layout = QFormLayout()
        
        # Default export format
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["PNG", "JPEG", "TIFF", "BMP"])
        self.export_format_combo.setCurrentText(self.settings.get("export_format", "PNG"))
        
        # Export DPI
        self.export_dpi_spinbox = QSpinBox()
        self.export_dpi_spinbox.setRange(72, 600)
        self.export_dpi_spinbox.setValue(self.settings.get("export_dpi", 300))
        
        # Default export directory
        self.export_dir_edit = QLineEdit()
        self.export_dir_edit.setText(self.settings.get("export_directory", ""))
        
        self.browse_dir_btn = QPushButton("Browse...")
        self.browse_dir_btn.clicked.connect(self.browse_export_directory)
        
        export_dir_layout = QHBoxLayout()
        export_dir_layout.addWidget(self.export_dir_edit)
        export_dir_layout.addWidget(self.browse_dir_btn)
        
        # Include metadata in export
        self.include_metadata_checkbox = QCheckBox()
        self.include_metadata_checkbox.setChecked(self.settings.get("include_metadata", True))
        
        export_layout.addRow("Export Format:", self.export_format_combo)
        export_layout.addRow("Export DPI:", self.export_dpi_spinbox)
        export_layout.addRow("Export Directory:", export_dir_layout)
        export_layout.addRow("Include Metadata:", self.include_metadata_checkbox)
        export_group.setLayout(export_layout)
        
        # Advanced settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout()
        
        # Auto-save session
        self.auto_save_checkbox = QCheckBox()
        self.auto_save_checkbox.setChecked(self.settings.get("auto_save", True))
        
        # Auto-save interval
        self.auto_save_interval_spinbox = QSpinBox()
        self.auto_save_interval_spinbox.setRange(1, 60)
        self.auto_save_interval_spinbox.setValue(self.settings.get("auto_save_interval", 5))
        self.auto_save_interval_spinbox.setSuffix(" min")
        
        # Maximum recent files
        self.max_recent_spinbox = QSpinBox()
        self.max_recent_spinbox.setRange(1, 20)
        self.max_recent_spinbox.setValue(self.settings.get("max_recent_files", 10))
        
        # Debug mode
        self.debug_mode_checkbox = QCheckBox()
        self.debug_mode_checkbox.setChecked(self.settings.get("debug_mode", False))
        
        advanced_layout.addRow("Auto-save Session:", self.auto_save_checkbox)
        advanced_layout.addRow("Auto-save Interval:", self.auto_save_interval_spinbox)
        advanced_layout.addRow("Max Recent Files:", self.max_recent_spinbox)
        advanced_layout.addRow("Debug Mode:", self.debug_mode_checkbox)
        advanced_group.setLayout(advanced_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.clicked.connect(self.apply_settings)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        
        self.load_btn = QPushButton("Load Settings")
        self.load_btn.clicked.connect(self.load_settings)
        
        buttons_layout.addWidget(self.apply_btn)
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.load_btn)
        
        # Add all groups to main layout
        layout.addWidget(extraction_group)
        layout.addWidget(display_group)
        layout.addWidget(export_group)
        layout.addWidget(advanced_group)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def load_default_settings(self) -> dict:
        """Load default settings."""
        return {
            # Extraction settings
            "extraction_flavor": "lattice",
            "line_scale": 15.0,
            "copy_text": True,
            "split_text": False,
            "strip_text": "\\n",
            
            # Display settings
            "default_zoom": 100,
            "auto_fit": True,
            "show_grid": False,
            "grid_size": 20,
            
            # Export settings
            "export_format": "PNG",
            "export_dpi": 300,
            "export_directory": "",
            "include_metadata": True,
            
            # Advanced settings
            "auto_save": True,
            "auto_save_interval": 5,
            "max_recent_files": 10,
            "debug_mode": False
        }
    
    def browse_export_directory(self):
        """Browse for export directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Choose Export Directory"
        )
        if directory:
            self.export_dir_edit.setText(directory)
    
    def apply_settings(self):
        """Apply current settings."""
        self.settings = {
            # Extraction settings
            "extraction_flavor": self.flavor_combo.currentText(),
            "line_scale": self.line_scale_spinbox.value(),
            "copy_text": self.copy_text_checkbox.isChecked(),
            "split_text": self.split_text_checkbox.isChecked(),
            "strip_text": self.strip_text_edit.text(),
            
            # Display settings
            "default_zoom": self.zoom_spinbox.value(),
            "auto_fit": self.auto_fit_checkbox.isChecked(),
            "show_grid": self.show_grid_checkbox.isChecked(),
            "grid_size": self.grid_size_spinbox.value(),
            
            # Export settings
            "export_format": self.export_format_combo.currentText(),
            "export_dpi": self.export_dpi_spinbox.value(),
            "export_directory": self.export_dir_edit.text(),
            "include_metadata": self.include_metadata_checkbox.isChecked(),
            
            # Advanced settings
            "auto_save": self.auto_save_checkbox.isChecked(),
            "auto_save_interval": self.auto_save_interval_spinbox.value(),
            "max_recent_files": self.max_recent_spinbox.value(),
            "debug_mode": self.debug_mode_checkbox.isChecked()
        }
        
        self.settings_changed.emit(self.settings)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = self.load_default_settings()
        self.update_ui_from_settings()
    
    def update_ui_from_settings(self):
        """Update UI controls from current settings."""
        # Extraction settings
        self.flavor_combo.setCurrentText(self.settings.get("extraction_flavor", "lattice"))
        self.line_scale_spinbox.setValue(self.settings.get("line_scale", 15.0))
        self.copy_text_checkbox.setChecked(self.settings.get("copy_text", True))
        self.split_text_checkbox.setChecked(self.settings.get("split_text", False))
        self.strip_text_edit.setText(self.settings.get("strip_text", "\\n"))
        
        # Display settings
        self.zoom_spinbox.setValue(self.settings.get("default_zoom", 100))
        self.auto_fit_checkbox.setChecked(self.settings.get("auto_fit", True))
        self.show_grid_checkbox.setChecked(self.settings.get("show_grid", False))
        self.grid_size_spinbox.setValue(self.settings.get("grid_size", 20))
        
        # Export settings
        self.export_format_combo.setCurrentText(self.settings.get("export_format", "PNG"))
        self.export_dpi_spinbox.setValue(self.settings.get("export_dpi", 300))
        self.export_dir_edit.setText(self.settings.get("export_directory", ""))
        self.include_metadata_checkbox.setChecked(self.settings.get("include_metadata", True))
        
        # Advanced settings
        self.auto_save_checkbox.setChecked(self.settings.get("auto_save", True))
        self.auto_save_interval_spinbox.setValue(self.settings.get("auto_save_interval", 5))
        self.max_recent_spinbox.setValue(self.settings.get("max_recent_files", 10))
        self.debug_mode_checkbox.setChecked(self.settings.get("debug_mode", False))
    
    def save_settings(self):
        """Save settings to file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Save Settings", "table_vision_settings.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.settings, f, indent=2)
            except Exception as e:
                print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load settings from file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Load Settings", "",
            "JSON Files (*.json)"
        )
        
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                self.settings.update(loaded_settings)
                self.update_ui_from_settings()
                
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def get_settings(self) -> dict:
        """Get current settings."""
        return self.settings.copy()
