"""Generate Graphviz assets and readable semantic graph descriptions."""

from __future__ import annotations

from copy import copy
from html import escape
from pathlib import Path
from types import SimpleNamespace

from docutils import nodes
from sphinx.ext.graphviz import GraphvizError, render_dot
from sphinx.util import logging

from sphinx_touchbook.generators.common import (
    html_additional_targets, html_class_attr, latex_targets,
)
from sphinx_touchbook.generators.click import keyed_graph_svg, keyed_target_html
from sphinx_touchbook.generators.stack import graph_pointer_indicators
from sphinx_touchbook.generators.graph_array import (
    array_dot, array_origin, cell_dimensions, measurement_dot,
)
from sphinx_touchbook.generators.graph_annotations import annotated_asset

logger = logging.getLogger(__name__)


def dot_string(value):
    """Quote a literal label without enabling DOT or Graphviz escapes."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def tree_components(node):
    """Find tree-shaped components without imposing new authoring constraints."""
    neighbors = {item["key"]: set() for item in node["nodes"]}
    incoming = dict.fromkeys(neighbors, 0)
    for edge in node["edges"]:
        neighbors[edge["source"]].add(edge["target"])
        neighbors[edge["target"]].add(edge["source"])
        incoming[edge["target"]] += 1
    unseen = set(neighbors)
    eligible = set()
    while unseen:
        pending = [unseen.pop()]
        component = set(pending)
        while pending:
            for neighbor in neighbors[pending.pop()]:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    pending.append(neighbor)
        if (sum(incoming[key] for key in component) == len(component) - 1
                and all(incoming[key] <= 1 for key in component)):
            eligible.update(component)
    return eligible


def edge_dot(edge, ids, style, *, weight=None):
    attributes = []
    if style["relationship-labels"] and edge["relationship"] is not None:
        attributes.append("label=" + dot_string(edge["relationship"]))
    if style["layout"] == "graph" and edge["relationship"] in ("left", "right"):
        port = "sw" if edge["relationship"] == "left" else "se"
        attributes.append(f'tailport="{port}"')
    if edge["invisible"]:
        attributes.append('style="invis"')
    if weight is not None:
        attributes.append(f'weight="{weight}"')
    suffix = f' [{", ".join(attributes)}]' if attributes else ""
    return f'{ids[edge["source"]]} -> {ids[edge["target"]]}{suffix};'


def tree_edges(node, ids, style, edges):
    """Center parents and put annotations in child gaps, or below leaves."""
    eligible = tree_components(node)
    grouped = grouped_indicators(node)
    annotations = {target: f'tb_indicators_{ids[target]}' for target in grouped}
    outgoing = {}
    for edge in edges:
        outgoing.setdefault(edge["source"], []).append(edge)
    lines = []
    for parent, children in outgoing.items():
        if parent not in eligible:
            lines.extend(edge_dot(edge, ids, style) for edge in children)
            continue
        targets = [ids[edge["target"]] for edge in children]
        if len(children) == 1:
            missing = f'tb_missing_{ids[parent]}'
            lines.append(f'{missing} [label="", style="invis", width="0.5", height="0.5"];')
            if children[0]["relationship"] == "right":
                targets.insert(0, missing)
            else:
                targets.append(missing)
        if parent in annotations:
            # Give the label its own central slot even for an odd child count;
            # keeping a real child on the centerline could obstruct the arrow.
            anchor = annotations[parent]
            targets.insert((len(targets) + 1) // 2, anchor)
        elif len(targets) % 2 == 0:
            anchor = f'tb_middle_{ids[parent]}'
            lines.append(f'{anchor} [label="", style="invis", shape="point", width="0", height="0"];')
            targets.insert(len(targets) // 2, anchor)
        else:
            anchor = targets[len(targets) // 2]
        by_target = {ids[edge["target"]]: edge for edge in children}
        for target in targets:
            if target in by_target:
                lines.append(edge_dot(by_target[target], ids, style,
                                      weight=100 if target == anchor else 1))
            elif target == annotations.get(parent):
                lines.extend(tree_annotation_edges(ids[parent], target, style, len(grouped[parent])))
            else:
                weight = 100 if target == anchor else 1
                lines.append(f'{ids[parent]} -> {target} [style="invis", weight="{weight}"];')
        if len(targets) > 1:
            lines.append('{rank="same"; ' + ' -> '.join(targets) +
                         ' [style="invis", weight="1"]; }')
    for target, annotation in annotations.items():
        if target not in outgoing or target not in eligible:
            # Leaves have no child row to reuse. A weighted edge keeps the
            # label just below the target, clear of its siblings on either side.
            lines.extend(tree_annotation_edges(ids[target], annotation, style, len(grouped[target])))
    return lines


def tree_annotation_edges(target, annotation, style, count):
    horizontal = style["orientation"] == "horizontal"
    return [f'{target} -> {annotation} [dir="back", arrowtail="vee", arrowhead="none", '
            f'arrowsize="0.6", weight="100", '
            f'tailport="{"e" if horizontal else "s"}", '
            f'headport="i{index}:{"w" if horizontal else "n"}"];'
            for index in range(count)]


def grouped_indicators(node):
    grouped = {}
    for indicator in graph_pointer_indicators(node):
        grouped.setdefault(indicator["target"], []).append(indicator)
    return grouped


def graph_indicators(node, ids):
    """Define annotation labels and position those outside tree spacing."""
    style = node["style"]
    horizontal = style["orientation"] == "horizontal" and style["layout"] != "ring"
    lines = []
    for target_key, indicators in grouped_indicators(node).items():
        target = ids[target_key]
        identifier = f"tb_indicators_{target}"
        cells = []
        for index, indicator in enumerate(indicators):
            label = escape(indicator["key"].replace("\\", "\\\\"))
            cells.append(f'<TD PORT="i{index}">{label}</TD>')
        # Tree labels sit below targets (to their right in horizontal trees),
        # so shared labels face the target in a row (or a column, respectively).
        label_row = not horizontal if style["layout"] == "tree" else horizontal
        rows = ("<TR>" + "".join(cells) + "</TR>" if label_row else
                "".join(f"<TR>{cell}</TR>" for cell in cells))
        spacing = 8 if len(indicators) > 1 else 0
        label = (f'<TABLE BORDER="0" CELLBORDER="0" CELLPADDING="0" CELLSPACING="{spacing}">'
                 + rows + '</TABLE>')
        lines.append(f'{identifier} [label=<{label}>, '
                     'shape="plain", style="solid", width="0", height="0", margin="0"];')
        if style["layout"] == "tree":
            # Tree edges attach this label within the tree's reserved spacing.
            continue
        if style["layout"] != "ring":
            lines.append(f'{{rank="same"; {target}; {identifier};}}')
        for index in range(len(indicators)):
            attributes = ['dir="back"', 'arrowtail="vee"', 'arrowhead="none"',
                          'arrowsize="0.6"', 'constraint="false"', 'weight="0"']
            if style["layout"] != "ring":
                attributes.extend(['tailport="s"' if horizontal else 'tailport="e"',
                                   f'headport="i{index}:{"n" if horizontal else "w"}"'])
            lines.append(f'{target} -> {identifier} [{", ".join(attributes)}];')
    return lines


def graph_dot(node, *, array_size=None, array_position=(0, 0)):
    """Map semantic keys to internal IDs; all attributes are generated here."""
    if node["style"]["layout"] == "array":
        if array_size is None:
            raise ValueError("Array rendering requires measured cell dimensions.")
        return array_dot(node, array_size, array_position)
    ids = {item["key"]: f"n{index}" for index, item in enumerate(node["nodes"])}
    style = node["style"]
    direction = "LR" if style["orientation"] == "horizontal" else "TB"
    splines = "line" if style["connectors"] == "straight" else "spline"
    node_attributes = ["shape=" + dot_string(style["shape"]),
                       "fontname=" + dot_string(style["font"]),
                       "fontsize=" + dot_string(str(style["font-size"]))]
    if style["fill"]:
        node_attributes.extend(['style="filled"', "fillcolor=" + dot_string(style["fill"])])
    if style["layout"] == "tree":
        node_attributes.extend(['width="0.5"', 'height="0.5"', 'margin="0.02"'])
    lines = ['digraph touchbook {',
             f'graph [bgcolor="transparent", ordering="out", rankdir="{direction}", '
             f'splines="{splines}", nodesep="{style["node-spacing"]}", ranksep="{style["level-spacing"]}"];',
             'node [' + ', '.join(node_attributes) + '];',
             'edge [fontname=' + dot_string(style["font"]) + ', fontsize=' +
             dot_string(str(style["font-size"])) + ', arrowhead=' +
             dot_string(style["arrows"]) + ', arrowsize="0.5"];']
    if style["layout"] == "ring":
        spacing = max(style["node-spacing"], .6) if graph_pointer_indicators(node) else style["node-spacing"]
        lines.append(f'graph [mindist="{spacing}"];')
    for item in node["nodes"]:
        attributes = ["label=" + dot_string(item["value"])]
        if region := node.get("click_regions", {}).get(item["key"]):
            attributes.append(f'URL="#tb-click-region-{region["index"]}"')
        if item["invisible"]:
            attributes.append('style="invis"')
        elif item["key"] in node["highlighted"]:
            attributes.append('penwidth="3"')
            if style.get("highlight-fill"):
                attributes.extend(['style="filled"',
                                   "fillcolor=" + dot_string(style["highlight-fill"])])
        lines.append(f'{ids[item["key"]]} [{", ".join(attributes)}];')
    # Ordered output edges and ports preserve the distinction of left/right roles.
    edges = sorted(node["edges"], key=lambda edge: (
        ids[edge["source"]], {"left": 0, "right": 2}.get(edge["relationship"], 1)))
    if style["layout"] == "tree":
        lines.extend(tree_edges(node, ids, style, edges))
    else:
        lines.extend(edge_dot(edge, ids, style) for edge in edges)
    lines.extend(graph_indicators(node, ids))
    lines.append('}')
    return "\n".join(lines)


def prose_list(items):
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + ", and " + items[-1]


def graph_description(node):
    content = base_graph_description(node)
    by_key = {item["key"]: item for item in node["nodes"]}
    for annotation in node.get("annotations", []):
        labels = [f'“{by_key[key]["value"]}” (node {key})' for key in annotation["targets"]]
        shape = annotation["shape"]
        article = "An" if shape == "ellipse" else "A"
        content += nodes.paragraph(text=f'{article} {shape} surrounds {prose_list(labels)}.')
    return content


def base_graph_description(node):
    """Explain the diagram in prose, using values rather than an edge inventory."""
    content = nodes.container()
    if description := node.get("description"):
        content += nodes.paragraph(text=description)
        return content
    if not node["nodes"]:
        content += nodes.paragraph(text="Empty graph.")
        return content
    if node["style"]["layout"] == "array":
        direction = "left to right" if node["style"]["orientation"] == "horizontal" else "top to bottom"
        values, highlighted = [], []
        for index, item in enumerate(node["nodes"]):
            label = f'“{item["value"]}”' if item["value"] else "an unused cell"
            if item["invisible"]:
                label = "an undisplayed cell"
            elif node["show_indices"]:
                label = f'index {index}: {label}'
            values.append(label)
            if not item["invisible"] and item["key"] in node["highlighted"]:
                highlighted.append(label)
        content += nodes.paragraph(text=f'Array with {len(values)} cells. From {direction}: {prose_list(values)}.')
        if highlighted:
            verb = "is" if len(highlighted) == 1 else "are"
            content += nodes.paragraph(text=f'{prose_list(highlighted)} {verb} highlighted.')
        targets = {item["key"]: (index, item) for index, item in enumerate(node["nodes"])}
        for indicator in node.get("indicators", []):
            index, item = targets[indicator["target"]]
            position = f'cell {index}, value “{item["value"]}”' if item["value"] else f'unused cell {index}'
            content += nodes.paragraph(text=f'Indicator “{indicator["key"]}” points to {position}.')
        return content
    by_key = {item["key"]: item for item in node["nodes"]}
    visible = [item for item in node["nodes"] if not item["invisible"]]
    edges = [edge for edge in node["edges"] if not edge["invisible"]]
    if not visible and not edges:
        content += nodes.paragraph(text="No visible graph components.")
        return content
    labels = {}
    counts = {}
    for item in visible:
        counts[item["value"]] = counts.get(item["value"], 0) + 1
    for item in visible:
        label = f'“{item["value"]}”' if item["value"] else "an unlabeled node"
        if counts[item["value"]] > 1:
            label += f' (node {item["key"]})'
        labels[item["key"]] = label
    outgoing = {}
    incoming = dict.fromkeys(by_key, 0)
    for edge in edges:
        outgoing.setdefault(edge["source"], []).append(edge)
        incoming[edge["target"]] += 1
    is_tree = (node["style"]["layout"] == "tree"
               and tree_components(node) == set(by_key))
    kind = "Tree diagram" if is_tree else "Directed graph"
    if node["style"]["layout"] == "list":
        kind = "Linked list diagram"
    elif node["style"]["layout"] == "ring":
        kind = "Circular graph diagram"
    count = len(visible)
    content += nodes.paragraph(text=f'{kind} with {count} visible {"node" if count == 1 else "nodes"}.')
    if is_tree:
        roots = [labels[item["key"]] for item in visible if incoming[item["key"]] == 0]
        if roots:
            subject = "The root is" if len(roots) == 1 else "The roots are"
            content += nodes.paragraph(text=f"{subject} {prose_list(roots)}.")
    sentences = []
    for source, connections in outgoing.items():
        source_label = labels.get(source, "An undisplayed endpoint")
        if is_tree:
            children = []
            for edge in sorted(connections, key=lambda edge: {"left": 0, "right": 2}.get(edge["relationship"], 1)):
                target = labels.get(edge["target"], "an undisplayed endpoint")
                role = edge["relationship"]
                child = f'{role} child {target}' if role in ("left", "right") else f'child {target}'
                children.append(child)
            sentences.append(f'{source_label} has {prose_list(children)}.')
        else:
            targets = []
            for edge in connections:
                target = labels.get(edge["target"], "an undisplayed endpoint")
                if edge["relationship"]:
                    target += f' through the “{edge["relationship"]}” relationship'
                targets.append(target)
            sentences.append(f'{source_label} points to {prose_list(targets)}.')
    if sentences:
        content += nodes.paragraph(text=" ".join(sentences))
    isolated = [labels[item["key"]] for item in visible
                if not outgoing.get(item["key"]) and incoming[item["key"]] == 0]
    if isolated and not is_tree:
        verb = "is" if len(isolated) == 1 else "are"
        content += nodes.paragraph(text=f'{prose_list(isolated)} {verb} isolated.')
    elif is_tree:
        leaves = [labels[item["key"]] for item in visible if not outgoing.get(item["key"])]
        if leaves:
            verb = "is a leaf" if len(leaves) == 1 else "are leaves"
            content += nodes.paragraph(text=f'{prose_list(leaves)} {verb}.')
    highlighted = [labels[item["key"]] for item in visible if item["key"] in node["highlighted"]]
    if highlighted:
        verb = "is" if len(highlighted) == 1 else "are"
        content += nodes.paragraph(text=f'{prose_list(highlighted)} {verb} highlighted.')
    for indicator in node.get("indicators", []):
        content += nodes.paragraph(text=f'Indicator “{indicator["key"]}” points to {labels[indicator["target"]]}.')
    return content


def render_graph(translator, node, format, *, return_path=False):
    if not node["nodes"]:
        return None
    if format != "svg" and node.get("click_regions"):
        node = node.copy()
        node.attributes.pop("click_regions")
    try:
        options = {"docname": translator.builder.env.path2doc(node.source) or "index"}
        if node["style"]["layout"] == "ring":
            options["graphviz_dot"] = "circo"
        array_size = None
        array_position = (0, 0)
        if node["style"]["layout"] == "array":
            # Measurements contain source labels, including invisible values.
            # Cache them with doctrees, outside the published image directory.
            builder = translator.builder
            if not hasattr(builder, "_graphviz_warned_dot"):
                builder._graphviz_warned_dot = {}
            cache_builder = copy(builder)
            cache_builder.outdir = builder.doctreedir
            cache_builder.imagedir = "tb-graph-measure"
            cached = SimpleNamespace(builder=cache_builder)
            _, measured = render_dot(cached, measurement_dot(node), options,
                                     "plain", prefix="tb-graph-measure")
            if measured is None:
                return None
            array_size = cell_dimensions(Path(measured).read_text(encoding="utf-8"))
            if graph_pointer_indicators(node):
                _, layout = render_dot(cached, graph_dot(node, array_size=array_size),
                                       options, "plain", prefix="tb-graph-measure")
                if layout is None:
                    return None
                array_position = array_origin(Path(layout).read_text(encoding="utf-8"))
        filename, output_path = render_dot(
            translator, graph_dot(node, array_size=array_size, array_position=array_position),
            options,
            "svg" if node.get("annotations") else format, prefix="tb-graph")
        if output_path is not None and node.get("annotations"):
            filename, output_path = annotated_asset(filename, output_path, node, format)
        return output_path if return_path else filename
    except GraphvizError as error:
        logger.warning("tb-graph could not render its diagram: %s", error,
                       location=node, type="touchbook", subtype="graphviz")
        return None


def visit_tb_graph_html(self, node):
    self.body.append(html_additional_targets(node))
    key = f' data-key="{escape(node["key"], quote=True)}"' if node["key"] else ""
    self.body.append(f'<tb-graph id="{escape(node["ids"][0], quote=True)}"{html_class_attr(node)}{key}>\n')
    for option in ("label", "caption"):
        if node[option]:
            self.body.append(f'<p class="tb-graph__{option}">{escape(node[option])}</p>\n')
    interactive = bool(node.get("click_regions"))
    filename = render_graph(self, node, "svg", return_path=interactive)
    if filename:
        if interactive:
            self.body.append(keyed_graph_svg(node, filename))
        else:
            alt = escape(node["label"] or node["caption"] or "Graph diagram", quote=True)
            self.body.append(f'<img class="tb-graph__diagram" src="{escape(str(filename), quote=True)}" alt="{alt}">\n')
        self.body.append('<details class="tb-graph__description"><summary>Text description</summary>\n')
    graph_description(node).walkabout(self)
    if filename:
        self.body.append('</details>\n')
    elif interactive:
        # Keep the question usable when Graphviz cannot produce an image.
        self.body.append('<ul class="tb-click__graph-targets">')
        for item in node["nodes"]:
            if item["key"] in node["click_regions"]:
                self.body.append('<li>' + keyed_target_html(node, item["key"], item["value"]) + '</li>')
        self.body.append('</ul>\n')
    self.body.append('</tb-graph>\n')
    raise nodes.SkipNode


def static_content(node):
    content = nodes.container()
    for option in ("label", "caption"):
        if node[option]:
            content += nodes.paragraph(text=node[option])
    return content


def visit_tb_graph_latex(self, node):
    latex_targets(self, node)
    content = static_content(node)
    filename = render_graph(self, node, "pdf")
    if filename:
        content += nodes.image(uri=str(filename),
                               alt=node["label"] or node["caption"] or "Graph diagram")
    content += graph_description(node)
    content.walkabout(self)
    raise nodes.SkipNode


def visit_tb_graph_text(self, node):
    content = static_content(node)
    content += graph_description(node)
    content.walkabout(self)
    raise nodes.SkipNode


def depart_tb_graph(self, node):
    pass
