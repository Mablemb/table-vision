"""
Table Vision - PDF Table Extraction and Visualization Tool

This application allows users to:
1. Load PDF documents
2. Extract tables using Camelot lattice method
3. Visualize and edit table boundaries interactively
4. Export individual table regions as images

Usage:
    python app.py
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from ui.main_window import main

if __name__ == "__main__":
    main()