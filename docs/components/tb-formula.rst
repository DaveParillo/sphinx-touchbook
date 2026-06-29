tb-formula
==========

The ``tb-formula`` directive creates a calculated numeric question. Authors
define variable ranges, use variable placeholders in the question, and provide
one formula that computes the expected answer from the generated values.

Synopsis
--------

The general format of the ``tb-formula`` directive is:

.. code-block:: rst

   .. tb-formula::
      :variables: x=min..max, y=min..max
      :optional parameter: value

      + --- Question area ---
      |
      | question text with {{x}} and {{y}} placeholders
      |
      + --- Answer formula ---

      .. answer-formula:: javascript

         formula using the variables

Options
-------

**variables**
   ``String``. Required.
   Comma-separated or semicolon-separated variable ranges. Each range uses
   ``name=min..max`` syntax. If both endpoints are integers, HTML generates
   integer values. Decimal endpoints generate decimal values.

**name**
   ``String``. Optional.
   Sphinx reference name for this calculated formula question.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

**tolerance**
   ``Number``. Optional.
   Accepted absolute difference from a numeric formula result. The default is
   ``0``. If the formula returns a range, ``tolerance`` is not used.

Sphinx configuration options
----------------------------

**tb_formula_default_endpoint**
   ``String``. Optional.
   URL for remote formula execution when ``answer-formula`` uses a language
   other than ``javascript`` or ``js``. The default is the same JOBE runs
   endpoint used by ``tb-code``.

**tb_formula_language_defaults**
   ``Dictionary``. Optional.
   Default JOBE parameters for remote formula languages. Supported keys are
   ``compileargs``, ``linkargs``, ``runargs``, and ``interpreterargs``.

Answer formula
--------------

The nested ``answer-formula`` block accepts an optional language argument.
When omitted, the language is ``javascript``.

JavaScript formulas run in the browser and can refer to each variable by name.
Other languages are sent to a remote server execution endpoint.
``tb-formula`` sends the generated variables as JSON text on standard input.
Results should print to standard output.

Remote formula blocks can set JOBE parameters with ``:compileargs:``,
``:linkargs:``, ``:runargs:``, and ``:interpreterargs:`` options. These options
accept either a shell-style string or a Python-style list of strings.

A formula can return:

- a number, such as ``4 * y + 3 * x``
- a range of acceptable values as either:

  - a two-item range as a JSON array, such as ``[359, 361]``
  - a JSON object with ``min`` and ``max`` keys

Accessibility behavior
----------------------

HTML shows the generated values as text and uses a text input with decimal
keyboard hints for the answer. The Check answer and New values controls are
native buttons. Result text uses a status region so assistive technology can
announce feedback.

Fallback behavior
-----------------

HTML without JavaScript shows the question with placeholder blanks and an
answer input. Text and PDF-oriented builders render the question with blanks
for generated values and a blank answer area. Static output does not include
the formula.

Examples
--------

Example 1: Glasses of water
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: formula-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-formula::
            :variables: x=4..8, y=10..20

            If a small glass can hold {{x}} ounces of water, and a large
            glass can hold {{y}} ounces of water, what's the total number of
            ounces in 4 large and 3 small glasses of water?

            .. answer-formula:: javascript

               4 * y + 3 * x

   .. tb-tab:: Rendered

      .. tb-formula::
         :variables: x=4..8, y=10..20

         If a small glass can hold {{x}} ounces of water, and a large glass
         can hold {{y}} ounces of water, what's the total number of ounces in
         4 large and 3 small glasses of water?

         .. answer-formula:: javascript

            4 * y + 3 * x

Example 2: Tolerance
~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: formula-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-formula::
            :variables: radius=2.0..5.0
            :tolerance: 0.05

            A circle has radius {{radius}}. What is its area?

            .. answer-formula:: javascript

               Math.PI * radius * radius

   .. tb-tab:: Rendered

      .. tb-formula::
         :variables: radius=2.0..5.0
         :tolerance: 0.05

         A circle has radius {{radius}}. What is its area?

         .. answer-formula:: javascript

            Math.PI * radius * radius

Example 3: Fixed answer range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: formula-ex3-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-formula::
            :variables: width=10..20

            A board is {{width}} centimeters wide. Estimate its width to the
            nearest 5 centimeters.

            .. answer-formula:: javascript

               [width - 2.5, width + 2.5]

   .. tb-tab:: Rendered

      .. tb-formula::
         :variables: width=10..20

         A board is {{width}} centimeters wide. Estimate its width to the
         nearest 5 centimeters.

         .. answer-formula:: javascript

            [width - 2.5, width + 2.5]

Example 4: Data-dependent range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: formula-ex4-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-formula::
            :variables: distance=80..120, time=8..12

            A cart travels {{distance}} meters in {{time}} seconds. What is
            its speed in meters per second? Answers within 5 percent are
            accepted.

            .. answer-formula:: javascript

               ({ min: (distance / time) * 0.95, max: (distance / time) * 1.05 })

   .. tb-tab:: Rendered

      .. tb-formula::
         :variables: distance=80..120, time=8..12

         A cart travels {{distance}} meters in {{time}} seconds. What is its
         speed in meters per second? Answers within 5 percent are accepted.

         .. answer-formula:: javascript

            ({ min: (distance / time) * 0.95, max: (distance / time) * 1.05 })

Example 5: Remote formula program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: formula-ex5-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-formula::
            :variables: x=1..10, y=1..10

            What is {{x}} plus {{y}}?

            .. answer-formula:: python3

               import json
               import sys

               values = json.load(sys.stdin)
               print(values["x"] + values["y"])

   .. tb-tab:: Rendered

      .. tb-formula::
         :variables: x=1..10, y=1..10

         What is {{x}} plus {{y}}?

         .. answer-formula:: python3

            import json
            import sys

            values = json.load(sys.stdin)
            print(values["x"] + values["y"])

Example 6: Minimal C++ formula program
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: formula-ex6-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-formula::
            :variables: n=2..9

            What is {{n}} squared?

            .. answer-formula:: cpp
               :compileargs: ['-std=c++11']

               #include <cctype>
               #include <iostream>
               #include <iterator>
               #include <string>

               int main() {
                 std::string input(
                   (std::istreambuf_iterator<char>(std::cin)),
                   std::istreambuf_iterator<char>()
                 );
                 std::string digits;
                 for (char c : input) {
                   if (std::isdigit(static_cast<unsigned char>(c))) {
                     digits += c;
                   }
                 }
                 int n = std::stoi(digits);
                 std::cout << n * n << '\n';
                 return 0;
               }

   .. tb-tab:: Rendered

      .. tb-formula::
         :variables: n=2..9

         What is {{n}} squared?

         .. answer-formula:: cpp
            :compileargs: ['-std=c++11']

            #include <cctype>
            #include <iostream>
            #include <iterator>
            #include <string>

            int main() {
              std::string input(
                (std::istreambuf_iterator<char>(std::cin)),
                std::istreambuf_iterator<char>()
              );
              std::string digits;
              for (char c : input) {
                if (std::isdigit(static_cast<unsigned char>(c))) {
                  digits += c;
                }
              }
              int n = std::stoi(digits);
              std::cout << n * n << '\n';
              return 0;
            }
