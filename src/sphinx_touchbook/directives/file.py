"""The ``tb-file`` directive."""

from __future__ import annotations

import base64
import mimetypes
import re
from pathlib import Path

from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbFileNode

FILENAME_PATTERN = re.compile(r"^[A-Za-z0-9._/-]+$")
IMAGE_MIME_TYPES = {"image/gif", "image/jpeg", "image/png", "image/svg+xml", "image/webp"}
TEXT_MIME_PREFIXES = ("text/",)
TEXT_MIME_TYPES = {
    "application/json",
    "application/javascript",
    "application/xml",
    "image/svg+xml",
}


def validate_filename(value: str) -> str:
    filename = value.strip()
    if not filename:
        raise ValueError("tb-file filename must not be empty")
    if not FILENAME_PATTERN.fullmatch(filename):
        raise ValueError("tb-file filename may contain only letters, numbers, dots, underscores, hyphens, and slashes")
    if filename.startswith("/"):
        raise ValueError("tb-file filename must be relative")
    parts = filename.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("tb-file filename must not contain empty, current, or parent directory segments")
    return filename


def validate_source_reference(raw_path: str) -> str:
    candidate = Path(raw_path)
    if raw_path.startswith("./") or candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError("tb-file source file references must be relative paths without current or parent segments")
    return raw_path


def _source_path(directive: Directive, raw_path: str) -> Path:
    try:
        validate_source_reference(raw_path)
    except ValueError as err:
        raise directive.error(str(err)) from err
    env = getattr(directive.state.document.settings, "env", None)
    source, _line = directive.state_machine.get_source_and_line(directive.lineno)
    base = Path(source).parent
    if env is not None:
        env.note_dependency(raw_path)
    return (base / raw_path).resolve()


def _mime_type(filename: str, source_path: Path | None) -> str:
    guessed, _encoding = mimetypes.guess_type(str(source_path or filename))
    return guessed or "text/plain"


def _is_text_mime(mime_type: str) -> bool:
    return mime_type.startswith(TEXT_MIME_PREFIXES) or mime_type in TEXT_MIME_TYPES


class TbFileDirective(Directive):
    """Parse a simulated local file into a semantic node."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "filename": validate_filename,
        "name": directives.unchanged,
        "hidden": directives.flag,
        "editable": directives.flag,
        "readonly": directives.flag,
        "encoding": directives.encoding,
    }

    def run(self):
        if "filename" not in self.options:
            raise self.error('tb-file requires a "filename" option.')

        node = TbFileNode()
        assign_node_id(self, node)
        node["filename"] = self.options["filename"]
        node["hidden"] = "hidden" in self.options
        node["source_path"] = None
        node["mime_type"] = _mime_type(node["filename"], None)
        node["content"] = ""
        node["data_url"] = None
        node["is_text"] = True
        node["editable"] = "readonly" not in self.options
        if "editable" in self.options:
            node["editable"] = True

        if self.arguments:
            path = _source_path(self, self.arguments[0])
            if not path.exists():
                raise self.error(f"tb-file source file {self.arguments[0]!r} does not exist.")
            node["source_path"] = str(path)
            node["mime_type"] = _mime_type(node["filename"], path)
            if node["mime_type"] in IMAGE_MIME_TYPES:
                data = path.read_bytes()
                node["data_url"] = f"data:{node['mime_type']};base64,{base64.b64encode(data).decode('ascii')}"
                node["is_text"] = False
                node["editable"] = False
            elif _is_text_mime(node["mime_type"]):
                encoding = self.options.get("encoding", "utf-8")
                node["content"] = path.read_text(encoding=encoding)
                node["is_text"] = True
            else:
                data = path.read_bytes()
                node["data_url"] = f"data:{node['mime_type']};base64,{base64.b64encode(data).decode('ascii')}"
                node["is_text"] = False
                node["editable"] = False
        else:
            self.assert_has_content()
            node["content"] = "\n".join(self.content)

        return [node]
