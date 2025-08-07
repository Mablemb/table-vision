"""
Example usage of Table Vision with page range functionality.

This example demonstrates how to use the new page range features
for efficient table extraction from specific pages.
"""
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def example_page_range_extraction():
    """
    Example of using page range extraction programmatically.
    
    This shows how to extract tables from specific page ranges
    instead of processing entire documents.
    """
    from ui.main_window import BatchExtractionWorkerCustom
    from PyQt5.QtCore import QCoreApplication
    
    print("Page Range Extraction Example")
    print("=" * 40)
    
    # Example: Extract tables from pages 5-10 of a document
    pdf_path = "sample_document.pdf"  # Replace with actual PDF path
    start_page = 5
    end_page = 10
    batch_size = 3
    
    print(f"Configuration:")
    print(f"  PDF: {pdf_path}")
    print(f"  Page Range: {start_page}-{end_page}")
    print(f"  Batch Size: {batch_size}")
    print(f"  Pages to Process: {end_page - start_page + 1}")
    
    # Create worker for custom page range
    worker = BatchExtractionWorkerCustom(
        pdf_path=pdf_path,
        batch_size=batch_size,
        start_page=start_page,
        end_page=end_page
    )
    
    # In a real application, you would connect these signals:
    print("\nSignals available for connection:")
    print("  - page_completed(int, list): Emitted when each page is processed")
    print("  - batch_completed(list): Emitted when entire range is processed")
    print("  - progress_updated(int, int): Emitted with progress updates")
    print("  - error_occurred(str): Emitted if an error occurs")
    
    print("\nExample signal connections:")
    print("  worker.page_completed.connect(on_page_completed)")
    print("  worker.batch_completed.connect(on_batch_completed)")
    print("  worker.progress_updated.connect(on_progress_updated)")
    print("  worker.error_occurred.connect(on_error_occurred)")
    
    return worker

def example_ui_usage():
    """
    Example of using the page range UI controls.
    
    This shows how users can interact with the new UI elements
    to select page ranges for extraction.
    """
    print("\nUI Usage Example")
    print("=" * 40)
    
    print("Step-by-step UI usage:")
    print("1. Load a PDF document using 'Open PDF' button")
    print("2. In the Page Range section:")
    print("   - Check 'All Pages' to process entire document")
    print("   - OR uncheck 'All Pages' and set 'From' and 'To' values")
    print("3. Set batch size for processing efficiency")
    print("4. Click 'Extract Tables' to start extraction")
    print("5. Monitor progress in the status bar")
    print("6. Stop extraction anytime using 'Stop Extraction' button")
    
    print("\nBenefits of page range selection:")
    print("• Faster processing for large documents")
    print("• Test extraction on small ranges before full processing")
    print("• Focus on specific sections of documents")
    print("• Reduced memory usage")
    print("• Better system responsiveness")

def example_use_cases():
    """
    Example use cases for page range functionality.
    """
    print("\nCommon Use Cases")
    print("=" * 40)
    
    use_cases = [
        {
            "scenario": "Testing extraction quality",
            "pages": "1-3",
            "description": "Test on first few pages to verify table detection quality"
        },
        {
            "scenario": "Processing specific chapters",
            "pages": "25-45",
            "description": "Extract tables from a specific chapter or section"
        },
        {
            "scenario": "Large document processing",
            "pages": "1-50, then 51-100",
            "description": "Process large documents in manageable chunks"
        },
        {
            "scenario": "Problem page investigation",
            "pages": "15-15",
            "description": "Focus on a specific page that needs attention"
        },
        {
            "scenario": "Data validation",
            "pages": "Random ranges",
            "description": "Sample different sections for quality assurance"
        }
    ]
    
    for i, case in enumerate(use_cases, 1):
        print(f"{i}. {case['scenario']}")
        print(f"   Pages: {case['pages']}")
        print(f"   Use: {case['description']}")
        print()

def example_performance_benefits():
    """
    Example showing performance benefits of page range selection.
    """
    print("Performance Benefits")
    print("=" * 40)
    
    # Simulated processing times (for illustration)
    scenarios = [
        {
            "description": "Full 100-page document",
            "pages": 100,
            "time": "~5-10 minutes",
            "memory": "~500MB"
        },
        {
            "description": "Pages 1-10 (testing)",
            "pages": 10,
            "time": "~30-60 seconds",
            "memory": "~50MB"
        },
        {
            "description": "Pages 25-35 (specific section)",
            "pages": 11,
            "time": "~45-90 seconds",
            "memory": "~55MB"
        },
        {
            "description": "Single page analysis",
            "pages": 1,
            "time": "~5-10 seconds",
            "memory": "~10MB"
        }
    ]
    
    print("Processing Time Estimates:")
    for scenario in scenarios:
        print(f"  {scenario['description']}")
        print(f"    Pages: {scenario['pages']}")
        print(f"    Time: {scenario['time']}")
        print(f"    Memory: {scenario['memory']}")
        print()

if __name__ == "__main__":
    print("Table Vision - Page Range Feature Examples")
    print("=" * 50)
    
    # Show all examples
    worker = example_page_range_extraction()
    example_ui_usage()
    example_use_cases()
    example_performance_benefits()
    
    print("=" * 50)
    print("✨ Page range functionality is now available!")
    print("Start the application with: python src/app.py")
