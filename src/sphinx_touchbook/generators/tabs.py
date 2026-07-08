"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

from html import escape

"""Builder generators for tab groups."""

from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.generators.common import html_additional_targets, html_class_attr, latex_targets
from sphinx_touchbook.nodes import TbGroupNode, TbTabNode


def _node_id(node) -> str:
    return node["ids"][0]


def visit_tb_group_html(self: HTML5Translator, node: TbGroupNode) -> None:
    self.body.append(html_additional_targets(node))
    self.body.append(f'<tb-group id="{escape(_node_id(node), quote=True)}"{html_class_attr(node)}>\n')
    self.body.append('<div class="tb-group__fallback">\n')


def depart_tb_group_html(self: HTML5Translator, node: TbGroupNode) -> None:
    self.body.append("</div>\n")
    self.body.append("</tb-group>\n")


def visit_tb_tab_html(self: HTML5Translator, node: TbTabNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    label = escape(node["label"], quote=True)
    label_text = escape(node["label"])
    self.body.append(html_additional_targets(node))
    self.body.append(f'<tb-tab id="{node_id}"{html_class_attr(node)} label="{label}">\n')
    self.body.append('<section class="tb-tab__fallback">\n')
    self.body.append(f'<p class="tb-tab__label"><strong>{label_text}</strong></p>\n')
    self.body.append('<div class="tb-tab__content">\n')


def depart_tb_tab_html(self: HTML5Translator, node: TbTabNode) -> None:
    self.body.append("</div>\n")
    self.body.append("</section>\n")
    self.body.append("</tb-tab>\n")


def visit_tb_group_latex(self: LaTeXTranslator, node: TbGroupNode) -> None:
    latex_targets(self, node)
    self.body.append("\n")


def depart_tb_group_latex(self: LaTeXTranslator, node: TbGroupNode) -> None:
    self.body.append("\n")


def visit_tb_tab_latex(self: LaTeXTranslator, node: TbTabNode) -> None:
    latex_targets(self, node)
    self.body.append("\n\\subsubsection*{")
    self.body.append(self.encode(node["label"]))
    self.body.append("}\n")


def depart_tb_tab_latex(self: LaTeXTranslator, node: TbTabNode) -> None:
    self.body.append("\n")


def visit_tb_group_text(self: TextTranslator, node: TbGroupNode) -> None:
    self.add_text(f"\n[{_node_id(node)}]\n")


def depart_tb_group_text(self: TextTranslator, node: TbGroupNode) -> None:
    self.add_text("\n")


def visit_tb_tab_text(self: TextTranslator, node: TbTabNode) -> None:
    self.add_text(f"\n{node['label']}\n")
    self.add_text("-" * len(node["label"]))
    self.add_text("\n")


def depart_tb_tab_text(self: TextTranslator, node: TbTabNode) -> None:
    self.add_text("\n")
