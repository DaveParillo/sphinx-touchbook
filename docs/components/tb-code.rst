tb-code
=======

The ``tb-code`` directive creates a runnable source-code block. In HTML,
readers can run the code through a configured execution service and optionally
edit the source before running it again.

Synopsis
--------

The general format of the ``tb-code`` directive is:

.. code-block:: rst

   .. tb-code:: language
      :optional parameter: value

      + --- Source code area ---
      |
      | one or more lines of source code
      |
      + ------------------------

The source code area is required.
The language can be supplied as the directive argument or as the ``language``
option.

Options
-------

**caption**
   ``String``. Optional.
   Standard ``code-block`` caption displayed with the static code listing.

**class**
   ``String`` or ``list``. Optional.
   Standard Sphinx ``code-block`` class option passed through to the static
   highlighted listing.
   See the
   `Sphinx code-block documentation <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#showing-code-examples>`__
   for more information.

**compileargs**, **linkargs**, **runargs**, **interpreterargs**
   ``String`` or ``list``. Optional.
   Arguments passed through the Jobe ``parameters`` object.
   Use Python-style list syntax when an argument contains punctuation or
   spaces, for example ``:compileargs: ['-Wall', '-std=c++11']``.
   A simple shell-style string such as ``:runargs: --verbose sample.txt`` is
   also accepted.
   When ``runargs`` is present, HTML shows the value in an editable text input.

**dedent**
   ``Integer``. Optional.
   Standard Sphinx ``code-block`` dedent option passed through to the static
   highlighted listing.
   See the
   `Sphinx code-block documentation <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#showing-code-examples>`__
   for more information.

**edit-label**, **hide-edit-label**
   ``String``. Optional. Labels for the edit toggle button. ``edit-label`` is
   used when the editor is hidden, and ``hide-edit-label`` is used when the
   editor is visible.

**emphasize-lines**
   ``String``. Optional.
   Standard Sphinx ``code-block`` emphasize-lines option passed through to the
   static highlighted listing.
   See the
   `Sphinx code-block documentation <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#showing-code-examples>`__
   for more information.

**endpoint**
   ``String``. Optional. Jobe-compatible ``runs`` endpoint for this code block.
   Defaults to ``tb_code_default_endpoint``.

**files**
   ``String``. Optional. Attaches one or more ``tb-file`` artifacts to the run
   request. Use filenames from the ``tb-file`` ``filename`` option, separated
   by spaces, commas, or new lines.

   .. code-block:: rst

      :files: input.txt data/config.json

   Text files appear in HTML as editable file textareas unless the ``tb-file``
   was marked ``readonly``. Binary files are attached as read-only base64
   content.

**files-endpoint**
   ``String``. Optional. Jobe-compatible ``files`` endpoint used to upload
   support files before a run. Defaults to ``tb_code_files_endpoint``.

**force**
   ``Boolean``. Optional.
   Standard Sphinx ``code-block`` force option passed through to the static
   highlighted listing.
   See the
   `Sphinx code-block documentation <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#showing-code-examples>`__
   for more information.

**hidden**
   ``Boolean``. Optional. Hides rendered output.
   Hidden blocks can still be named and included by another ``tb-code`` block.

**include**
   ``String``. Optional. Replaces ``{{PLACEHOLDER}}`` tokens in this block with
   literal source copied from a named ``tb-code``, ``code-block``, or
   ``literalinclude`` directive. Use one mapping per line:

   .. code-block:: rst

      :include:
         PUBLIC_MEMBERS: account-methods
         PRIVATE_MEMBERS: account-fields

   If the placeholder appears on its own indented line, the inserted source
   uses the same indentation.
   Include names use normal Sphinx reference names, so they can refer to named
   code in another source file.
   Duplicate include fragment names stop the build.

**language**
   ``String``. Optional. Source language.
   This may also be supplied as the directive argument. Default is configured
   by ``tb_code_default_language``.

**lineno-start**
   ``Integer``. Optional.
   Standard Sphinx ``code-block`` lineno-start option passed through to the
   static highlighted listing.
   See the
   `Sphinx code-block documentation <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#showing-code-examples>`__
   for more information.

**linenos**
   ``Boolean``. Optional.
   Standard Sphinx ``code-block`` linenos option passed through to the static
   highlighted listing.
   See the
   `Sphinx code-block documentation <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#showing-code-examples>`__
   for more information.

**name**
   ``String``. Optional.
   Sphinx reference name for this runnable code block.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

**readonly**
   ``Boolean``. Optional. Hides the edit control in HTML output.

**revision-label**
   ``String``. Optional. Label for the source version slider.

**run-after**
   ``String``. Optional. One or more named code fragments appended to the
   current source only when code is sent to the execution service.
   The appended source is not shown in the static listing, editor, or source
   version history.

   Use one name per line, or separate names with commas:

   .. code-block:: rst

      :run-after:
         test-main
         assertions

**run-before**
   ``String``. Optional. One or more named code fragments prepended to the
   current source only when code is sent to the execution service.
   The prepended source is not shown in the static listing, editor, or source
   version history.

   Use one name per line, or separate names with commas:

   .. code-block:: rst

      :run-before:
         imports
         setup-fixture

**run-label**
   ``String``. Optional. Label for the HTML run button.

**show-tutor**
   ``Boolean``. Optional. If present, HTML adds a Python Tutor button for
   supported languages: C, C++, Python, Java, and JavaScript.
   The button opens a new window with a Python Tutor permalink containing the
   current execution source, including any ``run-before`` and ``run-after``
   fragments.

**stdin**
   ``String``. Optional. Standard input sent with the run request.
   When present, HTML shows this value in an editable text input.

Sphinx configuration options
----------------------------

``tb_code_default_endpoint``
   ``String``. Default Jobe-compatible run endpoint. The project default
   is ``https://delicate-frost-8843.fly.dev/jobe/index.php/restapi/runs/``.

``tb_code_languages_endpoint``
   ``String``. Jobe-compatible language discovery endpoint. The project default
   is ``https://delicate-frost-8843.fly.dev/jobe/index.php/restapi/languages``.

``tb_code_files_endpoint``
   ``String``. Jobe-compatible file upload endpoint. The project default
   is ``https://delicate-frost-8843.fly.dev/jobe/index.php/restapi/files/``.

``tb_code_validate_language``
   ``Boolean``. If true, query the languages supported before running code.
   If discovery reports that the configured language is unsupported,
   show a warning. If discovery is unavailable, execution still proceeds.

``tb_code_default_language``
   ``String``. Default source language. The project default is ``python3``.

``tb_code_language_map``
   ``dict``. Optional aliases from author-facing language names to Jobe
   language identifiers. Use this when authors prefer a name that differs from
   the Jobe server's language ID, or when you want ``tb-code`` to match
   language names used elsewhere in the book.
  
   For example, ``{"python": "python3", "c++": "cpp", "js": "nodejs"}`` lets
   authors write ``.. tb-code:: python``, ``.. tb-code:: c++``, or ``..
   tb-code:: js`` while Jobe receives ``python3``, ``cpp``, or ``nodejs``. If
   the author-facing name already matches the Jobe ID, such as ``java`` to
   ``java``, no mapping is needed.

``tb_code_language_defaults``
   ``dict``. Optional per-language Jobe parameter defaults. Keys may be
   author-facing language names such as ``c++`` or Jobe language identifiers
   such as ``cpp``. Values are dictionaries containing ``compileargs``,
   ``linkargs``, ``runargs``, or ``interpreterargs`` lists. If both an
   author-facing name and its mapped Jobe ID have defaults, the author-facing
   name takes precedence.

``tb_code_block_defaults``
   ``dict``. Optional defaults for standard Sphinx ``code-block`` options used
   by ``tb-code``. This is useful for presentation settings that should apply
   to every runnable code block, such as line numbers or custom styling.

   .. code-block:: python

      tb_code_block_defaults = {
          "linenos": True,
          "lineno-start": 1,
          "class": ["touchbook-code"],
      }

   Directive options override matching values from ``tb_code_block_defaults``.
   Avoid setting ``name`` in this dictionary because reference names should be
   unique per block.

``tb_code_run_label``
   ``String``. Default label for the run button.
   The project default is ``Run``.

``tb_code_edit_label``
   ``String``. Default label for the edit button when the editor is hidden.
   The project default is ``Edit``.

``tb_code_hide_edit_label``
   ``String``. Default label for the edit button when the editor is visible.
   The project default is ``Hide editor``.

``tb_code_revision_label``
   ``String``. Default label for the source version slider.
   The project default is ``Source version``.

Service contract
----------------

Code that cannot be compiled natively in a browser is sent to a
`Jobe server <https://github.com/trampgeek/jobeinabox>`__ for processing.

``tb-code`` sends a Jobe-compatible request shaped like this:

.. code-block:: json

   {
     "run_spec": {
       "language_id": "cpp",
       "sourcecode": "int main() { return 0; }",
       "input": "Alice",
       "file_list": [["tbfileabc123", "input.txt"]],
       "parameters": {
         "compileargs": ["-Wall", "-std=c++11"],
         "linkargs": [],
         "runargs": [],
         "interpreterargs": []
       }
     }
   }

The directive options ``compileargs``, ``linkargs``, ``runargs``, and
``interpreterargs`` populate the corresponding keys in ``parameters``.
Values set on an individual directive override matching values from
``tb_code_language_defaults``.
Defaults for keys not supplied on the directive still apply.

If ``stdin`` or ``runargs`` are configured, HTML presents editable text inputs
initialized from those values.
The current input values are used when the reader presses Run.
These runtime inputs are separate from the source version history.

When ``files`` is configured, each attached file is uploaded to the configured
Jobe ``files`` endpoint before the run request is sent. The run request then
uses Jobe's ``file_list`` field to map each uploaded file identifier to the
filename visible inside the execution workspace.

When ``run-before`` or ``run-after`` is configured, those named fragments are
combined with the current source only for the execution request. They are not
shown in the static listing or editor. Treat these fragments as hidden from the
page interface, not as private code; generated HTML can still be inspected by a
reader.

When ``show-tutor`` is configured for C, C++, Python, Java, or JavaScript,
HTML adds a Python Tutor button. The permalink uses the same execution source
that the Run button sends to Jobe. Runtime standard input, run arguments, and
attached files are not included in the Python Tutor URL.

Accessibility behavior
----------------------

The no-JS HTML fallback is a normal Sphinx-highlighted code listing. HTML adds
native ``button`` controls, a ``textarea`` editor, a source version slider,
optional runtime text inputs, a polite status region, and a labeled output
region.

The edit button is a toggle. When the editor is opened, its label changes from
``tb_code_edit_label`` to ``tb_code_hide_edit_label`` and ``aria-expanded`` is
updated. The source version slider starts with the original source as version 1
and appears after the editable source creates a second version. Once more than
one version exists, the slider remains visible when the editor is hidden so
readers can select and run an older source version. Loading a version updates
the textarea and the visible source listing.

Fallback behavior
-----------------

PDF and text builders render the source code as static readable content.

Examples
--------

Example 1: Basic Python
~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: code-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-code:: python

            print("Hello, world")

   .. tb-tab:: Rendered

      .. tb-code:: python

         print("Hello, world")

Example 2: Python defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~

Python usually does not require compile or link arguments, but defaults can
still be set in ``conf.py``. The example below maps ``python`` to Jobe's
``python3`` language identifier and provides an interpreter argument default.

.. rubric:: ``conf.py``

.. code-block:: python

   tb_code_default_language = "python3"
   tb_code_language_map = {
       "python": "python3",
   }
   tb_code_language_defaults = {
       "python3": {
           "interpreterargs": ["-B"],
       },
   }

.. tb-group::
   :name: code-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-code:: python
            :caption: Hello from Python
            :interpreterargs: ['-B']

            print("Hello, world")

   .. tb-tab:: Rendered

      .. tb-code:: python
         :caption: Hello from Python
         :interpreterargs: ['-B']

         print("Hello, world")

Example 3: Include named code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``include`` to assemble a runnable block from named source fragments. This
is useful when an example needs to show part of a program separately and later
run it in a larger context.

.. tb-group::
   :name: code-ex3-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-code:: cpp
            :name: account-methods
            :hidden:

            public:
              int balance() const;

         .. code-block:: cpp
            :name: account-fields

            private:
              int balance_;

         .. tb-code:: cpp
            :name: code-ex3
            :caption: Account class assembled from named code
            :include:
               PUBLIC_MEMBERS: account-methods
               PRIVATE_MEMBERS: account-fields

            class account {
              {{PUBLIC_MEMBERS}}
              {{PRIVATE_MEMBERS}}
            };

   .. tb-tab:: Rendered

      .. tb-code:: cpp
         :name: account-methods
         :hidden:

         public:
           int balance() const;

      .. code-block:: cpp
         :name: account-fields

         private:
           int balance_;

      .. tb-code:: cpp
         :name: code-ex3
         :caption: Account class assembled from named code
         :include:
            PUBLIC_MEMBERS: account-methods
            PRIVATE_MEMBERS: account-fields

         class account {
           {{PUBLIC_MEMBERS}}
           {{PRIVATE_MEMBERS}}
         };

Example 4: Execution-only test runner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``run-after`` when code should be sent to the execution service without
being shown in the static listing or editor. This is useful for test runners
or support code that would distract from the code students should read.

.. tb-group::
   :name: code-ex4-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-code:: cpp
            :name: account-balance-tests
            :hidden:

            int main() {
              account sample;
              return sample.balance() == 100 ? 0 : 1;
            }

         .. tb-code:: cpp
            :name: code-ex4
            :caption: Account implementation with hidden tests
            :run-after: account-balance-tests
            :show-tutor:

            class account {
            public:
              int balance() const {
                return 100;
              }
            };

   .. tb-tab:: Rendered

      .. tb-code:: cpp
         :name: account-balance-tests
         :hidden:

         int main() {
           account sample;
           return sample.balance() == 100 ? 0 : 1;
         }

      .. tb-code:: cpp
         :name: code-ex4
         :caption: Account implementation with hidden tests
         :run-after: account-balance-tests
         :show-tutor:

         class account {
         public:
           int balance() const {
             return 100;
           }
         };

Example 5: Python command-line arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``runargs`` when a program expects command-line arguments. In HTML, the
initial value appears in an editable text input before the program runs.

.. tb-group::
   :name: code-ex5-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-code:: python
            :name: code-ex5
            :caption: Python command-line arguments
            :runargs: Ada Lovelace

            import sys

            if len(sys.argv) < 3:
                print("Please provide a first and last name.")
            else:
                first = sys.argv[1]
                last = sys.argv[2]
                print(f"Hello, {first} {last}!")

   .. tb-tab:: Rendered

      .. tb-code:: python
         :name: code-ex5
         :caption: Python command-line arguments
         :runargs: Ada Lovelace

         import sys

         if len(sys.argv) < 3:
             print("Please provide a first and last name.")
         else:
             first = sys.argv[1]
             last = sys.argv[2]
             print(f"Hello, {first} {last}!")

Example 6: Java
~~~~~~~~~~~~~~~

Java examples often need JVM limits. These can be configured once in
``conf.py`` and overridden on a specific ``tb-code`` block when needed.

.. rubric:: ``conf.py``

.. code-block:: python

   tb_code_language_defaults = {
       "java": {
           "interpreterargs": ["-Xrs", "-Xss8m", "-Xmx128m"],
       },
   }

.. tb-group::
   :name: code-ex6-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-code:: java
            :name: code-ex6
            :caption: Fahrenheit to Celsius
            :emphasize-lines: 9
            :interpreterargs: ['-Xrs', '-Xss8m', '-Xmx128m']
            :stdin: 100

            import java.util.Scanner;

            public class TempConv {
                public static void main(String[] args) {
                     Double fahr;
                     Double cel;
                     Scanner in;

                     in = new Scanner(System.in);
                     System.out.println("Enter the temperature in F: ");
                     fahr = in.nextDouble();

                     cel = (fahr - 32) * 5.0/9.0;
                     System.out.println(fahr + " degrees F is: " + cel + " C");
                }

            }

   .. tb-tab:: Rendered

      .. tb-code:: java
         :name: code-ex6
         :caption: Fahrenheit to Celsius
         :emphasize-lines: 9
         :interpreterargs: ['-Xrs', '-Xss8m', '-Xmx128m']
         :stdin: 100

         import java.util.Scanner;

         public class TempConv {
             public static void main(String[] args) {
                  Double fahr;
                  Double cel;
                  Scanner in;

                  in = new Scanner(System.in);
                  System.out.println("Enter the temperature in F: ");
                  fahr = in.nextDouble();

                  cel = (fahr - 32) * 5.0/9.0;
                  System.out.println(fahr + " degrees F is: " + cel + " C");
             }

         }

Example 7: C++
~~~~~~~~~~~~~~

For C++, use ``compileargs`` for compiler flags and ``linkargs`` for linker
flags. The language map lets authors write ``c++`` while sending Jobe the
``cpp`` language identifier.

.. rubric:: ``conf.py``

.. code-block:: python

   tb_code_language_map = {
       "c++": "cpp",
       "cpp": "cpp",
   }
   tb_code_language_defaults = {
       "cpp": {
           "compileargs": ["-Wall", "-Wextra", "-pedantic", "-std=c++11"],
       },
   }

.. tb-group::
   :name: code-ex7-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-code:: c++
            :name: code-ex7
            :caption: Hello from C++
            :compileargs: ['-Wall', '-Wextra', '-pedantic', '-std=c++11']
            :runargs: --repeat=3
            :stdin: Alice

            // A simple test for C++11 compiler
            #include <cstdlib>
            #include <iostream>
            #include <string>

            int main(int argc, char* argv[]) {
              int test[] = { 1, 2, 3, 5, 8 };
              for (auto i: test) {
                std::cout << "i is " << i << '\n';
              }

              int repeat = 1;
              for (int i = 1; i < argc; ++i) {
                std::string arg = argv[i];
                if (arg.find("--repeat=") == 0) {
                  repeat = std::atoi(arg.substr(9).c_str());
                  if (repeat < 1) {
                    repeat = 1;
                  }
                }
              }

              std::string name;
              std::cin >> name;
              for (int i = 0; i < repeat; ++i) {
                std::cout << "Hello, " << name << "!\n";
              }
              return 0;
            }

   .. tb-tab:: Rendered

      .. tb-code:: c++
         :name: code-ex7
         :caption: Hello from C++
         :compileargs: ['-Wall', '-Wextra', '-pedantic', '-std=c++11']
         :runargs: --repeat=3
         :stdin: Alice

         // A simple test for C++11 compiler
         #include <cstdlib>
         #include <iostream>
         #include <string>

         int main(int argc, char* argv[]) {
           int test[] = { 1, 2, 3, 5, 8 };
           for (auto i: test) {
             std::cout << "i is " << i << '\n';
           }

           int repeat = 1;
           for (int i = 1; i < argc; ++i) {
             std::string arg = argv[i];
             if (arg.find("--repeat=") == 0) {
               repeat = std::atoi(arg.substr(9).c_str());
               if (repeat < 1) {
                 repeat = 1;
               }
             }
           }

           std::string name;
           std::cin >> name;
           for (int i = 0; i < repeat; ++i) {
             std::cout << "Hello, " << name << "!\n";
           }
           return 0;
         }


Example 8: GNU Octave
~~~~~~~~~~~~~~~~~~~~~
Octave is a powerful Scientific Programming Language designed to be largely
compatible with Matlab.
Although Octave does support built-in 2D/3D plotting and visualization tools
those tools are not available through the touchbook interface.
Output is limited to text.

.. tb-group::
   :name: code-ex8-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-code:: octave
            :name: code-ex8
            :caption: Solve Linear Algebra Equations with Octave

            # Define matrices
            A = [2, 1; 1, 3];
            B = [5, 6; 4, 7];

            # Solve matrix equation X = A\B
            X = A \ B

   .. tb-tab:: Rendered

      .. tb-code:: octave
         :name: code-ex8
         :caption: Solve Linear Algebra Equations with Octave

         # Define matrices
         A = [2, 1; 1, 3];
         B = [5, 6; 4, 7];

         # Solve matrix equation X = A\B
         X = A \ B
