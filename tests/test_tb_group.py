from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.tabs import TbGroupDirective, TbTabDirective
from sphinx_touchbook.nodes import TbGroupNode, TbTabNode


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous_group = directives._directives.get("tb-group")
    previous_tab = directives._directives.get("tb-tab")
    directives.register_directive("tb-group", TbGroupDirective)
    directives.register_directive("tb-tab", TbTabDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous_group is None:
            directives._directives.pop("tb-group", None)
        else:
            directives._directives["tb-group"] = previous_group
        if previous_tab is None:
            directives._directives.pop("tb-tab", None)
        else:
            directives._directives["tb-tab"] = previous_tab
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


def test_directives_parse_semantic_nodes_without_group_id():
    document = parse_rst(
        """
.. tb-group::

   .. tb-tab:: First tab

      First content.

   .. tb-tab:: Second tab

      Second content.
"""
    )

    group = next(document.findall(TbGroupNode))
    tabs = list(group.findall(TbTabNode))
    assert len(group["ids"]) == 1
    assert group["ids"][0].startswith("tbgroupnode-")
    assert len(tabs[0]["ids"]) == 1
    assert len(tabs[1]["ids"]) == 1
    assert tabs[0]["ids"][0].startswith("tbtabnode-")
    assert tabs[1]["ids"][0].startswith("tbtabnode-")
    assert [tab["label"] for tab in tabs] == ["First tab", "Second tab"]
    assert "First content." in tabs[0].astext()
    assert "Second content." in tabs[1].astext()


def test_group_accepts_optional_name():
    document = parse_rst(
        """
.. tb-group::
   :name: example-tabs

   .. tb-tab:: First tab
      :name: first-tab

      First content.
"""
    )

    group = next(document.findall(TbGroupNode))
    tab = next(document.findall(TbTabNode))
    assert group["ids"] == ["example-tabs"]
    assert tab["ids"] == ["first-tab"]


def test_group_requires_at_least_one_tab():
    document = parse_rst(
        """
.. tb-group::

   This content is ignored.
"""
    )

    assert "tb-group must contain at least one immediate tb-tab directive" in document.astext()


def test_html_build_emits_custom_elements_and_assets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-group::

   .. tb-tab:: First

      First **content**.

   .. tb-tab:: Second

      Second content.
""",
    )

    html = (outdir / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    groups = soup.find_all("tb-group")
    assert len(groups) == 1
    group = groups[0]
    assert group["id"]
    tabs = group.find_all("tb-tab")
    assert len(tabs) == 2
    assert [tab["label"] for tab in tabs] == ["First", "Second"]
    assert group.find("div", class_="tb-group__fallback") is not None
    assert group.find("p", class_="tb-tab__label") is not None
    assert group.find("p", class_="tb-tab__title") is None
    assert "First" in group.get_text()
    assert "Second content" in group.get_text()
    assert (outdir / "_static" / "tb-group.js").exists()
    assert (outdir / "_static" / "tb-group.css").exists()
    assert "tb-group.js" in html
    assert "tb-group.css" in html


def test_html_uses_group_name_option(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-group::
   :name: group-one

   .. tb-tab:: First
      :name: first-tab

      First content.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    group = soup.find("tb-group")
    assert group is not None
    assert group["id"] == "group-one"
    tab = group.find("tb-tab")
    assert tab is not None
    assert tab["id"] == "first-tab"


def test_text_builder_preserves_tabs(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        """
Title
=====

.. tb-group::

   .. tb-tab:: First

      First content.

   .. tb-tab:: Second

      Second content.
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "First" in text
    assert "First content." in text
    assert "Second" in text
    assert "Second content." in text


def test_web_component_asset_defines_custom_element():
    source = Path("src/sphinx_touchbook/static/tb-group.js").read_text(encoding="utf-8")
    assert 'customElements.define("tb-group", TbGroup)' in source
    assert 'tablist.setAttribute("role", "tablist")' in source
    assert 'button.setAttribute("role", "tab")' in source
    assert 'panel.setAttribute("role", "tabpanel")' in source
    assert "ArrowRight" in source
    assert "ArrowLeft" in source
    assert "tb-tab__title" not in source
    assert "Math.random" not in source
