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
    TbMatchDistractorNode,
    TbMatchNode,
    TbMatchPairNode,
    TbMatchPromptNode,
    TbMatchSourceNode,
    TbMatchTargetNode,
)


def _node_id(node: TbMatchNode) -> str:
    return node["ids"][0]


def _pair_nodes(node: TbMatchNode) -> list[TbMatchPairNode]:
    return [child for child in node.children if isinstance(child, TbMatchPairNode)]


def _distractor_nodes(node: TbMatchNode) -> list[TbMatchDistractorNode]:
    return [child for child in node.children if isinstance(child, TbMatchDistractorNode)]


def _source_text(pair: TbMatchPairNode) -> str:
    source = next(child for child in pair.children if isinstance(child, TbMatchSourceNode))
    return source.astext()


def _source_order(node: TbMatchNode) -> list[TbMatchPairNode]:
    return sorted(_pair_nodes(node), key=lambda pair: (_source_text(pair).casefold(), int(pair["index"])))


def _target_text(pair: TbMatchPairNode) -> str:
    target = next(child for child in pair.children if isinstance(child, TbMatchTargetNode))
    return target.astext()


def _option_values(node: TbMatchNode) -> list[tuple[str, str]]:
    options = [(str(pair["index"]), _target_text(pair)) for pair in _pair_nodes(node)]
    options.extend((f"distractor-{index}", distractor.astext()) for index, distractor in enumerate(_distractor_nodes(node)))
    return sorted(options, key=lambda option: (option[1].casefold(), option[0]))


def _append_children(visitor, parent: nodes.Element) -> None:
    for child in parent.children:
        child.walkabout(visitor)


def visit_tb_match_html(self: HTML5Translator, node: TbMatchNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    self.body.append(f'<tb-match id="{node_id}">\n')


def depart_tb_match_html(self: HTML5Translator, node: TbMatchNode) -> None:
    node_id = _node_id(node)
    options = _option_values(node)
    self.body.append('<div class="tb-match__choices">\n')
    for pair in _source_order(node):
        source = next(child for child in pair.children if isinstance(child, TbMatchSourceNode))
        select_id = escape(f"{node_id}-select-{pair['index']}", quote=True)
        source_id = escape(f"{node_id}-source-{pair['index']}", quote=True)
        self.body.append(f'<div class="tb-match__choice" data-answer="{pair["index"]}">\n')
        self.body.append(f'<label id="{source_id}" class="tb-match__source" for="{select_id}">\n')
        _append_children(self, source)
        self.body.append("</label>\n")
        self.body.append(
            f'<select id="{select_id}" class="tb-match__select" data-answer="{pair["index"]}" '
            f'aria-labelledby="{source_id}">\n'
        )
        self.body.append('<option value="">Choose a definition</option>\n')
        for value, label in options:
            option_value = escape(value, quote=True)
            option_text = escape(label)
            self.body.append(f'<option value="{option_value}">{option_text}</option>\n')
        self.body.append("</select>\n")
        self.body.append("</div>\n")
    self.body.append("</div>\n")
    self.body.append('<div class="tb-match__actions">\n')
    self.body.append('<button type="button" class="tb-match__check" disabled>Check Me</button>\n')
    self.body.append('<p class="tb-match__status" role="status" aria-live="polite"></p>\n')
    self.body.append("</div>\n")
    self.body.append("</tb-match>\n")


def visit_tb_match_prompt_html(self: HTML5Translator, node: TbMatchPromptNode) -> None:
    self.body.append('<div class="tb-match__prompt">\n')


def depart_tb_match_prompt_html(self: HTML5Translator, node: TbMatchPromptNode) -> None:
    self.body.append("</div>\n")


def visit_tb_match_pair_html(self: HTML5Translator, node: TbMatchPairNode) -> None:
    raise nodes.SkipNode


def depart_tb_match_pair_html(self: HTML5Translator, node: TbMatchPairNode) -> None:
    pass


def visit_tb_match_source_html(self: HTML5Translator, node: TbMatchSourceNode) -> None:
    pass


def depart_tb_match_source_html(self: HTML5Translator, node: TbMatchSourceNode) -> None:
    pass


def visit_tb_match_target_html(self: HTML5Translator, node: TbMatchTargetNode) -> None:
    pass


def depart_tb_match_target_html(self: HTML5Translator, node: TbMatchTargetNode) -> None:
    pass


def visit_tb_match_latex(self: LaTeXTranslator, node: TbMatchNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{Matching question}\n")


def depart_tb_match_latex(self: LaTeXTranslator, node: TbMatchNode) -> None:
    self.body.append("\n\\textbf{Sources}\\par\n\\begin{itemize}\n")
    for pair in _source_order(node):
        source = next(child for child in pair.children if isinstance(child, TbMatchSourceNode))
        self.body.append("\\item ")
        self.body.append(self.encode(source.astext()))
        self.body.append("\n")
    self.body.append("\\end{itemize}\n\\textbf{Targets}\\par\n\\begin{enumerate}\n")
    for pair in _pair_nodes(node):
        target = next(child for child in pair.children if isinstance(child, TbMatchTargetNode))
        self.body.append("\\item ")
        self.body.append(self.encode(target.astext()))
        self.body.append("\n")
    for distractor in _distractor_nodes(node):
        self.body.append("\\item ")
        self.body.append(self.encode(distractor.astext()))
        self.body.append("\n")
    self.body.append("\\end{enumerate}\n")
    self.body.append("\n\\end{sphinxadmonition}\n")


def visit_tb_match_prompt_latex(self: LaTeXTranslator, node: TbMatchPromptNode) -> None:
    pass


def depart_tb_match_prompt_latex(self: LaTeXTranslator, node: TbMatchPromptNode) -> None:
    self.body.append("\n")


def visit_tb_match_pair_latex(self: LaTeXTranslator, node: TbMatchPairNode) -> None:
    raise nodes.SkipNode


def depart_tb_match_pair_latex(self: LaTeXTranslator, node: TbMatchPairNode) -> None:
    pass


def visit_tb_match_source_latex(self: LaTeXTranslator, node: TbMatchSourceNode) -> None:
    pass


def depart_tb_match_source_latex(self: LaTeXTranslator, node: TbMatchSourceNode) -> None:
    pass


def visit_tb_match_target_latex(self: LaTeXTranslator, node: TbMatchTargetNode) -> None:
    pass


def depart_tb_match_target_latex(self: LaTeXTranslator, node: TbMatchTargetNode) -> None:
    pass


def visit_tb_match_text(self: TextTranslator, node: TbMatchNode) -> None:
    self.add_text("\n[Matching question]\n")


def depart_tb_match_text(self: TextTranslator, node: TbMatchNode) -> None:
    self.add_text("\nSources:\n")
    for pair in _source_order(node):
        source = next(child for child in pair.children if isinstance(child, TbMatchSourceNode))
        self.add_text(f"- {source.astext()}\n")
    self.add_text("\nTargets:\n")
    targets = [target for _, target in _option_values(node)]
    for index, target in enumerate(targets, start=1):
        self.add_text(f"{index}. {target}\n")
    self.add_text("\n")


def visit_tb_match_prompt_text(self: TextTranslator, node: TbMatchPromptNode) -> None:
    pass


def depart_tb_match_prompt_text(self: TextTranslator, node: TbMatchPromptNode) -> None:
    self.add_text("\n")


def visit_tb_match_pair_text(self: TextTranslator, node: TbMatchPairNode) -> None:
    raise nodes.SkipNode


def depart_tb_match_pair_text(self: TextTranslator, node: TbMatchPairNode) -> None:
    pass


def visit_tb_match_source_text(self: TextTranslator, node: TbMatchSourceNode) -> None:
    pass


def depart_tb_match_source_text(self: TextTranslator, node: TbMatchSourceNode) -> None:
    pass


def visit_tb_match_target_text(self: TextTranslator, node: TbMatchTargetNode) -> None:
    pass


def depart_tb_match_target_text(self: TextTranslator, node: TbMatchTargetNode) -> None:
    pass


def visit_tb_match_distractor_html(self: HTML5Translator, node: TbMatchDistractorNode) -> None:
    raise nodes.SkipNode


def depart_tb_match_distractor_html(self: HTML5Translator, node: TbMatchDistractorNode) -> None:
    pass


def visit_tb_match_distractor_latex(self: LaTeXTranslator, node: TbMatchDistractorNode) -> None:
    raise nodes.SkipNode


def depart_tb_match_distractor_latex(self: LaTeXTranslator, node: TbMatchDistractorNode) -> None:
    pass


def visit_tb_match_distractor_text(self: TextTranslator, node: TbMatchDistractorNode) -> None:
    raise nodes.SkipNode


def depart_tb_match_distractor_text(self: TextTranslator, node: TbMatchDistractorNode) -> None:
    pass
