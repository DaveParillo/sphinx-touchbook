tb-reveal
=========

The ``tb-reveal`` directive hides content until a reader asks to show it.

Synopsis
--------

The general format of the ``tb-reveal`` directive is:

.. code-block:: rst

   .. tb-reveal::
      :name: optional-name
      :showlabel: Show
      :hidelabel: Hide
      :modal:
      :modal-titlebar: Message from the author

      Content area

      One or more lines of initially hidden content.
      Content can include ordinary Sphinx markup and directives.

Required content
----------------

content area
   The ``tb-reveal`` directive must contain at least one line of content.

Options
-------

``name``
   ``String``. Optional. Sphinx reference name for this reveal block.
   This is a `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

``showlabel``
   ``String``. Optional. Label for the show button.
   Default is ``Show``.

``hidelabel``
   ``String``. Optional. Label for the hide or close button.
   Default is ``Hide``.

``modal``
   ``Boolean``. Optional.
   If included, the revealed content is presented in a modal dialog.
   The default behavior reveals content inline.

``modal-titlebar``
   ``String``. Optional.
   Text displayed in the modal dialog titlebar and used as the dialog's
   accessible label.
   Default is ``Message from the author``.

Sphinx configuration options
----------------------------

No directive-specific configuration options exist.

Accessibility and fallback behavior
-----------------------------------

The no-JS HTML fallback uses native ``details`` and ``summary``. Inline HTML
uses a native ``button`` and synchronizes ``aria-expanded``. Modal content uses
a native ``dialog`` element when available and includes an accessible dialog
label.

PDF and text builders render the content as labeled static content.

Examples
--------

Example 1: Basic reveal
~~~~~~~~~~~~~~~~~~~~~~~

Source
^^^^^^

.. code-block:: rst

   .. tb-reveal::
      :name: re-ex1

      This content starts out hidden.

      - *Any* valid `Sphinx markup <http://www.sphinx-doc.org>`__ can be included.
      - Hidden content can be shown by using the Show button.
      - When shown, a Hide button appears at the end of the hidden content.

Rendered
^^^^^^^^

.. tb-reveal::
   :name: re-ex1

   This content starts out hidden.

   - *Any* valid `Sphinx markup <http://www.sphinx-doc.org>`__ can be included.
   - Hidden content can be shown by using the Show button.
   - When shown, a Hide button appears at the end of the hidden content.

Example 2: Custom button labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Source
^^^^^^

.. code-block:: rst

   .. tb-reveal::
      :name: re-ex2
      :showlabel: Reveal Content
      :hidelabel: Hide Content

      The reveal block can contain other directives. This example uses a
      standard Sphinx code block until an ``activecode`` directive exists:

      .. code-block:: python

         print("Hello, world")

Rendered
^^^^^^^^

.. tb-reveal::
   :name: re-ex2
   :showlabel: Reveal Content
   :hidelabel: Hide Content

   The reveal block can contain other directives. This example uses a
   standard Sphinx code block until an ``activecode`` directive exists:

   .. code-block:: python

      print("Hello, world")

Example 3: Modal reveal
~~~~~~~~~~~~~~~~~~~~~~~

Source
^^^^^^

.. code-block:: rst

   Given the following C++ statements:

   .. code-block:: cpp

      int  val = 0;
      int& ir  = val;
      auto x   = ir;

   What type is x?

   .. tb-reveal::
      :name: reveal-ex3
      :modal:
      :modal-titlebar: Understanding auto type deduction

      If you said, ``int``, excellent job!

      ``ir`` is a reference to ``val``,
      which makes ``ir`` just another name for ``val``.
      ``auto x = ir;`` is exactly the same as if we had written
      ``auto x = val;`` here.

Rendered
^^^^^^^^

Given the following C++ statements:

.. code-block:: cpp

   int  val = 0;
   int& ir  = val;
   auto x   = ir;

What type is x?

.. tb-reveal::
   :name: reveal-ex3
   :modal:
   :modal-titlebar: Understanding auto type deduction

   If you said, ``int``, excellent job!

   ``ir`` is a reference to ``val``,
   which makes ``ir`` just another name for ``val``.
   ``auto x = ir;`` is exactly the same as if we had written
   ``auto x = val;`` here.
