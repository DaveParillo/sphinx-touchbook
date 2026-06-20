"""The ``tb-reveal`` directive."""

from __future__ import annotations

from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbRevealNode


class TbRevealDirective(Directive):
    """Parse author reveal content into a semantic node."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "id": directives.unchanged_required,
        "showtitle": directives.unchanged,
        "hidetitle": directives.unchanged,
        "modal": directives.flag,
        "modaltitle": directives.unchanged,
    }

    def run(self):
        self.assert_has_content()
        node = TbRevealNode()
        assign_node_id(self, node)
        node["showtitle"] = self.options.get("showtitle", "Show")
        node["hidetitle"] = self.options.get("hidetitle", "Hide")
        node["modal"] = "modal" in self.options
        node["modaltitle"] = self.options.get("modaltitle", "Message from the author")
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
