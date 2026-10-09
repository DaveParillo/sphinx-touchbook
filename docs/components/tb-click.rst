.. _tb-click:

tb-click
========

The ``tb-click`` directive creates a click-on-source question.
Authors provide normal prompt content, exactly one source block, and
one or more ``tb-hit`` or ``tb-miss`` regions.

Use ``tb-hit`` for correct clickable regions.
Use ``tb-miss`` for incorrect clickable regions with feedback.
Use a code-block, literal block, :ref:`tb-array`, or :ref:`tb-graph` as the
source. Selectors are case-sensitive: text selectors match source text;
array and graph selectors match local item or node keys.

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
      | exactly one code-block, literal block, tb-array, or tb-graph
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

For code and literal blocks, use these text selectors:

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

For arrays and graphs, give the bare local key to ``tb-hit`` or ``tb-miss``.
For example, ``.. tb-hit:: middle`` selects the item or node named ``middle``.
Keys identify targets independently of displayed values and indices. Repeated
values can receive different feedback. An array source must declare keyed
items, such as ``middle = 13``. A graph source uses node keys, such as
``middle[13]``. The source's object key is optional.

Each selected key must exist in the source and appear in only one ``tb-hit``
or ``tb-miss``. Invisible graph nodes cannot be selected. Graph relationships,
indicator labels, and array indices are not selectable targets. Items and nodes
without a region remain ordinary source content. Text selector prefixes do not
apply to arrays or graphs. At least one ``tb-hit`` is required for every source
type.

Options
-------

**class**
   ``String`` or ``List``. Optional.
   A CSS class to add to the directive.
   See :ref:`common` for details.

**name**
   ``String``. Optional.
   Sphinx reference name for this click question.
   See :ref:`common` for details.

**show-hints**
   ``Boolean``. Optional.
   If present, clickable source regions start with hint styling visible.
   By default, clickable regions match surrounding source text until focus,
   selection state, or the user chooses to show hints.
   For graph sources, hints draw dashed borders around selectable nodes.
   They identify both correct and incorrect choices without changing node
   fills or outlining nodes that cannot be selected. Selected nodes keep
   their feedback styling when hints are toggled.

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

HTML renders text regions and array items as native buttons. Graph nodes are
focusable controls in the diagram; press Enter or Space to select a focused
node. Accessible labels identify keyed targets by their keys and values.
The selected region receives visible state, feedback is shown, and result text
uses a status region so assistive technology can announce the result after a
click. Clickable
regions have neutral accessible labels before selection, so correctness is not
revealed before the user answers.

Fallback behavior
-----------------

HTML without JavaScript retains the prompt and source. Selecting targets and
revealing feedback requires JavaScript. Text and PDF-oriented builders render
the prompt and source only: arrays retain their tables, and graphs retain their
PDF diagrams or text descriptions. If a diagram cannot be generated, HTML shows
the graph's description and buttons for its selected keys.
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

Example 4: Select an array item by key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The two middle values are equal. The keys distinguish their positions without
making the displayed value or index part of the answer selector.

.. tb-group::
   :name: click-ex4-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-click::

            Select the first occurrence of 13.

            .. tb-array::

               first = 8
               second = 13
               third = 13
               fourth = 21

            .. tb-hit:: second

               This is the first occurrence of 13, at index 1.

            .. tb-miss:: third

               This is the second occurrence of 13, at index 2.

            .. tb-miss:: first

               This item's value is 8.

            .. tb-miss:: fourth

               This item's value is 21.

   .. tb-tab:: Rendered

      .. tb-click::

         Select the first occurrence of 13.

         .. tb-array::

            first = 8
            second = 13
            third = 13
            fourth = 21

         .. tb-hit:: second

            This is the first occurrence of 13, at index 1.

         .. tb-miss:: third

            This is the second occurrence of 13, at index 2.

         .. tb-miss:: first

            This item's value is 8.

         .. tb-miss:: fourth

            This item's value is 21.

Example 5: Select a tree node by key
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Graph keys select nodes in the diagram. The same selector syntax works with
all graph styles, including ``array`` and ``ring``.

.. tb-group::
   :name: click-ex5-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-click::

            Select the right child of the root.

            .. tb-graph::
               :style: tree

               root[8] -left-> left[3]
               root -right-> right[12]

            .. tb-hit:: right

               Node 12 is the right child of root 8.

            .. tb-miss:: left

               Node 3 is the left child of root 8.

            .. tb-miss:: root

               Node 8 is the root, not one of its children.

   .. tb-tab:: Rendered

      .. tb-click::

         Select the right child of the root.

         .. tb-graph::
            :style: tree

            root[8] -left-> left[3]
            root -right-> right[12]

         .. tb-hit:: right

            Node 12 is the right child of root 8.

         .. tb-miss:: left

            Node 3 is the left child of root 8.

         .. tb-miss:: root

            Node 8 is the root, not one of its children.
