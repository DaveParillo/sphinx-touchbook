"""Shared directive helpers."""

from __future__ import annotations

from docutils import nodes


def assign_node_id(directive, node: nodes.Element) -> None:
    """Assign an explicit or deterministic generated ID to a directive node."""

    explicit_id = directive.options.get("id")
    if explicit_id:
        node["ids"].append(nodes.make_id(explicit_id))
        directive.state.document.note_explicit_target(node, node)
    else:
        directive.state.document.set_id(node)
