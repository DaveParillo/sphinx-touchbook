"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

from html import escape
from urllib.parse import urlsplit
from xml.etree import ElementTree

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.generators.common import html_additional_targets, html_class_attr, latex_targets
from sphinx_touchbook.nodes import (
    TbClickNode,
    TbClickPromptNode,
    TbClickRegionNode,
    TbClickSourceNode,
)


def _node_id(node: TbClickNode) -> str:
    return node["ids"][0]


def keyed_target_attributes(node, key, value):
    """Connect a rendered keyed object to its question's semantic region."""
    region = node.get("click_regions", {}).get(key)
    if region is None:
        return {}
    feedback_id = f"{node['click_question_id']}-feedback-{region['index']}"
    return {
        "class": "tb-click__target",
        "data-key": key,
        "data-correct": "true" if region["correct"] else "false",
        "data-feedback-id": feedback_id,
        "aria-label": f"{key}: {value or 'Empty value'}",
        "aria-pressed": "false",
    }


def keyed_target_html(node, key, value):
    attributes = keyed_target_attributes(node, key, value)
    if not attributes:
        return escape(value)
    attrs = " ".join(f'{name}="{escape(value, quote=True)}"' for name, value in attributes.items())
    return f'<button type="button" {attrs}>{escape(value) or "&#8203;"}</button>'


def keyed_graph_svg(node, filename):
    """Make Graphviz's generated link regions accessible question controls."""
    root = ElementTree.parse(filename).getroot()
    svg_ns = "http://www.w3.org/2000/svg"
    href = "{http://www.w3.org/1999/xlink}href"
    items = {item["key"]: item for item in node["nodes"]}
    regions = {f"tb-click-region-{region['index']}": key
               for key, region in node["click_regions"].items()}
    root.set("class", "tb-graph__diagram tb-click__diagram")
    root.set("role", "group")
    root.set("aria-label", node.get("alt", node["label"] or node["caption"] or "Graph diagram"))
    for element in root.iter():
        # Graphviz titles expose renderer IDs such as n0, not author content.
        for title in element.findall(f"{{{svg_ns}}}title"):
            element.remove(title)
        if "id" in element.attrib:
            element.set("id", f"{node['ids'][0]}-{element.get('id')}")
        if element.tag == f"{{{svg_ns}}}a":
            key = regions[urlsplit(element.attrib.pop(href, "")).fragment]
            element.attrib.clear()
            element.tag = f"{{{svg_ns}}}g"
            element.attrib.update(keyed_target_attributes(node, key, items[key]["value"]))
            element.set("role", "button")
            element.set("tabindex", "0")
    # Register the default namespace so the inline SVG also parses as HTML.
    ElementTree.register_namespace("", svg_ns)
    return ElementTree.tostring(root, encoding="unicode")


def _annotated_source_html(node: TbClickSourceNode) -> str:
    source = node["source"]
    regions = sorted(node.parent["regions"], key=lambda region: region["start"])
    parts = []
    offset = 0
    for region in regions:
        start = int(region["start"])
        end = int(region["end"])
        parts.append(escape(source[offset:start]))
        selected = escape(source[start:end])
        correct = "true" if region["correct"] else "false"
        feedback_id = escape(f"{_node_id(node.parent)}-feedback-{region['index']}", quote=True)
        parts.append(
            '<button type="button" class="tb-click__target" '
            f'data-correct="{correct}" data-feedback-id="{feedback_id}" '
            'aria-label="Clickable source region">'
            f"{selected}</button>"
        )
        offset = end
    parts.append(escape(source[offset:]))
    return "".join(parts)


def visit_tb_click_html(self: HTML5Translator, node: TbClickNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    hints = escape(node.get("hints", "false"), quote=True)
    self.body.append(html_additional_targets(node))
    self.body.append(f'<tb-click id="{node_id}"{html_class_attr(node)} hints="{hints}">\n')


def depart_tb_click_html(self: HTML5Translator, node: TbClickNode) -> None:
    if node.get("hints") != "never":
        self.body.append(
            '<button type="button" class="tb-click__hint-toggle">'
            "Show Hints</button>\n"
        )
    self.body.append('<p class="tb-click__status" role="status" aria-live="polite"></p>\n')
    self.body.append("</tb-click>\n")


def visit_tb_click_prompt_html(self: HTML5Translator, node: TbClickPromptNode) -> None:
    self.body.append('<div class="tb-click__prompt">\n')


def depart_tb_click_prompt_html(self: HTML5Translator, node: TbClickPromptNode) -> None:
    self.body.append("</div>\n")


def visit_tb_click_source_html(self: HTML5Translator, node: TbClickSourceNode) -> None:
    if node.get("kind", "text") != "text":
        self.body.append('<div class="tb-click__source">\n')
        return
    language = escape(node.get("language", "none"), quote=True)
    self.body.append(f'<div class="highlight-{language} notranslate tb-click__source">\n')
    self.body.append("<div class=\"highlight\"><pre>")
    self.body.append(_annotated_source_html(node))
    self.body.append("</pre></div>\n")
    self.body.append("</div>\n")
    raise nodes.SkipNode


def depart_tb_click_source_html(self: HTML5Translator, node: TbClickSourceNode) -> None:
    if node.get("kind", "text") != "text":
        self.body.append('</div>\n')


def visit_tb_click_region_html(self: HTML5Translator, node: TbClickRegionNode) -> None:
    feedback_id = escape(f"{_node_id(node.parent)}-feedback-{node['index']}", quote=True)
    correct = "true" if node["correct"] else "false"
    classes = "tb-click__feedback"
    if node.get("classes"):
        classes += " " + " ".join(escape(name, quote=True) for name in node["classes"])
    self.body.append(
        f'<div id="{feedback_id}" class="{classes}" '
        f'data-correct="{correct}" hidden>\n'
    )


def depart_tb_click_region_html(self: HTML5Translator, node: TbClickRegionNode) -> None:
    self.body.append("</div>\n")


def visit_tb_click_latex(self: LaTeXTranslator, node: TbClickNode) -> None:
    latex_targets(self, node)
    self.body.append("\n\\subsubsection*{Click question}\n")


def depart_tb_click_latex(self: LaTeXTranslator, node: TbClickNode) -> None:
    self.body.append("\n")


def visit_tb_click_prompt_latex(self: LaTeXTranslator, node: TbClickPromptNode) -> None:
    pass


def depart_tb_click_prompt_latex(self: LaTeXTranslator, node: TbClickPromptNode) -> None:
    self.body.append("\n")


def visit_tb_click_source_latex(self: LaTeXTranslator, node: TbClickSourceNode) -> None:
    if node.get("kind", "text") != "text":
        return
    if self.config.tb_pdf_tagging:
        from .common import tagged_listing
        tagged_listing(self, node['source'], 'text', '', location=node)
        raise nodes.SkipNode
    self.body.append("\n\\begin{sphinxVerbatim}\n")
    self.body.append(node["source"])
    self.body.append("\n\\end{sphinxVerbatim}\n")
    raise nodes.SkipNode


def depart_tb_click_source_latex(self: LaTeXTranslator, node: TbClickSourceNode) -> None:
    pass


def visit_tb_click_region_latex(self: LaTeXTranslator, node: TbClickRegionNode) -> None:
    raise nodes.SkipNode


def depart_tb_click_region_latex(self: LaTeXTranslator, node: TbClickRegionNode) -> None:
    pass


def visit_tb_click_text(self: TextTranslator, node: TbClickNode) -> None:
    self.add_text("\n[Click question]\n")


def depart_tb_click_text(self: TextTranslator, node: TbClickNode) -> None:
    self.add_text("\n")


def visit_tb_click_prompt_text(self: TextTranslator, node: TbClickPromptNode) -> None:
    pass


def depart_tb_click_prompt_text(self: TextTranslator, node: TbClickPromptNode) -> None:
    self.add_text("\n")


def visit_tb_click_source_text(self: TextTranslator, node: TbClickSourceNode) -> None:
    if node.get("kind", "text") != "text":
        return
    self.add_text(node["source"])
    self.add_text("\n")
    raise nodes.SkipNode


def depart_tb_click_source_text(self: TextTranslator, node: TbClickSourceNode) -> None:
    pass


def visit_tb_click_region_text(self: TextTranslator, node: TbClickRegionNode) -> None:
    raise nodes.SkipNode


def depart_tb_click_region_text(self: TextTranslator, node: TbClickRegionNode) -> None:
    pass
