"""Builder generators for ``tb-reveal``."""

from __future__ import annotations

from html import escape

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
