from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.choice import TbChoiceDirective
from sphinx_touchbook.nodes import TbChoiceNode, TbChoiceOptionNode


CHOICE_RST = """
.. tb-choice::
   :name: choice-example

   What does the following code print when ``x`` has been set to 187?

   .. code-block:: java

      if (x < 0)
      {
          System.out.println("x is negative");
      }
      else
      {
          System.out.println("x is positive");
      }

   - x is negative

     - This only prints for values less than zero.

   - x is positive

     + The first condition is false, so the else block executes.
"""


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-choice")
    directives.register_directive("tb-choice", TbChoiceDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-choice", None)
        else:
            directives._directives["tb-choice"] = previous
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


def test_directive_parses_single_answer_choice():
    document = parse_rst(CHOICE_RST)

    node = next(document.findall(TbChoiceNode))
    options = list(node.findall(TbChoiceOptionNode))
    assert node["ids"] == ["choice-example"]
    assert node["multiple"] is False
    assert len(options) == 2
    assert [option["correct"] for option in options] == [False, True]
    assert "What does the following code print" in node.astext()
    assert "x is positive" in node.astext()


def test_directive_parses_multiple_answer_choice():
    document = parse_rst(
        """
.. tb-choice::

   Select prime numbers.

   - 2

     + Prime.

   - 3

     + Prime.

   - 4

     - Composite.
"""
    )

    node = next(document.findall(TbChoiceNode))
    assert node["multiple"] is True
    assert [option["correct"] for option in node.findall(TbChoiceOptionNode)] == [True, True, False]


def test_directive_parses_random_flag():
    document = parse_rst(
        """
.. tb-choice::
   :random:

   Pick one.

   - A

     + Correct.

   - B

     - Incorrect.
"""
    )

    node = next(document.findall(TbChoiceNode))
    assert node["random"] is True


def test_directive_reports_missing_correct_answer():
    document = parse_rst(
        """
.. tb-choice::

   Pick one.

   - A

     - Feedback.
"""
    )

    assert list(document.findall(nodes.system_message))
    assert "at least one correct answer" in document.astext()


def test_html_build_emits_radio_choice(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        f"""
Title
=====

{CHOICE_RST}
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-choice", id="choice-example")
    assert element is not None
    assert element["mode"] == "single"
    assert element.find("div", class_="highlight-java") is not None
    inputs = element.find_all("input", class_="tb-choice__input")
    assert [item["type"] for item in inputs] == ["radio", "radio"]
    assert len({item["name"] for item in inputs}) == 1
    options = element.find_all("div", class_="tb-choice__option")
    assert [option["data-correct"] for option in options] == ["false", "true"]
    assert "x is negative" in options[0].get_text(" ", strip=True)
    assert "less than zero" in options[0].find("div", class_="tb-choice__feedback").get_text(" ", strip=True)
    assert element.find("button", class_="tb-choice__check").get_text(strip=True) == "Check answer"
    assert (outdir / "_static" / "tb-choice.js").exists()
    assert (outdir / "_static" / "tb-choice.css").exists()


def test_html_build_emits_checkbox_choice_for_multiple_correct(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-choice::

   Select prime numbers.

   - 2

     + Prime.

   - 3

     + Prime.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-choice")
    assert element["mode"] == "multiple"
    assert [item["type"] for item in element.find_all("input")] == ["checkbox", "checkbox"]


def test_html_build_emits_random_attribute(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-choice::
   :random:

   Pick one.

   - A

     + Correct.

   - B

     - Incorrect.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-choice")
    assert element["random"] == "true"


def test_text_builder_renders_choice_and_feedback(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        f"""
Title
=====

{CHOICE_RST}
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "[Question]" in text
    assert "[*]" in text
    assert "Feedback:" in text
    assert "The first condition is false" in text


def test_latex_builder_renders_choice_and_feedback(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        f"""
Title
=====

{CHOICE_RST}
""",
    )

    latex = read_latex_output(outdir)
    assert r"\begin{sphinxadmonition}{note}{Question}" in latex
    assert "[*]" in latex
    assert "Feedback" in latex
