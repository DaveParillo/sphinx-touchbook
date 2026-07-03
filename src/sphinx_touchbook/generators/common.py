"""Shared builder helpers."""

from __future__ import annotations

from html import escape

from docutils import nodes


def html_class_attr(node: nodes.Element) -> str:
    classes = node.get("classes", [])
    if not classes:
        return ""
    value = " ".join(escape(name, quote=True) for name in classes)
    return f' class="{value}"'
