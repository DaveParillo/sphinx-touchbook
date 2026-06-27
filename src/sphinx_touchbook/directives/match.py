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

A Touchbook directive for matching source terms to target definitions.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

from copy import deepcopy

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import (
    TbMatchDistractorNode,
    TbMatchNode,
    TbMatchPairNode,
    TbMatchPromptNode,
    TbMatchSourceNode,
    TbMatchTargetNode,
)


class MatchError(ValueError):
    """Raised when tb-match content is not a valid matching question."""


class TbMatchDirective(Directive):
    """Parse a matching assessment from a definition list."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "distractors": directives.unchanged,
        "name": directives.unchanged_required,
    }

    def run(self):
        self.assert_has_content()
        parsed = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, parsed)

        try:
            node = self._build_node(parsed)
        except MatchError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]

        return [node]

    def _build_node(self, parsed: nodes.container) -> TbMatchNode:
        list_index = self._definition_list_index(parsed)
        if list_index is None:
            raise MatchError("tb-match must contain a definition list of source and target pairs.")
        if len([child for child in parsed.children if isinstance(child, nodes.definition_list)]) != 1:
            raise MatchError("tb-match must contain exactly one definition list.")
        if len(parsed.children) > list_index + 1:
            raise MatchError("tb-match content after the definition list is not supported.")

        definition_list = parsed.children[list_index]
        if len(definition_list.children) < 2:
            raise MatchError("tb-match must contain at least two source and target pairs.")

        node = TbMatchNode()
        assign_node_id(self, node)

        prompt = TbMatchPromptNode()
        prompt.extend(deepcopy(child) for child in parsed.children[:list_index])
        node += prompt

        for index, item in enumerate(definition_list.children):
            node += self._pair_from_item(item, index)
        for distractor in self._distractors():
            node += distractor
        return node

    def _definition_list_index(self, parsed: nodes.container) -> int | None:
        for index, child in enumerate(parsed.children):
            if isinstance(child, nodes.definition_list):
                return index
        return None

    def _pair_from_item(self, item: nodes.definition_list_item, index: int) -> TbMatchPairNode:
        terms = [child for child in item.children if isinstance(child, nodes.term)]
        definitions = [child for child in item.children if isinstance(child, nodes.definition)]
        if len(terms) != 1 or len(definitions) != 1:
            raise MatchError("Each tb-match definition item must have exactly one term and one definition.")
        if not terms[0].children:
            raise MatchError("Each tb-match source term must contain content.")
        if not definitions[0].children:
            raise MatchError("Each tb-match target definition must contain content.")

        pair = TbMatchPairNode()
        pair["index"] = index

        source = TbMatchSourceNode()
        source.extend(deepcopy(child) for child in terms[0].children)
        pair += source

        target = TbMatchTargetNode()
        target.extend(deepcopy(child) for child in definitions[0].children)
        pair += target
        return pair

    def _distractors(self) -> list[TbMatchDistractorNode]:
        value = self.options.get("distractors")
        if not value:
            return []

        entries = []
        for line in value.splitlines():
            entries.extend(part.strip() for part in line.split(";"))

        distractors = []
        for entry in entries:
            if not entry:
                continue
            distractor = TbMatchDistractorNode()
            distractor += nodes.paragraph(text=entry)
            distractors.append(distractor)
        return distractors
