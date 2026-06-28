tb-parsons
==========

The ``tb-parsons`` directive creates a Parsons problem. Authors write the
fragments in the correct order. HTML shuffles the fragments and lets students
move, indent, outdent, use, or skip each fragment before checking the answer.

Synopsis
--------

The general format of the ``tb-parsons`` directive is:

.. code-block:: rst

   .. tb-parsons::
      :optional parameter: value

      + --- Optional prompt area ---
      |
      | question text and optional Sphinx content
      |
      + --- Source block in correct order ---

      .. code-block:: language

         first fragment
         {{group}}
             grouped fragment line one
             grouped fragment line two
         {{endgroup}}
         {{distractor}}
             optional distractor fragment

Options
-------

**name**
   ``String``. Optional.
   Sphinx reference name for this Parsons problem.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

**no-indent**
   ``Flag``. Optional.
   If present, indentation does not affect checking. Students still see indent
   controls, but only fragment order and skipped distractors are graded.

Authoring fragments
-------------------

If the source block contains no markers, each non-blank source line becomes one
fragment.

Use ``{{group}}`` and ``{{endgroup}}`` to make multiple source lines one
fragment. Use this when a line and its body should move together.
After ``{{endgroup}}``, following non-blank lines become single-line fragments
until another marker appears.

Use ``{{distractor}}`` to mark the following fragment as a distractor. HTML
shows distractors with the other fragments.
Students must mark distractors as skipped before checking their answer.

A ``{{distractor}}`` can precede a single line or a group:

.. code-block:: text

   {{distractor}}
   single-line distractor

   {{distractor}}
   {{group}}
   multi-line distractor
   {{endgroup}}


Accessibility behavior
----------------------

HTML uses native buttons for movement, indentation, and use/skip state. Each
Use/Skip button keeps ``aria-pressed`` synchronized with its state and includes
visible text. Result text uses a status region so assistive technology can
announce feedback after checking.

Fallback behavior
-----------------

HTML without JavaScript renders the prompt and a deterministic fragment order
with controls. Text and PDF-oriented builders render the prompt and fragments as
a Parsons problem. Static output does not support interactive checking.

Examples
--------

Example 1: Function maximum
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: parsons-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-parsons::

            Construct a function that returns the max value from a list.

            .. code-block:: python

               def findmax(alist):
               {{group}}
                   if len(alist) == 0:
                       return None
               {{endgroup}}

                   curmax = alist[0]
                   for item in alist:
                       if item > curmax:
                           curmax = item
                   return curmax

   .. tb-tab:: Rendered

      .. tb-parsons::

         Construct a function that returns the max value from a list.

         .. code-block:: python

            def findmax(alist):
            {{group}}
                if len(alist) == 0:
                    return None
            {{endgroup}}

                curmax = alist[0]
                for item in alist:
                    if item > curmax:
                        curmax = item
                return curmax

Example 2: Distractor fragment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: parsons-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-parsons::

            Construct a loop that prints each item in ``values``.

            .. code-block:: python

               for value in values:
               {{group}}
                   print(value)
               {{endgroup}}
               {{distractor}}
                   return value

   .. tb-tab:: Rendered

      .. tb-parsons::

         Construct a loop that prints each item in ``values``.

         .. code-block:: python

            for value in values:
            {{group}}
                print(value)
            {{endgroup}}
            {{distractor}}
                return value

Example 3: Ignore indentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: parsons-ex3-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-parsons::
            :no-indent:

            Put the SQL clauses in order.

            .. code-block:: sql

               SELECT name
               FROM students
               WHERE active = 1
               ORDER BY name

   .. tb-tab:: Rendered

      .. tb-parsons::
         :no-indent:

         Put the SQL clauses in order.

         .. code-block:: sql

            SELECT name
            FROM students
            WHERE active = 1
            ORDER BY name
