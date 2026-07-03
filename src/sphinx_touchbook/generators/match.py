"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.

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

from sphinx_touchbook.generators.common import html_class_attr
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


def _letter_label(index: int) -> str:
    label = ""
    current = index
    while True:
        current, remainder = divmod(current, 26)
        label = chr(ord("A") + remainder) + label
        if current == 0:
            return label
        current -= 1


def _latex_cell_text(visitor: LaTeXTranslator, text: str) -> str:
    return visitor.encode(" ".join(text.split()))


def visit_tb_match_html(self: HTML5Translator, node: TbMatchNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    self.body.append(f'<tb-match id="{node_id}"{html_class_attr(node)}>\n')


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
    self.body.append("\n\\subsubsection*{Matching question}\n")


def depart_tb_match_latex(self: LaTeXTranslator, node: TbMatchNode) -> None:
    sources = [
        (_letter_label(index), _source_text(pair))
        for index, pair in enumerate(_source_order(node))
    ]
    targets = [target for _, target in _option_values(node)]
    row_count = max(len(sources), len(targets))

    self.body.append(
        "\n\\noindent\\begin{tabular}{@{}p{0.42\\linewidth}p{0.52\\linewidth}@{}}\n"
    )
    for index in range(row_count):
        if index < len(sources):
            label, source = sources[index]
            source_cell = f"\\textbf{{{label}.}} {_latex_cell_text(self, source)}"
        else:
            source_cell = ""

        if index < len(targets):
            target = _latex_cell_text(self, targets[index])
            target_cell = f"\\underline{{\\hspace{{1.5em}}}} {target}"
        else:
            target_cell = ""

        self.body.append(f"{source_cell} & {target_cell}\\\\[0.45em]\n")
    self.body.append("\\end{tabular}\n")


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
