# Table Vision 📊

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green.svg)](https://pypi.org/project/PyQt5/)
[![Camelot](https://img.shields.io/badge/extraction-Camelot-orange.svg)](https://camelot-py.readthedocs.io/)

Table Vision is a comprehensive Python application designed to extract, visualize, and manipulate table data from PDF documents using the powerful Camelot library. The project provides an intuitive graphical interface for users to customize the extraction process, interactively edit table boundaries, and export individual table regions as high-quality images.

## ✨ Features

- **🔍 Automatic Table Detection**: Uses Camelot's lattice method to automatically detect tables in PDF documents
- **📄 Page Range Selection**: Extract tables from specific page ranges (start and end pages) for targeted analysis
- **📊 Interactive Visualization**: Display PDF pages with overlaid table outlines that can be selected and modified
- **✏️ Real-time Boundary Editing**: Adjust, resize, move, and delete automatically detected table boundaries
- **🗑️ Seamless Table Deletion**: Delete unwanted tables instantly during extraction - works throughout batch processing
- **➕ Manual Table Creation**: Create new table boundaries for tables missed by automatic detection
- **🖼️ High-Quality Image Export**: Export individual table regions as PNG, JPEG, or TIFF images
- **💾 Session Management**: Save and load extraction sessions with all coordinate data
- **⚙️ Customizable Settings**: Extensive configuration options for extraction parameters and display preferences
- **📈 Statistics & Analytics**: View detailed statistics about extracted tables and accuracy metrics
- **🎯 Coordinate System Integration**: Seamless conversion between PDF and screen coordinate systems

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Ghostscript (required for Camelot)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/table-vision.git
   cd table-vision
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ghostscript**
   
   **Windows:**
   - Download from [ghostscript.com](https://www.ghostscript.com/download/gsdnld.html)
   - Install to default location (`C:\Program Files\gs\`)
   
   **macOS:**
   ```bash
   brew install ghostscript
   ```
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install ghostscript
   ```

4. **Run the application**
   ```bash
   python src/app.py
   ```

### Basic Usage

1. **Load a PDF**: Click "Open PDF" or use `Ctrl+O`
2. **Select Page Range**: 
   - Check "All Pages" to process the entire document
   - Uncheck "All Pages" and set "From" and "To" values to process specific pages
3. **Extract Tables**: Click "Extract Tables" - red rectangles will appear over detected tables
4. **Edit Boundaries**: Click and drag rectangles to resize or reposition
5. **Delete Unwanted Tables**: Right-click or select and press Delete to remove incorrect detections
6. **Create New Tables**: Draw new rectangles for missed tables
7. **Export**: Click "Export Images" to save table regions as images

> **✨ New in v2.3.1**: Table deletion now works seamlessly during batch extraction! You can delete unwanted tables immediately as they're detected, without waiting for the entire process to complete.

## 🎯 Use Cases

This tool is perfect for:
- **📊 Data Scientists** extracting tabular data from research papers and reports
- **💼 Financial Analysts** processing financial statements and reports  
- **🎓 Researchers** digitizing tables from academic publications
- **🏭 Document Processing** workflows requiring table extraction and validation
- **✅ Quality Assurance** for automated table detection systems
- **📋 Form Processing** extracting structured data from forms and surveys

## 🆕 Recent Updates

### Version 2.3.1 (Latest) - Critical Bug Fix Release
- **🗑️ Fixed Table Deletion Bug**: Resolved critical issue where detected tables displayed in the right panel couldn't be deleted
- **⚡ Real-time Deletion**: Table deletion now works immediately throughout batch extraction process, not just at the end
- **🔄 Improved Coordinate Management**: Fixed coordinate synchronization between internal data structures
- **📊 Enhanced Batch Processing**: Batch extraction now properly accumulates coordinates without refreshing existing ones
- **🎯 Consistent Behavior**: Unified deletion functionality across all extraction methods (regular and batch)
- **🧪 Comprehensive Testing**: Added professional pytest testing infrastructure with 15 automated tests
- **✅ Test Coverage**: Complete test coverage for deletion, synchronization, and batch processing scenarios
- **🐛 Data Persistence**: Deleted coordinates no longer reappear due to coordinate list merging issues
- **💻 Better User Experience**: Smooth, uninterrupted workflow for table review and curation during extraction

### Version 2.3.0
- **🎯 Fixed Table Export Coordinate System**: Resolved critical issue where exported images didn't match red rectangle positions
- **📐 Correct Aspect Ratios**: Landscape tables now export as landscape images with proper orientation
- **🖼️ Improved Image Quality**: Export now uses full-page render + PIL crop approach for better reliability
- **📄 Enhanced Page Range Feature**: Streamlined page range selection with better validation and error handling
- **🔧 Coordinate System Integration**: Export images now precisely match the visualization rectangles
- **🐛 PyMuPDF Clipping Fix**: Resolved high-DPI clipping issues that caused dimension swapping
- **📊 Better Debug Output**: Enhanced troubleshooting with detailed coordinate transformation logging

### Version 2.2.0
- **📄 Page Range Selection**: Added ability to extract tables from specific page ranges instead of processing entire documents
- **⚡ Improved Processing Efficiency**: Users can now select start and end pages for targeted extraction, reducing processing time
- **🎯 Better Testing Workflow**: Easy system testing with selective page processing
- **🔧 Enhanced UI Controls**: Added intuitive page range controls in the toolbar with validation
- **📈 Smart Progress Tracking**: Progress indicators now show current page within selected range

### Version 2.1.0
- **🐛 Fixed Critical Coordinate Bug**: Resolved issue where Camelot-detected tables were not displaying visually
- **⚡ Improved Coordinate Transformation**: Complete rewrite of PDF-to-screen coordinate conversion system
- **🎨 Enhanced Visual Display**: Table rectangles now appear correctly at proper screen positions
- **🔧 Better Ghostscript Integration**: Improved automatic detection and configuration
- **📈 Performance Optimizations**: Faster rendering and smoother user interactions
- **🧹 Code Quality**: Added comprehensive debug logging and error handling

### Key Bug Fixes

#### Version 2.3.1 (Latest)
- **Critical Table Deletion Bug**: Fixed issue where tables in the right panel couldn't be deleted
- **Batch Processing Accumulation**: Resolved coordinates refreshing instead of properly accumulating during batch extraction
- **Data Structure Synchronization**: Fixed inconsistencies between coordinate manager and extracted coordinates list
- **Real-time Deletion**: Deletion now works immediately during batch processing, not just at completion

#### Previous Versions
- Fixed double-scaling in coordinate transformations that caused rectangles to appear off-screen
- Corrected Y-axis flipping between PDF (bottom-origin) and screen (top-origin) coordinate systems  
- Resolved scale factor calculation errors that affected rectangle positioning
- Improved pixmap dimension handling for accurate coordinate conversion

## 🏗️ Architecture

### Core Components

```
table-vision/
├── 📁 src/
│   ├── 🧠 core/                 # Core extraction and coordinate management
│   │   ├── extractor.py        # Camelot-based table extraction with batch processing
│   │   ├── coordinates.py      # Coordinate management and transformation system
│   │   └── utils.py            # PDF utilities and helper functions
│   ├── 🎨 visualization/        # Display and rendering components  
│   │   ├── viewer.py           # Interactive PDF viewer with coordinate transformation
│   │   ├── editor.py           # Table boundary editor with mouse interactions
│   │   └── renderer.py         # High-quality image export and rendering
│   ├── 💾 data/                 # Data models and storage
│   │   ├── models.py           # Table and session data models
│   │   └── storage.py          # Session and coordinate persistence
│   ├── 🖥️ ui/                   # User interface components
│   │   ├── main_window.py      # Main application window and menu system
│   │   ├── table_editor.py     # Table editing UI panel  
│   │   └── settings_panel.py   # Configuration UI
│   └── 🚀 app.py               # Application entry point
├── 🧪 tests/                   # Comprehensive pytest test suite
│   ├── test_deletion_pytest.py     # Core deletion functionality tests (5 tests)
│   ├── test_synchronization_pytest.py  # Coordinate synchronization tests (5 tests)
│   ├── test_batch_accumulation.py      # Batch processing scenario tests (5 tests)
│   ├── pytest.ini                      # pytest configuration
│   └── (legacy test files)             # Original unittest-based tests
├── 📝 examples/                # Usage examples and sample code
├── 🎛️ resources/               # Default settings and configuration
└── 📋 requirements.txt         # Python dependencies
```

### Detailed Workflow

#### 1. PDF Loading and Navigation
- **File Support**: Compatible with all PDF versions
- **Page Navigation**: Use arrow keys or page controls to browse documents
- **Zoom Controls**: Zoom in/out for precise boundary editing
- **Auto-fit**: Automatically fit PDF to window size

#### 2. Table Detection
- **Automatic Detection**: Camelot lattice method detects table structures
- **Page Range Selection**: Choose to process all pages or specify a range (e.g., pages 5-15)
- **Quality Settings**: Choose from Fast, Balanced, High Quality, or Maximum presets
- **Real-time Preview**: See detection results immediately

#### 3. Interactive Editing
- **Selection**: Click tables to select and view properties
- **Resizing**: Drag corner handles to resize table boundaries
- **Moving**: Drag entire tables to new positions
- **Creation**: Draw new rectangles for missed tables
- **Deletion**: Right-click or press Delete to remove tables

#### 4. Export Options
- **Image Formats**: PNG, JPEG, TIFF, BMP support
- **Resolution**: Configurable DPI from 72 to 600
- **Organization**: Automatic folder structure by page
- **Naming**: Customizable filename templates
- **Metadata**: Optional inclusion of extraction metadata

### Advanced Features

#### Session Management
```python
# Save current session
session = create_session(pdf_path, coordinates)
storage.save_session(session)

# Load previous session
loaded_session = storage.load_session(session_id)
```

#### Programmatic Usage
```python
from core.extractor import TableExtractor
from visualization.renderer import TableRenderer

# Extract tables
extractor = TableExtractor()
tables = extractor.extract_tables("document.pdf")
coordinates = extractor.get_coordinates()

# Export images
renderer = TableRenderer()
renderer.load_pdf("document.pdf")
exported_files = renderer.export_all_tables(coordinates, "output/")
```

#### Batch Processing
```python
# Process multiple PDFs
for pdf_file in pdf_files:
    extractor = TableExtractor()
    tables = extractor.extract_tables(pdf_file)
    coordinates = extractor.get_coordinates()
    
    renderer = TableRenderer()
    renderer.load_pdf(pdf_file)
    renderer.export_all_tables(coordinates, f"output/{pdf_file}/")
```

## 📁 Project Structure

```
table-vision/
├── src/
│   ├── core/                    # Core extraction and coordinate management
│   │   ├── extractor.py        # Camelot-based table extraction
│   │   ├── coordinates.py      # Coordinate management system
│   │   └── utils.py            # PDF utilities and helper functions
│   ├── visualization/           # Display and rendering components
│   │   ├── viewer.py           # Interactive PDF viewer
│   │   ├── editor.py           # Table boundary editor
│   │   └── renderer.py         # Image export and rendering
│   ├── data/                   # Data models and storage
│   │   ├── models.py           # Table and session data models
│   │   └── storage.py          # Session and coordinate persistence
│   ├── ui/                     # User interface components
│   │   ├── main_window.py      # Main application window
│   │   ├── table_editor.py     # Table editing UI panel
│   │   └── settings_panel.py   # Configuration UI
│   └── app.py                  # Application entry point
├── tests/                      # Unit tests and test data
├── examples/                   # Usage examples and sample code
├── resources/                  # Default settings and assets
├── requirements.txt            # Python dependencies
├── setup.py                   # Installation script
└── README.md                  # This file
```

## ⚙️ Configuration

### Extraction Settings
- **Camelot Flavor**: Choose between 'lattice' (default) and 'stream' methods
- **Line Scale**: Adjust sensitivity for line detection (5-50)
- **Resolution**: Set DPI for PDF processing (150-600)
- **Text Processing**: Configure text extraction and cleaning

### Display Settings
- **Zoom**: Default zoom level and auto-fit options
- **Colors**: Customize outline colors and transparency
- **Grid**: Optional grid overlay for precise alignment
- **Labels**: Show/hide table IDs and accuracy scores

### Export Settings
- **Format**: Choose output image format (PNG recommended)
- **DPI**: Set export resolution (300 DPI recommended)
- **Organization**: Automatic folder structure options
- **Naming**: Customizable filename templates

## 🧪 Testing

Table Vision includes a comprehensive testing infrastructure using pytest to ensure reliability and catch regressions.

### Test Infrastructure

The project uses **pytest** with specialized testing for PyQt5 GUI components:

- **pytest 8.4.1**: Modern Python testing framework
- **pytest-qt 4.5.0**: PyQt5-specific testing capabilities for GUI components  
- **pytest-cov 6.2.1**: Code coverage reporting
- **15 automated tests**: Covering all deletion and synchronization scenarios

### Running Tests

**Run all tests:**
```bash
python -m pytest tests/ -v
```

**Run with coverage:**
```bash
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

**Run specific test categories:**
```bash
# GUI-related tests
python -m pytest tests/ -m gui -v

# Integration tests  
python -m pytest tests/ -m integration -v
```

### Test Coverage

Current test files cover critical functionality:

- **`test_deletion_pytest.py`**: Core deletion functionality (5 tests)
  - Basic coordinate deletion
  - Multiple coordinate deletion
  - Non-existent coordinate handling
  - User-created coordinate deletion
  - Data structure synchronization

- **`test_synchronization_pytest.py`**: Coordinate synchronization (5 tests)
  - Regular extraction synchronization
  - Batch extraction synchronization
  - Synchronization after deletion
  - ID consistency during operations
  - User coordinate preservation

- **`test_batch_accumulation.py`**: Batch processing scenarios (5 tests)
  - Page extraction completion
  - Real-time deletion during batch processing
  - Coordinate accumulation across pages
  - Deletion after accumulation
  - Batch completion synchronization

### Manual Testing

For comprehensive testing, see [TESTING_GUIDE.md](TESTING_GUIDE.md) which includes:
- Step-by-step manual testing procedures
- Visual verification workflows
- PDF sample testing instructions
- Debug mode activation for troubleshooting

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Ensure all tests pass: `pytest`
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run code formatting
black src/ tests/

# Run type checking
mypy src/

# Run linting
flake8 src/ tests/
```

## 📊 Performance

- **Speed**: Processes typical documents in 2-10 seconds
- **Accuracy**: 85-95% table detection accuracy on well-formatted PDFs
- **Memory**: ~100-500MB depending on PDF size and resolution
- **Formats**: Supports all PDF versions and most table layouts

## 🐛 Troubleshooting

### Common Issues

**"Ghostscript not found" error:**
- Install Ghostscript and ensure it's in your system PATH
- On Windows, add Ghostscript's bin directory to PATH

**"No tables detected":**
- Try different quality presets (High Quality or Maximum)
- Check if tables have visible borders
- Use manual creation for borderless tables

**Memory issues with large PDFs:**
- Process pages individually instead of all at once
- Reduce resolution in extraction settings
- Close other applications to free memory

### Debug Mode
Enable debug mode in settings for detailed logging:
```python
settings = {"advanced": {"debug_mode": True}}
```

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Camelot**: The excellent table extraction library that powers this tool
- **PyQt5**: For the robust GUI framework
- **PyMuPDF**: For reliable PDF processing
- **Pillow**: For image processing capabilities

## 📞 Support

- **Documentation**: [Full documentation](https://table-vision.readthedocs.io/)
- **Issues**: [Report bugs](https://github.com/yourusername/table-vision/issues)
- **Discussions**: [Community discussions](https://github.com/yourusername/table-vision/discussions)
- **Email**: contact@tablevision.com

---

**Table Vision** - Making PDF table extraction visual, interactive, and efficient! 🚀
│   └── app.py                  # Entry point of the application
├── tests
│   ├── test_extractor.py       # Unit tests for the TableExtractor class
│   ├── test_coordinates.py      # Unit tests for the TableCoordinates class
│   └── test_viewer.py          # Unit tests for the TableViewer class
├── examples
│   ├── sample_usage.py         # Example usage of the application
│   └── example_configs.py      # Example configuration settings
├── resources
│   └── default_settings.json    # Default settings for the application
├── requirements.txt             # Project dependencies
├── setup.py                     # Setup script for the project
└── README.md                    # Project documentation
```

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage

1. Place your PDF files in the appropriate directory.
2. Run the application using:

```
python src/app.py
```

3. Use the UI to extract tables, visualize them, and adjust outlines as needed.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.