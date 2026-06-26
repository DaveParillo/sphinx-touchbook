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

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

import json
import posixpath
import re
from html import escape

"""Builder generators for ``tb-video``."""

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.nodes import TbVideoNode


def _node_id(node: TbVideoNode) -> str:
    return node["ids"][0]


def _unitless_number(value: str) -> bool:
    return bool(re.fullmatch(r"\d+(?:\.\d+)?", value))


def _css_length(value: str) -> str:
    if _unitless_number(value):
        return f"{value}px"
    return value


def _element_style(node: TbVideoNode) -> str:
    width = node["width"]
    height = node["height"]
    declarations = []
    if node.get("has_width"):
        declarations.append(f"--tb-video-width: {_css_length(width)}")
    if node.get("has_height"):
        declarations.append(f"--tb-video-height: {_css_length(height)}")
    if node.get("has_width") and node.get("has_height") and _unitless_number(width) and _unitless_number(height):
        declarations.append(f"--tb-video-aspect-ratio: {width} / {height}")
    return "; ".join(declarations)


def _html_asset_url(self: HTML5Translator, url: str | None) -> str | None:
    if not url:
        return url
    if url.startswith("_static/"):
        docname = getattr(self.builder, "current_docname", "")
        from_dir = posixpath.dirname(docname)
        if not from_dir:
            return url
        return posixpath.relpath(url, from_dir)
    return url


def _config(self: HTML5Translator, node: TbVideoNode) -> dict[str, object]:
    return {
        "sourceUrl": _html_asset_url(self, node["source_url"]),
        "embedUrl": _html_asset_url(self, node["embed_url"]),
        "provider": node["provider"],
        "kind": node["kind"],
        "thumbnailUrl": _html_asset_url(self, node.get("thumbnail_url")),
        "window": node["window"],
        "width": node["width"],
        "height": node["height"],
        "playLabel": "Play video",
        "pauseLabel": "Pause video",
        "openLabel": "Open video in new window",
    }


def visit_tb_video_html(self: HTML5Translator, node: TbVideoNode) -> None:
    if node.get("hidden"):
        raise nodes.SkipNode

    node_id = escape(_node_id(node), quote=True)
    html_source_url = _html_asset_url(self, node["source_url"])
    html_embed_url = _html_asset_url(self, node["embed_url"])
    html_thumbnail_url = _html_asset_url(self, node.get("thumbnail_url"))
    source_url = escape(html_source_url or "", quote=True)
    embed_url = escape(html_embed_url or "", quote=True)
    width = escape(node["width"], quote=True)
    height = escape(node["height"], quote=True)
    provider = escape(node["provider"], quote=True)
    kind = escape(node["kind"], quote=True)
    thumbnail_url = html_thumbnail_url
    style = _element_style(node)
    style_attr = f' style="{escape(style, quote=True)}"' if style else ""
    window_attr = ' window="true"' if node["window"] else ""

    self.body.append(
        f'<tb-video id="{node_id}" source-url="{source_url}" embed-url="{embed_url}" '
        f'provider="{provider}" kind="{kind}" width="{width}" height="{height}"'
        f'{style_attr}{window_attr}'
    )
    self.body.append(">\n")
    self.body.append('<figure class="tb-video__fallback">\n')
    self.body.append(
        f'<a class="tb-video__placeholder" href="{source_url}" '
        f'target="_blank" rel="noopener noreferrer">\n'
    )
    if thumbnail_url:
        thumbnail = escape(thumbnail_url, quote=True)
        self.body.append(f'<img class="tb-video__thumbnail" src="{thumbnail}" alt="">\n')
    self.body.append('<span class="tb-video__placeholder-icon" aria-hidden="true"></span>\n')
    self.body.append('<span class="tb-video__placeholder-label">Open video</span>\n')
    self.body.append("</a>\n")
    self.body.append("</figure>\n")
    if node.get("has_notes"):
        self.body.append('<div class="tb-video__notes">\n')


def depart_tb_video_html(self: HTML5Translator, node: TbVideoNode) -> None:
    if node.get("has_notes"):
        self.body.append("</div>\n")
    payload = json.dumps(_config(self, node), ensure_ascii=False).replace("</", "<\\/")
    self.body.append(f'<script type="application/json" class="tb-video__config">{payload}</script>\n')
    self.body.append("</tb-video>\n")


def visit_tb_video_latex(self: LaTeXTranslator, node: TbVideoNode) -> None:
    if node.get("hidden"):
        raise nodes.SkipNode
    self.body.append("\n\\begin{sphinxadmonition}{note}{Video}\n")
    self.body.append(self.encode(f"Video URL: {node['source_url']}"))
    self.body.append("\n")
    if node.get("has_notes"):
        self.body.append("\\textbf{Notes.}\\par\n")


def depart_tb_video_latex(self: LaTeXTranslator, node: TbVideoNode) -> None:
    self.body.append("\n\\end{sphinxadmonition}\n")


def visit_tb_video_text(self: TextTranslator, node: TbVideoNode) -> None:
    if node.get("hidden"):
        raise nodes.SkipNode
    self.add_text("\n[Video]\n")
    self.add_text(f"Video URL: {node['source_url']}\n")
    if node.get("has_notes"):
        self.add_text("Notes:\n")


def depart_tb_video_text(self: TextTranslator, node: TbVideoNode) -> None:
    self.add_text("\n")
