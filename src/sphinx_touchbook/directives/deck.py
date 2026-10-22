"""Parse instructional decks, complete cards, and local references."""

from __future__ import annotations

import re

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.array import KEY, validate_key
from sphinx_touchbook.directives.positions import resolve_target
from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import (
    TbDeckNode, TbCardNode, TbPointerNode, TbArrayNode, TbGraphNode, is_card_object,
)

COMMON_OPTIONS = {
    "name": directives.unchanged_required,
    "class": directives.class_option,
    "caption": directives.unchanged_required,
}

def resolve_position(reference, objects):
    """Resolve an explicit position in this card."""
    if reference == "none":
        return None
    match = re.fullmatch(rf"({KEY})\.(.+)", reference)
    if match is None:
        raise ValueError(f"Invalid position reference {reference!r}; select a node, element, or boundary.")
    key, position = match.groups()
    target = objects.get(key)
    if target is None:
        raise ValueError(f"Unknown card object {key!r} in {reference!r}.")
    return resolve_target(reference, target, position)


def normalize_card(card, document=None):
    objects = {}
    for descendant in card.findall():
        if descendant is card:
            continue
        if isinstance(descendant, (TbDeckNode, TbCardNode)):
            raise ValueError("Cards cannot contain nested cards or decks.")
        if is_card_object(descendant):
            if descendant.parent is not card:
                raise ValueError("Card objects must be immediate children of tb-card.")
            key = descendant["key"]
            if key is None:
                raise ValueError("Arrays and graphs inside a card require an object key.")
            validate_key(key, kind="card object")
            if key in objects:
                raise ValueError(f"Duplicate card object key {key!r}.")
            if not descendant["ids"] and document is not None:
                document.set_id(descendant)
            objects[key] = descendant
    for pointer in (item for item in objects.values() if isinstance(item, TbPointerNode)):
        try:
            pointer["at"] = pointer["at_source"]
            pointer["position"] = resolve_position(pointer["at"], objects)
        except ValueError as error:
            raise ValueError(f"pointer {pointer['key']!r}: {error}") from error


def validate_deck(deck):
    if not deck.children or any(not isinstance(child, TbCardNode) for child in deck.children):
        raise ValueError("tb-deck requires one or more immediate tb-card directives and no other content.")
    types, modes = {}, {}
    for number, card in enumerate(deck.children, 1):
        card["number"] = number
        for item in card.children:
            if not is_card_object(item):
                continue
            key = item["key"]
            if key in types and types[key] is not type(item):
                raise ValueError(f"Card {number}: object {key!r} changes type across cards.")
            types[key] = type(item)
            if isinstance(item, TbArrayNode) and item["elements"]:
                if key in modes and modes[key] != item["mode"]:
                    raise ValueError(f"Card {number}: array {key!r} mixes keyed and unkeyed modes across cards.")
                modes[key] = item["mode"]
    for card in deck.children:
        for item in card.children:
            if isinstance(item, TbArrayNode) and not item["elements"]:
                item["mode"] = modes.get(item["key"], "unkeyed")


class TbCardDirective(Directive):
    has_content = True
    option_spec = COMMON_OPTIONS

    def run(self):
        node = TbCardNode()
        node.source, node.line = self.state.document.current_source, self.lineno
        assign_node_id(self, node)
        node["caption"] = self.options.get("caption", "")
        if isinstance(self.state.parent, TbDeckNode):
            node["number"] = len(self.state.parent.children) + 1
        self.state.nested_parse(self.content, self.content_offset, node)
        if errors := [message for message in node.findall(nodes.system_message) if message["level"] >= 3]:
            return errors
        try:
            normalize_card(node, self.state.document)
        except ValueError as error:
            context = f"card {node['number']}" if "number" in node else "tb-card"
            return [self.state_machine.reporter.error(f"{context}: {error}", line=self.lineno)]
        return [node]


class TbDeckDirective(Directive):
    has_content = True
    option_spec = COMMON_OPTIONS

    def run(self):
        node = TbDeckNode()
        node.source, node.line = self.state.document.current_source, self.lineno
        assign_node_id(self, node)
        node["caption"] = self.options.get("caption", "")
        self.state.nested_parse(self.content, self.content_offset, node)
        if errors := [message for message in node.findall(nodes.system_message) if message["level"] >= 3]:
            return errors
        try:
            validate_deck(node)
        except ValueError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]
        return [node]


class TbPointerDirective(Directive):
    required_arguments = 1
    option_spec = {
        **COMMON_OPTIONS,
        "label": directives.unchanged_required,
        "at": directives.unchanged_required,
    }

    def run(self):
        key = self.arguments[0]
        try:
            validate_key(key, kind="pointer")
            if not isinstance(self.state.parent, TbCardNode):
                raise ValueError("tb-pointer requires an immediate tb-card parent.")
            if "at" not in self.options:
                raise ValueError("tb-pointer requires :at:.")
        except ValueError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]
        node = TbPointerNode()
        node.source, node.line = self.state.document.current_source, self.lineno
        assign_node_id(self, node)
        node.attributes.update(key=key,
                               label=self.options.get("label", key),
                               caption=self.options.get("caption", ""),
                               at_source=self.options["at"])
        return [node]
