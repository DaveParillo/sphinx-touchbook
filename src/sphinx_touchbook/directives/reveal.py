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

A Touchbook directive to provide a button that show content
inline or in a modal popup window.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""




from __future__ import annotations


from __future__ import annotations

from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbRevealNode


class TbRevealDirective(Directive):
    """Parse author reveal content into a semantic node."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "name": directives.unchanged_required,
        "showlabel": directives.unchanged,
        "hidelabel": directives.unchanged,
        "modal-titlebar": directives.unchanged,
        "modal": directives.flag,
    }

    def run(self):
        self.assert_has_content()
        node = TbRevealNode()
        assign_node_id(self, node)
        node["showlabel"] = self.options.get("showlabel", "Show")
        node["hidelabel"] = self.options.get("hidelabel", "Hide")
        node["modal"] = "modal" in self.options
        node["modal_titlebar"] = self.options.get("modal-titlebar", "Message from the author")
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
