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

A Touchbook directive for selecting exact regions in literal source text.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

from copy import deepcopy
import re

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import (
    TbClickNode,
    TbClickPromptNode,
    TbClickRegionNode,
    TbClickSourceNode,
)

TEXT_SELECTOR_RE = re.compile(r"^(?P<text>.*)#(?P<ordinal>[1-9]\d*)$")
RANGE_SELECTOR_RE = re.compile(
    r"^(?P<line>[1-9]\d*):(?P<start>[1-9]\d*)-(?P<end>[1-9]\d*)$"
)
DEFAULT_SHOW_HINTS = False
HINTS_NEVER = "never"


class SelectorError(ValueError):
    """Raised when a click selector cannot be resolved."""


def _config(directive):
    env = getattr(directive.state.document.settings, "env", None)
    return getattr(env, "config", None)


def _config_value(config, name: str, default):
    return getattr(config, name, default) if config is not None else default


def _normalize_hints(value) -> str:
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == HINTS_NEVER:
            return HINTS_NEVER
        if normalized in {"1", "true", "yes", "on"}:
            return "true"
        if normalized in {"0", "false", "no", "off", ""}:
            return "false"
    return "true" if bool(value) else "false"


def _line_spans(source: str) -> list[tuple[int, int, str]]:
    spans = []
    offset = 0
    for raw_line in source.splitlines(keepends=True):
        line = raw_line.rstrip("\r\n")
        start = offset
        end = start + len(line)
        spans.append((start, end, line))
        offset += len(raw_line)
    if not spans and source == "":
        spans.append((0, 0, ""))
    return spans


def _parse_selector(selector: str) -> tuple[str, str, int | None]:
    if selector.startswith("text:"):
        kind = "text"
        value = selector[5:]
    elif selector.startswith("line:"):
        kind = "line"
        value = selector[5:]
    elif selector.startswith("range:"):
        kind = "range"
        value = selector[6:]
    else:
        kind = "text"
        value = selector

    if not value:
        raise SelectorError("tb-click selectors must not be empty.")

    ordinal = None
    if kind == "text":
        match = TEXT_SELECTOR_RE.match(value)
        if match:
            value = match.group("text")
            ordinal = int(match.group("ordinal"))
            if not value:
                raise SelectorError("tb-click text selectors must not be empty.")
    return kind, value, ordinal


def resolve_selector(source: str, selector: str) -> tuple[int, int]:
    """Resolve a selector to a zero-based, end-exclusive source range."""

    kind, value, ordinal = _parse_selector(selector.strip())
    if kind == "text":
        return _resolve_text_selector(source, value, ordinal or 1)
    if kind == "line":
        return _resolve_line_selector(source, value)
    if kind == "range":
        return _resolve_range_selector(source, value)
    raise SelectorError(f"Unsupported tb-click selector kind: {kind}")


def _resolve_text_selector(source: str, text: str, ordinal: int) -> tuple[int, int]:
    start = -1
    search_from = 0
    for _ in range(ordinal):
        start = source.find(text, search_from)
        if start < 0:
            raise SelectorError(f"tb-click selector did not match source text: {text!r}")
        search_from = start + len(text)
    return start, start + len(text)


def _resolve_line_selector(source: str, text: str) -> tuple[int, int]:
    for start, end, line in _line_spans(source):
        if text in line:
            return start, end
    raise SelectorError(f"tb-click line selector did not match source text: {text!r}")


def _resolve_range_selector(source: str, value: str) -> tuple[int, int]:
    match = RANGE_SELECTOR_RE.match(value)
    if not match:
        raise SelectorError(
            "tb-click range selectors must use 'range:line:start-end', "
            "for example 'range:3:11-12'."
        )

    line_number = int(match.group("line"))
    start_column = int(match.group("start"))
    end_column = int(match.group("end"))
    if end_column < start_column:
        raise SelectorError("tb-click range selector end column must be after start column.")

    spans = _line_spans(source)
    if line_number > len(spans):
        raise SelectorError(f"tb-click range selector line {line_number} is outside the source block.")

    line_start, line_end, line = spans[line_number - 1]
    if end_column > len(line):
        raise SelectorError(
            f"tb-click range selector column {end_column} is outside line {line_number}."
        )
    return line_start + start_column - 1, line_start + end_column


def _validate_non_overlapping(regions: list[dict[str, object]]) -> None:
    ordered = sorted(regions, key=lambda region: (region["start"], region["end"]))
    previous = None
    for region in ordered:
        if previous is not None and int(region["start"]) < int(previous["end"]):
            raise SelectorError(
                "tb-click selectors must not overlap: "
                f"{previous['selector']!r} overlaps {region['selector']!r}."
            )
        previous = region


class TbClickRegionDirective(Directive):
    """Parse one clickable hit or miss region."""

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    correct = False

    def run(self):
        self.assert_has_content()
        node = TbClickRegionNode()
        node["selector"] = self.arguments[0].strip()
        node["correct"] = self.correct
        self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class TbClickHitDirective(TbClickRegionDirective):
    """Parse a correct clickable region."""

    correct = True


class TbClickMissDirective(TbClickRegionDirective):
    """Parse an incorrect clickable region."""


class TbClickDirective(Directive):
    """Parse a clickable-source assessment."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "name": directives.unchanged_required,
        "show-hints": directives.flag,
    }

    def run(self):
        self.assert_has_content()
        parsed = nodes.container()
        self.state.nested_parse(self.content, self.content_offset, parsed)

        try:
            node = self._build_node(parsed)
        except SelectorError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]

        return [node]

    def _build_node(self, parsed: nodes.container) -> TbClickNode:
        source_index = self._source_index(parsed)
        if source_index is None:
            raise SelectorError("tb-click must contain exactly one code-block or literal block.")

        source_block = parsed.children[source_index]
        if len([child for child in parsed.children if isinstance(child, nodes.literal_block)]) != 1:
            raise SelectorError("tb-click must contain exactly one code-block or literal block.")

        prompt_children = [deepcopy(child) for child in parsed.children[:source_index]]
        region_nodes = self._region_nodes(parsed.children[source_index + 1 :])
        if not region_nodes:
            raise SelectorError("tb-click must contain at least one tb-hit region.")
        if not any(region["correct"] for region in region_nodes):
            raise SelectorError("tb-click must contain at least one tb-hit region.")

        source = source_block.astext()
        regions = []
        for index, region_node in enumerate(region_nodes):
            start, end = resolve_selector(source, region_node["selector"])
            region_node["index"] = index
            region_node["start"] = start
            region_node["end"] = end
            regions.append(
                {
                    "selector": region_node["selector"],
                    "correct": region_node["correct"],
                    "start": start,
                    "end": end,
                    "index": index,
                }
            )
        _validate_non_overlapping(regions)

        node = TbClickNode()
        assign_node_id(self, node)
        node["source"] = source
        node["regions"] = regions
        node["language"] = self._language(source_block)
        config = _config(self)
        node["hints"] = (
            "true"
            if "show-hints" in self.options
            else _normalize_hints(_config_value(config, "tb_click_show_hints", DEFAULT_SHOW_HINTS))
        )

        prompt = TbClickPromptNode()
        prompt.extend(prompt_children)
        node += prompt

        source_node = TbClickSourceNode()
        source_node["source"] = source
        source_node["language"] = node["language"]
        node += source_node

        node.extend(region_nodes)
        return node

    def _source_index(self, parsed: nodes.container) -> int | None:
        for index, child in enumerate(parsed.children):
            if isinstance(child, nodes.literal_block):
                return index
        return None

    def _region_nodes(self, children: list[nodes.Node]) -> list[TbClickRegionNode]:
        regions = []
        for child in children:
            if not isinstance(child, TbClickRegionNode):
                raise SelectorError("tb-click content after the source block must be tb-hit or tb-miss directives.")
            regions.append(child)
        return regions

    def _language(self, source_block: nodes.literal_block) -> str:
        for css_class in source_block.get("classes", []):
            if css_class.startswith("language-"):
                return css_class.removeprefix("language-")
            if css_class.startswith("highlight-"):
                return css_class.removeprefix("highlight-")
        return "none"
