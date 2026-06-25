"""Docutils nodes for interactive textbook directives."""

from __future__ import annotations

from docutils import nodes


class TbRevealNode(nodes.General, nodes.Element):
    """Semantic node for content revealed inline or in a modal."""


class TbGroupNode(nodes.General, nodes.Element):
    """Semantic node for a group of selectable tabs."""


class TbTabNode(nodes.General, nodes.Element):
    """Semantic node for one tab inside a tab group."""


class TbCodeNode(nodes.General, nodes.Element):
    """Semantic node for runnable source code."""


class TbFileNode(nodes.General, nodes.Element):
    """Semantic node for a simulated local file."""


class TbVideoNode(nodes.General, nodes.Element):
    """Semantic node for an instructional video."""
