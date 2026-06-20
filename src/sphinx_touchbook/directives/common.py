"""Shared directive helpers."""

from __future__ import annotations

from docutils import nodes


def assign_node_id(directive, node: nodes.Element) -> None:
    """Assign an explicit or deterministic generated ID to a directive node."""

    explicit_name = directive.options.get("name")
    if explicit_name:
        node_id = nodes.make_id(explicit_name)
        if node_id:
            node["ids"].append(node_id)
        node["names"].append(nodes.fully_normalize_name(explicit_name))
        directive.state.document.note_explicit_target(node, node)
    else:
        directive.state.document.set_id(node)
