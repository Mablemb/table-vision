# Contributing to Table Vision 🤝

Thank you for your interest in contributing to Table Vision! We welcome contributions from everyone and are grateful for any help you can provide.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Issue Guidelines](#issue-guidelines)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [contact@tablevision.com](mailto:contact@tablevision.com).

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Ghostscript (for PDF processing)
- Basic understanding of PyQt5 and PDF processing

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/table-vision.git
   cd table-vision
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/originalowner/table-vision.git
   ```

## 🛠️ Development Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development tools
   ```

3. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

4. **Run tests to ensure setup works**:
   ```bash
   python -m pytest tests/
   ```

## 💡 How to Contribute

### Types of Contributions

We welcome several types of contributions:

- 🐛 **Bug Reports**: Found something broken? Let us know!
- ✨ **Feature Requests**: Have an idea for improvement? Share it!
- 📝 **Documentation**: Help improve our docs
- 🧪 **Tests**: Add or improve test coverage
- 🔧 **Bug Fixes**: Fix reported issues
- ⚡ **Performance**: Optimize existing functionality
- 🎨 **UI/UX**: Improve the user interface and experience

### Areas That Need Help

- **Coordinate System Testing**: More test cases for coordinate transformations
- **PDF Format Support**: Testing with various PDF formats and layouts
- **Performance Optimization**: Speed improvements for large PDF processing
- **Documentation**: More usage examples and tutorials
- **Accessibility**: Making the UI more accessible
- **Cross-platform Testing**: Ensuring functionality across different OS

## 🔄 Pull Request Process

### Before You Start

1. **Check existing issues**: Look for existing issues or discussions about your idea
2. **Create an issue first**: For significant changes, create an issue to discuss the approach
3. **Keep changes focused**: One feature/fix per pull request

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

2. **Make your changes**:
   - Write clean, readable code
   - Add tests for new functionality
   - Update documentation as needed
   - Follow our coding standards

3. **Test your changes**:
   ```bash
   # Run tests
   python -m pytest tests/
   
   # Run linting
   flake8 src/ tests/
   
   # Type checking
   mypy src/
   
   # Format code
   black src/ tests/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new coordinate validation system"
   ```
   
   Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `refactor:` for code refactoring
   - `test:` for test changes
   - `chore:` for maintenance tasks

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**:
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what your changes do and why
   - Include screenshots for UI changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
[Add screenshots here]

## Related Issues
Fixes #(issue number)
```

## 📏 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Maximum line length: 88 characters (Black's default)
- Use type hints where appropriate

### Code Quality Tools

We use several tools to maintain code quality:

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Security scanning
bandit -r src/
```

### Documentation Standards

- Use docstrings for all public functions and classes
- Follow [Google Style](https://google.github.io/styleguide/pyguide.html) for docstrings
- Update README.md for user-facing changes
- Add inline comments for complex logic

Example docstring:
```python
def transform_coordinates(self, coord: Dict, scale: float) -> QRect:
    """Transform PDF coordinates to screen coordinates.
    
    Args:
        coord: Dictionary containing PDF coordinate data
        scale: Scale factor for transformation
        
    Returns:
        QRect object with screen coordinates
        
    Raises:
        ValueError: If coordinate data is invalid
    """
```

## 🧪 Testing Guidelines

### Test Structure

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Measure performance characteristics

### Writing Tests

1. **Follow AAA pattern**: Arrange, Act, Assert
2. **Use descriptive test names**: `test_coordinate_transformation_with_negative_values`
3. **Test edge cases**: Empty inputs, invalid data, boundary conditions
4. **Mock external dependencies**: PDF files, Ghostscript calls

Example test:
```python
def test_coord_to_screen_rect_basic_transformation():
    """Test basic coordinate transformation from PDF to screen."""
    # Arrange
    viewer = PDFViewer()
    coord = {'x1': 100, 'y1': 200, 'x2': 300, 'y2': 400}
    
    # Act
    result = viewer._coord_to_screen_rect(coord, 0, 0)
    
    # Assert
    assert isinstance(result, QRect)
    assert result.width() > 0
    assert result.height() > 0
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_viewer.py

# Run tests with verbose output
python -m pytest tests/ -v
```

## 🐛 Issue Guidelines

### Reporting Bugs

When reporting bugs, please include:

1. **Environment details**:
   - OS and version
   - Python version
   - Dependency versions (`pip freeze`)

2. **Steps to reproduce**:
   - Minimal example that reproduces the issue
   - Expected vs actual behavior

3. **Additional context**:
   - Screenshots or error messages
   - PDF files that trigger the issue (if possible)
   - Log output with debug enabled

### Feature Requests

For feature requests, please include:

1. **Problem description**: What problem does this solve?
2. **Proposed solution**: How should it work?
3. **Alternatives considered**: What other approaches did you consider?
4. **Use cases**: Who would benefit from this feature?

## 📞 Getting Help

- **Documentation**: Check our [full documentation](https://table-vision.readthedocs.io/)
- **Discussions**: Use [GitHub Discussions](https://github.com/yourusername/table-vision/discussions) for questions
- **Issues**: Use [GitHub Issues](https://github.com/yourusername/table-vision/issues) for bugs and feature requests
- **Email**: Contact us at [contact@tablevision.com](mailto:contact@tablevision.com)

## 🏆 Recognition

Contributors are recognized in several ways:

- Listed in the README.md contributors section
- Mentioned in release notes for significant contributions
- Special recognition for major features or bug fixes

## 📄 License

By contributing to Table Vision, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

---

Thank you for contributing to Table Vision! 🚀
