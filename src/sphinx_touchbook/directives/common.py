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

Shared directive helpers.
"""

from __future__ import annotations

from docutils import nodes


def assign_node_id(directive, node: nodes.Element) -> None:
    """Assign an explicit or deterministic generated ID to a
       directive node."""

    explicit_name = directive.options.get("name")
    if explicit_name:
        node_id = nodes.make_id(explicit_name)
        if node_id:
            node["ids"].append(node_id)
        node["names"].append(nodes.fully_normalize_name(explicit_name))
        directive.state.document.note_explicit_target(node, node)
    else:
        directive.state.document.set_id(node)
