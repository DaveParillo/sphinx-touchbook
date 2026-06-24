from __future__ import annotations

import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError

from sphinx_touchbook.directives.code import DEFAULT_ENDPOINT, DEFAULT_FILES_ENDPOINT, DEFAULT_LANGUAGES_ENDPOINT, TbCodeDirective
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


def build_sphinx_files(
    tmp_path: Path,
    builder: str,
    files: dict[str, str],
    conf_extra: str = "",
) -> Path:
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
    for relative_path, content in files.items():
        path = srcdir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
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


def read_latex_output(outdir: Path) -> str:
    tex_files = sorted(path for path in outdir.glob("*.tex") if path.name != "sphinxmessages.sty")
    assert tex_files
    return tex_files[0].read_text(encoding="utf-8")


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
    assert node["revision_label"] == "Source version"
    assert node["run_before_names"] == []
    assert node["run_after_names"] == []
    assert node["run_before"] == []
    assert node["run_after"] == []
    assert node["show_tutor"] is False


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
   :hidden:

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
    assert node["hidden"] is True
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
   :show-tutor:

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
    assert config["filesEndpoint"] == DEFAULT_FILES_ENDPOINT
    assert config["languagesEndpoint"] == DEFAULT_LANGUAGES_ENDPOINT
    assert config["validateLanguage"] is True
    assert config["runLabel"] == "Execute"
    assert config["editLabel"] == "Change"
    assert config["hideEditLabel"] == "Done"
    assert config["revisionLabel"] == "Version"
    assert config["showTutor"] is True
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
            'tb_code_files_endpoint = "https://example.test/files/"\n'
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
    assert config["filesEndpoint"] == "https://example.test/files/"
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
            'tb_code_block_defaults = {"linenos": True, "lineno-start": 25, "emphasize-lines": "2", "class": ["from-conf"]}\n'
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


def test_include_replaces_placeholders_from_named_tb_code_and_code_block(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-code:: cpp
   :name: account-methods
   :hidden:

   public:
     int balance() const;

.. code-block:: cpp
   :name: account-fields

   private:
     int balance_;

.. tb-code:: cpp
   :name: account-class
   :include:
      PUBLIC_MEMBERS: account-methods
      PRIVATE_MEMBERS: account-fields

   class account {
     {{PUBLIC_MEMBERS}}
     {{PRIVATE_MEMBERS}}
   };
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    assert soup.find("tb-code", id="account-methods") is None
    element = soup.find("tb-code", id="account-class")
    config = json.loads(element.find("script", class_="tb-code__config").string)
    assert config["source"] == (
        "class account {\n"
        "  public:\n"
        "    int balance() const;\n"
        "  private:\n"
        "    int balance_;\n"
        "};"
    )
    assert "{{PUBLIC_MEMBERS}}" not in element.get_text()
    assert "int balance() const;" in element.get_text()
    assert "int balance_;" in element.get_text()


def test_run_before_and_run_after_are_execution_only_fragments(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-code:: cpp
   :name: test-header
   :hidden:

   #include <cassert>

.. code-block:: cpp
   :name: test-main

   int main() {
     assert(answer() == 42);
   }

.. tb-code:: cpp
   :name: answer-function
   :run-before: test-header
   :run-after: test-main

   int answer() {
     return 42;
   }
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    assert soup.find("tb-code", id="test-header") is None
    element = soup.find("tb-code", id="answer-function")
    config = json.loads(element.find("script", class_="tb-code__config").string)
    assert config["source"] == "int answer() {\n  return 42;\n}"
    assert config["runBefore"] == ["#include <cassert>"]
    assert config["runAfter"] == ["int main() {\n  assert(answer() == 42);\n}"]
    assert "#include <cassert>" not in element.get_text()
    assert "assert(answer() == 42)" not in element.get_text()
    assert "int answer()" in element.get_text()


def test_include_replaces_placeholder_from_named_literalinclude(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. literalinclude:: account-methods.cpp
   :name: account-methods
   :language: cpp

.. tb-code:: cpp
   :name: account-class
   :include: PUBLIC_MEMBERS: account-methods

   class account {
     {{PUBLIC_MEMBERS}}
   };
""",
            "account-methods.cpp": """
public:
  int balance() const;
""".lstrip(),
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-code", id="account-class")
    config = json.loads(element.find("script", class_="tb-code__config").string)
    assert config["source"] == (
        "class account {\n"
        "  public:\n"
        "    int balance() const;\n"
        "};"
    )
    assert "{{PUBLIC_MEMBERS}}" not in config["source"]


def test_include_replaces_placeholder_from_captioned_named_literalinclude(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. literalinclude:: account-fields.cpp
   :name: account-fields
   :caption: Account fields
   :language: cpp

.. tb-code:: cpp
   :name: account-class
   :include: PRIVATE_MEMBERS: account-fields

   class account {
     {{PRIVATE_MEMBERS}}
   };
""",
            "account-fields.cpp": """
private:
  int balance_;
""".lstrip(),
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-code", id="account-class")
    config = json.loads(element.find("script", class_="tb-code__config").string)
    assert config["source"] == (
        "class account {\n"
        "  private:\n"
        "    int balance_;\n"
        "};"
    )
    assert "{{PRIVATE_MEMBERS}}" not in config["source"]


def test_text_builder_uses_included_code(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        """
Title
=====

.. code-block:: python
   :name: helper-function

   def helper():
       return 42

.. tb-code:: python
   :include: HELPER: helper-function

   {{HELPER}}

   print(helper())
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "def helper():" in text
    assert "print(helper())" in text
    assert "{{HELPER}}" not in text


def test_hidden_tb_code_is_available_for_includes_but_not_rendered_in_text(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        """
Title
=====

.. tb-code:: python
   :name: hidden-helper
   :hidden:

   def helper():
       return 42

.. tb-code:: python
   :include: HELPER: hidden-helper

   {{HELPER}}

   print(helper())
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert text.count("def helper():") == 1
    assert "print(helper())" in text
    assert "{{HELPER}}" not in text


def test_include_replaces_placeholders_from_named_code_in_another_document(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. toctree::

   fragments
   example
""",
            "fragments.rst": """
Fragments
=========

.. tb-code:: cpp
   :name: account-methods
   :hidden:

   public:
     int balance() const;

.. code-block:: cpp
   :name: account-fields

   private:
     int balance_;
""",
            "example.rst": """
Example
=======

.. tb-code:: cpp
   :name: account-class
   :include:
      PUBLIC_MEMBERS: account-methods
      PRIVATE_MEMBERS: account-fields

   class account {
     {{PUBLIC_MEMBERS}}
     {{PRIVATE_MEMBERS}}
   };
""",
        },
    )

    soup = BeautifulSoup((outdir / "example.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-code", id="account-class")
    config = json.loads(element.find("script", class_="tb-code__config").string)
    assert "int balance() const;" in config["source"]
    assert "int balance_;" in config["source"]
    assert "{{PUBLIC_MEMBERS}}" not in config["source"]
    assert "{{PRIVATE_MEMBERS}}" not in config["source"]
    fragments = BeautifulSoup((outdir / "fragments.html").read_text(encoding="utf-8"), "html.parser")
    assert fragments.find("tb-code", id="account-methods") is None


def test_tb_code_attaches_named_tb_files(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-file::
   :filename: input.txt
   :hidden:

   Alice Bob

.. tb-code:: python
   :name: file-reader
   :files: input.txt

   print(open("input.txt").read())
""",
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    assert soup.find("tb-file") is None
    element = soup.find("tb-code", id="file-reader")
    config = json.loads(element.find("script", class_="tb-code__config").string)
    assert config["files"] == [
        {
            "filename": "input.txt",
            "content": "Alice Bob",
            "data_url": None,
            "mime_type": "text/plain",
            "is_text": True,
            "editable": True,
        }
    ]


def test_tb_code_attaches_tb_files_from_another_document(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. toctree::

   files
   example
""",
            "files.rst": """
Files
=====

.. tb-file::
   :filename: data/input.txt
   :hidden:

   42
""",
            "example.rst": """
Example
=======

.. tb-code:: python
   :name: cross-doc-file-reader
   :files: data/input.txt

   print(open("data/input.txt").read())
""",
        },
    )

    soup = BeautifulSoup((outdir / "example.html").read_text(encoding="utf-8"), "html.parser")
    config = json.loads(soup.find("tb-code", id="cross-doc-file-reader").find("script", class_="tb-code__config").string)
    assert config["files"][0]["filename"] == "data/input.txt"
    assert config["files"][0]["content"] == "42"


def test_tb_code_missing_file_reference_warns(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-code:: python
   :files: missing.txt

   print("missing")
""",
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    config = json.loads(soup.find("tb-code").find("script", class_="tb-code__config").string)
    assert config["files"] == []


def test_duplicate_include_fragment_names_stop_the_build(tmp_path):
    with pytest.raises(ExtensionError, match="duplicate tb-code include fragment name"):
        build_sphinx_files(
            tmp_path,
            "html",
            {
                "index.rst": """
Title
=====

.. toctree::

   first
   second
""",
                "first.rst": """
First
=====

.. tb-code:: python
   :name: duplicate-fragment

   print("first")
""",
                "second.rst": """
Second
======

.. code-block:: python
   :name: duplicate-fragment

   print("second")
""",
            },
        )


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


def test_latex_builder_uses_pygments_highlighting(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        """
Title
=====

.. tb-code:: python
   :caption: Static listing

   print("Hello")
""",
    )

    latex = read_latex_output(outdir)
    assert "Static listing" in latex
    assert r"\begin{sphinxVerbatim}" in latex
    assert r"\PYG" in latex
    assert "Hello" in latex


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
    assert "createRuntimeInput" in source
    assert "runtimeParameters" in source
    assert "splitArguments" in source
    assert "tb-code__runtime-input" in source
    assert "resetButton" not in source
    assert "resetCode" not in source
    assert "resetLabel" not in source
    assert 'role", "status"' in source
    assert "Math.random" not in source
