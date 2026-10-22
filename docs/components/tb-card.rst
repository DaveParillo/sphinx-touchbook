.. _tb-card:

tb-card
=======

The ``tb-card`` directive groups a complete instructional composition. Use it
alone for a static composition or inside :ref:`tb-deck` for a navigable step.
Objects and references are local to the card. Every referenced object must be
declared in that card; no content is inherited from an earlier card.

Synopsis
--------

The general format of the ``tb-card`` directive is:

.. code-block:: rst

   .. tb-card::
      :optional parameter: value

      + --- Card content ---
      |
      | prose, code blocks, keyed tb-array and tb-graph objects,
      | and tb-pointer declarations
      |
      + ---------------------

Options
-------

**caption**
   ``String``. Optional.
   Plain-text explanation of this card. Decks show it beside the navigation
   controls, or below them in narrow layouts. It also names the card for
   assistive technology.

**class**
   ``String`` or ``List``. Optional.
   Space-separated CSS classes for this card.
   See :ref:`common` for details.

**name**
   ``String``. Optional.
   Sphinx reference target for this particular card.
   See :ref:`common` for details.

Content and references
----------------------

Any content except a deck or another card is valid content.
References in a card can precede their target declarations.
A card may be empty.
Different cards may reuse the same object keys for graph or
pointer directives.

Accessibility behavior
----------------------

A standalone card is a group named by its card heading. In an interactive
deck, it is described as a slide and named by its caption, or by its position
and total count when no caption is provided.

A card does not alter the accessibility of its content.
When a card is part of a deck, inactive cards are hidden in HTML until
navigation selects them or a document link reveals their named content.

Fallback behavior
-----------------

Standalone cards have no playback controls. HTML without JavaScript, text,
and PDF render cards as static content. Captions and pointer positions remain
available in every builder.

Examples
--------

Example 1: A static array and pointer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-card::

            .. tb-array:: values

               3 7 11

            .. tb-pointer:: current
               :at: values.slot[1]

   .. tb-tab:: Rendered

      .. tb-card::

         .. tb-array:: values

            3 7 11

         .. tb-pointer:: current
            :at: values.slot[1]
