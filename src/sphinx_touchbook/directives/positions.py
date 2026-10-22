"""Resolve explicit visual positions shared by card pointers and indicators."""

import re

from sphinx_touchbook.directives.array import KEY, INDEX
from sphinx_touchbook.nodes import TbArrayNode, TbGraphNode
from sphinx_touchbook.graph_content import scalar_text, cell_key


CELL_POSITION = re.compile(rf"node\[({KEY})\]\.slot\[({INDEX})\]")

POSITION = re.compile(rf"(?:(slot)\[({INDEX})\]|(item|node)\[({KEY})\]|(begin|end))")


def resolve_target(reference, target, position):
    if cell := CELL_POSITION.fullmatch(position):
        if not isinstance(target, TbGraphNode):
            raise ValueError(f"Cell reference {reference!r} requires a graph.")
        item = next((item for item in target["nodes"] if item["key"] == cell[1]), None)
        if item is None or "content" not in item:
            raise ValueError(f"Cell reference {reference!r} requires an array-content node.")
        index = int(cell[2])
        values = item["content"]["values"]
        if index >= len(values):
            raise ValueError(f"Cell index out of bounds in {reference!r}.")
        return {"type": "cell", "object": target["key"], "key": cell[1],
                "index": index, "value": "" if item["invisible"] else scalar_text(values[index]),
                "invisible": item["invisible"], "reference": reference}
    match = POSITION.fullmatch(position)
    if match is None:
        raise ValueError(f"Invalid position reference {reference!r}.")
    slot, index, entity, item_key, boundary = match.groups()
    graph = isinstance(target, TbGraphNode)
    array = isinstance(target, TbArrayNode) or (graph and target["style"]["layout"] == "array")
    if entity == "node":
        if not graph:
            raise ValueError(f"Node reference {reference!r} requires a graph.")
        item = next((item for item in target["nodes"] if item["key"] == item_key), None)
        if item is None:
            raise ValueError(f"Unknown graph node in {reference!r}.")
        if "content" in item:
            raise ValueError(f"Array node reference {reference!r} requires .slot[index]; select a concrete cell.")
        return {"type": "node", "object": target["key"], "key": item_key,
                "value": "" if item["invisible"] else item["value"],
                "invisible": item["invisible"], "reference": reference}
    if not array:
        raise ValueError(f"Array reference {reference!r} requires an array or array-style graph.")
    items = target["nodes"] if graph else target["elements"]
    length = len(items)
    if entity == "item":
        if graph or target["mode"] != "keyed":
            raise ValueError(f"Item reference {reference!r} requires a keyed array.")
        index = next((i for i, item in enumerate(items) if item["key"] == item_key), None)
        if index is None:
            raise ValueError(f"Unknown array item in {reference!r}.")
    elif slot:
        index = int(index)
        if index >= length:
            raise ValueError(f"Slot index out of bounds in {reference!r}; use .end for the end boundary.")
    else:
        index = length if boundary == "end" else 0
    invisible = graph and index < length and items[index]["invisible"]
    return {"type": "array", "object": target["key"], "index": index,
            "display_index": index + target.get("start_index", 0), "end": index == length,
            "value": items[index]["value"] if index < length and not invisible else "",
            "invisible": invisible,
            "reference": reference}


def graph_indicator_target(position, graph):
    """Use node keys for real cells and a distinct token for the end boundary."""
    if position is None:
        return None
    if position["type"] == "cell":
        return cell_key(position["key"], position["index"])
    if position["type"] == "node":
        return position["key"]
    return ".end" if position["end"] else graph["nodes"][position["index"]]["key"]
