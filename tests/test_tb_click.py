from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.click import (
    TbClickDirective,
    TbClickHitDirective,
    TbClickMissDirective,
    resolve_selector,
)
from sphinx_touchbook.nodes import TbClickNode, TbClickRegionNode


CLICK_RST = """
.. tb-click::
   :name: sql-click

   Click the comparison operator.

   .. code-block:: sql

      SELECT name
      FROM students
      WHERE age >= 18;

   .. tb-hit:: >=

      ``>=`` is the comparison operator.

   .. tb-miss:: line:SELECT name

      This line selects output columns.
"""


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = {
        "tb-click": directives._directives.get("tb-click"),
        "tb-hit": directives._directives.get("tb-hit"),
        "tb-miss": directives._directives.get("tb-miss"),
    }
    directives.register_directive("tb-click", TbClickDirective)
    directives.register_directive("tb-hit", TbClickHitDirective)
    directives.register_directive("tb-miss", TbClickMissDirective)
    try:
        parser.parse(source, document)
    finally:
        for name, directive in previous.items():
            if directive is None:
                directives._directives.pop(name, None)
            else:
                directives._directives[name] = directive
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


def test_resolve_text_selector_defaults_to_first_exact_match():
    source = "int x = 0;\nx = x + 1;"

    assert resolve_selector(source, "x") == (4, 5)
    assert resolve_selector(source, "text:x#2") == (11, 12)


def test_resolve_line_and_range_selectors():
    source = "SELECT name\nFROM students\nWHERE age >= 18;"

    assert resolve_selector(source, "line:FROM students") == (12, 25)
    assert resolve_selector(source, "range:3:11-12") == (36, 38)


def test_directive_parses_click_regions():
    document = parse_rst(CLICK_RST)

    node = next(document.findall(TbClickNode))
    regions = list(node.findall(TbClickRegionNode))
    assert node["ids"] == ["sql-click"]
    assert node["source"] == "SELECT name\nFROM students\nWHERE age >= 18;"
    assert [region["correct"] for region in regions] == [True, False]
    assert [(region["start"], region["end"]) for region in regions] == [(36, 38), (0, 11)]


def test_directive_reports_overlapping_regions():
    document = parse_rst(
        """
.. tb-click::

   .. code-block:: text

      abc

   .. tb-hit:: ab

      Correct.

   .. tb-miss:: range:1:2-3

      Overlaps.
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "must not overlap" in document.astext()


def test_html_build_emits_clickable_targets_and_feedback(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        f"""
Title
=====

{CLICK_RST}
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-click", id="sql-click")
    assert element is not None
    assert element["hints"] == "false"
    assert "Click the comparison operator" in element.find("div", class_="tb-click__prompt").get_text(" ", strip=True)
    targets = element.find_all("button", class_="tb-click__target")
    assert [target.get_text() for target in targets] == ["SELECT name", ">="]
    assert [target["data-correct"] for target in targets] == ["false", "true"]
    feedback = element.find_all("div", class_="tb-click__feedback")
    assert len(feedback) == 2
    assert feedback[0].has_attr("hidden")
    assert element.find("button", class_="tb-click__hint-toggle").get_text(strip=True) == "Show Hints"
    assert (outdir / "_static" / "tb-click.js").exists()
    assert (outdir / "_static" / "tb-click.css").exists()


def test_html_build_emits_show_hints_state_when_requested(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-click::
   :show-hints:

   .. code-block:: text

      abc

   .. tb-hit:: b

      Correct.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-click")
    assert element["hints"] == "true"
    assert element.find("button", class_="tb-click__hint-toggle") is not None


def test_html_build_uses_global_show_hints_config(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-click::

   .. code-block:: text

      abc

   .. tb-hit:: b

      Correct.
""",
        conf_extra="tb_click_show_hints = True\n",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-click")
    assert element["hints"] == "true"


def test_html_build_hides_hint_button_when_hints_never(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-click::

   .. code-block:: text

      abc

   .. tb-hit:: b

      Correct.
""",
        conf_extra='tb_click_show_hints = "never"\n',
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-click")
    assert element["hints"] == "never"
    assert element.find("button", class_="tb-click__hint-toggle") is None


def test_text_builder_renders_prompt_and_source_without_feedback(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        f"""
Title
=====

{CLICK_RST}
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "[Click question]" in text
    assert "Click the comparison operator" in text
    assert "WHERE age >= 18;" in text
    assert "comparison operator." not in text.replace("Click the comparison operator.", "")
    assert "This line selects output columns." not in text


def test_latex_builder_renders_prompt_and_source_without_feedback(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        f"""
Title
=====

{CLICK_RST}
""",
    )

    latex = read_latex_output(outdir)
    assert r"\begin{sphinxadmonition}{note}{Click question}" in latex
    assert "Click the comparison operator" in latex
    assert "WHERE age >= 18;" in latex
    assert "This line selects output columns." not in latex
