tb-match
========

The ``tb-match`` directive creates a matching question.
Authors provide normal prompt content followed by one definition list.
Each definition-list term is a source item.
Each definition is the matching target.

HTML renders each source item beside a dropdown list of definitions. Students
choose one definition for each source item, then use ``Check Me`` to evaluate
the matches. Authors can add distractor definitions that appear as dropdown
choices but do not match any source item.

Synopsis
--------

The general format of the ``tb-match`` directive is:

.. code-block:: rst

   .. tb-match::
      :optional parameter: value

      + --- Prompt area ---
      |
      | question text and optional Sphinx content
      |
      + --- Pair area ---
      |
      | source item
      |    matching target
      |
      | another source item
      |    another matching target
      |
      + -----------------

Options
-------

**distractors**
   ``String``. Optional.
   Additional definitions that do not match any source item. Separate multiple
   distractors with semicolons or continuation lines. Dropdown choices are
   sorted by visible definition text, so distractors do not always appear after
   the matching definitions.

**name**
   ``String``. Optional.
   Sphinx reference name for this matching question.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

Accessibility behavior
----------------------

HTML uses native select controls so keyboard and assistive technology behavior
comes from the browser. The result text uses a status region so assistive
technology can announce the result after checking.

Fallback behavior
-----------------

HTML without JavaScript renders source and target content in the page.
Text and PDF-oriented builders render the prompt, a source list, and a target
list. The source and target lists are separated so printed output does not
serve as an answer key.

Examples
--------

Example 1: Terms and meanings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: match-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-match::

            Match each term with its meaning.

            compiler
               Translates source code into executable code.

            interpreter
               Executes source code directly.

            linker
               Combines object files into a program.

   .. tb-tab:: Rendered

      .. tb-match::

         Match each term with its meaning.

         compiler
            Translates source code into executable code.

         interpreter
            Executes source code directly.

         linker
            Combines object files into a program.

Example 2: SQL clauses
~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: match-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-match::
            :distractors:
               Sorts rows after filtering
               Groups rows by value

            Match each SQL clause with its purpose.

            ``SELECT``
               Chooses output columns.

            ``FROM``
               Names the source table.

            ``WHERE``
               Filters rows before they appear in the result.

   .. tb-tab:: Rendered

      .. tb-match::
         :distractors:
            Sorts rows after filtering
            Groups rows by value

         Match each SQL clause with its purpose.

         ``SELECT``
            Chooses output columns.

         ``FROM``
            Names the source table.

         ``WHERE``
            Filters rows before they appear in the result.

Example 3: Simple Code
~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: match-ex3-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-match::

            Match the function declaration to an example of its function call.

            int times_two(double x, string y)
               times_two(4.5,"hello");

            int times_two(string x, double y)
               times_two("hello", 10);

            int times_two(string x, string y)
               times_two("hello", "there");

            int times_two(int x, int y)
               times_two(4,7);

   .. tb-tab:: Rendered

      .. tb-match::

         Match the function declaration to an example of its function call.

         int times_two(double x, string y)
            times_two(4.5,"hello");

         int times_two(string x, double y)
            times_two("hello", 10);

         int times_two(string x, string y)
            times_two("hello", "there");

         int times_two(int x, int y)
            times_two(4,7);
