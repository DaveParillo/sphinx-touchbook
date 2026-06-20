tb-code
=======

The ``tb-code`` directive creates a runnable source-code block. HTML readers can run the code through a configured execution service and optionally edit the source before running it again.

Synopsis
--------

The general format of the ``tb-code`` directive is:

.. code-block:: rst

   .. tb-code:: python3
      :name: optional-reference-name
      :caption: Example program
      :linenos:
      :stdin: optional standard input

      print("Hello, world")

Required content
----------------

content area
   The ``tb-code`` directive must contain at least one line of source code.

Options
-------

``name``
   ``String``. Optional. Sphinx reference name for this runnable code block. This is a `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__. If omitted, docutils assigns a deterministic generated ID derived from the document and node position.

``language``
   ``String``. Optional. Source language. This may also be supplied as the directive argument. Default is configured by ``tb_code_default_language``.

``caption``
   ``String``. Optional. Standard ``code-block`` caption displayed with the static code listing.

``linenos``, ``lineno-start``, ``emphasize-lines``, ``dedent``, ``class``, ``force``
   Optional. Standard Sphinx ``code-block`` options passed through to the static highlighted listing. The ``class`` option is also a `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__. These options affect the no-JS HTML fallback and built documentation output; the editable HTML control remains a plain text editor.

``endpoint``
   ``String``. Optional. JOBE-compatible ``runs`` endpoint for this code block. Defaults to ``tb_code_default_endpoint``.

``stdin``
   ``String``. Optional. Standard input sent with the run request.

``compileargs``, ``linkargs``, ``runargs``, ``interpreterargs``
   ``String`` or ``list``. Optional. Arguments passed through the JOBE ``parameters`` object.
   Use Python-style list syntax when an argument contains punctuation or spaces,
   for example ``:compileargs: ['-Wall', '-std=c++11']``.
   A simple shell-style string such as ``:runargs: --verbose sample.txt`` is also accepted.

``readonly``
   ``Boolean``. Optional. Hides the edit control in enhanced HTML output.

``run-label``
   ``String``. Optional. Label for the enhanced HTML run button.

``edit-label``, ``hide-edit-label``
   ``String``. Optional. Labels for the edit toggle button. ``edit-label`` is
   used when the editor is hidden, and ``hide-edit-label`` is used when the
   editor is visible.

``revision-label``
   ``String``. Optional. Label for the editor revision slider. The slider lets
   readers load the original source or later saved editor revisions.

Sphinx configuration options
----------------------------

``tb_code_default_endpoint``
   ``String``. Default JOBE-compatible run endpoint. The project default is ``https://delicate-frost-8843.fly.dev/jobe/index.php/restapi/runs/``.

``tb_code_languages_endpoint``
   ``String``. JOBE-compatible language discovery endpoint. The project default is ``https://delicate-frost-8843.fly.dev/jobe/index.php/restapi/languages``.

``tb_code_validate_language``
   ``Boolean``. If true, the Web Component queries the language discovery endpoint before running code. If discovery fails, execution still proceeds.

``tb_code_default_language``
   ``String``. Default source language. The project default is ``python3``.

``tb_code_language_map``
   ``dict``. Optional aliases from author-facing language names to JOBE language identifiers. Use this when authors prefer a name that differs from the JOBE server's language ID, or when you want ``tb-code`` to match language names used elsewhere in the book. For example, ``{"python": "python3", "c++": "cpp", "js": "nodejs"}`` lets authors write ``.. tb-code:: python``, ``.. tb-code:: c++``, or ``.. tb-code:: js`` while JOBE receives ``python3``, ``cpp``, or ``nodejs``. If the author-facing name already matches the JOBE ID, such as ``java`` to ``java``, no mapping is needed.

``tb_code_language_defaults``
   ``dict``. Optional per-language JOBE parameter defaults. Keys may be author-facing language names such as ``c++`` or JOBE language identifiers such as ``cpp``. Values are dictionaries containing ``compileargs``, ``linkargs``, ``runargs``, or ``interpreterargs`` lists. If both an author-facing name and its mapped JOBE ID have defaults, the author-facing name takes precedence.

``tb_code_code_block_defaults``
   ``dict``. Optional defaults for standard Sphinx ``code-block`` options used by ``tb-code``. This is useful for presentation settings that should apply to every runnable code block, such as line numbers.

   .. code-block:: python

      tb_code_code_block_defaults = {
          "linenos": True,
          "lineno-start": 1,
          "class": ["touchbook-code"],
      }

   Directive options override matching values from ``tb_code_code_block_defaults``. Avoid setting ``name`` in this dictionary because reference names should be unique per block.

``tb_code_run_label``
   ``String``. Default label for the run button. The project default is ``Run``.

``tb_code_edit_label``
   ``String``. Default label for the edit toggle button when the editor is hidden. The project default is ``Edit``.

``tb_code_hide_edit_label``
   ``String``. Default label for the edit toggle button when the editor is visible. The project default is ``Hide editor``.

``tb_code_revision_label``
   ``String``. Default label for the editor revision slider. The project default is ``Editor revision``.

JOBE parameters
---------------

``tb-code`` sends a JOBE-compatible request shaped like this:

.. code-block:: json

   {
     "run_spec": {
       "language_id": "cpp",
       "sourcecode": "int main() { return 0; }",
       "input": "Alice",
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
``tb_code_language_defaults``. Defaults for keys not supplied on the directive
still apply.

Accessibility and fallback behavior
-----------------------------------

The no-JS HTML fallback is a normal Sphinx-highlighted code listing. The enhanced Web Component adds native ``button`` controls, a ``textarea`` editor, an editor revision slider, a polite status region, and a labeled output region.

The edit button is a toggle. When the editor is opened, its label changes from
``tb_code_edit_label`` to ``tb_code_hide_edit_label`` and ``aria-expanded`` is
updated. The revision slider starts with the original source as revision 1 and
adds revisions when the editable source changes or runs. Loading a revision
updates the textarea without changing the static fallback listing.

PDF and text builders render the source code as static readable content.

Examples
--------

Example 1: Python
~~~~~~~~~~~~~~~~~

Python usually does not require compile or link arguments, but defaults can
still be set in ``conf.py``. The example below maps ``python`` to JOBE's
``python3`` language identifier and provides an interpreter argument default.

``conf.py``
^^^^^^^^^^^

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

Source
^^^^^^

.. code-block:: rst

   .. tb-code:: python
      :name: code-ex1
      :caption: Hello from Python
      :edit-label: Edit source
      :hide-edit-label: Hide source
      :interpreterargs: ['-B']

      print("Hello, world")

Rendered
^^^^^^^^

.. tb-code:: python
   :name: code-ex1
   :caption: Hello from Python
   :edit-label: Edit source
   :hide-edit-label: Hide source
   :interpreterargs: ['-B']

   print("Hello, world")

Example 2: Java
~~~~~~~~~~~~~~~

Java examples often need JVM limits. These can be configured once in ``conf.py``
and overridden on a specific ``tb-code`` block when needed.

``conf.py``
^^^^^^^^^^^

.. code-block:: python

   tb_code_language_defaults = {
       "java": {
           "interpreterargs": ["-Xrs", "-Xss8m", "-Xmx128m"],
       },
   }

Source
^^^^^^

.. code-block:: rst

   .. tb-code:: java
      :name: code-ex2
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

Rendered
^^^^^^^^

.. tb-code:: java
   :name: code-ex2
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

Example 3: C++
~~~~~~~~~~~~~~

For C++, use ``compileargs`` for compiler flags and ``linkargs`` for linker
flags. The language map lets authors write ``c++`` while sending JOBE the
``cpp`` language identifier.

``conf.py``
^^^^^^^^^^^

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

Source
^^^^^^

.. code-block:: rst

   .. tb-code:: c++
      :name: code-ex3
      :caption: Hello from C++
      :compileargs: ['-Wall', '-Wextra', '-pedantic', '-std=c++11']
      :stdin: Alice

      // A simple test for C++11 compiler
      #include <iostream>
      #include <string>

      int main() {
        int test[] = { 1, 2, 3, 5, 8 };
        for (auto i: test) {
          std::cout << "i is " << i << '\n';
        }

        std::string name;
        std::cin >> name;
        std::cout << "Hello, " << name << "!\n";
        return 0;
      }

Rendered
^^^^^^^^

.. tb-code:: c++
   :name: code-ex3
   :caption: Hello from C++
   :compileargs: ['-Wall', '-Wextra', '-pedantic', '-std=c++11']
   :stdin: Alice

   // A simple test for C++11 compiler
   #include <iostream>
   #include <string>

   int main() {
     int test[] = { 1, 2, 3, 5, 8 };
     for (auto i: test) {
       std::cout << "i is " << i << '\n';
     }

     std::string name;
     std::cin >> name;
     std::cout << "Hello, " << name << "!\n";
     return 0;
   }
