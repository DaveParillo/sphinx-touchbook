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


class TbChoiceNode(nodes.General, nodes.Element):
    """Semantic node for a multiple choice or multiple answer prompt."""


class TbChoicePromptNode(nodes.General, nodes.Element):
    """Prompt content for a choice assessment."""


class TbChoiceOptionNode(nodes.General, nodes.Element):
    """One answer option for a choice assessment."""


class TbChoiceAnswerNode(nodes.General, nodes.Element):
    """Visible answer content for a choice option."""


class TbChoiceFeedbackNode(nodes.General, nodes.Element):
    """Feedback content for a choice option."""
