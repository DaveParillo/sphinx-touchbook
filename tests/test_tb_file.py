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

from sphinx_touchbook.directives.file import TbFileDirective, validate_filename, validate_source_reference
from sphinx_touchbook.nodes import TbFileNode


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-file")
    directives.register_directive("tb-file", TbFileDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-file", None)
        else:
            directives._directives["tb-file"] = previous
    return document


def build_sphinx_files(
    tmp_path: Path,
    builder: str,
    files: dict[str, str | bytes],
) -> Path:
    _app, outdir = build_sphinx_app(tmp_path, builder, files)
    return outdir


def build_sphinx_app(
    tmp_path: Path,
    builder: str,
    files: dict[str, str | bytes],
) -> tuple[Sphinx, Path]:
    srcdir = tmp_path / "src"
    outdir = tmp_path / f"_build_{builder}"
    doctreedir = tmp_path / f"_doctree_{builder}"
    srcdir.mkdir()
    (srcdir / "conf.py").write_text(
        'extensions = ["sphinx_touchbook"]\n'
        'html_theme = "alabaster"\n',
        encoding="utf-8",
    )
    for relative_path, content in files.items():
        path = srcdir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
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
    return app, outdir


def read_latex_output(outdir: Path) -> str:
    tex_files = sorted(path for path in outdir.glob("*.tex") if path.name != "sphinxmessages.sty")
    assert tex_files
    return tex_files[0].read_text(encoding="utf-8")


def test_directive_parses_inline_text_file():
    document = parse_rst(
        """
.. tb-file::
   :name: sample-file
   :filename: data/input.txt

   Alice
   Bob
"""
    )

    node = next(document.findall(TbFileNode))
    assert node["ids"] == ["sample-file"]
    assert node["names"] == ["sample-file"]
    assert node["filename"] == "data/input.txt"
    assert node["content"] == "Alice\nBob"
    assert node["is_text"] is True
    assert node["editable"] is True


def test_directive_rejects_invalid_filenames():
    document = parse_rst(
        """
.. tb-file::
   :filename: ../secret.txt

   hidden
"""
    )

    assert not list(document.findall(TbFileNode))
    assert any("tb-file filename" in message.astext() for message in document.findall() if message.tagname == "system_message")


@pytest.mark.parametrize(
    "filename",
    [
        "input.txt",
        "data/input-file.txt",
        "data/input_file.txt",
        "nested/path/sample-1_2.txt",
    ],
)
def test_filename_validation_accepts_allowed_characters(filename):
    assert validate_filename(filename) == filename


@pytest.mark.parametrize(
    "filename",
    [
        "/tmp/file.txt",
        "data//input.txt",
        "data/./input.txt",
        "data/../input.txt",
        "data/input text.txt",
        "data/input.txt?",
    ],
)
def test_filename_validation_rejects_unsafe_or_invalid_paths(filename):
    with pytest.raises(ValueError, match="tb-file filename"):
        validate_filename(filename)


@pytest.mark.parametrize(
    "source_reference",
    [
        "/tmp/sample.txt",
        "./sample.txt",
        "nested/../sample.txt",
    ],
)
def test_file_reference_rejects_unsafe_source_paths(source_reference):
    with pytest.raises(ValueError, match="tb-file source file references"):
        validate_source_reference(source_reference)


def test_file_reference_accepts_nested_relative_source_path():
    assert validate_source_reference("data/sample.txt") == "data/sample.txt"


def test_html_build_emits_text_file_custom_element_and_assets(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-file::
   :name: input-file
   :filename: input.txt

   Alice Bob
""",
        },
    )

    html = (outdir / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("tb-file", id="input-file")
    assert element is not None
    assert element["filename"] == "input.txt"
    assert element.find("figcaption", class_="tb-file__caption").get_text(strip=True) == "input.txt"
    assert element.find("pre", class_="tb-file__content").get_text(strip=True) == "Alice Bob"
    config = json.loads(element.find("script", class_="tb-file__config").string)
    assert config["filename"] == "input.txt"
    assert config["content"] == "Alice Bob"
    assert config["isText"] is True
    assert config["editable"] is True
    assert (outdir / "_static" / "tb-file.js").exists()
    assert (outdir / "_static" / "tb-file.css").exists()
    assert "tb-file.js" in html
    assert "tb-file.css" in html


def test_registry_contains_visible_text_file_metadata(tmp_path):
    app, _outdir = build_sphinx_app(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-file::
   :filename: input.txt

   Alice Bob
""",
        },
    )

    file_info = app.env.tb_files["input.txt"]
    assert file_info["docname"] == "index"
    assert file_info["filename"] == "input.txt"
    assert file_info["content"] == "Alice Bob"
    assert file_info["mime_type"] == "text/plain"
    assert file_info["is_text"] is True
    assert file_info["data_url"] is None


def test_html_build_reads_text_file_reference(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-file:: sample.txt
   :filename: data/sample.txt
""",
            "sample.txt": "from referenced file\n",
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    config = json.loads(soup.find("script", class_="tb-file__config").string)
    assert config["filename"] == "data/sample.txt"
    assert config["content"] == "from referenced file\n"
    assert config["mimeType"] == "text/plain"


def test_missing_file_reference_reports_directive_error():
    document = parse_rst(
        """
.. tb-file:: missing.txt
   :filename: missing.txt
"""
    )

    assert not list(document.findall(TbFileNode))
    assert any(
        "tb-file source file 'missing.txt' does not exist" in message.astext()
        for message in document.findall()
        if message.tagname == "system_message"
    )


def test_html_build_embeds_image_file_reference(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-file:: images/pic.svg
   :filename: images/pic.svg
""",
            "images/pic.svg": '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"></svg>\n',
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-file")
    image = element.find("img", class_="tb-file__image")
    assert image is not None
    assert image["src"].startswith("data:image/svg+xml;base64,")
    config = json.loads(element.find("script", class_="tb-file__config").string)
    assert config["filename"] == "images/pic.svg"
    assert config["isText"] is False
    assert config["dataUrl"].startswith("data:image/svg+xml;base64,")
    assert config["editable"] is False


def test_html_build_embeds_binary_png_file_reference(tmp_path):
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
        b"\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-file:: images/pic.png
   :filename: images/pic.png
""",
            "images/pic.png": png_bytes,
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    config = json.loads(soup.find("script", class_="tb-file__config").string)
    assert config["mimeType"] == "image/png"
    assert config["isText"] is False
    assert config["editable"] is False
    assert config["dataUrl"].startswith("data:image/png;base64,")


def test_html_build_marks_non_image_binary_file_readonly(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-file:: docs/sample.pdf
   :filename: docs/sample.pdf
   :editable:
""",
            "docs/sample.pdf": b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n",
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-file")
    assert element["editable"] == "false"
    assert element.find("p", class_="tb-file__binary").get_text(strip=True) == "Binary file: docs/sample.pdf (application/pdf)"
    config = json.loads(element.find("script", class_="tb-file__config").string)
    assert config["mimeType"] == "application/pdf"
    assert config["isText"] is False
    assert config["editable"] is False
    assert config["dataUrl"].startswith("data:application/pdf;base64,")


def test_hidden_file_is_registered_but_not_rendered(tmp_path):
    app, outdir = build_sphinx_app(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-file::
   :filename: hidden.txt
   :hidden:

   secret
""",
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    assert soup.find("tb-file") is None
    assert app.env.tb_files["hidden.txt"]["content"] == "secret"


def test_duplicate_file_filenames_stop_the_build(tmp_path):
    with pytest.raises(ExtensionError, match="duplicate tb-file filename"):
        build_sphinx_files(
            tmp_path,
            "html",
            {
                "index.rst": """
Title
=====

.. tb-file::
   :filename: input.txt

   first

.. tb-file::
   :filename: input.txt

   second
""",
            },
        )


def test_duplicate_file_filenames_across_documents_stop_the_build(tmp_path):
    with pytest.raises(ExtensionError, match="duplicate tb-file filename"):
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

.. tb-file::
   :filename: input.txt

   first
""",
                "second.rst": """
Second
======

.. tb-file::
   :filename: input.txt

   second
""",
            },
        )


def test_readonly_text_file_disables_editor_in_config(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "html",
        {
            "index.rst": """
Title
=====

.. tb-file::
   :filename: readonly.txt
   :readonly:

   do not edit
""",
        },
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-file")
    assert element["editable"] == "false"
    config = json.loads(element.find("script", class_="tb-file__config").string)
    assert config["editable"] is False


def test_text_builder_preserves_text_file(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "text",
        {
            "index.rst": """
Title
=====

.. tb-file::
   :filename: input.txt

   Alice
""",
        },
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "[input.txt]" in text
    assert "Alice" in text


def test_text_builder_skips_hidden_file(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "text",
        {
            "index.rst": """
Title
=====

.. tb-file::
   :filename: hidden.txt
   :hidden:

   secret
""",
        },
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "hidden.txt" not in text
    assert "secret" not in text


def test_latex_builder_preserves_visible_text_file(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "latex",
        {
            "index.rst": """
Title
=====

.. tb-file::
   :filename: input.txt

   Alice
""",
        },
    )

    latex = read_latex_output(outdir)
    assert "input.txt" in latex
    assert "Alice" in latex


def test_latex_builder_skips_hidden_file(tmp_path):
    outdir = build_sphinx_files(
        tmp_path,
        "latex",
        {
            "index.rst": """
Title
=====

.. tb-file::
   :filename: hidden.txt
   :hidden:

   secret
""",
        },
    )

    latex = read_latex_output(outdir)
    assert "hidden.txt" not in latex
    assert "secret" not in latex
