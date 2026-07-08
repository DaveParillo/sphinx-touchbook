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


def html_additional_targets(node: nodes.Element) -> str:
    ids = node.get("ids", [])
    if len(ids) < 2:
        return ""
    return "".join(f'<span id="{escape(node_id, quote=True)}"></span>\n' for node_id in ids[1:])


def latex_targets(translator, node: nodes.Element) -> None:
    if node.get("ids"):
        translator.body.append(translator.hypertarget_to(node, anchor=True))
