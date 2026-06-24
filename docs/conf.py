import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

project = 'Sphinx Touchbook Author Guide'
author = 'Dave Parillo'
project_copyright = '2026, ' + author
version = '0.1.0'
release = version + '-alpha'


extensions = ['sphinx_touchbook']
language = 'en'
html_theme = 'sphinx_nefertiti'
# html_theme_options = {
#     'pygments_light_style': 'solarized-light',
#     'pygments_dark_style': 'solarized-dark',
# }
html_theme_options = {
    'header_links': [
        {
            'text': 'Home',
            'link': 'index',
        },
        {
            'text': 'GitHub',
            'link': 'https://github.com/DaveParillo/sphinx-touchbook',
        },
    ],
    'logo': 'hand-index-thumb.svg',
    'logo_width': 40,
    'logo_height': 24,
}

tb_code_block_defaults = {
    'linenos': True,
}
