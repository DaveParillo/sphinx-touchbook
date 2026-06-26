"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
Copyright (C) 2026 Dave Parillo.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
---

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

from sphinx_touchbook.nodes import TbGroupNode, TbTabNode


def _node_id(node) -> str:
    return node["ids"][0]


def visit_tb_group_html(self: HTML5Translator, node: TbGroupNode) -> None:
    self.body.append(f'<tb-group id="{escape(_node_id(node), quote=True)}">\n')
    self.body.append('<div class="tb-group__fallback">\n')


def depart_tb_group_html(self: HTML5Translator, node: TbGroupNode) -> None:
    self.body.append("</div>\n")
    self.body.append("</tb-group>\n")


def visit_tb_tab_html(self: HTML5Translator, node: TbTabNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    label = escape(node["label"], quote=True)
    label_text = escape(node["label"])
    self.body.append(f'<tb-tab id="{node_id}" label="{label}">\n')
    self.body.append('<section class="tb-tab__fallback">\n')
    self.body.append(f'<p class="tb-tab__label"><strong>{label_text}</strong></p>\n')
    self.body.append('<div class="tb-tab__content">\n')


def depart_tb_tab_html(self: HTML5Translator, node: TbTabNode) -> None:
    self.body.append("</div>\n")
    self.body.append("</section>\n")
    self.body.append("</tb-tab>\n")


def visit_tb_group_latex(self: LaTeXTranslator, node: TbGroupNode) -> None:
    self.body.append("\n")


def depart_tb_group_latex(self: LaTeXTranslator, node: TbGroupNode) -> None:
    self.body.append("\n")


def visit_tb_tab_latex(self: LaTeXTranslator, node: TbTabNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{")
    self.body.append(self.encode(node["label"]))
    self.body.append("}\n")


def depart_tb_tab_latex(self: LaTeXTranslator, node: TbTabNode) -> None:
    self.body.append("\n\\end{sphinxadmonition}\n")


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
