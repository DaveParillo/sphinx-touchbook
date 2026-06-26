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
from html import escape

"""Builder generators for ``tb-file``."""

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.nodes import TbFileNode


def _node_id(node: TbFileNode) -> str:
    return node["ids"][0]


def _config(node: TbFileNode) -> dict[str, object]:
    return {
        "filename": node["filename"],
        "content": node.get("content", ""),
        "mimeType": node["mime_type"],
        "isText": node["is_text"],
        "dataUrl": node.get("data_url"),
        "editable": node["editable"],
        "editLabel": "Edit",
        "hideEditLabel": "Hide editor",
    }


def visit_tb_file_html(self: HTML5Translator, node: TbFileNode) -> None:
    if node.get("hidden"):
        raise nodes.SkipNode
    node_id = escape(_node_id(node), quote=True)
    filename = escape(node["filename"], quote=True)
    editable = "true" if node["editable"] else "false"
    self.body.append(f'<tb-file id="{node_id}" filename="{filename}" editable="{editable}">\n')
    self.body.append('<figure class="tb-file__fallback">\n')
    self.body.append(f'<figcaption class="tb-file__caption">{escape(node["filename"])}</figcaption>\n')
    if node["is_text"]:
        self.body.append(f'<pre class="tb-file__content"><code>{escape(node.get("content", ""))}</code></pre>\n')
    elif node["mime_type"].startswith("image/"):
        src = escape(node["data_url"], quote=True)
        self.body.append(f'<img class="tb-file__image" src="{src}" alt="{filename}">\n')
    else:
        mime_type = escape(node["mime_type"])
        self.body.append(f'<p class="tb-file__binary">Binary file: {filename} ({mime_type})</p>\n')
    self.body.append("</figure>\n")
    payload = json.dumps(_config(node), ensure_ascii=False).replace("</", "<\\/")
    self.body.append(f'<script type="application/json" class="tb-file__config">{payload}</script>\n')


def depart_tb_file_html(self: HTML5Translator, node: TbFileNode) -> None:
    self.body.append("</tb-file>\n")


def visit_tb_file_latex(self: LaTeXTranslator, node: TbFileNode) -> None:
    if node.get("hidden"):
        raise nodes.SkipNode
    self.body.append("\n\\begin{sphinxadmonition}{note}{")
    self.body.append(self.encode(node["filename"]))
    self.body.append("}\n")
    if node["is_text"]:
        self.body.append("\\begin{sphinxVerbatim}[commandchars=\\\\\\{\\}]\n")
        self.body.append(self.encode(node.get("content", "")))
    else:
        self.body.append(self.encode(f"Image file: {node['filename']}"))


def depart_tb_file_latex(self: LaTeXTranslator, node: TbFileNode) -> None:
    if node["is_text"]:
        self.body.append("\n\\end{sphinxVerbatim}\n")
    self.body.append("\n\\end{sphinxadmonition}\n")


def visit_tb_file_text(self: TextTranslator, node: TbFileNode) -> None:
    if node.get("hidden"):
        raise nodes.SkipNode
    self.add_text(f"\n[{node['filename']}]\n")
    if node["is_text"]:
        self.add_text(f"\n{node.get('content', '')}\n")
    else:
        self.add_text(f"\nImage file: {node['filename']}\n")


def depart_tb_file_text(self: TextTranslator, node: TbFileNode) -> None:
    self.add_text("\n")
