# Testing Guide

## 🧪 Automated Testing with pytest

Table Vision now includes a comprehensive automated testing suite using pytest for reliable validation of core functionality.

### Test Infrastructure

- **pytest 8.4.1**: Modern Python testing framework
- **pytest-qt 4.5.0**: PyQt5-specific testing for GUI components
- **pytest-cov 6.2.1**: Code coverage reporting integration
- **15 automated tests**: Complete coverage of deletion and synchronization scenarios

### Running Automated Tests

**Install test dependencies (if not already installed):**
```bash
pip install pytest pytest-qt pytest-cov
```

**Run all automated tests:**
```bash
python -m pytest tests/ -v
```

**Run with code coverage:**
```bash
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

**Run specific test files:**
```bash
# Deletion functionality tests
python -m pytest tests/test_deletion_pytest.py -v

# Synchronization tests  
python -m pytest tests/test_synchronization_pytest.py -v

# Batch processing tests
python -m pytest tests/test_batch_accumulation.py -v
```

### Test Coverage Summary

The automated tests validate:

- ✅ **Basic coordinate deletion** - Removing single coordinates
- ✅ **Multiple coordinate deletion** - Batch deletion operations
- ✅ **Non-existent coordinate handling** - Graceful error handling
- ✅ **User-created coordinate deletion** - Manual table deletion
- ✅ **Data structure synchronization** - Internal consistency
- ✅ **Real-time deletion during batch processing** - Critical fix verification
- ✅ **Coordinate accumulation across pages** - Multi-page extraction
- ✅ **ID consistency during operations** - Proper coordinate tracking
- ✅ **User coordinate preservation** - Protecting manual additions

## 🐛 Manual Testing for Bug Fixes

## Issues Fixed

### 1. ✅ Coordinate System Mismatch
**Problem**: Camelot tables not showing up correctly due to coordinate transformation errors.  
**Fix**: Completely rewrote `_coord_to_screen_rect()` and `_screen_to_coord_rect()` to properly handle:
- PyMuPDF's 2x rendering scale
- PDF coordinate system (bottom-left origin) to screen coordinate system (top-left origin) conversion
- Proper scaling factors

### 2. ✅ Wrong Page Display 
**Problem**: Tables showing on wrong pages.  
**Fix**: Verified page numbering conversion from Camelot (1-based) to viewer (0-based) is correct.

### 3. ✅ Missing Rectangle Editing
**Problem**: Could not move or resize table outlines.  
**Fix**: Implemented complete move/resize functionality:
- Added `rectangle_moved` signal connection
- Implemented `on_rectangle_moved()` handler in main window  
- Added proper mouse move/resize logic in viewer
- Coordinate updates now propagate to both coordinate manager and display

### 4. ✅ Coordinate Persistence 
**Problem**: User-drawn rectangles disappearing.  
**Fix**: Enhanced coordinate preservation system.

## Testing Steps

### Step 1: Enable Debug Mode (if needed)
If you want to see detailed coordinate conversion info, set these debug flags to `True` in `src/visualization/viewer.py`:
- Line ~156: `debug = True` (for coordinate transformation)
- Line ~197: `debug = True` (for screen-to-coordinate conversion)  
- Line ~100: `debug = True` (for page filtering)

### Step 2: Test Coordinate Transformation
```bash
cd table-vision
python debug_coordinates.py
```
**Expected**: You should see "✅ Transformation is accurate!" for each detected table.

### Step 3: Test Full Application
```bash
python src/app.py
```

### Step 4: Complete Workflow Test

1. **Load PDF**: Open a PDF with tables
2. **Extract Tables**: Click "Extract Tables" 
   - ✅ **Expected**: Camelot-detected outlines should appear exactly over the tables
   - ❌ **If not**: Check debug output for coordinate transformation issues

3. **Draw New Outlines**: 
   - Click and drag to create new table outlines where Camelot missed tables
   - ✅ **Expected**: New outlines appear where you draw them

4. **Edit Existing Outlines**:
   - Click on any outline to select it (should show green resize handles)
   - Drag to move the entire outline
   - Drag corner/edge handles to resize
   - ✅ **Expected**: Outlines should move/resize smoothly and accurately

5. **Page Navigation**:
   - Navigate between pages 
   - ✅ **Expected**: Outlines should appear on correct pages only

6. **Re-run Extraction**:
   - Click "Extract Tables" again
   - ✅ **Expected**: Your hand-drawn outlines should persist while new Camelot results are added

7. **Zoom Testing**:
   - Use zoom slider to zoom in/out
   - ✅ **Expected**: All outlines should scale correctly and stay positioned over tables

## Debug Information

If issues persist, check console output for these debug messages:

### Coordinate Transformation Debug:
```
DEBUG - Converting coordinates to screen:
  Input coord: {'id': 1000, 'page': 0, 'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400, ...}
  Pixmap dimensions: 1684 x 2378
  Original PDF dimensions: 421.0 x 594.5
  Screen coordinates: x1=200.0, y1=388.0, x2=600.0, y2=588.0
```

### Page Filtering Debug:
```
DEBUG - Page filtering: current_page=0
  Total coordinates: 5
  Current page coordinates: 3
    Coord page=0, id=1000, user_created=False
    Coord page=0, id=1, user_created=True
```

### Rectangle Movement Debug:
```
DEBUG - Rectangle 1000 moved to: x1=105.2, y1=203.1, x2=305.2, y2=403.1
DEBUG - Updated coordinate 1000 in manager
DEBUG - Updated coordinate 1000 in extracted list
```

## Common Issues & Solutions

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Camelot outlines not showing | Coordinate transformation error | Enable debug mode, check coordinate conversion |
| Outlines on wrong page | Page numbering mismatch | Check page filtering debug output |
| Can't move/resize outlines | Missing signal connections | Check that rectangle_moved signal is connected |
| User outlines disappear | Coordinate preservation issue | Check extraction completion handlers |
| Performance issues | Debug output enabled | Disable debug flags |

## Quick Debug Enable/Disable

**Enable all debug output**:
```python
# In src/visualization/viewer.py
debug = True  # Lines ~156, ~197, ~100
```

**Disable all debug output** (for normal use):
```python
# In src/visualization/viewer.py  
debug = False  # Lines ~156, ~197, ~100
```

## Expected Final Result

After these fixes, you should have:
- ✅ Camelot-detected table outlines appearing exactly over tables in the PDF
- ✅ Ability to draw new table outlines anywhere 
- ✅ Ability to move and resize any table outline
- ✅ User-created outlines persisting through re-extraction
- ✅ Correct page-specific display of outlines
- ✅ Proper zoom scaling of all outlines
