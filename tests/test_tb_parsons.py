from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.parsons import TbParsonsDirective
from sphinx_touchbook.nodes import TbParsonsItemNode, TbParsonsNode, TbParsonsPromptNode


PARSONS_RST = """
.. tb-parsons::
   :name: parsons-example

   Construct a function that returns the maximum value in a list.

   .. code-block:: python

      def findmax(alist):
      {{group}}
          if len(alist) == 0:
              return None
      {{endgroup}}
          curmax = alist[0]
      {{distractor}}
          return item
      {{group}}
          return curmax
      {{endgroup}}
"""


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-parsons")
    directives.register_directive("tb-parsons", TbParsonsDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-parsons", None)
        else:
            directives._directives["tb-parsons"] = previous
    return document


def build_sphinx(tmp_path: Path, builder: str, index: str) -> Path:
    srcdir = tmp_path / "src"
    outdir = tmp_path / f"_build_{builder}"
    doctreedir = tmp_path / f"_doctree_{builder}"
    srcdir.mkdir()
    (srcdir / "conf.py").write_text(
        'extensions = ["sphinx_touchbook"]\n'
        'html_theme = "alabaster"\n',
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


def test_directive_parses_grouped_literal_fragments():
    document = parse_rst(
        """
.. tb-parsons::
   :name: parsons-grouped

   Construct the function.

   ::

      def findmax(alist):
      {{group}}
          if len(alist) == 0:
              return None
      {{endgroup}}
      {{distractor}}
          return item
      {{group}}
          return curmax
      {{endgroup}}
"""
    )

    node = next(document.findall(TbParsonsNode))
    prompt = next(document.findall(TbParsonsPromptNode))
    items = list(document.findall(TbParsonsItemNode))
    assert node["ids"] == ["parsons-grouped"]
    assert "Construct the function" in prompt.astext()
    assert [item["index"] for item in items] == [0, 1, 2, 3]
    assert [item["distractor"] for item in items] == [False, False, True, False]
    assert items[1]["code"] == "if len(alist) == 0:\n    return None"
    assert items[1]["indent"] == 4


def test_directive_resumes_single_line_fragments_after_endgroup():
    document = parse_rst(
        """
.. tb-parsons::

   ::

      start()
      {{group}}
          grouped_one()
          grouped_two()
      {{endgroup}}
      finish()
"""
    )

    items = list(document.findall(TbParsonsItemNode))
    assert [item["code"] for item in items] == [
        "start()",
        "grouped_one()\ngrouped_two()",
        "finish()",
    ]


def test_directive_parses_unmarked_lines_as_fragments():
    document = parse_rst(
        """
.. tb-parsons::

   ::

      first()
      second()
"""
    )

    items = list(document.findall(TbParsonsItemNode))
    assert [item["code"] for item in items] == ["first()", "second()"]


def test_directive_rejects_too_few_required_fragments():
    document = parse_rst(
        """
.. tb-parsons::

   ::

      only()
      {{distractor}}
      extra()
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "at least two required code fragments" in document.astext()


def test_directive_rejects_unclosed_group():
    document = parse_rst(
        """
.. tb-parsons::

   ::

      first()
      {{group}}
      second()
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "without a matching {{endgroup}}" in document.astext()


def test_html_build_emits_parsons_element_controls_and_assets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        f"""
Title
=====

{PARSONS_RST}
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-parsons", id="parsons-example")
    assert element is not None
    assert element["data-no-indent"] == "false"
    items = element.find_all("li", class_="tb-parsons__item")
    assert len(items) == 5
    assert any(item["data-distractor"] == "true" for item in items)
    assert all(item.find("button", class_="tb-parsons__move-up") for item in items)
    assert all(item.find("button", class_="tb-parsons__indent-in") for item in items)
    assert all(item.find("button", class_="tb-parsons__toggle") for item in items)
    assert element.find("button", class_="tb-parsons__check") is not None
    assert (outdir / "_static" / "tb-parsons.js").exists()
    assert (outdir / "_static" / "tb-parsons.css").exists()


def test_html_build_emits_no_indent_option(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-parsons::
   :name: parsons-no-indent
   :no-indent:

   ::

      first()
      second()
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-parsons", id="parsons-no-indent")
    assert element["data-no-indent"] == "true"


def test_text_builder_renders_static_parsons_question(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        f"""
Title
=====

{PARSONS_RST}
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "[Parsons problem]" in text
    assert "Code fragments:" in text
    assert "return curmax" in text


def test_latex_builder_renders_static_parsons_question(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        f"""
Title
=====

{PARSONS_RST}
""",
    )

    latex = read_latex_output(outdir)
    assert r"\begin{sphinxadmonition}{note}{Parsons problem}" in latex
    assert "return curmax" in latex
