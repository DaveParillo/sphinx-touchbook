"""Sphinx transforms for Touchbook directives."""

from __future__ import annotations

import re

from docutils import nodes
from docutils.transforms import Transform
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.errors import ExtensionError

from sphinx_touchbook.nodes import TbCodeNode, TbFileNode


def purge_tb_code_snippets(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    snippets = getattr(env, "tb_code_snippets", {})
    env.tb_code_snippets = {
        name: snippet for name, snippet in snippets.items() if snippet["docname"] != docname
    }


def purge_tb_files(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    files = getattr(env, "tb_files", {})
    env.tb_files = {
        filename: file_info for filename, file_info in files.items() if file_info["docname"] != docname
    }


def collect_tb_code_snippets(app: Sphinx, doctree: nodes.document) -> None:
    env = app.env
    if not hasattr(env, "tb_code_snippets"):
        env.tb_code_snippets = {}
    docname = env.docname
    for node, source in _iter_named_code(doctree):
        for raw_name in node.get("names", []):
            name = nodes.fully_normalize_name(raw_name)
            existing = env.tb_code_snippets.get(name)
            if existing is not None:
                raise ExtensionError(
                    "duplicate tb-code include fragment name "
                    f"{name!r} in {docname!r}; already defined in {existing['docname']!r}"
                )
            env.tb_code_snippets[name] = {
                "docname": docname,
                "source": source,
            }


def collect_tb_files(app: Sphinx, doctree: nodes.document) -> None:
    env = app.env
    if not hasattr(env, "tb_files"):
        env.tb_files = {}
    docname = env.docname
    for node in doctree.findall(TbFileNode):
        filename = node["filename"]
        existing = env.tb_files.get(filename)
        if existing is not None:
            raise ExtensionError(
                "duplicate tb-file filename "
                f"{filename!r} in {docname!r}; already defined in {existing['docname']!r}"
            )
        env.tb_files[filename] = {
            "docname": docname,
            "filename": filename,
            "content": node.get("content", ""),
            "data_url": node.get("data_url"),
            "mime_type": node["mime_type"],
            "is_text": node["is_text"],
            "editable": node["editable"],
        }


def merge_tb_code_snippets(app: Sphinx, env: BuildEnvironment, docnames, other: BuildEnvironment) -> None:
    if not hasattr(env, "tb_code_snippets"):
        env.tb_code_snippets = {}
    for name, snippet in getattr(other, "tb_code_snippets", {}).items():
        existing = env.tb_code_snippets.get(name)
        if existing is not None:
            raise ExtensionError(
                "duplicate tb-code include fragment name "
                f"{name!r} in {snippet['docname']!r}; already defined in {existing['docname']!r}"
            )
        env.tb_code_snippets[name] = snippet


def merge_tb_files(app: Sphinx, env: BuildEnvironment, docnames, other: BuildEnvironment) -> None:
    if not hasattr(env, "tb_files"):
        env.tb_files = {}
    for filename, file_info in getattr(other, "tb_files", {}).items():
        existing = env.tb_files.get(filename)
        if existing is not None:
            raise ExtensionError(
                "duplicate tb-file filename "
                f"{filename!r} in {file_info['docname']!r}; already defined in {existing['docname']!r}"
            )
        env.tb_files[filename] = file_info


def _iter_named_code(doctree: nodes.document):
    for node in doctree.findall(nodes.Element):
        if isinstance(node, TbCodeNode):
            yield node, node.get("source", "")
        elif isinstance(node, nodes.literal_block):
            if node.get("names"):
                yield node, node.astext()
        elif isinstance(node, nodes.container):
            literal = next((child for child in node.children if isinstance(child, nodes.literal_block)), None)
            if literal is not None:
                yield node, literal.astext()


class TbCodeIncludeTransform(Transform):
    """Resolve source and file references inside ``tb-code`` nodes."""

    default_priority = 500

    def apply(self) -> None:
        env = getattr(self.document.settings, "env", None)
        code_by_name = getattr(env, "tb_code_snippets", {}) if env is not None else {}
        file_by_filename = getattr(env, "tb_files", {}) if env is not None else {}
        for node in self.document.findall(TbCodeNode):
            specs = node.get("include_specs", [])
            if specs:
                source = node["source"]
                for placeholder, source_name in specs:
                    if not placeholder or not source_name:
                        self.document.reporter.warning(
                            f"tb-code include must use 'PLACEHOLDER: source-name', got {placeholder!r}.",
                            line=node.line,
                        )
                        continue
                    normalized_source_name = nodes.fully_normalize_name(source_name)
                    if normalized_source_name not in code_by_name:
                        self.document.reporter.warning(
                            f"tb-code include could not find named code block {source_name!r}.",
                            line=node.line,
                        )
                        continue
                    source = self._replace_placeholder(source, placeholder, code_by_name[normalized_source_name]["source"])
                node["source"] = source

            attached_files = []
            for filename in node.get("file_specs", []):
                if filename not in file_by_filename:
                    self.document.reporter.warning(
                        f"tb-code files could not find tb-file filename {filename!r}.",
                        line=node.line,
                    )
                    continue
                file_info = dict(file_by_filename[filename])
                file_info.pop("docname", None)
                attached_files.append(file_info)
            node["files"] = attached_files

    def _replace_placeholder(self, source: str, placeholder: str, replacement: str) -> str:
        token = f"{{{{{placeholder}}}}}"
        line_pattern = re.compile(rf"(?m)^([ \t]*){re.escape(token)}[ \t]*$")

        def replace_line(match: re.Match[str]) -> str:
            indent = match.group(1)
            return "\n".join(f"{indent}{line}" if line else line for line in replacement.splitlines())

        replaced, count = line_pattern.subn(replace_line, source)
        if count:
            return replaced
        return source.replace(token, replacement)
