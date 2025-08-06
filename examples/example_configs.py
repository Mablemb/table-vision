"""
Example configuration settings for the Table Vision application.
"""

# Default extraction settings
EXTRACTION_CONFIG = {
    "camelot_flavor": "lattice",  # or "stream"
    "line_scale": 15,  # Line scale threshold for lattice method
    "copy_text": True,  # Copy text from table cells
    "split_text": False,  # Split text on whitespace
    "strip_text": "\n",  # Characters to strip from text
    "pages": "all",  # Pages to extract from ("all", "1,2,3", etc.)
    "table_areas": None,  # Specific areas to look for tables
    "columns": None,  # Column separators for stream method
    "password": None,  # PDF password if needed
    "backend": "poppler",  # Backend for PDF processing
    "resolution": 300  # DPI for image processing
}

# Display and UI settings
DISPLAY_CONFIG = {
    "default_zoom": 100,  # Default zoom percentage
    "auto_fit": True,  # Auto-fit PDF to window
    "show_grid": False,  # Show grid overlay
    "grid_size": 20,  # Grid size in pixels
    "outline_color": "#FF0000",  # Default outline color (red)
    "outline_width": 2,  # Default outline width
    "selected_color": "#00FF00",  # Selected outline color (green)
    "background_color": "#FFFFFF",  # Background color
    "show_labels": True,  # Show table ID labels
    "show_accuracy": True,  # Show accuracy percentages
    "animation_enabled": True  # Enable UI animations
}

# Export settings
EXPORT_CONFIG = {
    "default_format": "PNG",  # Default export format
    "default_dpi": 300,  # Default export DPI
    "include_metadata": True,  # Include metadata in exports
    "create_subdirectories": True,  # Create subdirectories by page
    "filename_template": "table_{id}_page{page}_{type}",  # Filename template
    "export_directory": "",  # Default export directory (empty = ask user)
    "overwrite_existing": False,  # Overwrite existing files
    "preserve_aspect_ratio": True,  # Preserve aspect ratio
    "add_margins": False,  # Add margins to exported images
    "margin_size": 10  # Margin size in pixels
}

# Session management settings
SESSION_CONFIG = {
    "auto_save": True,  # Auto-save sessions
    "auto_save_interval": 300,  # Auto-save interval in seconds (5 minutes)
    "max_recent_files": 10,  # Maximum recent files to remember
    "session_directory": "table_vision_data/sessions",  # Session storage directory
    "backup_sessions": True,  # Create session backups
    "max_backups": 5,  # Maximum number of backups to keep
    "compress_sessions": True,  # Compress session files
    "cleanup_old_sessions": True,  # Cleanup old sessions automatically
    "cleanup_days": 30  # Days to keep old sessions
}

# Advanced settings
ADVANCED_CONFIG = {
    "debug_mode": False,  # Enable debug mode
    "log_level": "INFO",  # Logging level
    "log_to_file": True,  # Log to file
    "log_directory": "table_vision_data/logs",  # Log directory
    "performance_monitoring": False,  # Enable performance monitoring
    "memory_limit": 1024,  # Memory limit in MB
    "thread_count": 4,  # Number of threads for processing
    "cache_enabled": True,  # Enable caching
    "cache_size": 100,  # Cache size in MB
    "gpu_acceleration": False,  # Use GPU acceleration if available
    "validate_pdf": True  # Validate PDF files before processing
}

# Keyboard shortcuts
KEYBOARD_SHORTCUTS = {
    "open_file": "Ctrl+O",
    "save_session": "Ctrl+S",
    "save_as": "Ctrl+Shift+S",
    "export_images": "Ctrl+E",
    "extract_tables": "Ctrl+T",
    "zoom_in": "Ctrl++",
    "zoom_out": "Ctrl+-",
    "zoom_fit": "Ctrl+0",
    "previous_page": "Ctrl+Left",
    "next_page": "Ctrl+Right",
    "delete_selection": "Delete",
    "select_all": "Ctrl+A",
    "deselect_all": "Ctrl+D",
    "undo": "Ctrl+Z",
    "redo": "Ctrl+Y",
    "copy": "Ctrl+C",
    "paste": "Ctrl+V",
    "quit": "Ctrl+Q"
}

# Color schemes
COLOR_SCHEMES = {
    "default": {
        "outline_color": "#FF0000",
        "selected_color": "#00FF00",
        "background_color": "#FFFFFF",
        "text_color": "#000000",
        "grid_color": "#CCCCCC"
    },
    "dark": {
        "outline_color": "#FF6666",
        "selected_color": "#66FF66",
        "background_color": "#2B2B2B",
        "text_color": "#FFFFFF",
        "grid_color": "#555555"
    },
    "high_contrast": {
        "outline_color": "#FFFF00",
        "selected_color": "#00FFFF",
        "background_color": "#000000",
        "text_color": "#FFFFFF",
        "grid_color": "#888888"
    }
}

# Quality presets for extraction
QUALITY_PRESETS = {
    "fast": {
        "camelot_flavor": "stream",
        "line_scale": 40,
        "resolution": 150,
        "backend": "poppler"
    },
    "balanced": {
        "camelot_flavor": "lattice",
        "line_scale": 15,
        "resolution": 200,
        "backend": "poppler"
    },
    "high_quality": {
        "camelot_flavor": "lattice",
        "line_scale": 10,
        "resolution": 300,
        "backend": "poppler"
    },
    "maximum": {
        "camelot_flavor": "lattice",
        "line_scale": 5,
        "resolution": 600,
        "backend": "poppler"
    }
}

# File type associations
FILE_ASSOCIATIONS = {
    "pdf": ["*.pdf"],
    "images": ["*.png", "*.jpg", "*.jpeg", "*.tiff", "*.bmp"],
    "data": ["*.json", "*.csv", "*.xlsx"],
    "sessions": ["*.tvs"]  # Table Vision Session files
}

# Default window settings
WINDOW_CONFIG = {
    "width": 1400,
    "height": 900,
    "center_on_screen": True,
    "remember_position": True,
    "remember_size": True,
    "maximized": False,
    "fullscreen": False,
    "splitter_position": [1000, 400],  # Viewer : Editor ratio
    "toolbar_visible": True,
    "statusbar_visible": True,
    "menubar_visible": True
}

# Error handling settings
ERROR_CONFIG = {
    "show_error_dialogs": True,
    "continue_on_error": False,
    "error_log_enabled": True,
    "send_error_reports": False,  # Send anonymous error reports
    "max_error_history": 50,  # Maximum errors to keep in history
    "detailed_error_info": True  # Show detailed error information
}


def get_default_config():
    """Get the complete default configuration."""
    return {
        "extraction": EXTRACTION_CONFIG,
        "display": DISPLAY_CONFIG,
        "export": EXPORT_CONFIG,
        "session": SESSION_CONFIG,
        "advanced": ADVANCED_CONFIG,
        "shortcuts": KEYBOARD_SHORTCUTS,
        "colors": COLOR_SCHEMES,
        "quality": QUALITY_PRESETS,
        "files": FILE_ASSOCIATIONS,
        "window": WINDOW_CONFIG,
        "errors": ERROR_CONFIG
    }


def get_config_for_quality(quality_level):
    """Get configuration for a specific quality level."""
    if quality_level not in QUALITY_PRESETS:
        quality_level = "balanced"
    
    config = EXTRACTION_CONFIG.copy()
    config.update(QUALITY_PRESETS[quality_level])
    return config


def get_color_scheme(scheme_name):
    """Get a specific color scheme."""
    if scheme_name not in COLOR_SCHEMES:
        scheme_name = "default"
    
    return COLOR_SCHEMES[scheme_name]


# Example usage:
if __name__ == "__main__":
    # Print all configuration sections
    config = get_default_config()
    
    print("Table Vision - Configuration Examples")
    print("=" * 50)
    
    for section_name, section_config in config.items():
        print(f"\n{section_name.upper()} SETTINGS:")
        print("-" * 30)
        
        for key, value in section_config.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")
    
    print("\n" + "=" * 50)
    print("To use these configurations in your application:")
    print("1. Import this file: from examples.example_configs import get_default_config")
    print("2. Load config: config = get_default_config()")
    print("3. Access settings: extraction_settings = config['extraction']")
