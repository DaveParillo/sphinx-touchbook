import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

project = "Sphinx Touchbook Author Guide"
extensions = ["sphinx_touchbook"]
language = "en"
html_theme = "sphinx_nefertiti"
html_theme_options = {
    # ... other options ...
    'pygments_light_style': 'solarized-light',
    'pygments_dark_style': 'solarized-dark'
}

# import sphinx_bootstrap_theme
# html_theme = "bootstrap"
# html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
#html_theme = "pydata_sphinx_theme"
# pygments_style = "a11y-high-contrast-light"
# pygments_dark_style = "a11y-high-contrast-dark"
