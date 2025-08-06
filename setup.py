"""
Setup script for Table Vision - PDF Table Extraction and Visualization Tool
"""
from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="table-vision",
    version="1.0.0",
    author="Table Vision Team",
    author_email="contact@tablevision.com",
    description="PDF Table Extraction and Visualization Tool using Camelot",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/table-vision",
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include additional files
    package_data={
        "": ["*.json", "*.txt", "*.md"],
        "resources": ["*.json"],
    },
    include_package_data=True,
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Optional dependencies for different features
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
            "sphinxcontrib-napoleon>=0.7",
        ],
        "gpu": [
            "opencv-python-headless>=4.5",
            "cupy-cuda11x>=9.0",  # For GPU acceleration
        ],
    },
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    
    # Keywords
    keywords=[
        "pdf", "table", "extraction", "camelot", "data-analysis", 
        "document-processing", "visualization", "gui", "pyqt5"
    ],
    
    # Entry points for command-line scripts
    entry_points={
        "console_scripts": [
            "table-vision=app:main",
        ],
        "gui_scripts": [
            "table-vision-gui=app:main",
        ],
    },
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/yourusername/table-vision/issues",
        "Source": "https://github.com/yourusername/table-vision",
        "Documentation": "https://table-vision.readthedocs.io/",
    },
    
    # License
    license="MIT",
    
    # Zip safe
    zip_safe=False,
)