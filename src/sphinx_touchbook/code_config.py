"""Validate and resolve tb-code settings without constructing document nodes.

Project settings are normalized once by ``config-inited``. Per-block resolution
also works without Sphinx, using the same defaults and normalization rules.
"""

from __future__ import annotations

import ast
import shlex
from dataclasses import dataclass

from docutils.parsers.rst import directives
from sphinx.directives.code import CodeBlock
from sphinx.errors import ConfigError


DEFAULT_REST_API = "https://delicate-frost-8843.fly.dev/jobe/index.php/restapi"
DEFAULT_ENDPOINT = f"{DEFAULT_REST_API}/runs/"
DEFAULT_LANGUAGES_ENDPOINT = f"{DEFAULT_REST_API}/languages"
DEFAULT_FILES_ENDPOINT = f"{DEFAULT_REST_API}/files/"
DEFAULT_LANGUAGE = "python3"
DEFAULT_RUNNER = "jobe"
BROWSER_LANGUAGES = {"sql", "sqlite", "sqlite3", "javascript", "js", "html", "html5"}
DEFAULT_LANGUAGE_MAP = {
    "python": "python3", "py": "python3", "python3": "python3",
    "cpp": "cpp", "c++": "cpp", "c": "c", "java": "java",
    "js": "nodejs", "javascript": "nodejs", "node": "nodejs",
    "nodejs": "nodejs", "octave": "octave", "pascal": "pascal",
    "php": "php",
}
DEFAULT_LANGUAGE_DEFAULTS: dict[str, dict[str, list[str]]] = {}
DEFAULT_COMPILER_EXPLORER_DEFAULTS: dict[str, dict[str, str]] = {}
DEFAULT_CODE_BLOCK_OPTIONS: dict[str, object] = {}
CODE_BLOCK_OPTION_NAMES = set(CodeBlock.option_spec)
PARAMETER_NAMES = ("compileargs", "linkargs", "runargs", "interpreterargs")
TOOL_FLAGS = ("show-tutor", "show-compiler-explorer")
LABEL_DEFAULTS = {
    "run_label": "Run", "edit_label": "Edit",
    "hide_edit_label": "Hide editor", "revision_label": "Source version",
}


@dataclass
class ResolvedCodeSettings:
    attributes: dict[str, object]
    listing_options: dict[str, object]
    warnings: tuple[str, ...] = ()


def _dictionary(value, location):
    if not isinstance(value, dict):
        raise ValueError(f"{location}: expected a dictionary")
    return value


def _string(value, location, *, nonempty=False):
    if not isinstance(value, str) or (nonempty and not value.strip()):
        kind = "a nonempty string" if nonempty else "a string"
        raise ValueError(f"{location}: expected {kind}")
    return value


def _check_keys(mapping, allowed, location):
    for key in mapping:
        if key not in allowed:
            raise ValueError(f"{location}: unknown setting {key!r}")


def _runner(value, location):
    if value not in ("jobe", "browser"):
        raise ValueError(f"{location}: expected 'jobe' or 'browser'")
    return value


def _argument_list(value, location):
    if value is None:
        return []
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            try:
                return shlex.split(value)
            except ValueError as error:
                raise ValueError(f"{location}: {error}") from error
        if parsed is None or isinstance(parsed, (str, int, float, bool)):
            return [str(parsed)]
        value = parsed
    if not isinstance(value, (list, tuple)) or any(
        not isinstance(item, (str, int, float, bool)) for item in value
    ):
        raise ValueError(
            f"{location}: expected a string or a sequence of arguments"
        )
    return [str(item) for item in value]


def _flag(value, location):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ("", "0", "false", "no", "off"):
            return False
        if value in ("1", "true", "yes", "on"):
            return True
    raise ValueError(f"{location}: expected a boolean flag")


def _listing_options(options, location):
    result = dict(options)
    for name, value in options.items():
        setting = f"{location}[{name!r}]"
        if name in ("linenos", "force", *TOOL_FLAGS):
            # Preserve the existing null-value rules. Tool directive flags use
            # option presence below; listing line numbers also accept None.
            result[name] = (
                (name == "linenos" and value is None) or _flag(value, setting)
            )
        elif name in ("dedent", "lineno-start"):
            if name == "dedent" and value in (None, ""):
                result[name] = None
            elif isinstance(value, bool) or not isinstance(value, (int, str)):
                raise ValueError(f"{setting}: expected an integer")
            else:
                try:
                    result[name] = int(value)
                except ValueError as error:
                    raise ValueError(f"{setting}: expected an integer") from error
        elif name == "class":
            values = value if isinstance(value, (list, tuple)) else [value]
            classes = []
            for item in values:
                classes.extend(directives.class_option(_string(item, setting)))
            result[name] = classes
        else:
            result[name] = _string(value, setting)
    return result


def _profiles(value, location, *, compiler_explorer=False):
    profiles = {}
    for language, profile in _dictionary(value, location).items():
        _string(language, location, nonempty=True)
        setting = f"{location}[{language!r}]"
        profile = _dictionary(profile, setting)
        allowed = (
            {"language", "compiler", "options"}
            if compiler_explorer else PARAMETER_NAMES
        )
        _check_keys(profile, allowed, setting)
        if compiler_explorer:
            normalized = {
                name: _string(item, f"{setting}[{name!r}]", nonempty=name != "options")
                for name, item in profile.items()
            }
        else:
            normalized = {
                name: _argument_list(item, f"{setting}[{name!r}]")
                for name, item in profile.items()
            }
        profiles[language] = normalized
    return profiles


def _normalize_project_config(config):
    def get(name, default):
        return getattr(config, name, default)

    language_map = dict(_dictionary(
        get("tb_code_language_map", DEFAULT_LANGUAGE_MAP), "tb_code_language_map"
    ))
    for alias, language in language_map.items():
        _string(alias, "tb_code_language_map", nonempty=True)
        _string(language, f"tb_code_language_map[{alias!r}]", nonempty=True)
    block_defaults = _dictionary(
        get("tb_code_block_defaults", DEFAULT_CODE_BLOCK_OPTIONS),
        "tb_code_block_defaults",
    )
    _check_keys(block_defaults, CODE_BLOCK_OPTION_NAMES | set(TOOL_FLAGS),
                "tb_code_block_defaults")
    validate_language = get("tb_code_validate_language", True)
    if not isinstance(validate_language, bool):
        raise ValueError("tb_code_validate_language: expected a boolean")
    settings = {
        "default_runner": _runner(
            get("tb_code_default_runner", DEFAULT_RUNNER), "tb_code_default_runner"
        ),
        "language_map": language_map,
        "language_defaults": _profiles(
            get("tb_code_language_defaults", DEFAULT_LANGUAGE_DEFAULTS),
            "tb_code_language_defaults",
        ),
        "compiler_explorer_defaults": _profiles(
            get("tb_code_compiler_explorer_defaults",
                DEFAULT_COMPILER_EXPLORER_DEFAULTS),
            "tb_code_compiler_explorer_defaults", compiler_explorer=True,
        ),
        "block_defaults": _listing_options(block_defaults, "tb_code_block_defaults"),
        "default_language": _string(
            get("tb_code_default_language", DEFAULT_LANGUAGE),
            "tb_code_default_language", nonempty=True,
        ),
        "validate_language": validate_language,
    }
    for name, config_name, default in (
        ("endpoint", "tb_code_default_endpoint", DEFAULT_ENDPOINT),
        ("files_endpoint", "tb_code_files_endpoint", DEFAULT_FILES_ENDPOINT),
        ("languages_endpoint", "tb_code_languages_endpoint",
         DEFAULT_LANGUAGES_ENDPOINT),
    ):
        settings[name] = _string(get(config_name, default), config_name)
    for name, default in LABEL_DEFAULTS.items():
        config_name = f"tb_code_{name}"
        settings[name] = _string(get(config_name, default), config_name)
    return settings


def configure_code(app, config):
    """Validate once, before reading documents, without rewriting public config."""
    try:
        config._tb_code_settings = _normalize_project_config(config)
    except ValueError as error:
        raise ConfigError(str(error)) from error


def _language_profile(profiles, language, jobe_language):
    # Preserve whole-profile precedence: an alias entry replaces, rather than
    # merges with, the mapped language entry. An empty alias profile is explicit.
    if language in profiles:
        return profiles[language]
    return profiles.get(jobe_language, {})


def resolve_code_settings(config, options, arguments=()):
    """Apply explicit block options over the selected project defaults.

    Language: :language: > positional argument > project default.
    Profiles: author-facing language > mapped JOBE language (whole entry).
    Listings and execution arguments: explicit option > project/profile value.
    Tool flags enable a tool; otherwise its project default applies.
    """
    project = getattr(config, "_tb_code_settings", None)
    if project is None:
        project = _normalize_project_config(config)
    language = options.get("language") or (arguments[0] if arguments else None)
    language = language or project["default_language"]
    runner = _runner(options.get("runner", project["default_runner"]),
                     "tb-code :runner:")
    if runner == "browser" and language.lower() not in BROWSER_LANGUAGES:
        raise ValueError(f"tb-code: the browser runner does not support {language!r}")
    jobe_language = project["language_map"].get(language, language)
    profile = _language_profile(project["language_defaults"], language, jobe_language)
    listing = {key: value for key, value in project["block_defaults"].items()
               if key in CODE_BLOCK_OPTION_NAMES}
    if "class" in listing:
        listing["class"] = list(listing["class"])
    explicit_listing = {key: value for key, value in options.items()
                        if key in CODE_BLOCK_OPTION_NAMES}
    listing.update(_listing_options(explicit_listing, "tb-code"))
    attributes = {
        "runner": runner,
        "language": language, "jobe_language": jobe_language,
        "endpoint": options.get("endpoint") or project["endpoint"],
        "files_endpoint": options.get("files-endpoint") or project["files_endpoint"],
        "languages_endpoint": project["languages_endpoint"],
        "validate_language": project["validate_language"],
        "readonly": "readonly" in options, "hidden": "hidden" in options,
        "parameters": {
            name: (_argument_list(options[name], f"tb-code option {name!r}")
                   if name in options else list(profile.get(name, [])))
            for name in PARAMETER_NAMES
        },
    }
    for name in TOOL_FLAGS:
        attributes[name.replace("-", "_")] = (
            name in options or bool(project["block_defaults"].get(name, False))
        )
    for name in LABEL_DEFAULTS:
        attributes[name] = options.get(name.replace("_", "-")) or project[name]
    if "stdin" in options:
        attributes["stdin"] = options["stdin"]
    attributes["compiler_explorer"] = None
    warnings = ()
    if attributes.pop("show_compiler_explorer") and not attributes["hidden"]:
        ce_profile = _language_profile(
            project["compiler_explorer_defaults"], language, jobe_language
        )
        if not ce_profile.get("language") or not ce_profile.get("compiler"):
            warnings = (
                "tb-code :show-compiler-explorer: needs a language and compiler in "
                "tb_code_compiler_explorer_defaults",
            )
        else:
            attributes["compiler_explorer"] = dict(ce_profile)
    return ResolvedCodeSettings(attributes, listing, warnings)
