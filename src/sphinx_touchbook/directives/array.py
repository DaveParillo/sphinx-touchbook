"""Parse static arrays with positional values or explicit item keys."""

from __future__ import annotations

import re

from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbArrayNode


KEY = r"[A-Za-z_][A-Za-z0-9_-]*"
INDEX = r"(?:0|[1-9][0-9]*)"
NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
ASSIGNMENT = re.compile(rf"({KEY})[ \t]*=[ \t]*")
REFERENCE = re.compile(rf"({KEY})\.(slot|item)\[({INDEX}|{KEY})\]")
SLICE = re.compile(rf"({INDEX}):({INDEX})")


def orientation_option(value):
    return directives.choice(value, ("horizontal", "vertical"))


def validate_key(key: str, *, kind="array") -> None:
    if not re.fullmatch(KEY, key) or key == "null":
        raise ValueError(f"Invalid {kind} key {key!r}; use an identifier other than 'null'.")


def parse_values(source: str) -> list[str]:
    """Decode one physical row, retaining the spelling of numeric values."""
    values = []
    position = 0
    while position < len(source):
        if source[position] in " \t":
            position += 1
            continue
        if source[position] == "#":
            break
        if source[position] in "\"'":
            quote = source[position]
            position += 1
            characters = []
            while position < len(source) and source[position] != quote:
                character = source[position]
                if character == "\\":
                    position += 1
                    if position == len(source) or source[position] not in (quote, "\\", "n"):
                        raise ValueError("Invalid string escape; escape only the enclosing quote, backslash, or 'n' for a newline.")
                    character = "\n" if source[position] == "n" else source[position]
                characters.append(character)
                position += 1
            if position == len(source):
                raise ValueError("Unterminated string; strings must end on the same line.")
            position += 1
            value = "".join(characters)
        else:
            match = NUMBER.match(source, position)
            if match is None:
                raise ValueError("Array values must be numbers or quoted strings.")
            value = match[0]
            position = match.end()
        if position < len(source) and source[position] not in " \t#":
            raise ValueError("Separate array values with whitespace; invalid value or punctuation.")
        values.append(value)
    return values


class TbArrayDirective(Directive):
    """Declare one array without parsing its body as reStructuredText."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        "name": directives.unchanged_required,
        "class": directives.class_option,
        "caption": directives.unchanged_required,
        "label": directives.unchanged_required,
        "highlight": directives.unchanged_required,
        "range": directives.unchanged_required,
        "range-label": directives.unchanged_required,
        "orientation": orientation_option,
        "show-keys": directives.flag,
        "start-index": int,
    }

    def run(self):
        key = self.arguments[0] if self.arguments else None
        elements = []
        mode = None
        seen = set()
        error_line = self.lineno
        try:
            if key is not None:
                validate_key(key)
            for row, source in enumerate(self.content):
                error_line = self.content_offset + row + 1
                source = source.strip(" \t")
                if not source or source.startswith("#"):
                    continue
                assignment = ASSIGNMENT.match(source)
                row_mode = "keyed" if assignment else "unkeyed"
                if mode is not None and mode != row_mode:
                    raise ValueError("Cannot mix keyed and unkeyed array rows.")
                mode = row_mode
                item_key = assignment[1] if assignment else None
                if item_key is not None:
                    validate_key(item_key)
                    if item_key in seen:
                        raise ValueError(f"Duplicate array item key {item_key!r}.")
                    seen.add(item_key)
                values = parse_values(source[assignment.end():] if assignment else source)
                if assignment and len(values) != 1:
                    raise ValueError("A keyed array row requires exactly one value.")
                elements.extend({"key": item_key, "value": value} for value in values)

            error_line = self.lineno
            highlighted = set()
            if "highlight" in self.options:
                if key is None:
                    raise ValueError(":highlight: requires an explicit array object key.")
                for reference in self.options["highlight"].split():
                    match = REFERENCE.fullmatch(reference)
                    if match is None or match[1] != key:
                        raise ValueError(f"Invalid local array highlight reference {reference!r}.")
                    if match[2] == "slot":
                        if not re.fullmatch(INDEX, match[3]):
                            raise ValueError(f"Invalid slot index in {reference!r}.")
                        index = int(match[3])
                        if index >= len(elements):
                            raise ValueError(f"Slot index out of bounds in {reference!r}.")
                    else:
                        if mode != "keyed" or match[3] not in seen:
                            raise ValueError(f"Unknown keyed array item in {reference!r}.")
                        index = next(i for i, item in enumerate(elements) if item["key"] == match[3])
                    highlighted.add(index)

            interval = None
            if "range" in self.options:
                match = SLICE.fullmatch(self.options["range"])
                if match is None:
                    raise ValueError(":range: must be a half-open start:end interval with nonnegative indices.")
                start, end = map(int, match.groups())
                if not 0 <= start <= end <= len(elements):
                    raise ValueError(":range: requires 0 <= start <= end <= array length.")
                interval = [start, end]
            if "range-label" in self.options and interval is None:
                raise ValueError(":range-label: requires :range:.")
        except ValueError as error:
            return [self.state_machine.reporter.error(
                f"tb-array {key or '(anonymous)'!r}: {error}", line=error_line)]

        node = TbArrayNode()
        node.source = self.state.document.current_source
        node.line = self.lineno
        assign_node_id(self, node)
        node.attributes.update({
            "key": key,
            "mode": mode or "unkeyed",
            "elements": elements,
            "highlighted": sorted(highlighted),
            "range": interval,
            "range_label": self.options.get("range-label", ""),
            "label": self.options.get("label", ""),
            "caption": self.options.get("caption", ""),
            "orientation": self.options.get("orientation", "horizontal"),
            "show_keys": "show-keys" in self.options,
            "start_index": self.options.get("start-index", 0),
        })
        return [node]
