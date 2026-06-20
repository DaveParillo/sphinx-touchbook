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
        "name": directives.unchanged_required,
        "showlabel": directives.unchanged,
        "hidelabel": directives.unchanged,
        "modal-titlebar": directives.unchanged,
        "modal": directives.flag,
    }

    def run(self):
        self.assert_has_content()
        node = TbRevealNode()
        assign_node_id(self, node)
        node["showlabel"] = self.options.get("showlabel", "Show")
        node["hidelabel"] = self.options.get("hidelabel", "Hide")
        node["modal"] = "modal" in self.options
        node["modal_titlebar"] = self.options.get("modal-titlebar", "Message from the author")
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
