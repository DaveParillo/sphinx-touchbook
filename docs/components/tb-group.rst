tb-group
========

The ``tb-group`` directive is a container that splits related content into selectable tabs, viewable one at a time in enhanced HTML output.

Synopsis
--------

The general format of the ``tb-group`` directive is:

.. code-block:: rst

   .. tb-group::
      :name: optional-name

      .. tb-tab:: Tab 1
         :name: optional-tab-name

         Content area 1

      .. tb-tab:: Tab 2

         Content area 2

There is no hard limit on the maximum number of tabs allowed.
On narrow pages, the tabs wrap to fit the available width.
Too many tabs can impair usability, so use judgment when grouping content.

Required content
----------------

The ``tb-group`` directive must contain at least one immediate ``tb-tab``
directive and may contain only ``tb-tab``\ s.

Content placed as an immediate child of ``tb-group`` that is not inside ``tb-tab`` is ignored by the enhanced tab interface.

``tb-tab`` label
   ``String``. Creates a new tab and labels it with the provided string. A label is required and may contain spaces.

   Any valid Sphinx markup can reside within a tab.

Options
-------

``name``
   ``String``. Optional.
   
   Sphinx reference name for this group or tab. This is a `Docutils common
   option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

Sphinx configuration options
----------------------------

No directive-specific configuration options exist.

Accessibility and fallback behavior
-----------------------------------

The no-JS HTML fallback shows each tab as a labeled content block. The enhanced Web Component creates an ARIA ``tablist`` with native ``button`` controls and keyboard support for Arrow Left, Arrow Right, Home, and End.

PDF and text builders render each tab as labeled static content.

Examples
--------

Example 1: Basic tab group
~~~~~~~~~~~~~~~~~~~~~~~~~~

Source
^^^^^^

.. code-block:: rst

   .. tb-group::
      :name: tab-ex1

      .. tb-tab:: First tab
         :name: tab-ex1-first

         This is the first tab.

      .. tb-tab:: Second tab
         :name: tab-ex1-second

         This is the second tab.

Rendered
^^^^^^^^

.. tb-group::
   :name: tab-ex1

   .. tb-tab:: First tab
      :name: tab-ex1-first

      This is the first tab.

   .. tb-tab:: Second tab
      :name: tab-ex1-second

      This is the second tab.

Example 2: Sphinx markup inside tabs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Source
^^^^^^

.. code-block:: rst

   .. tb-group::
      :name: tab-ex2

      .. tb-tab:: Python
         :name: tab-ex2-python

         .. code-block:: python

            print("Hello from Python")

      .. tb-tab:: C++
         :name: tab-ex2-cpp

         .. code-block:: cpp

            #include <iostream>

            int main() {
                std::cout << "Hello from C++\n";
            }

Rendered
^^^^^^^^

.. tb-group::
   :name: tab-ex2

   .. tb-tab:: Python
      :name: tab-ex2-python

      .. code-block:: python

         print("Hello from Python")

   .. tb-tab:: C++
      :name: tab-ex2-cpp

      .. code-block:: cpp

         #include <iostream>

         int main() {
             std::cout << "Hello from C++\n";
         }
