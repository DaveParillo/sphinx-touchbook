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

A Touchbook directive for multiple choice questions.

The content area allows questions and feedback defined in one of two
formats: 'compact' and 'nested list'.
Compact questions look like:
   - [x] correct choice
   - [ ] incorrect choice

     Feedback as a separate paragraph within a list is optional.

To support arbitrarily complex answer options the nested list option is
also available.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

# Inspired by the Runestone multiple choice directive and its list-based author
# interface by Bradley N. Miller and Barbara Ericson:
# https://github.com/RunestoneInteractive/RunestoneComponents/blob/master/runestone/mchoice/multiplechoice.py

from __future__ import annotations

from copy import deepcopy
import re

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

COMPACT_MARKER_RE = re.compile(r"^\[(?P<marker>[xX+\- ])\]\s*")
DEFAULT_RANDOM = False
DEFAULT_FORCE_MULTIPLE = False


def _config(directive):
    env = getattr(directive.state.document.settings, "env", None)
    return getattr(env, "config", None)


def _config_bool(config, name: str, default: bool) -> bool:
    return bool(getattr(config, name, default)) if config is not None else default


class TbChoiceDirective(Directive):
    """Parse a multiple choice or multiple answer assessment."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "force-multiple": directives.flag,
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
                    "tb-choice must contain at least one correct answer marked "
                    "with '[x]', '[+]', or nested '+' feedback.",
                    line=self.lineno,
                )
            ]

        node = TbChoiceNode()
        assign_node_id(self, node)
        config = _config(self)
        force_multiple = "force-multiple" in self.options or _config_bool(
            config,
            "tb_choice_force_multiple",
            DEFAULT_FORCE_MULTIPLE,
        )

        node["multiple"] = correct_count > 1 or force_multiple
        node["random"] = "random" in self.options or _config_bool(
            config,
            "tb_choice_random",
            DEFAULT_RANDOM,
        )

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
            if isinstance(child, nodes.bullet_list) and self._is_answer_list(child):
                return index
        return None

    def _is_answer_list(self, answer_list: nodes.bullet_list) -> bool:
        return all(
            isinstance(item, nodes.list_item)
            and (self._has_compact_marker(item) or self._has_feedback_list(item))
            for item in answer_list.children
        )

    def _has_compact_marker(self, item: nodes.list_item) -> bool:
        if not item.children or not isinstance(item.children[0], nodes.paragraph):
            return False
        paragraph = item.children[0]
        return (
            bool(paragraph.children)
            and isinstance(paragraph.children[0], nodes.Text)
            and bool(COMPACT_MARKER_RE.match(paragraph.children[0].astext()))
        )

    def _has_feedback_list(self, item: nodes.list_item) -> bool:
        return any(
            isinstance(child, nodes.bullet_list) and child.get("bullet") in {"+", "-"}
            for child in item.children
        )

    def _option_from_item(self, item: nodes.list_item, index: int) -> TbChoiceOptionNode:
        compact = self._compact_option_from_item(item, index)
        if compact is not None:
            return compact

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

    def _compact_option_from_item(self, item: nodes.list_item, index: int) -> TbChoiceOptionNode | None:
        if not item.children or not isinstance(item.children[0], nodes.paragraph):
            return None

        first_paragraph = deepcopy(item.children[0])
        marker = self._remove_compact_marker(first_paragraph)
        if marker is None:
            return None

        option = TbChoiceOptionNode()
        option["correct"] = marker in {"x", "X", "+"}
        option["index"] = index

        answer = TbChoiceAnswerNode()
        if first_paragraph.children:
            answer += first_paragraph
        else:
            raise ValueError("Each compact tb-choice answer must contain answer text after its marker.")

        feedback = TbChoiceFeedbackNode()
        feedback.extend(deepcopy(child) for child in item.children[1:])

        option += answer
        if feedback.children:
            option += feedback
        return option

    def _remove_compact_marker(self, paragraph: nodes.paragraph) -> str | None:
        if not paragraph.children or not isinstance(paragraph.children[0], nodes.Text):
            return None

        text_node = paragraph.children[0]
        match = COMPACT_MARKER_RE.match(text_node.astext())
        if not match:
            return None

        marker = match.group("marker")
        remaining = text_node.astext()[match.end() :]
        if remaining:
            paragraph[0] = nodes.Text(remaining)
        else:
            paragraph.children.pop(0)
        return marker
