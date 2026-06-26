"""Builder generators for ``tb-choice``."""

from __future__ import annotations

from html import escape

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.nodes import (
    TbChoiceAnswerNode,
    TbChoiceFeedbackNode,
    TbChoiceNode,
    TbChoiceOptionNode,
    TbChoicePromptNode,
)


def _node_id(node) -> str:
    return node["ids"][0]


def visit_tb_choice_html(self: HTML5Translator, node: TbChoiceNode) -> None:
    node_id = escape(_node_id(node), quote=True)
    mode = "multiple" if node["multiple"] else "single"
    random_attr = ' random="true"' if node.get("random") else ""
    self.body.append(f'<tb-choice id="{node_id}" mode="{mode}"{random_attr}>\n')


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
    node_id = escape(_node_id(parent), quote=True)
    index = int(node["index"])
    input_id = escape(f"{_node_id(parent)}-option-{index}", quote=True)
    input_type = "checkbox" if parent["multiple"] else "radio"
    name = escape(f"{_node_id(parent)}-answer", quote=True)
    correct = "true" if node["correct"] else "false"

    self.body.append(f'<div class="tb-choice__option" data-correct="{correct}">\n')
    self.body.append('<label class="tb-choice__label">\n')
    self.body.append(
        f'<input id="{input_id}" class="tb-choice__input" type="{input_type}" '
        f'name="{name}" value="{index}">\n'
    )
    self.body.append('<div class="tb-choice__answer">\n')


def depart_tb_choice_option_html(self: HTML5Translator, node: TbChoiceOptionNode) -> None:
    self.body.append("</div>\n")


def visit_tb_choice_answer_html(self: HTML5Translator, node: TbChoiceAnswerNode) -> None:
    pass


def depart_tb_choice_answer_html(self: HTML5Translator, node: TbChoiceAnswerNode) -> None:
    self.body.append("</div>\n")
    self.body.append("</label>\n")


def visit_tb_choice_feedback_html(self: HTML5Translator, node: TbChoiceFeedbackNode) -> None:
    self.body.append('<div class="tb-choice__feedback">\n')


def depart_tb_choice_feedback_html(self: HTML5Translator, node: TbChoiceFeedbackNode) -> None:
    self.body.append("</div>\n")


def visit_tb_choice_latex(self: LaTeXTranslator, node: TbChoiceNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{Question}\n")


def depart_tb_choice_latex(self: LaTeXTranslator, node: TbChoiceNode) -> None:
    self.body.append("\n\\end{itemize}\n\\end{sphinxadmonition}\n")


def visit_tb_choice_prompt_latex(self: LaTeXTranslator, node: TbChoicePromptNode) -> None:
    self.body.append("\n")


def depart_tb_choice_prompt_latex(self: LaTeXTranslator, node: TbChoicePromptNode) -> None:
    self.body.append("\n\\begin{itemize}\n")


def visit_tb_choice_option_latex(self: LaTeXTranslator, node: TbChoiceOptionNode) -> None:
    self.body.append("\n\\item ")


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
    self.add_text("- ")


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
