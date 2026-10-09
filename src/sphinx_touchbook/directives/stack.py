"""Parse instructional stacks, complete scenes, and local references."""

from __future__ import annotations

import re

from docutils import nodes
from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.array import KEY, validate_key
from sphinx_touchbook.directives.positions import resolve_target
from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import (
    TbStackNode, TbSceneNode, TbPointerNode, TbArrayNode, TbGraphNode, is_scene_object,
)

COMMON_OPTIONS = {
    "name": directives.unchanged_required,
    "class": directives.class_option,
    "caption": directives.unchanged_required,
}

def resolve_position(reference, objects):
    """Resolve an explicit position in this scene."""
    if reference == "none":
        return None
    match = re.fullmatch(rf"({KEY})\.(.+)", reference)
    if match is None:
        raise ValueError(f"Invalid position reference {reference!r}; select a node, element, or boundary.")
    key, position = match.groups()
    target = objects.get(key)
    if target is None:
        raise ValueError(f"Unknown scene object {key!r} in {reference!r}.")
    return resolve_target(reference, target, position)


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
            pointer["at"] = pointer["at_source"]
            pointer["position"] = resolve_position(pointer["at"], objects)
        except ValueError as error:
            raise ValueError(f"pointer {pointer['key']!r}: {error}") from error


def validate_stack(stack):
    if not stack.children or any(not isinstance(child, TbSceneNode) for child in stack.children):
        raise ValueError("tb-stack requires one or more immediate tb-scene directives and no other content.")
    types, modes = {}, {}
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
        "label": directives.unchanged_required,
        "at": directives.unchanged_required,
    }

    def run(self):
        key = self.arguments[0]
        try:
            validate_key(key, kind="pointer")
            if not isinstance(self.state.parent, TbSceneNode):
                raise ValueError("tb-pointer requires an immediate tb-scene parent.")
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
