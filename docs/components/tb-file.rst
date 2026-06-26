.. Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
   Copyright (C) 2026 Dave Parillo.
   See https://daveparillo.github.io/sphinx-touchbook/ for details.

tb-file
=======

The ``tb-file`` directive describes a simulated local file. A file can be
shown in the document, hidden for later execution use, or attached to a
``tb-code`` execution request.

Synopsis
--------

The general format of the ``tb-file`` directive is:

.. code-block:: rst

   .. tb-file::
      :filename: required-filename
      :optional parameter: value

      + --- File content area ---
      |
      | one or more lines of file content
      |
      + -------------------------

The ``filename`` option is required.
Inline content or a referenced source file is required.

The directive can also read content from a source file in the Sphinx project:

.. code-block:: rst

   .. tb-file:: examples/input.txt
      :filename: input.txt

Options
-------

**filename**
   ``String``. Required. The simulated local filename.
   This is the filename that code should expect when the file is attached to
   an execution environment.

   Filenames may contain only letters, numbers, dots, underscores, hyphens, and
   forward slashes and must be relative paths.
   Empty path segments, ``.``, ``..``, absolute paths, spaces, and other
   punctuation are rejected.

**editable**
   ``Boolean``. Optional. Text files are editable by default.
   This option can explicitly request editing if a project-level default later
   changes.

**encoding**
   ``String``. Optional. Encoding used when reading a referenced text file.
   Default is ``utf-8``.

**hidden**
   ``Boolean``. Optional.
   If present, register the file but do not render it in output.

**name**
   ``String``. Optional.
   Sphinx reference name for this file artifact.
   This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

**readonly**
   ``Boolean``. Optional.
   If present, do not add editing controls for text files in HTML.
   Binary files are never editable.

Sphinx configuration options
----------------------------

No directive-specific configuration options exist.

Accessibility behavior
----------------------

Visible text files render their filename as a caption and their content as
readable preformatted text before JavaScript runs. When editing is available,
HTML adds a native button and textarea with programmatic labels.

Image files render with the simulated filename as alternate text. Authors
should choose filenames that communicate the image's instructional role when
using image files this way.

Fallback behavior
-----------------

Text and PDF-oriented builders render visible text files as a labeled file
listing. Image files render as labeled image-file references. Hidden files are
not rendered, but remain available in the Sphinx environment registry for
later execution integration.

Referenced binary files are registered and marked read-only. HTML can display
image formats supported by browsers. Text and PDF-oriented builders render a
labeled file reference for binary files rather than embedding incompatible
data. Authors should use builder-specific ``only`` sections when a binary file
format is suitable for one output format but not another, such as a
PostScript file for LaTeX-oriented output.

Examples
--------

Example 1: Inline text file
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: file-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-file::
            :filename: input.txt

            Hello file!

   .. tb-tab:: Rendered

      .. tb-file::
         :filename: input.txt

         Hello file!

Example 2: Hidden text file
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: file-ex2-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-file::
            :filename: data/input.txt
            :hidden:

            100

   .. tb-tab:: Rendered

      .. tb-file::
         :filename: data/input.txt
         :hidden:

         100

      The file is registered but not displayed.

Example 3: Reading a simulated file from C++
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example uses text from Lewis Carroll's *Jabberwocky*.
When Run is pressed, the current contents of ``poem_text`` are sent with the
execution request. If the file is edited in the attached-file editor, that
edited content is sent instead of the original content.

.. tb-group::
   :name: file-ex3-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-file::
            :filename: poem_text

            Beware the Jabberwock, my son!
              The jaws that bite, the claws that catch!

         .. tb-code:: c++
            :caption: Read a simulated local file
            :files: poem_text

            #include <fstream>
            #include <iostream>

            int main () {
              std::ifstream is("poem_text");
              char c;
              while (is.get(c)) {
                std::cout << c;
              }
              is.close();
              return 0;
            }

   .. tb-tab:: Rendered

      .. tb-file::
         :filename: poem_text

         Beware the Jabberwock, my son!
           The jaws that bite, the claws that catch!
         Beware the Jubjub bird, and shun
           The frumious Bandersnatch!"

         He took his vorpal sword in hand:
           Long time the manxome foe he sought --
         So rested he by the Tumtum tree,
           And stood awhile in thought.

         And, as in uffish thought he stood,
           The Jabberwock, with eyes of flame,
         Came whiffling through the tulgey wood,
           And burbled as it came!

         One, two! One, two! And through and through
           The vorpal blade went snicker-snack!
         He left it dead, and with its head
           He went galumphing back.

         And, has thou slain the Jabberwock?
           Come to my arms, my beamish boy!
         O frabjous day! Callooh! Callay!'
           He chortled in his joy.

      -- Lewis Carroll's *Jabberwocky*.

      .. tb-code:: c++
         :caption: Read a simulated local file
         :files: poem_text

         #include <fstream>
         #include <iostream>

         int main () {
           std::ifstream is("poem_text");
           char c;
           while (is.get(c)) {
             std::cout << c;
           }
           is.close();
           return 0;
         }
