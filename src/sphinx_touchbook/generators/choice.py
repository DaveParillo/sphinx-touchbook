"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

from html import escape

"""Builder generators for ``tb-choice``."""

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.generators.common import html_additional_targets, html_class_attr, latex_targets
from sphinx_touchbook.nodes import (
    TbChoiceAnswerNode,
    TbChoiceFeedbackNode,
    TbChoiceNode,
    TbChoiceOptionNode,
    TbChoicePromptNode,
)


def _node_id(node) -> str:
    return node["ids"][0]


def _choice_text_marker(node: TbChoiceOptionNode) -> str:
    return "☐" if node.parent["multiple"] else "○"


def _choice_latex_marker(node: TbChoiceOptionNode) -> str:
    return r"$\square$" if node.parent["multiple"] else r"$\bigcirc$"


def visit_tb_choice_html(self: HTML5Translator, node: TbChoiceNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    mode = "multiple" if node["multiple"] else "single"
    random_attr = ' random="true"' if node.get("random") else ""
    self.body.append(html_additional_targets(node))
    self.body.append(f'<tb-choice id="{node_id}"{html_class_attr(node)} mode="{mode}"{random_attr}>\n')


def depart_tb_choice_html(self: HTML5Translator, node: TbChoiceNode) -> None:
    self.body.append("</div>\n")
    self.body.append('<div class="tb-choice__actions">\n')
    self.body.append('<button type="button" class="tb-choice__check">Check answer</button>\n')
    self.body.append('<p class="tb-choice__status" role="status" aria-live="polite"></p>\n')
    self.body.append("</div>\n")
    self.body.append("</tb-choice>\n")


def visit_tb_choice_prompt_html(self: HTML5Translator, node: TbChoicePromptNode) -> None:
    parent = node.parent
    prompt_id = escape(f"{_node_id(parent)}-prompt", quote=True)
    self.body.append(f'<div id="{prompt_id}" class="tb-choice__prompt">\n')


def depart_tb_choice_prompt_html(self: HTML5Translator, node: TbChoicePromptNode) -> None:
    self.body.append("</div>\n")
    parent = node.parent
    prompt_id = escape(f"{_node_id(parent)}-prompt", quote=True)
    self.body.append(f'<div class="tb-choice__options" role="group" aria-labelledby="{prompt_id}">\n')


def visit_tb_choice_option_html(self: HTML5Translator, node: TbChoiceOptionNode) -> None:
    parent = node.parent
    index = int(node["index"])
    input_id = escape(f"{_node_id(parent)}-option-{index}", quote=True)
    input_type = "checkbox" if parent["multiple"] else "radio"
    name = escape(f"{_node_id(parent)}-answer", quote=True)
    correct = "true" if node["correct"] else "false"

    self.body.append(f'<div class="tb-choice__option" data-correct="{correct}">\n')
    answer = next(child for child in node if isinstance(child, TbChoiceAnswerNode))
    has_intro = isinstance(answer[0], nodes.paragraph)
    has_details = len(answer) > 1 or not has_intro
    describedby = f' aria-describedby="{input_id}-details"' if has_details else ""
    self.body.append('<div class="tb-choice__row">\n')
    self.body.append(
        f'<input id="{input_id}" class="tb-choice__input" type="{input_type}" '
        f'name="{name}" value="{index}"{describedby}>\n'
    )
    self.body.append('<div class="tb-choice__answer">\n')


def depart_tb_choice_option_html(self: HTML5Translator, node: TbChoiceOptionNode) -> None:
    self.body.append("</div>\n")


def visit_tb_choice_answer_html(self: HTML5Translator, node: TbChoiceAnswerNode) -> None:
    option = node.parent
    input_id = escape(f"{_node_id(option.parent)}-option-{int(option['index'])}", quote=True)
    children = list(node.children)
    if isinstance(children[0], nodes.paragraph):
        paragraph = children.pop(0)
        self.body.append(self.starttag(paragraph, "p", ""))
        self.body.append(f'<label class="tb-choice__label" for="{input_id}">')
        for child in paragraph.children:
            child.walkabout(self)
        self.body.append("</label></p>\n")
    else:
        # Nested-list answers may start with a block rather than a paragraph.
        self.body.append(f'<p><label class="tb-choice__label" for="{input_id}">'
                         f'Option {int(option["index"]) + 1}</label></p>\n')
    if children:
        self.body.append(f'<div id="{input_id}-details" class="tb-choice__details">\n')
        for child in children:
            child.walkabout(self)
        self.body.append("</div>\n")
    self.body.append("</div>\n</div>\n")
    raise nodes.SkipNode


def depart_tb_choice_answer_html(self: HTML5Translator, node: TbChoiceAnswerNode) -> None:
    pass


def visit_tb_choice_feedback_html(self: HTML5Translator, node: TbChoiceFeedbackNode) -> None:
    self.body.append('<div class="tb-choice__feedback">\n')


def depart_tb_choice_feedback_html(self: HTML5Translator, node: TbChoiceFeedbackNode) -> None:
    self.body.append("</div>\n")


def visit_tb_choice_latex(self: LaTeXTranslator, node: TbChoiceNode) -> None:
    latex_targets(self, node)
    self.body.append("\n\\subsubsection*{Question}\n")


def depart_tb_choice_latex(self: LaTeXTranslator, node: TbChoiceNode) -> None:
    self.body.append("\n\\end{itemize}\n")


def visit_tb_choice_prompt_latex(self: LaTeXTranslator, node: TbChoicePromptNode) -> None:
    self.body.append("\n")


def depart_tb_choice_prompt_latex(self: LaTeXTranslator, node: TbChoicePromptNode) -> None:
    self.body.append("\n\\begin{itemize}\n")


def visit_tb_choice_option_latex(self: LaTeXTranslator, node: TbChoiceOptionNode) -> None:
    self.body.append(f"\n\\item[{_choice_latex_marker(node)}] ")


def depart_tb_choice_option_latex(self: LaTeXTranslator, node: TbChoiceOptionNode) -> None:
    self.body.append("\n")


def visit_tb_choice_answer_latex(self: LaTeXTranslator, node: TbChoiceAnswerNode) -> None:
    pass


def depart_tb_choice_answer_latex(self: LaTeXTranslator, node: TbChoiceAnswerNode) -> None:
    pass


def visit_tb_choice_feedback_latex(self: LaTeXTranslator, node: TbChoiceFeedbackNode) -> None:
    raise nodes.SkipNode


def depart_tb_choice_feedback_latex(self: LaTeXTranslator, node: TbChoiceFeedbackNode) -> None:
    pass


def visit_tb_choice_text(self: TextTranslator, node: TbChoiceNode) -> None:
    self.add_text("\n[Question]\n")


def depart_tb_choice_text(self: TextTranslator, node: TbChoiceNode) -> None:
    self.add_text("\n")


def visit_tb_choice_prompt_text(self: TextTranslator, node: TbChoicePromptNode) -> None:
    pass


def depart_tb_choice_prompt_text(self: TextTranslator, node: TbChoicePromptNode) -> None:
    self.add_text("\nChoices:\n")


def visit_tb_choice_option_text(self: TextTranslator, node: TbChoiceOptionNode) -> None:
    self.add_text(f"{_choice_text_marker(node)} ")


def depart_tb_choice_option_text(self: TextTranslator, node: TbChoiceOptionNode) -> None:
    self.add_text("\n")


def visit_tb_choice_answer_text(self: TextTranslator, node: TbChoiceAnswerNode) -> None:
    pass


def depart_tb_choice_answer_text(self: TextTranslator, node: TbChoiceAnswerNode) -> None:
    pass


def visit_tb_choice_feedback_text(self: TextTranslator, node: TbChoiceFeedbackNode) -> None:
    raise nodes.SkipNode


def depart_tb_choice_feedback_text(self: TextTranslator, node: TbChoiceFeedbackNode) -> None:
    pass


def skip_choice_child(self, node) -> None:
    raise nodes.SkipNode
