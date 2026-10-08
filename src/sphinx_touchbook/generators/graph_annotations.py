"""Compose static annotations over Graphviz's completed SVG layout."""

from __future__ import annotations

from hashlib import sha256
import json
import math
import os
from pathlib import Path
import re
import subprocess
from tempfile import NamedTemporaryFile
import xml.etree.ElementTree as ET

from sphinx.ext.graphviz import GraphvizError


SVG = "http://www.w3.org/2000/svg"
NUMBER = r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?"


def tag(name):
    return f"{{{SVG}}}{name}"


def shape_bounds(shape):
    """Bounds in Graphviz's drawing coordinates, including stroke width."""
    if shape.tag == tag("ellipse"):
        x, y, rx, ry = (float(shape.get(key)) for key in ("cx", "cy", "rx", "ry"))
        bounds = x - rx, y - ry, x + rx, y + ry
    elif shape.tag in (tag("polygon"), tag("path")):
        # Bezier control points give conservative bounds for rounded cells.
        numbers = list(map(float, re.findall(NUMBER, shape.get("points", shape.get("d", "")))))
        if not numbers or len(numbers) % 2:
            raise ValueError("Invalid Graphviz shape coordinates.")
        xs, ys = numbers[::2], numbers[1::2]
        bounds = min(xs), min(ys), max(xs), max(ys)
    else:
        raise ValueError("Unsupported Graphviz node shape.")
    stroke = float(shape.get("stroke-width", "1")) / 2
    return expand(bounds, stroke)


def expand(bounds, padding):
    x0, y0, x1, y1 = bounds
    return x0 - padding, y0 - padding, x1 + padding, y1 + padding


def union(bounds):
    return (min(box[0] for box in bounds), min(box[1] for box in bounds),
            max(box[2] for box in bounds), max(box[3] for box in bounds))


def node_bounds(graph, node):
    """Resolve author keys to actual rendered node or array-cell bounds."""
    if node["style"]["layout"] == "array":
        # Array borders are paths in Graphviz's background drawing, in cell
        # declaration order. Invisible cells have no border or exposed value.
        visible = [item for item in node["nodes"] if not item["invisible"]]
        borders = graph.findall(tag("path"))
        if len(visible) != len(borders):
            raise ValueError("Graphviz did not return the array cell borders.")
        return {item["key"]: shape_bounds(border) for item, border in zip(visible, borders)}
    rendered = {}
    for group in graph.findall(f"{tag('g')}[@class='node']"):
        title = group.find(tag("title"))
        if title is None:
            continue
        shapes = [shape_bounds(shape) for shape in group.iter()
                  if shape.tag in (tag("ellipse"), tag("polygon"), tag("path"))]
        if shapes:
            rendered[title.text] = union(shapes)
    return {item["key"]: rendered[f"n{index}"]
            for index, item in enumerate(node["nodes"]) if not item["invisible"]}


def ellipse_geometry(bounds, padding):
    """Align the ellipse with the targets and enclose every padded target box."""
    padded = [expand(box, padding) for box in bounds]
    centers = [((box[0] + box[2]) / 2, (box[1] + box[3]) / 2) for box in bounds]
    ox = sum(x for x, y in centers) / len(centers)
    oy = sum(y for x, y in centers) / len(centers)
    xx = sum((x - ox) ** 2 for x, y in centers)
    yy = sum((y - oy) ** 2 for x, y in centers)
    xy = sum((x - ox) * (y - oy) for x, y in centers)
    angle = math.atan2(2 * xy, xx - yy) / 2 if xx != yy or xy else 0
    cosine, sine = math.cos(angle), math.sin(angle)
    points = [((x - ox) * cosine + (y - oy) * sine,
               -(x - ox) * sine + (y - oy) * cosine)
              for box in padded for x in (box[0], box[2]) for y in (box[1], box[3])]
    x0, y0 = min(x for x, y in points), min(y for x, y in points)
    x1, y1 = max(x for x, y in points), max(y for x, y in points)
    local_x, local_y = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = max((x1 - x0) / 2, .5), max((y1 - y0) / 2, .5)
    scale = max(1, *(math.hypot((x - local_x) / rx, (y - local_y) / ry) for x, y in points))
    return (ox + local_x * cosine - local_y * sine,
            oy + local_x * sine + local_y * cosine,
            rx * scale, ry * scale, math.degrees(angle))


def transform_point(x, y, transform):
    """Apply Graphviz's SVG viewport transform, in SVG composition order."""
    operations = re.findall(r"(\w+)\s*\(([^)]*)\)", transform)
    for operation, source in reversed(operations):
        values = list(map(float, re.findall(NUMBER, source)))
        if operation == "translate":
            x, y = x + values[0], y + (values[1] if len(values) > 1 else 0)
        elif operation == "scale":
            x, y = x * values[0], y * (values[1] if len(values) > 1 else values[0])
        elif operation == "rotate":
            angle = math.radians(values[0])
            ox, oy = values[1:] if len(values) == 3 else (0, 0)
            x, y = x - ox, y - oy
            x, y = (x * math.cos(angle) - y * math.sin(angle) + ox,
                    x * math.sin(angle) + y * math.cos(angle) + oy)
        elif operation == "matrix":
            a, b, c, d, e, f = values
            x, y = a * x + c * y + e, b * x + d * y + f
        else:
            raise ValueError(f"Unsupported Graphviz SVG transform {operation!r}.")
    return x, y


def overlay_geometry(annotation, bounds):
    """Return a shape and its drawing bounds independently of graph nodes."""
    targets = [bounds[key] for key in annotation["targets"]]
    padding = annotation["padding"]
    if annotation["shape"] == "ellipse":
        cx, cy, rx, ry, angle = ellipse_geometry(targets, padding)
        rotation = f"rotate({angle:.6f} {cx:.6f} {cy:.6f})"
        shape = ET.Element(tag("ellipse"), {
            "cx": f"{cx:.6f}", "cy": f"{cy:.6f}", "rx": f"{rx:.6f}", "ry": f"{ry:.6f}",
            "transform": rotation,
        })
        extent = cx - rx, cy - ry, cx + rx, cy + ry
    else:
        x0, y0, x1, y1 = union([expand(box, padding) for box in targets])
        rotation = ""
        if annotation["shape"] == "circle":
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            radius = math.hypot((x1 - x0) / 2, (y1 - y0) / 2)
            shape = ET.Element(tag("circle"), {
                "cx": f"{cx:.6f}", "cy": f"{cy:.6f}", "r": f"{radius:.6f}",
            })
            extent = cx - radius, cy - radius, cx + radius, cy + radius
        elif annotation["shape"] == "rectangle":
            shape = ET.Element(tag("rect"), {
                "x": f"{x0:.6f}", "y": f"{y0:.6f}",
                "width": f"{x1 - x0:.6f}", "height": f"{y1 - y0:.6f}",
            })
            extent = x0, y0, x1, y1
        else:
            raise ValueError(f"Unsupported overlay shape {annotation['shape']!r}.")
    shape.attrib.update({"fill": "none", "stroke": "#b45309", "stroke-width": "2",
                         "data-targets": " ".join(annotation["targets"]),
                         "data-shape": annotation["shape"]})
    return shape, expand(extent, 2), rotation


def compose_svg(source, node):
    """Add layers without rerunning layout or changing existing SVG geometry."""
    root = ET.fromstring(source)
    graph = root.find(f"{tag('g')}[@class='graph']")
    if graph is None:
        raise ValueError("Graphviz did not return an SVG graph group.")
    bounds = node_bounds(graph, node)
    layers = {layer: ET.Element(tag("g"), {
        "class": f"tb-graph__annotations tb-graph__annotations--{layer}",
        "pointer-events": "none", "aria-hidden": "true",
    }) for layer in ("background", "foreground")}
    viewport = list(map(float, root.get("viewBox").split()))
    viewport_bounds = [(viewport[0], viewport[1], viewport[0] + viewport[2], viewport[1] + viewport[3])]
    for annotation in node["annotations"]:
        shape, (x0, y0, x1, y1), rotation = overlay_geometry(annotation, bounds)
        layers[annotation["layer"]].append(shape)
        corners = [transform_point(x, y, graph.get("transform", "") + " " + rotation)
                   for x in (x0, x1) for y in (y0, y1)]
        viewport_bounds.append((min(x for x, y in corners), min(y for x, y in corners),
                                max(x for x, y in corners), max(y for x, y in corners)))
    # The transparent canvas comes first; annotation layers share the graph's
    # transform and scale together with nodes, labels, and edges.
    canvas = graph.find(tag("polygon"))
    graph.insert(list(graph).index(canvas) + 1 if canvas is not None else 0, layers["background"])
    graph.append(layers["foreground"])
    x0, y0, x1, y1 = union(viewport_bounds)
    root.set("viewBox", f"{x0:.6f} {y0:.6f} {x1 - x0:.6f} {y1 - y0:.6f}")
    root.set("width", f"{x1 - x0:.6f}pt")
    root.set("height", f"{y1 - y0:.6f}pt")
    ET.register_namespace("", SVG)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def write_asset(path, content):
    """Publish complete cached assets atomically for parallel Sphinx builds."""
    with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    try:
        os.replace(temporary_path, path)
    finally:
        temporary_path.unlink(missing_ok=True)


def annotated_asset(filename, output_path, node, format):
    """Cache composition separately from the unchanged Graphviz layout asset."""
    source = Path(output_path).read_bytes()
    identity = source + json.dumps(node["annotations"], sort_keys=True).encode() + b"annotations-v3"
    name = f"tb-graph-annotated-{sha256(identity).hexdigest()}"
    path = Path(output_path).with_name(f"{name}.{format}")
    if not path.is_file():
        try:
            composed = compose_svg(source, node)
            if format == "pdf":
                result = subprocess.run(["rsvg-convert", "--format=pdf"], input=composed,
                                        capture_output=True, check=True, timeout=30)
                composed = result.stdout
                if not composed.startswith(b"%PDF-"):
                    raise ValueError("rsvg-convert did not produce a PDF.")
            write_asset(path, composed)
        except (ValueError, KeyError, ET.ParseError, OSError, subprocess.SubprocessError) as error:
            requirement = (" Annotated PDF output requires librsvg's rsvg-convert on PATH."
                           if format == "pdf" else "")
            raise GraphvizError(f"Could not compose graph annotations.{requirement} {error}") from error
    return str(Path(filename).with_name(path.name)), path
