from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.micro_parsons import TbMicroParsonsDirective
from sphinx_touchbook.nodes import (
    TbMicroParsonsNode,
    TbMicroParsonsPromptNode,
    TbMicroParsonsTokenNode,
)


MICRO_PARSONS_RST = """
.. tb-micro-parsons::
   :name: micro-parsons-example
   :distractor: float; ==

   Arrange the tokens to create a valid assignment statement.

   - int
   - x
   - =
   - 42
   - ;
"""


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-micro-parsons")
    directives.register_directive("tb-micro-parsons", TbMicroParsonsDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-micro-parsons", None)
        else:
            directives._directives["tb-micro-parsons"] = previous
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


def test_directive_parses_tokens_prompt_and_distractors():
    document = parse_rst(MICRO_PARSONS_RST)

    node = next(document.findall(TbMicroParsonsNode))
    prompt = next(document.findall(TbMicroParsonsPromptNode))
    tokens = list(document.findall(TbMicroParsonsTokenNode))
    assert node["ids"] == ["micro-parsons-example"]
    assert node["has_distractors"] is True
    assert "valid assignment" in prompt.astext()
    assert [token["label"] for token in tokens] == ["int", "x", "=", "42", ";", "float", "=="]
    assert [token["distractor"] for token in tokens] == [False, False, False, False, False, True, True]


def test_directive_rejects_too_few_tokens():
    document = parse_rst(
        """
.. tb-micro-parsons::

   - only
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "at least two tokens" in document.astext()


def test_html_build_emits_tokens_controls_and_assets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        f"""
Title
=====

{MICRO_PARSONS_RST}
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-micro-parsons", id="micro-parsons-example")
    assert element is not None
    assert element["data-has-distractors"] == "true"
    assert element.find("ol", class_="tb-micro-parsons__source") is not None
    assert element.find("ol", class_="tb-micro-parsons__target") is not None
    tokens = element.find_all("li", class_="tb-micro-parsons__token")
    assert len(tokens) == 7
    assert any(token["data-distractor"] == "true" for token in tokens)
    assert all(token["data-location"] == "source" for token in tokens)
    assert all(token.find("button", class_="tb-micro-parsons__token-button") for token in tokens)
    assert element.find("button", class_="tb-micro-parsons__check") is not None
    assert (outdir / "_static" / "tb-micro-parsons.js").exists()
    assert (outdir / "_static" / "tb-micro-parsons.css").exists()


def test_html_build_omits_toggle_when_no_distractors(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-micro-parsons::
   :name: no-distractors

   - a
   - b
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-micro-parsons", id="no-distractors")
    assert element["data-has-distractors"] == "false"
    assert element.find("button", class_="tb-micro-parsons__token-button") is not None


def test_text_builder_renders_static_micro_parsons_question(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        f"""
Title
=====

{MICRO_PARSONS_RST}
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "[Micro Parsons problem]" in text
    assert "Tokens:" in text
    assert "Answer:" in text
    assert "________________________________" in text


def test_latex_builder_renders_static_micro_parsons_question(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        f"""
Title
=====

{MICRO_PARSONS_RST}
""",
    )

    latex = read_latex_output(outdir)
    assert r"\begin{sphinxadmonition}{note}{Micro Parsons problem}" in latex
    assert r"\textbf{Answer:}" in latex
