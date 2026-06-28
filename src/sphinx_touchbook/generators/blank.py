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
import json

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.nodes import TbBlankInputNode, TbBlankNode, TbBlankPromptNode


def _node_id(node: TbBlankNode) -> str:
    return node["ids"][0]


def visit_tb_blank_html(self: HTML5Translator, node: TbBlankNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    case_sensitive = "true" if node["case_sensitive"] else "false"
    trim = "true" if node["trim"] else "false"
    self.body.append(f'<tb-blank id="{node_id}" case-sensitive="{case_sensitive}" trim="{trim}">\n')


def depart_tb_blank_html(self: HTML5Translator, node: TbBlankNode) -> None:
    config = {
        "blanks": node["blanks"],
        "answers": node["answers"],
    }
    data = escape(json.dumps(config), quote=False)
    self.body.append(f'<script type="application/json" class="tb-blank__config">{data}</script>\n')
    self.body.append('<div class="tb-blank__actions">\n')
    self.body.append('<button type="button" class="tb-blank__check">Check answer</button>\n')
    self.body.append('<p class="tb-blank__status" role="status" aria-live="polite"></p>\n')
    self.body.append("</div>\n")
    self.body.append("</tb-blank>\n")


def visit_tb_blank_prompt_html(self: HTML5Translator, node: TbBlankPromptNode) -> None:
    self.body.append('<div class="tb-blank__prompt">\n')


def depart_tb_blank_prompt_html(self: HTML5Translator, node: TbBlankPromptNode) -> None:
    self.body.append("</div>\n")


def visit_tb_blank_input_html(self: HTML5Translator, node: TbBlankInputNode) -> None:
    parent = node.parent
    while parent is not None and not isinstance(parent, TbBlankNode):
        parent = parent.parent
    root_id = _node_id(parent) if parent is not None else "tb-blank"
    blank_id = escape(node["blank_id"], quote=True)
    input_id = escape(f"{root_id}-{blank_id}", quote=True)
    self.body.append(
        f'<input id="{input_id}" class="tb-blank__input" type="text" '
        f'data-blank-id="{blank_id}" aria-label="Blank {int(node["index"]) + 1}">'
    )
    raise nodes.SkipNode


def depart_tb_blank_input_html(self: HTML5Translator, node: TbBlankInputNode) -> None:
    pass


def visit_tb_blank_latex(self: LaTeXTranslator, node: TbBlankNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{Fill in the blank}\n")


def depart_tb_blank_latex(self: LaTeXTranslator, node: TbBlankNode) -> None:
    self.body.append("\n\\end{sphinxadmonition}\n")


def visit_tb_blank_prompt_latex(self: LaTeXTranslator, node: TbBlankPromptNode) -> None:
    pass


def depart_tb_blank_prompt_latex(self: LaTeXTranslator, node: TbBlankPromptNode) -> None:
    pass


def visit_tb_blank_input_latex(self: LaTeXTranslator, node: TbBlankInputNode) -> None:
    self.body.append(r"\underline{\hspace{2cm}}")
    raise nodes.SkipNode


def depart_tb_blank_input_latex(self: LaTeXTranslator, node: TbBlankInputNode) -> None:
    pass


def visit_tb_blank_text(self: TextTranslator, node: TbBlankNode) -> None:
    self.add_text("\n[Fill in the blank]\n")


def depart_tb_blank_text(self: TextTranslator, node: TbBlankNode) -> None:
    self.add_text("\n")


def visit_tb_blank_prompt_text(self: TextTranslator, node: TbBlankPromptNode) -> None:
    pass


def depart_tb_blank_prompt_text(self: TextTranslator, node: TbBlankPromptNode) -> None:
    pass


def visit_tb_blank_input_text(self: TextTranslator, node: TbBlankInputNode) -> None:
    self.add_text("________")
    raise nodes.SkipNode


def depart_tb_blank_input_text(self: TextTranslator, node: TbBlankInputNode) -> None:
    pass
