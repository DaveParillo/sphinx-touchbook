from __future__ import annotations

import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from sphinx.application import Sphinx

from sphinx_touchbook.directives.video import DEFAULT_HEIGHT, DEFAULT_WIDTH, TbVideoDirective
from sphinx_touchbook.nodes import TbVideoNode


def parse_rst(source: str):
    parser = Parser()
    settings = get_default_settings(Parser)
    document = new_document("<test>", settings=settings)
    previous = directives._directives.get("tb-video")
    directives.register_directive("tb-video", TbVideoDirective)
    try:
        parser.parse(source, document)
    finally:
        if previous is None:
            directives._directives.pop("tb-video", None)
        else:
            directives._directives["tb-video"] = previous
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


def read_latex_output(outdir: Path) -> str:
    tex_files = sorted(path for path in outdir.glob("*.tex") if path.name != "sphinxmessages.sty")
    assert tex_files
    return tex_files[0].read_text(encoding="utf-8")


def test_directive_parses_defaults_and_notes():
    document = parse_rst(
        """
.. tb-video:: https://www.youtube.com/watch?v=aqz-KE-bpKQ

   Start at 1:15 for the worked example.
"""
    )

    node = next(document.findall(TbVideoNode))
    assert node["source_url"] == "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    assert node["provider"] == "youtube"
    assert node["kind"] == "iframe"
    assert node["embed_url"] == "https://www.youtube.com/embed/aqz-KE-bpKQ"
    assert node["thumbnail_url"] == "https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg"
    assert node["window"] is False
    assert node["width"] == DEFAULT_WIDTH
    assert node["height"] == DEFAULT_HEIGHT
    assert node["has_notes"] is True
    assert "Start at 1:15" in node.astext()


def test_directive_accepts_dimensions_and_window_flag():
    document = parse_rst(
        """
.. tb-video:: https://vimeo.com/486845755
   :name: lecture-video
   :width: 640
   :height: 360
   :window:

   Jump to the review question.
"""
    )

    node = next(document.findall(TbVideoNode))
    assert node["ids"] == ["lecture-video"]
    assert node["names"] == ["lecture-video"]
    assert node["provider"] == "vimeo"
    assert node["kind"] == "iframe"
    assert node["embed_url"] == "https://player.vimeo.com/video/486845755"
    assert node["thumbnail_url"] == "https://vumbnail.com/486845755.jpg"
    assert node["window"] is True
    assert node["width"] == "640"
    assert node["height"] == "360"


def test_directive_accepts_thumbnail_override():
    document = parse_rst(
        """
.. tb-video:: media/lecture-01.mp4
   :thumbnail: media/lecture-01.png
"""
    )

    node = next(document.findall(TbVideoNode))
    assert node["provider"] == "local"
    assert node["kind"] == "video"
    assert node["thumbnail_url"] == "media/lecture-01.png"


def test_directive_accepts_local_webm_video():
    document = parse_rst(
        """
.. tb-video:: _static/Baby_Chick_Hatching.webm
"""
    )

    node = next(document.findall(TbVideoNode))
    assert node["provider"] == "local"
    assert node["kind"] == "video"
    assert node["source_url"] == "_static/Baby_Chick_Hatching.webm"
    assert node["embed_url"] == "_static/Baby_Chick_Hatching.webm"


def test_directive_accepts_local_ogv_video():
    document = parse_rst(
        """
.. tb-video:: _static/wilms-tumor-ct-scan.ogv
"""
    )

    node = next(document.findall(TbVideoNode))
    assert node["provider"] == "local"
    assert node["kind"] == "video"
    assert node["source_url"] == "_static/wilms-tumor-ct-scan.ogv"
    assert node["embed_url"] == "_static/wilms-tumor-ct-scan.ogv"


def test_directive_normalizes_youtube_embed_to_watch_url():
    document = parse_rst(
        """
.. tb-video:: https://www.youtube.com/embed/aqz-KE-bpKQ?start=75
"""
    )

    node = next(document.findall(TbVideoNode))
    assert node["provider"] == "youtube"
    assert node["source_url"] == "https://www.youtube.com/watch?v=aqz-KE-bpKQ&t=75s"
    assert node["embed_url"] == "https://www.youtube.com/embed/aqz-KE-bpKQ?start=75"


@pytest.mark.parametrize(
    "url,provider,embed_url",
    [
        (
            "https://canvas.example.edu/courses/1/external_tools/2",
            "canvas",
            "https://canvas.example.edu/courses/1/external_tools/2",
        ),
        (
            "https://odysee.com/@example/video:abc",
            "odysee",
            "https://odysee.com/$/embed/@example/video:abc",
        ),
    ],
)
def test_directive_detects_other_provider_urls(url, provider, embed_url):
    document = parse_rst(
        f"""
.. tb-video:: {url}
"""
    )

    node = next(document.findall(TbVideoNode))
    assert node["provider"] == provider
    assert node["kind"] == "iframe"
    assert node["embed_url"] == embed_url


def test_html_build_emits_placeholder_and_config(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-video:: https://www.youtube.com/watch?v=aqz-KE-bpKQ
   :name: video-example
   :width: 640
   :height: 360

   Fast-forward to 1:15 for the worked example.
""",
    )

    html = (outdir / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("tb-video", id="video-example")
    assert element is not None
    assert element["provider"] == "youtube"
    assert element["kind"] == "iframe"
    assert element["source-url"] == "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    assert "--tb-video-width: 640px" in element["style"]
    assert "--tb-video-height: 360px" in element["style"]
    assert "--tb-video-aspect-ratio: 640 / 360" in element["style"]
    assert element.find("figure", class_="tb-video__fallback") is not None
    placeholder = element.find("a", class_="tb-video__placeholder")
    assert placeholder["href"] == "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    assert placeholder.get_text(strip=True) == "Open video"
    thumbnail = element.find("img", class_="tb-video__thumbnail")
    assert thumbnail["src"] == "https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg"
    assert thumbnail["alt"] == ""
    assert "Fast-forward to 1:15" in element.find("div", class_="tb-video__notes").get_text(" ", strip=True)
    config = json.loads(element.find("script", class_="tb-video__config").string)
    assert config["sourceUrl"] == "https://www.youtube.com/watch?v=aqz-KE-bpKQ"
    assert config["embedUrl"] == "https://www.youtube.com/embed/aqz-KE-bpKQ"
    assert config["thumbnailUrl"] == "https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg"
    assert config["provider"] == "youtube"
    assert config["kind"] == "iframe"
    assert config["width"] == "640"
    assert config["height"] == "360"
    assert (outdir / "_static" / "tb-video.js").exists()
    assert (outdir / "_static" / "tb-video.css").exists()
    assert "tb-video.js" in html
    assert "tb-video.css" in html
    css = (outdir / "_static" / "tb-video.css").read_text(encoding="utf-8")
    assert ".tb-video__fallback" in css
    assert "width: var(--tb-video-width, 100%);" in css
    assert ".tb-video__player" in css
    assert ".tb-video__unsupported" in css
    assert "@media (prefers-color-scheme: dark)" in css


def test_html_build_emits_native_video_for_local_webm(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-video:: _static/Baby_Chick_Hatching.webm
   :name: local-webm
   :width: 360
   :height: 202.5
""",
    )

    html = (outdir / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("tb-video", id="local-webm")
    assert element is not None
    assert element["provider"] == "local"
    assert element["kind"] == "video"
    assert element["source-url"] == "_static/Baby_Chick_Hatching.webm"
    assert "--tb-video-width: 360px" in element["style"]
    assert "--tb-video-height: 202.5px" in element["style"]
    assert "--tb-video-aspect-ratio: 360 / 202.5" in element["style"]
    assert element.find("a", class_="tb-video__placeholder")["href"] == "_static/Baby_Chick_Hatching.webm"
    config = json.loads(element.find("script", class_="tb-video__config").string)
    assert config["kind"] == "video"
    assert config["embedUrl"] == "_static/Baby_Chick_Hatching.webm"


def test_html_build_emits_native_video_for_local_ogv(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-video:: _static/wilms-tumor-ct-scan.ogv
   :name: local-ogv
""",
    )

    html = (outdir / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("tb-video", id="local-ogv")
    assert element is not None
    assert element["provider"] == "local"
    assert element["kind"] == "video"
    assert element["source-url"] == "_static/wilms-tumor-ct-scan.ogv"
    config = json.loads(element.find("script", class_="tb-video__config").string)
    assert config["kind"] == "video"
    assert config["embedUrl"] == "_static/wilms-tumor-ct-scan.ogv"


def test_html_build_resolves_static_video_relative_to_nested_page(tmp_path):
    srcdir = tmp_path / "src"
    outdir = tmp_path / "_build_html"
    doctreedir = tmp_path / "_doctree_html"
    components = srcdir / "components"
    components.mkdir(parents=True)
    (srcdir / "conf.py").write_text(
        'extensions = ["sphinx_touchbook"]\n'
        'html_theme = "alabaster"\n',
        encoding="utf-8",
    )
    (srcdir / "index.rst").write_text(
        """
Title
=====

.. toctree::

   components/video
""",
        encoding="utf-8",
    )
    (components / "video.rst").write_text(
        """
Video
=====

.. tb-video:: _static/Baby_Chick_Hatching.webm
   :name: nested-local-webm
""",
        encoding="utf-8",
    )
    app = Sphinx(
        srcdir=str(srcdir),
        confdir=str(srcdir),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername="html",
        warningiserror=True,
        freshenv=True,
    )
    app.build()

    soup = BeautifulSoup((outdir / "components" / "video.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-video", id="nested-local-webm")
    assert element["source-url"] == "../_static/Baby_Chick_Hatching.webm"
    assert element["embed-url"] == "../_static/Baby_Chick_Hatching.webm"
    assert element.find("a", class_="tb-video__placeholder")["href"] == "../_static/Baby_Chick_Hatching.webm"
    config = json.loads(element.find("script", class_="tb-video__config").string)
    assert config["sourceUrl"] == "../_static/Baby_Chick_Hatching.webm"
    assert config["embedUrl"] == "../_static/Baby_Chick_Hatching.webm"


def test_text_builder_renders_url_and_notes(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "text",
        """
Title
=====

.. tb-video:: media/lecture-01.mp4

   Notes for the lecture video.
""",
    )

    text = (outdir / "index.txt").read_text(encoding="utf-8")
    assert "Video URL: media/lecture-01.mp4" in text
    assert "Notes for the lecture video." in text


def test_latex_builder_renders_url_and_notes(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        """
Title
=====

.. tb-video:: https://vimeo.com/486845755

   Notes for the lecture video.
""",
    )

    latex = read_latex_output(outdir)
    assert "Video URL: https://vimeo.com/486845755" in latex
    assert "Notes for the lecture video." in latex
    assert r"\begin{sphinxadmonition}{note}{Video}" in latex


def test_html_build_uses_configured_default_dimensions(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-video:: https://www.youtube.com/watch?v=aqz-KE-bpKQ
""",
        conf_extra=(
            'tb_video_default_width = "800"\n'
            'tb_video_default_height = "450"\n'
        ),
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    config = json.loads(soup.find("script", class_="tb-video__config").string)
    element = soup.find("tb-video")
    assert config["width"] == "800"
    assert config["height"] == "450"
    assert "style" not in element.attrs


def test_html_build_omitted_dimensions_use_full_width_fallback(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-video:: https://vimeo.com/486845755
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    element = soup.find("tb-video")
    assert "style" not in element.attrs
