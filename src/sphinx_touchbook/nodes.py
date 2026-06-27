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

Docutils nodes for interactive textbook directives.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

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
