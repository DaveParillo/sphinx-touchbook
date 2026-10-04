.. _tb-array:

tb-array
========

The ``tb-array`` directive displays an ordered array with zero-based indices.
Values can be numbers or quoted strings. Optional item keys identify entries
independently of their values and positions. Authors can highlight entries and
label one half-open range of slots.

Synopsis
--------

The general format of ``tb-array`` is:

.. code-block:: rst

   .. tb-array:: [optional object key]
      :optional parameter: value

      + --- Array data ---
      |
      | whitespace-separated values, or one key = value row per item
      |
      + ------------------

The object key is optional for an independent array. An explicit key is required
when ``highlight`` references its slots or items. It is separate from ``name``,
which creates a Sphinx reference target.

Options
-------

**caption**
   ``String``. Optional.
   Plain-text caption displayed with the array.

**class**
   ``String``. Optional.
   Space-separated CSS class names. This is a
   `Docutils common option
   <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   See :ref:`common` for details.

**highlight**
   ``String``. Optional.
   Space-separated references to this array's entries. Use
   ``values.slot[0]`` for a position or ``values.item[a]`` for a keyed item.
   Requires an explicit object key, here ``values``. All references must resolve
   to existing entries. Highlighting does not depend on color alone.

**label**
   ``String``. Optional.
   Plain-text object label. Displayed only when explicitly provided.

**name**
   ``String``. Optional.
   Sphinx reference target for this array occurrence. It does not supply an
   object key. This is a
   `Docutils common option
   <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   See :ref:`common` for details.

**orientation**
   ``horizontal`` or ``vertical``. Optional. Defaults to ``horizontal``.
   HTML displays entries across columns by default. Use ``vertical`` to
   display one entry per row. Indices and entry order stay the same.

**range**
   ``String``. Optional.
   One half-open interval written as ``start:end``. For example, ``0:2``
   includes slots 0 and 1. Both bounds are required, nonnegative integers.
   The start must not exceed the end, and the end must not exceed the array
   length. An empty interval such as ``2:2`` is valid.

**range-label**
   ``String``. Optional.
   Plain-text description of the interval, such as ``Sorted prefix``.
   Requires ``range``. Entries in an unlabeled range show ``In range``.

**show-keys**
   ``Flag``. Optional. Disabled by default.
   Display item keys with their values. Write ``:show-keys:`` without a value.
   Hidden keys still identify items in highlight references. This option has
   no effect on unkeyed arrays.

**start-index**
   ``Integer``. Optional. Defaults to ``0``. Negative integers are allowed.
   Set the displayed index of the first entry. Subsequent indices increase
   by one. Slot references and ``:range:`` bounds remain zero-based positions;
   displayed range descriptions use the shifted indices. Item keys are unchanged.

Data syntax
-----------

Unkeyed values are separated by spaces or tabs. Multiple lines continue the
same array. Numbers retain their spelling, including decimal and exponent
forms. Quote all other values with single or double quotes. Empty strings and
Unicode text are allowed. Escape the enclosing quote or backslash, or use
``\n`` to insert a line break within a value:

.. code-block:: text

   7 -3 2.50 1e2 'dark blue' "dark\ngreen" "it's" 'it\'s' 'a\\b' ''

Use one assignment per line for keyed items:

.. code-block:: text

   a = 7
   b = 3
   c = 'nine'

Keys are case-sensitive identifiers beginning with a letter or underscore,
followed by letters, digits, underscores, or hyphens. The key ``null`` is
reserved. Item keys must be unique. Keyed and unkeyed rows cannot be mixed.
Equal values are allowed; values never supply identity.

Blank lines and ``#`` comments outside strings are ignored. An empty or
comment-only body displays an empty array. Semicolons, literal multiline strings,
negative slot indices, omitted range bounds, and other string escapes such as
``\t`` are rejected. The data body contains literal values, not nested RST.
Write ``\\n`` within a string to display a literal backslash followed by ``n``.

Click questions
---------------

Use a keyed array as the source of :ref:`tb-click` to ask students to select
items. ``tb-hit`` and ``tb-miss`` select local item keys, independently of
values and displayed indices. See :ref:`tb-click` for an array question example.

Accessibility behavior
----------------------

HTML uses a table with index headers. Captions and object labels appear only
when explicitly provided. Highlighted entries have a thicker outline and an
accessible description, without additional visible text. Range entries show
their range label or ``In range``. Item keys appear only with ``:show-keys:``. Wide arrays
can be scrolled horizontally with the keyboard. These are static displays with
no execution or editing controls.

Fallback behavior
-----------------

HTML displays the complete array without JavaScript. Text and PDF display a
vertical table with indices, values, optional keys, and highlight/range notes.
The text and PDF layout is vertical regardless of ``:orientation:``;
keys appear only with ``:show-keys:``.
Line breaks in values are preserved. Text shows continuation lines with a
blank index rather than repeating the entry's index.
Captions, labels, empty arrays, and range descriptions are preserved in all
three formats.

Examples
--------

Example 1: An independent array
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-array::

            7 3 9 5

   .. tb-tab:: Rendered

      .. tb-array::

         7 3 9 5

Example 2: Strings and comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-array::
            :caption: Color names

            'red' "dark blue"  # Spaces stay inside a string.
            'green' "dark\ngreen"

   .. tb-tab:: Rendered

      .. tb-array::
         :caption: Color names

         'red' "dark blue"  # Spaces stay inside a string.
         'green' "dark\ngreen"

Example 3: Keyed items and highlights
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-array:: values
            :label: Values
            :show-keys:
            :highlight: values.item[b] values.slot[2]

            a = 7
            b = 3
            c = 9

   .. tb-tab:: Rendered

      .. tb-array:: values
         :label: Values
         :show-keys:
         :highlight: values.item[b] values.slot[2]

         a = 7
         b = 3
         c = 9

Example 4: A labeled range
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-array::
            :range: 0:2
            :range-label: Sorted prefix

            3 7 9 5

   .. tb-tab:: Rendered

      .. tb-array::
         :range: 0:2
         :range-label: Sorted prefix

         3 7 9 5

Example 5: An empty array
~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-array::
            :label: Empty sequence
            :range: 0:0

   .. tb-tab:: Rendered

      .. tb-array::
         :label: Empty sequence
         :range: 0:0

Example 6: A named reference target
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-array::
            :name: array-reference-example
            :class: sample-array

            10 20

   .. tb-tab:: Rendered

      .. tb-array::
         :name: array-reference-example
         :class: sample-array

         10 20

Refer to the last example with :ref:`this array <array-reference-example>`.

Example 7: A vertical array
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-array::
            :orientation: vertical
            :start-index: 1

            10 20 30

   .. tb-tab:: Rendered

      .. tb-array::
         :orientation: vertical
         :start-index: 1

         10 20 30
