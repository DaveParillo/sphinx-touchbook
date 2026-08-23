.. _tb-reveal:

tb-reveal
=========

The ``tb-reveal`` directive hides content until a reader asks to show it.

Synopsis
--------

The general format of the ``tb-reveal`` directive is:

.. code-block:: rst

   .. tb-reveal:: [title]

      + --- Content area ---
      |
      | one or more lines of initially hidden content
      | which can include any Touchbook or Sphinx supported directives.
      |
      + --------------------

The content area is required.

Options
-------

**class**
   ``String`` or ``List``. Optional.
   A CSS class to add to the directive.
   See :ref:`common` for details.

**name**
   ``String``. Optional.
   Sphinx reference name for this reveal block.
   See :ref:`common` for details.

**title**
   ``String``. Optional.
   The disclosure control label. The default is ``Details``.

Sphinx configuration options
----------------------------

No directive-specific configuration options exist.

Accessibility behavior
----------------------

The no-JS HTML fallback uses native ``details`` and ``summary``. HTML uses a
native ``button`` and synchronizes ``aria-expanded`` and ``aria-controls``.

Fallback behavior
-----------------

PDF and text builders render the content as labeled static content.

Examples
--------

Example 1: Basic reveal
~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: reveal-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-reveal::

            This content starts out hidden.

            - *Any* valid `Sphinx markup <http://www.sphinx-doc.org>`__ can be
              included.
            - Select Details to show or hide the content.

   .. tb-tab:: Rendered

      .. tb-reveal::

         This content starts out hidden.

         - *Any* valid `Sphinx markup <http://www.sphinx-doc.org>`__ can be
           included.
           - Select Details to show or hide the content.

Example 2: Title and nested content
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: reveal-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-reveal:: Explanation
            :name: re-ex2

            The reveal block can contain other directives. This example uses a
            standard Sphinx code block:

            .. code-block:: python

               print("Hello, world")

            and a ``tb-code`` block:

            .. tb-code:: python

               print("Hello, world")

   .. tb-tab:: Rendered

      .. tb-reveal:: Explanation
         :name: re-ex2

         The reveal block can contain other directives. This example uses a
         standard Sphinx code block:

         .. code-block:: python

            print("Hello, world")

         and a ``tb-code`` block:

         .. tb-code:: python

            print("Hello, world")
