"""Structured content keeps graph layout, cell targeting, and fallbacks aligned."""

import json
import re
import subprocess
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from docutils import nodes
import pytest

from sphinx_touchbook.directives.positions import resolve_target
from sphinx_touchbook.generators.graph import graph_description, graph_dot
from sphinx_touchbook.generators.graph_annotations import compose_svg, node_bounds, tag
from sphinx_touchbook.nodes import TbGraphNode
from test_tb_graph import parse_rst, graph_source, build_sphinx


BODY = '''root{"type": "array", "values": [54, "a", ""]} -left-> left
root -right-> right
left{"type": "array", "values": [54]}
right[26]'''


def graph(body=BODY, options="", style="tree"):
    doc = parse_rst(graph_source(body, f"   :style: {style}\n" + options, "g"))
    errors = list(doc.findall(nodes.system_message))
    assert not errors, [error.astext() for error in errors]
    return next(doc.findall(TbGraphNode))


@pytest.mark.parametrize("style", ["tree", "list"])
def test_structured_content_normalization_and_cell_positions(style):
    node = graph(options="   :highlight: g.node[root].slot[1]\n"
                 "   :indicators: current=.node[root].slot[0] tail=right\n"
                 "   :overlay: .node[root].slot[0] g.node[left].slot[0]", style=style)
    assert node["nodes"][0]["content"] == {"type": "array", "values": [54, "a", ""]}
    assert node["nodes"][1]["value"] == "[54]"
    assert node["highlighted"] == ["root.slot[1]"]
    assert node["indicators"] == [{"key": "current", "target": "root.slot[0]"},
                                  {"key": "tail", "target": "right"}]
    assert node["annotations"][0]["targets"] == ["root.slot[0]", "left.slot[0]"]
    position = resolve_target("g.node[root].slot[1]", node, "node[root].slot[1]")
    assert position["type"] == "cell" and position["value"] == "a"
    assert position["key"] == "root" and position["index"] == 1
    description = graph_description(node).astext()
    assert 'array node root with 3 cells [“54”, “a”, an unused cell]' in description
    assert 'cell 1) is highlighted' in description
    assert 'Indicator “current” points to “54” (node root, cell 0)' in description


@pytest.mark.parametrize("payload", [
    '{"type":"array"}', '{"type":"array","values":[],"extra":1}',
    '{"type":"list","values":[1]}', '{"type":"array","values":1}',
    '{"type":"array","values":[true]}', '{"type":"array","values":[null]}',
    '{"type":"array","values":[{}]}', '{"type":"array","values":[[1]]}',
    '{"type":"array","values":[NaN]}', '{"type":"array","values":[1e999]}',
    '{"type":"array","type":"array","values":[]}',
    '{"type":"array","values":["\\u0000"]}',
    '{"type":"array","values":["\\ud800"]}',
    "{'type':'array','values':[1]}", '{"type":"array","values":[1,]}',
])
def test_invalid_structured_payloads_fail_during_parsing(payload):
    doc = parse_rst(graph_source("a" + payload, "   :style: tree"))
    assert list(doc.findall(nodes.system_message))
    assert not list(doc.findall(TbGraphNode))


@pytest.mark.parametrize("style", ["graph", "ring", "array"])
def test_structured_nodes_require_supported_layout(style):
    doc = parse_rst(graph_source(BODY, f"   :style: {style}"))
    assert 'require a tree or list style' in next(doc.findall(nodes.system_message)).astext()


@pytest.mark.parametrize("option", [
    ':highlight: g.node[root]', ':highlight: g.node[root].slot[3]',
    ':highlight: g.node[right].slot[0]', ':highlight: other.node[root].slot[0]',
    ':indicators: p=root', ':indicators: p=.node[root].slot[3]',
    ':overlay: root', ':overlay: .node[root].slot[3]',
])
def test_container_targets_and_invalid_cells_are_rejected(option):
    doc = parse_rst(graph_source(BODY, "   :style: tree\n   " + option, "g"))
    assert list(doc.findall(nodes.system_message))


@pytest.mark.parametrize("position", ["node[root]", "node[root].slot[3]", "node[right].slot[0]"])
def test_pointers_reject_container_targets_and_invalid_cells(position):
    with pytest.raises(ValueError):
        resolve_target("g." + position, graph(), position)


@pytest.mark.parametrize("style", ["tree", "list"])
@pytest.mark.parametrize("fill_stroke", ["none", "transparent"])
def test_native_table_rendering_cell_bounds_and_overlay_geometry(style, fill_stroke):
    node = graph(options="   :show-indices:\n"
                 "   :highlight: g.node[root].slot[1]\n"
                 "   :indicators: first=.node[root].slot[0] last=.node[root].slot[2]\n"
                 "   :overlay: .node[root].slot[1]\n   :overlay-shape: rectangle", style=style)
    dot = graph_dot(node, array_size=(40, 32))
    if style == "tree":
        assert 'n0:i0 -> tb_indicators_n0' in dot
        assert 'n0:i2 -> tb_indicators_n0' in dot
    else:
        indicator_edges = [line for line in dot.splitlines()
                           if line.startswith('n0 -> tb_indicators_n0')]
        assert len(indicator_edges) == 2
        assert 'tailport="i0"' in indicator_edges[0]
        assert 'tailport="i2"' in indicator_edges[1]
    svg = subprocess.run(["dot", "-Tsvg"], input=dot, text=True,
                         capture_output=True, check=True)
    assert not svg.stderr
    root = ET.fromstring(svg.stdout)
    group = root.find(f"{tag('g')}[@class='graph']")
    indicator_edges = [edge for edge in group.findall(f"{tag('g')}[@class='edge']")
                       if 'tb_indicators_n0' in edge.find(tag("title")).text]
    assert len(indicator_edges) == 2
    assert all(len(edge.findall(tag("polygon"))) == 1 for edge in indicator_edges)
    # Exercise both Graphviz spellings regardless of the installed version.
    fills = [polygon for polygon in group.iter(tag("polygon"))
             if polygon.get("stroke") in ("none", "transparent")]
    assert len(fills) == 3  # two filled root cells and the filled leaf cell
    for polygon in fills:
        polygon.set("stroke", fill_stroke)
    svg_source = ET.tostring(root, encoding="unicode")
    bounds = node_bounds(group, node)
    assert "root" not in bounds
    assert set(bounds) == {"root.slot[0]", "root.slot[1]", "root.slot[2]", "left.slot[0]", "right"}
    assert bounds["root.slot[0]"][2] <= bounds["root.slot[1]"][2]
    composed = ET.fromstring(compose_svg(svg_source, node))
    overlay = next(element for element in composed.iter() if element.get("data-targets"))
    assert overlay.get("data-targets") == "root.slot[1]"
    assert float(overlay.get("width")) < bounds["root.slot[2]"][2] - bounds["root.slot[0]"][0]


@pytest.mark.parametrize("builder", ["html", "text", "latex"])
def test_structured_scene_across_builders(tmp_path, builder):
    source = '''Structured graph
================

.. tb-stack::

   .. tb-scene::
      :caption: Split the array

      .. tb-graph:: g
         :style: array-tree
         :show-indices:
         :highlight: g.node[root].slot[0]
         :indicators: current=.node[root].slot[1]
         :overlay: .node[left].slot[0]

         root{"type": "array", "values": [54, 26]}
         left{"type": "array", "values": [54]}
         right{"type": "array", "values": [26]}
         root -left-> left
         root -right-> right

      .. tb-pointer:: selected
         :at: g.node[left].slot[0]
'''
    config = 'tb_graph_styles = {"array-tree": {"base": "tree", "highlight-fill": "#fde68a"}}\n'
    out, _ = build_sphinx(tmp_path, builder, source, config=config)
    if builder == "html":
        soup = BeautifulSoup((out / "index.html").read_text(), "html.parser")
        assert len(soup.find_all("tb-graph")) == 1
        assert len(soup.select("tb-graph details")) == 1
        model = json.loads(soup.find("tb-stack").find("script").string)
        scene = model["scenes"][0]["objects"]
        assert scene[0]["nodes"][0]["content"]["values"] == [54, 26]
        assert scene[1]["position"]["type"] == "cell"
        assert list((out / "_images").glob("*.svg"))
        output = soup.get_text(" ")
    elif builder == "text":
        output = (out / "index.txt").read_text()
    else:
        output = next(out.glob("*.tex")).read_text()
        assert list(out.glob("tb-graph*.pdf"))
    assert "array node root with 2 cells" in output
    assert "selected points to g node left, cell 0" in output


def test_empty_arrays_literals_and_invisible_content():
    node = graph('''a{"type":"array","values":[]} -> b
b{"type":"array","values":["<script> & -> #", "x\\ny", "a\\\\b"]}
hidden{"type":"array","values":["secret"]} {invisible}''',
                 options="   :indicators: p=.node[hidden].slot[0]")
    dot = graph_dot(node)
    assert "&lt;script&gt; &amp; -&gt; #" in dot
    assert '<BR ALIGN="CENTER"/>' in dot
    assert 'style="invis"' in dot
    assert "secret" not in graph_description(node).astext()
    with pytest.raises(ValueError):
        resolve_target("g.node[a].slot[0]", node, "node[a].slot[0]")


def test_multiline_json_forward_declarations_and_error_location():
    node = graph('''root -left-> child
root{
    "type": "array",
    "values": [54, "a -> # { }", -2.5]
}
child[1]''')
    assert node["nodes"][0]["content"]["values"] == [54, "a -> # { }", -2.5]
    assert node["edges"][0]["target"] == "child"
    doc = parse_rst(graph_source('a[1]\nb{\n "type": "array",\n "values": [[1]]\n}', "   :style: tree"))
    error = next(doc.findall(nodes.system_message))
    assert "nested arrays" in error.astext()
    assert error["line"] == 5  # declaration begins on the second body line


@pytest.mark.parametrize("style", ["tree", "list"])
def test_structured_click_targets_select_cells_and_escape_values(tmp_path, style):
    from test_tb_click import keyed_question
    source = graph_source('root{"type":"array","values":["<tag> & text", ""]}',
                          f"   :style: {style}")
    regions = ".. tb-hit:: root.slot[0]\n\n   Correct.\n\n.. tb-miss:: root.slot[1]\n\n   Try again."
    out, _ = build_sphinx(tmp_path, "html", "Cells\n=====\n\n" + keyed_question(source, regions))
    soup = BeautifulSoup((out / "index.html").read_text(), "html.parser")
    controls = soup.select("tb-graph svg [role=button]")
    assert {control["data-key"] for control in controls} == {"root.slot[0]", "root.slot[1]"}
    assert all(control["tabindex"] == "0" for control in controls)
    assert controls[0]["aria-label"] == "root.slot[0]: <tag> & text"
    assert not soup.find("tag")


@pytest.mark.parametrize("style,orientation", [("tree", "horizontal"), ("list", "vertical")])
def test_custom_orientation_keeps_arrays_in_rows_and_targets_cells(style, orientation):
    node = graph(options="   :indicators: current=.node[root].slot[2]", style=style)
    node["style"]["orientation"] = orientation
    dot = graph_dot(node, array_size=(40, 40))
    result = subprocess.run(["dot", "-Tsvg"], input=dot, text=True,
                            capture_output=True, check=True)
    assert not result.stderr
    group = ET.fromstring(result.stdout).find(f"{tag('g')}[@class='graph']")
    bounds = node_bounds(group, node)
    first, last = bounds["root.slot[0]"], bounds["root.slot[2]"]
    assert first[0] < last[0] and first[1] == last[1]


def test_tree_leaf_arrays_share_a_row_with_uniform_cell_sizes():
    node = graph('''root{"type":"array","values":[54,26,93,17]}
left{"type":"array","values":[54,26]}
right{"type":"array","values":[93,17]}
a{"type":"array","values":[54]}
b{"type":"array","values":[26]}
c{"type":"array","values":[93]}
d{"type":"array","values":[17]}
root -left-> left
root -right-> right
left -left-> a
left -right-> b
right -left-> c
right -right-> d''')
    result = subprocess.run(["dot", "-Tsvg"], input=graph_dot(node, array_size=(40, 40)),
                            text=True, capture_output=True, check=True)
    group = ET.fromstring(result.stdout).find(f"{tag('g')}[@class='graph']")
    bounds = node_bounds(group, node)
    leaves = [bounds[f"{key}.slot[0]"] for key in "abcd"]
    assert len({(box[1], box[3]) for box in leaves}) == 1
    assert [box[0] for box in leaves] == sorted(box[0] for box in leaves)
    assert len({round(box[2]-box[0], 2) for box in bounds.values()}) == 1


def test_structured_question_without_graphviz_has_cell_buttons(tmp_path, monkeypatch):
    from test_tb_click import keyed_question, build_sphinx as build_click
    from sphinx_touchbook.generators import graph as generator
    monkeypatch.setattr(generator, "render_graph", lambda *args, **kwargs: None)
    source = graph_source('a{"type":"array","values":["text"]}', "   :style: tree")
    out = build_click(tmp_path, "html", keyed_question(source, ".. tb-hit:: a.slot[0]\n\n   Correct."))
    soup = BeautifulSoup((out / "index.html").read_text(), "html.parser")
    button = soup.select_one("tb-graph button.tb-click__target")
    assert button["data-key"] == "a.slot[0]" and button.get_text() == "text"


def test_measured_json_strings_fit_and_preserve_literal_graphviz_escapes():
    from sphinx_touchbook.generators.graph_content import measurement_graph
    from sphinx_touchbook.generators.graph_array import cell_dimensions
    values = ["long label\twith tabs", "first line\nsecond longer line", r"literal \N and \G", "<b>α & β</b>"]
    node = graph("root" + json.dumps({"type": "array", "values": values}),
                 options="   :highlight: g.node[root].slot[1]")
    plain = subprocess.run(["dot", "-Tplain"], input=measurement_graph(node),
                           text=True, capture_output=True, check=True)
    dot = graph_dot(node, array_size=cell_dimensions(plain.stdout))
    svg = subprocess.run(["dot", "-Tsvg"], input=dot,
                         text=True, capture_output=True, check=True)
    assert not svg.stderr
    text = " ".join(element.text or "" for element in ET.fromstring(svg.stdout).iter(tag("text")))
    assert r"literal \N and \G" in text
    assert "second longer line" in text
    assert "<b>α & β</b>" in text


def rounded_svg(node, size=(40, 40)):
    from sphinx_touchbook.generators.graph_content import content_positions
    plain = subprocess.run(["dot", "-Tplain"], input=graph_dot(node, array_size=size),
                           text=True, capture_output=True, check=True)
    assert not plain.stderr
    dot = graph_dot(node, array_size=size, structured_positions=content_positions(plain.stdout))
    result = subprocess.run(["dot", "-Tsvg"], input=dot,
                            text=True, capture_output=True, check=True)
    assert not result.stderr
    return ET.fromstring(result.stdout), dot


@pytest.mark.parametrize("style", ["tree", "list"])
def test_scalar_nodes_match_embedded_cell_dimensions(style):
    node = graph('a{"type":"array","values":["a",2]} -> tail[4]', style=style)
    root, _ = rounded_svg(node, size=(32, 32))
    group = root.find(f"{tag('g')}[@class='graph']")
    bounds = node_bounds(group, node)
    cell, scalar = bounds['a.slot[0]'], bounds['tail']
    assert scalar[2] - scalar[0] == pytest.approx(cell[2] - cell[0], abs=.1)
    assert scalar[3] - scalar[1] == pytest.approx(cell[3] - cell[1], abs=.1)


@pytest.mark.parametrize("style", ["tree", "list"])
@pytest.mark.parametrize("count", [1, 3])
def test_embedded_arrays_share_standalone_corner_geometry(style, count):
    from sphinx_touchbook.generators.graph_array import array_dot
    from sphinx_touchbook.generators.graph_annotations import shape_bounds, NUMBER
    node = graph('a' + json.dumps({"type": "array", "values": list(range(1, count+1))}), style=style)
    node["style"]["fill"] = "#add8e6"
    root, _ = rounded_svg(node)
    group = root.find(f"{tag('g')}[@class='graph']")
    paths = group.findall(tag("path"))
    assert len(paths) == count
    standalone = graph(' -> '.join(f'n{i}[{i+1}]' for i in range(count)), style="array")
    result = subprocess.run(["dot", "-Tsvg"], input=array_dot(standalone, (40, 40)),
                            text=True, capture_output=True, check=True)
    reference = ET.fromstring(result.stdout).find(f"{tag('g')}[@class='graph']").findall(tag("path"))
    for actual, expected in zip(paths, reference):
        actual_points = list(map(float, re.findall(NUMBER, actual.get("d"))))
        expected_points = list(map(float, re.findall(NUMBER, expected.get("d"))))
        # Native plain output rounds layout positions; SVG points use 0.01 pt.
        assert actual_points == pytest.approx(expected_points, abs=.02)
    assert all(path.get("fill") == "#add8e6" for path in paths)
    bounds = node_bounds(group, node)
    assert all(bounds[f'a.slot[{i}]'] == shape_bounds(paths[i]) for i in range(count))


def test_single_empty_highlighted_and_invisible_array_shapes():
    node = graph('''single{"type":"array","values":[9]}
empty{"type":"array","values":[]}
hidden{"type":"array","values":["secret"]} {invisible}''',
                 options="   :highlight: g.node[single].slot[0]\n   :show-indices:")
    root, _ = rounded_svg(node, size=(64, 40))
    group = root.find(f"{tag('g')}[@class='graph']")
    paths = group.findall(tag("path"))
    assert len(paths) == 2  # one real cell and the empty-array outline
    assert paths[0].get("stroke-width") == "3"
    assert set(node_bounds(group, node)) == {"single.slot[0]"}
    assert "secret" not in "".join(root.itertext())


def test_rounded_cells_remain_clickable_and_overlay_targets(tmp_path):
    from test_tb_click import keyed_question
    source = graph_source('a{"type":"array","values":[1,2,3]} -> tail[4]',
                          "   :style: list\n   :highlight: g.node[a].slot[2]\n"
                          "   :overlay: .node[a].slot[0] .node[a].slot[2]", key="g")
    regions = ".. tb-hit:: a.slot[0]\n\n   Correct.\n\n.. tb-miss:: a.slot[2]\n\n   Try again."
    out, _ = build_sphinx(tmp_path, "html", "Rounded cells\n=============\n\n" + keyed_question(source, regions))
    soup = BeautifulSoup((out / "index.html").read_text(), "html.parser")
    svg = soup.select_one("tb-graph svg")
    assert {item["data-key"] for item in svg.select("[role=button]")} == {"a.slot[0]", "a.slot[2]"}
    assert len(svg.select("g.graph > path")) == 3
    assert svg.select_one("[data-targets]")["data-targets"] == "a.slot[0] a.slot[2]"
    assert any(path.get("stroke-width") == "3" for path in svg.select("g.graph > path"))
