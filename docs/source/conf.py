import os
import sys
# Point Sphinx to your package source directory
sys.path.insert(0, os.path.abspath('../../src'))

# Import your package info dynamically
import hub2gos

project = 'hub2gos'
copyright = '2026, Shaun Adkins'
author = 'Shaun Adkins'

# The short X.Y version
version = '.'.join(hub2gos.__version__.split('.')[:2]) # e.g., '0.1'
# The full version, including alpha/beta/rc tags
release = hub2gos.__version__

# Extensions: enable automatic docstring parsing and GitHub Pages adjustments
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Supports clean Google/NumPy docstring styles
    'sphinx.ext.githubpages' # Handles the .nojekyll configuration automatically
]

# A modern, clean theme (built-in, no extra pip installation required)
html_theme = 'pydata_sphinx_theme'