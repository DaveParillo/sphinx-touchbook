from __future__ import annotations

from io import StringIO
from copy import deepcopy
from pathlib import Path
import shutil
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
import pytest

from sphinx_touchbook.directives.graph import TbGraphDirective
from sphinx_touchbook.generators.graph import graph_description, graph_dot
from sphinx_touchbook.nodes import TbGraphNode
from sphinx_touchbook.graph_styles import resolve_graph_styles
from sphinx_touchbook.generators import graph as graph_generator
from sphinx_touchbook.generators.graph_array import cell_dimensions, measurement_dot


def graph_source(body="", options="", key=""):
    return f".. tb-graph:: {key}\n{options}\n\n" + "\n".join(
        f"   {line}" for line in body.splitlines()) + "\n"


def parse_rst(source):
    settings = get_default_settings(Parser)
    settings.warning_stream = StringIO()
    document = new_document("graph.rst", settings=settings)
    previous = directives._directives.get("tb-graph")
    directives.register_directive("tb-graph", TbGraphDirective)
    try:
        Parser().parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-graph", None)
        else:
            directives._directives["tb-graph"] = previous
    return document


def test_complete_graph_with_forward_references_chains_and_common_options():
    document = parse_rst(graph_source("a['10'] -> b -> c[\"30\"]\nb[20]", """   :name: graph-target
   :class: first second
   :label: Chain
   :caption: A caption
   :highlight: chain.node[b] chain.node[b]""", "chain"))
    node = next(document.findall(TbGraphNode))
    assert node["key"] == "chain"
    assert node["ids"] == ["graph-target"]
    assert node["classes"] == ["first", "second"]
    assert {item["key"]: item["value"] for item in node["nodes"]} == {"a": "10", "b": "20", "c": "30"}
    assert [(edge["source"], edge["target"]) for edge in node["edges"]] == [("a", "b"), ("b", "c")]
    assert node["highlighted"] == ["b"]
    assert node.source == "graph.rst"


def test_labels_are_literals_and_punctuation_is_not_graph_syntax():
    document = parse_rst(graph_source(r'''a['it\'s # -> [literal] **text**'] -some-role-> b["a \"quote\" and a\\b"]
c[ -2.50e+2 ]
d[''] # comment'''))
    node = next(document.findall(TbGraphNode))
    assert [item["value"] for item in node["nodes"]] == [
        "it's # -> [literal] **text**", 'a "quote" and a\\b', "-2.50e+2", ""]
    assert node["edges"][0]["relationship"] == "some-role"


@pytest.mark.parametrize("body", ["", "# empty\n\n# still empty"])
def test_empty_graph(body):
    node = next(parse_rst(graph_source(body)).findall(TbGraphNode))
    assert node["nodes"] == [] and node["edges"] == []
    assert node["key"] is None
    assert node["label"] == "" and node["caption"] == ""
    assert node["style_name"] == "graph"


def test_cycles_self_edges_disconnected_nodes_and_named_parallel_edges():
    source = "a[1] -> b[2] -> a\na -self-> a\na -first-> c[3]\na -second-> c\nd[4]\nb -self-> b"
    node = next(parse_rst(graph_source(source)).findall(TbGraphNode))
    assert len(node["nodes"]) == 4 and len(node["edges"]) == 6


def test_invisible_nodes_and_edges_have_independent_visibility():
    source = "a[10] -next-> hidden['secret'] {invisible}\na -spacing-> {invisible} spacer['private'] {invisible}"
    node = next(parse_rst(graph_source(source, "   :highlight: graph.node[hidden]", "graph")).findall(TbGraphNode))
    assert [item["invisible"] for item in node["nodes"]] == [False, True, True]
    assert [edge["invisible"] for edge in node["edges"]] == [False, True]
    description = graph_description(node).astext()
    assert "“10” points to an undisplayed endpoint through the “next” relationship." in description
    for hidden in ("secret", "private", "hidden", "spacer", "spacing", "highlighted"):
        assert hidden not in description
    assert 'n1 [label="secret", style="invis"]' in graph_dot(node)
    assert 'n0 -> n2 [label="spacing", style="invis"]' in graph_dot(node)


@pytest.mark.parametrize("body,options,key,message", [
    ("a[1] -> missing", "", "", "no value declaration"),
    ("a -> b", "", "", "no value declaration"),
    ("a", "", "", "standalone node"),
    ("a[1]\na[1]", "", "", "Duplicate node declaration"),
    ("a[1]->b[2]", "", "", "whitespace"),
    ("root-left->child", "", "", "whitespace"),
    ("a[1] ->b[2]", "", "", "whitespace"),
    ("a[1]-> b[2]", "", "", "whitespace"),
    ("a [1]", "", "", "edge operator"),
    ("a[1]; b[2]", "", "", "edge operator"),
    ("a[01]", "", "", "Expected ']'"),
    ("a[text]", "", "", "quoted strings"),
    ("a['unterminated]", "", "", "Unterminated string"),
    (r"a['line\nbreak']", "", "", "Invalid string escape"),
    ("a['a' 'b']", "", "", "Expected ']'"),
    ("null[1]", "", "", "Invalid graph key"),
    ("a[1] -> null", "", "", "Invalid graph key"),
    ("a[1] -null-> b[2]", "", "", "Invalid graph key"),
    ("a[1]", "", "null", "Invalid graph key"),
    ("a[1] -> b[2]\na -> b", "", "", "parallel edge"),
    ("a[1] -next-> b[2]\na -next-> c[3]", "", "", "Duplicate relationship"),
    ("a[1] -> b[2]\na -next-> b", "", "", "parallel edge"),
    ("a[1] -next-> b[2]\na -> b", "", "", "parallel edge"),
    ("a[1] - next-> b[2]", "", "", "edge operator"),
    ("a[1] -> {invisible}b[2]", "", "", "whitespace"),
    ("a[1]\na {invisible}", "", "", "edge operator"),
    ("a[1]", "   :highlight: graph.node[a]", "", "explicit graph object key"),
    ("a[1]", "   :highlight: other.node[a]", "graph", "Invalid local"),
    ("a[1]", "   :highlight: graph.slot[0]", "graph", "Invalid local"),
    ("a[1]", "   :highlight: graph.node[missing]", "graph", "Unknown graph node"),
])
def test_invalid_graph_reports_context(body, options, key, message):
    document = parse_rst(graph_source(body, options, key))
    assert not list(document.findall(TbGraphNode))
    error = next(document.findall(nodes.system_message))
    assert message in error.astext()
    assert "tb-graph" in error.astext()
    assert error["line"] >= 1


@pytest.mark.parametrize("options", ["   :id: legacy", "   :layout: neato",
                                     "   :label: One\n   :label: Two"])
def test_unknown_and_repeated_options_are_errors(options):
    document = parse_rst(graph_source("a[1]", options))
    assert not list(document.findall(TbGraphNode))
    assert list(document.findall(nodes.system_message))


def test_unknown_style_is_an_error():
    document = parse_rst(graph_source("a[1]", "   :style: missing"))
    assert not list(document.findall(TbGraphNode))
    assert "Unknown graph style" in next(document.findall(nodes.system_message)).astext()


def test_array_and_ring_defaults_and_custom_bases():
    styles = resolve_graph_styles({
        "vertical-array": {"base": "array", "orientation": "vertical"},
        "custom-ring": {"base": "ring", "fill": "gold"},
    })
    assert styles["array"]["orientation"] == "horizontal"
    assert styles["array"]["unused-fill"] == "#eeeeee"
    assert styles["ring"]["shape"] == "ellipse"
    assert styles["vertical-array"]["layout"] == "array"
    assert styles["vertical-array"]["orientation"] == "vertical"
    assert styles["custom-ring"]["layout"] == "ring"
    assert styles["custom-ring"]["fill"] == "gold"
    plain = next(parse_rst(graph_source("a[8]", "   :style: array")).findall(TbGraphNode))
    indexed = next(parse_rst(graph_source("a[8]", "   :style: array\n   :show-indices:")).findall(TbGraphNode))
    assert plain["show_indices"] is False and indexed["show_indices"] is True
    invalid = parse_rst(graph_source("a[8]", "   :show-indices: true"))
    assert not list(invalid.findall(TbGraphNode))


def test_indicators_resolve_local_nodes_and_preserve_graph_data():
    node = next(parse_rst(graph_source("a[8] -> b\nb[13]", """   :style: array
   :indicators: head=a current=b
      tail=b""")).findall(TbGraphNode))
    assert node["key"] is None
    assert node["indicators"] == [
        {"key": "head", "target": "a"}, {"key": "current", "target": "b"},
        {"key": "tail", "target": "b"}]
    assert [item["key"] for item in node["nodes"]] == ["a", "b"]
    assert len(node["edges"]) == 1
    assert "Indicator “current” points to cell 1, value “13”." in graph_description(node).astext()
    ordinary = next(parse_rst(graph_source("a[8]")).findall(TbGraphNode))
    assert ordinary["indicators"] == []


@pytest.mark.parametrize("definition,body,style,message", [
    ("current=missing", "a[8]", "array", "Unknown indicator target"),
    ("head=a current=b", "a[8] -> b[13]", "tree", "at most one indicator"),
    ("current=a", "a[8] {invisible}", "array", "invisible node"),
    ("current=a current=b", "a[8]\nb[13]", "array", "Duplicate indicator label"),
    ("null=a", "a[8]", "array", "Invalid indicator key"),
    ("current=null", "a[8]", "array", "Invalid graph key"),
    ("current=a", "", "array", "Unknown indicator target"),
    ("current=a=b", "a[8]", "array", "Invalid indicator"),
    ("current=values.node[a]", "a[8]", "array", "Invalid indicator"),
    ("current = a", "a[8]", "array", "Invalid indicator"),
    ('"current value"=a', "a[8]", "array", "Invalid indicator"),
])
def test_invalid_indicators_report_context(definition, body, style, message):
    document = parse_rst(graph_source(body, f"   :style: {style}\n   :indicators: {definition}"))
    assert not list(document.findall(TbGraphNode))
    assert message in next(document.findall(nodes.system_message)).astext()


@pytest.mark.parametrize("style", ["graph", "list", "tree", "ring"])
def test_graph_indicators_are_annotations_and_not_relationships(style):
    node = next(parse_rst(graph_source("a[8] -> b[13]", f"   :style: {style}\n   :indicators: current=b")).findall(TbGraphNode))
    original = deepcopy(node.attributes)
    assert len(node["nodes"]) == 2 and len(node["edges"]) == 1
    assert "Indicator “current” points to “13”." in graph_description(node).astext()
    graph_dot(node)
    assert node.attributes == original
    hidden = parse_rst(graph_source("a[8] {invisible}", f"   :style: {style}\n   :indicators: current=a"))
    assert not list(hidden.findall(TbGraphNode))
    assert "invisible node" in next(hidden.findall(nodes.system_message)).astext()


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("builder", ["html", "text", "latex"])
@pytest.mark.parametrize("style", ["graph", "list", "tree", "ring"])
def test_indicators_for_other_graph_styles_across_builders(tmp_path, builder, style):
    if style == "ring" and builder != "text" and shutil.which("circo") is None:
        pytest.skip("Graphviz circo is required")
    definitions = "current=b" if style == "tree" else "head=a current=b other=b"
    body = "a[8] -> b[13]\na -> c[21]" if style == "tree" else "a[8] -> b[13] -> c[21] -> a"
    source = "Indicators\n==========\n\n" + graph_source(
        body, f"   :style: custom\n   :indicators: {definitions}")
    out, _ = build_sphinx(tmp_path, builder, source, config=f'tb_graph_styles = {{"custom": {{"base": {style!r}}}}}\n')
    if builder == "html":
        graph = BeautifulSoup((out / "index.html").read_text(), "html.parser").find("tb-graph")
        result = graph.get_text()
        svg = ET.parse(out / graph.find("img")["src"]).getroot()
        ns = {"s": "http://www.w3.org/2000/svg"}
        groups = svg.findall('.//s:g[@class="node"]', ns)
        annotations = [group for group in groups if group.find("s:title", ns).text.startswith("tb_indicators_")]
        assert {element.text for group in annotations for element in group.findall("s:text", ns)} == set(
            definition.split("=")[0] for definition in definitions.split())
        assert all(group.find("s:ellipse", ns) is None and group.find("s:polygon", ns) is None for group in annotations)
        edges = svg.findall('.//s:g[@class="edge"]', ns)
        annotated = [edge for edge in edges if "tb_indicators_" in edge.find("s:title", ns).text]
        assert len(annotated) == len(definitions.split())
        assert all(edge.find("s:polygon", ns) is not None for edge in annotated)
        if style == "tree":
            connections = [edge for edge in edges if edge not in annotated]
            assert len(connections) == 2
            assert all(edge.find("s:polygon", ns) is None for edge in connections)
        if style == "list":
            # Two labels on one target sit side by side, so arrows don't cross text.
            shared = next(group for group in annotations if len(group.findall("s:text", ns)) == 2)
            first, second = shared.findall("s:text", ns)
            assert first.attrib["y"] == second.attrib["y"]
            assert float(first.attrib["x"]) < float(second.attrib["x"])
        if style == "ring":
            ellipses = svg.findall('.//s:g[@class="node"]/s:ellipse', ns)
            assert len(ellipses) == 3
    elif builder == "latex":
        result = next(out.glob("*.tex")).read_text()
        assert next(out.glob("tb-graph-*.pdf")).read_bytes().startswith(b"%PDF-")
    else:
        result = (out / "index.txt").read_text()
    result = " ".join(result.split())
    assert "Indicator “current” points to “13”." in result
    assert "visible nodes" in result
    if style != "tree":
        assert "Indicator “other” points to “13”." in result
    if style == "tree":
        assert "Tree diagram with 3 visible nodes" in result
        assert "“13” and “21” are leaves" in result


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("target", ["a", "f"])
def test_tree_indicator_preserves_levels_and_child_sides(target):
    body = "a[30] -left-> b[20]\na -right-> c[70]\nb -left-> d[10]\nc -left-> f[50]\nf -left-> l[40]\nf -right-> m[60]"
    node = next(parse_rst(graph_source(body, f"   :style: tree\n   :indicators: current={target}")).findall(TbGraphNode))
    positions = dot_positions(node)
    ids = {item["key"]: f"n{index}" for index, item in enumerate(node["nodes"])}
    point = lambda key: positions[ids[key]]
    assert point("b")[0] < point("a")[0] < point("c")[0]
    assert point("b")[1] == point("c")[1] < point("a")[1]
    assert point("f")[1] == point("d")[1] < point("c")[1]
    assert point("l")[0] < point("f")[0] < point("m")[0]
    assert point("f")[0] == pytest.approx((point("l")[0] + point("m")[0]) / 2, abs=.01)


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("builder", ["html", "text", "latex"])
@pytest.mark.parametrize("orientation", ["horizontal", "vertical"])
def test_array_indicators_render_labels_arrows_and_text_targets(tmp_path, builder, orientation):
    source = "Indicators\n==========\n\n" + graph_source("a[8]\nb[13]\nc['']", """   :style: custom-array
   :show-indices:
   :indicators: head=a current=b another=b tail=c
   :highlight: values.node[b]""", "values")
    config = f'tb_graph_styles = {{"custom-array": {{"base": "array", "orientation": {orientation!r}}}}}\n'
    out, _ = build_sphinx(tmp_path, builder, source, config=config)
    if builder == "html":
        graphs = BeautifulSoup((out / "index.html").read_text(), "html.parser").find_all("tb-graph")
        assert len(graphs) == 1
        graph = graphs[0]
        result = graph.get_text()
        svg = ET.parse(out / graph.find("img")["src"]).getroot()
        ns = {"s": "http://www.w3.org/2000/svg"}
        edges = svg.findall('.//s:g[@class="edge"]', ns)
        assert len(edges) == 4 and all(edge.find("s:polygon", ns) is not None for edge in edges)
        groups = svg.findall('.//s:g[@class="node"]', ns)
        labels = {element.text for group in groups[1:] for element in group.findall("s:text", ns)}
        assert labels == {"head", "current", "another", "tail"}
        cells = svg.findall('./s:g/s:path', ns)
        assert len(cells) == 3 and cells[1].attrib["stroke-width"] == "3"
        assert cells[2].attrib["fill"] == "#eeeeee"
        bounds = []
        for cell in cells:
            coordinates = list(map(float, re.findall(r"-?\d+(?:\.\d+)?", cell.attrib["d"])))
            bounds.append((min(coordinates[::2]), max(coordinates[::2]),
                           min(coordinates[1::2]), max(coordinates[1::2])))
        # Borders follow the table after indicator labels shift its layout.
        values = groups[0].findall("s:text", ns)[:2] if orientation == "horizontal" else groups[0].findall("s:text", ns)[1:4:2]
        for index, value in enumerate(values):
            x0, x1, y0, y1 = bounds[index]
            assert x0 < float(value.attrib["x"]) < x1
            assert y0 < float(value.attrib["y"]) < y1
        for group in groups[1:]:
            value = group.find("s:text", ns)
            if orientation == "horizontal":
                assert float(value.attrib["y"]) < min(bound[2] for bound in bounds)
            else:
                assert float(value.attrib["x"]) > max(bound[1] for bound in bounds)
        assert not list((out / "_images").glob("*.plain"))
    elif builder == "latex":
        result = next(out.glob("*.tex")).read_text()
        assert next(out.glob("tb-graph-*.pdf")).read_bytes().startswith(b"%PDF-")
    else:
        result = (out / "index.txt").read_text()
    result = " ".join(result.split())
    assert "head” points to cell 0, value “8”" in result
    assert "current” points to cell 1, value “13”" in result
    assert "another” points to cell 1, value “13”" in result
    assert "tail” points to unused cell 2" in result


@pytest.mark.parametrize("format", ["svg", "pdf"])
def test_ring_selects_circo_for_each_image_format(monkeypatch, format):
    node = next(parse_rst(graph_source("a[8] -> b[13] -> a", "   :style: ring")).findall(TbGraphNode))
    node["style"] = resolve_graph_styles({"custom": {"base": "ring"}})["custom"]
    translator = SimpleNamespace(builder=SimpleNamespace(env=SimpleNamespace(path2doc=lambda source: "lesson")))
    calls = []
    def render(translator, code, options, image_format, **kwargs):
        calls.append((code, options, image_format))
        return "diagram." + image_format, "unused"
    monkeypatch.setattr(graph_generator, "render_dot", render)
    assert graph_generator.render_graph(translator, node, format) == "diagram." + format
    assert calls[0][1] == {"docname": "lesson", "graphviz_dot": "circo"}
    assert calls[0][2] == format


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("orientation", ["horizontal", "vertical"])
@pytest.mark.parametrize("indices", [False, True])
def test_array_cells_are_adjacent_with_optional_indices_and_literal_values(orientation, indices):
    body = r'''a['<b>&"literal</b>'] -> last
b['\\N']
last['']'''
    node = next(parse_rst(graph_source(body, "   :style: array")).findall(TbGraphNode))
    node["show_indices"] = indices
    node["style"] = resolve_graph_styles({"array": {"orientation": orientation}})["array"]
    original = deepcopy(node.attributes)
    plain = subprocess.run([shutil.which("dot"), "-Tplain"], input=measurement_dot(node),
                           capture_output=True, text=True, check=True).stdout
    svg = ET.fromstring(subprocess.run([shutil.which("dot"), "-Tsvg"],
                                      input=graph_dot(node, array_size=cell_dimensions(plain)),
                                      capture_output=True, text=True, check=True).stdout)
    ns = {"s": "http://www.w3.org/2000/svg"}
    texts = [element.text for element in svg.findall('.//s:text', ns)]
    assert texts == (["0", '<b>&"literal</b>', "1", r"\N", "2"]
                     if indices and orientation == "vertical" else
                     ['<b>&"literal</b>', r"\N"] + (["0", "1", "2"] if indices else []))
    assert not svg.findall('.//s:g[@class="edge"]', ns)
    shapes = svg.findall('./s:g/s:path', ns)
    assert len(shapes) == 3
    bounds = []
    all_points = []
    for shape in shapes:
        coordinates = list(map(float, re.findall(r"-?\d+(?:\.\d+)?", shape.attrib["d"])))
        points = list(zip(coordinates[::2], coordinates[1::2]))
        all_points.append(set(points))
        bounds.append((min(x for x, y in points), max(x for x, y in points),
                       min(y for x, y in points), max(y for x, y in points)))
    assert len({round(x1 - x0, 2) for x0, x1, y0, y1 in bounds}) == 1
    assert len({round(y1 - y0, 2) for x0, x1, y0, y1 in bounds}) == 1
    assert shapes[2].attrib["fill"] == "#eeeeee"
    x0, x1, y0, y1 = bounds[1]
    assert {(x0, y0), (x1, y0), (x0, y1), (x1, y1)} <= all_points[1]
    if orientation == "horizontal":
        assert all(bounds[i][1] == pytest.approx(bounds[i + 1][0]) for i in range(2))
        assert len({(y0, y1) for x0, x1, y0, y1 in bounds}) == 1
        x0, x1, y0, y1 = bounds[0]
        assert (x0, y0) not in all_points[0] and (x0, y1) not in all_points[0]
        assert (x1, y0) in all_points[0] and (x1, y1) in all_points[0]
        x0, x1, y0, y1 = bounds[2]
        assert (x1, y0) not in all_points[2] and (x1, y1) not in all_points[2]
        if indices:
            elements = svg.findall('.//s:text', ns)
            assert max(float(element.attrib["y"]) for element in elements[:2]) < min(
                float(element.attrib["y"]) for element in elements[2:])
    else:
        assert all(bounds[i][3] == pytest.approx(bounds[i + 1][2]) for i in range(2))
        assert len({(x0, x1) for x0, x1, y0, y1 in bounds}) == 1
    assert node.attributes == original


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("builder", ["html", "text", "latex"])
def test_array_style_builders_preserve_order_highlights_and_hidden_cells(tmp_path, builder):
    source = "Array\n=====\n\n" + graph_source(
        "a[8] -> later\nhidden['secret'] {invisible}\nlater[13]",
        "   :style: custom-array\n   :show-indices:\n   :highlight: values.node[later] values.node[hidden]", "values")
    config = ('tb_graph_styles = {"custom-array": {"base": "array", "orientation": "vertical", '
              '"fill": "lightblue", "highlight-fill": "gold"}}\n')
    out, _ = build_sphinx(tmp_path, builder, source, config=config)
    if builder != "text":
        assert list((out / ".doctrees" / "tb-graph-measure").glob("*.plain"))
        assert not list((out / "_images").glob("*.plain"))
        assert not list(out.glob("*.plain"))
    if builder == "html":
        graph = BeautifulSoup((out / "index.html").read_text(), "html.parser").find("tb-graph")
        result = graph.get_text()
        svg = ET.parse(out / graph.find("img")["src"]).getroot()
        texts = [element.text for element in svg.iter("{http://www.w3.org/2000/svg}text")]
        assert texts == ["0", "8", "2", "13"]
        assert svg.find('.//*[@fill="lightblue"]') is not None
        assert svg.find('.//*[@fill="gold"]') is not None
        assert svg.find('.//*[@stroke-width="3"]') is not None
    elif builder == "latex":
        result = next(out.glob("*.tex")).read_text()
        assert next(out.glob("tb-graph-*.pdf")).read_bytes().startswith(b"%PDF-")
    else:
        result = (out / "index.txt").read_text()
    result = " ".join(result.split())
    assert "index 0:" in result and "index 2:" in result
    assert "an undisplayed cell" in result and "is highlighted" in result
    assert "top to bottom" in result and "secret" not in result
    assert "points to" not in result and "isolated" not in result


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("unused_fill", [None, "#eeeeee", "lightgray"])
def test_unused_array_fill_and_highlight_precedence(tmp_path, unused_fill):
    source = "Unused slots\n============\n\n" + graph_source(
        "a['']\nb['']\nc[0]", "   :style: array\n   :highlight: values.node[b]", "values")
    config = f'tb_graph_styles = {{"array": {{"unused-fill": {unused_fill!r}, "highlight-fill": "gold"}}}}\n'
    out, _ = build_sphinx(tmp_path, "html", source, config=config)
    graph = BeautifulSoup((out / "index.html").read_text(), "html.parser").find("tb-graph")
    svg = ET.parse(out / graph.find("img")["src"]).getroot()
    shapes = svg.findall('./{http://www.w3.org/2000/svg}g/{http://www.w3.org/2000/svg}path')
    assert [shape.attrib["fill"] for shape in shapes] == [unused_fill or "none", "gold", "none"]
    assert shapes[1].attrib["stroke-width"] == "3"
    assert "an unused cell" in graph.get_text()
    assert "“0”" in graph.get_text()


def test_missing_dot_retains_array_description(tmp_path):
    source = "Array\n=====\n\n" + graph_source("a[8]\nb['']", "   :style: array\n   :show-indices:")
    out, log = build_sphinx(tmp_path, "html", source,
                           config='graphviz_dot = "touchbook-missing-dot"\n', fail_on_warning=False)
    graph = BeautifulSoup((out / "index.html").read_text(), "html.parser").find("tb-graph")
    assert not graph.find("img")
    assert "cannot be run" in log and "index 1: an unused cell" in graph.get_text()


@pytest.mark.skipif(shutil.which("circo") is None, reason="Graphviz circo is required")
@pytest.mark.parametrize("builder", ["html", "latex", "text"])
def test_ring_style_builders_use_circular_layout_and_ellipse_nodes(tmp_path, builder):
    source = "Ring\n====\n\n" + graph_source("a[8] -> b[13] -> c[21] -> d[34] -> a", "   :style: ring")
    out, _ = build_sphinx(tmp_path, builder, source)
    if builder == "html":
        graph = BeautifulSoup((out / "index.html").read_text(), "html.parser").find("tb-graph")
        result = graph.get_text()
        svg = ET.parse(out / graph.find("img")["src"]).getroot()
        ns = {"s": "http://www.w3.org/2000/svg"}
        shapes = svg.findall('.//s:g[@class="node"]/s:ellipse', ns)
        assert len(shapes) == 4 and all(shape.attrib["fill"] == "none" for shape in shapes)
        assert len(svg.findall('.//s:g[@class="edge"]', ns)) == 4
        points = [(float(shape.attrib["cx"]), float(shape.attrib["cy"])) for shape in shapes]
        center = tuple(sum(point[axis] for point in points) / 4 for axis in (0, 1))
        radii = [sum((point[axis] - center[axis]) ** 2 for axis in (0, 1)) ** .5 for point in points]
        assert max(radii) - min(radii) < .1
        assert len({round(x, 1) for x, y in points}) >= 2
        assert len({round(y, 1) for x, y in points}) >= 2
    elif builder == "latex":
        result = next(out.glob("*.tex")).read_text()
        assert next(out.glob("tb-graph-*.pdf")).read_bytes().startswith(b"%PDF-")
    else:
        result = (out / "index.txt").read_text()
    assert "Circular graph diagram" in result and "points to" in result


def test_custom_styles_inherit_configured_builtin_without_mutating_defaults():
    overrides = {"custom": {"base": "list", "shape": "ellipse"},
                 "list": {"fill": "#e0f2fe", "highlight-fill": "#fde68a", "font-size": 16}}
    original = deepcopy(overrides)
    styles = resolve_graph_styles(overrides)
    assert styles["custom"]["orientation"] == "horizontal"
    assert styles["custom"]["layout"] == "list"
    assert styles["custom"]["fill"] == "#e0f2fe"
    assert styles["custom"]["font-size"] == 16
    assert styles["custom"]["highlight-fill"] == "#fde68a"
    assert styles["custom"]["shape"] == "ellipse"
    assert resolve_graph_styles({})["list"]["fill"] == "#add8e6"
    assert overrides == original


@pytest.mark.parametrize("overrides", [
    [], {"bad.name": {}}, {"custom": []}, {"custom": {"base": "unknown"}},
    {"tree": {"layout": "neato"}}, {"list": {"shape": "record"}},
    {"list": {"orientation": "diagonal"}}, {"list": {"font-size": 0}},
    {"tree": {"node-spacing": float("inf")}}, {"tree": {"level-spacing": -1}},
    {"list": {"fill": '" ]; bad [label="injected"'}},
    {"list": {"font": "unsafe\nfont"}}, {"tree": {"relationship-labels": "false"}},
    {"custom": {"arrows": "bad"}}, {"custom": {"connectors": "bad"}},
    {"tree": {"highlight-fill": '" ]; bad [label="injected"'}},
    {"tree": {"highlight-fill": 3}},
    {"array": {"unused-fill": '" ]; injected'}},
    {"array": {"unused-fill": 3}},
])
def test_invalid_style_configuration_is_rejected(overrides):
    with pytest.raises(ValueError):
        resolve_graph_styles(overrides)


def dot_positions(node):
    result = subprocess.run([shutil.which("dot"), "-Tplain"], input=graph_dot(node),
                            capture_output=True, text=True, check=True)
    positions = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if parts and parts[0] == "node":
            positions[parts[1]] = (float(parts[2]), float(parts[3]))
    return positions


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("reverse", [False, True])
def test_list_style_is_horizontal_with_boxes_and_arrowheads(reverse):
    body = "head['head'] -> a[8] -> b[13] -> c[21] -> tail['tail']"
    if reverse:
        body += "\ntail -> c -> b -> a -> head"
    node = next(parse_rst(graph_source(body, "   :style: list")).findall(TbGraphNode))
    positions = dot_positions(node)
    points = [positions[f"n{index}"] for index in range(5)]
    assert all(points[i][0] < points[i + 1][0] for i in range(4))
    assert max(y for x, y in points) - min(y for x, y in points) < .01
    svg = subprocess.run([shutil.which("dot"), "-Tsvg"], input=graph_dot(node),
                         capture_output=True, text=True, check=True).stdout
    tree = ET.fromstring(svg)
    ns = {"s": "http://www.w3.org/2000/svg"}
    assert len(tree.findall('.//s:g[@class="node"]/s:polygon', ns)) == 5
    assert len(tree.findall('.//s:g[@class="edge"]/s:polygon', ns)) == (8 if reverse else 4)


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
def test_tree_style_centers_levels_and_preserves_missing_child_sides():
    body = ("a[30] -right-> c[70]\na -left-> b[20]\nb -left-> d[10]\n"
            "c -left-> f[50]\nf -left-> l[40]\nf -right-> m[60]")
    node = next(parse_rst(graph_source(body, "   :style: tree")).findall(TbGraphNode))
    original = deepcopy(node.attributes)
    positions = dot_positions(node)
    ids = {item["key"]: f"n{index}" for index, item in enumerate(node["nodes"])}
    point = lambda key: positions[ids[key]]
    assert point("b")[0] < point("a")[0] < point("c")[0]
    assert point("b")[1] == point("c")[1] < point("a")[1]
    assert point("a")[0] == pytest.approx((point("b")[0] + point("c")[0]) / 2, abs=.01)
    assert point("f")[0] == pytest.approx((point("l")[0] + point("m")[0]) / 2, abs=.01)
    assert point("d")[0] < point("b")[0]
    assert point("f")[0] < point("c")[0]
    assert any(key.startswith("tb_missing_") for key in positions)
    assert node.attributes == original
    assert "tb_middle" not in graph_description(node).astext()
    svg = subprocess.run([shutil.which("dot"), "-Tsvg"], input=graph_dot(node),
                         capture_output=True, text=True, check=True).stdout
    tree = ET.fromstring(svg)
    ns = {"s": "http://www.w3.org/2000/svg"}
    assert len(tree.findall('.//s:g[@class="node"]/s:ellipse', ns)) == 7
    assert not tree.findall('.//s:g[@class="edge"]/s:polygon', ns)
    # SVG encodes even straight edges as cubic paths; control points are collinear.
    for path in tree.findall('.//s:g[@class="edge"]/s:path', ns):
        numbers = list(map(float, re.findall(r"-?\d+(?:\.\d+)?", path.attrib["d"])))
        points = list(zip(numbers[::2], numbers[1::2]))
        x0, y0 = points[0]
        x1, y1 = points[-1]
        for x, y in points[1:-1]:
            assert abs((x - x0) * (y1 - y0) - (y - y0) * (x1 - x0)) < 1


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("operator,side", [("-left->", -1), ("-right->", 1), ("->", -1)])
def test_tree_style_reserves_the_missing_child_position(operator, side):
    node = next(parse_rst(graph_source(
        f"parent[30] {operator} child[20]", "   :style: tree")).findall(TbGraphNode))
    positions = dot_positions(node)
    assert (positions["n1"][0] - positions["n0"][0]) * side > 0
    assert positions["n1"][1] < positions["n0"][1]


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
def test_tree_style_accepts_cycles_and_shared_children_without_extra_nodes():
    for body in ("a[1] -> b[2] -> a", "a[1] -> c[3]\nb[2] -> c"):
        node = next(parse_rst(graph_source(body, "   :style: tree")).findall(TbGraphNode))
        assert "tb_middle_" not in graph_dot(node)
        assert "tb_missing_" not in graph_dot(node)
        assert len(dot_positions(node)) == len(node["nodes"])


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("fill", [None, "#add8e6"])
@pytest.mark.parametrize("highlight_fill", [None, "#fde68a", "gold"])
def test_highlight_fill_only_changes_visible_highlighted_nodes(fill, highlight_fill):
    node = next(parse_rst(graph_source(
        "a[8] -> b[13] -> hidden[21] {invisible}",
        "   :highlight: graph.node[b] graph.node[hidden]", "graph")).findall(TbGraphNode))
    node["style"] = resolve_graph_styles({"graph": {
        "fill": fill, "highlight-fill": highlight_fill}})["graph"]
    svg = subprocess.run([shutil.which("dot"), "-Tsvg"], input=graph_dot(node),
                         capture_output=True, text=True, check=True).stdout
    tree = ET.fromstring(svg)
    ns = {"s": "http://www.w3.org/2000/svg"}
    groups = tree.findall('.//s:g[@class="node"]', ns)
    assert len(groups) == 2
    shapes = {group.find("s:title", ns).text: group.find("s:ellipse", ns)
              for group in groups}
    assert shapes["n0"].attrib["fill"] == (fill or "none")
    assert shapes["n1"].attrib["fill"] == (highlight_fill or fill or "none")
    assert shapes["n1"].attrib["stroke-width"] == "3"


def build_sphinx(tmp_path: Path, builder, source, *, config="", tagged=False, fail_on_warning=True):
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text(
        'extensions = ["sphinx_touchbook"]\nhtml_theme = "alabaster"\n'
        + f'tb_pdf_tagging = {tagged!r}\n' + config)
    (src / "index.rst").write_text(source)
    out = tmp_path / "out"
    args = [sys.executable, "-m", "sphinx", "-E", "-b", builder, str(src), str(out)]
    if fail_on_warning:
        args.append("-W")
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return out, result.stdout + result.stderr


BUILD_SOURCE = r'''
Graphs
======

See :ref:`the graph <graph-target>` and :ref:`external <external-target>`.

.. _external-target:

.. tb-graph:: tree
   :name: graph-target
   :class: first second
   :label: Values
   :caption: A caption & example
   :highlight: tree.node[child] tree.node[hidden]

   root['<script>alert("x")</script>'] -right-> other[12]
   root -left-> child['a_b%&#{}']
   other -next-> hidden['secret hidden label'] {invisible}
   root -spacing-> {invisible} spacer['private'] {invisible}

.. tb-graph::
'''


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
def test_html_renders_svg_and_accessible_description(tmp_path):
    out, _ = build_sphinx(tmp_path, "html", BUILD_SOURCE)
    soup = BeautifulSoup((out / "index.html").read_text(), "html.parser")
    graphs = soup.find_all("tb-graph")
    assert len(graphs) == 2
    graph = graphs[0]
    assert graph["id"] == "graph-target"
    assert graph["data-key"] == "tree"
    assert graph["class"] == ["first", "second"]
    assert not graph.find("script")
    assert graph.select_one(".tb-graph__label").get_text() == "Values"
    assert graph.select_one(".tb-graph__caption").get_text() == "A caption & example"
    assert '<script>alert("x")</script>' in graph.get_text()
    assert "“a_b%&#{}” is highlighted." in graph.get_text()
    assert "“12” points to an undisplayed endpoint through the “next” relationship." in graph.get_text()
    assert "secret hidden label" not in graph.get_text() and "private" not in graph.get_text()
    assert graph.find("details").find("summary").get_text() == "Text description"
    image = graph.find("img")
    assert image["alt"] == "Values"
    svg = ET.parse(out / image["src"]).getroot()
    texts = [element.text for element in svg.iter("{http://www.w3.org/2000/svg}text")]
    assert '<script>alert("x")</script>' in texts
    assert "secret hidden label" not in texts and "private" not in texts
    assert svg.find('.//*[@stroke-width="3"]') is not None
    assert "Empty graph." in graphs[1].get_text()
    assert not graphs[1].find("img")
    assert not graphs[1].select(".tb-graph__label, .tb-graph__caption")
    for target in ("external-target", "graph-target"):
        assert len(soup.find_all(id=target)) == 1
        assert soup.find("a", href=f"#{target}")
    assert soup.find("link", href=lambda href: href and "tb-graph.css" in href)


@pytest.mark.parametrize("builder", ["text", "latex"])
def test_non_html_preserves_semantic_description(tmp_path, builder):
    if builder == "latex" and shutil.which("dot") is None:
        pytest.skip("Graphviz dot is required")
    out, _ = build_sphinx(tmp_path, builder, BUILD_SOURCE)
    result = (out / "index.txt").read_text() if builder == "text" else next(out.glob("*.tex")).read_text()
    for text in ("Values", "highlighted", "undisplayed endpoint", "Empty graph", "Directed graph", "points to"):
        assert text in result
    assert "secret hidden label" not in result and "private" not in result
    if builder == "latex":
        assert "index:graph-target" in result and "index:external-target" in result
        assert "sphinxincludegraphics" in result
        pdfs = list(out.glob("tb-graph-*.pdf"))
        assert len(pdfs) == 1 and pdfs[0].read_bytes().startswith(b"%PDF-")
    else:
        assert '<script>alert("x")</script>' in result


def test_missing_dot_leaves_readable_html_and_warns(tmp_path):
    out, log = build_sphinx(tmp_path, "html", BUILD_SOURCE,
                           config='graphviz_dot = "touchbook-missing-dot"\n', fail_on_warning=False)
    assert "cannot be run" in log
    graph = BeautifulSoup((out / "index.html").read_text(), "html.parser").find("tb-graph")
    assert not graph.find("img") and not graph.find("details")
    assert "Directed graph" in graph.get_text() and "undisplayed endpoint" in graph.get_text()


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
def test_dot_quotes_prevent_attribute_injection_and_graphviz_escapes(tmp_path):
    source = graph_source(r'''a['" ]; evil [label="injected"]'] -> b['\\N']
c['<b>literal</b>']''')
    node = next(parse_rst(source).findall(TbGraphNode))
    result = subprocess.run([shutil.which("dot"), "-Tsvg"], input=graph_dot(node),
                            capture_output=True, text=True, check=True)
    svg = ET.fromstring(result.stdout)
    texts = [element.text for element in svg.iter("{http://www.w3.org/2000/svg}text")]
    assert texts == [item["value"] for item in node["nodes"]]
    assert len(svg.findall('.//{http://www.w3.org/2000/svg}g[@class="node"]')) == 3


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
def test_tagged_pdf_uses_native_image_with_alt_text(tmp_path):
    out, _ = build_sphinx(tmp_path, "latex", BUILD_SOURCE, tagged=True)
    result = next(out.glob("*.tex")).read_text()
    assert result.startswith(r"\DocumentMetadata{lang=en-US,tagging=on}")
    assert r"\TBIncludeGraphics[alt={Values}" in result
    assert "undisplayed endpoint" in result


@pytest.mark.skipif(shutil.which("dot") is None, reason="Graphviz dot is required")
@pytest.mark.parametrize("builder", ["html", "latex", "text"])
def test_book_style_configuration_is_applied_by_builders(tmp_path, builder):
    config = ('tb_graph_styles = {"custom": {"base": "list", "fill": "#e0f2fe", '
              '"highlight-fill": "#fde68a"}}\n')
    source = "Styles\n======\n\n" + graph_source(
        "a[8] -next-> b[13]", "   :style: custom\n   :highlight: values.node[b]", "values")
    out, _ = build_sphinx(tmp_path, builder, source, config=config)
    if builder == "html":
        soup = BeautifulSoup((out / "index.html").read_text(), "html.parser")
        graph = soup.find("tb-graph")
        svg = ET.parse(out / graph.find("img")["src"]).getroot()
        assert svg.find('.//*[@fill="#e0f2fe"]') is not None
        assert svg.find('.//*[@fill="#fde68a"]') is not None
        assert "“8” points to “13” through the “next” relationship." in graph.get_text()
    elif builder == "latex":
        assert next(out.glob("tb-graph-*.pdf")).read_bytes().startswith(b"%PDF-")
        assert "sphinxincludegraphics" in next(out.glob("*.tex")).read_text()
    else:
        assert "“8” points to “13” through the “next” relationship." in (out / "index.txt").read_text()


def test_tree_description_explains_values_roots_children_leaves_and_highlights():
    node = next(parse_rst(graph_source(
        "root[8] -left-> child[3]\nroot -right-> other[12]\nchild -right-> added[6]",
        "   :style: tree\n   :highlight: tree.node[added]", "tree")).findall(TbGraphNode))
    prose = graph_description(node).astext()
    assert "The root is “8”." in prose
    assert "“8” has left child “3” and right child “12”." in prose
    assert "“3” has right child “6”." in prose
    assert "“12” and “6” are leaves." in prose
    assert "“6” is highlighted." in prose
    assert not any(key in prose for key in ("root:", "added", "other", "tb_middle"))


def test_description_disambiguates_duplicate_and_empty_labels():
    node = next(parse_rst(graph_source("a[8] -> b[8]\nc['']\nd['']")).findall(TbGraphNode))
    prose = graph_description(node).astext()
    assert "“8” (node a) points to “8” (node b)." in prose
    assert "an unlabeled node (node c) and an unlabeled node (node d) are isolated." in prose


@pytest.mark.parametrize("builder", ["html", "text", "latex"])
def test_author_description_replaces_generated_prose_and_is_literal(tmp_path, builder):
    if builder != "text" and shutil.which("dot") is None:
        pytest.skip("Graphviz dot is required")
    description = "The new node preserves ordering. <script>literal</script> **plain**"
    source = "Description\n===========\n\n" + graph_source(
        "a[8] -> b[13]", "   :description: " + description)
    node = next(parse_rst(graph_source("a[8] -> b[13]",
                                     "   :description: " + description)).findall(TbGraphNode))
    assert graph_description(node).astext() == description
    out, _ = build_sphinx(tmp_path, builder, source)
    if builder == "html":
        graph = BeautifulSoup((out / "index.html").read_text(), "html.parser").find("tb-graph")
        assert not graph.find("script") and not graph.find("strong")
        assert description in graph.get_text()
        assert "Directed graph with" not in graph.get_text()
        assert graph.find("img")
    else:
        filename = out / "index.txt" if builder == "text" else next(out.glob("*.tex"))
        result = filename.read_text()
        assert "The new node preserves ordering." in result
        assert "Directed graph with" not in result
