from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils.utils import new_document
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from sphinx.application import Sphinx

from sphinx_touchbook.directives.reveal import TbRevealDirective
from sphinx_touchbook.nodes import TbRevealNode


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-reveal")
    directives.register_directive("tb-reveal", TbRevealDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-reveal", None)
        else:
            directives._directives["tb-reveal"] = previous
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


def test_directive_parses_semantic_node_defaults():
    document = parse_rst(
        """
.. tb-reveal::

   Hidden content.
"""
    )

    node = next(document.findall(TbRevealNode))
    assert len(node["ids"]) == 1
    assert node["ids"][0].startswith("tbrevealnode-")
    assert node["showtitle"] == "Show"
    assert node["hidetitle"] == "Hide"
    assert node["modal"] is False
    assert node["modaltitle"] == "Message from the author"
    assert "Hidden content." in node.astext()


def test_directive_parses_modal_options():
    document = parse_rst(
        """
.. tb-reveal::
   :showtitle: Open
   :hidetitle: Close
   :modal:
   :modaltitle: Author note

   Hidden content.
"""
    )

    node = next(document.findall(TbRevealNode))
    assert node["showtitle"] == "Open"
    assert node["hidetitle"] == "Close"
    assert node["modal"] is True
    assert node["modaltitle"] == "Author note"


def test_html_build_emits_one_custom_element_and_assets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-reveal::
   :showtitle: Open
   :hidetitle: Close

   Hidden **content**.
""",
    )

    html = (outdir / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.find_all("tb-reveal")
    assert len(elements) == 1
    element = elements[0]
    assert element["showtitle"] == "Open"
    assert element["hidetitle"] == "Close"
    assert "modal" not in element.attrs
    assert element.find("details", class_="tb-reveal__fallback") is not None
    assert element.find("summary").get_text(strip=True) == "Open"
    assert "Hidden" in element.get_text()
    assert (outdir / "_static" / "tb-reveal.js").exists()
    assert (outdir / "_static" / "tb-reveal.css").exists()
    assert "tb-reveal.js" in html
    assert "tb-reveal.css" in html


def test_html_generates_id_when_omitted(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-reveal::

   Hidden content.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-reveal")
    assert element is not None
    assert element["id"]


def test_html_uses_id_option(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-reveal::
   :id: reveal-id

   Hidden content.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-reveal")
    assert element is not None
    assert element["id"] == "reveal-id"


def test_modal_html_attributes(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-reveal::
   :modal:
   :modaltitle: Author note

   Hidden content.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    elements = soup.find_all("tb-reveal")
    assert len(elements) == 1
    element = elements[0]
    assert "modal" in element.attrs
    assert element["modaltitle"] == "Author note"


def test_text_builder_preserves_content(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        """
Title
=====

.. tb-reveal::
   :showtitle: Explanation

   Hidden content for static output.
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "Explanation" in text
    assert "Hidden content for static output." in text


def test_web_component_asset_defines_custom_element():
    source = Path("src/sphinx_touchbook/static/tb-reveal.js").read_text(encoding="utf-8")
    assert 'customElements.define("tb-reveal", TbReveal)' in source
    assert 'button.setAttribute("aria-expanded", "false")' in source
    assert 'button.setAttribute("aria-controls", panelId)' in source
    assert 'openButton.setAttribute("aria-haspopup", "dialog")' in source
    assert "showModal" in source
    assert "Math.random" not in source
