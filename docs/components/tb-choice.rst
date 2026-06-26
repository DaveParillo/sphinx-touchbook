.. Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
   Copyright (C) 2026 Dave Parillo.
   See https://daveparillo.github.io/sphinx-touchbook/ for details.

tb-choice
=========

The ``tb-choice`` directive creates a multiple choice or multiple answer
question. Use one top-level bullet list for answer choices. For compact
questions, mark each answer with ``[x]`` for correct or ``[ ]`` for incorrect.
Any content after the first answer paragraph becomes feedback.

For complex multi-block answer content, use a nested feedback bullet. Mark
correct feedback with ``+`` and incorrect feedback with ``-``.

If exactly one answer is marked correct, HTML uses radio buttons. If more than
one answer is marked correct, HTML uses checkboxes.

Synopsis
--------

The ``tb-choice`` directive allows questions and feedback defined in one of two
formats: 'compact' and 'nested list'.
The compact format looks like this:

.. code-block:: rst

   .. tb-choice::
      :optional parameter: value

      + --- Prompt area ---
      |
      | question text / content
      |
      + --- Answer area ---
      |
      | - [x] correct answer content
      | - [ ] answer content
      |
      |   optional feedback for an incorrect answer
      |
      + -------------------

The compact format is limited to a single list paragraph for an answer because all following paragraphs are assumed to be feedback.
The first 'word' in a list *must* be `[x]` or `[ ]`.

.. note:: Alternate indicators

   `[x]`, `[X]`, and `[+]` are all synonyms for a correct answer.

   `[ ]` and `[-]` are both synonyms for a wrong answer.

For complex answers and feedback, use nested feedback lists:

.. code-block:: rst

   .. tb-choice::

      question text

      - answer content that can contain multiple blocks

        - feedback for an incorrect answer

      - answer content that can contain multiple blocks

        + feedback for a correct answer

Options
-------

**name**
   ``String``. Optional.
   Sphinx reference name for this choice block.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

**force-multiple**
   ``Boolean``. Optional.
   If present, HTML uses checkboxes even when only one answer is correct.
   This can keep the input type from revealing whether the question has one
   correct answer or more than one correct answer.

**random**
   ``Boolean``. Optional.
   If present, HTML randomizes the answer order when the page loads.
   Text and PDF-oriented builders keep the authored order.

Sphinx configuration options
----------------------------

**tb_choice_force_multiple**
   ``Boolean``. Optional. Default: ``False``.
   If ``True``, all ``tb-choice`` directives use checkboxes, even when only one
   answer is correct. A directive can also opt in with ``:force-multiple:``.

**tb_choice_random**
   ``Boolean``. Optional. Default: ``False``.
   If ``True``, all ``tb-choice`` directives randomize answer order when the
   page loads. A directive can also opt in with ``:random:``.

Accessibility behavior
----------------------

HTML uses native radio buttons or checkboxes. A native button checks the
selection. The result text uses a status region so assistive technology can
announce the result after checking.

Fallback behavior
-----------------

HTML without JavaScript renders the prompt, answers, and feedback in document
order. Text and PDF-oriented builders render the prompt and choices without
correctness markers. Single-select questions use open-circle choice markers.
Multiple-select questions use open-square choice markers. Feedback is omitted
from paper-oriented output so the printed document can ask the complete
question without revealing the answer.

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

            - [ ] x is negative

              This will only print if x has been set to a number less than
              zero. Has it?

            - [ ] x is zero

              This will only print if x has been set to 0. Has it?

            - [x] x is positive

              The first condition is false and ``x`` is not equal to zero, so
              the else block executes.

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

         - [ ] x is negative

           This will only print if x has been set to a number less than zero.
           Has it?

         - [ ] x is zero

           This will only print if x has been set to 0. Has it?

         - [x] x is positive

           The first condition is false and ``x`` is not equal to zero, so the
           else block executes.

Example 2: More than one correct answer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: choice-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-choice::
            :random:

            Select the prime numbers.

            - [x] 2

              ``2`` is prime.

            - [x] 3

              ``3`` is prime.

            - [ ] 4

              ``4`` is composite.

   .. tb-tab:: Rendered

      .. tb-choice::
         :random:

         Select the prime numbers.

         - [x] 2

           ``2`` is prime.

         - [x] 3

           ``3`` is prime.

         - [ ] 4

           ``4`` is composite.

Example 3: Compact choices without feedback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: choice-ex3-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-choice::
            :force-multiple:

            Which color is found in the rainbow?

            - [ ] Black
            - [x] Green
            - [ ] White
            - [ ] Brown
            - [ ] Gray

   .. tb-tab:: Rendered

      .. tb-choice::
         :force-multiple:

         Which color is found in the rainbow?

         - [ ] Black
         - [x] Green
         - [ ] White
         - [ ] Brown
         - [ ] Gray

Example 4: List markup in the question
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: choice-ex4-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-choice::

            Review the following observations:

            - The variable ``total`` starts at ``0``.
            - The loop adds each item in the list.
            - The loop stops after the final item.

            What value does ``total`` contain after summing ``2``, ``4``,
            and ``6``?

            - [ ] 6

              This only includes the final item.

            - [ ] 10

              This misses one of the values in the list.

            - [x] 12

              ``2 + 4 + 6`` gives the final total.

   .. tb-tab:: Rendered

      .. tb-choice::

         Review the following observations:

         - The variable ``total`` starts at ``0``.
         - The loop adds each item in the list.
         - The loop stops after the final item.

         What value does ``total`` contain after summing ``2``, ``4``,
         and ``6``?

         - [ ] 6

           This only includes the final item.

         - [ ] 10

           This misses one of the values in the list.

         - [x] 12

           ``2 + 4 + 6`` gives the final total.

Example 5: Nested feedback with math
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: choice-ex5-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-choice::

            The Pythagorean theorem is :math:`a^2 + b^2 = c^2`. Given:

            .. math::

               3^2 + 4^2 = c^2

            What is the value of ``c``?

            - :math:`5`

              + Correct. The display calculation is:

                .. math::

                   9 + 16 = 25 = 5^2

            - :math:`7`

              - This adds the side lengths directly. The theorem squares
                each leg first:

                .. math::

                   3^2 + 4^2 \neq 3 + 4

            - :math:`25`

              - This is :math:`c^2`, not ``c``. Take the square root:

                .. math::

                   c = \sqrt{25} = 5

   .. tb-tab:: Rendered

      .. tb-choice::

         The Pythagorean theorem is :math:`a^2 + b^2 = c^2`. Given:

         .. math::

            3^2 + 4^2 = c^2

         What is the value of ``c``?

         - :math:`5`

           + Correct. The display calculation is:

             .. math::

                9 + 16 = 25 = 5^2

         - :math:`7`

           - This adds the side lengths directly. The theorem squares each leg
             first:

             .. math::

                3^2 + 4^2 \neq 3 + 4

         - :math:`25`

           - This is :math:`c^2`, not ``c``. Take the square root:

             .. math::

                c = \sqrt{25} = 5
