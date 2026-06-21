import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

project = "Sphinx Touchbook Author Guide"
extensions = ["sphinx_touchbook"]
language = "en"
html_theme = "sphinx_nefertiti"
# html_theme_options = {
#     "pygments_light_style": "solarized-light",
#     "pygments_dark_style": "solarized-dark",
# }

tb_code_block_defaults = {
    "linenos": True,
}
