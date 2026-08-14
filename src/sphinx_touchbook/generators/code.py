"""Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.

See:
https://daveparillo.github.io/sphinx-touchbook/
for details.
"""

from __future__ import annotations

import json
from html import escape

"""Builder generators for ``tb-code``."""

from docutils import nodes
from sphinx.writers.html5 import HTML5Translator
from sphinx.writers.latex import LaTeXTranslator
from sphinx.writers.text import TextTranslator

from sphinx_touchbook.generators.common import html_additional_targets, html_class_attr, latex_targets
from sphinx_touchbook.nodes import TbCodeNode


def _node_id(node: TbCodeNode) -> str:
    return node["ids"][0]


def _config(node: TbCodeNode) -> dict[str, object]:
    return {
        "language": node["language"],
        "jobeLanguage": node["jobe_language"],
        "source": node["source"],
        "runBefore": node.get("run_before", []),
        "runAfter": node.get("run_after", []),
        "endpoint": node["endpoint"],
        "filesEndpoint": node["files_endpoint"],
        "languagesEndpoint": node["languages_endpoint"],
        "validateLanguage": node["validate_language"],
        "stdin": node["stdin"],
        "parameters": node["parameters"],
        "files": node.get("files", []),
        "editable": node["editable"],
        "showTutor": node.get("show_tutor", False),
        "runLabel": node["run_label"],
        "editLabel": node["edit_label"],
        "hideEditLabel": node["hide_edit_label"],
        "revisionLabel": node["revision_label"],
    }


def _highlight_html(self: HTML5Translator, node: TbCodeNode) -> str:
    code_options = node.get("code_block_options", {})
    linenos = "inline" if code_options.get("linenos", False) else False
    highlight_args = dict(code_options.get("highlight_args", {}))
    opts = self.config.highlight_options.get(node["language"], {})
    return self.highlighter.highlight_block(
        node["source"],
        node["language"],
        opts=opts,
        linenos=linenos,
        force=code_options.get("force", False),
        location=node,
        **highlight_args,
    )


def _highlight_latex(self: LaTeXTranslator, node: TbCodeNode) -> str:
    code_options = node.get("code_block_options", {})
    highlight_args = dict(code_options.get("highlight_args", {}))
    highlight_args["force"] = code_options.get("force", False)
    opts = self.config.highlight_options.get(node["language"], {})
    hlcode = self.highlighter.highlight_block(
        node["source"],
        node["language"],
        opts=opts,
        linenos=code_options.get("linenos", False),
        location=node,
        **highlight_args,
    )
    return hlcode.replace(r"\begin{Verbatim}", r"\begin{sphinxVerbatim}").replace(
        r"\end{Verbatim}",
        r"\end{sphinxVerbatim}",
    )


def visit_tb_code_html(self: HTML5Translator, node: TbCodeNode) -> None:
    if node.get("hidden"):
        raise nodes.SkipNode
    node_id = escape(_node_id(node), quote=True)
    language = escape(node["language"], quote=True)
    editable = "true" if node["editable"] else "false"
    code_options = node.get("code_block_options", {})
    classes = " ".join(escape(name, quote=True) for name in code_options.get("classes", []))
    fallback_class = "tb-code__fallback" if not classes else f"tb-code__fallback {classes}"
    self.body.append(html_additional_targets(node))
    self.body.append(f'<tb-code id="{node_id}"{html_class_attr(node)} language="{language}" editable="{editable}">\n')
    self.body.append(f'<figure class="{fallback_class}">\n')
    if node["caption"]:
        self.body.append(f'<figcaption class="tb-code__caption">{escape(node["caption"])}</figcaption>\n')
    self.body.append(_highlight_html(self, node))
    self.body.append("</figure>\n")
    payload = json.dumps(_config(node), ensure_ascii=False).replace("</", "<\\/")
    self.body.append(f'<script type="application/json" class="tb-code__config">{payload}</script>\n')


def depart_tb_code_html(self: HTML5Translator, node: TbCodeNode) -> None:
    self.body.append("</tb-code>\n")


def visit_tb_code_latex(self: LaTeXTranslator, node: TbCodeNode) -> None:
    if node.get("hidden"):
        raise nodes.SkipNode
    latex_targets(self, node)
    if node["caption"]:
        self.body.append("\n\\sphinxSetupCaptionForVerbatim{")
        self.body.append(self.encode(node["caption"]))
        self.body.append("}\n")
    self.body.append(_highlight_latex(self, node))
    raise nodes.SkipNode


def depart_tb_code_latex(self: LaTeXTranslator, node: TbCodeNode) -> None:
    pass


def visit_tb_code_text(self: TextTranslator, node: TbCodeNode) -> None:
    if node.get("hidden"):
        raise nodes.SkipNode
    if node["caption"]:
        self.add_text(f"\n[{node['caption']}]\n")
    self.add_text(f"\n{node['source']}\n")


def depart_tb_code_text(self: TextTranslator, node: TbCodeNode) -> None:
    self.add_text("\n")
