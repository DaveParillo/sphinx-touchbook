PDF accessibility fixture
=========================

Chapter heading
---------------

A paragraph with an `external link <https://example.org>`__.

A footnote [#note]_.

.. [#note] Native tagged footnote text.

.. note::

   A note with a list:

   * First note item.
   * Second note item.

* First item.
* Second item with **strong text**.

Term
   A definition with a native list label.

.. glossary::

   tagged term
      :Relation: A nested glossary field.

      A definition with a reference destination.

See :term:`tagged term`.

:Field label: A field-list value.

Section heading
~~~~~~~~~~~~~~~

Subsection heading
^^^^^^^^^^^^^^^^^^

Subsubsection heading
"""""""""""""""""""""

Paragraph heading
+++++++++++++++++

Subparagraph heading
********************

Deep paragraph.

.. parsed-literal::

   A **strong** word and an `inline link <https://example.org/code>`__.

.. list-table:: Measurements
   :header-rows: 1

   * - Name
     - Value
   * - Sample
     - 42

.. tb-group::

   .. tb-tab:: Run It

      .. tb-code:: cpp
         :caption: A small C++ listing

         // A comment
         int main() { return 0; }

.. code-block:: python
   :caption: Standard listing

   # Standard Sphinx code
   print("Hello")

.. tb-file::
   :filename: input.txt
   :caption: Input data

   Alice
   Bob

.. figure:: pixel.png
   :alt: A blue test square
   :width: 40px

   Standard figure caption.

.. tb-file:: pixel.png
   :filename: sample.png
   :alt: A blue square supplied as a runtime file
   :caption: Runtime image

.. image:: pixel.png
   :class: tb-pdf-artifact
   :width: 20px

.. index:: accessibility

An indexed term.

.. include:: long-table.rst
