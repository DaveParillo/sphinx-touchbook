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

A Touchbook directive to provide tabbed panels in HTML.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""




from __future__ import annotations



from __future__ import annotations

from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbGroupNode, TbTabNode


class TbGroupDirective(Directive):
    """Parse a tab group container."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "name": directives.unchanged_required,
    }

    def run(self):
        self.assert_has_content()
        node = TbGroupNode()
        assign_node_id(self, node)
        self.state.nested_parse(self.content, self.content_offset, node)
        if not any(isinstance(child, TbTabNode) for child in node.children):
            return [
                self.state_machine.reporter.error(
                    "tb-group must contain at least one immediate tb-tab directive.",
                    line=self.lineno,
                )
            ]
        return [node]


class TbTabDirective(Directive):
    """Parse one tab panel."""

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "name": directives.unchanged_required,
    }

    def run(self):
        self.assert_has_content()
        node = TbTabNode()
        assign_node_id(self, node)
        node["label"] = self.arguments[0]
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
