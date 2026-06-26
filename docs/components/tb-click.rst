tb-click
========

The ``tb-click`` directive creates a click-on-source question.
Authors provide normal prompt content, exactly one literal source block, and
one or more ``tb-hit`` or ``tb-miss`` regions.

Use ``tb-hit`` for correct clickable regions.
Use ``tb-miss`` for incorrect clickable regions with feedback.
Selectors are exact, case-sensitive matches against the source text.

Synopsis
--------

The general format of the ``tb-click`` directive is:

.. code-block:: rst

   .. tb-click::
      :optional parameter: value

      + --- Prompt area ---
      |
      | question text and optional Sphinx content
      |
      + --- Source area ---
      |
      | exactly one code-block or literal block
      |
      + --- Region area ---
      |
      | .. tb-hit:: selector
      |
      |    feedback for a correct click
      |
      | .. tb-miss:: selector
      |
      |    feedback for an incorrect click
      |
      + -------------------

Selector Forms
--------------

Bare selector
   A bare selector is the same as ``text:``.
   It selects the first exact text match.

``text:literal``
   Selects the first exact text match.

``text:literal#n``
   Selects the nth exact text match.

``line:literal``
   Selects the whole line that contains the exact text.

``range:line:start-end``
   Selects a 1-based, inclusive line and column range.
   For example, ``range:3:11-12`` selects columns 11 through 12 on line 3.

Options
-------

**name**
   ``String``. Optional.
   Sphinx reference name for this click question.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

**show-hints**
   ``Boolean``. Optional.
   If present, clickable source regions start with hint styling visible.
   By default, clickable regions match surrounding source text until focus,
   selection state, or the user chooses to show hints.

Sphinx configuration options
----------------------------

**tb_click_show_hints**
   ``Boolean`` or ``"never"``. Optional. Default: ``False``.
   If ``True``, hints are initially shown and the hint button starts with
   ``Hide Hints``. If ``False``, hints are initially hidden and the hint button
   starts with ``Show Hints``. If ``"never"``, hints are not shown and the
   hint button is omitted.

Accessibility behavior
----------------------

HTML renders each clickable source region as a native button. The selected
region receives visible state, feedback is shown, and result text uses a status
region so assistive technology can announce the result after a click. Clickable
regions have neutral accessible labels before selection, so correctness is not
revealed before the user answers.

Fallback behavior
-----------------

HTML without JavaScript renders the prompt, source, and feedback in document
order. Text and PDF-oriented builders render the prompt and source only.
Feedback is omitted from paper-oriented output so the printed document can ask
the complete question without revealing the answer.

Examples
--------

Example 1: SQL operator
~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: click-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-click::

            Click the comparison operator.

            .. code-block:: sql

               SELECT name
               FROM students
               WHERE age >= 18;

            .. tb-hit:: >=

               ``>=`` is the comparison operator.

            .. tb-miss:: line:SELECT name

               This line selects output columns.

            .. tb-miss:: line:FROM students

               This line names the table.

   .. tb-tab:: Rendered

      .. tb-click::

         Click the comparison operator.

         .. code-block:: sql

            SELECT name
            FROM students
            WHERE age >= 18;

         .. tb-hit:: >=

            ``>=`` is the comparison operator.

         .. tb-miss:: line:SELECT name

            This line selects output columns.

         .. tb-miss:: line:FROM students

            This line names the table.

Example 2: C++ token occurrence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: click-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-click::

            Click the second use of ``x``.

            .. code-block:: cpp

               int x = 3;
               x = x + 1;
               std::cout << x;

            .. tb-hit:: text:x#2

               This is the second occurrence of ``x``.

            .. tb-miss:: int

               ``int`` is the type, not the requested occurrence.

   .. tb-tab:: Rendered

      .. tb-click::

         Click the second use of ``x``.

         .. code-block:: cpp

            int x = 3;
            x = x + 1;
            std::cout << x;

         .. tb-hit:: text:x#2

            This is the second occurrence of ``x``.

         .. tb-miss:: int

            ``int`` is the type, not the requested occurrence.

         .. tb-miss:: x = 3;

            This is the first use of ``x`` - the definition.

         .. tb-miss:: x + 1;

            This is the third occurrence of ``x``.

         .. tb-miss:: range:3:10-15

            This is the fourth occurrence of ``x``.



Example 3: Poetry line
~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: click-ex3-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-click::

            Click the line that names the season.

            .. code-block:: text

               The woods are still.
               Autumn gathers at the gate.
               A lantern waits beside the road.

            .. tb-hit:: line:Autumn gathers

               This line names the season.

            .. tb-miss:: line:The woods are still.

               This line describes the setting.

   .. tb-tab:: Rendered

      .. tb-click::

         Click the line that names the season.

         .. code-block:: text

            The woods are still.
            Autumn gathers at the gate.
            A lantern waits beside the road.

         .. tb-hit:: line:Autumn gathers

            This line names the season.

         .. tb-miss:: line:The woods are still.

            This line describes the setting.
