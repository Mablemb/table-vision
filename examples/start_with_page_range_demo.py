#!/usr/bin/env python3
"""
Quick visual test for the page range feature.
This script starts the application and automatically loads a test configuration.
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Start the application for visual testing."""
    from PyQt5.QtWidgets import QApplication
    from ui.main_window import MainWindow
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Table Vision - Page Range Test")
    
    # Create main window
    window = MainWindow()
    
    # Set test configuration to demonstrate page range feature
    window.all_pages_checkbox.setChecked(False)
    window.start_page_input.setValue(5)
    window.end_page_input.setValue(15)
    window.batch_size_spinbox.setValue(3)
    
    # Show window
    window.show()
    
    # Display feature information
    from PyQt5.QtWidgets import QMessageBox
    QMessageBox.information(
        window,
        "Page Range Feature Demo",
        "Page Range Selection Feature is now active!\n\n"
        "New Features:\n"
        "• Select specific page ranges (From/To)\n"
        "• Toggle between 'All Pages' and custom ranges\n"
        "• Efficient batch processing for selected pages\n"
        "• Progress tracking for selected ranges\n\n"
        "Demo Configuration:\n"
        "• Range: Pages 5-15\n"
        "• Batch Size: 3 pages\n\n"
        "Load a PDF and click 'Extract Tables' to test!"
    )
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    print("Starting Table Vision with Page Range Feature...")
    print("=" * 50)
    print("Features Available:")
    print("• Page range selection (start and end pages)")
    print("• Efficient batch processing")
    print("• Progress tracking for selected ranges")
    print("• Validation and error handling")
    print("=" * 50)
    
    main()
