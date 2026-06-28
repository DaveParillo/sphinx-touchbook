"""Sphinx extension entrypoint for Touchbook interactive directives."""

from __future__ import annotations

from pathlib import Path

from sphinx.application import Sphinx

from .directives.blank import TbBlankDirective
from .directives.code import (
    DEFAULT_CODE_BLOCK_OPTIONS,
    DEFAULT_ENDPOINT,
    DEFAULT_FILES_ENDPOINT,
    DEFAULT_LANGUAGE,
    DEFAULT_LANGUAGE_DEFAULTS,
    DEFAULT_LANGUAGE_MAP,
    DEFAULT_LANGUAGES_ENDPOINT,
    TbCodeDirective,
)
from .directives.choice import DEFAULT_FORCE_MULTIPLE, DEFAULT_RANDOM, TbChoiceDirective
from .directives.click import (
    DEFAULT_SHOW_HINTS,
    TbClickDirective,
    TbClickHitDirective,
    TbClickMissDirective,
)
from .directives.file import TbFileDirective
from .directives.match import TbMatchDirective
from .directives.reveal import TbRevealDirective
from .directives.tabs import TbGroupDirective, TbTabDirective
from .directives.video import TbVideoDirective
from .nodes import (
    TbBlankInputNode,
    TbBlankNode,
    TbBlankPromptNode,
    TbChoiceAnswerNode,
    TbChoiceFeedbackNode,
    TbChoiceNode,
    TbChoiceOptionNode,
    TbChoicePromptNode,
    TbClickNode,
    TbClickPromptNode,
    TbClickRegionNode,
    TbClickSourceNode,
    TbCodeNode,
    TbFileNode,
    TbMatchDistractorNode,
    TbMatchNode,
    TbMatchPairNode,
    TbMatchPromptNode,
    TbMatchSourceNode,
    TbMatchTargetNode,
    TbRevealNode,
    TbGroupNode,
    TbTabNode,
    TbVideoNode,
)
from .generators.blank import (
    depart_tb_blank_html,
    depart_tb_blank_input_html,
    depart_tb_blank_input_latex,
    depart_tb_blank_input_text,
    depart_tb_blank_latex,
    depart_tb_blank_prompt_html,
    depart_tb_blank_prompt_latex,
    depart_tb_blank_prompt_text,
    depart_tb_blank_text,
    visit_tb_blank_html,
    visit_tb_blank_input_html,
    visit_tb_blank_input_latex,
    visit_tb_blank_input_text,
    visit_tb_blank_latex,
    visit_tb_blank_prompt_html,
    visit_tb_blank_prompt_latex,
    visit_tb_blank_prompt_text,
    visit_tb_blank_text,
)
from .generators.click import (
    depart_tb_click_html,
    depart_tb_click_latex,
    depart_tb_click_prompt_html,
    depart_tb_click_prompt_latex,
    depart_tb_click_prompt_text,
    depart_tb_click_region_html,
    depart_tb_click_region_latex,
    depart_tb_click_region_text,
    depart_tb_click_source_html,
    depart_tb_click_source_latex,
    depart_tb_click_source_text,
    depart_tb_click_text,
    visit_tb_click_html,
    visit_tb_click_latex,
    visit_tb_click_prompt_html,
    visit_tb_click_prompt_latex,
    visit_tb_click_prompt_text,
    visit_tb_click_region_html,
    visit_tb_click_region_latex,
    visit_tb_click_region_text,
    visit_tb_click_source_html,
    visit_tb_click_source_latex,
    visit_tb_click_source_text,
    visit_tb_click_text,
)
from .generators.choice import (
    depart_tb_choice_answer_html,
    depart_tb_choice_answer_latex,
    depart_tb_choice_answer_text,
    depart_tb_choice_feedback_html,
    depart_tb_choice_feedback_latex,
    depart_tb_choice_feedback_text,
    depart_tb_choice_html,
    depart_tb_choice_latex,
    depart_tb_choice_option_html,
    depart_tb_choice_option_latex,
    depart_tb_choice_option_text,
    depart_tb_choice_prompt_html,
    depart_tb_choice_prompt_latex,
    depart_tb_choice_prompt_text,
    depart_tb_choice_text,
    visit_tb_choice_answer_html,
    visit_tb_choice_answer_latex,
    visit_tb_choice_answer_text,
    visit_tb_choice_feedback_html,
    visit_tb_choice_feedback_latex,
    visit_tb_choice_feedback_text,
    visit_tb_choice_html,
    visit_tb_choice_latex,
    visit_tb_choice_option_html,
    visit_tb_choice_option_latex,
    visit_tb_choice_option_text,
    visit_tb_choice_prompt_html,
    visit_tb_choice_prompt_latex,
    visit_tb_choice_prompt_text,
    visit_tb_choice_text,
)
from .generators.code import (
    depart_tb_code_html,
    depart_tb_code_latex,
    depart_tb_code_text,
    visit_tb_code_html,
    visit_tb_code_latex,
    visit_tb_code_text,
)
from .generators.file import (
    depart_tb_file_html,
    depart_tb_file_latex,
    depart_tb_file_text,
    visit_tb_file_html,
    visit_tb_file_latex,
    visit_tb_file_text,
)
from .generators.match import (
    depart_tb_match_html,
    depart_tb_match_distractor_html,
    depart_tb_match_distractor_latex,
    depart_tb_match_distractor_text,
    depart_tb_match_latex,
    depart_tb_match_pair_html,
    depart_tb_match_pair_latex,
    depart_tb_match_pair_text,
    depart_tb_match_prompt_html,
    depart_tb_match_prompt_latex,
    depart_tb_match_prompt_text,
    depart_tb_match_source_html,
    depart_tb_match_source_latex,
    depart_tb_match_source_text,
    depart_tb_match_target_html,
    depart_tb_match_target_latex,
    depart_tb_match_target_text,
    depart_tb_match_text,
    visit_tb_match_html,
    visit_tb_match_distractor_html,
    visit_tb_match_distractor_latex,
    visit_tb_match_distractor_text,
    visit_tb_match_latex,
    visit_tb_match_pair_html,
    visit_tb_match_pair_latex,
    visit_tb_match_pair_text,
    visit_tb_match_prompt_html,
    visit_tb_match_prompt_latex,
    visit_tb_match_prompt_text,
    visit_tb_match_source_html,
    visit_tb_match_source_latex,
    visit_tb_match_source_text,
    visit_tb_match_target_html,
    visit_tb_match_target_latex,
    visit_tb_match_target_text,
    visit_tb_match_text,
)
from .generators.reveal import (
    depart_tb_reveal_html,
    depart_tb_reveal_latex,
    depart_tb_reveal_text,
    visit_tb_reveal_html,
    visit_tb_reveal_latex,
    visit_tb_reveal_text,
)
from .generators.video import (
    depart_tb_video_html,
    depart_tb_video_latex,
    depart_tb_video_text,
    visit_tb_video_html,
    visit_tb_video_latex,
    visit_tb_video_text,
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
from .transforms import (
    TbCodeIncludeTransform,
    collect_tb_files,
    collect_tb_code_snippets,
    merge_tb_files,
    merge_tb_code_snippets,
    purge_tb_files,
    purge_tb_code_snippets,
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
    app.add_config_value("tb_code_files_endpoint", DEFAULT_FILES_ENDPOINT, "html")
    app.add_config_value("tb_code_languages_endpoint", DEFAULT_LANGUAGES_ENDPOINT, "html")
    app.add_config_value("tb_code_validate_language", True, "html")
    app.add_config_value("tb_code_default_language", DEFAULT_LANGUAGE, "env")
    app.add_config_value("tb_code_language_map", DEFAULT_LANGUAGE_MAP, "env")
    app.add_config_value("tb_code_language_defaults", DEFAULT_LANGUAGE_DEFAULTS, "env")
    app.add_config_value("tb_code_block_defaults", DEFAULT_CODE_BLOCK_OPTIONS, "env")
    app.add_config_value("tb_code_run_label", "Run", "html")
    app.add_config_value("tb_code_edit_label", "Edit", "html")
    app.add_config_value("tb_code_hide_edit_label", "Hide editor", "html")
    app.add_config_value("tb_code_revision_label", "Source version", "html")
    app.add_config_value("tb_choice_random", DEFAULT_RANDOM, "env")
    app.add_config_value("tb_choice_force_multiple", DEFAULT_FORCE_MULTIPLE, "env")
    app.add_config_value("tb_click_show_hints", DEFAULT_SHOW_HINTS, "html")
    app.add_config_value("tb_video_default_width", "560", "env")
    app.add_config_value("tb_video_default_height", "315", "env")
    app.add_node(
        TbBlankNode,
        html=(visit_tb_blank_html, depart_tb_blank_html),
        latex=(visit_tb_blank_latex, depart_tb_blank_latex),
        text=(visit_tb_blank_text, depart_tb_blank_text),
    )
    app.add_node(
        TbBlankPromptNode,
        html=(visit_tb_blank_prompt_html, depart_tb_blank_prompt_html),
        latex=(visit_tb_blank_prompt_latex, depart_tb_blank_prompt_latex),
        text=(visit_tb_blank_prompt_text, depart_tb_blank_prompt_text),
    )
    app.add_node(
        TbBlankInputNode,
        html=(visit_tb_blank_input_html, depart_tb_blank_input_html),
        latex=(visit_tb_blank_input_latex, depart_tb_blank_input_latex),
        text=(visit_tb_blank_input_text, depart_tb_blank_input_text),
    )
    app.add_node(
        TbCodeNode,
        html=(visit_tb_code_html, depart_tb_code_html),
        latex=(visit_tb_code_latex, depart_tb_code_latex),
        text=(visit_tb_code_text, depart_tb_code_text),
    )
    app.add_node(
        TbFileNode,
        html=(visit_tb_file_html, depart_tb_file_html),
        latex=(visit_tb_file_latex, depart_tb_file_latex),
        text=(visit_tb_file_text, depart_tb_file_text),
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
    app.add_node(
        TbVideoNode,
        html=(visit_tb_video_html, depart_tb_video_html),
        latex=(visit_tb_video_latex, depart_tb_video_latex),
        text=(visit_tb_video_text, depart_tb_video_text),
    )
    app.add_node(
        TbChoiceNode,
        html=(visit_tb_choice_html, depart_tb_choice_html),
        latex=(visit_tb_choice_latex, depart_tb_choice_latex),
        text=(visit_tb_choice_text, depart_tb_choice_text),
    )
    app.add_node(
        TbChoicePromptNode,
        html=(visit_tb_choice_prompt_html, depart_tb_choice_prompt_html),
        latex=(visit_tb_choice_prompt_latex, depart_tb_choice_prompt_latex),
        text=(visit_tb_choice_prompt_text, depart_tb_choice_prompt_text),
    )
    app.add_node(
        TbChoiceOptionNode,
        html=(visit_tb_choice_option_html, depart_tb_choice_option_html),
        latex=(visit_tb_choice_option_latex, depart_tb_choice_option_latex),
        text=(visit_tb_choice_option_text, depart_tb_choice_option_text),
    )
    app.add_node(
        TbChoiceAnswerNode,
        html=(visit_tb_choice_answer_html, depart_tb_choice_answer_html),
        latex=(visit_tb_choice_answer_latex, depart_tb_choice_answer_latex),
        text=(visit_tb_choice_answer_text, depart_tb_choice_answer_text),
    )
    app.add_node(
        TbChoiceFeedbackNode,
        html=(visit_tb_choice_feedback_html, depart_tb_choice_feedback_html),
        latex=(visit_tb_choice_feedback_latex, depart_tb_choice_feedback_latex),
        text=(visit_tb_choice_feedback_text, depart_tb_choice_feedback_text),
    )
    app.add_node(
        TbClickNode,
        html=(visit_tb_click_html, depart_tb_click_html),
        latex=(visit_tb_click_latex, depart_tb_click_latex),
        text=(visit_tb_click_text, depart_tb_click_text),
    )
    app.add_node(
        TbClickPromptNode,
        html=(visit_tb_click_prompt_html, depart_tb_click_prompt_html),
        latex=(visit_tb_click_prompt_latex, depart_tb_click_prompt_latex),
        text=(visit_tb_click_prompt_text, depart_tb_click_prompt_text),
    )
    app.add_node(
        TbClickSourceNode,
        html=(visit_tb_click_source_html, depart_tb_click_source_html),
        latex=(visit_tb_click_source_latex, depart_tb_click_source_latex),
        text=(visit_tb_click_source_text, depart_tb_click_source_text),
    )
    app.add_node(
        TbClickRegionNode,
        html=(visit_tb_click_region_html, depart_tb_click_region_html),
        latex=(visit_tb_click_region_latex, depart_tb_click_region_latex),
        text=(visit_tb_click_region_text, depart_tb_click_region_text),
    )
    app.add_node(
        TbMatchNode,
        html=(visit_tb_match_html, depart_tb_match_html),
        latex=(visit_tb_match_latex, depart_tb_match_latex),
        text=(visit_tb_match_text, depart_tb_match_text),
    )
    app.add_node(
        TbMatchPromptNode,
        html=(visit_tb_match_prompt_html, depart_tb_match_prompt_html),
        latex=(visit_tb_match_prompt_latex, depart_tb_match_prompt_latex),
        text=(visit_tb_match_prompt_text, depart_tb_match_prompt_text),
    )
    app.add_node(
        TbMatchPairNode,
        html=(visit_tb_match_pair_html, depart_tb_match_pair_html),
        latex=(visit_tb_match_pair_latex, depart_tb_match_pair_latex),
        text=(visit_tb_match_pair_text, depart_tb_match_pair_text),
    )
    app.add_node(
        TbMatchSourceNode,
        html=(visit_tb_match_source_html, depart_tb_match_source_html),
        latex=(visit_tb_match_source_latex, depart_tb_match_source_latex),
        text=(visit_tb_match_source_text, depart_tb_match_source_text),
    )
    app.add_node(
        TbMatchTargetNode,
        html=(visit_tb_match_target_html, depart_tb_match_target_html),
        latex=(visit_tb_match_target_latex, depart_tb_match_target_latex),
        text=(visit_tb_match_target_text, depart_tb_match_target_text),
    )
    app.add_node(
        TbMatchDistractorNode,
        html=(visit_tb_match_distractor_html, depart_tb_match_distractor_html),
        latex=(visit_tb_match_distractor_latex, depart_tb_match_distractor_latex),
        text=(visit_tb_match_distractor_text, depart_tb_match_distractor_text),
    )
    app.add_directive("tb-blank", TbBlankDirective)
    app.add_directive("tb-code", TbCodeDirective)
    app.add_directive("tb-choice", TbChoiceDirective)
    app.add_directive("tb-click", TbClickDirective)
    app.add_directive("tb-hit", TbClickHitDirective)
    app.add_directive("tb-miss", TbClickMissDirective)
    app.add_directive("tb-file", TbFileDirective)
    app.add_directive("tb-match", TbMatchDirective)
    app.add_directive("tb-reveal", TbRevealDirective)
    app.add_directive("tb-group", TbGroupDirective)
    app.add_directive("tb-tab", TbTabDirective)
    app.add_directive("tb-video", TbVideoDirective)
    app.add_post_transform(TbCodeIncludeTransform)
    app.connect("env-purge-doc", purge_tb_code_snippets)
    app.connect("env-purge-doc", purge_tb_files)
    app.connect("doctree-read", collect_tb_code_snippets)
    app.connect("doctree-read", collect_tb_files)
    app.connect("env-merge-info", merge_tb_code_snippets)
    app.connect("env-merge-info", merge_tb_files)
    app.connect("builder-inited", _add_static_path)
    app.add_css_file("tb-reveal.css")
    app.add_css_file("tb-group.css")
    app.add_css_file("tb-code.css")
    app.add_css_file("tb-blank.css")
    app.add_css_file("tb-choice.css")
    app.add_css_file("tb-click.css")
    app.add_css_file("tb-file.css")
    app.add_css_file("tb-match.css")
    app.add_css_file("tb-video.css")
    app.add_js_file("tb-reveal.js", loading_method="defer")
    app.add_js_file("tb-group.js", loading_method="defer")
    app.add_js_file("tb-code.js", loading_method="defer")
    app.add_js_file("tb-blank.js", loading_method="defer")
    app.add_js_file("tb-choice.js", loading_method="defer")
    app.add_js_file("tb-click.js", loading_method="defer")
    app.add_js_file("tb-file.js", loading_method="defer")
    app.add_js_file("tb-match.js", loading_method="defer")
    app.add_js_file("tb-video.js", loading_method="defer")
    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
