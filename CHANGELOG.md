# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-08-06

### 🐛 Fixed
- **Critical Bug**: Fixed Camelot-detected tables not displaying visually on screen
- **Coordinate System**: Completely rewritten coordinate transformation logic in `viewer.py`
- **Double Scaling**: Resolved issue where scale factors were applied twice, causing rectangles to appear off-screen
- **Y-axis Flipping**: Corrected transformation between PDF bottom-left origin and screen top-left origin coordinate systems
- **Rectangle Positioning**: Fixed calculation of screen coordinates for proper visual overlay of table boundaries

### ⚡ Improved
- **Performance**: Optimized coordinate transformation calculations for faster rendering
- **Debug Logging**: Added comprehensive debug output for coordinate conversion troubleshooting
- **Error Handling**: Enhanced error handling in coordinate transformation methods
- **Code Quality**: Improved code documentation and inline comments

### 🔧 Technical Details
- Simplified coordinate transformation from complex double-scaling to clear two-step process
- Fixed `_coord_to_screen_rect()` method to properly handle PDF page dimensions
- Corrected `_screen_to_coord_rect()` method for accurate reverse transformations
- Updated coordinate calculation to account for 2x rendering scale and viewer zoom separately

### 📊 Before/After
- **Before**: `QRect(532, 1553, 49, 110)` - Y coordinate 1553 was off-screen (pixmap height: 1682)
- **After**: `QRect(544, 507, 54, 122)` - Properly positioned within visible screen bounds

## [2.0.0] - 2025-07-15

### ✨ Added
- Interactive PDF viewer with table overlay system
- Real-time table boundary editing with mouse interactions
- Batch table extraction with progress tracking
- Session management for saving/loading extraction results
- High-quality image export functionality
- Comprehensive settings panel for customization

### 🔧 Technical
- PyQt5-based GUI framework implementation
- Camelot integration for automatic table detection
- PyMuPDF for PDF rendering and processing
- Coordinate management system for table boundaries

## [1.0.0] - 2025-06-01

### ✨ Initial Release
- Basic table extraction using Camelot library
- Command-line interface for PDF processing
- Simple coordinate extraction and storage
- Ghostscript integration for PDF processing

---

## Contributing

When contributing to this project, please:

1. **Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)**
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `refactor:` for code refactoring
   - `test:` for test additions/changes

2. **Update this CHANGELOG.md** with your changes under the "Unreleased" section

3. **Use semantic versioning** for version bumps:
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes (backward compatible)

## Version History Summary

- **2.1.0**: Critical coordinate system bug fixes, visual display now working correctly
- **2.0.0**: Complete GUI rewrite with interactive editing capabilities  
- **1.0.0**: Initial command-line version with basic extraction
