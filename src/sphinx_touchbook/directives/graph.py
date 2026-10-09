"""Parse Touchbook's node-and-edge language into a complete graph."""

from __future__ import annotations

import re
import math

from docutils.parsers.rst import Directive, directives
from sphinx.ext.graphviz import align_spec

from sphinx_touchbook.directives.array import KEY, NUMBER, validate_key
from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.directives.positions import resolve_target, graph_indicator_target
from sphinx_touchbook.nodes import TbGraphNode
from sphinx_touchbook.graph_styles import resolve_graph_styles


IDENTIFIER = re.compile(KEY)
EDGE = re.compile(rf"[ \t]+(?:->|-({KEY})->)[ \t]+")
INVISIBLE = "{invisible}"
NODE_REFERENCE = re.compile(rf"({KEY})\.node\[({KEY})\]")
INDICATOR = re.compile(rf"({KEY})=(\S+)")


OVERLAY_SHAPES = ("ellipse", "circle", "rectangle", "box")
OVERLAY_LAYERS = ("background", "foreground")


def overlay_padding(value):
    padding = float(value)
    if not math.isfinite(padding) or not 0 <= padding <= 1000:
        raise ValueError("Overlay padding must be a finite number from 0 to 1000 points.")
    return padding


def overlay_shape(value):
    shape = directives.choice(value, OVERLAY_SHAPES)
    return "rectangle" if shape == "box" else shape


def overlay_layer(value):
    return directives.choice(value, OVERLAY_LAYERS)


def parse_overlays(options, graph_key, graph_nodes):
    """One target group per option line, with defaults and local overrides."""
    if "overlay" not in options:
        if any(option in options for option in ("overlay-shape", "overlay-layer", "overlay-padding")):
            raise ValueError(":overlay-shape:, :overlay-layer:, and :overlay-padding: require :overlay:.")
        return []
    by_key = {item["key"]: item for item in graph_nodes}
    converters = {":overlay-shape:": overlay_shape,
                  ":overlay-layer:": overlay_layer,
                  ":overlay-padding:": overlay_padding}
    defaults = {"shape": options.get("overlay-shape", "ellipse"),
                "layer": options.get("overlay-layer", "foreground"),
                "padding": options.get("overlay-padding", 8)}
    overlays = []
    for number, line in enumerate(options["overlay"].splitlines(), 1):
        try:
            tokens = line.split()
            if not tokens:
                continue
            targets, overrides = [], {}
            position = 0
            while position < len(tokens):
                token = tokens[position]
                if token.startswith(":"):
                    if token not in converters:
                        raise ValueError(f"Unknown overlay setting {token!r}.")
                    if token in overrides:
                        raise ValueError(f"Duplicate overlay setting {token!r}.")
                    if position + 1 == len(tokens):
                        raise ValueError(f"Missing value for overlay setting {token!r}.")
                    overrides[token] = converters[token](tokens[position + 1])
                    position += 2
                    continue
                if overrides:
                    raise ValueError("Overlay target keys must precede settings.")
                if match := NODE_REFERENCE.fullmatch(token):
                    if match[1] != graph_key:
                        raise ValueError(f"Invalid local overlay reference {token!r}.")
                    target = match[2]
                else:
                    if not IDENTIFIER.fullmatch(token):
                        raise ValueError(f"Invalid overlay target {token!r}.")
                    validate_key(token, kind="graph")
                    target = token
                if target not in by_key:
                    raise ValueError(f"Unknown overlay target {token!r}.")
                if by_key[target]["invisible"]:
                    raise ValueError(f"Overlay target {token!r} is invisible.")
                if target not in targets:
                    targets.append(target)
                position += 1
            if not targets:
                raise ValueError("An overlay requires at least one node key.")
            overlays.append({**defaults, "targets": targets,
                             **{option.strip(":").removeprefix("overlay-"): value
                                for option, value in overrides.items()}})
        except ValueError as error:
            raise ValueError(f"overlay {number}: {error}") from error
    if not overlays:
        raise ValueError(":overlay: requires at least one node key.")
    return overlays


class GraphSyntaxError(ValueError):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line


class GraphParser:
    """A line scanner that recognizes punctuation only outside quoted values."""

    def __init__(self):
        self.declarations = {}
        self.references = []
        self.edges = []
        self.relationships = set()
        self.pairs = {}
        self.line = 1

    def fail(self, message):
        raise GraphSyntaxError(message, self.line)

    def key(self, source, position):
        match = IDENTIFIER.match(source, position)
        if match is None:
            self.fail("Expected a node key.")
        try:
            validate_key(match[0], kind="graph")
        except ValueError as error:
            self.fail(str(error))
        return match[0], match.end()

    def value(self, source, position):
        if position < len(source) and source[position] in "\"'":
            quote = source[position]
            position += 1
            result = []
            while position < len(source) and source[position] != quote:
                character = source[position]
                if character == "\\":
                    position += 1
                    if position == len(source) or source[position] not in (quote, "\\"):
                        self.fail("Invalid string escape; escape only the enclosing quote or backslash.")
                    character = source[position]
                result.append(character)
                position += 1
            if position == len(source):
                self.fail("Unterminated string; labels must end on the same line.")
            return "".join(result), position + 1
        match = NUMBER.match(source, position)
        if match is None:
            self.fail("Node labels must be numbers or quoted strings.")
        return match[0], match.end()

    def term(self, source, position):
        key, position = self.key(source, position)
        self.references.append((key, self.line))
        declared = position < len(source) and source[position] == "["
        if declared:
            position += 1
            position += len(source[position:]) - len(source[position:].lstrip(" \t"))
            value, position = self.value(source, position)
            position += len(source[position:]) - len(source[position:].lstrip(" \t"))
            if position == len(source) or source[position] != "]":
                self.fail("Expected ']' after the node label.")
            position += 1
            modifier = re.match(r"[ \t]+\{invisible\}", source[position:])
            invisible = modifier is not None
            if modifier:
                position += modifier.end()
            if key in self.declarations:
                self.fail(f"Duplicate node declaration {key!r}.")
            self.declarations[key] = {"key": key, "value": value, "invisible": invisible}
        return key, position, declared

    def statement(self, source):
        source = source.strip(" \t")
        if not source or source.startswith("#"):
            return
        source_key, position, declared = self.term(source, 0)
        has_edge = False
        while source[position:].strip(" \t") and not source[position:].lstrip(" \t").startswith("#"):
            match = EDGE.match(source, position)
            if match is None:
                self.fail("Expected an edge operator with whitespace on both sides.")
            relationship = match[1]
            if relationship is not None:
                try:
                    validate_key(relationship, kind="graph")
                except ValueError as error:
                    self.fail(str(error))
            position = match.end()
            invisible = source.startswith(INVISIBLE, position)
            if invisible:
                position += len(INVISIBLE)
                whitespace = re.match(r"[ \t]+", source[position:])
                if whitespace is None:
                    self.fail("Separate an invisible edge modifier from its destination with whitespace.")
                position += whitespace.end()
            target_key, position, _ = self.term(source, position)
            pair = (source_key, target_key)
            if relationship is not None:
                identity = (source_key, relationship)
                if identity in self.relationships:
                    self.fail(f"Duplicate relationship {relationship!r} on node {source_key!r}.")
                self.relationships.add(identity)
            if pair in self.pairs and (relationship is None or None in self.pairs[pair]):
                self.fail(f"Duplicate or ambiguous parallel edge {source_key!r} -> {target_key!r}.")
            self.pairs.setdefault(pair, []).append(relationship)
            self.edges.append({"source": source_key, "target": target_key,
                               "relationship": relationship, "invisible": invisible})
            source_key = target_key
            has_edge = True
        if not declared and not has_edge:
            self.fail("A standalone node requires a value declaration.")

    def parse(self, content):
        for self.line, source in enumerate(content, start=1):
            self.statement(source)
        for key, line in self.references:
            if key not in self.declarations:
                raise GraphSyntaxError(f"Node {key!r} has no value declaration in this graph.", line)
        return list(self.declarations.values()), self.edges


class TbGraphDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        "alt": directives.unchanged,
        "align": align_spec,
        "name": directives.unchanged_required,
        "class": directives.class_option,
        "caption": directives.unchanged_required,
        "label": directives.unchanged_required,
        "highlight": directives.unchanged_required,
        "style": directives.unchanged_required,
        "description": directives.unchanged_required,
        "show-indices": directives.flag,
        "indicators": directives.unchanged_required,
        "overlay": directives.unchanged_required,
        "overlay-shape": overlay_shape,
        "overlay-layer": overlay_layer,
        "overlay-padding": overlay_padding,
    }

    def run(self):
        key = self.arguments[0] if self.arguments else None
        error_line = self.lineno
        try:
            if key is not None:
                validate_key(key, kind="graph")
            env = getattr(self.state.document.settings, "env", None)
            styles = resolve_graph_styles(env.config.tb_graph_styles if env else {})
            style_name = self.options.get("style", "graph")
            if style_name not in styles:
                raise ValueError(f"Unknown graph style {style_name!r}; choose from {', '.join(styles)}.")
            graph_nodes, edges = GraphParser().parse(self.content)
            highlighted = set()
            keys = {item["key"] for item in graph_nodes}
            annotations = parse_overlays(self.options, key, graph_nodes)
            if "highlight" in self.options:
                if key is None:
                    raise ValueError(":highlight: requires an explicit graph object key.")
                for reference in self.options["highlight"].split():
                    match = NODE_REFERENCE.fullmatch(reference)
                    if match is None or match[1] != key:
                        raise ValueError(f"Invalid local graph highlight reference {reference!r}.")
                    if match[2] not in keys:
                        raise ValueError(f"Unknown graph node in {reference!r}.")
                    highlighted.add(match[2])
            indicators = []
            if "indicators" in self.options:
                indicator_keys = set()
                target_graph = TbGraphNode(key=key, nodes=graph_nodes, style=styles[style_name])
                for definition in self.options["indicators"].split():
                    match = INDICATOR.fullmatch(definition)
                    if match is None:
                        raise ValueError(f"Invalid indicator {definition!r}; use label=position.")
                    label, reference = match.groups()
                    validate_key(label, kind="indicator")
                    if label in indicator_keys:
                        raise ValueError(f"Duplicate indicator label {label!r}.")
                    if reference == "none":
                        position = None
                    else:
                        if IDENTIFIER.fullmatch(reference):
                            validate_key(reference, kind="graph")
                            if reference not in keys:
                                raise ValueError(f"Unknown indicator target {reference!r}.")
                            local = f"node[{reference}]"
                        elif reference.startswith("."):
                            local = reference[1:]
                        elif key and reference.startswith(key + "."):
                            local = reference[len(key) + 1:]
                        else:
                            raise ValueError(f"Invalid local indicator reference {reference!r}.")
                        position = resolve_target(reference, target_graph, local)
                    target = graph_indicator_target(position, target_graph)
                    indicators.append({"key": label, "target": target})
                    indicator_keys.add(label)
        except ValueError as error:
            if isinstance(error, GraphSyntaxError):
                error_line = self.content_offset + error.line
            return [self.state_machine.reporter.error(
                f"tb-graph {key or '(anonymous)'!r}: {error}", line=error_line)]
        node = TbGraphNode()
        node.source = self.state.document.current_source
        node.line = self.lineno
        assign_node_id(self, node)
        node.attributes.update({
            "key": key, "nodes": graph_nodes, "edges": edges,
            "highlighted": sorted(highlighted),
            "label": self.options.get("label", ""),
            "caption": self.options.get("caption", ""),
            "style_name": style_name, "style": styles[style_name],
            "description": self.options.get("description", ""),
            "show_indices": "show-indices" in self.options,
            "indicators": indicators,
            "annotations": annotations,
        })
        for option in ("alt", "align"):
            if option in self.options:
                node[option] = self.options[option]
        return [node]
