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

A Touchbook directive for token-level Parsons problems.
"""

from __future__ import annotations

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import (
    TbMicroParsonsNode,
    TbMicroParsonsPromptNode,
    TbMicroParsonsTokenNode,
)


class TbMicroParsonsDirective(Directive):
    """Parse a micro-Parsons assessment from a bullet list."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "distractor": directives.unchanged,
        "name": directives.unchanged_required,
    }

    def run(self):
        self.assert_has_content()
        try:
            prompt_lines, tokens = self._split_content()
        except ValueError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]

        parsed = nodes.container()
        self.state.nested_parse(prompt_lines, self.content_offset, parsed)

        try:
            token_nodes = self._token_nodes(tokens)
        except ValueError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]

        node = TbMicroParsonsNode()
        assign_node_id(self, node)
        node["has_distractors"] = any(token["distractor"] for token in token_nodes)
        if parsed.children:
            prompt = TbMicroParsonsPromptNode()
            prompt.extend(parsed.children)
            node += prompt
        node.extend(token_nodes)
        return [node]

    def _split_content(self) -> tuple[StringList, list[str]]:
        prompt_lines = StringList()
        tokens = []
        in_token_list = False
        for index, line in enumerate(self.content):
            parsed = self._token_line(line)
            if parsed is None:
                if in_token_list and line.strip():
                    raise ValueError("tb-micro-parsons content after the token list is not supported.")
                if not in_token_list:
                    prompt_lines.append(line, source=self.content.source(index), offset=self.content.offset(index))
                continue
            in_token_list = True
            tokens.append(parsed)

        if not tokens:
            raise ValueError("tb-micro-parsons must contain one bullet list of tokens.")
        if len(tokens) < 2:
            raise ValueError("tb-micro-parsons must contain at least two tokens.")
        return prompt_lines, tokens

    def _token_line(self, line: str) -> str | None:
        stripped = line.strip()
        if len(stripped) < 3 or stripped[0] not in "-*+" or stripped[1] != " ":
            return None
        token = stripped[2:].strip()
        if not token:
            raise ValueError("tb-micro-parsons tokens must contain content.")
        return token

    def _token_nodes(self, tokens: list[str]) -> list[TbMicroParsonsTokenNode]:
        token_nodes = [self._token(token, index, distractor=False) for index, token in enumerate(tokens)]
        for distractor in self._distractors():
            token_nodes.append(self._distractor_token(distractor, len(token_nodes)))
        return token_nodes

    def _token(self, text: str, index: int, *, distractor: bool) -> TbMicroParsonsTokenNode:
        token = TbMicroParsonsTokenNode()
        token["index"] = index
        token["distractor"] = distractor
        token["label"] = text
        paragraph = nodes.paragraph()
        paragraph += nodes.Text(text)
        token += paragraph
        return token

    def _distractor_token(self, text: str, index: int) -> TbMicroParsonsTokenNode:
        return self._token(text, index, distractor=True)

    def _distractors(self) -> list[str]:
        value = self.options.get("distractor")
        if not value:
            return []
        distractors = []
        for line in value.splitlines():
            for part in line.split(";"):
                token = part.strip()
                if token:
                    distractors.append(token)
        return distractors
