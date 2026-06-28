from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.order import TbOrderDirective
from sphinx_touchbook.nodes import TbOrderItemNode, TbOrderNode, TbOrderPromptNode


ORDER_RST = """
.. tb-order::
   :name: order-example

   - Wake up
   - Eat breakfast
   - Go to class
"""


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-order")
    directives.register_directive("tb-order", TbOrderDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-order", None)
        else:
            directives._directives["tb-order"] = previous
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


def test_directive_parses_bullet_list_items():
    document = parse_rst(ORDER_RST)

    node = next(document.findall(TbOrderNode))
    items = list(document.findall(TbOrderItemNode))
    assert node["ids"] == ["order-example"]
    assert [item["index"] for item in items] == [0, 1, 2]
    assert [item.astext() for item in items] == ["Wake up", "Eat breakfast", "Go to class"]


def test_directive_requires_at_least_two_lines():
    document = parse_rst(
        """
.. tb-order::

   - Only one item
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "at least two list items" in document.astext()


def test_directive_parses_prompt_before_item_list():
    document = parse_rst(
        """
.. tb-order::

   Put these steps in chronological order.

   .. note::

      Think about what must happen first.

   - Wake up
   - Eat breakfast
   - Go to class
"""
    )

    node = next(document.findall(TbOrderNode))
    prompt = next(document.findall(TbOrderPromptNode))
    items = list(document.findall(TbOrderItemNode))
    assert "chronological order" in prompt.astext()
    assert "Think about what must happen first" in prompt.astext()
    assert [item.astext() for item in items] == ["Wake up", "Eat breakfast", "Go to class"]
    assert prompt.parent is node


def test_directive_rejects_content_after_item_list():
    document = parse_rst(
        """
.. tb-order::

   - First
   - Second

   Extra content.
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "after the item list" in document.astext()


def test_html_build_emits_items_controls_and_assets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        f"""
Title
=====

{ORDER_RST}
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-order", id="order-example")
    assert element is not None
    items = element.find_all("li", class_="tb-order__item")
    assert sorted(item["data-order"] for item in items) == ["0", "1", "2"]
    assert all(item.find("button", class_="tb-order__move-up") for item in items)
    assert all(item.find("button", class_="tb-order__move-down") for item in items)
    assert element.find("button", class_="tb-order__check") is not None
    assert (outdir / "_static" / "tb-order.js").exists()
    assert (outdir / "_static" / "tb-order.css").exists()


def test_html_build_emits_prompt_before_item_list(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-order::
   :name: order-with-prompt

   Put these in order.

   - First
   - Second
   - Third
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-order", id="order-with-prompt")
    prompt = element.find("div", class_="tb-order__prompt")
    assert prompt is not None
    assert "Put these in order." in prompt.get_text(" ", strip=True)
    assert [item.get_text(" ", strip=True) for item in element.find_all("div", class_="tb-order__content")] == [
        "First",
        "Second",
        "Third",
    ]


def test_text_builder_renders_static_ordering_question(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        f"""
Title
=====

{ORDER_RST}
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "[Ordering question]" in text
    assert "Items:" in text
    assert "Wake up" in text


def test_latex_builder_renders_static_ordering_question(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        f"""
Title
=====

{ORDER_RST}
""",
    )

    latex = read_latex_output(outdir)
    assert r"\begin{sphinxadmonition}{note}{Ordering question}" in latex
    assert "Wake up" in latex
