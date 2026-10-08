"""Annotations use completed graph geometry and survive static exports."""

from copy import deepcopy
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from docutils import nodes
import pytest
from sphinx.ext.graphviz import GraphvizError

from sphinx_touchbook.generators.graph import graph_description, graph_dot
from sphinx_touchbook.generators.graph_annotations import (
    annotated_asset, compose_svg, ellipse_geometry, node_bounds, tag,
    transform_point,
)
from sphinx_touchbook.generators.graph_array import cell_dimensions, measurement_dot
from sphinx_touchbook.nodes import TbGraphNode
from test_tb_graph import build_sphinx, graph_source, parse_rst


def graph(options="", body="a[8] -left-> b[3]\na -right-> c[12]", key="tree"):
    return next(parse_rst(graph_source(body, options, key)).findall(TbGraphNode))


def test_overlay_resolves_forward_references_and_preserves_graph_identity():
    node = graph("   :overlay: tree.node[b] tree.node[c] tree.node[b]\n"
                 "   :overlay-padding: 12.5\n   :overlay-layer: background")
    assert node["annotations"] == [{"shape": "ellipse", "targets": ["b", "c"],
                                    "padding": 12.5, "layer": "background"}]
    assert len(node["nodes"]) == 3 and len(node["edges"]) == 2
    original = deepcopy(node)
    original["annotations"] = []
    assert graph_dot(node) == graph_dot(original)
    assert "An ellipse surrounds “3” (node b) and “12” (node c)." in graph_description(node).astext()


@pytest.mark.parametrize("option,body,key,message", [
    (":overlay: tree.node[b]", "a[1]", "", "Invalid local overlay reference"),
    (":overlay: other.node[a]", "a[1]", "tree", "Invalid local overlay reference"),
    (":overlay: tree.slot[0]", "a[1]", "tree", "Invalid overlay target"),
    (":overlay: tree.node[missing]", "a[1]", "tree", "Unknown overlay target"),
    (":overlay: tree.node[a]", "a['secret'] {invisible}", "tree", "is invisible"),
    (":overlay:", "a[1]", "tree", "argument required"),
    (":overlay-padding: 8", "a[1]", "tree", "require :overlay:"),
    (":overlay-layer: background", "a[1]", "tree", "require :overlay:"),
    (":overlay: tree.node[a]\n   :overlay-padding: -1", "a[1]", "tree", "finite number"),
    (":overlay: tree.node[a]\n   :overlay-padding: nan", "a[1]", "tree", "finite number"),
    (":overlay: tree.node[a]\n   :overlay-padding: inf", "a[1]", "tree", "finite number"),
    (":overlay: tree.node[a]\n   :overlay-padding: 1001", "a[1]", "tree", "finite number"),
    (":overlay: tree.node[a]\n   :overlay-layer: top", "a[1]", "tree", "invalid option value"),
    (':overlay: tree.node[a] <script>alert(1)</script>', "a[1]", "tree", "Invalid overlay target"),
    (":overlay-shape: circle", "a[1]", "tree", "require :overlay:"),
    (":overlay: a\n   :overlay-shape: triangle", "a[1]", "tree", "invalid option value"),
    (":overlay: a :overlay-shape: triangle", "a[1]", "tree", "overlay 1"),
    (":overlay: a :overlay-shape:", "a[1]", "tree", "Missing value"),
    (":overlay: a :color: red", "a[1]", "tree", "Unknown overlay setting"),
    (":overlay: a :overlay-layer: foreground :overlay-layer: background", "a[1]", "tree", "Duplicate overlay setting"),
    (":overlay: a :overlay-padding: nan", "a[1]", "tree", "finite number"),
    (":overlay: a :overlay-layer: upper", "a[1]", "tree", "overlay 1"),
    (":overlay: :overlay-shape: circle", "a[1]", "tree", "at least one node key"),
    (":overlay: a :overlay-padding: 4 b", "a[1]\nb[2]", "tree", "must precede settings"),
    (":overlay: a\n             missing", "a[1]", "tree", "overlay 2: Unknown overlay target"),
])
def test_invalid_overlay_options(option, body, key, message):
    document = parse_rst(graph_source(body, "   " + option, key))
    assert not list(document.findall(TbGraphNode))
    assert message in next(document.findall(nodes.system_message)).astext()


def test_multiple_overlays_have_independent_settings_and_accept_standalone_keys():
    node = graph("""   :overlay: a b a
             b c :overlay-shape: circle :overlay-layer: foreground :overlay-padding: 3
             a :overlay-shape: box
   :overlay-shape: rectangle
   :overlay-layer: background
   :overlay-padding: 12.5""", key="")
    assert node["annotations"] == [
        {"shape": "rectangle", "targets": ["a", "b"], "layer": "background", "padding": 12.5},
        {"shape": "circle", "targets": ["b", "c"], "layer": "foreground", "padding": 3},
        {"shape": "rectangle", "targets": ["a"], "layer": "background", "padding": 12.5},
    ]
    assert graph("   :overlay: a", key="")["annotations"] == [
        {"shape": "ellipse", "targets": ["a"], "layer": "foreground", "padding": 8}]
    assert graph()["annotations"] == []
    assert "A circle surrounds" in graph_description(node).astext()
    assert graph_description(node).astext().count("A rectangle surrounds") == 2


def test_enclosing_ellipse_includes_diagonal_padded_boxes():
    boxes = [(0, 0, 30, 30), (80, 90, 130, 145)]
    cx, cy, rx, ry, angle = ellipse_geometry(boxes, 8)
    for x0, y0, x1, y1 in boxes:
        for x in (x0 - 8, x1 + 8):
            for y in (y0 - 8, y1 + 8):
                px, py = transform_point(x, y, f"rotate({-angle} {cx} {cy})")
                assert ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1 + 1e-12


@pytest.mark.skipif(not shutil.which("dot"), reason="Graphviz is not installed")
@pytest.mark.parametrize("style", ["graph", "tree", "list", "array", "ring"])
@pytest.mark.parametrize("layer", ["background", "foreground"])
@pytest.mark.parametrize("shape", ["ellipse", "circle", "rectangle"])
def test_composition_uses_actual_bounds_preserves_layout_and_expands_viewport(style, layer, shape):
    node = graph(f"   :style: {style}\n   :overlay: tree.node[a] tree.node[b]\n"
                 f"   :overlay-layer: {layer}\n   :overlay-padding: 16\n   :overlay-shape: {shape}",
                 "a['a long value'] -> b[3]\nb -> c[12]\nspacer['private'] {invisible}")
    if style == "array":
        measurement = subprocess.run([shutil.which("dot"), "-Tplain"],
                                     input=measurement_dot(node), text=True, capture_output=True, check=True).stdout
        code = graph_dot(node, array_size=cell_dimensions(measurement))
    else:
        code = graph_dot(node)
    engine = "circo" if style == "ring" else "dot"
    source = subprocess.run([shutil.which(engine), "-Tsvg"], input=code,
                            text=True, capture_output=True, check=True).stdout
    original = ET.fromstring(source)
    original_graph = original.find(f"{tag('g')}[@class='graph']")
    root = ET.fromstring(compose_svg(source, node))
    rendered = root.find(f"{tag('g')}[@class='graph']")
    foreground = rendered.find(f"{tag('g')}[@class='tb-graph__annotations tb-graph__annotations--foreground']")
    background = rendered.find(f"{tag('g')}[@class='tb-graph__annotations tb-graph__annotations--background']")
    assert list(rendered)[-1] is foreground
    graph_groups = [element for element in rendered if element.tag == tag("g")
                    and element.get("class") in ("node", "edge")]
    assert list(rendered).index(background) < min(list(rendered).index(element) for element in graph_groups)
    assert foreground.get("pointer-events") == background.get("pointer-events") == "none"
    outline = (foreground if layer == "foreground" else background).find(
        tag({"ellipse": "ellipse", "circle": "circle", "rectangle": "rect"}[shape]))
    assert outline.get("data-targets") == "a b"
    assert outline.get("data-shape") == shape
    for key in ("a", "b"):
        x0, y0, x1, y1 = node_bounds(original_graph, node)[key]
        for x in (x0 - 16, x1 + 16):
            for y in (y0 - 16, y1 + 16):
                if shape == "ellipse":
                    cx, cy, rx, ry = (float(outline.get(key)) for key in ("cx", "cy", "rx", "ry"))
                    angle = float(outline.get("transform").split("(")[1].split()[0])
                    px, py = transform_point(x, y, f"rotate({-angle} {cx} {cy})")
                    assert ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1 + 1e-6
                elif shape == "circle":
                    cx, cy, radius = (float(outline.get(key)) for key in ("cx", "cy", "r"))
                    assert (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2 + 1e-3
                else:
                    bx, by, width, height = (float(outline.get(key)) for key in ("x", "y", "width", "height"))
                    assert bx - 1e-6 <= x <= bx + width + 1e-6
                    assert by - 1e-6 <= y <= by + height + 1e-6
    vx, vy, vw, vh = map(float, root.get("viewBox").split())
    if shape == "circle":
        rx = ry = radius
    elif shape == "rectangle":
        cx, cy, rx, ry = bx + width / 2, by + height / 2, width / 2, height / 2
    for x in (cx - rx - 1, cx + rx + 1):
        for y in (cy - ry - 1, cy + ry + 1):
            px, py = transform_point(x, y, rendered.get("transform") + " " + outline.get("transform", ""))
            assert vx <= px <= vx + vw and vy <= py <= vy + vh
    for group in (foreground, background):
        rendered.remove(group)
    assert ET.tostring(rendered) == ET.tostring(original_graph)
    assert "private" not in "".join(root.itertext())


@pytest.mark.parametrize("transform,point", [
    ("scale(2 3) rotate(0) translate(4 5)", (10, 21)),
    ("rotate(90) translate(4 5)", (-7, 5)),
    ("matrix(2 0 0 3 4 5)", (6, 11)),
])
def test_viewport_transforms(transform, point):
    assert transform_point(1, 2, transform) == pytest.approx(point)


@pytest.mark.skipif(not shutil.which("dot"), reason="Graphviz is not installed")
@pytest.mark.parametrize("builder", ["html", "text", "latex"])
def test_annotated_scene_across_builders(tmp_path, builder):
    if builder == "latex" and not shutil.which("rsvg-convert"):
        pytest.skip("librsvg is not installed")
    content = graph_source("a[8] -> b[3]", "   :style: tree\n"
                           "   :description: Compare the parent and child.\n"
                           "   :overlay: a b\n"
                           "             a :overlay-shape: rectangle :overlay-layer: background :overlay-padding: 4\n"
                           "             b :overlay-shape: circle", "tree")
    source = ("Annotated scenes\n================\n\n.. tb-stack::\n\n"
              "   .. tb-scene::\n      :caption: Compare\n\n"
              + "\n".join("      " + line for line in content.splitlines()))
    out, _ = build_sphinx(tmp_path, builder, source)
    if builder == "html":
        soup = BeautifulSoup((out / "index.html").read_text(), "html.parser")
        assert len(soup.find_all("tb-graph")) == len(soup.find_all("tb-scene")) == 1
        result = soup.find("tb-graph").get_text()
        asset = out / soup.find("tb-graph").find("img")["src"]
        assert "annotated" in asset.name
        assert ET.parse(asset).find(f".//{tag('ellipse')}[@data-targets='a b']") is not None
        model = json.loads(soup.find("tb-stack").find("script").string)
        assert model["scenes"][0]["objects"][0]["annotations"][0]["targets"] == ["a", "b"]
        assert len(model["scenes"][0]["objects"][0]["annotations"]) == 3
        root = ET.parse(asset).getroot()
        assert root.find(f".//{tag('circle')}[@data-targets='b']") is not None
        assert root.find(f".//{tag('rect')}[@data-targets='a']") is not None
    elif builder == "text":
        result = (out / "index.txt").read_text()
    else:
        result = next(out.glob("*.tex")).read_text()
        assert "tb-graph-annotated-" in result
        assert next(out.glob("tb-graph-annotated-*.pdf")).read_bytes().startswith(b"%PDF-")
    assert "Compare the parent and child." in result
    assert "An ellipse surrounds" in result
    assert "A circle surrounds" in result
    assert "A rectangle surrounds" in result


@pytest.mark.skipif(not shutil.which("dot"), reason="Graphviz is not installed")
def test_annotation_does_not_intercept_keyed_graph_clicks(tmp_path):
    source = """Click nodes
===========

.. tb-click::

   Select the smaller value.

   .. tb-graph:: tree
      :overlay: tree.node[a] tree.node[b]

      a[8] -> b[3]

   .. tb-hit:: b

      Correct.

   .. tb-miss:: a

      Try the child.
"""
    out, _ = build_sphinx(tmp_path, "html", source)
    soup = BeautifulSoup((out / "index.html").read_text(), "html.parser")
    assert len(soup.select('svg [role="button"]')) == 2
    layers = soup.select("svg .tb-graph__annotations")
    assert len(layers) == 2 and all(layer["pointer-events"] == "none" for layer in layers)
    assert "An ellipse surrounds" in soup.find("tb-graph").get_text()


def test_pdf_conversion_failure_reports_instead_of_exporting_unannotated_graph(tmp_path, monkeypatch):
    source = tmp_path / "original.svg"
    source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 60">'
                      '<g class="graph"><g class="node"><title>n0</title>'
                      '<ellipse cx="30" cy="30" rx="10" ry="10"/></g></g></svg>')
    node = graph("   :overlay: tree.node[a]", "a[8]")
    def unavailable(*args, **kwargs):
        raise FileNotFoundError("rsvg-convert")
    monkeypatch.setattr("sphinx_touchbook.generators.graph_annotations.subprocess.run", unavailable)
    with pytest.raises(GraphvizError, match="rsvg-convert on PATH"):
        annotated_asset("original.svg", source, node, "pdf")
    assert not list(tmp_path.glob("*.pdf"))
    svg_name, svg_path = annotated_asset("original.svg", source, node, "svg")
    assert Path(svg_name).name == svg_path.name
    assert source.read_text().count("ellipse") == 1
    first = svg_path.read_bytes()
    assert annotated_asset("original.svg", source, node, "svg")[1] == svg_path
    assert svg_path.read_bytes() == first
    node["annotations"][0]["padding"] = 20
    assert annotated_asset("original.svg", source, node, "svg")[1] != svg_path
