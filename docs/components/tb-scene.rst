.. _tb-scene:

tb-scene
========

The ``tb-scene`` directive groups a complete instructional scene. Use it alone
for a static composition or inside :ref:`tb-stack` for a navigable step.
Objects and references are local to the scene. Every referenced object must be
declared in that scene; no content is inherited from an earlier scene.

Synopsis
--------

The general format of the ``tb-scene`` directive is:

.. code-block:: rst

   .. tb-scene::
      :optional parameter: value

      + --- Scene content ---
      |
      | prose, code blocks, keyed tb-array and tb-graph objects,
      | and tb-pointer declarations
      |
      + ---------------------

Options
-------

**caption**
   ``String``. Optional.
   Plain-text explanation of this scene. Stacks include it in the scene
   heading above the navigation buttons and scene count.

**class**
   ``String`` or ``List``. Optional.
   Space-separated CSS classes for this scene.
   See :ref:`common` for details.

**name**
   ``String``. Optional.
   Sphinx reference target for this particular scene.
   See :ref:`common` for details.

Content and references
----------------------

Arrays, graphs, and pointers must be immediate children with unique object
keys in the scene. They can accompany normal RST content and code blocks.
References can precede their target declarations. A scene may be empty.
Do not place another scene or stack inside a scene, even through a nested
container. Separate static scenes may reuse the same object keys.

Accessibility behavior
----------------------

A scene retains the accessibility of its prose, code, arrays, and graphs.
Pointer descriptions identify target positions as text as well as visual
arrows. When a scene is part of a stack, inactive scenes are hidden until
navigation selects them or a document link reveals their named content.

Fallback behavior
-----------------

Standalone scenes have no playback controls. HTML without JavaScript, text,
and PDF render scenes as static content. Captions and pointer positions remain
available in every builder.

Examples
--------

Example 1: A static array and pointer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-scene::

            .. tb-array:: values

               3 7 11

            .. tb-pointer:: current
               :at: values.slot[1]

   .. tb-tab:: Rendered

      .. tb-scene::

         .. tb-array:: values

            3 7 11

         .. tb-pointer:: current
            :at: values.slot[1]
