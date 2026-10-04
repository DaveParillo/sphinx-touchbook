from __future__ import annotations

from io import StringIO
from pathlib import Path
import subprocess
import sys

import pytest
from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document

from sphinx_touchbook.directives.array import TbArrayDirective
from sphinx_touchbook.nodes import TbArrayNode


def parse_rst(source):
    settings = get_default_settings(Parser)
    settings.warning_stream = StringIO()
    document = new_document("array.rst", settings=settings)
    previous = directives._directives.get("tb-array")
    directives.register_directive("tb-array", TbArrayDirective)
    try:
        Parser().parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-array", None)
        else:
            directives._directives["tb-array"] = previous
    return document


def array_source(body="", options="", key=""):
    return f".. tb-array:: {key}\n{options}\n\n" + "\n".join(f"   {line}" for line in body.splitlines()) + "\n"


def test_values_preserve_spelling_quotes_comments_and_empty_strings():
    document = parse_rst(array_source(
        r'''7 -3 2.50 1e+2 'dark blue' "# literal" 'it\'s' 'a\\b' '' # comment
'<script> & **literal**' '''))
    node = next(document.findall(TbArrayNode))
    assert [item["value"] for item in node["elements"]] == [
        "7", "-3", "2.50", "1e+2", "dark blue", "# literal", "it's", "a\\b", "",
        "<script> & **literal**",
    ]
    assert node["mode"] == "unkeyed"
    assert node["key"] is None
    assert node["orientation"] == "horizontal"
    assert node["show_keys"] is False
    assert node["start_index"] == 0
    assert node.source == "array.rst"


def test_keys_highlights_and_range_are_normalized_separately_from_targets():
    document = parse_rst(array_source("b = 3\na = 7\nc = 9", """   :name: document-target
   :class: first second
   :caption: A caption
   :label: Values
   :highlight: values.item[a] values.slot[2] values.item[a]
   :range: 0:2
   :range-label: Sorted prefix""", "values"))
    node = next(document.findall(TbArrayNode))
    assert node["key"] == "values"
    assert node["ids"] == ["document-target"]
    assert node["classes"] == ["first", "second"]
    assert [item["key"] for item in node["elements"]] == ["b", "a", "c"]
    assert node["highlighted"] == [1, 2]
    assert node["range"] == [0, 2]
    assert node["caption"] == "A caption"


def test_newline_escape_and_literal_backslash_n_are_distinct():
    document = parse_rst(array_source(r'''"dark\ngreen" 'light\nblue' "literal\\n" "\n\n"'''))
    node = next(document.findall(TbArrayNode))
    assert [item["value"] for item in node["elements"]] == [
        "dark\ngreen", "light\nblue", r"literal\n", "\n\n",
    ]


@pytest.mark.parametrize("body", ["", "# empty\n\n# still empty"])
def test_empty_arrays_and_empty_ranges(body):
    document = parse_rst(array_source(body, "   :range: 0:0"))
    node = next(document.findall(TbArrayNode))
    assert node["elements"] == []
    assert node["mode"] == "unkeyed"
    assert node["range"] == [0, 0]


@pytest.mark.parametrize("body,options,key,message", [
    ("a = 7\n3 9", "", "", "mix keyed and unkeyed"),
    ("a = 7\na = 3", "", "", "Duplicate array item"),
    ("null = 3", "", "", "Invalid array key"),
    ("7", "", "null", "Invalid array key"),
    ("7", "", "bad.key", "Invalid array key"),
    ("hello world", "", "", "numbers or quoted strings"),
    ("a = 7 3", "", "", "exactly one value"),
    ("a = # no value", "", "", "exactly one value"),
    ("'broken", "", "", "Unterminated string"),
    (r"'bad\t'", "", "", "Invalid string escape"),
    ("01", "", "", "invalid value or punctuation"),
    ("7;3", "", "", "invalid value or punctuation"),
    ("'a''b'", "", "", "Separate array values"),
    ("7", "   :highlight: values.slot[0]", "", "explicit array object key"),
    ("7", "   :highlight: other.slot[0]", "values", "Invalid local"),
    ("7", "   :highlight: values.end", "values", "Invalid local"),
    ("7", "   :highlight: values.slot[1]", "values", "out of bounds"),
    ("7", "   :highlight: values.slot[01]", "values", "Invalid local"),
    ("7", "   :highlight: values.slot[a]", "values", "Invalid slot index"),
    ("7", "   :highlight: values.item[a]", "values", "Unknown keyed"),
    ("a = 7", "   :highlight: values.item[b]", "values", "Unknown keyed"),
    ("7", "   :range: 1:0", "", "0 <= start"),
    ("7", "   :range: 0:2", "", "0 <= start"),
    ("7", "   :range: :1", "", "half-open"),
    ("7", "   :range: -1:1", "", "half-open"),
    ("7", "   :range: 0 : 1", "", "half-open"),
    ("7", "   :range-label: Sorted", "", "requires :range:"),
    (".. note::", "", "", "numbers or quoted strings"),
])
def test_invalid_arrays_report_context(body, options, key, message):
    document = parse_rst(array_source(body, options, key))
    assert not list(document.findall(TbArrayNode))
    error = next(document.findall(nodes.system_message))
    assert message in error.astext()
    assert "tb-array" in error.astext()
    assert error["line"] >= 1


def test_unknown_and_repeated_options_are_rejected():
    for options in ("   :id: legacy", "   :label: One\n   :label: Two",
                    "   :orientation: diagonal", "   :orientation:",
                    "   :show-keys: true", "   :show-keys: false",
                    "   :start-index: abc", "   :start-index: 1.5",
                    "   :start-index:"):
        document = parse_rst(array_source("7", options))
        assert not list(document.findall(TbArrayNode))
        assert list(document.findall(nodes.system_message))


def build_sphinx(tmp_path: Path, builder, source, *, tagged=False):
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text(
        'extensions = ["sphinx_touchbook"]\nhtml_theme = "alabaster"\n'
        + f'tb_pdf_tagging = {tagged!r}\n')
    (src / "index.rst").write_text(source)
    out = tmp_path / "out"
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-E", "-W", "-b", builder, str(src), str(out)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return out


BUILD_SOURCE = r'''
Arrays
======

See :ref:`the array <array-target>` and :ref:`external target <external-target>`.

.. _external-target:

.. tb-array:: values
   :name: array-target
   :class: custom first
   :caption: A caption & example
   :label: Values
   :show-keys:
   :highlight: values.item[b]
   :range: 0:2
   :range-label: Sorted prefix

   a = '<script>alert("x")</script>'
   b = 7
   c = 'a_b%&#{}'

.. tb-array::
   :range: 0:0
'''


def test_html_is_static_accessible_escaped_and_has_unique_targets(tmp_path):
    out = build_sphinx(tmp_path, "html", BUILD_SOURCE)
    soup = BeautifulSoup((out / "index.html").read_text(), "html.parser")
    assert len(soup.find_all("tb-array")) == 2
    array = soup.find("tb-array", id="array-target")
    assert array["data-key"] == "values"
    assert array["class"] == ["custom", "first"]
    assert not array.find("script")
    assert '<script>alert("x")</script>' in array.get_text()
    assert array.find("caption").get_text() == "A caption & example"
    assert array.select_one(".tb-array__label").get_text() == "Values"
    assert not array.select("p.tb-array__caption")
    assert [header.get_text() for header in array.select('th[scope="col"]')] == ["0", "1", "2"]
    highlighted = array.select_one(".tb-array__cell--highlighted")
    assert highlighted.get_text().endswith("Sorted prefix")
    assert "Highlighted" not in array.get_text()
    assert highlighted["aria-description"] == "Highlighted"
    assert len(array.select(".tb-array__cell--range")) == 2
    assert array.select_one('[tabindex="0"]')["aria-label"] == "Values scroll area"
    assert "Empty array" in soup.find_all("tb-array")[1].get_text()
    for target in ("external-target", "array-target"):
        assert len(soup.find_all(id=target)) == 1
        assert soup.find("a", href=f"#{target}")
    assert soup.find("link", href=lambda href: href and "tb-array.css" in href)


@pytest.mark.parametrize("builder", ["html", "text", "latex"])
def test_labels_and_captions_are_only_rendered_when_explicit(tmp_path, builder):
    source = "Display options\n===============\n\n"
    cases = []
    for empty in (False, True):
        for label, caption in ((False, False), (True, False), (False, True), (True, True)):
            index = len(cases)
            options = []
            if label:
                options.append(f"   :label: Explicit label {index}")
            if caption:
                options.append(f"   :caption: Explicit caption {index}")
            source += array_source("" if empty else "7 8", "\n".join(options)) + "\n\n"
            cases.append((empty, label, caption))
    out = build_sphinx(tmp_path, builder, source)
    if builder == "latex":
        filename = next(out.glob("*.tex"))
    else:
        filename = out / ("index.html" if builder == "html" else "index.txt")
    result = filename.read_text()
    if builder == "html":
        arrays = BeautifulSoup(result, "html.parser").find_all("tb-array")
        assert len(arrays) == len(cases)
        for index, (array, (empty, label, caption)) in enumerate(zip(arrays, cases)):
            assert len(array.select(".tb-array__label")) == int(label)
            assert len(array.select("caption, .tb-array__caption")) == int(caption)
            assert "Array" not in array.get_text()
            if label:
                assert array.get_text().count(f"Explicit label {index}") == 1
            if caption:
                assert array.get_text().count(f"Explicit caption {index}") == 1
                assert bool(array.find("caption")) == (not empty)
    else:
        assert "Array" not in result
        for index, (_, label, caption) in enumerate(cases):
            assert result.count(f"Explicit label {index}") == int(label)
            assert result.count(f"Explicit caption {index}") == int(caption)


@pytest.mark.parametrize("builder", ["text", "latex"])
def test_non_html_builds_preserve_values_keys_and_annotations(tmp_path, builder):
    out = build_sphinx(tmp_path, builder, BUILD_SOURCE)
    filename = out / "index.txt" if builder == "text" else next(out.glob("*.tex"))
    result = filename.read_text()
    for text in ("Values", "Highlighted", "Sorted prefix", "Empty array", "Index", "Key", "Notes"):
        assert text in result
    assert "tb-array" not in result
    if builder == "latex":
        assert "index:array-target" in result and "index:external-target" in result
        assert r"\%" in result
        assert "longtable" in result or "tabular" in result
    else:
        assert '<script>alert("x")</script>' in result


@pytest.mark.parametrize("orientation", ["horizontal", "vertical"])
@pytest.mark.parametrize("show_keys", [False, True])
@pytest.mark.parametrize("start_index", [-3, 1])
def test_orientation_and_key_visibility(tmp_path, orientation, show_keys, start_index):
    options = (f"   :orientation: {orientation}\n   :start-index: {start_index}"
               "\n   :highlight: values.slot[1]\n   :range: 0:1")
    if show_keys:
        options += "\n   :show-keys:"
    source = array_source("a = 7\nb = 3", options, "values")
    node = next(parse_rst(source).findall(TbArrayNode))
    assert node["orientation"] == orientation
    assert node["show_keys"] is show_keys
    assert node["start_index"] == start_index
    out = build_sphinx(tmp_path, "html", "Layout\n======\n\n" + source)
    array = BeautifulSoup((out / "index.html").read_text(), "html.parser").find("tb-array")
    assert [cell.get_text() for cell in array.select(".tb-array__value")] == ["7", "3"]
    assert [key.get_text() for key in array.select(".tb-array__key")] == (
        ["Key: a", "Key: b"] if show_keys else [])
    assert len(array.select("tbody tr")) == (2 if orientation == "vertical" else 1)
    if orientation == "vertical":
        assert [header.get_text() for header in array.select('tbody th[scope="row"]')] == [
            str(start_index), str(start_index + 1)]
        assert [header.get_text() for header in array.select('thead th[scope="col"]')] == ["Index", "Value"]
    else:
        assert [header.get_text() for header in array.select('thead th[scope="col"]')] == [
            str(start_index), str(start_index + 1)]
    assert array.select_one(".tb-array__range").get_text() == f"Range [{start_index}, {start_index + 1})"
    assert array.select_one(".tb-array__cell--highlighted .tb-array__value").get_text() == "3"
    assert "Highlighted" not in array.get_text()
    assert array.select_one(".tb-array__cell--highlighted")["aria-description"] == "Highlighted"
    assert not array.select_one(".tb-array__cell--highlighted .tb-array__annotation")
    assert array.select_one(".tb-array__cell--range .tb-array__value").get_text() == "7"


@pytest.mark.parametrize("builder", ["text", "latex"])
@pytest.mark.parametrize("show_keys", [False, True])
def test_non_html_key_visibility(tmp_path, builder, show_keys):
    options = "   :orientation: vertical\n   :highlight: values.item[hidden_key]"
    if show_keys:
        options += "\n   :show-keys:"
    source = "Keys\n====\n\n" + array_source("hidden_key = 7", options, "values")
    out = build_sphinx(tmp_path, builder, source)
    filename = out / "index.txt" if builder == "text" else next(out.glob("*.tex"))
    result = filename.read_text()
    key = "hidden_key" if builder == "text" else r"hidden\_key"
    assert (key in result) is show_keys
    assert "Highlighted" in result


@pytest.mark.parametrize("builder", ["text", "latex"])
def test_non_html_start_index(tmp_path, builder):
    source = "Offset\n======\n\n" + array_source(
        "7 8", "   :start-index: 101\n   :range: 0:1")
    out = build_sphinx(tmp_path, builder, source)
    filename = out / "index.txt" if builder == "text" else next(out.glob("*.tex"))
    result = filename.read_text()
    assert result.count("101") == 2 and result.count("102") == 2
    assert "Range [101, 102)" in result.replace("{[}", "[")


@pytest.mark.parametrize("builder", ["html", "text"])
def test_long_array_preserves_all_entries(tmp_path, builder):
    source = "Long array\n==========\n\n" + array_source(" ".join(map(str, range(150))))
    out = build_sphinx(tmp_path, builder, source)
    result = (out / ("index.html" if builder == "html" else "index.txt")).read_text()
    assert "149" in result
    if builder == "html":
        soup = BeautifulSoup(result, "html.parser")
        assert len(soup.select("tb-array td")) == 150


@pytest.mark.parametrize("builder", ["html", "text", "latex"])
def test_newline_values_render_with_line_breaks(tmp_path, builder):
    source = "Line breaks\n===========\n\n" + array_source(r'''"dark\ngreen" "literal\\n"''')
    out = build_sphinx(tmp_path, builder, source)
    filename = next(out.glob("*.tex")) if builder == "latex" else out / (
        "index.html" if builder == "html" else "index.txt")
    result = filename.read_text()
    if builder == "html":
        soup = BeautifulSoup(result, "html.parser")
        assert [value.get_text() for value in soup.select(".tb-array__value")] == [
            "dark\ngreen", r"literal\n"]
        css = (out / "_static" / "tb-array.css").read_text()
        assert "white-space: pre-wrap" in css
    elif builder == "text":
        assert "dark" in result and "green" in result
        assert not any("dark" in line and "green" in line for line in result.splitlines())
        assert r"literal\n" in result
    else:
        assert r"\begin{DUlineblock}" in result
        assert r"\item[] dark" in result and r"\item[] green" in result


def test_array_works_with_tagged_pdf_translator(tmp_path):
    out = build_sphinx(tmp_path, "latex", BUILD_SOURCE, tagged=True)
    result = next(out.glob("*.tex")).read_text()
    assert result.startswith(r"\DocumentMetadata{lang=en-US,tagging=on}")
    assert "Highlighted" in result and "Sorted prefix" in result
    assert "table/header-rows" in result
