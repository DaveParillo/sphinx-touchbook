tb-blank
========

The ``tb-blank`` directive creates a fill-in-the-blank question.
Authors place one or more ``{{blank}}`` markers in normal Sphinx content.
Nested ``tb-answer`` blocks define accepted answers, targeted hints for common
wrong answers, and fallback incorrect feedback.

Synopsis
--------

The general format of the ``tb-blank`` directive is:

.. code-block:: rst

   .. tb-blank::
      :optional parameter: value

      + --- Prompt area ---
      |
      | question text and optional Sphinx content with {{blank}} markers
      |
      + --- Answer area ---
      |
      | .. tb-answer:: optional-blank-id
      |    :match: accepted answer
      |    :feedback: correct feedback
      |    :hint: known wrong answer; targeted feedback
      |    :incorrect: fallback incorrect feedback
      |
      + -----------------

Options
-------

**case-sensitive**
   ``Flag``. Optional.
   Require exact case when comparing submitted answers. By default, matching is
   case-insensitive.

**name**
   ``String``. Optional.
   Sphinx reference name for this fill-in-the-blank question.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

**preserve-whitespace**
   ``Flag``. Optional.
   Preserve leading and trailing whitespace when comparing submitted answers.
   By default, submitted answers and expected answers are trimmed.

Answer Options
--------------

Nested ``tb-answer`` blocks support these options:

**feedback**
   ``String``. Optional.
   Feedback shown when a submitted answer matches one of the accepted answers.

**hint**
   ``String``. Optional. Repeatable.
   Known wrong answer and targeted feedback separated by the first semicolon.
   For example, ``:hint: 7; Check the assignment in the else block.``.

**incorrect**
   ``String``. Optional.
   Feedback shown when the submitted answer does not match an accepted answer
   or a known wrong answer.

**match**
   ``String``. Required. Repeatable.
   Accepted answer. Matching is case-insensitive and trims leading and trailing
   whitespace unless directive options override those defaults.

**regex**
   ``Flag``. Optional.
   Treat ``match`` values as regular expressions.

Accessibility behavior
----------------------

HTML uses native text inputs and a native button. Result text uses a status
region so assistive technology can announce feedback after checking.

Fallback behavior
-----------------

HTML without JavaScript renders the prompt and input fields. Text and
PDF-oriented builders render each blank as an underline. Answers and feedback
are not rendered in fallback output.

Examples
--------

Example 1: Single blank
~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: blank-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-blank::

            The capital of France is {{blank}}.

            .. tb-answer::
               :match: Paris
               :feedback: Correct.
               :incorrect: Try again.

   .. tb-tab:: Rendered

      .. tb-blank::

         The capital of France is {{blank}}.

         .. tb-answer::
            :match: Paris
            :feedback: Correct.
            :incorrect: Try again.

Example 2: Code reasoning with targeted hints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: blank-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-blank::

            .. code-block:: c

               int main(void) {
                 int a = 7;
                 int b = 4;

                 if (a<=b) {
                   a = 99;
                 } else {
                   int t = a;
                   a = b;
                   b = t;
                 }
                 return a;
               }

            What value is returned from main? {{blank}}

            .. tb-answer::
               :match: 4
               :match: 4.0
               :feedback: Correct.
               :hint: 7; No, because the variable a is modified in the else block.
               :hint: 99; No. Since a is greater than b, line 6 is never executed.
               :incorrect: Sorry, no. What is happening in the else block?

   .. tb-tab:: Rendered

      .. tb-blank::

         .. code-block:: c

            int main(void) {
              int a = 7;
              int b = 4;

              if (a<=b) {
                a = 99;
              } else {
                int t = a;
                a = b;
                b = t;
              }
              return a;
            }

         What value is returned from main? {{blank}}

         .. tb-answer::
            :match: 4
            :match: 4.0
            :feedback: Correct.
            :hint: 7; No, because the variable a is modified in the else block.
            :hint: 99; No. Since a is greater than b, line 6 is never executed.
            :incorrect: Sorry, no. What is happening in the else block?
