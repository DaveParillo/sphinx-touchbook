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

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.nodes import TbOrderItemNode, TbOrderNode, TbOrderPromptNode


def _node_id(node: TbOrderNode) -> str:
    return node["ids"][0]


def _item_nodes(node: TbOrderNode) -> list[TbOrderItemNode]:
    return [child for child in node.children if isinstance(child, TbOrderItemNode)]


def _display_order(node: TbOrderNode) -> list[TbOrderItemNode]:
    return sorted(_item_nodes(node), key=lambda item: (item.astext().casefold(), int(item["index"])))


def _append_children(visitor, parent: nodes.Element) -> None:
    for child in parent.children:
        child.walkabout(visitor)


def visit_tb_order_html(self: HTML5Translator, node: TbOrderNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    self.body.append(f'<tb-order id="{node_id}">\n')


def depart_tb_order_html(self: HTML5Translator, node: TbOrderNode) -> None:
    self.body.append('<ol class="tb-order__list" aria-label="Items to order">\n')
    for item in _display_order(node):
        index = int(item["index"])
        self.body.append(f'<li class="tb-order__item" data-order="{index}">\n')
        self.body.append('<div class="tb-order__content">\n')
        _append_children(self, item)
        self.body.append("</div>\n")
        self.body.append('<div class="tb-order__controls" aria-label="Move item">\n')
        self.body.append('<button type="button" class="tb-order__move tb-order__move-up" aria-label="Move item up">↑</button>\n')
        self.body.append('<button type="button" class="tb-order__move tb-order__move-down" aria-label="Move item down">↓</button>\n')
        self.body.append("</div>\n")
        self.body.append("</li>\n")
    self.body.append("</ol>\n")
    self.body.append('<div class="tb-order__actions">\n')
    self.body.append('<button type="button" class="tb-order__check">Check order</button>\n')
    self.body.append('<p class="tb-order__status" role="status" aria-live="polite"></p>\n')
    self.body.append("</div>\n")
    self.body.append("</tb-order>\n")


def visit_tb_order_item_html(self: HTML5Translator, node: TbOrderItemNode) -> None:
    raise nodes.SkipNode


def depart_tb_order_item_html(self: HTML5Translator, node: TbOrderItemNode) -> None:
    pass


def visit_tb_order_prompt_html(self: HTML5Translator, node: TbOrderPromptNode) -> None:
    self.body.append('<div class="tb-order__prompt">\n')


def depart_tb_order_prompt_html(self: HTML5Translator, node: TbOrderPromptNode) -> None:
    self.body.append("</div>\n")


def visit_tb_order_latex(self: LaTeXTranslator, node: TbOrderNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{Ordering question}\n")


def depart_tb_order_latex(self: LaTeXTranslator, node: TbOrderNode) -> None:
    self.body.append("\n\\textbf{Items}\\par\n\\begin{itemize}\n")
    for item in _display_order(node):
        self.body.append("\\item ")
        self.body.append(self.encode(item.astext()))
        self.body.append("\n")
    self.body.append("\\end{itemize}\n\\end{sphinxadmonition}\n")


def visit_tb_order_item_latex(self: LaTeXTranslator, node: TbOrderItemNode) -> None:
    raise nodes.SkipNode


def depart_tb_order_item_latex(self: LaTeXTranslator, node: TbOrderItemNode) -> None:
    pass


def visit_tb_order_prompt_latex(self: LaTeXTranslator, node: TbOrderPromptNode) -> None:
    pass


def depart_tb_order_prompt_latex(self: LaTeXTranslator, node: TbOrderPromptNode) -> None:
    self.body.append("\n")


def visit_tb_order_text(self: TextTranslator, node: TbOrderNode) -> None:
    self.add_text("\n[Ordering question]\n")


def depart_tb_order_text(self: TextTranslator, node: TbOrderNode) -> None:
    self.add_text("\nItems:\n")
    for item in _display_order(node):
        self.add_text(f"- {item.astext()}\n")
    self.add_text("\n")


def visit_tb_order_item_text(self: TextTranslator, node: TbOrderItemNode) -> None:
    raise nodes.SkipNode


def depart_tb_order_item_text(self: TextTranslator, node: TbOrderItemNode) -> None:
    pass


def visit_tb_order_prompt_text(self: TextTranslator, node: TbOrderPromptNode) -> None:
    pass


def depart_tb_order_prompt_text(self: TextTranslator, node: TbOrderPromptNode) -> None:
    self.add_text("\n")
