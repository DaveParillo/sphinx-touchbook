"""Render arrays as static, accessible HTML and native builder tables."""

from __future__ import annotations

from html import escape

from docutils import nodes

from sphinx_touchbook.generators.common import (
    html_additional_targets, html_class_attr, latex_targets,
)
from sphinx_touchbook.generators.click import keyed_target_html
from sphinx_touchbook.generators.stack import pointer_html, pointers_for


def annotations(node, index, *, include_highlight=True):
    result = []
    if include_highlight and index in node["highlighted"]:
        result.append("Highlighted")
    interval = node["range"]
    if interval is not None and interval[0] <= index < interval[1]:
        result.append(node["range_label"] or "In range")
    return result


def range_description(node):
    interval = node["range"]
    if interval is None:
        return ""
    start = node["start_index"]
    description = f"Range [{interval[0] + start}, {interval[1] + start})"
    if node["range_label"]:
        description += f": {node['range_label']}"
    if interval[0] == interval[1]:
        description += " (empty)"
    return description


def html_cell(node, index, item):
    classes = ["tb-array__cell"]
    description = ""
    if index in node["highlighted"]:
        classes.append("tb-array__cell--highlighted")
        description = ' aria-description="Highlighted"'
    interval = node["range"]
    if interval and interval[0] <= index < interval[1]:
        classes.append("tb-array__cell--range")
    item_attr = f' data-item-key="{escape(item["key"], quote=True)}"' if item["key"] else ""
    parts = [f'<td class="{" ".join(classes)}" data-slot="{index}"{item_attr}{description}>',
             f'<span class="tb-array__value">{keyed_target_html(node, item["key"], item["value"])}</span>']
    if node["show_keys"] and item["key"] is not None:
        parts.append(f'<span class="tb-array__key">Key: {escape(item["key"])}</span>')
    for annotation in annotations(node, index, include_highlight=False):
        parts.append(f'<span class="tb-array__annotation">{escape(annotation)}</span>')
    parts.append('</td>')
    return "".join(parts)


def visit_tb_array_html(self, node):
    node_id = escape(node["ids"][0], quote=True)
    self.body.append(html_additional_targets(node))
    key_attr = f' data-key="{escape(node["key"], quote=True)}"' if node["key"] else ""
    self.body.append(f'<tb-array id="{node_id}"{html_class_attr(node)}{key_attr}>\n')
    if node["label"]:
        self.body.append(f'<p class="tb-array__label">{escape(node["label"])}</p>\n')
    pointers = pointers_for(node, position_type="array")
    end_pointers = [pointer for pointer in pointers if pointer["position"]["end"]]

    def markers(index, vertical=False):
        return "".join(pointer_html(pointer, placed=True, vertical=vertical) for pointer in pointers
                       if pointer["position"]["index"] == index)

    if node["elements"]:
        scroll_label = escape(f'{node["label"] or node["caption"] or "Array"} scroll area', quote=True)
        self.body.append(f'<div class="tb-array__scroll" role="region" aria-label="{scroll_label}" tabindex="0">'
                         '<table class="tb-array__table">\n')
        if node["caption"]:
            self.body.append(f'<caption>{escape(node["caption"])}</caption>\n')
        if node["orientation"] == "vertical":
            self.body.append('<thead><tr><th scope="col">Index</th>'
                             '<th scope="col">Value</th>')
            if pointers:
                self.body.append('<th scope="col">Pointer</th>')
            self.body.append('</tr></thead>\n<tbody>')
            for index, item in enumerate(node["elements"]):
                self.body.append(f'<tr><th scope="row">{index + node["start_index"]}</th>')
                self.body.append(html_cell(node, index, item))
                if pointers:
                    self.body.append('<td class="tb-array__pointers">' + markers(index, True) + '</td>')
                self.body.append('</tr>')
            if end_pointers:
                self.body.append(f'<tr><th scope="row">{len(node["elements"]) + node["start_index"]}</th>'
                                 '<td class="tb-array__end">End</td><td class="tb-array__pointers">'
                                 + markers(len(node["elements"]), True) + '</td></tr>')
        else:
            self.body.append('<thead>')
            if pointers:
                self.body.append('<tr class="tb-array__pointers"><td></td>')
                for index in range(len(node["elements"]) + bool(end_pointers)):
                    self.body.append('<td>' + markers(index) + '</td>')
                self.body.append('</tr>')
            self.body.append('<tr><th scope="row">Index</th>')
            for index in range(len(node["elements"])):
                self.body.append(f'<th scope="col">{index + node["start_index"]}</th>')
            if end_pointers:
                self.body.append('<th scope="col">End</th>')
            self.body.append('</tr></thead>\n<tbody><tr><th scope="row">Value</th>')
            for index, item in enumerate(node["elements"]):
                self.body.append(html_cell(node, index, item))
            if end_pointers:
                self.body.append('<td class="tb-array__end">Past the end</td>')
            self.body.append('</tr>')
        self.body.append('</tbody></table></div>\n')
    else:
        if node["caption"]:
            self.body.append(f'<p class="tb-array__caption">{escape(node["caption"])}</p>\n')
        self.body.append('<p>Empty array.</p>\n')
        for pointer in pointers:
            self.body.append(pointer_html(pointer) + '\n')
    if description := range_description(node):
        self.body.append(f'<p class="tb-array__range">{escape(description)}</p>\n')
    self.body.append('</tb-array>\n')
    raise nodes.SkipNode


def static_content(node, *, text=False):
    """Native nodes keep escaping, table wrapping, and PDF tagging in Sphinx."""
    content = nodes.container()
    if node["label"]:
        content += nodes.paragraph(text=node["label"])
    if node["caption"]:
        content += nodes.paragraph(text=node["caption"])
    if not node["elements"]:
        content += nodes.paragraph(text="Empty array.")
    else:
        keyed = node["show_keys"] and node["mode"] == "keyed"
        headings = ["Index"] + (["Key"] if keyed else []) + ["Value", "Notes"]
        rows = []
        for index, item in enumerate(node["elements"]):
            values = [str(index + node["start_index"])] + ([item["key"]] if keyed else [])
            notes = "; ".join(annotations(node, index))
            if text:
                # Sphinx's text table wrapper collapses embedded newlines.
                # Blank index/key fields identify continuation lines.
                lines = item["value"].split("\n")
                rows.append(values + [lines[0], notes])
                rows.extend([""] * len(values) + [line, ""] for line in lines[1:])
            else:
                rows.append(values + [item["value"], notes])
        table = nodes.table()
        group = nodes.tgroup(cols=len(headings))
        for column, heading in enumerate(headings):
            width = max(len(heading), *(min(40, len(row[column])) for row in rows))
            group += nodes.colspec(colwidth=width)
        head = nodes.thead()
        header = nodes.row()
        for heading in headings:
            entry = nodes.entry()
            entry += nodes.paragraph(text=heading)
            header += entry
        head += header
        group += head
        body = nodes.tbody()
        for values in rows:
            row = nodes.row()
            for value in values:
                entry = nodes.entry()
                if "\n" in value:
                    # A table value is text, not a list. DUlineblock's legacy
                    # list environment fails with LaTeX's PDF tagging enabled.
                    paragraph = nodes.paragraph()
                    for line_index, line in enumerate(value.split("\n")):
                        if line_index:
                            paragraph += nodes.raw("", r"\newline{}", format="latex")
                        # Keep leading, trailing, and consecutive empty lines.
                        paragraph += nodes.raw("", r"\strut{}", format="latex")
                        paragraph += nodes.Text(line)
                    entry += paragraph
                else:
                    entry += nodes.paragraph(text=value)
                row += entry
            body += row
        group += body
        table += group
        content += table
    if description := range_description(node):
        content += nodes.paragraph(text=description)
    return content


def visit_tb_array_latex(self, node):
    latex_targets(self, node)
    static_content(node).walkabout(self)
    raise nodes.SkipNode


def visit_tb_array_text(self, node):
    static_content(node, text=True).walkabout(self)
    raise nodes.SkipNode


def depart_tb_array(self, node):
    pass
