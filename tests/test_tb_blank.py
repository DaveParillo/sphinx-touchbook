from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.blank import TbBlankDirective
from sphinx_touchbook.nodes import TbBlankInputNode, TbBlankNode


BLANK_RST = """
.. tb-blank::
   :name: blank-example

   The capital of France is {{blank}}.

   .. tb-answer::
      :match: Paris
      :feedback: Correct.
      :hint: London; London is the capital of the United Kingdom.
      :incorrect: Try again.
"""


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-blank")
    directives.register_directive("tb-blank", TbBlankDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-blank", None)
        else:
            directives._directives["tb-blank"] = previous
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


def test_directive_parses_single_blank_and_answer_options():
    document = parse_rst(BLANK_RST)

    node = next(document.findall(TbBlankNode))
    blank = next(document.findall(TbBlankInputNode))
    assert node["ids"] == ["blank-example"]
    assert node["blanks"] == ["blank1"]
    assert blank["blank_id"] == "blank1"
    assert node["answers"]["blank1"]["matches"] == ["Paris"]
    assert node["answers"]["blank1"]["hints"] == [
        {"value": "London", "feedback": "London is the capital of the United Kingdom."}
    ]
    assert node["answers"]["blank1"]["incorrect"] == "Try again."


def test_directive_requires_named_answers_for_multiple_blanks():
    document = parse_rst(
        """
.. tb-blank::

   {{blank:first}} and {{blank:second}}

   .. tb-answer::
      :match: first
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "must name a blank" in document.astext()


def test_directive_rejects_malformed_hint():
    document = parse_rst(
        """
.. tb-blank::

   {{blank}}

   .. tb-answer::
      :match: ok
      :hint: missing separator
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "value; feedback" in document.astext()


def test_html_build_emits_input_config_and_assets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        f"""
Title
=====

{BLANK_RST}
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-blank", id="blank-example")
    assert element is not None
    assert element["case-sensitive"] == "false"
    assert element["trim"] == "true"
    input_element = element.find("input", class_="tb-blank__input")
    assert input_element["data-blank-id"] == "blank1"
    config = element.find("script", class_="tb-blank__config")
    assert '"Paris"' in config.string
    assert "London is the capital" in config.string
    assert element.find("button", class_="tb-blank__check") is not None
    assert (outdir / "_static" / "tb-blank.js").exists()
    assert (outdir / "_static" / "tb-blank.css").exists()


def test_text_builder_renders_static_blank(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        f"""
Title
=====

{BLANK_RST}
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "[Fill in the blank]" in text
    assert "The capital of France is" in text
    assert "________" in text
    assert "Paris" not in text


def test_latex_builder_renders_static_blank(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        f"""
Title
=====

{BLANK_RST}
""",
    )

    latex = read_latex_output(outdir)
    assert r"\begin{sphinxadmonition}{note}{Fill in the blank}" in latex
    assert r"\underline{\hspace{2cm}}" in latex
    assert "Paris" not in latex
