# Table Vision Coordinate System Fixes

## Problems Fixed

### 1. **Coordinate System Mismatch**
- **Issue**: Camelot uses PDF coordinates (bottom-left origin) while the PDF viewer uses screen coordinates (top-left origin)
- **Fix**: Updated `_coord_to_screen_rect()` and `_screen_to_coord_rect()` in `src/visualization/viewer.py` to properly handle the coordinate transformation, accounting for PyMuPDF's 2x rendering scale

### 2. **Disappearing User-Created Outlines**
- **Issue**: User-drawn outlines disappeared when Camelot re-ran extraction
- **Fix**: 
  - Modified `on_page_extraction_completed()` and `on_batch_extraction_completed()` to preserve user-created coordinates
  - Fixed ID management to avoid conflicts between Camelot IDs (1000+) and user IDs (1+)
  - Updated `update_coordinates_display()` to merge coordinates from both sources

### 3. **ID Management Issues**
- **Issue**: Conflicting IDs between user-created and Camelot-detected tables
- **Fix**: 
  - User-created coordinates now use IDs starting from 1
  - Camelot-detected coordinates use IDs starting from 1000
  - Fixed batch extraction to use proper global ID counters

## Testing Your Fixes

### Step 1: Test Coordinate Transformation
```bash
cd table-vision
python debug_coordinates.py
```
This will show you if the coordinate transformation is working correctly. You should see "✅ Transformation is accurate!" for each detected table.

### Step 2: Test the Full Application
```bash
cd table-vision
python src/app.py
```

### Step 3: Test the Following Workflow:
1. **Load a PDF** with tables
2. **Extract tables** using Camelot - outlines should appear correctly positioned
3. **Draw new outlines** by clicking and dragging on areas where Camelot missed tables
4. **Re-run extraction** - your hand-drawn outlines should persist
5. **Navigate between pages** - outlines should stay in correct positions

## Debug Mode

If outlines are still not appearing correctly:

1. **Enable debug output** in `src/visualization/viewer.py`:
   ```python
   debug = True  # Set to True for debugging coordinate transformation issues
   ```

2. **Check the console output** when loading tables - you'll see detailed coordinate transformation info

3. **Look for these debug messages**:
   - "DEBUG - Converting coordinates to screen:" (shows Camelot→Screen conversion)
   - "DEBUG - Converting screen to coordinates:" (shows Screen→Camelot conversion)
   - "DEBUG - Camelot detected table..." (shows table detection)
   - "DEBUG - User drew table..." (shows user creation)

## Expected Behavior

✅ **Correct behavior:**
- Table outlines appear exactly over the tables in the PDF
- User-drawn outlines persist after re-running Camelot
- Outlines stay in correct positions when zooming/panning
- No duplicate or overlapping outline IDs

❌ **If you still see issues:**
- Outlines appear in wrong locations → Coordinate transformation issue
- User outlines disappear → Coordinate persistence issue  
- App crashes on outline creation → ID management issue

## Files Modified

1. `src/visualization/viewer.py` - Fixed coordinate transformations
2. `src/ui/main_window.py` - Fixed coordinate persistence and ID management
3. `src/core/extractor.py` - Fixed ID assignment for Camelot tables
4. `src/core/coordinates.py` - Fixed user ID management
5. `debug_coordinates.py` - Updated to test new coordinate system

## Quick Debug Tips

- **Outlines in wrong place**: Check coordinate transformation in debug mode
- **Outlines disappear**: Check if user coordinates are being preserved in extraction
- **Can't create outlines**: Check for ID conflicts or coordinate conversion errors
- **App performance**: Disable debug output by setting `debug = False`
