"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
Copyright (C) 2026 Dave Parillo.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
---

A Touchbook directive to run video content in HTML pages.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""




from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from docutils.parsers.rst import Directive, directives

from sphinx_touchbook.directives.common import assign_node_id
from sphinx_touchbook.nodes import TbVideoNode

DEFAULT_WIDTH = "560"
DEFAULT_HEIGHT = "315"
VIDEO_EXTENSIONS = {".mp4", ".ogg", ".ogm", ".ogv", ".webm", ".mov"}
YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
    "music.youtube.com",
}
VIMEO_HOSTS = {"vimeo.com", "www.vimeo.com", "player.vimeo.com"}


def _config(directive: Directive) -> dict[str, str]:
    env = getattr(directive.state.document.settings, "env", None)
    config = getattr(env, "config", None) if env is not None else None
    return {
        "width": str(getattr(config, "tb_video_default_width", DEFAULT_WIDTH)),
        "height": str(getattr(config, "tb_video_default_height", DEFAULT_HEIGHT)),
    }


def _seconds(value: str) -> int | None:
    candidate = value.strip()
    if not candidate:
        return None
    if candidate.isdigit():
        return int(candidate)
    match = re.fullmatch(
        r"(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?",
        candidate,
    )
    if not match:
        return None
    total = 0
    if match.group("hours"):
        total += int(match.group("hours")) * 3600
    if match.group("minutes"):
        total += int(match.group("minutes")) * 60
    if match.group("seconds"):
        total += int(match.group("seconds"))
    return total


def _youtube_video_id(parsed, query: dict[str, list[str]]) -> str | None:
    if parsed.netloc in {"youtu.be", "www.youtu.be"}:
        return parsed.path.strip("/") or None
    elif "youtube" in parsed.netloc:
        if parsed.path.startswith("/watch"):
            return query.get("v", [None])[0]
        else:
            parts = [part for part in parsed.path.split("/") if part]
            if "embed" in parts:
                index = parts.index("embed")
                if index + 1 < len(parts):
                    return parts[index + 1]
            elif "shorts" in parts:
                index = parts.index("shorts")
                if index + 1 < len(parts):
                    return parts[index + 1]
    return None


def _youtube_watch_url(parsed, query: dict[str, list[str]]) -> str | None:
    video_id = _youtube_video_id(parsed, query)
    if not video_id:
        return None

    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    params: dict[str, str] = {}
    start = query.get("start", [None])[0] or query.get("t", [None])[0]
    if start:
        seconds = _seconds(start)
        if seconds is not None and seconds > 0:
            params["t"] = f"{seconds}s"
    if params:
        return f"{watch_url}&{urlencode(params)}"
    return watch_url


def _youtube_embed_url(parsed, query: dict[str, list[str]]) -> str | None:
    video_id = _youtube_video_id(parsed, query)
    if not video_id:
        return None

    embed_url = f"https://www.youtube.com/embed/{video_id}"
    params: dict[str, str] = {}
    start = query.get("start", [None])[0] or query.get("t", [None])[0]
    if start:
        seconds = _seconds(start)
        if seconds is not None and seconds > 0:
            params["start"] = str(seconds)
    if params:
        return f"{embed_url}?{urlencode(params)}"
    return embed_url


def _youtube_thumbnail_url(parsed, query: dict[str, list[str]]) -> str | None:
    video_id = _youtube_video_id(parsed, query)
    if not video_id:
        return None
    return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"


def _vimeo_embed_url(parsed) -> str | None:
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None
    if parts[0] == "video" and len(parts) > 1:
        video_id = parts[1]
    else:
        video_id = parts[-1]
    if not video_id.isdigit():
        return None
    return f"https://player.vimeo.com/video/{video_id}"


def _vimeo_thumbnail_url(parsed) -> str | None:
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None
    if parts[0] == "video" and len(parts) > 1:
        video_id = parts[1]
    else:
        video_id = parts[-1]
    if not video_id.isdigit():
        return None
    return f"https://vumbnail.com/{video_id}.jpg"


def _odysee_embed_url(parsed) -> str:
    if parsed.path.startswith("/$/embed/"):
        return urlunparse(parsed)
    return urlunparse(parsed._replace(path=f"/$/embed{parsed.path}"))


def _local_video(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"", "file", "http", "https"}:
        return False
    path = Path(parsed.path)
    return path.suffix.lower() in VIDEO_EXTENSIONS


def _resolve_source(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    host = parsed.netloc.lower()

    if host in YOUTUBE_HOSTS or "youtube.com" in host:
        watch_url = _youtube_watch_url(parsed, query)
        embed_url = _youtube_embed_url(parsed, query)
        if watch_url and embed_url:
            return {
                "provider": "youtube",
                "kind": "iframe",
                "source_url": watch_url,
                "embed_url": embed_url,
                "thumbnail_url": _youtube_thumbnail_url(parsed, query),
            }
    if host in VIMEO_HOSTS or "vimeo.com" in host:
        embed_url = _vimeo_embed_url(parsed)
        if embed_url:
            return {
                "provider": "vimeo",
                "kind": "iframe",
                "embed_url": embed_url,
                "thumbnail_url": _vimeo_thumbnail_url(parsed),
            }
    if "odysee.com" in host:
        return {"provider": "odysee", "kind": "iframe", "embed_url": _odysee_embed_url(parsed), "thumbnail_url": None}
    if "canvas" in host or "instructure.com" in host:
        return {"provider": "canvas", "kind": "iframe", "embed_url": url, "thumbnail_url": None}
    if _local_video(url):
        return {"provider": "local", "kind": "video", "embed_url": url, "thumbnail_url": None}
    return {"provider": "generic", "kind": "iframe", "embed_url": url, "thumbnail_url": None}


class TbVideoDirective(Directive):
    """Parse a video reference and optional notes into a semantic node."""

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "name": directives.unchanged_required,
        "width": directives.length_or_percentage_or_unitless,
        "height": directives.length_or_percentage_or_unitless,
        "thumbnail": directives.uri,
        "window": directives.flag,
    }

    def run(self):
        source_url = self.arguments[0].strip()
        if not source_url:
            raise self.error("tb-video requires a video URL.")

        node = TbVideoNode()
        assign_node_id(self, node)

        defaults = _config(self)
        resolved = _resolve_source(source_url)
        node["source_url"] = resolved.get("source_url", source_url)
        node["provider"] = resolved["provider"]
        node["kind"] = resolved["kind"]
        node["embed_url"] = resolved["embed_url"]
        node["thumbnail_url"] = self.options.get("thumbnail", resolved.get("thumbnail_url"))
        node["window"] = "window" in self.options
        node["width"] = self.options.get("width", defaults["width"])
        node["height"] = self.options.get("height", defaults["height"])
        node["has_width"] = "width" in self.options
        node["has_height"] = "height" in self.options
        node["has_notes"] = any(line.strip() for line in self.content)

        if node["has_notes"]:
            self.state.nested_parse(self.content, self.content_offset, node)

        return [node]
