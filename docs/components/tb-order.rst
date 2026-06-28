tb-order
========

The ``tb-order`` directive creates an ordering question. Authors can include
optional prompt content before one bullet list. Authors write list items in the
correct order. HTML presents the items in a shuffled order and lets students
move them with native Up and Down buttons before checking the answer.

Synopsis
--------

The general format of the ``tb-order`` directive is:

.. code-block:: rst

   .. tb-order::
      :optional parameter: value

      + --- Optional prompt area ---
      |
      | question text and optional Sphinx content
      |
      + --- Ordered item list ---

      - first item in the correct order
      - second item in the correct order
      - third item in the correct order

Options
-------

**name**
   ``String``. Optional.
   Sphinx reference name for this ordering question.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

Accessibility behavior
----------------------

HTML uses native buttons for each reorder action. Each item has an Up button
and a Down button. Buttons are disabled when an item cannot move farther in
that direction. Result text uses a status region so assistive technology can
announce feedback after checking.

Fallback behavior
-----------------

HTML without JavaScript renders the prompt and a deterministic item order with
movement buttons. Text and PDF-oriented builders render the prompt and items as
an ordering question. Static output does not support interactive checking.

Examples
--------

Example 1: Daily sequence
~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: order-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-order::

            Put these events in order.

            - Wake up
            - Eat breakfast
            - Go to class

   .. tb-tab:: Rendered

      .. tb-order::

         Put these events in order.

         - Wake up
         - Eat breakfast
         - Go to class

Example 2: C++ compilation stages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: order-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-order::

            - Write source code
            - Preprocess source files
            - Compile translation units
            - Link object files
            - Run the executable

   .. tb-tab:: Rendered

      .. tb-order::

         - Write source code
         - Preprocess source files
         - Compile translation units
         - Link object files
         - Run the executable
