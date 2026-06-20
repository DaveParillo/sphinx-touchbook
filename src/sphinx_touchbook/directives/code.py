"""The ``tb-code`` directive."""

from __future__ import annotations

import ast
import shlex

from docutils.parsers.rst import Directive, directives
from sphinx.directives.code import CodeBlock, dedent_lines, parse_line_num_spec

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbCodeNode

DEFAULT_REST_API = "https://delicate-frost-8843.fly.dev/jobe/index.php/restapi"
DEFAULT_ENDPOINT = f"{DEFAULT_REST_API}/runs/"
DEFAULT_LANGUAGES_ENDPOINT = f"{DEFAULT_REST_API}/languages"
DEFAULT_LANGUAGE = "python3"
DEFAULT_LANGUAGE_MAP = {
    "python": "python3",
    "py": "python3",
    "python3": "python3",
    "cpp": "cpp",
    "c++": "cpp",
    "c": "c",
    "java": "java",
    "js": "nodejs",
    "javascript": "nodejs",
    "node": "nodejs",
    "nodejs": "nodejs",
    "octave": "octave",
    "pascal": "pascal",
    "php": "php",
}
DEFAULT_LANGUAGE_DEFAULTS: dict[str, dict[str, list[str]]] = {}
DEFAULT_CODE_BLOCK_OPTIONS: dict[str, object] = {}
CODE_BLOCK_OPTION_NAMES = set(CodeBlock.option_spec)


def _config(directive):
    env = getattr(directive.state.document.settings, "env", None)
    return getattr(env, "config", None)


def _config_value(config, name: str, default):
    return getattr(config, name, default) if config is not None else default


def _as_arg_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            parsed = ast.literal_eval(stripped)
        except (SyntaxError, ValueError):
            return shlex.split(stripped)
        if isinstance(parsed, (list, tuple)):
            return [str(item) for item in parsed]
        if isinstance(parsed, str):
            return [parsed]
        return [str(parsed)]
    return [str(value)]


def _language_defaults(config, language: str, jobe_language: str) -> dict[str, object]:
    defaults = _config_value(config, "tb_code_language_defaults", DEFAULT_LANGUAGE_DEFAULTS)
    if language in defaults:
        return defaults[language]
    return defaults.get(jobe_language, {})


def _code_block_defaults(config) -> dict[str, object]:
    defaults = _config_value(config, "tb_code_code_block_defaults", DEFAULT_CODE_BLOCK_OPTIONS)
    return {key: value for key, value in dict(defaults).items() if key in CODE_BLOCK_OPTION_NAMES}


def _merged_code_block_options(config, options: dict[str, object]) -> dict[str, object]:
    merged = _code_block_defaults(config)
    for name in CODE_BLOCK_OPTION_NAMES:
        if name in options:
            merged[name] = options[name]
    return merged


def _as_bool_flag(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "off"}
    return bool(value)


def _as_class_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return directives.class_option(value)
    if isinstance(value, (list, tuple)):
        classes: list[str] = []
        for item in value:
            classes.extend(directives.class_option(str(item)))
        return classes
    return directives.class_option(str(value))


def _as_optional_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _as_int(value: object) -> int:
    return int(value)


def _normalize_code_block_options(directive, source: str, options: dict[str, object]) -> tuple[str, dict[str, object]]:
    normalized: dict[str, object] = {
        "classes": _as_class_list(options.get("class")),
        "force": _as_bool_flag(options.get("force")),
        "linenos": _as_bool_flag(options.get("linenos")) or "lineno-start" in options,
        "highlight_args": {},
    }

    if "dedent" in options:
        dedent = _as_optional_int(options.get("dedent"))
        lines = source.splitlines(True)
        source = "".join(dedent_lines(lines, dedent, location=directive.state_machine.get_source_and_line(directive.lineno)))

    if "emphasize-lines" in options:
        linespec = str(options["emphasize-lines"])
        try:
            nlines = len(source.splitlines())
            hl_lines = parse_line_num_spec(linespec, nlines)
            normalized["highlight_args"]["hl_lines"] = [line + 1 for line in hl_lines if line < nlines]
        except ValueError as err:
            directive.state.document.reporter.warning(err, line=directive.lineno)

    if "lineno-start" in options:
        normalized["highlight_args"]["linenostart"] = _as_int(options["lineno-start"])

    return source, normalized


class TbCodeDirective(Directive):
    """Parse runnable source code into a semantic node."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        **CodeBlock.option_spec,
        "language": directives.unchanged,
        "endpoint": directives.uri,
        "stdin": directives.unchanged,
        "compileargs": directives.unchanged,
        "linkargs": directives.unchanged,
        "runargs": directives.unchanged,
        "interpreterargs": directives.unchanged,
        "editable": directives.flag,
        "readonly": directives.flag,
        "run-label": directives.unchanged,
        "edit-label": directives.unchanged,
        "hide-edit-label": directives.unchanged,
        "revision-label": directives.unchanged,
    }

    def run(self):
        self.assert_has_content()
        node = TbCodeNode()
        assign_node_id(self, node)
        language = self.options.get("language") or (self.arguments[0] if self.arguments else None)
        config = _config(self)
        node["language_map"] = dict(_config_value(config, "tb_code_language_map", DEFAULT_LANGUAGE_MAP))
        node["language"] = language or _config_value(config, "tb_code_default_language", DEFAULT_LANGUAGE)
        node["jobe_language"] = node["language_map"].get(node["language"], node["language"])
        language_defaults = _language_defaults(config, node["language"], node["jobe_language"])
        code_block_options = _merged_code_block_options(config, self.options)
        source, normalized_code_block_options = _normalize_code_block_options(
            self,
            "\n".join(self.content),
            code_block_options,
        )
        node["source"] = source
        node["caption"] = code_block_options.get("caption")
        node["code_block_options"] = normalized_code_block_options
        node["endpoint"] = self.options.get("endpoint") or _config_value(
            config,
            "tb_code_default_endpoint",
            DEFAULT_ENDPOINT,
        )
        node["languages_endpoint"] = _config_value(
            config,
            "tb_code_languages_endpoint",
            DEFAULT_LANGUAGES_ENDPOINT,
        )
        node["validate_language"] = _config_value(config, "tb_code_validate_language", True)
        node["stdin"] = self.options.get("stdin", "")
        node["parameters"] = {}
        for name in ("compileargs", "linkargs", "runargs", "interpreterargs"):
            value = self.options[name] if name in self.options else language_defaults.get(name)
            node["parameters"][name] = _as_arg_list(value)
        node["editable"] = "readonly" not in self.options
        if "editable" in self.options:
            node["editable"] = True
        node["run_label"] = self.options.get("run-label") or _config_value(config, "tb_code_run_label", "Run")
        node["edit_label"] = self.options.get("edit-label") or _config_value(config, "tb_code_edit_label", "Edit")
        node["hide_edit_label"] = self.options.get("hide-edit-label") or _config_value(
            config,
            "tb_code_hide_edit_label",
            "Hide editor",
        )
        node["revision_label"] = self.options.get("revision-label") or _config_value(
            config,
            "tb_code_revision_label",
            "Editor revision",
        )
        return [node]
