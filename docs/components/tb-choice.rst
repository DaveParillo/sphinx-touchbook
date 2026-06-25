tb-choice
=========

The ``tb-choice`` directive creates a multiple choice or multiple answer
question. Use one top-level bullet list for answer choices. Each answer choice
must contain one nested feedback bullet. Mark correct feedback with ``+`` and
incorrect feedback with ``-``.

If exactly one answer is marked correct, HTML uses radio buttons. If more than
one answer is marked correct, HTML uses checkboxes.

Synopsis
--------

The general format of the ``tb-choice`` directive is:

.. code-block:: rst

   .. tb-choice::
      :optional parameter: value

      + --- Prompt area ---
      |
      | question text and optional Sphinx content
      |
      + --- Answer area ---
      |
      | - answer content
      |
      |   - feedback for an incorrect answer
      |
      | - answer content
      |
      |   + feedback for a correct answer
      |
      + -------------------

Options
-------

**name**
   ``String``. Optional.
   Sphinx reference name for this choice block.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

**random**
   ``Boolean``. Optional.
   If present, HTML randomizes the answer order when the page loads.
   Text and PDF-oriented builders keep the authored order.

Accessibility behavior
----------------------

HTML uses native radio buttons or checkboxes. A native button checks the
selection. The result text uses a status region so assistive technology can
announce the result after checking.

Fallback behavior
-----------------

HTML without JavaScript renders the prompt, answers, and feedback in document
order. Text and PDF-oriented builders render the prompt, choices, and feedback.
Correct choices are marked with ``[*]`` and incorrect choices with ``[ ]``.

Examples
--------

Example 1: One correct answer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: choice-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-choice::

            What does the following code print when ``x`` has been set to 187?

            .. code-block:: java

               if (x < 0)
               {
                   System.out.println("x is negative");
               }
               else if (x == 0)
               {
                   System.out.println("x is zero");
               }
               else
               {
                   System.out.println("x is positive");
               }

            - x is negative

              - This will only print if x has been set to a number less than
                zero. Has it?

            - x is zero

              - This will only print if x has been set to 0. Has it?

            - x is positive

              + The first condition is false and ``x`` is not equal to zero,
                so the else block executes.

   .. tb-tab:: Rendered

      .. tb-choice::

         What does the following code print when ``x`` has been set to 187?

         .. code-block:: java

            if (x < 0)
            {
                System.out.println("x is negative");
            }
            else if (x == 0)
            {
                System.out.println("x is zero");
            }
            else
            {
                System.out.println("x is positive");
            }

         - x is negative

           - This will only print if x has been set to a number less than zero.
             Has it?

         - x is zero

           - This will only print if x has been set to 0. Has it?

         - x is positive

           + The first condition is false and ``x`` is not equal to zero, so
             the else block executes.

Example 2: More than one correct answer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: choice-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-choice::
            :random:

            Select the prime numbers.

            - 2

              + ``2`` is prime.

            - 3

              + ``3`` is prime.

            - 4

              - ``4`` is composite.

   .. tb-tab:: Rendered

      .. tb-choice::
         :random:

         Select the prime numbers.

         - 2

           + ``2`` is prime.

         - 3

           + ``3`` is prime.

         - 4

           - ``4`` is composite.
