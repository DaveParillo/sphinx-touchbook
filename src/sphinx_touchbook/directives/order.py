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

A Touchbook directive for ordering line-based content.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

from copy import deepcopy

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbOrderItemNode, TbOrderNode, TbOrderPromptNode


class TbOrderDirective(Directive):
    """Parse an ordering assessment from a bullet list."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "name": directives.unchanged_required,
    }

    def run(self):
        self.assert_has_content()
        parsed = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, parsed)

        try:
            prompt_children, item_nodes = self._extract_parts(parsed)
        except ValueError as error:
            return [
                self.state_machine.reporter.error(
                    str(error),
                    line=self.lineno,
                )
            ]

        node = TbOrderNode()
        assign_node_id(self, node)
        if prompt_children:
            prompt = TbOrderPromptNode()
            prompt.extend(prompt_children)
            node += prompt
        node.extend(item_nodes)
        return [node]

    def _extract_parts(self, parsed: nodes.container) -> tuple[list[nodes.Node], list[TbOrderItemNode]]:
        list_index = self._item_list_index(parsed)
        if list_index is None:
            raise ValueError("tb-order must contain one bullet list of items to order.")
        if len([child for child in parsed.children if isinstance(child, nodes.bullet_list)]) != 1:
            raise ValueError("tb-order must contain exactly one bullet list.")
        if len(parsed.children) > list_index + 1:
            raise ValueError("tb-order content after the item list is not supported.")

        item_list = parsed.children[list_index]
        if len(item_list.children) < 2:
            raise ValueError("tb-order must contain at least two list items.")

        prompt_children = [deepcopy(child) for child in parsed.children[:list_index]]
        item_nodes = [self._item_from_list_item(item, index) for index, item in enumerate(item_list.children)]
        return prompt_children, item_nodes

    def _item_list_index(self, parsed: nodes.container) -> int | None:
        for index, child in enumerate(parsed.children):
            if isinstance(child, nodes.bullet_list):
                return index
        return None

    def _item_from_list_item(self, item: nodes.list_item, index: int) -> TbOrderItemNode:
        if not isinstance(item, nodes.list_item):
            raise ValueError("tb-order items must be bullet list items.")
        if not item.children:
            raise ValueError("tb-order list items must contain content.")

        order_item = TbOrderItemNode()
        order_item["index"] = index
        order_item.extend(deepcopy(child) for child in item.children)
        return order_item
