"""Tab group directives."""

from __future__ import annotations

from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbGroupNode, TbTabNode


class TbGroupDirective(Directive):
    """Parse a tab group container."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "id": directives.unchanged_required,
    }

    def run(self):
        self.assert_has_content()
        node = TbGroupNode()
        assign_node_id(self, node)
        self.state.nested_parse(self.content, self.content_offset, node)
        if not any(isinstance(child, TbTabNode) for child in node.children):
            return [
                self.state_machine.reporter.error(
                    "tb-group must contain at least one immediate tb-tab directive.",
                    line=self.lineno,
                )
            ]
        return [node]


class TbTabDirective(Directive):
    """Parse one tab panel."""

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "id": directives.unchanged_required,
    }

    def run(self):
        self.assert_has_content()
        node = TbTabNode()
        assign_node_id(self, node)
        node["label"] = self.arguments[0]
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
