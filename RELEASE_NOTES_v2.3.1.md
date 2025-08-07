# Release Notes - Table Vision v2.3.1

**Release Date**: August 7, 2025  
**Type**: Critical Bug Fix Release  
**Priority**: Recommended for all users

## 🚨 Critical Bug Fix

### Table Deletion Functionality Restored
This release resolves a critical bug that prevented users from deleting detected tables displayed in the right panel. This issue significantly impacted user workflow during table extraction and curation.

## 🐛 Issues Resolved

### Primary Issues
- **Table Deletion Bug**: Detected tables in the right panel couldn't be deleted
- **Coordinate Persistence**: Deleted coordinates would reappear due to data structure inconsistencies
- **Batch Processing Limitation**: Deletion only worked at the end of batch extraction, not during the process

### Technical Issues
- **Data Structure Synchronization**: Fixed inconsistencies between `coordinates_manager` and `all_extracted_coordinates`
- **Batch Accumulation**: Resolved coordinates refreshing instead of properly accumulating during batch extraction
- **Coordinate Duplication**: Fixed duplicate coordinate storage in regular extraction mode

## ✨ Improvements

### Enhanced User Experience
- **Real-time Deletion**: Delete unwanted tables immediately during batch extraction
- **Consistent Behavior**: Unified deletion functionality across all extraction methods
- **Improved Workflow**: Smooth, uninterrupted table review and curation process

### Technical Enhancements
- **Incremental Coordinate Management**: Both data structures are now maintained in real-time during batch processing
- **Enhanced Debug Logging**: Comprehensive logging for troubleshooting coordinate management
- **Robust Testing**: Added 13+ automated tests covering all deletion scenarios

## 🧪 Testing

This release includes comprehensive testing to ensure reliability:
- ✅ **4/4** Basic deletion functionality tests
- ✅ **3/3** Coordinate synchronization tests  
- ✅ **1/1** Batch accumulation tests
- ✅ **5/5** Comprehensive workflow tests

**Total: 13/13 automated tests passing**

## 🔧 Technical Details

### Modified Components
- **`src/ui/main_window.py`**: Enhanced coordinate management methods
- **`delete_coordinate()`**: Now removes from both data structures
- **`on_page_extraction_completed()`**: Maintains both structures incrementally
- **`on_batch_extraction_completed()`**: Simplified to focus on UI cleanup

### New Test Files
- `tests/test_deletion_fix.py`: Basic deletion functionality
- `tests/test_coordinate_sync.py`: Data structure synchronization
- `tests/test_batch_accumulation.py`: Batch processing accumulation
- `tests/test_comprehensive_deletion.py`: Full workflow testing

## 📋 Upgrade Instructions

### For Existing Users
1. Update your installation using your preferred method (git pull, download, etc.)
2. No additional configuration required - bug fixes are automatically active
3. Existing PDF sessions and coordinates remain compatible

### For New Users
Follow the standard installation instructions in the README.md

## 🎯 Impact

### Before v2.3.1
- Table deletion was unreliable or non-functional
- Batch extraction required waiting until completion to delete tables
- Inconsistent behavior between extraction methods
- Poor user experience during table curation

### After v2.3.1
- Immediate, reliable table deletion
- Real-time deletion during batch extraction
- Consistent behavior across all extraction methods  
- Smooth, efficient table curation workflow

## 🔄 Compatibility

- **Backward Compatible**: All existing features and workflows remain unchanged
- **PDF Support**: No changes to supported PDF formats or versions
- **Settings**: All existing settings and configurations are preserved
- **Export**: No changes to image export functionality

## 🚀 Next Steps

With table deletion functionality now fully operational, future releases will focus on:
- Performance optimizations for large documents
- Additional export formats and options
- Enhanced table detection algorithms
- Advanced batch processing features

## 📞 Support

If you encounter any issues with this release:
1. Check the troubleshooting section in README.md
2. Run the test suite: `python -m pytest tests/`
3. Enable debug mode for detailed logging
4. Report issues on GitHub with relevant logs

---

**Thank you for using Table Vision!** This critical fix ensures a smooth, efficient table extraction workflow for all users.
