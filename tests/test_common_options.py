from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup
from sphinx.application import Sphinx


def read_latex(outdir: Path) -> str:
    return next(outdir.glob("*.tex")).read_text(encoding="utf-8")


def build_sphinx(tmp_path: Path, builder: str, index: str) -> Path:
    srcdir = tmp_path / "src"
    outdir = tmp_path / f"_build_{builder}"
    doctreedir = tmp_path / f"_doctree_{builder}"
    srcdir.mkdir()
    (srcdir / "conf.py").write_text(
        'extensions = ["sphinx_touchbook"]\n'
        'html_theme = "alabaster"\n',
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


def test_touchbook_directives_accept_class_common_option(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

.. tb-reveal::
   :class: reveal-class shared-class

   Reveal content.

.. tb-group::
   :class: group-class

   .. tb-tab:: First
      :class: tab-class

      Tab content.

.. tb-video:: https://vimeo.com/486845755
   :class: video-class

.. tb-file::
   :filename: class-file.txt
   :class: file-class

   File content.

.. tb-code:: python
   :class: code-class

   print("hello")

.. tb-choice::
   :class: choice-class

   Choose one.

   - [x] Correct
   - [ ] Incorrect

.. tb-blank::
   :class: blank-class

   Type {{blank}}.

   .. tb-answer::
      :match: yes

.. tb-formula::
   :class: formula-class
   :variables: x=1..2

   What is {{x}}?

   .. answer-formula::

      x

.. tb-match::
   :class: match-class

   Match each term.

   a
      alpha

   b
      beta

.. tb-micro-parsons::
   :class: micro-parsons-class

   Arrange the tokens.

   - a
   - b

.. tb-order::
   :class: order-class

   Put these in order.

   - first
   - second

.. tb-parsons::
   :class: parsons-class

   Construct the program.

   ::

      first()
      second()

.. tb-click::
   :class: click-class

   Select ``a``.

   .. code-block:: none

      abc

   .. tb-hit:: a
      :class: hit-class

      Correct.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    expected = {
        "tb-reveal": ["reveal-class", "shared-class"],
        "tb-group": ["group-class"],
        "tb-tab": ["tab-class"],
        "tb-video": ["video-class"],
        "tb-file": ["file-class"],
        "tb-code": ["code-class"],
        "tb-choice": ["choice-class"],
        "tb-blank": ["blank-class"],
        "tb-formula": ["formula-class"],
        "tb-match": ["match-class"],
        "tb-micro-parsons": ["micro-parsons-class"],
        "tb-order": ["order-class"],
        "tb-parsons": ["parsons-class"],
        "tb-click": ["click-class"],
    }
    for tag, classes in expected.items():
        element = soup.find(tag)
        assert element is not None, tag
        for css_class in classes:
            assert css_class in element.get("class", []), tag

    feedback = soup.find("div", class_="tb-click__feedback")
    assert feedback is not None
    assert "hit-class" in feedback.get("class", [])


def test_touchbook_directive_targets_are_preserved_in_html(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "html",
        """
Title
=====

See :ref:`explicit code target <explicit-code-target>`,
:ref:`named code target <named-code-target>`,
:ref:`explicit group target <explicit-group-target>`, and
:ref:`named group target <named-group-target>`.

.. _explicit-code-target:

.. tb-code:: python
   :name: named-code-target

   print("hello")

.. _explicit-group-target:

.. tb-group::
   :name: named-group-target

   .. tb-tab:: Rendered

      Group content.
""",
    )

    soup = BeautifulSoup((outdir / "index.html").read_text(encoding="utf-8"), "html.parser")
    for node_id in (
        "explicit-code-target",
        "named-code-target",
        "explicit-group-target",
        "named-group-target",
    ):
        assert soup.find(id=node_id) is not None, node_id
        assert soup.find("a", href=f"#{node_id}") is not None, node_id


def test_touchbook_directive_targets_are_preserved_in_latex(tmp_path):
    outdir = build_sphinx(
        tmp_path,
        "latex",
        """
Title
=====

See :ref:`explicit code target <explicit-code-target>`,
:ref:`named code target <named-code-target>`,
:ref:`explicit group target <explicit-group-target>`, and
:ref:`named group target <named-group-target>`.

.. _explicit-code-target:

.. tb-code:: python
   :name: named-code-target

   print("hello")

.. _explicit-group-target:

.. tb-group::
   :name: named-group-target

   .. tb-tab:: Rendered

      Group content.
""",
    )

    latex = read_latex(outdir)
    for node_id in (
        "explicit-code-target",
        "named-code-target",
        "explicit-group-target",
        "named-group-target",
    ):
        assert f"index:{node_id}" in latex
