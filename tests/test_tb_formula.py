from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.formula import TbFormulaDirective
from sphinx_touchbook.nodes import TbFormulaNode, TbFormulaVariableNode


FORMULA_RST = """
.. tb-formula::
   :name: formula-example
   :variables: x=80..90, y=10..20
   :tolerance: 0.01

   If a small glass can hold {{x}} ounces of water, and a large glass can
   hold {{y}} ounces of water, what's the total number of ounces in 4 large
   and 3 small glasses of water?

   .. answer-formula:: javascript

      4 * y + 3 * x
"""


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-formula")
    directives.register_directive("tb-formula", TbFormulaDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-formula", None)
        else:
            directives._directives["tb-formula"] = previous
    return document


def build_sphinx(tmp_path: Path, builder: str, index: str, conf_extra: str = "") -> Path:
    srcdir = tmp_path / "src"
    outdir = tmp_path / f"_build_{builder}"
    doctreedir = tmp_path / f"_doctree_{builder}"
    srcdir.mkdir()
    (srcdir / "conf.py").write_text(
        'extensions = ["sphinx_touchbook"]\n'
        'html_theme = "alabaster"\n'
        f"{conf_extra}",
        encoding="utf-8",
    )
    (srcdir / "index.rst").write_text(index, encoding="utf-8")
    app = Sphinx(
        srcdir=str(srcdir),
        confdir=str(srcdir),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername=builder,
        warningiserror=True,
        freshenv=True,
    )
    app.build()
    return outdir


def read_latex_output(outdir: Path) -> str:
    tex_files = sorted(path for path in outdir.glob("*.tex") if path.name != "sphinxmessages.sty")
    assert tex_files
    return tex_files[0].read_text(encoding="utf-8")


def test_directive_parses_variables_prompt_and_formula():
    document = parse_rst(FORMULA_RST)

    node = next(document.findall(TbFormulaNode))
    variables = list(document.findall(TbFormulaVariableNode))
    assert node["ids"] == ["formula-example"]
    assert node["variables"]["x"] == {"min": 80.0, "max": 90.0, "integer": True}
    assert node["variables"]["y"] == {"min": 10.0, "max": 20.0, "integer": True}
    assert node["formula"] == {
        "language": "javascript",
        "source": "4 * y + 3 * x",
        "parameters": {"compileargs": [], "linkargs": [], "runargs": [], "interpreterargs": []},
    }
    assert node["tolerance"] == 0.01
    assert [variable["name"] for variable in variables] == ["x", "y"]


def test_directive_defaults_formula_language_to_javascript():
    document = parse_rst(
        """
.. tb-formula::
   :variables: x=1..2

   What is {{x}} doubled?

   .. answer-formula::

      x * 2
"""
    )

    node = next(document.findall(TbFormulaNode))
    assert node["formula"]["language"] == "javascript"


def test_directive_parses_answer_formula_parameters():
    document = parse_rst(
        """
.. tb-formula::
   :variables: n=2..9

   What is {{n}} squared?

   .. answer-formula:: cpp
      :compileargs: ['-Wall', '-Wextra', '-std=c++11']

      #include <iostream>
      int main() {
        std::cout << 4 << '\\n';
      }
"""
    )

    node = next(document.findall(TbFormulaNode))
    assert node["formula"]["language"] == "cpp"
    assert node["formula"]["source"].startswith("#include <iostream>")
    assert node["formula"]["parameters"]["compileargs"] == ["-Wall", "-Wextra", "-std=c++11"]


def test_directive_rejects_missing_variable_range():
    document = parse_rst(
        """
.. tb-formula::
   :variables: x=1..2

   What is {{y}}?

   .. answer-formula::

      y
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "missing variable ranges: y" in document.astext()


def test_directive_requires_one_answer_formula():
    document = parse_rst(
        """
.. tb-formula::
   :variables: x=1..2

   What is {{x}}?
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "exactly one nested answer-formula" in document.astext()


def test_html_build_emits_formula_config_input_and_assets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        f"""
Title
=====

{FORMULA_RST}
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-formula", id="formula-example")
    assert element is not None
    assert "jobe/index.php/restapi/runs" in element["data-endpoint"]
    variables = element.find_all("span", class_="tb-formula__variable")
    assert [variable["data-variable"] for variable in variables] == ["x", "y"]
    config = element.find("script", class_="tb-formula__config")
    assert '"4 * y + 3 * x"' in config.string
    input_element = element.find("input", class_="tb-formula__input")
    assert input_element is not None
    assert input_element["type"] == "text"
    assert input_element["inputmode"] == "decimal"
    assert element.find("button", class_="tb-formula__check") is not None
    assert element.find("button", class_="tb-formula__new-values") is not None
    assert (outdir / "_static" / "tb-formula.js").exists()
    assert (outdir / "_static" / "tb-formula.css").exists()


def test_html_build_preserves_angle_brackets_in_formula_source(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-formula::
   :name: formula-cpp
   :variables: n=2..9

   What is {{n}} squared?

   .. answer-formula:: cpp
      :compileargs: -std=c++11

      #include <iostream>
      int main() {
        std::cout << 4 << '\\n';
      }
""",
    )

    html = (outdir / "index.html").read_text(encoding="utf-8")
    assert "#include <iostream>" in html
    assert "#include &lt;iostream&gt;" not in html


def test_html_build_uses_formula_language_defaults(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-formula::
   :name: formula-defaults
   :variables: n=2..9

   What is {{n}} squared?

   .. answer-formula:: cpp

      #include <iostream>
      int main() {
        std::cout << 4 << '\\n';
      }
""",
        conf_extra='tb_formula_language_defaults = {"cpp": {"compileargs": ["-std=c++11"]}}\n',
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    config = soup.find("script", class_="tb-formula__config")
    assert '"compileargs": ["-std=c++11"]' in config.string


def test_text_builder_renders_static_formula_question(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        f"""
Title
=====

{FORMULA_RST}
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "[Calculated formula]" in text
    assert "small glass can hold" in text
    assert "____" in text
    assert "4 * y + 3 * x" not in text


def test_latex_builder_renders_static_formula_question(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        f"""
Title
=====

{FORMULA_RST}
""",
    )

    latex = read_latex_output(outdir)
    assert r"\begin{sphinxadmonition}{note}{Calculated formula}" in latex
    assert r"\underline{\hspace{1cm}}" in latex
    assert "4 * y + 3 * x" not in latex
