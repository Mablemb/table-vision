# Table Vision - Installation and Testing Guide

This guide will help you install dependencies, run the application, and execute tests for the Table Vision PDF table extraction tool.

## Installation

### 1. Install Python Dependencies

First, install the core dependencies:

```powershell
# Navigate to the project directory
cd C:\Users\mable\CamelotApp\table-vision

# Install core dependencies (this should work without issues)
pip install -r requirements.txt
```

**Note**: The computer vision extras (`pdftopng`, `ghostscript`) are optional and may have installation issues on Windows. The application will work with just the core dependencies for basic table extraction using the lattice method.

**Alternative Installation (if above fails):**

```powershell
# Install dependencies one by one to avoid conflicts
pip install camelot-py==0.11.0
pip install PyQt5==5.15.9
pip install PyMuPDF==1.23.26
pip install Pillow==10.1.0
pip install numpy==1.24.3
pip install pandas==2.1.3
pip install opencv-python==4.8.1.78
pip install matplotlib==3.8.2

# Skip these if they fail to install - they're not required for basic functionality:
# pip install ghostscript
# pip install pdftopng==0.1.0
```

### 2. Verify Installation

Check that key dependencies are installed correctly:

```powershell
# Test Camelot import
python -c "import camelot; print('Camelot installed successfully')"

# Test PyQt5 import
python -c "import PyQt5.QtWidgets; print('PyQt5 installed successfully')"

# Test PyMuPDF import
python -c "import fitz; print('PyMuPDF installed successfully')"
```

## Running the Application

### Launch the GUI Application

```powershell
# Run the main application
python src/app.py
```

This will open the Table Vision GUI where you can:
1. Load PDF files
2. Extract tables automatically using Camelot with **batch processing**
3. View and edit table boundaries with **persistent zoom**
4. Export table regions as images

### New Features ✨

**Batch Processing**: Tables are now extracted in configurable batches (default: 3 pages at a time), allowing you to review results while extraction continues in the background.

**Persistent Zoom**: The zoom level now persists when navigating between pages, maintaining your preferred view scale.

**Real-time Updates**: See table boundaries appear as each batch completes, no need to wait for the entire document to finish processing.

**Stop/Resume**: Stop extraction at any time and resume later, or work with partial results.

### Command Line Usage

You can also use the application programmatically:

```powershell
# Run the example script
python examples/sample_usage.py
```

## Testing

### Run All Tests

```powershell
# Run the complete test suite
python run_tests.py
```

### Run Specific Test Modules

```powershell
# Test the table extractor
python run_tests.py extractor

# Test coordinate handling
python run_tests.py coordinates

# Test the PDF viewer
python run_tests.py viewer

# Test the image renderer
python run_tests.py renderer
```

### Using Pytest (Alternative)

If you have pytest installed:

```powershell
# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_extractor.py -v
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and paths are set correctly
2. **PDF Loading Issues**: Verify PDF files are not corrupted and accessible
3. **GUI Display Issues**: Check PyQt5 installation and display settings
4. **Camelot Errors**: Ensure OpenCV dependencies are properly installed

### Dependency Issues

If you encounter issues with specific dependencies:

```powershell
# For Camelot computer vision features
pip install "camelot-py[cv]==0.11.0" --force-reinstall

# For PyQt5 issues
pip install PyQt5==5.15.9 --force-reinstall

# For PDF processing issues  
pip install PyMuPDF==1.23.26 --force-reinstall
```

### Environment Verification

Run this comprehensive check:

```powershell
python -c "
import sys
print(f'Python Version: {sys.version}')

try:
    import camelot
    print('✓ Camelot installed')
except:
    print('✗ Camelot not installed')

try:
    import PyQt5
    print('✓ PyQt5 installed')
except:
    print('✗ PyQt5 not installed')

try:
    import fitz
    print('✓ PyMuPDF installed')
except:
    print('✗ PyMuPDF not installed')

try:
    import PIL
    print('✓ Pillow installed')
except:
    print('✗ Pillow not installed')
"
```

## Development

### Running Tests During Development

For continuous testing during development:

```powershell
# Watch for file changes and run tests (requires pytest-watch)
pip install pytest-watch
ptw tests/
```

### Code Coverage

To check test coverage:

```powershell
# Install coverage tools
pip install pytest-cov

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report (opens in browser)
start coverage_html_report/index.html
```

## Example Usage

### Basic PDF Processing

```python
from src.core.extractor import TableExtractor

# Initialize extractor
extractor = TableExtractor()

# Load PDF and extract tables
pdf_path = "your_document.pdf"
tables = extractor.extract_tables(pdf_path)

# Get coordinates
coordinates = extractor.get_coordinates()

print(f"Found {len(tables)} tables")
print(f"Extracted {len(coordinates)} coordinates")
```

### GUI Application

The main GUI application provides:
- Interactive PDF viewing
- Table boundary editing
- Real-time coordinate adjustment
- Batch image export
- Session management

Launch with: `python src/app.py`

## Next Steps

1. **Load a PDF**: Use File → Open to load your PDF document
2. **Configure Batch Size**: Set batch size (1-10 pages) in the toolbar for optimal performance
3. **Extract Tables**: Click "Extract Tables (Batch)" to run Camelot detection with batch processing
4. **Monitor Progress**: Watch as tables appear page by page while extraction continues
5. **Edit Boundaries**: Drag and resize table outlines as needed with persistent zoom
6. **Export Images**: Use "Export All Tables" to save table images
7. **Save Session**: Save your work to continue later

### Batch Processing Tips

- **Small Batch Size (1-2 pages)**: Better for immediate feedback and large documents
- **Medium Batch Size (3-5 pages)**: Good balance between speed and feedback
- **Large Batch Size (6-10 pages)**: Faster processing for smaller documents

- **Stop Anytime**: Use the "Stop Extraction" button to halt processing and work with partial results
- **Zoom Persistence**: Set your preferred zoom level once - it will be maintained across all pages
- **Real-time Review**: Start reviewing and editing tables from early batches while later pages are still processing

For more detailed usage instructions, see the main README.md file.
