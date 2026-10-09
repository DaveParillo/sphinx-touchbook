"""Resolve explicit visual positions shared by scene pointers and indicators."""

import re

from sphinx_touchbook.directives.array import KEY, INDEX
from sphinx_touchbook.nodes import TbArrayNode, TbGraphNode


POSITION = re.compile(rf"(?:(slot)\[({INDEX})\]|(item|node)\[({KEY})\]|(begin|end))")


def resolve_target(reference, target, position):
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
    if position["type"] == "node":
        return position["key"]
    return ".end" if position["end"] else graph["nodes"][position["index"]]["key"]
