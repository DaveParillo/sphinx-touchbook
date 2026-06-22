tb-file
=======

The ``tb-file`` directive describes a simulated local file that can be shown in
the document, hidden for later execution use, or used as a stable named
artifact in a textbook example.

``tb-file`` creates the file artifact and renders useful HTML, text, and
PDF-oriented fallback output. A ``tb-code`` directive can attach registered
files to an execution request with its ``files`` option.

Syntax
------

The general format of the ``tb-file`` directive is:

.. code-block:: rst

   .. tb-file::
      :filename: input.txt

      File contents go here.

The directive can also read content from a source file in the Sphinx project:

.. code-block:: rst

   .. tb-file:: examples/input.txt
      :filename: input.txt

Options
-------

``filename``
   ``String``. Required. The simulated local filename.
   This is the filename that code should expect when the file is eventually
   attached to an execution environment.

   Filenames may contain only letters, numbers, dots, underscores, hyphens, and
   forward slashes and must be relative paths.
   Empty path segments, ``.``, ``..``, absolute paths, spaces, and other
   punctuation are rejected.

``name``
   ``String``. Optional.
   A Docutils common option used as a Sphinx reference target.
   See the `Docutils common options <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__ reference.

``hidden``
   ``Boolean``. Optional.
   If present, register the file but do not render it in output.

``readonly``
   ``Boolean``. Optional.
   If present, do not add editing controls for text files in HTML.
   Binary files are never editable.

``editable``
   ``Boolean``. Optional. Text files are editable by default.
   This option can be used to explicitly request editing if a project-level
   default later changes.

``encoding``
   ``String``. Optional. Encoding used when reading a referenced text file.
   Default is ``utf-8``.

Examples
--------

Inline text file:

.. code-block:: rst

   .. tb-file::
      :name: sample-input
      :filename: input.txt

      Hello file!

Rendered example:

.. tb-file::
   :name: sample-input
   :filename: input.txt

   Hello file!

Hidden text file:

.. code-block:: rst

   .. tb-file::
      :filename: data/input.txt
      :hidden:

      100

Referenced image file:

.. code-block:: rst

   .. tb-file:: flow.png
      :filename: images/diagram.png

Binary files:

Referenced binary files are registered and marked read-only. HTML can display
image formats supported by browsers. Text and PDF-oriented builders render a
labeled file reference for binary files rather than embedding incompatible
data. Authors should use builder-specific ``only`` sections when a binary file
format is suitable for one output format but not another, such as a
PostScript file for LaTeX-oriented output.

Reading a simulated file from C++:

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

File definition:

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

Companion source:

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

When Run is pressed, the current contents of ``poem_text`` are sent with the
execution request. If the file is edited in the attached-file editor, that
edited content is sent instead of the original content.

Accessibility
-------------

Visible text files render their filename as a caption and their content as
readable preformatted text before JavaScript runs. When editing is available,
HTML output adds a native button and textarea with programmatic labels.

Image files render with the simulated filename as alternate text. Authors
should choose filenames that communicate the image's instructional role when
using image files this way.

Fallback Behavior
-----------------

Text and PDF-oriented builders render visible text files as a labeled file listing.
Image files render as labeled image-file references.
Hidden files are not rendered, but remain available in the Sphinx environment
registry for later execution integration.

