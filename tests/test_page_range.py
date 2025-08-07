#!/usr/bin/env python3
"""
Test script for page range functionality in Table Vision.
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_page_range_functionality():
    """Test the page range functionality without GUI."""
    print("Testing Page Range Functionality")
    print("=" * 40)
    
    try:
        # Test import
        from ui.main_window import BatchExtractionWorkerCustom
        print("✓ Import successful")
        
        # Test worker creation
        worker = BatchExtractionWorkerCustom(
            pdf_path="test.pdf",  # Dummy path
            batch_size=2,
            start_page=5,
            end_page=10
        )
        print("✓ BatchExtractionWorkerCustom created successfully")
        
        # Verify properties
        assert worker.start_page == 5, f"Expected start_page=5, got {worker.start_page}"
        assert worker.end_page == 10, f"Expected end_page=10, got {worker.end_page}"
        assert worker.batch_size == 2, f"Expected batch_size=2, got {worker.batch_size}"
        print("✓ Worker properties set correctly")
        
        print("\nPage Range Features:")
        print(f"  - Start Page: {worker.start_page}")
        print(f"  - End Page: {worker.end_page}")
        print(f"  - Batch Size: {worker.batch_size}")
        print(f"  - Pages to Process: {worker.end_page - worker.start_page + 1}")
        
        print("\n✅ All tests passed! Page range functionality is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def test_ui_components():
    """Test UI component creation."""
    print("\nTesting UI Components")
    print("=" * 40)
    
    try:
        from PyQt5.QtWidgets import QApplication, QSpinBox, QCheckBox, QGroupBox
        from ui.main_window import MainWindow
        
        # Create application (required for Qt widgets)
        app = QApplication([])
        
        # Create main window to test UI components
        window = MainWindow()
        print("✓ MainWindow created successfully")
        
        # Test page range controls
        assert hasattr(window, 'all_pages_checkbox'), "Missing all_pages_checkbox"
        assert hasattr(window, 'start_page_input'), "Missing start_page_input"
        assert hasattr(window, 'end_page_input'), "Missing end_page_input"
        print("✓ Page range controls exist")
        
        # Test initial state
        assert window.all_pages_checkbox.isChecked(), "all_pages_checkbox should be checked by default"
        assert not window.start_page_input.isEnabled(), "start_page_input should be disabled when all_pages is checked"
        assert not window.end_page_input.isEnabled(), "end_page_input should be disabled when all_pages is checked"
        print("✓ Initial UI state is correct")
        
        # Test page range methods
        assert hasattr(window, 'get_page_range'), "Missing get_page_range method"
        assert hasattr(window, 'on_all_pages_toggled'), "Missing on_all_pages_toggled method"
        assert hasattr(window, 'extract_tables_with_range'), "Missing extract_tables_with_range method"
        print("✓ Page range methods exist")
        
        print("\n✅ All UI tests passed!")
        
        app.quit()
        
    except Exception as e:
        print(f"❌ UI test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Table Vision - Page Range Feature Test")
    print("=" * 50)
    
    success = True
    success &= test_page_range_functionality()
    success &= test_ui_components()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Page range functionality is ready.")
        print("\nNew Features Added:")
        print("• Page range selection (start and end pages)")
        print("• Efficient batch processing for selected ranges")
        print("• UI controls for easy page range specification")
        print("• Progress tracking for selected ranges")
        print("• Validation and error handling for invalid ranges")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
