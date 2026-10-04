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


extensions = ['sphinx_touchbook', 'sphinx_copybutton']
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
    'logo_alt': '',
    'logo_width': 40,
    'logo_height': 24,
}

tb_code_block_defaults = {
    'linenos': True,
}

tb_code_compiler_explorer_defaults = {
    'python': {'language': 'python', 'compiler': 'python314'},
    'cpp': {'language': 'c++', 'compiler': 'g153'},
    'c++': {'language': 'c++', 'compiler': 'g153'},
    'java': {'language': 'java', 'compiler': 'java1702'},
}

tb_graph_styles = {
    "list": {"fill": "#e0f2fe", "font-size": 14},
    "plain-list": {"base": "list", "shape": "ellipse","fill": None},
    "tree": {
        "fill": "#dcfce7", "highlight-fill": "#fde68a",
        "level-spacing": 0.4,
    },
}

