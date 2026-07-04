.. _general:

General Syntax
==============

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

.. _common:

Common options
--------------

Every Touchbook directive accepts the optional ``name`` and ``class``
parameters as described in 
`Docutils common option <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
If ``name`` is omitted, an ID is automatically generated based on the current
document and node position.
This ID is deterministic, but not stable:
if your document changes the generated name may change.
Use an explicit ``name`` when you want a stable
human-readable target for references, tests, or custom integration.

.. code-block:: rst

   .. tb-reveal::
      :name: optional-name

      Content that can be revealed.

The ``class`` parameter takes a space-separated list of class names.
HTML output attaches those classes to the directive's root ``tb-*`` element.

.. code-block:: rst

   .. tb-reveal::
      :class: review-note compact

      Content that can be styled with project CSS.

.. code-block:: rst

   .. tb-code:: python
      :class: highlight-override

      print("Hello")

