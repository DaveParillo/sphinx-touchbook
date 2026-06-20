"""Sphinx extension entrypoint for Touchbook interactive directives."""

from __future__ import annotations

from pathlib import Path

from sphinx.application import Sphinx

from .directives.reveal import TbRevealDirective
from .directives.tabs import TbGroupDirective, TbTabDirective
from .nodes import TbRevealNode, TbGroupNode, TbTabNode
from .generators.reveal import (
    depart_tb_reveal_html,
    depart_tb_reveal_latex,
    depart_tb_reveal_text,
    visit_tb_reveal_html,
    visit_tb_reveal_latex,
    visit_tb_reveal_text,
)
from .generators.tabs import (
    depart_tb_group_html,
    depart_tb_group_latex,
    depart_tb_group_text,
    depart_tb_tab_html,
    depart_tb_tab_latex,
    depart_tb_tab_text,
    visit_tb_group_html,
    visit_tb_group_latex,
    visit_tb_group_text,
    visit_tb_tab_html,
    visit_tb_tab_latex,
    visit_tb_tab_text,
)


def _add_static_path(app: Sphinx) -> None:
    static_path = str(Path(__file__).parent / "static")
    if static_path not in app.config.html_static_path:
        app.config.html_static_path.append(static_path)


def setup(app: Sphinx) -> dict[str, object]:
    app.add_node(
        TbRevealNode,
        html=(visit_tb_reveal_html, depart_tb_reveal_html),
        latex=(visit_tb_reveal_latex, depart_tb_reveal_latex),
        text=(visit_tb_reveal_text, depart_tb_reveal_text),
    )
    app.add_node(
        TbGroupNode,
        html=(visit_tb_group_html, depart_tb_group_html),
        latex=(visit_tb_group_latex, depart_tb_group_latex),
        text=(visit_tb_group_text, depart_tb_group_text),
    )
    app.add_node(
        TbTabNode,
        html=(visit_tb_tab_html, depart_tb_tab_html),
        latex=(visit_tb_tab_latex, depart_tb_tab_latex),
        text=(visit_tb_tab_text, depart_tb_tab_text),
    )
    app.add_directive("tb-reveal", TbRevealDirective)
    app.add_directive("tb-group", TbGroupDirective)
    app.add_directive("tb-tab", TbTabDirective)
    app.connect("builder-inited", _add_static_path)
    app.add_css_file("tb-reveal.css")
    app.add_css_file("tb-group.css")
    app.add_js_file("tb-reveal.js", loading_method="defer")
    app.add_js_file("tb-group.js", loading_method="defer")
    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
