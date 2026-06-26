"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
Copyright (C) 2026 Dave Parillo.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
html_theme_options = {
    'header_links': [
        {
            'text': 'on GitHub',
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
