"""Graphviz array tables with measured cells and rounded outer corners."""

from html import escape
from math import ceil
from sphinx_touchbook.generators.stack import graph_pointer_indicators


def dot_string(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def measurement_dot(node):
    """Ask Graphviz to size literal labels using the selected font."""
    style = node["style"]
    lines = ['digraph touchbook {',
             'node [shape="box", width="0", height="0", margin="0.083333,0.083333", '
             'fontname=' + dot_string(style["font"]) + ', fontsize=' +
             dot_string(str(style["font-size"])) + '];']
    for index, item in enumerate(node["nodes"]):
        lines.append(f'n{index} [label={dot_string(item["value"])}];')
        if node["show_indices"]:
            lines.append(f'i{index} [label="{index}"];')
    return "\n".join(lines + ['}'])


def cell_dimensions(plain):
    """Use a common size large enough for every value and index (in points)."""
    sizes = [line.split()[4:6] for line in plain.splitlines()
             if line.startswith("node ")]
    width = max([32] + [ceil(float(width) * 72) + 2 for width, height in sizes])
    height = max([32] + [ceil(float(height) * 72) + 2 for width, height in sizes])
    return width, height


def rounded_box(x, y, width, height, radii):
    """An xdot Bezier path; radii are top-left, top-right, bottom-right, bottom-left."""
    tl, tr, br, bl = radii
    k = .5522847498
    points = [(x + tl, y + height)]

    def line(end):
        points.extend([points[-1], end, end])

    line((x + width - tr, y + height))
    points.extend([(x + width - tr + k * tr, y + height),
                   (x + width, y + height - tr + k * tr),
                   (x + width, y + height - tr)])
    line((x + width, y + br))
    points.extend([(x + width, y + br - k * br),
                   (x + width - br + k * br, y), (x + width - br, y)])
    line((x + bl, y))
    points.extend([(x + bl - k * bl, y), (x, y + bl - k * bl), (x, y + bl)])
    line((x, y + height - tl))
    points.extend([(x, y + height - tl + k * tl),
                   (x + tl - k * tl, y + height), (x + tl, y + height)])
    return str(len(points)) + " " + " ".join(f"{px:g} {py:g}" for px, py in points)


def array_origin(plain):
    """Find the array table's lower-left corner after automatic indicator layout."""
    for line in plain.splitlines():
        parts = line.split()
        if len(parts) >= 6 and parts[:2] == ["node", "tb_array"]:
            x, y, width, height = map(float, parts[2:6])
            return (x - width / 2) * 72, (y - height / 2) * 72
    raise ValueError("Graphviz did not return the array table position.")


def array_dot(node, size, origin=(0, 0)):
    """Keep text in native Graphviz cells; draw their borders and fills behind it."""
    style = node["style"]
    width, height = size
    vertical = style["orientation"] == "vertical"
    index_height = max(16, height - 8)
    values, indices, drawing = [], [], []
    count = len(node["nodes"])
    markers = graph_pointer_indicators(node)
    show_end = any(marker["target"] == ".end" for marker in markers)
    gap = 20 if count and show_end else 0
    extra_height = height + gap if vertical and show_end else 0
    for index, item in enumerate(node["nodes"]):
        invisible = ' STYLE="INVIS"' if item["invisible"] else ""
        value = escape(item["value"].replace("\\", "\\\\"), quote=True)
        link = ""
        if region := node.get("click_regions", {}).get(item["key"]):
            link = f' HREF="#tb-click-region-{region["index"]}"'
        values.append(f'<TD PORT="n{index}" WIDTH="{width}" HEIGHT="{height}" '
                      f'FIXEDSIZE="TRUE"{invisible}{link}>{value}</TD>')
        indices.append(f'<TD WIDTH="{width}" HEIGHT="{height if vertical else index_height}" '
                       f'FIXEDSIZE="TRUE"{invisible}>{index}</TD>')
        if item["invisible"]:
            continue
        fill = style.get("unused-fill") if item["value"] == "" else style["fill"]
        highlighted = item["key"] in node["highlighted"]
        if highlighted:
            fill = style.get("highlight-fill") or fill
        pen = "setlinewidth(3)" if highlighted else "setlinewidth(1)"
        drawing.append(f'c 5 -black S {len(pen)} -{pen}')
        if fill:
            drawing.append(f'C {len(fill)} -{fill}')
        radius = min(6, width / 4, height / 4)
        first, last = index == 0, index == count - 1
        if vertical:
            x = width if node["show_indices"] else 0
            y = (count - index - 1) * height + extra_height
            radii = (radius if first else 0, radius if first else 0,
                     radius if last else 0, radius if last else 0)
        else:
            x = index * width
            y = index_height if node["show_indices"] else 0
            radii = (radius if first else 0, radius if last else 0,
                     radius if last else 0, radius if first else 0)
        drawing.append(("b " if fill else "B ") + rounded_box(
            x + origin[0], y + origin[1], width, height, radii))
    if vertical:
        rows = [f'<TR>{indices[index] if node["show_indices"] else ""}{value}</TR>'
                for index, value in enumerate(values)]
        if show_end:
            if gap:
                columns = 2 if node["show_indices"] else 1
                rows.append(f'<TR><TD COLSPAN="{columns}" HEIGHT="{gap}" FIXEDSIZE="TRUE" WIDTH="{width * columns}"></TD></TR>')
            rows.append('<TR>' + (f'<TD WIDTH="{width}" HEIGHT="{height}"></TD>' if node["show_indices"] else '')
                        + f'<TD PORT="end" WIDTH="{width}" HEIGHT="{height}" FIXEDSIZE="TRUE"></TD></TR>')
    else:
        if show_end:
            if gap:
                values.append(f'<TD WIDTH="{gap}" HEIGHT="{height}" FIXEDSIZE="TRUE"></TD>')
                indices.append(f'<TD WIDTH="{gap}" HEIGHT="{index_height}" FIXEDSIZE="TRUE"></TD>')
            values.append(f'<TD PORT="end" WIDTH="{width}" HEIGHT="{height}" FIXEDSIZE="TRUE"></TD>')
            indices.append(f'<TD WIDTH="{width}" HEIGHT="{index_height}" FIXEDSIZE="TRUE"></TD>')
        rows = ["<TR>" + "".join(values) + "</TR>"]
        if node["show_indices"]:
            rows.append("<TR>" + "".join(indices) + "</TR>")
    if show_end:
        x = (width if node["show_indices"] else 0) if vertical else count * width + gap
        y = 0 if vertical else (index_height if node["show_indices"] else 0)
        drawing.extend(['c 5 -black S 15 -setlinewidth(1) S 6 -dotted',
                        'B ' + rounded_box(x + origin[0], y + origin[1], width, height, (0, 0, 0, 0))])
    table = ('<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="0">'
             + "".join(rows) + '</TABLE>')
    direction = "LR" if vertical else "TB"
    indicators = []
    positions = {item["key"]: index for index, item in enumerate(node["nodes"])}
    for index, indicator in enumerate(markers):
        identifier = f"tb_indicator_{index}"
        indicators.append(f'{identifier} [label={dot_string(indicator["key"])}];')
        port = 'tb_array:end' if indicator["target"] == ".end" else f'tb_array:n{positions[indicator["target"]]}'
        if vertical:
            indicators.append(f'{port}:e -> {identifier}:w [dir="back", arrowtail="vee"];')
        else:
            indicators.append(f'{identifier}:s -> {port}:n;')
    return ('digraph touchbook {\n'
            'graph [bgcolor="transparent", _background=' + dot_string(" ".join(drawing)) + '];\n'
            f'graph [rankdir="{direction}", splines="line", ranksep="0.3"];\n'
            'node [shape="plain", fontname=' + dot_string(style["font"]) +
            ', fontsize=' + dot_string(str(style["font-size"])) + '];\n'
            'edge [arrowhead="vee", arrowsize="0.6"];\n'
            'tb_array [label=<' + table + '>];\n' + "\n".join(indicators) + '\n}')
