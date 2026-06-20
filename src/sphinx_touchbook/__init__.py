"""Sphinx extension entrypoint for Touchbook interactive directives."""

from __future__ import annotations

from pathlib import Path

from sphinx.application import Sphinx

from .directives.code import (
    DEFAULT_CODE_BLOCK_OPTIONS,
    DEFAULT_ENDPOINT,
    DEFAULT_LANGUAGE,
    DEFAULT_LANGUAGE_DEFAULTS,
    DEFAULT_LANGUAGE_MAP,
    DEFAULT_LANGUAGES_ENDPOINT,
    TbCodeDirective,
)
from .directives.reveal import TbRevealDirective
from .directives.tabs import TbGroupDirective, TbTabDirective
from .nodes import TbCodeNode, TbRevealNode, TbGroupNode, TbTabNode
from .generators.code import (
    depart_tb_code_html,
    depart_tb_code_latex,
    depart_tb_code_text,
    visit_tb_code_html,
    visit_tb_code_latex,
    visit_tb_code_text,
)
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
    app.add_config_value(
        "tb_code_default_endpoint",
        DEFAULT_ENDPOINT,
        "html",
    )
    app.add_config_value("tb_code_languages_endpoint", DEFAULT_LANGUAGES_ENDPOINT, "html")
    app.add_config_value("tb_code_validate_language", True, "html")
    app.add_config_value("tb_code_default_language", DEFAULT_LANGUAGE, "env")
    app.add_config_value("tb_code_language_map", DEFAULT_LANGUAGE_MAP, "env")
    app.add_config_value("tb_code_language_defaults", DEFAULT_LANGUAGE_DEFAULTS, "env")
    app.add_config_value("tb_code_code_block_defaults", DEFAULT_CODE_BLOCK_OPTIONS, "env")
    app.add_config_value("tb_code_run_label", "Run", "html")
    app.add_config_value("tb_code_edit_label", "Edit", "html")
    app.add_config_value("tb_code_hide_edit_label", "Hide editor", "html")
    app.add_config_value("tb_code_revision_label", "Editor revision", "html")
    app.add_node(
        TbCodeNode,
        html=(visit_tb_code_html, depart_tb_code_html),
        latex=(visit_tb_code_latex, depart_tb_code_latex),
        text=(visit_tb_code_text, depart_tb_code_text),
    )
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
    app.add_directive("tb-code", TbCodeDirective)
    app.add_directive("tb-reveal", TbRevealDirective)
    app.add_directive("tb-group", TbGroupDirective)
    app.add_directive("tb-tab", TbTabDirective)
    app.connect("builder-inited", _add_static_path)
    app.add_css_file("tb-reveal.css")
    app.add_css_file("tb-group.css")
    app.add_css_file("tb-code.css")
    app.add_js_file("tb-reveal.js", loading_method="defer")
    app.add_js_file("tb-group.js", loading_method="defer")
    app.add_js_file("tb-code.js", loading_method="defer")
    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
