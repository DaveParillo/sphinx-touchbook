import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

ROOT = Path(__file__).resolve().parents[1]


def project_version():
    with (ROOT / "pyproject.toml").open("rb") as pyproject:
        return tomllib.load(pyproject)["project"]["version"]

project = 'Sphinx Touchbook Author Guide'
author = 'Dave Parillo'
project_copyright = '2026, ' + author
version = project_version()
release = version + '-alpha'


extensions = ['sphinx_touchbook']
language = 'en'
html_theme = 'sphinx_nefertiti'
html_theme_options = {
    'header_links': [
        {
            'text': 'on GitHub',
            'link': 'https://github.com/DaveParillo/sphinx-touchbook',
        },
    ],
    'logo': 'touchbook-logo.svg',
    'logo_width': 40,
    'logo_height': 24,
}

tb_code_block_defaults = {
    'linenos': True,
}
