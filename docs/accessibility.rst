Accessibility And Keyboard Use
==============================

Touchbook directives use native HTML controls wherever possible. Buttons,
inputs, text areas, selects, links, and dialogs keep their browser keyboard
behavior and programmatic labels. This helps assistive technology and lets each
browser expose controls in the way users expect.

Keyboard Basics
---------------

Most Touchbook controls follow standard browser behavior:

* ``Tab`` moves forward through focusable controls.
* ``Shift+Tab`` moves backward through focusable controls.
* ``Enter`` activates links and most buttons.
* ``Space`` activates buttons, checkboxes, radio buttons, and similar controls.
* Arrow keys may move within composite widgets, such as tab groups.

Tab Groups
----------

The ``tb-group`` directive renders an ARIA tab interface. Only the selected tab
is in the normal ``Tab`` order. This is intentional and follows the common
roving-tabindex pattern for tabs.

When focus is on a tab:

* ``ArrowRight`` moves to the next tab.
* ``ArrowLeft`` moves to the previous tab.
* ``Home`` moves to the first tab.
* ``End`` moves to the last tab.
* ``Tab`` moves into the selected tab panel when that panel contains a
  focusable control.

For example, if a ``tb-group`` has ``Source`` and ``Rendered`` tabs, ``Tab``
does not normally move from ``Source`` to ``Rendered``. Use the arrow keys to
select ``Rendered``. Then use ``Tab`` to enter the rendered content.

Platform Settings
-----------------

Keyboard navigation can depend on operating system and browser settings. If
``Tab`` skips buttons or other native controls, check the platform settings
before assuming the page is broken.

macOS
   In System Settings, open **Keyboard** and enable full keyboard navigation.
   Safari also has a browser-specific setting in **Advanced** named
   **Press Tab to highlight each item on a webpage**.

   When full keyboard access is disabled, macOS browsers may require
   ``Option+Tab`` or ``Alt+Tab`` to move to buttons and other controls.

Windows
   Windows browsers usually include buttons in the normal ``Tab`` order. If
   navigation seems incomplete, check browser accessibility settings and any
   installed keyboard or assistive-technology utilities. In Microsoft Edge and
   Chrome, also check whether caret browsing or extension settings are changing
   keyboard behavior.

Linux
   Linux behavior depends on the desktop environment, browser, and assistive
   technology stack. GNOME, KDE, Firefox, Chrome, and Chromium usually include
   native buttons in the normal ``Tab`` order. If they do not, check desktop
   keyboard accessibility settings, browser settings, and screen-reader or
   extension configuration.

Testing Guidance
----------------

When testing Touchbook content for keyboard accessibility:

* Test with full keyboard navigation enabled.
* Confirm that every visible control can receive focus.
* Confirm that visible focus is easy to see.
* Activate buttons with ``Space`` and ``Enter``.
* Test ``tb-group`` tabs with arrow keys, not only with ``Tab``.
* Test the static fallback output when building text or PDF formats.

Touchbook should provide accessible controls and predictable focus behavior.
Operating system and browser settings can still change how users move through
native controls.

Experimental Tagged PDF
-----------------------

Touchbook provides an opt-in LuaLaTeX tagging profile. Enable it in ``conf.py``:

.. code-block:: python

   tb_pdf_tagging = True
   tb_pdf_language = "en-US"

The profile is being tested with Sphinx 9.1 and TeX Live 2026. It requires
LaTeX's current ``DocumentMetadata`` tagging support; older distribution
packages may not work. It selects LuaLaTeX and supplies document metadata
before the document class loads. Do not add a second ``DocumentMetadata``
command in your preamble.
For upstream package compatibility, consult the
`LaTeX tagging project instructions <https://tagging-project.latex-project.org/documentation/usage-instructions>`__.

The profile requests title display in PDF viewers and structure-based link
tab order. Actual navigation depends on the PDF viewer. Native LaTeX tagging
provides heading, paragraph, list, table, figure, caption, and link structures.
Some tag names use role mappings to standard PDF roles rather than literal
names such as ``H1`` and ``P``.

.. rubric:: Tagging tips

- Supply meaningful ``:alt:`` text on instructional images, including
  ``tb-file`` images.
- Missing image descriptions produce a ``touchbook.pdf_alt`` warning.
- Mark purely decorative images with ``:class: tb-pdf-artifact``.

  Do not apply this class to instructional content.

The PDF-specific Pygments style darkens the default palette until every token
foreground reaches at least 4.5:1 contrast against both white and the gray
highlight background. HTML colors do not change. The optional
``tb_pdf_pygments_style`` setting accepts a Pygments style name or import path.

Compatibility changes affect layout: the profile uses native headings instead
of ``titlesec``/``fncychap``, booktabs tables without row striping, native
footnotes, and unframed topic and admonition boxes. It installs a custom LaTeX
translator and should not be combined with another extension that replaces
that translator without integration testing.

This is not a PDF/UA compliance claim. Complex tables, mathematics, raw LaTeX,
third-party diagrams, and other extensions need separate validation. Authors
remain responsible for meaningful descriptions, correct heading hierarchy,
table headers, reading order, and accessible source content. Validate the
compiled PDF with a PDF accessibility checker and assistive technology.
Avoid treating a successful compile or the presence of tags as proof of
accessible output.

The ``tests/pdf`` checks metadata, headings, lists, links, tables, images, code
captions, footnotes, TOC, and index.
The ``audit.py`` script inspects the compiled structure tree with ``pypdf``;
it is not a real conformance validator.

