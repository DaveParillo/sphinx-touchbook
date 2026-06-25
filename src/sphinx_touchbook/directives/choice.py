"""The ``tb-choice`` directive."""

# Inspired by the Runestone multiple choice directive and its list-based author
# interface by Bradley N. Miller and Barbara Ericson:
# https://github.com/RunestoneInteractive/RunestoneComponents/blob/master/runestone/mchoice/multiplechoice.py

from __future__ import annotations

from copy import deepcopy

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import (
    TbChoiceAnswerNode,
    TbChoiceFeedbackNode,
    TbChoiceNode,
    TbChoiceOptionNode,
    TbChoicePromptNode,
)


class TbChoiceDirective(Directive):
    """Parse a multiple choice or multiple answer assessment."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "name": directives.unchanged_required,
        "random": directives.flag,
    }

    def run(self):
        self.assert_has_content()
        parsed = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, parsed)

        try:
            prompt_children, option_nodes = self._extract_parts(parsed)
        except ValueError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]

        correct_count = sum(1 for option in option_nodes if option["correct"])
        if correct_count == 0:
            return [
                self.state_machine.reporter.error(
                    "tb-choice must contain at least one correct answer marked with '+'.",
                    line=self.lineno,
                )
            ]

        node = TbChoiceNode()
        assign_node_id(self, node)
        node["multiple"] = correct_count > 1
        node["random"] = "random" in self.options

        prompt = TbChoicePromptNode()
        prompt.extend(prompt_children)
        node += prompt
        node.extend(option_nodes)
        return [node]

    def _extract_parts(self, parsed: nodes.container):
        answer_list_index = self._answer_list_index(parsed)
        if answer_list_index is None:
            raise ValueError("tb-choice must contain a bullet list of answer choices.")

        prompt_children = [deepcopy(child) for child in parsed.children[:answer_list_index]]
        answer_list = parsed.children[answer_list_index]
        if not isinstance(answer_list, nodes.bullet_list):
            raise ValueError("tb-choice answer choices must be a bullet list.")
        if len(parsed.children) > answer_list_index + 1:
            raise ValueError("tb-choice content after the answer list is not supported.")

        option_nodes = []
        for index, item in enumerate(answer_list.children):
            if not isinstance(item, nodes.list_item):
                raise ValueError("tb-choice answer choices must be list items.")
            option_nodes.append(self._option_from_item(item, index))
        return prompt_children, option_nodes

    def _answer_list_index(self, parsed: nodes.container) -> int | None:
        for index, child in enumerate(parsed.children):
            if isinstance(child, nodes.bullet_list):
                return index
        return None

    def _option_from_item(self, item: nodes.list_item, index: int) -> TbChoiceOptionNode:
        feedback_lists = [
            child for child in item.children if isinstance(child, nodes.bullet_list) and child.get("bullet") in {"+", "-"}
        ]
        if len(feedback_lists) != 1:
            raise ValueError(
                "Each tb-choice answer must contain exactly one nested feedback "
                "list marked with '+' for correct or '-' for incorrect."
            )

        feedback_list = feedback_lists[0]
        if len(feedback_list.children) != 1:
            raise ValueError("Each tb-choice feedback list must contain exactly one item.")

        option = TbChoiceOptionNode()
        option["correct"] = feedback_list.get("bullet") == "+"
        option["index"] = index

        answer = TbChoiceAnswerNode()
        for child in item.children:
            if child is not feedback_list:
                answer += deepcopy(child)
        if not answer.children:
            raise ValueError("Each tb-choice answer must contain visible answer content.")

        feedback = TbChoiceFeedbackNode()
        feedback.extend(deepcopy(child) for child in feedback_list.children[0].children)
        if not feedback.children:
            raise ValueError("Each tb-choice answer must contain feedback content.")

        option += answer
        option += feedback
        return option
