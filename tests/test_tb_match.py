from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.match import TbMatchDirective
from sphinx_touchbook.nodes import TbMatchDistractorNode, TbMatchNode, TbMatchPairNode


MATCH_RST = """
.. tb-match::
   :name: match-example

   Match each term with its meaning.

   compiler
      Translates source code into executable code.

   interpreter
      Executes source code directly.

   linker
      Combines object files into a program.
"""


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-match")
    directives.register_directive("tb-match", TbMatchDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-match", None)
        else:
            directives._directives["tb-match"] = previous
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


def test_directive_parses_definition_list_pairs():
    document = parse_rst(MATCH_RST)

    node = next(document.findall(TbMatchNode))
    pairs = list(node.findall(TbMatchPairNode))
    assert node["ids"] == ["match-example"]
    assert len(pairs) == 3
    assert [pair[0].astext() for pair in pairs] == ["compiler", "interpreter", "linker"]
    assert "Translates source code" in pairs[0][1].astext()


def test_directive_requires_definition_list():
    document = parse_rst(
        """
.. tb-match::

   Match these.

   - compiler
   - interpreter
"""
    )

    messages = list(document.findall(nodes.system_message))
    assert messages
    assert "definition list" in document.astext()


def test_directive_parses_semicolon_and_line_distractors():
    document = parse_rst(
        """
.. tb-match::
   :distractors: Formats source code; Optimizes database queries
                 Deploys web applications

   Match these.

   compiler
      Translates source code.

   interpreter
      Executes source code.
"""
    )

    node = next(document.findall(TbMatchNode))
    distractors = list(node.findall(TbMatchDistractorNode))
    assert [distractor.astext() for distractor in distractors] == [
        "Formats source code",
        "Optimizes database queries",
        "Deploys web applications",
    ]


def test_html_build_emits_sources_targets_and_assets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        f"""
Title
=====

{MATCH_RST}
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-match", id="match-example")
    assert element is not None
    assert "Match each term" in element.find("div", class_="tb-match__prompt").get_text(" ", strip=True)
    sources = element.find_all("label", class_="tb-match__source")
    assert [source.get_text(" ", strip=True) for source in sources] == ["compiler", "interpreter", "linker"]
    selects = element.find_all("select", class_="tb-match__select")
    assert [select["data-answer"] for select in selects] == ["0", "1", "2"]
    assert all(select.find("option", value="") for select in selects)
    assert all(len(select.find_all("option")) == 4 for select in selects)
    assert "Translates source code into executable code." in selects[0].get_text(" ", strip=True)
    assert element.find("section", class_="tb-match__definitions") is None
    assert element.find("button", class_="tb-match__check").has_attr("disabled")
    assert element.find("button", class_="tb-match__reset") is None
    assert (outdir / "_static" / "tb-match.js").exists()
    assert (outdir / "_static" / "tb-match.css").exists()


def test_html_build_includes_distractors_as_unmatched_select_options(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-match::
   :name: match-distractors
   :distractors: Builds a final executable; Runs automated tests

   Match these.

   compiler
      Compiles source code.

   interpreter
      Executes source code.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-match", id="match-distractors")
    selects = element.find_all("select", class_="tb-match__select")
    assert all(len(select.find_all("option")) == 5 for select in selects)
    options = selects[0].find_all("option")
    assert [option.get_text(strip=True) for option in options] == [
        "Choose a definition",
        "Builds a final executable",
        "Compiles source code.",
        "Executes source code.",
        "Runs automated tests",
    ]
    assert options[1]["value"] == "distractor-0"
    assert options[4]["value"] == "distractor-1"
    assert [select["data-answer"] for select in selects] == ["0", "1"]


def test_text_builder_renders_prompt_sources_and_targets_without_pairs(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        f"""
Title
=====

{MATCH_RST}
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "[Matching question]" in text
    assert "Match each term" in text
    assert "Sources:" in text
    assert "- compiler" in text
    assert "Targets:" in text
    assert "source code into executable code." in normalized
    assert "Executes source code directly." in normalized
    assert "Combines object files into a program." in normalized


def test_latex_builder_renders_prompt_sources_and_targets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        f"""
Title
=====

{MATCH_RST}
""",
    )

    latex = read_latex_output(outdir)
    assert r"\begin{sphinxadmonition}{note}{Matching question}" in latex
    assert "Match each term" in latex
    assert r"\textbf{Sources}" in latex
    assert "compiler" in latex
    assert r"\textbf{Targets}" in latex
    assert "Translates source code into executable code." in latex
