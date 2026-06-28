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

Builder visitors for Parsons problems.
"""

from __future__ import annotations

from html import escape

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.nodes import TbParsonsItemNode, TbParsonsNode, TbParsonsPromptNode


def _node_id(node: TbParsonsNode) -> str:
    return node["ids"][0]


def _item_nodes(node: TbParsonsNode) -> list[TbParsonsItemNode]:
    return [child for child in node.children if isinstance(child, TbParsonsItemNode)]


def _display_order(node: TbParsonsNode) -> list[TbParsonsItemNode]:
    return sorted(_item_nodes(node), key=lambda item: (item["code"].casefold(), int(item["index"])))


def visit_tb_parsons_html(self: HTML5Translator, node: TbParsonsNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    no_indent = "true" if node["no_indent"] else "false"
    language = escape(node.get("language", ""), quote=True)
    self.body.append(f'<tb-parsons id="{node_id}" data-no-indent="{no_indent}" data-language="{language}">\n')


def depart_tb_parsons_html(self: HTML5Translator, node: TbParsonsNode) -> None:
    self.body.append('<ol class="tb-parsons__list" aria-label="Code fragments">\n')
    for item in _display_order(node):
        index = int(item["index"])
        indent = int(item["indent"])
        distractor = "true" if item["distractor"] else "false"
        code = escape(item["code"])
        self.body.append(
            '<li class="tb-parsons__item" '
            f'data-order="{index}" data-indent="{indent}" '
            f'data-current-indent="0" data-distractor="{distractor}">\n'
        )
        self.body.append('<pre class="tb-parsons__code"><code>')
        self.body.append(code)
        self.body.append("</code></pre>\n")
        self.body.append('<div class="tb-parsons__controls" aria-label="Arrange fragment">\n')
        self.body.append(
            '<button type="button" class="tb-parsons__move tb-parsons__move-up" '
            'aria-label="Move fragment up">↑</button>\n'
        )
        self.body.append(
            '<button type="button" class="tb-parsons__move tb-parsons__move-down" '
            'aria-label="Move fragment down">↓</button>\n'
        )
        self.body.append(
            '<button type="button" class="tb-parsons__indent tb-parsons__outdent" '
            'aria-label="Outdent fragment">←</button>\n'
        )
        self.body.append(
            '<button type="button" class="tb-parsons__indent tb-parsons__indent-in" '
            'aria-label="Indent fragment">→</button>\n'
        )
        self.body.append(
            '<button type="button" class="tb-parsons__toggle" '
            'aria-pressed="true" aria-label="Included in solution">'
            '<span class="tb-parsons__toggle-icon" aria-hidden="true">✓</span> '
            '<span class="tb-parsons__toggle-label">Use</span></button>\n'
        )
        self.body.append("</div>\n")
        self.body.append("</li>\n")
    self.body.append("</ol>\n")
    self.body.append('<div class="tb-parsons__actions">\n')
    self.body.append('<button type="button" class="tb-parsons__check">Check answer</button>\n')
    self.body.append('<p class="tb-parsons__status" role="status" aria-live="polite"></p>\n')
    self.body.append("</div>\n")
    self.body.append("</tb-parsons>\n")


def visit_tb_parsons_item_html(self: HTML5Translator, node: TbParsonsItemNode) -> None:
    raise nodes.SkipNode


def depart_tb_parsons_item_html(self: HTML5Translator, node: TbParsonsItemNode) -> None:
    pass


def visit_tb_parsons_prompt_html(self: HTML5Translator, node: TbParsonsPromptNode) -> None:
    self.body.append('<div class="tb-parsons__prompt">\n')


def depart_tb_parsons_prompt_html(self: HTML5Translator, node: TbParsonsPromptNode) -> None:
    self.body.append("</div>\n")


def visit_tb_parsons_latex(self: LaTeXTranslator, node: TbParsonsNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{Parsons problem}\n")


def depart_tb_parsons_latex(self: LaTeXTranslator, node: TbParsonsNode) -> None:
    self.body.append("\n\\textbf{Code fragments}\\par\n\\begin{itemize}\n")
    for item in _display_order(node):
        self.body.append("\\item \\sphinxcode{")
        self.body.append(self.encode(item["code"]))
        self.body.append("}\n")
    self.body.append("\\end{itemize}\n\\end{sphinxadmonition}\n")


def visit_tb_parsons_item_latex(self: LaTeXTranslator, node: TbParsonsItemNode) -> None:
    raise nodes.SkipNode


def depart_tb_parsons_item_latex(self: LaTeXTranslator, node: TbParsonsItemNode) -> None:
    pass


def visit_tb_parsons_prompt_latex(self: LaTeXTranslator, node: TbParsonsPromptNode) -> None:
    pass


def depart_tb_parsons_prompt_latex(self: LaTeXTranslator, node: TbParsonsPromptNode) -> None:
    self.body.append("\n")


def visit_tb_parsons_text(self: TextTranslator, node: TbParsonsNode) -> None:
    self.add_text("\n[Parsons problem]\n")


def depart_tb_parsons_text(self: TextTranslator, node: TbParsonsNode) -> None:
    self.add_text("\nCode fragments:\n")
    for item in _display_order(node):
        self.add_text(f"- {item['code']}\n")
    self.add_text("\n")


def visit_tb_parsons_item_text(self: TextTranslator, node: TbParsonsItemNode) -> None:
    raise nodes.SkipNode


def depart_tb_parsons_item_text(self: TextTranslator, node: TbParsonsItemNode) -> None:
    pass


def visit_tb_parsons_prompt_text(self: TextTranslator, node: TbParsonsPromptNode) -> None:
    pass


def depart_tb_parsons_prompt_text(self: TextTranslator, node: TbParsonsPromptNode) -> None:
    self.add_text("\n")
