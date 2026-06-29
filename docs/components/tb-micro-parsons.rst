tb-micro-parsons
================

The ``tb-micro-parsons`` directive creates a token-level Parsons problem.
Authors write tokens in the correct order. HTML shuffles the tokens and lets
students move tokens from a source row into an answer row before checking the
answer.

Synopsis
--------

The general format of the ``tb-micro-parsons`` directive is:

.. code-block:: rst

   .. tb-micro-parsons::
      :optional parameter: value

      + --- Optional prompt area ---
      |
      | question text and optional Sphinx content
      |
      + --- Token list in correct order ---

      - first-token
      - second-token
      - third-token

Options
-------

**name**
   ``String``. Optional.
   Sphinx reference name for this micro-Parsons problem.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

**distractor**
   ``String``. Optional.
   Additional tokens that do not belong in the final answer. Tokens can be
   separated with semicolons or written one per continuation line.

Accessibility behavior
----------------------

HTML renders each token as a native button. Activating a token in the source
row moves it to the end of the answer row. Activating a token in the answer row
moves it back to the source row. Keyboard focus remains on the token after it
moves. Result text uses a status region so assistive technology can announce
feedback after checking.

Distractors are omitted by leaving them in the source row.

Fallback behavior
-----------------

HTML without JavaScript renders the prompt, a deterministic token order, and an
empty answer row. Text and PDF-oriented builders render the prompt, shuffled
tokens, and a blank answer line. Static output does not support interactive
checking.

Examples
--------

Example 1: Assignment statement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: micro-parsons-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-micro-parsons::

            Arrange the tokens to create a valid assignment statement.

            - int
            - x
            - =
            - 42
            - ;

   .. tb-tab:: Rendered

      .. tb-micro-parsons::

         Arrange the tokens to create a valid assignment statement.

         - int
         - x
         - =
         - 42
         - ;

Example 2: Distractor tokens
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: micro-parsons-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-micro-parsons::
            :distractor: float; ==

            Arrange the tokens to create a valid assignment statement.

            - int
            - x
            - =
            - 42
            - ;

   .. tb-tab:: Rendered

      .. tb-micro-parsons::
         :distractor: float; ==

         Arrange the tokens to create a valid assignment statement.

         - int
         - x
         - =
         - 42
         - ;

Example 3: SQL clause
~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: micro-parsons-ex3-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-micro-parsons::
            :distractor:
               ORDER
               GROUP

            Arrange the tokens to create a SQL ``WHERE`` condition.

            - WHERE
            - score
            - >=
            - 90

   .. tb-tab:: Rendered

      .. tb-micro-parsons::
         :distractor:
            ORDER
            GROUP

         Arrange the tokens to create a SQL ``WHERE`` condition.

         - WHERE
         - score
         - >=
         - 90
