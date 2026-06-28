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

A Touchbook directive for fill-in-the-blank assessments.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import NamedTuple

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbBlankInputNode, TbBlankNode, TbBlankPromptNode

BLANK_RE = re.compile(r"\{\{blank(?::(?P<name>[A-Za-z0-9_-]+))?\}\}")
ANSWER_RE = re.compile(r"^(?P<indent>\s*)\.\.\s+tb-answer::(?:\s+(?P<blank>[A-Za-z0-9_-]+))?\s*$")
OPTION_RE = re.compile(r"^\s*:(?P<name>[A-Za-z-]+):(?:\s*(?P<value>.*))?$")


class BlankError(ValueError):
    """Raised when tb-blank content is invalid."""


class AnswerBlock(NamedTuple):
    blank: str | None
    options: list[tuple[str, str]]


class TbBlankDirective(Directive):
    """Parse a fill-in-the-blank assessment."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "case-sensitive": directives.flag,
        "name": directives.unchanged_required,
        "preserve-whitespace": directives.flag,
    }

    def run(self):
        self.assert_has_content()
        try:
            prompt_lines, answer_blocks = self._split_content()
            parsed = nodes.container()
            self.state.nested_parse(prompt_lines, self.content_offset, parsed)
            node = self._build_node(parsed, answer_blocks)
        except BlankError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]

        return [node]

    def _split_content(self) -> tuple[StringList, list[AnswerBlock]]:
        prompt_lines = StringList()
        answer_blocks = []
        index = 0
        while index < len(self.content):
            line = self.content[index]
            match = ANSWER_RE.match(line)
            if match is None:
                prompt_lines.append(line, source=self.content.source(index), offset=self.content.offset(index))
                index += 1
                continue

            block_indent = len(match.group("indent"))
            blank = match.group("blank")
            block_lines = []
            index += 1
            while index < len(self.content):
                next_line = self.content[index]
                nested_match = ANSWER_RE.match(next_line)
                if nested_match is not None and len(nested_match.group("indent")) <= block_indent:
                    break
                if next_line.strip() and self._indent_width(next_line) <= block_indent:
                    break
                block_lines.append(next_line[block_indent + 3 :] if len(next_line) > block_indent + 3 else "")
                index += 1
            answer_blocks.append(self._answer_block(blank, block_lines))
        return prompt_lines, answer_blocks

    def _answer_block(self, blank: str | None, lines: list[str]) -> AnswerBlock:
        options: list[tuple[str, str]] = []
        current: tuple[str, str] | None = None
        for line in lines:
            option = OPTION_RE.match(line)
            if option is not None:
                if current is not None:
                    options.append(current)
                current = (option.group("name"), option.group("value") or "")
                continue
            if current is not None and (not line.strip() or self._indent_width(line) > 0):
                current = (current[0], f"{current[1]}\n{line.strip()}".strip())
                continue
            if line.strip():
                raise BlankError(f"Unsupported tb-answer content: {line.strip()}")
        if current is not None:
            options.append(current)
        if not any(name == "match" for name, _ in options):
            raise BlankError("Each tb-answer block must contain at least one :match: option.")
        for name, value in options:
            if name == "hint" and ";" not in value:
                raise BlankError("Each :hint: option must use 'value; feedback' syntax.")
        return AnswerBlock(blank=blank, options=options)

    def _build_node(self, parsed: nodes.container, answer_blocks: list[AnswerBlock]) -> TbBlankNode:
        node = TbBlankNode()
        assign_node_id(self, node)
        node["case_sensitive"] = "case-sensitive" in self.options
        node["trim"] = "preserve-whitespace" not in self.options

        prompt = TbBlankPromptNode()
        prompt.extend(deepcopy(child) for child in parsed.children)
        blanks = self._replace_blank_markers(prompt)
        if not blanks:
            raise BlankError("tb-blank prompt must contain at least one {{blank}} marker.")

        node["blanks"] = blanks
        node["answers"] = self._answers_for_blanks(blanks, answer_blocks)
        node += prompt
        return node

    def _replace_blank_markers(self, root: nodes.Element) -> list[str]:
        blanks = []
        generated_index = 0
        for text_node in list(root.findall(nodes.Text)):
            text = text_node.astext()
            parts: list[nodes.Node] = []
            last = 0
            for match in BLANK_RE.finditer(text):
                if match.start() > last:
                    parts.append(nodes.Text(text[last : match.start()]))
                blank_id = match.group("name") or f"blank{generated_index + 1}"
                generated_index += 1
                input_node = TbBlankInputNode()
                input_node["blank_id"] = blank_id
                input_node["index"] = len(blanks)
                parts.append(input_node)
                blanks.append(blank_id)
                last = match.end()
            if not parts:
                continue
            if last < len(text):
                parts.append(nodes.Text(text[last:]))
            text_node.parent.replace(text_node, parts)
        if len(blanks) != len(set(blanks)):
            raise BlankError("Each named blank in tb-blank must be unique.")
        return blanks

    def _answers_for_blanks(self, blanks: list[str], answer_blocks: list[AnswerBlock]) -> dict[str, dict[str, object]]:
        if not answer_blocks:
            raise BlankError("tb-blank must contain at least one nested tb-answer block.")
        if len(blanks) > 1 and any(block.blank is None for block in answer_blocks):
            raise BlankError("tb-answer must name a blank when tb-blank contains multiple blanks.")

        answers = {blank: {"matches": [], "hints": [], "feedback": None, "incorrect": None, "regex": False} for blank in blanks}
        for block in answer_blocks:
            blank = block.blank or blanks[0]
            if blank not in answers:
                raise BlankError(f"tb-answer references unknown blank '{blank}'.")
            target = answers[blank]
            for name, value in block.options:
                if name == "match":
                    target["matches"].append(value)
                elif name == "feedback":
                    target["feedback"] = value
                elif name == "incorrect":
                    target["incorrect"] = value
                elif name == "hint":
                    hint_value, hint_feedback = value.split(";", 1)
                    target["hints"].append({"value": hint_value.strip(), "feedback": hint_feedback.strip()})
                elif name == "regex":
                    target["regex"] = True
                else:
                    raise BlankError(f"Unsupported tb-answer option ':{name}:'.")

        for blank, data in answers.items():
            if not data["matches"]:
                raise BlankError(f"Blank '{blank}' must have at least one accepted answer.")
        return answers

    def _indent_width(self, line: str) -> int:
        return len(line) - len(line.lstrip(" "))
