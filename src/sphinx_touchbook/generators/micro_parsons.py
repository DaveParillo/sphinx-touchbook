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

Builder visitors for token-level Parsons problems.
"""

from __future__ import annotations

from html import escape

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.nodes import (
    TbMicroParsonsNode,
    TbMicroParsonsPromptNode,
    TbMicroParsonsTokenNode,
)


def _node_id(node: TbMicroParsonsNode) -> str:
    return node["ids"][0]


def _token_nodes(node: TbMicroParsonsNode) -> list[TbMicroParsonsTokenNode]:
    return [child for child in node.children if isinstance(child, TbMicroParsonsTokenNode)]


def _display_order(node: TbMicroParsonsNode) -> list[TbMicroParsonsTokenNode]:
    return sorted(_token_nodes(node), key=lambda token: (token["label"].casefold(), int(token["index"])))


def visit_tb_micro_parsons_html(self: HTML5Translator, node: TbMicroParsonsNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    has_distractors = "true" if node["has_distractors"] else "false"
    self.body.append(f'<tb-micro-parsons id="{node_id}" data-has-distractors="{has_distractors}">\n')


def depart_tb_micro_parsons_html(self: HTML5Translator, node: TbMicroParsonsNode) -> None:
    self.body.append('<div class="tb-micro-parsons__workspace">\n')
    self.body.append('<div class="tb-micro-parsons__row">\n')
    self.body.append('<p class="tb-micro-parsons__row-label">Tokens</p>\n')
    self.body.append('<ol class="tb-micro-parsons__tokens tb-micro-parsons__source" aria-label="Available tokens">\n')
    for token in _display_order(node):
        index = int(token["index"])
        distractor = "true" if token["distractor"] else "false"
        label = escape(token["label"], quote=True)
        self.body.append(
            '<li class="tb-micro-parsons__token" '
            f'data-order="{index}" data-distractor="{distractor}" data-location="source">\n'
        )
        self.body.append(
            '<button type="button" class="tb-micro-parsons__token-button" '
            f'aria-label="Move {label} to answer">\n'
        )
        self.body.append('<code class="tb-micro-parsons__content">')
        self.body.append(escape(token.astext()))
        self.body.append("</code>\n")
        self.body.append("</button>\n")
        self.body.append("</li>\n")
    self.body.append("</ol>\n")
    self.body.append("</div>\n")
    self.body.append('<div class="tb-micro-parsons__row">\n')
    self.body.append('<p class="tb-micro-parsons__row-label">Answer</p>\n')
    self.body.append('<ol class="tb-micro-parsons__tokens tb-micro-parsons__target" aria-label="Answer tokens"></ol>\n')
    self.body.append("</div>\n")
    self.body.append("</div>\n")
    self.body.append('<div class="tb-micro-parsons__actions">\n')
    self.body.append('<button type="button" class="tb-micro-parsons__check">Check answer</button>\n')
    self.body.append('<p class="tb-micro-parsons__status" role="status" aria-live="polite"></p>\n')
    self.body.append("</div>\n")
    self.body.append("</tb-micro-parsons>\n")


def visit_tb_micro_parsons_token_html(self: HTML5Translator, node: TbMicroParsonsTokenNode) -> None:
    raise nodes.SkipNode


def depart_tb_micro_parsons_token_html(self: HTML5Translator, node: TbMicroParsonsTokenNode) -> None:
    pass


def visit_tb_micro_parsons_prompt_html(self: HTML5Translator, node: TbMicroParsonsPromptNode) -> None:
    self.body.append('<div class="tb-micro-parsons__prompt">\n')


def depart_tb_micro_parsons_prompt_html(self: HTML5Translator, node: TbMicroParsonsPromptNode) -> None:
    self.body.append("</div>\n")


def visit_tb_micro_parsons_latex(self: LaTeXTranslator, node: TbMicroParsonsNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{Micro Parsons problem}\n")


def depart_tb_micro_parsons_latex(self: LaTeXTranslator, node: TbMicroParsonsNode) -> None:
    self.body.append("\n\\textbf{Tokens}\\par\n\\begin{itemize}\n")
    for token in _display_order(node):
        self.body.append("\\item ")
        self.body.append(self.encode(token.astext()))
        self.body.append("\n")
    self.body.append("\\end{itemize}\n\\textbf{Answer:} \\underline{\\hspace{6cm}}\n")
    self.body.append("\\end{sphinxadmonition}\n")


def visit_tb_micro_parsons_token_latex(self: LaTeXTranslator, node: TbMicroParsonsTokenNode) -> None:
    raise nodes.SkipNode


def depart_tb_micro_parsons_token_latex(self: LaTeXTranslator, node: TbMicroParsonsTokenNode) -> None:
    pass


def visit_tb_micro_parsons_prompt_latex(self: LaTeXTranslator, node: TbMicroParsonsPromptNode) -> None:
    pass


def depart_tb_micro_parsons_prompt_latex(self: LaTeXTranslator, node: TbMicroParsonsPromptNode) -> None:
    self.body.append("\n")


def visit_tb_micro_parsons_text(self: TextTranslator, node: TbMicroParsonsNode) -> None:
    self.add_text("\n[Micro Parsons problem]\n")


def depart_tb_micro_parsons_text(self: TextTranslator, node: TbMicroParsonsNode) -> None:
    self.add_text("\nTokens:\n")
    for token in _display_order(node):
        self.add_text(f"- {token.astext()}\n")
    self.add_text("\nAnswer: ________________________________\n")


def visit_tb_micro_parsons_token_text(self: TextTranslator, node: TbMicroParsonsTokenNode) -> None:
    raise nodes.SkipNode


def depart_tb_micro_parsons_token_text(self: TextTranslator, node: TbMicroParsonsTokenNode) -> None:
    pass


def visit_tb_micro_parsons_prompt_text(self: TextTranslator, node: TbMicroParsonsPromptNode) -> None:
    pass


def depart_tb_micro_parsons_prompt_text(self: TextTranslator, node: TbMicroParsonsPromptNode) -> None:
    self.add_text("\n")
