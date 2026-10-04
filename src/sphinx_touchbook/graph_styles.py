"""Semantic graph presentation presets, shared by directive normalization."""

from __future__ import annotations

import math
import re

from sphinx.errors import ConfigError


GRAPH_STYLE = {
    "layout": "graph", "orientation": "vertical", "shape": "ellipse",
    "fill": None, "highlight-fill": None, "unused-fill": None,
    "font": "sans-serif", "font-size": 14,
    "connectors": "curved", "arrows": "normal", "relationship-labels": True,
    "node-spacing": .25, "level-spacing": .5,
}
DEFAULT_GRAPH_STYLES = {
    "graph": GRAPH_STYLE,
    "list": {**GRAPH_STYLE, "layout": "list", "orientation": "horizontal",
             "shape": "box", "fill": "#add8e6", "connectors": "straight",
             "arrows": "vee", "relationship-labels": False},
    "tree": {**GRAPH_STYLE, "layout": "tree", "shape": "circle",
             "fill": "#add8e6", "connectors": "straight", "arrows": "none",
             "relationship-labels": False, "level-spacing": .3},
    "array": {**GRAPH_STYLE, "layout": "array", "orientation": "horizontal",
              "shape": "box", "relationship-labels": False, "unused-fill": "#eeeeee"},
    "ring": {**GRAPH_STYLE, "layout": "ring", "relationship-labels": False},
}
CHOICES = {
    "orientation": ("horizontal", "vertical"),
    "shape": ("box", "rectangle", "circle", "ellipse"),
    "connectors": ("straight", "curved"),
    "arrows": ("normal", "vee", "none"),
}


def resolve_graph_styles(overrides):
    """Merge named styles with built-ins; reject unknown presentation settings."""
    if not isinstance(overrides, dict):
        raise ValueError("tb_graph_styles must be a dictionary of named styles.")
    styles = {name: dict(style) for name, style in DEFAULT_GRAPH_STYLES.items()}
    # Resolve built-in overrides first so custom styles inherit book defaults.
    names = sorted(overrides, key=lambda name: name not in DEFAULT_GRAPH_STYLES)
    for name in names:
        options = overrides[name]
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", name):
            raise ValueError(f"Invalid tb_graph_styles name {name!r}.")
        if not isinstance(options, dict):
            raise ValueError(f"tb_graph_styles[{name!r}] must be a dictionary.")
        base = options.get("base", name if name in DEFAULT_GRAPH_STYLES else "graph")
        if not isinstance(base, str) or base not in DEFAULT_GRAPH_STYLES:
            raise ValueError(f"Style {name!r}: base must be one of {', '.join(DEFAULT_GRAPH_STYLES)}.")
        style = dict(DEFAULT_GRAPH_STYLES[base] if name in DEFAULT_GRAPH_STYLES else styles[base])
        for option, value in options.items():
            if option == "base":
                continue
            if option not in GRAPH_STYLE or option == "layout":
                raise ValueError(f"Style {name!r}: unknown setting {option!r}.")
            valid = True
            if option in CHOICES:
                valid = value in CHOICES[option]
            elif option in ("font-size", "node-spacing", "level-spacing"):
                valid = (isinstance(value, (int, float)) and not isinstance(value, bool)
                         and math.isfinite(value) and value > 0)
            elif option == "relationship-labels":
                valid = isinstance(value, bool)
            elif option in ("fill", "highlight-fill", "unused-fill"):
                valid = value is None or (isinstance(value, str) and re.fullmatch(
                    r"#[0-9a-fA-F]{6}|[A-Za-z][A-Za-z0-9]*", value))
            elif option == "font":
                valid = isinstance(value, str) and bool(value.strip()) and not any(
                    ord(character) < 32 for character in value)
            if not valid:
                raise ValueError(f"Style {name!r}: invalid {option} value {value!r}.")
            style[option] = value
        styles[name] = style
    return styles


def configure_graph_styles(app, config):
    try:
        resolve_graph_styles(config.tb_graph_styles)
    except ValueError as error:
        raise ConfigError(str(error)) from error
