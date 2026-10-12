"""Native Graphviz table labels for array content inside tree/list nodes."""

from html import escape

from sphinx_touchbook.graph_content import CELL_TARGET, cell_key, scalar_text
from sphinx_touchbook.generators.graph_array import (
    measurement_dot, cell_drawing, cell_radii,
)


def measurement_graph(node):
    labels = []
    for item in node["nodes"]:
        if "content" not in item:
            labels.append({"value": item["value"]})
            continue
        if not item["content"]["values"]:
            labels.append({"value": "[]"})
        for index, value in enumerate(item["content"]["values"]):
            labels.append({"value": plain_label(value)})
            if node["show_indices"]:
                labels.append({"value": str(index)})
    return measurement_dot({"style": node["style"], "nodes": labels,
                            "show_indices": False})


def plain_label(value):
    return scalar_text(value).replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")


def label_html(value):
    text = plain_label(value).replace("\\", "\\\\")
    return escape(text, quote=True).replace("\n", '<BR ALIGN="CENTER"/>')


def table_label(item, node, size, *, background=False):
    """Return generated DOT attributes, never author-provided DOT/HTML."""
    width, height = size
    style = node["style"]
    cells, indices = [], []
    for index, value in enumerate(item["content"]["values"]):
        target = cell_key(item["key"], index)
        fill = style.get("unused-fill") if value == "" else style["fill"]
        highlighted = target in node["highlighted"]
        if highlighted:
            fill = style.get("highlight-fill") or fill
        attrs = [f'PORT="c{index}"', f'WIDTH="{width}"', f'HEIGHT="{height}"',
                 'FIXEDSIZE="TRUE"', f'BORDER="{0 if background else 3 if highlighted else 1}"']
        if fill and not background:
            attrs.append(f'BGCOLOR="{escape(fill, quote=True)}"')
        if region := node.get("click_regions", {}).get(target):
            attrs.append(f'HREF="#tb-click-region-{region["index"]}"')
        cells.append('<TD ' + ' '.join(attrs) + '>' + label_html(value) + '</TD>')
        indices.append(f'<TD PORT="i{index}" BORDER="0" WIDTH="{width}">{index}</TD>')
    # An empty array still has a visible shape, but no selectable cell.
    if not cells:
        cells.append(f'<TD BORDER="{0 if background else 1}" WIDTH="{width}" '
                     f'HEIGHT="{height}" FIXEDSIZE="TRUE">[]</TD>')
    rows = '<TR>' + ''.join(cells) + '</TR>'
    if node["show_indices"] and indices:
        rows += '<TR>' + ''.join(indices) + '</TR>'
    table = ('<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3">'
             + rows + '</TABLE>')
    return ['label=<' + table + '>', 'shape="plain"', 'style="solid"',
            'margin="0"', 'width="0"', 'height="0"']


def target_endpoint(target, ids, node):
    if match := CELL_TARGET.fullmatch(target):
        port = "i" if node["show_indices"] else "c"
        return f'{ids[match[1]]}:{port}{match[2]}'
    return ids[target]


def target_port(target, side, node):
    match = CELL_TARGET.fullmatch(target)
    port = "i" if node["show_indices"] else "c"
    return f"{port}{match[2]}:{side}" if match else side


def content_positions(plain):
    """Read native table bounds from the completed Graphviz layout, in points."""
    positions = {}
    for line in plain.splitlines():
        parts = line.split()
        if len(parts) >= 6 and parts[0] == "node":
            positions[parts[1]] = tuple(float(value) * 72 for value in parts[2:6])
    return positions


def content_drawing(node, size, positions):
    """Draw measured arrays behind native labels without changing layout."""
    width, height = size
    style = node["style"]
    drawing = []
    for number, item in enumerate(node["nodes"]):
        if "content" not in item or item["invisible"]:
            continue
        cx, cy, total_width, total_height = positions[f"n{number}"]
        x, y = cx - total_width / 2, cy + total_height / 2 - height
        values = item["content"]["values"]
        count = max(1, len(values))
        for index in range(count):
            value = values[index] if values else "[]"
            fill = style.get("unused-fill") if value == "" else style["fill"]
            highlighted = cell_key(item["key"], index) in node["highlighted"]
            if highlighted:
                fill = style.get("highlight-fill") or fill
            drawing.extend(cell_drawing(x + index * width, y, size,
                                        cell_radii(size, index, count), fill,
                                        highlighted))
    return " ".join(drawing)
