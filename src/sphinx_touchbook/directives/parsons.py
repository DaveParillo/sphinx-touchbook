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

A Touchbook directive for Parsons problems.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbParsonsItemNode, TbParsonsNode, TbParsonsPromptNode


class TbParsonsDirective(Directive):
    """Parse a Parsons problem from a prompt and source block."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "name": directives.unchanged_required,
        "no-indent": directives.flag,
    }
    GROUP_MARKER = "{{group}}"
    DISTRACTOR_MARKER = "{{distractor}}"
    ENDGROUP_MARKER = "{{endgroup}}"
    MARKERS = {GROUP_MARKER, DISTRACTOR_MARKER, ENDGROUP_MARKER}

    def run(self):
        self.assert_has_content()
        parsed = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, parsed)

        try:
            prompt_children, item_nodes, language = self._extract_parts(parsed)
        except ValueError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]

        node = TbParsonsNode()
        assign_node_id(self, node)
        node["no_indent"] = "no-indent" in self.options
        node["language"] = language
        if prompt_children:
            prompt = TbParsonsPromptNode()
            prompt.extend(prompt_children)
            node += prompt
        node.extend(item_nodes)
        return [node]

    def _extract_parts(self, parsed: nodes.container):
        source_index = self._source_index(parsed)
        if source_index is None:
            raise ValueError("tb-parsons must contain one code-block, literal block, or bullet list.")
        if len([child for child in parsed.children if self._is_source(child)]) != 1:
            raise ValueError("tb-parsons must contain exactly one code-block, literal block, or bullet list.")
        if len(parsed.children) > source_index + 1:
            raise ValueError("tb-parsons content after the source block is not supported.")

        prompt_children = [deepcopy(child) for child in parsed.children[:source_index]]
        source = parsed.children[source_index]
        if isinstance(source, nodes.bullet_list):
            items = self._items_from_list(source)
            language = ""
        else:
            items = self._items_from_literal(source)
            language = source.get("language", "")
        required_count = len([item for item in items if not item["distractor"]])
        if required_count < 2:
            raise ValueError("tb-parsons must contain at least two required code fragments.")
        return prompt_children, items, language

    def _source_index(self, parsed: nodes.container) -> int | None:
        for index, child in enumerate(parsed.children):
            if self._is_source(child):
                return index
        return None

    def _is_source(self, node: nodes.Node) -> bool:
        return isinstance(node, nodes.literal_block | nodes.bullet_list)

    def _items_from_literal(self, source: nodes.literal_block) -> list[TbParsonsItemNode]:
        lines = source.astext().splitlines()
        if not any(line.strip() in self.MARKERS for line in lines):
            return self._line_items(lines)
        return self._group_items(lines)

    def _items_from_list(self, source: nodes.bullet_list) -> list[TbParsonsItemNode]:
        return [
            self._item(item.astext(), 0, index, distractor=False)
            for index, item in enumerate(source.children)
            if item.astext().strip()
        ]

    def _line_items(self, lines: list[str]) -> list[TbParsonsItemNode]:
        items = []
        for line in lines:
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip(" "))
            items.append(self._item(line.lstrip(" "), indent, len(items), distractor=False))
        return items

    def _group_items(self, lines: list[str]) -> list[TbParsonsItemNode]:
        groups: list[_Fragment] = []
        current: list[str] = []
        current_distractor = False
        in_group = False
        pending_distractor = False

        for line in lines:
            marker = line.strip()
            if marker == self.GROUP_MARKER:
                if in_group:
                    raise ValueError("tb-parsons cannot start a group before ending the current group.")
                in_group = True
                current = []
                current_distractor = pending_distractor
                pending_distractor = False
                continue
            if marker == self.DISTRACTOR_MARKER:
                if in_group:
                    raise ValueError("tb-parsons cannot start a distractor before ending the current group.")
                pending_distractor = True
                continue
            if marker == self.ENDGROUP_MARKER:
                if not in_group:
                    raise ValueError("tb-parsons found {{endgroup}} without a matching {{group}}.")
                self._append_group(groups, current, current_distractor)
                current = []
                current_distractor = False
                in_group = False
                continue
            if in_group:
                current.append(line)
            elif line.strip():
                self._append_group(groups, [line], pending_distractor)
                pending_distractor = False
        if in_group:
            raise ValueError("tb-parsons found {{group}} without a matching {{endgroup}}.")
        if pending_distractor:
            raise ValueError("tb-parsons found {{distractor}} without a following fragment.")

        items: list[TbParsonsItemNode] = []
        for index, group in enumerate(groups):
            indent = _minimum_indent(group.lines)
            code = "\n".join(_dedent_line(line, indent) for line in group.lines).strip("\n")
            items.append(self._item(code, indent, index, distractor=group.distractor))
        return items

    def _append_group(self, groups: list[_Fragment], lines: list[str], distractor: bool) -> None:
        trimmed = _trim_blank_edges(lines)
        if trimmed:
            groups.append(_Fragment(trimmed, distractor))

    def _item(self, code: str, indent: int, index: int, *, distractor: bool) -> TbParsonsItemNode:
        item = TbParsonsItemNode()
        item["index"] = index
        item["code"] = code
        item["indent"] = indent
        item["distractor"] = distractor
        item += nodes.Text(code)
        return item


@dataclass
class _Fragment:
    lines: list[str]
    distractor: bool


def _trim_blank_edges(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]


def _minimum_indent(lines: list[str]) -> int:
    indents = [len(line) - len(line.lstrip(" ")) for line in lines if line.strip()]
    return min(indents, default=0)


def _dedent_line(line: str, indent: int) -> str:
    if not line.strip():
        return ""
    return line[indent:]
