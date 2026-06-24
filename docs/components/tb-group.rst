tb-group
========

The ``tb-group`` directive is a container that splits related content into
selectable tabs in HTML output.

Synopsis
--------

The general format of the ``tb-group`` directive is:

.. code-block:: rst

   .. tb-group::
      :optional parameter: value

      + --- Tab area ---
      |
      | .. tb-tab:: required tab label
      |
      |    one or more lines of tab content
      |
      | .. tb-tab:: required tab label
      |
      |    one or more lines of tab content
      |
      + ----------------

The ``tb-group`` directive must contain at least one immediate ``tb-tab``
directive and may contain only ``tb-tab``\ s.

Content placed as an immediate child of ``tb-group`` that is not inside
``tb-tab`` is ignored by the tab interface.

There is no hard limit on the maximum number of tabs allowed.
On narrow pages, the tabs wrap to fit the available width.
Too many tabs can impair usability, so use judgment when grouping content.

Options
-------

**tab label**
   ``String``. Required for ``tb-tab``.
   Creates a new tab and labels it with the provided string.
   The label may contain spaces.

   Any valid Sphinx markup can reside within a tab.

**name**
   ``String``. Optional.
   Sphinx reference name for this group or tab. This is a
   `Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   If omitted, docutils assigns a deterministic generated ID derived from the
   document and node position.

Sphinx configuration options
----------------------------

No directive-specific configuration options exist.

Accessibility behavior
----------------------

The no-JS HTML fallback shows each tab as a labeled content block. HTML creates
an ARIA ``tablist`` with native ``button`` controls and keyboard support for
Arrow Left, Arrow Right, Home, and End.

Fallback behavior
-----------------

PDF and text builders render each tab as labeled static content.

Examples
--------

Example 1: Basic tab group
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: group-ex1-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-group::

            .. tb-tab:: First tab

               This is the first tab.

            .. tb-tab:: Second tab

               This is the second tab.

   .. tb-tab:: Rendered

      .. tb-group::

         .. tb-tab:: First tab

            This is the first tab.

         .. tb-tab:: Second tab

            This is the second tab.

Example 2: Sphinx markup inside tabs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::
   :name: group-ex2-tabs

   .. tb-tab:: Source

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

   .. tb-tab:: Rendered

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
