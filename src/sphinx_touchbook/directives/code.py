"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
Copyright (C) 2026 Dave Parillo.

A Touchbook directive to execute code in a web page.

In HTML, readers can run code through Jobe or in the browser and optionally
edit the source before running it again.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""



from __future__ import annotations

from docutils.parsers.rst import Directive, directives
from sphinx.directives.code import CodeBlock, dedent_lines, parse_line_num_spec

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.directives.file import validate_filename
from sphinx_touchbook.nodes import TbCodeNode

# Re-export defaults for existing imports from this module.
from sphinx_touchbook.code_config import (
    DEFAULT_REST_API, DEFAULT_ENDPOINT, DEFAULT_LANGUAGES_ENDPOINT,
    DEFAULT_FILES_ENDPOINT, DEFAULT_LANGUAGE, DEFAULT_LANGUAGE_MAP,
    DEFAULT_LANGUAGE_DEFAULTS, DEFAULT_COMPILER_EXPLORER_DEFAULTS,
    DEFAULT_CODE_BLOCK_OPTIONS, resolve_code_settings,
)


def _parse_include_specs(value: str | None) -> list[tuple[str, str]]:
    if not value:
        return []
    specs = []
    for line in value.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            specs.append((stripped, ""))
            continue
        placeholder, source_name = stripped.split(":", 1)
        specs.append((placeholder.strip(), source_name.strip()))
    return specs


def _parse_file_specs(value: str | None) -> list[str]:
    if not value:
        return []
    filenames = []
    for line in value.splitlines():
        for raw_filename in line.replace(",", " ").split():
            filenames.append(validate_filename(raw_filename))
    return filenames


def _parse_run_fragment_names(value: str | None) -> list[str]:
    if not value:
        return []
    names = []
    for line in value.splitlines():
        for raw_name in line.split(","):
            name = raw_name.strip()
            if name:
                names.append(name)
    return names


def _prepare_listing(
    directive, source: str, options: dict[str, object]
) -> tuple[str, dict[str, object]]:
    """Apply source-dependent Sphinx listing options after settings resolution."""
    normalized: dict[str, object] = {
        "classes": list(options.get("class", [])),
        "force": options.get("force", False),
        "linenos": options.get("linenos", False) or "lineno-start" in options,
        "highlight_args": {},
    }

    if "dedent" in options:
        dedent = options["dedent"]
        lines = source.splitlines(True)
        location = directive.state_machine.get_source_and_line(directive.lineno)
        source = "".join(dedent_lines(lines, dedent, location=location))

    if "emphasize-lines" in options:
        linespec = str(options["emphasize-lines"])
        try:
            nlines = len(source.splitlines())
            hl_lines = parse_line_num_spec(linespec, nlines)
            normalized["highlight_args"]["hl_lines"] = [
                line + 1 for line in hl_lines if line < nlines
            ]
        except ValueError as err:
            directive.state.document.reporter.warning(err, line=directive.lineno)

    if "lineno-start" in options:
        normalized["highlight_args"]["linenostart"] = options["lineno-start"]

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
        "runner": directives.unchanged,
        "endpoint": directives.uri,
        "files-endpoint": directives.uri,
        "stdin": directives.unchanged,
        "compileargs": directives.unchanged,
        "linkargs": directives.unchanged,
        "runargs": directives.unchanged,
        "interpreterargs": directives.unchanged,
        "readonly": directives.flag,
        "hidden": directives.flag,
        "show-tutor": directives.flag,
        "show-compiler-explorer": directives.flag,
        "run-label": directives.unchanged,
        "edit-label": directives.unchanged,
        "hide-edit-label": directives.unchanged,
        "revision-label": directives.unchanged,
        "include": directives.unchanged,
        "run-before": directives.unchanged,
        "run-after": directives.unchanged,
        "files": directives.unchanged,
    }

    def run(self):
        self.assert_has_content()
        node = TbCodeNode()
        assign_node_id(self, node)
        env = getattr(self.state.document.settings, "env", None)
        config = getattr(env, "config", None)
        try:
            settings = resolve_code_settings(config, self.options, self.arguments)
        except ValueError as error:
            raise self.error(str(error)) from error
        node.attributes.update(settings.attributes)
        for warning in settings.warnings:
            self.state.document.reporter.warning(warning, line=self.lineno)
        code_block_options = settings.listing_options
        source, normalized_code_block_options = _prepare_listing(
            self,
            "\n".join(self.content),
            code_block_options,
        )
        node["source"] = source
        node["include_specs"] = _parse_include_specs(self.options.get("include"))
        node["run_before_names"] = _parse_run_fragment_names(self.options.get("run-before"))
        node["run_after_names"] = _parse_run_fragment_names(self.options.get("run-after"))
        node["run_before"] = []
        node["run_after"] = []
        node["file_specs"] = _parse_file_specs(self.options.get("files"))
        node["files"] = []
        node["caption"] = code_block_options.get("caption")
        node["code_block_options"] = normalized_code_block_options
        return [node]
