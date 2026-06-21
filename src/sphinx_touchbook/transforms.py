"""Sphinx transforms for Touchbook directives."""

from __future__ import annotations

import re

from docutils import nodes
from docutils.transforms import Transform

from sphinx_touchbook.nodes import TbCodeNode


class TbCodeIncludeTransform(Transform):
    """Resolve literal source includes inside ``tb-code`` nodes."""

    default_priority = 500

    def apply(self) -> None:
        code_by_name = self._collect_named_code()
        for node in self.document.findall(TbCodeNode):
            specs = node.get("include_specs", [])
            if not specs:
                continue
            source = node["source"]
            for placeholder, source_name in specs:
                if not placeholder or not source_name:
                    self.document.reporter.warning(
                        f"tb-code include must use 'PLACEHOLDER: source-name', got {placeholder!r}.",
                        line=node.line,
                    )
                    continue
                if source_name not in code_by_name:
                    self.document.reporter.warning(
                        f"tb-code include could not find named code block {source_name!r}.",
                        line=node.line,
                    )
                    continue
                source = self._replace_placeholder(source, placeholder, code_by_name[source_name])
            node["source"] = source

    def _collect_named_code(self) -> dict[str, str]:
        code_by_name: dict[str, str] = {}
        for node in self.document.findall(nodes.Element):
            if isinstance(node, TbCodeNode):
                self._add_names(code_by_name, node, node.get("source", ""))
            elif isinstance(node, nodes.literal_block):
                self._add_names(code_by_name, node, node.astext())
            elif isinstance(node, nodes.container):
                literal = next((child for child in node.children if isinstance(child, nodes.literal_block)), None)
                if literal is not None:
                    self._add_names(code_by_name, node, literal.astext())
        return code_by_name

    def _add_names(self, code_by_name: dict[str, str], node: nodes.Element, source: str) -> None:
        for name in node.get("names", []):
            code_by_name.setdefault(name, source)

    def _replace_placeholder(self, source: str, placeholder: str, replacement: str) -> str:
        token = f"{{{{{placeholder}}}}}"
        line_pattern = re.compile(rf"(?m)^([ \t]*){re.escape(token)}[ \t]*$")

        def replace_line(match: re.Match[str]) -> str:
            indent = match.group(1)
            return "\n".join(f"{indent}{line}" if line else line for line in replacement.splitlines())

        replaced, count = line_pattern.subn(replace_line, source)
        if count:
            return replaced
        return source.replace(token, replacement)
