"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.

Docutils nodes for interactive textbook directives.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

from docutils import nodes

class TbAnimationNode(nodes.General, nodes.Element):
    """An ordered sequence of complete instructional scenes."""


class TbSceneNode(nodes.General, nodes.Element):
    """A complete, independently renderable scene and local object scope."""


class TbPointerNode(nodes.General, nodes.Element):
    """A pointer or bounded iterator with a resolved scene-local position."""


class TbArrayNode(nodes.General, nodes.Element):
    """Semantic node for an ordered array of values or keyed items."""


class TbGraphNode(nodes.General, nodes.Element):
    """Semantic node for a complete directed graph."""


def is_scene_object(node):
    """Recognize semantic object keys independently of directive type."""
    return isinstance(node, nodes.Element) and (
        "key" in node or isinstance(node, (TbArrayNode, TbGraphNode, TbPointerNode))
    )


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


class TbBlankNode(nodes.General, nodes.Element):
    """Semantic node for a fill-in-the-blank assessment."""


class TbBlankPromptNode(nodes.General, nodes.Element):
    """Prompt content for a fill-in-the-blank assessment."""


class TbBlankInputNode(nodes.General, nodes.Element):
    """One blank input location in a fill-in-the-blank assessment."""


class TbFormulaNode(nodes.General, nodes.Element):
    """Semantic node for a calculated numeric formula assessment."""


class TbFormulaPromptNode(nodes.General, nodes.Element):
    """Prompt content for a calculated formula assessment."""


class TbFormulaVariableNode(nodes.General, nodes.Element):
    """One generated variable location in a calculated formula assessment."""


class TbOrderNode(nodes.General, nodes.Element):
    """Semantic node for an ordering assessment."""


class TbOrderPromptNode(nodes.General, nodes.Element):
    """Prompt content for an ordering assessment."""


class TbOrderItemNode(nodes.General, nodes.Element):
    """One item in an ordering assessment."""


class TbParsonsNode(nodes.General, nodes.Element):
    """Semantic node for a Parsons problem."""


class TbParsonsPromptNode(nodes.General, nodes.Element):
    """Prompt content for a Parsons problem."""


class TbParsonsItemNode(nodes.General, nodes.Element):
    """One code fragment in a Parsons problem."""


class TbClickNode(nodes.General, nodes.Element):
    """Semantic node for a clickable-source assessment."""


class TbClickPromptNode(nodes.General, nodes.Element):
    """Prompt content for a clickable-source assessment."""


class TbClickSourceNode(nodes.General, nodes.Element):
    """Literal source content for a clickable-source assessment."""


class TbClickRegionNode(nodes.General, nodes.Element):
    """Feedback for one clickable source region."""


class TbMatchNode(nodes.General, nodes.Element):
    """Semantic node for a matching assessment."""


class TbMatchPromptNode(nodes.General, nodes.Element):
    """Prompt content for a matching assessment."""


class TbMatchPairNode(nodes.General, nodes.Element):
    """One source and target pair for a matching assessment."""


class TbMatchSourceNode(nodes.General, nodes.Element):
    """Draggable source content for a matching pair."""


class TbMatchTargetNode(nodes.General, nodes.Element):
    """Target content for a matching pair."""


class TbMatchDistractorNode(nodes.General, nodes.Element):
    """Unmatched target option for a matching assessment."""


class TbMicroParsonsNode(nodes.General, nodes.Element):
    """Semantic node for a token-level Parsons assessment."""


class TbMicroParsonsPromptNode(nodes.General, nodes.Element):
    """Prompt content for a token-level Parsons assessment."""


class TbMicroParsonsTokenNode(nodes.General, nodes.Element):
    """One token in a token-level Parsons assessment."""
