"""Parse instructional stacks, complete scenes, and local references."""

from __future__ import annotations

import re

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.array import KEY, INDEX, validate_key
from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import (
    TbStackNode, TbSceneNode, TbPointerNode, TbArrayNode, TbGraphNode, is_scene_object,
)

COMMON_OPTIONS = {
    "name": directives.unchanged_required,
    "class": directives.class_option,
    "caption": directives.unchanged_required,
}
POSITION = re.compile(rf"({KEY})\.(?:(slot)\[({INDEX})\]|(item|node)\[({KEY})\]|(begin|end))")


def resolve_position(reference, objects, *, bound=False):
    """Resolve a typed reference against this scene, never another state."""
    if re.fullmatch(KEY, reference):
        if bound:
            raise ValueError("Array bounds require .begin, .end, or .slot[index] references.")
        validate_key(reference, kind="target")
        target = objects.get(reference)
        if target is None:
            raise ValueError(f"Unknown scene object {reference!r}.")
        return {"type": "object", "object": reference, "reference": reference,
                "target_id": target["ids"][0], "label": target.get("label") or reference}
    match = POSITION.fullmatch(reference)
    if not match:
        raise ValueError(f"Invalid position reference {reference!r}.")
    key, slot, index, entity, item_key, boundary = match.groups()
    target = objects.get(key)
    if target is None:
        raise ValueError(f"Unknown scene object {key!r} in {reference!r}.")
    if entity == "node":
        if bound or not isinstance(target, TbGraphNode):
            raise ValueError(f"Node reference {reference!r} requires a graph, not an array bound.")
        item = next((item for item in target["nodes"] if item["key"] == item_key), None)
        if item is None:
            raise ValueError(f"Unknown graph node in {reference!r}.")
        return {"type": "node", "object": key, "key": item_key,
                "value": "" if item["invisible"] else item["value"],
                "invisible": item["invisible"], "reference": reference}
    if not isinstance(target, TbArrayNode):
        raise ValueError(f"Array reference {reference!r} requires an array.")
    length = len(target["elements"])
    if entity == "item":
        if bound or target["mode"] != "keyed":
            raise ValueError(f"Item reference {reference!r} requires a keyed array and cannot be a bound.")
        index = next((i for i, item in enumerate(target["elements"]) if item["key"] == item_key), None)
        if index is None:
            raise ValueError(f"Unknown array item in {reference!r}.")
    elif slot:
        index = int(index)
        if index >= length:
            raise ValueError(f"Slot index out of bounds in {reference!r}; use {key}.end for the end boundary.")
    else:
        index = length if boundary == "end" else 0
    return {"type": "array", "object": key, "index": index,
            "display_index": index + target["start_index"], "end": index == length,
            "value": target["elements"][index]["value"] if index < length else "",
            "reference": reference}


def resolve_range(value, objects):
    if value == "null":
        return None
    if re.fullmatch(KEY, value):
        validate_key(value)
        bounds = [f"{value}.begin", f"{value}.end"]
    else:
        bounds = [part.strip() for part in value.split(",")]
        if len(bounds) != 2:
            raise ValueError(":range: requires an array key, two array bounds, or null.")
    start, end = [resolve_position(bound, objects, bound=True) for bound in bounds]
    if start["object"] != end["object"] or start["index"] > end["index"]:
        raise ValueError(":range: requires ordered bounds in the same array.")
    return {"object": start["object"], "start": start["index"],
            "end": end["index"], "begin_reference": bounds[0]}


def normalize_scene(scene, document=None):
    objects = {}
    for descendant in scene.findall():
        if descendant is scene:
            continue
        if isinstance(descendant, (TbStackNode, TbSceneNode)):
            raise ValueError("Scenes cannot contain nested scenes or stacks.")
        if is_scene_object(descendant):
            if descendant.parent is not scene:
                raise ValueError("Scene objects must be immediate children of tb-scene.")
            key = descendant["key"]
            if key is None:
                raise ValueError("Arrays and graphs inside a scene require an object key.")
            validate_key(key, kind="scene object")
            if key in objects:
                raise ValueError(f"Duplicate scene object key {key!r}.")
            if not descendant["ids"] and document is not None:
                document.set_id(descendant)
            objects[key] = descendant
    for pointer in (item for item in objects.values() if isinstance(item, TbPointerNode)):
        try:
            interval = resolve_range(pointer["range_source"], objects) if pointer["range_source"] is not None else None
            at = pointer["at_source"]
            if at is None:
                at = interval["begin_reference"] if interval else "null"
            position = None if at == "null" else resolve_position(at, objects)
            if pointer["kind"] == "iterator":
                if interval is None or position is None:
                    raise ValueError("Iterators require a non-null array range and position.")
                if (position["type"] != "array" or position["object"] != interval["object"]
                        or not interval["start"] <= position["index"] <= interval["end"]):
                    raise ValueError("Iterator position is outside its declared range.")
            pointer["position"] = position
            pointer["range"] = interval
            pointer["at"] = at
        except ValueError as error:
            raise ValueError(f"pointer {pointer['key']!r}: {error}") from error


def validate_stack(stack):
    if not stack.children or any(not isinstance(child, TbSceneNode) for child in stack.children):
        raise ValueError("tb-stack requires one or more immediate tb-scene directives and no other content.")
    types, modes, kinds = {}, {}, {}
    for number, scene in enumerate(stack.children, 1):
        scene["number"] = number
        for item in scene.children:
            if not is_scene_object(item):
                continue
            key = item["key"]
            if key in types and types[key] is not type(item):
                raise ValueError(f"Scene {number}: object {key!r} changes type across scenes.")
            types[key] = type(item)
            if isinstance(item, TbArrayNode) and item["elements"]:
                if key in modes and modes[key] != item["mode"]:
                    raise ValueError(f"Scene {number}: array {key!r} mixes keyed and unkeyed modes across scenes.")
                modes[key] = item["mode"]
            if isinstance(item, TbPointerNode):
                if key in kinds and kinds[key] != item["kind"]:
                    raise ValueError(f"Scene {number}: pointer {key!r} changes kind across scenes.")
                kinds[key] = item["kind"]
    for scene in stack.children:
        for item in scene.children:
            if isinstance(item, TbArrayNode) and not item["elements"]:
                item["mode"] = modes.get(item["key"], "unkeyed")


class TbSceneDirective(Directive):
    has_content = True
    option_spec = COMMON_OPTIONS

    def run(self):
        node = TbSceneNode()
        node.source, node.line = self.state.document.current_source, self.lineno
        assign_node_id(self, node)
        node["caption"] = self.options.get("caption", "")
        if isinstance(self.state.parent, TbStackNode):
            node["number"] = len(self.state.parent.children) + 1
        self.state.nested_parse(self.content, self.content_offset, node)
        if errors := [message for message in node.findall(nodes.system_message) if message["level"] >= 3]:
            return errors
        try:
            normalize_scene(node, self.state.document)
        except ValueError as error:
            context = f"scene {node['number']}" if "number" in node else "tb-scene"
            return [self.state_machine.reporter.error(f"{context}: {error}", line=self.lineno)]
        return [node]


class TbStackDirective(Directive):
    has_content = True
    option_spec = COMMON_OPTIONS

    def run(self):
        node = TbStackNode()
        node.source, node.line = self.state.document.current_source, self.lineno
        assign_node_id(self, node)
        node["caption"] = self.options.get("caption", "")
        self.state.nested_parse(self.content, self.content_offset, node)
        if errors := [message for message in node.findall(nodes.system_message) if message["level"] >= 3]:
            return errors
        try:
            validate_stack(node)
        except ValueError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]
        return [node]


class TbPointerDirective(Directive):
    required_arguments = 1
    option_spec = {
        **COMMON_OPTIONS,
        "kind": lambda value: directives.choice(value, ("pointer", "iterator")),
        "label": directives.unchanged_required,
        "range": directives.unchanged_required,
        "at": directives.unchanged_required,
    }

    def run(self):
        key = self.arguments[0]
        try:
            validate_key(key, kind="pointer")
            if not isinstance(self.state.parent, TbSceneNode):
                raise ValueError("tb-pointer requires an immediate tb-scene parent.")
            if "at" not in self.options and "range" not in self.options:
                raise ValueError("tb-pointer requires :at: or :range:.")
            if self.options.get("kind") == "iterator" and "range" not in self.options:
                raise ValueError("Iterators require :range:.")
        except ValueError as error:
            return [self.state_machine.reporter.error(str(error), line=self.lineno)]
        node = TbPointerNode()
        node.source, node.line = self.state.document.current_source, self.lineno
        assign_node_id(self, node)
        node.attributes.update(key=key, kind=self.options.get("kind", "pointer"),
                               label=self.options.get("label", key),
                               caption=self.options.get("caption", ""),
                               at_source=self.options.get("at"), range_source=self.options.get("range"))
        return [node]
