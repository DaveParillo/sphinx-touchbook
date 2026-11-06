"""Configuration contracts independent of Sphinx parsing and HTML generation."""

from copy import deepcopy
from types import SimpleNamespace

import pytest
from sphinx.errors import ConfigError

from sphinx_touchbook.code_config import configure_code, resolve_code_settings


def resolve(options=None, arguments=(), **project):
    return resolve_code_settings(SimpleNamespace(**project), options or {}, arguments)


def test_existing_javascript_blocks_still_use_jobe():
    settings = resolve(arguments=["js"])
    assert settings.attributes["runner"] == "jobe"
    assert settings.attributes["jobe_language"] == "nodejs"


@pytest.mark.parametrize("language", ["sql", "sqlite", "sqlite3", "html", "html5", "js", "javascript"])
def test_browser_runner_can_be_selected_for_supported_languages(language):
    assert resolve({"runner": "browser"}, [language]).attributes["runner"] == "browser"


def test_block_runner_overrides_project_runner():
    assert resolve(arguments=["sql"], tb_code_default_runner="browser").attributes[
        "runner"
    ] == "browser"
    assert resolve({"runner": "jobe"}, ["cpp"],
                   tb_code_default_runner="browser").attributes["runner"] == "jobe"


def test_invalid_runner_or_browser_language_reports_a_configuration_error():
    with pytest.raises(ConfigError, match="tb_code_default_runner"):
        configure_code(None, SimpleNamespace(tb_code_default_runner="unknown"))
    with pytest.raises(ValueError, match="tb-code :runner:"):
        resolve({"runner": "unknown"})
    with pytest.raises(ValueError, match="does not support 'nodejs'"):
        resolve({"runner": "browser"}, ["nodejs"])


@pytest.mark.parametrize("language", ["cpp", "c++"])
def test_one_mapped_language_profile_serves_all_aliases(language):
    settings = resolve(arguments=[language], tb_code_language_defaults={
        "cpp": {"compileargs": ["-std=c++20"], "linkargs": ["-lm"]},
    })
    assert settings.attributes["language"] == language
    assert settings.attributes["jobe_language"] == "cpp"
    assert settings.attributes["parameters"]["compileargs"] == ["-std=c++20"]
    assert settings.attributes["parameters"]["linkargs"] == ["-lm"]


@pytest.mark.parametrize("alias_profile", [{}, {"compileargs": ["-std=c++17"]}])
def test_explicit_alias_profile_replaces_entire_mapped_profile(alias_profile):
    settings = resolve(arguments=["c++"], tb_code_language_defaults={
        "cpp": {"compileargs": ["-std=c++20"], "linkargs": ["-lm"]},
        "c++": alias_profile,
    })
    parameters = settings.attributes["parameters"]
    assert parameters["compileargs"] == alias_profile.get("compileargs", [])
    assert parameters["linkargs"] == []


def test_language_option_overrides_argument_and_project_default():
    settings = resolve({"language": "js"}, ["cpp"],
                       tb_code_default_language="python")
    assert settings.attributes["language"] == "js"
    assert settings.attributes["jobe_language"] == "nodejs"
    assert resolve(arguments=["cpp"], tb_code_default_language="python").attributes[
        "language"
    ] == "cpp"
    assert resolve(tb_code_default_language="python").attributes["language"] == "python"


def test_custom_language_map_replaces_builtins_and_is_not_followed_recursively():
    project = {"tb_code_language_map": {"custom": "python", "python": "python3"}}
    custom = resolve(arguments=["custom"], **project)
    assert custom.attributes["jobe_language"] == "python"
    assert resolve(arguments=["js"], **project).attributes["jobe_language"] == "js"


def test_explicit_empty_arguments_clear_defaults_and_stdin_remains_raw():
    settings = resolve({"runargs": "", "stdin": 'a "b c"\n'}, ["cpp"],
                       tb_code_language_defaults={"cpp": {"runargs": ["default"]}})
    assert settings.attributes["parameters"]["runargs"] == []
    assert settings.attributes["stdin"] == 'a "b c"\n'
    assert "stdin" not in resolve().attributes
    assert resolve({"stdin": ""}).attributes["stdin"] == ""


@pytest.mark.parametrize(("value", "expected"), [
    ('--name "two words"', ["--name", "two words"]),
    ("['-Wall', '-Wextra']", ["-Wall", "-Wextra"]),
    ('"one argument"', ["one argument"]),
    ("12", ["12"]),
    ("False", ["False"]),
    ("None", ["None"]),
])
def test_existing_argument_syntax(value, expected):
    assert resolve({"runargs": value}).attributes["parameters"]["runargs"] == expected


def test_block_options_override_project_listing_defaults():
    settings = resolve({"class": ["local"], "linenos": None, "dedent": None},
                       tb_code_block_defaults={"class": "global", "linenos": False,
                                               "dedent": "4", "lineno-start": "7"})
    assert settings.listing_options == {
        "class": ["local"], "linenos": True, "dedent": None, "lineno-start": 7,
    }


def test_flags_and_labels_keep_their_existing_override_rules():
    settings = resolve({"show-tutor": None, "run-label": "Execute"},
                       tb_code_block_defaults={"show-tutor": False},
                       tb_code_run_label="Go")
    assert settings.attributes["show_tutor"] is True
    assert settings.attributes["run_label"] == "Execute"
    assert resolve(tb_code_block_defaults={"show-tutor": "off"}).attributes[
        "show_tutor"
    ] is False


def test_null_flag_defaults_keep_their_existing_meaning():
    settings = resolve(tb_code_block_defaults={
        "linenos": None, "force": None, "show-tutor": None,
    })
    assert settings.listing_options["linenos"] is True
    assert settings.listing_options["force"] is False
    assert settings.attributes["show_tutor"] is False


def test_compiler_explorer_profile_uses_same_whole_entry_precedence():
    settings = resolve({"show-compiler-explorer": None}, ["c++"],
                       tb_code_compiler_explorer_defaults={
                           "cpp": {"language": "c++", "compiler": "gsnapshot"},
                           "c++": {"language": "c++"},
                       })
    assert settings.attributes["compiler_explorer"] is None
    assert "needs a language and compiler" in settings.warnings[0]


def test_missing_compiler_explorer_profile_warns_only_when_requested_and_visible():
    assert not resolve().warnings
    assert resolve({"show-compiler-explorer": None}).warnings
    assert not resolve({"show-compiler-explorer": None, "hidden": None}).warnings


@pytest.mark.parametrize(("project", "location"), [
    ({"tb_code_language_map": []}, "tb_code_language_map"),
    ({"tb_code_language_map": {"cpp": 1}}, "tb_code_language_map['cpp']"),
    ({"tb_code_language_defaults": []}, "tb_code_language_defaults"),
    ({"tb_code_language_defaults": {"cpp": []}}, "tb_code_language_defaults['cpp']"),
    ({"tb_code_language_defaults": {"cpp": {"compilearg": []}}}, "compilearg"),
    ({"tb_code_language_defaults": {"cpp": {"compileargs": {}}}},
     "tb_code_language_defaults['cpp']['compileargs']"),
    ({"tb_code_language_defaults": {"cpp": {"runargs": '"unclosed'}}},
     "tb_code_language_defaults['cpp']['runargs']"),
    ({"tb_code_compiler_explorer_defaults": {"cpp": []}},
     "tb_code_compiler_explorer_defaults['cpp']"),
    ({"tb_code_compiler_explorer_defaults": {"cpp": {"compiler": 42}}},
     "tb_code_compiler_explorer_defaults['cpp']['compiler']"),
    ({"tb_code_block_defaults": []}, "tb_code_block_defaults"),
    ({"tb_code_block_defaults": {"lineos": True}}, "lineos"),
    ({"tb_code_block_defaults": {"lineno-start": "many"}},
     "tb_code_block_defaults['lineno-start']"),
    ({"tb_code_block_defaults": {"linenos": "sometimes"}},
     "tb_code_block_defaults['linenos']"),
    ({"tb_code_validate_language": "False"}, "tb_code_validate_language"),
    ({"tb_code_default_language": ""}, "tb_code_default_language"),
    ({"tb_code_default_endpoint": 42}, "tb_code_default_endpoint"),
    ({"tb_code_run_label": False}, "tb_code_run_label"),
])
def test_configuration_errors_identify_the_setting(project, location):
    with pytest.raises(ConfigError) as error:
        configure_code(None, SimpleNamespace(**project))
    assert location in str(error.value)


def test_malformed_block_arguments_have_a_block_specific_error():
    message = "tb-code option 'runargs': No closing quotation"
    with pytest.raises(ValueError, match=message):
        resolve({"runargs": '"unclosed'})


def test_normalization_and_resolution_do_not_mutate_public_settings():
    project = {"tb_code_language_defaults": {"cpp": {"compileargs": ["-Wall"]}},
               "tb_code_block_defaults": {"class": ["example"]}}
    original = deepcopy(project)
    config = SimpleNamespace(**project)
    configure_code(None, config)
    first = resolve_code_settings(config, {}, ["cpp"])
    first.attributes["parameters"]["compileargs"].append("-Wextra")
    first.listing_options["class"].append("changed")
    second = resolve_code_settings(config, {}, ["cpp"])
    assert second.attributes["parameters"]["compileargs"] == ["-Wall"]
    assert second.listing_options["class"] == ["example"]
    assert {name: getattr(config, name) for name in project} == original
