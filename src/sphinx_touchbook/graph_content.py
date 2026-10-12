"""Validated graph-node content and concrete scalar/cell target identities."""

import json
import math
import re


CELL_TARGET = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*)\.slot\[(0|[1-9][0-9]*)\]")


def scalar_text(value):
    return value if isinstance(value, str) else str(value)


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate structured node field {key!r}.")
        result[key] = value
    return result


def parse_content(source, position):
    """Decode one strict JSON array-content object, leaving edges to the parser."""
    def invalid_constant(value):
        raise ValueError(f"Non-finite JSON number {value!r} is not supported.")

    decoder = json.JSONDecoder(object_pairs_hook=unique_fields,
                               parse_constant=invalid_constant)
    try:
        content, end = decoder.raw_decode(source, position)
    except RecursionError as error:
        raise ValueError("Structured node JSON is nested too deeply.") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid structured node JSON: {error.msg}.") from error
    if not isinstance(content, dict) or set(content) != {"type", "values"}:
        raise ValueError("Structured nodes require exactly 'type' and 'values'.")
    if content["type"] != "array":
        raise ValueError("Structured node type must be 'array'.")
    values = content["values"]
    if not isinstance(values, list):
        raise ValueError("Structured array 'values' must be a JSON array.")
    for value in values:
        if type(value) not in (str, int, float):
            raise ValueError("Structured array values must be numbers or strings; nested arrays and objects are unsupported.")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("Structured array numbers must be finite.")
        if isinstance(value, str) and any(
                (ord(character) < 32 and character not in "\n\r\t")
                or 0xD800 <= ord(character) <= 0xDFFF for character in value):
            raise ValueError("Structured array strings contain unsupported control characters.")
    return content, end


def cell_key(key, index):
    return f"{key}.slot[{index}]"


def target_owner(target):
    match = CELL_TARGET.fullmatch(target)
    return match[1] if match else target


def concrete_targets(items):
    """Expand content into annotation targets; array containers are not targets."""
    result = {}
    for item in items:
        content = item.get("content")
        if content:
            for index, value in enumerate(content["values"]):
                result[cell_key(item["key"], index)] = {
                    "key": item["key"], "index": index,
                    "value": scalar_text(value), "invisible": item["invisible"],
                }
        else:
            result[item["key"]] = item
    return result


def target_label(target, items):
    item = concrete_targets(items)[target]
    if "index" in item:
        value = f'“{item["value"]}”' if item["value"] else "an unused cell"
        return f'{value} (node {item["key"]}, cell {item["index"]})'
    return f'“{item["value"]}” (node {target})'


def graph_statements(content):
    """Join multiline JSON objects without changing scalar line syntax."""
    pending, depth, quote, escaped = [], 0, None, False
    first = 1
    for number, line in enumerate(content, 1):
        if not pending:
            first = number
        pending.append(line)
        for character in line:
            if quote:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    quote = None
            elif character in "\"'":
                quote = character
            elif character == "#" and depth == 0:
                break
            elif character == "{":
                depth += 1
            elif character == "}" and depth:
                depth -= 1
        if depth == 0:
            yield first, "\n".join(pending)
            pending, quote, escaped = [], None, False
    if pending:
        yield first, "\n".join(pending)
