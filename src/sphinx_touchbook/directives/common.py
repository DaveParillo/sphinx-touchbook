"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
Copyright (C) 2026 Dave Parillo.

Shared directive helpers.
"""

from __future__ import annotations

import re

from docutils import nodes
from docutils.parsers.rst import directives


NAME_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")


def class_names(value) -> list[str]:
    if isinstance(value, str):
        return directives.class_option(value)
    if isinstance(value, (list, tuple)):
        classes: list[str] = []
        for item in value:
            classes.extend(class_names(item))
        return classes
    return directives.class_option(str(value))


def assign_node_id(directive, node: nodes.Element) -> None:
    """Assign an explicit or deterministic generated ID to a
       directive node."""

    explicit_name = directive.options.get("name")
    if explicit_name:
        node_id = nodes.make_id(explicit_name)
        if not NAME_PATTERN.fullmatch(explicit_name):
            directive.state_machine.reporter.warning(
                f":name: {explicit_name!r} is not a valid identifier; it was converted to {node_id!r}. "
                "Use lowercase letters, digits, and hyphens, beginning with a letter.",
                line=directive.lineno,
            )
        if node_id:
            node["ids"].append(node_id)
        node["names"].append(nodes.fully_normalize_name(explicit_name))
        directive.state.document.note_explicit_target(node, node)
    else:
        directive.state.document.set_id(node)

    if "class" in directive.options:
        node["classes"].extend(class_names(directive.options["class"]))
