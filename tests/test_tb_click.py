from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx
import pytest

from sphinx_touchbook.directives.array import TbArrayDirective
from sphinx_touchbook.directives.graph import TbGraphDirective

from sphinx_touchbook.directives.click import (
    TbClickDirective,
    TbClickHitDirective,
    TbClickMissDirective,
    resolve_selector,
)
from sphinx_touchbook.nodes import TbArrayNode, TbClickNode, TbClickRegionNode, TbGraphNode


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
    registered = {"tb-click": TbClickDirective, "tb-hit": TbClickHitDirective,
                  "tb-miss": TbClickMissDirective, "tb-array": TbArrayDirective,
                  "tb-graph": TbGraphDirective}
    previous = {name: directives._directives.get(name) for name in registered}
    for name, directive in registered.items():
        directives.register_directive(name, directive)
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
    assert r"\subsubsection*{Click question}" in latex
    assert "Click the comparison operator" in latex
    assert "WHERE age >= 18;" in latex
    assert "This line selects output columns." not in latex


def keyed_question(source, regions=None):
    regions = regions or """.. tb-hit:: b

   Correct keyed feedback.

.. tb-miss:: a

   Incorrect keyed feedback."""
    return (".. tb-click::\n   :name: keyed-question\n\n"
            "   Choose the second item, even though its value repeats.\n\n"
            + "\n".join("   " + line for line in source.splitlines()) + "\n\n"
            + "\n".join("   " + line for line in regions.splitlines()) + "\n")


ARRAY_SOURCE = """.. tb-array:: values
   :name: keyed-array
   :class: source-array
   :start-index: 10

   a = 'same'
   b = 'same'
   c = 'other'"""


def graph_source(style="graph"):
    return f""".. tb-graph:: values
   :name: keyed-graph
   :class: source-graph
   :style: {style}
   :indicators: current=b

   a['same'] -> b['same'] -> c['other']
   hidden['secret'] {{invisible}}"""


@pytest.mark.parametrize("source,source_type", [(ARRAY_SOURCE, TbArrayNode), (graph_source(), TbGraphNode)])
def test_keyed_sources_preserve_nodes_and_resolve_identity(source, source_type):
    document = parse_rst(keyed_question(source))
    assert not list(document.findall(nodes.system_message))
    question = next(document.findall(TbClickNode))
    source_node = next(question.findall(source_type))
    assert source_node["click_question_id"] == "keyed-question"
    assert list(source_node["click_regions"]) == ["b", "a"]
    assert [(region["selector"], region["correct"]) for region in question["regions"]] == [("b", True), ("a", False)]
    assert all("start" not in region for region in question["regions"])
    assert source_node["ids"] == ["keyed-array" if source_type is TbArrayNode else "keyed-graph"]


@pytest.mark.parametrize("source,regions,message", [
    (".. tb-array::\n\n   1 2 3", None, "explicitly keyed items"),
    (ARRAY_SOURCE, ".. tb-hit:: same\n\n   Feedback.", "visible source key"),
    (graph_source(), ".. tb-hit:: hidden\n\n   Feedback.", "visible source key"),
    (graph_source(), ".. tb-hit:: text:same\n\n   Feedback.", "visible source key"),
    (graph_source(), ".. tb-hit:: missing\n\n   Feedback.", "visible source key"),
    (ARRAY_SOURCE, ".. tb-hit:: a\n\n   Hit.\n\n.. tb-miss:: a\n\n   Miss.", "Duplicate tb-click source key"),
    (ARRAY_SOURCE + "\n\n" + graph_source(), None, "exactly one"),
    (".. code-block:: text\n\n   abc\n\n" + graph_source(), None, "exactly one"),
])
def test_keyed_source_validation(source, regions, message):
    document = parse_rst(keyed_question(source, regions))
    assert list(document.findall(nodes.system_message))
    assert message in document.astext()


@pytest.mark.parametrize("orientation", ["horizontal", "vertical"])
def test_array_question_html_has_native_keyed_controls(tmp_path, orientation):
    source = ARRAY_SOURCE.replace(":start-index: 10", f":start-index: 10\n   :orientation: {orientation}")
    outdir = build_sphinx(tmp_path, "html", keyed_question(source))
    soup = BeautifulSoup((outdir / "index.html").read_text(), "html.parser")
    assert len(soup.find_all("tb-click")) == len(soup.find_all("tb-array")) == 1
    array = soup.find("tb-array", id="keyed-array")
    assert "source-array" in array["class"]
    targets = array.select("td button.tb-click__target")
    assert [target["data-key"] for target in targets] == ["a", "b"]
    assert [target["data-correct"] for target in targets] == ["false", "true"]
    assert [target.get_text() for target in targets] == ["same", "same"]
    assert [target["aria-label"] for target in targets] == ["a: same", "b: same"]
    assert "10" in array.get_text() and "12" in array.get_text()
    for target in targets:
        assert soup.find(id=target["data-feedback-id"]) is not None
    assert not array.select('[data-key="c"].tb-click__target')


@pytest.mark.parametrize("style", ["graph", "list", "tree", "ring", "array"])
def test_graph_question_html_has_inline_keyed_controls(tmp_path, style):
    source = graph_source(style).replace(":style:", ':alt: A "graph" & <nodes>\n   :align: right\n   :style:')
    if style == "array":
        source = source.replace(":indicators: current=b", ":indicators: current=b finish=.end")
    outdir = build_sphinx(tmp_path, "html", keyed_question(source))
    soup = BeautifulSoup((outdir / "index.html").read_text(), "html.parser")
    assert len(soup.find_all("tb-click")) == len(soup.find_all("tb-graph")) == 1
    graph = soup.find("tb-graph", id="keyed-graph")
    assert "source-graph" in graph["class"]
    svg = graph.find("svg")
    assert svg is not None and svg["role"] == "group"
    assert svg["aria-label"] == 'A "graph" & <nodes>'
    assert svg.parent["align"] == "right"
    targets = svg.select(".tb-click__target")
    assert {target["data-key"]: target["data-correct"] for target in targets} == {"a": "false", "b": "true"}
    for target in targets:
        assert target.name == "g" and target["role"] == "button"
        assert target["tabindex"] == "0" and target["aria-pressed"] == "false"
        assert target["aria-label"] == f"{target['data-key']}: same"
        assert not target.has_attr("aria-describedby")
        assert soup.find(id=target["data-feedback-id"]) is not None
    assert not svg.find("a")
    assert "secret" not in svg.get_text()
    assert not svg.select('[data-key="current"], [data-key="hidden"], [data-key="c"]')
    assert all(item["id"].startswith("keyed-graph-") for item in svg.select("[id]"))


@pytest.mark.parametrize("source", [ARRAY_SOURCE, graph_source(), graph_source("array")])
@pytest.mark.parametrize("builder", ["text", "latex"])
def test_keyed_questions_keep_static_sources_without_answer_feedback(tmp_path, source, builder):
    outdir = build_sphinx(tmp_path, builder, keyed_question(source))
    output = (outdir / "index.txt").read_text() if builder == "text" else read_latex_output(outdir)
    assert "Choose the second item" in output and "same" in output and "other" in output
    assert "Correct keyed feedback" not in output
    assert "Incorrect keyed feedback" not in output
    assert "tb-click-region-" not in output
    if builder == "latex" and "tb-graph" in source:
        assert list(outdir.glob("tb-graph*.pdf"))


def test_graph_question_has_keyed_buttons_when_diagram_is_unavailable(tmp_path, monkeypatch):
    from sphinx_touchbook.generators import graph
    monkeypatch.setattr(graph, "render_graph", lambda *args, **kwargs: None)
    outdir = build_sphinx(tmp_path, "html", keyed_question(graph_source()))
    soup = BeautifulSoup((outdir / "index.html").read_text(), "html.parser")
    assert {target["data-key"] for target in soup.select("tb-graph button.tb-click__target")} == {"a", "b"}
    assert "other" in soup.find("tb-graph").get_text()


@pytest.mark.parametrize("kind", ["array", "graph"])
def test_keyed_controls_escape_literal_markup_and_keep_empty_values_selectable(tmp_path, kind):
    value = '<script>alert("x")</script> & same'
    body = (f"a = '{value}'\nb = ''" if kind == "array" else
            f"a['{value}'] -> b['']")
    source = f".. tb-{kind}::\n\n" + "\n".join("   " + line for line in body.splitlines())
    outdir = build_sphinx(tmp_path, "html", keyed_question(source))
    soup = BeautifulSoup((outdir / "index.html").read_text(), "html.parser")
    rendered = soup.find(f"tb-{kind}")
    assert not rendered.find("script")
    targets = {target["data-key"]: target for target in rendered.select(".tb-click__target")}
    assert targets["a"]["aria-label"] == f"a: {value}"
    assert targets["b"]["aria-label"] == "b: Empty value"
    assert value in targets["a"].get_text()
    assert all(not target.has_attr("aria-describedby") for target in targets.values())
