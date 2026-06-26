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

from sphinx_touchbook.nodes import (
    TbClickNode,
    TbClickPromptNode,
    TbClickRegionNode,
    TbClickSourceNode,
)


def _node_id(node: TbClickNode) -> str:
    return node["ids"][0]


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
            f'aria-describedby="{feedback_id}" aria-label="Clickable source region">'
            f"{selected}</button>"
        )
        offset = end
    parts.append(escape(source[offset:]))
    return "".join(parts)


def visit_tb_click_html(self: HTML5Translator, node: TbClickNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    hints = escape(node.get("hints", "false"), quote=True)
    self.body.append(f'<tb-click id="{node_id}" hints="{hints}">\n')


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
    language = escape(node.get("language", "none"), quote=True)
    self.body.append(f'<div class="highlight-{language} notranslate tb-click__source">\n')
    self.body.append("<div class=\"highlight\"><pre>")
    self.body.append(_annotated_source_html(node))
    self.body.append("</pre></div>\n")
    self.body.append("</div>\n")
    raise nodes.SkipNode


def depart_tb_click_source_html(self: HTML5Translator, node: TbClickSourceNode) -> None:
    pass


def visit_tb_click_region_html(self: HTML5Translator, node: TbClickRegionNode) -> None:
    feedback_id = escape(f"{_node_id(node.parent)}-feedback-{node['index']}", quote=True)
    correct = "true" if node["correct"] else "false"
    self.body.append(
        f'<div id="{feedback_id}" class="tb-click__feedback" '
        f'data-correct="{correct}" hidden>\n'
    )


def depart_tb_click_region_html(self: HTML5Translator, node: TbClickRegionNode) -> None:
    self.body.append("</div>\n")


def visit_tb_click_latex(self: LaTeXTranslator, node: TbClickNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{Click question}\n")


def depart_tb_click_latex(self: LaTeXTranslator, node: TbClickNode) -> None:
    self.body.append("\n\\end{sphinxadmonition}\n")


def visit_tb_click_prompt_latex(self: LaTeXTranslator, node: TbClickPromptNode) -> None:
    pass


def depart_tb_click_prompt_latex(self: LaTeXTranslator, node: TbClickPromptNode) -> None:
    self.body.append("\n")


def visit_tb_click_source_latex(self: LaTeXTranslator, node: TbClickSourceNode) -> None:
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
    self.add_text(node["source"])
    self.add_text("\n")
    raise nodes.SkipNode


def depart_tb_click_source_text(self: TextTranslator, node: TbClickSourceNode) -> None:
    pass


def visit_tb_click_region_text(self: TextTranslator, node: TbClickRegionNode) -> None:
    raise nodes.SkipNode


def depart_tb_click_region_text(self: TextTranslator, node: TbClickRegionNode) -> None:
    pass
