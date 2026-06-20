from __future__ import annotations

import json
from pathlib import Path

from bs4 import BeautifulSoup
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.code import DEFAULT_ENDPOINT, DEFAULT_LANGUAGES_ENDPOINT, TbCodeDirective
from sphinx_touchbook.nodes import TbCodeNode


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-code")
    directives.register_directive("tb-code", TbCodeDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-code", None)
        else:
            directives._directives["tb-code"] = previous
    return document


def build_sphinx(tmp_path: Path, builder: str, index: str, conf_extra: str = "") -> Path:
    srcdir = tmp_path / "src"
    outdir = tmp_path / f"_build_{builder}"
    doctreedir = tmp_path / f"_doctree_{builder}"
    srcdir.mkdir()
    (srcdir / "conf.py").write_text(
        'extensions = ["sphinx_touchbook"]\n'
        'html_theme = "alabaster"\n'
        f"{conf_extra}\n",
        encoding="utf-8",
    )
    (srcdir / "index.rst").write_text(index, encoding="utf-8")
    app = Sphinx(
        srcdir=str(srcdir),
        confdir=str(srcdir),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername=builder,
        warningiserror=True,
        freshenv=True,
    )
    app.build()
    return outdir


def test_directive_parses_semantic_node_defaults():
    document = parse_rst(
        """
.. tb-code::

   print("Hello")
"""
    )

    node = next(document.findall(TbCodeNode))
    assert node["language"] == "python3"
    assert node["source"] == 'print("Hello")'
    assert node["endpoint"] == DEFAULT_ENDPOINT
    assert node["languages_endpoint"] == DEFAULT_LANGUAGES_ENDPOINT
    assert node["validate_language"] is True
    assert node["editable"] is True
    assert node["edit_label"] == "Edit"
    assert node["hide_edit_label"] == "Hide editor"
    assert node["revision_label"] == "Editor revision"


def test_directive_accepts_language_argument_and_options():
    document = parse_rst(
        """
.. tb-code:: cpp
   :name: hello-cpp
   :caption: C++ hello
   :stdin: input text
   :compileargs: -Wall
   :linenos:
   :lineno-start: 10
   :emphasize-lines: 1
   :class: sample-code
   :readonly:

   #include <iostream>
"""
    )

    node = next(document.findall(TbCodeNode))
    assert node["ids"] == ["hello-cpp"]
    assert node["names"] == ["hello-cpp"]
    assert node["language"] == "cpp"
    assert node["caption"] == "C++ hello"
    assert node["stdin"] == "input text"
    assert node["parameters"]["compileargs"] == ["-Wall"]
    assert node["editable"] is False
    assert node["code_block_options"]["linenos"] is True
    assert node["code_block_options"]["highlight_args"]["linenostart"] == 10
    assert node["code_block_options"]["highlight_args"]["hl_lines"] == [1]
    assert node["code_block_options"]["classes"] == ["sample-code"]


def test_html_build_emits_custom_element_config_and_assets(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-code:: python
   :caption: Runnable example
   :run-label: Execute
   :edit-label: Change
   :hide-edit-label: Done
   :revision-label: Version

   print("Hello, world")
""",
    )

    html = (outdir / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("tb-code")
    assert element is not None
    assert element["language"] == "python"
    assert element.find("figure", class_="tb-code__fallback") is not None
    assert element.find("figcaption", class_="tb-code__caption").get_text(strip=True) == "Runnable example"
    config = json.loads(element.find("script", class_="tb-code__config").string)
    assert config["language"] == "python"
    assert config["jobeLanguage"] == "python3"
    assert config["endpoint"] == DEFAULT_ENDPOINT
    assert config["languagesEndpoint"] == DEFAULT_LANGUAGES_ENDPOINT
    assert config["validateLanguage"] is True
    assert config["runLabel"] == "Execute"
    assert config["editLabel"] == "Change"
    assert config["hideEditLabel"] == "Done"
    assert config["revisionLabel"] == "Version"
    assert config["source"] == 'print("Hello, world")'
    assert (outdir / "_static" / "tb-code.js").exists()
    assert (outdir / "_static" / "tb-code.css").exists()
    assert "tb-code.js" in html
    assert "tb-code.css" in html


def test_conf_py_overrides_defaults(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-code:: js

   console.log("Hello")
""",
        conf_extra=(
            'tb_code_default_endpoint = "https://example.test/runs/"\n'
            'tb_code_languages_endpoint = "https://example.test/languages"\n'
            'tb_code_language_map = {"js": "nodejs"}\n'
            'tb_code_language_defaults = {"js": {"interpreterargs": ["--trace-warnings"]}}\n'
            "tb_code_validate_language = False\n"
            'tb_code_edit_label = "Modify"\n'
            'tb_code_hide_edit_label = "Hide source"\n'
            'tb_code_revision_label = "Source version"\n'
        ),
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    config = json.loads(soup.find("script", class_="tb-code__config").string)
    assert config["endpoint"] == "https://example.test/runs/"
    assert config["languagesEndpoint"] == "https://example.test/languages"
    assert config["jobeLanguage"] == "nodejs"
    assert config["validateLanguage"] is False
    assert config["parameters"]["interpreterargs"] == ["--trace-warnings"]
    assert config["editLabel"] == "Modify"
    assert config["hideEditLabel"] == "Hide source"
    assert config["revisionLabel"] == "Source version"


def test_conf_py_can_set_code_block_option_defaults(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-code:: python

   print("one")
   print("two")
""",
        conf_extra=(
            'tb_code_code_block_defaults = {"linenos": True, "lineno-start": 25, "emphasize-lines": "2", "class": ["from-conf"]}\n'
        ),
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-code")
    fallback = element.find("figure", class_="tb-code__fallback")
    assert "from-conf" in fallback["class"]
    assert fallback.find(class_="linenos") is not None
    assert "25" in fallback.get_text()
    assert fallback.find(class_="hll") is not None


def test_directive_argument_lists_override_language_defaults(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-code:: cpp
   :compileargs: ['-Wall', '-Wextra', '-pedantic', '-std=c++11']
   :runargs: --sample one

   int main() { return 0; }
""",
        conf_extra=(
            'tb_code_language_defaults = {"cpp": {"compileargs": ["-std=c++17"], "linkargs": ["-lm"]}}\n'
        ),
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    config = json.loads(soup.find("script", class_="tb-code__config").string)
    assert config["parameters"]["compileargs"] == ["-Wall", "-Wextra", "-pedantic", "-std=c++11"]
    assert config["parameters"]["linkargs"] == ["-lm"]
    assert config["parameters"]["runargs"] == ["--sample", "one"]


def test_language_defaults_can_use_jobe_language_id(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-code:: c++

   int main() { return 0; }
""",
        conf_extra='tb_code_language_defaults = {"cpp": {"compileargs": ["-std=c++11"]}}\n',
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    config = json.loads(soup.find("script", class_="tb-code__config").string)
    assert config["jobeLanguage"] == "cpp"
    assert config["parameters"]["compileargs"] == ["-std=c++11"]


def test_text_builder_preserves_source(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        """
Title
=====

.. tb-code:: python3
   :caption: Static listing

   print("Hello")
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "Static listing" in text
    assert 'print("Hello")' in text


def test_web_component_contract():
    source = Path("src/sphinx_touchbook/static/tb-code.js").read_text(encoding="utf-8")
    assert 'customElements.define("tb-code", TbCode)' in source
    assert "fetchWithTimeout" in source
    assert "AbortController" in source
    assert "languagePreloadsByEndpoint" in source
    assert "this.preloadSupportedLanguages();" in source
    assert source.index("this.renderControls();") < source.index("this.preloadSupportedLanguages();")
    assert "Checking language support..." in source
    assert source.index("this.setBusy(true") < source.index("await this.fetchSupportedLanguages()")
    assert "run_spec" in source
    assert "language_id" in source
    assert "sourcecode" in source
    assert "toggleEditor" in source
    assert "hideEditLabel" in source
    assert "captureCurrentRevision" in source
    assert "loadRevision" in source
    assert "revisionSlider.type = \"range\"" in source
    assert "resetButton" not in source
    assert "resetCode" not in source
    assert "resetLabel" not in source
    assert 'role", "status"' in source
    assert "Math.random" not in source
