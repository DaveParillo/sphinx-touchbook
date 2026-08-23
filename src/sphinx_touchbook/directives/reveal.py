"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
Copyright (C) 2026 Dave Parillo.

A Touchbook directive to provide a button that show content
inline or in a modal popup window.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""




from __future__ import annotations


from __future__ import annotations

from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbRevealNode


class TbRevealDirective(Directive):
    """Parse author reveal content into a semantic node."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "class": directives.class_option,
        "name": directives.unchanged_required,
    }

    def run(self):
        self.assert_has_content()
        node = TbRevealNode()
        assign_node_id(self, node)
        node["title"] = self.arguments[0] if self.arguments else "Details"
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]
