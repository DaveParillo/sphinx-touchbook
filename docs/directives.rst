.. Sphinx-Touchbook: Interactive textbook widgets for Sphinx-doc.
   Copyright (C) 2026 Dave Parillo.
   See https://daveparillo.github.io/sphinx-touchbook/ for details.

Touchbook Directives Documentation
==================================

Every Touchbook directive has a single purpose.
Each is detailed below, including:

- What each directive allows you to create
- The syntax for using each directive and parameter
- Examples, or links to examples, of how instructors can use these directives
  in interactive textbook work
- Available additional developer documentation or notes

Custom Touchbook directives exist in the following general categories.
Implemented directives link to detailed pages. Planned directives are listed as
plain text until they exist.

================= ===================================
Categories        Directives
================= ===================================
Working with Code - :doc:`components/tb-code`
                  - :doc:`components/tb-file`
Containers        - :doc:`components/tb-group`
                  - :doc:`components/tb-reveal`
                  - :doc:`components/tb-video`
Assessments       - :doc:`components/tb-choice`
                  - :doc:`components/tb-blank`
                  - :doc:`components/tb-click`
                  - :doc:`components/tb-match`
                  - ``tb-order`` (planned)
                  - ``tb-parsons`` (planned)
================= ===================================

.. toctree::
   :hidden:
   :titlesonly:

   components/tb-code
   components/tb-blank
   components/tb-choice
   components/tb-click
   components/tb-match
   components/tb-file
   components/tb-group
   components/tb-reveal
   components/tb-video

General Syntax
--------------

All directives start with ``..``, then a single space, followed by the name of
the directive, then ``::``.

Many directives also accept options. Options are indented below the directive
line and begin with ``:``:

.. tb-group::
   :name: directives-reveal-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-reveal::
            :showlabel: Show answer
            :hidelabel: Hide answer

            The answer is 42.

   .. tb-tab:: Rendered

      .. tb-reveal::
         :showlabel: Show answer
         :hidelabel: Hide answer

         The answer is 42.

Container directives can contain other directives:

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-group::

            .. tb-tab:: First tab

               Content for the first tab.

            .. tb-tab:: Useful forms

               Here is a useful summation, along with the closed-form solution:

               .. math::

                  \sum_{k = 1}^{n} k = \frac{n (n+1)}{2}.

   .. tb-tab:: Rendered

      .. tb-group::

         .. tb-tab:: First tab

            Content for the first tab.

         .. tb-tab:: Useful forms

            Here is a useful summation, along with the closed-form solution:

            .. math::

               \sum_{k = 1}^{n} k = \frac{n (n+1)}{2}.

Every Touchbook directive accepts the optional ``name``
`Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
If omitted, an ID is automatically generated based on the current
document and node position.
This ID is deterministic, but not stable:
if your document changes the generated name may change.
Use an explicit ``name`` when you want a stable
human-readable target for references, tests, or custom integration.

.. code-block:: rst

   .. tb-reveal::
      :name: optional-name

      Content that can be revealed.
