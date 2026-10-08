"""Render complete scenes and navigation configuration for every builder."""

from html import escape
import json

from docutils import nodes

from sphinx_touchbook.generators.common import html_additional_targets, html_class_attr, latex_targets
from sphinx_touchbook.nodes import TbArrayNode, TbGraphNode, TbPointerNode, TbSceneNode, is_scene_object


# Bootstrap Icons (MIT); license in static/bootstrap-icons-LICENSE.txt.
# https://icons.getbootstrap.com/icons/chevron-double-left/ and related chevrons.
NAVIGATION_ICONS = (
    ("first", "chevron-double-left", "First scene", (
        "M8.354 1.646a.5.5 0 0 1 0 .708L2.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0",
        "M12.354 1.646a.5.5 0 0 1 0 .708L6.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0",
    )),
    ("previous", "chevron-left", "Previous scene", (
        "M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0",
    )),
    ("next", "chevron-right", "Next scene", (
        "M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708",
    )),
    ("last", "chevron-double-right", "Last scene", (
        "M3.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L9.293 8 3.646 2.354a.5.5 0 0 1 0-.708",
        "M7.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L13.293 8 7.646 2.354a.5.5 0 0 1 0-.708",
    )),
)


def pointers_for(node, *, position_type=None):
    if not isinstance(node.parent, TbSceneNode):
        return []
    return [item for item in node.parent.children if isinstance(item, TbPointerNode)
            and item["position"] is not None and item["position"]["object"] == node["key"]
            and (position_type is None or item["position"]["type"] == position_type)]


def graph_pointer_indicators(node):
    return node.get("indicators", []) + [
        {"key": pointer["label"], "target": pointer["position"]["key"]}
        for pointer in pointers_for(node, position_type="node")
    ]


def scene_model(scene):
    fields = {
        TbArrayNode: ("elements", "mode", "highlighted", "range", "range_label",
                      "label", "orientation", "start_index", "show_keys"),
        TbGraphNode: ("nodes", "edges", "highlighted", "style", "style_name",
                      "label", "description", "show_indices", "indicators", "annotations"),
        TbPointerNode: ("kind", "label", "position", "range", "at"),
    }
    objects = []
    for item in scene.children:
        if not is_scene_object(item):
            continue
        objects.append({"type": {TbArrayNode: "array", TbGraphNode: "graph", TbPointerNode: "pointer"}.get(type(item), "object"),
                        "key": item["key"], "dom_id": item["ids"][0],
                        "caption": item.get("caption", ""), "classes": item["classes"],
                        **{key: item[key] for key in fields.get(type(item), ())}})
    return {"id": scene["ids"][0], "caption": scene["caption"], "objects": objects}


def pointer_description(pointer):
    position = pointer["position"]
    label = pointer["label"]
    if position is None:
        return f"{label} is null."
    target = position["object"]
    if position["type"] == "object":
        return f"{label} points to scene object {target}."
    if position["type"] == "node":
        if position["invisible"]:
            return f"{label} points to an undisplayed node in {target}."
        return f"{label} points to {target} node {position['key']}, value {position['value']!r}."
    if position["end"]:
        return f"{label} is at {target}.end, past the last element (index {position['display_index']})."
    if pointer["kind"] == "iterator" and position["index"] == pointer["range"]["end"]:
        return f"{label} is at the end of its range in {target} (index {position['display_index']})."
    return f"{label} points to {target} at index {position['display_index']}, value {position['value']!r}."


def pointer_html(pointer, *, placed=False, vertical=False):
    direction = "left" if vertical else "down"
    attrs = (f' id="{escape(pointer["ids"][0], quote=True)}"{html_class_attr(pointer)}'
             f' data-key="{escape(pointer["key"], quote=True)}"'
             f' data-at="{escape(pointer["at"], quote=True)}"')
    parts = [f'<tb-pointer{attrs}>', html_additional_targets(pointer)]
    if placed:
        arrow = "&#8592;" if vertical else "&#8595;"
        parts.append(f'<span class="tb-pointer__marker tb-pointer__marker--{direction}" aria-hidden="true">'
                     f'<span class="tb-pointer__label">{escape(pointer["label"])}</span>'
                     f'<span class="tb-pointer__arrow">{arrow}</span></span>')
    position = pointer["position"]
    object_target = position is not None and position["type"] == "object"
    if object_target:
        parts.append(f'<span class="tb-pointer__object-link">{escape(pointer["label"])} '
                     '<span aria-hidden="true">&#8594;</span> '
                     f'<a href="#{escape(position["target_id"], quote=True)}">{escape(position["label"])}</a></span>')
    css_class = "tb-pointer__description tb-pointer__description--placed" if placed or object_target else "tb-pointer__description"
    parts.append(f'<span class="{css_class}">{escape(pointer_description(pointer))}</span>')
    if pointer["caption"]:
        parts.append(f'<span class="tb-pointer__caption">{escape(pointer["caption"])}</span>')
    parts.append('</tb-pointer>')
    return "".join(parts)


def visit_tb_pointer_html(self, node):
    # Array tables render their pointer roots in the corresponding positions.
    if node["position"] is None or node["position"]["type"] != "array":
        self.body.append(pointer_html(node) + "\n")
    raise nodes.SkipNode


def visit_tb_pointer_latex(self, node):
    latex_targets(self, node)
    content = nodes.container()
    content += nodes.paragraph(text=pointer_description(node))
    if node["caption"]:
        content += nodes.paragraph(text=node["caption"])
    content.walkabout(self)
    raise nodes.SkipNode


def visit_tb_pointer_text(self, node):
    self.add_text(pointer_description(node) + "\n")
    if node["caption"]:
        self.add_text(node["caption"] + "\n")
    raise nodes.SkipNode


def visit_tb_stack_html(self, node):
    self.body.append(f'<tb-stack id="{escape(node["ids"][0], quote=True)}"{html_class_attr(node)}>\n')
    self.body.append(html_additional_targets(node))
    if node["caption"]:
        self.body.append(f'<p class="tb-stack__caption">{escape(node["caption"])}</p>\n')
    self.body.append('<div class="tb-stack__controls" hidden>\n')
    self.body.append('<p class="tb-stack__scene-caption" hidden></p>\n')
    self.body.append('<div class="tb-stack__navigation">\n')
    for action, icon, label, paths in NAVIGATION_ICONS:
        self.body.append(f'<button type="button" data-action="{action}" aria-label="{label}" title="{label}">'
                         f'<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
                         f'viewBox="0 0 16 16" fill="currentColor" class="bi bi-{icon}" '
                         'aria-hidden="true" focusable="false">')
        self.body.extend(f'<path fill-rule="evenodd" d="{path}"/>' for path in paths)
        self.body.append('</svg></button>\n')
    self.body.append('<p class="tb-stack__status" role="status" aria-live="polite" aria-atomic="true"></p>\n')
    self.body.append('</div>\n</div>\n')
    self.body.append('<div class="tb-stack__scenes">\n')


def depart_tb_stack_html(self, node):
    self.body.append('</div>\n')
    config = {"version": 1, "scenes": [scene_model(scene) for scene in node.children]}
    encoded = json.dumps(config, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    self.body.append(f'<script type="application/json">{encoded}</script>\n')
    self.body.append('</tb-stack>\n')


def scene_heading(node):
    heading = f"Scene {node['number']}" if "number" in node else "Scene"
    return f"{heading}: {node['caption']}" if node["caption"] else heading


def visit_tb_scene_html(self, node):
    self.body.append(f'<tb-scene id="{escape(node["ids"][0], quote=True)}"{html_class_attr(node)}>\n')
    self.body.append(html_additional_targets(node))
    self.body.append(f'<p class="tb-scene__caption">{escape(scene_heading(node))}</p>\n')


def depart_tb_scene_html(self, node):
    self.body.append('</tb-scene>\n')


def visit_tb_stack_latex(self, node):
    latex_targets(self, node)
    if node["caption"]:
        content = nodes.container()
        content += nodes.paragraph(text=node["caption"])
        content.walkabout(self)


def visit_tb_scene_latex(self, node):
    latex_targets(self, node)
    content = nodes.container()
    content += nodes.paragraph('', '', nodes.strong(text=scene_heading(node)))
    content.walkabout(self)


def visit_tb_stack_text(self, node):
    if node["caption"]:
        self.add_text(node["caption"] + "\n")


def visit_tb_scene_text(self, node):
    self.add_text("\n" + scene_heading(node) + "\n")


def depart_static(self, node):
    pass
