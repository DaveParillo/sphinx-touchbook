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

from html import escape

"""Builder generators for ``tb-reveal``."""

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.nodes import TbRevealNode


def _node_id(node: TbRevealNode) -> str:
    return node["ids"][0]


def _attrs(node: TbRevealNode) -> str:
    attrs = {
        "id": _node_id(node),
        "showlabel": node["showlabel"],
        "hidelabel": node["hidelabel"],
        "modal-titlebar": node["modal_titlebar"],
    }
    parts = [f'{name}="{escape(value, quote=True)}"' for name, value in attrs.items()]
    if node["modal"]:
        parts.append("modal")
    return " ".join(parts)


def visit_tb_reveal_html(self: HTML5Translator, node: TbRevealNode) -> None:
    self.body.append(f'<tb-reveal {_attrs(node)}>\n')
    self.body.append('<details class="tb-reveal__fallback">\n')
    self.body.append(f'<summary>{escape(node["showlabel"])}</summary>\n')
    self.body.append('<div class="tb-reveal__content">\n')


def depart_tb_reveal_html(self: HTML5Translator, node: TbRevealNode) -> None:
    self.body.append("</div>\n")
    self.body.append("</details>\n")
    self.body.append("</tb-reveal>\n")


def visit_tb_reveal_latex(self: LaTeXTranslator, node: TbRevealNode) -> None:
    self.body.append("\n\\begin{sphinxadmonition}{note}{")
    self.body.append(self.encode(node["modal_titlebar"] if node["modal"] else node["showlabel"]))
    self.body.append("}\n")


def depart_tb_reveal_latex(self: LaTeXTranslator, node: TbRevealNode) -> None:
    self.body.append("\n\\end{sphinxadmonition}\n")


def visit_tb_reveal_text(self: TextTranslator, node: TbRevealNode) -> None:
    label = node["modal_titlebar"] if node["modal"] else node["showlabel"]
    self.add_text(f"\n[{label}]\n")


def depart_tb_reveal_text(self: TextTranslator, node: TbRevealNode) -> None:
    self.add_text("\n")
