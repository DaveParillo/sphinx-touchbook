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

Builder visitors for calculated formula assessments.
"""

from __future__ import annotations

import json
from html import escape

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.nodes import TbFormulaNode, TbFormulaPromptNode, TbFormulaVariableNode


def _node_id(node: TbFormulaNode) -> str:
    return node["ids"][0]


def visit_tb_formula_html(self: HTML5Translator, node: TbFormulaNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    endpoint = escape(str(self.config.tb_formula_default_endpoint), quote=True)
    self.body.append(f'<tb-formula id="{node_id}" data-endpoint="{endpoint}">\n')


def depart_tb_formula_html(self: HTML5Translator, node: TbFormulaNode) -> None:
    config = {
        "variables": node["variables"],
        "formula": node["formula"],
        "tolerance": node["tolerance"],
    }
    data = json.dumps(config).replace("</", "<\\/")
    self.body.append(f'<script type="application/json" class="tb-formula__config">{data}</script>\n')
    self.body.append('<div class="tb-formula__answer">\n')
    self.body.append('<label class="tb-formula__label">Answer ')
    self.body.append('<input class="tb-formula__input" type="text" inputmode="decimal">')
    self.body.append("</label>\n")
    self.body.append("</div>\n")
    self.body.append('<div class="tb-formula__actions">\n')
    self.body.append('<button type="button" class="tb-formula__check">Check answer</button>\n')
    self.body.append('<button type="button" class="tb-formula__new-values">New values</button>\n')
    self.body.append('<p class="tb-formula__status" role="status" aria-live="polite"></p>\n')
    self.body.append("</div>\n")
    self.body.append("</tb-formula>\n")


def visit_tb_formula_prompt_html(self: HTML5Translator, node: TbFormulaPromptNode) -> None:
    self.body.append('<div class="tb-formula__prompt">\n')


def depart_tb_formula_prompt_html(self: HTML5Translator, node: TbFormulaPromptNode) -> None:
    self.body.append("</div>\n")


def visit_tb_formula_variable_html(self: HTML5Translator, node: TbFormulaVariableNode) -> None:
    name = escape(node["name"], quote=True)
    self.body.append(f'<span class="tb-formula__variable" data-variable="{name}">{{{{{name}}}}}</span>')
    raise nodes.SkipNode


def depart_tb_formula_variable_html(self: HTML5Translator, node: TbFormulaVariableNode) -> None:
    pass


def visit_tb_formula_latex(self: LaTeXTranslator, node: TbFormulaNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{Calculated formula}\n")


def depart_tb_formula_latex(self: LaTeXTranslator, node: TbFormulaNode) -> None:
    self.body.append("\n\\underline{\\hspace{2cm}}\n\\end{sphinxadmonition}\n")


def visit_tb_formula_prompt_latex(self: LaTeXTranslator, node: TbFormulaPromptNode) -> None:
    pass


def depart_tb_formula_prompt_latex(self: LaTeXTranslator, node: TbFormulaPromptNode) -> None:
    pass


def visit_tb_formula_variable_latex(self: LaTeXTranslator, node: TbFormulaVariableNode) -> None:
    self.body.append(r"\underline{\hspace{1cm}}")
    raise nodes.SkipNode


def depart_tb_formula_variable_latex(self: LaTeXTranslator, node: TbFormulaVariableNode) -> None:
    pass


def visit_tb_formula_text(self: TextTranslator, node: TbFormulaNode) -> None:
    self.add_text("\n[Calculated formula]\n")


def depart_tb_formula_text(self: TextTranslator, node: TbFormulaNode) -> None:
    self.add_text("\nAnswer: ________\n")


def visit_tb_formula_prompt_text(self: TextTranslator, node: TbFormulaPromptNode) -> None:
    pass


def depart_tb_formula_prompt_text(self: TextTranslator, node: TbFormulaPromptNode) -> None:
    pass


def visit_tb_formula_variable_text(self: TextTranslator, node: TbFormulaVariableNode) -> None:
    self.add_text("____")
    raise nodes.SkipNode


def depart_tb_formula_variable_text(self: TextTranslator, node: TbFormulaVariableNode) -> None:
    pass
