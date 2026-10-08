.. _tb-pointer:

tb-pointer
==========

The ``tb-pointer`` directive points to any keyed object in a :ref:`tb-scene`,
or to a position within an array or graph. Its required argument is the
pointer's object key. Pointers and iterators use the same arrows; iterator kind
adds movement bounds validation.

Synopsis
--------

The general format of the ``tb-pointer`` directive is:

.. code-block:: rst

   .. tb-pointer:: object-key
      :at: position-reference
      :optional parameter: value

The pointer body is empty. Place the declaration directly inside a scene.
Either ``:at:`` or ``:range:`` is required. Targets can be declared later in the
same scene.

Options
-------

**at**
   ``String``. Required when ``range`` is absent; otherwise optional.
   Current target: a bare scene object key such as ``values``, ``chain``, or
   ``current``, or a typed position such as ``values.slot[0]``, ``values.item[first]``,
   ``values.begin``, ``values.end``, ``chain.node[head]``, or pointer-only
   ``null``. Slots are zero-based regardless of the array's ``start-index``.
   A bare key targets the whole object, including another pointer. It does not
   select an array's first element or a graph node with the same key.
   Item references follow explicitly keyed items to their current positions.
   ``values.end`` is a boundary, not an element. Without ``at``, the position
   defaults to the beginning of the range, or null for ``:range: null``.

**caption**
   ``String``. Optional.
   Plain-text caption for this pointer occurrence.

**class**
   ``String`` or ``List``. Optional.
   Space-separated CSS classes for this pointer.
   See :ref:`common` for details.

**kind**
   ``String``. Optional. Default: ``pointer``.
   Either ``pointer`` or ``iterator``. Iterator kind requires an array range
   and a position within its bounds, including its end boundary. Null ranges
   and positions are invalid for iterators. Kind remains stable for a pointer
   key across stack scenes.

**label**
   ``String``. Optional. Default: the object key.
   Plain-text label beside the arrow.

**name**
   ``String``. Optional.
   Sphinx reference target for this particular pointer occurrence.
   See :ref:`common` for details.

**range**
   ``String``. Required for iterators; optional for pointers.
   An array key, a pair of ordered array bounds, or pointer-only ``null``.
   ``values`` means ``values.begin, values.end``. An explicit interval, such
   as ``values.slot[1], values.end``, is half-open; its end is also a valid
   iterator position. Bounds must belong to the same array. Empty ranges are
   valid. Item and graph-node references cannot be range bounds.
   For pointer kind, the range supplies a default position without restricting
   an explicit ``at``. A null range needs no target object.

Accessibility behavior
----------------------

HTML places array pointer labels and arrows above horizontal arrays or beside
vertical arrays. An end pointer marks a separate boundary position, and an
empty array retains its end-position description. Pointers to graph nodes have
labelled arrows in their diagrams and text descriptions beside them. Tree
styles support multiple pointers and indicators, including shared targets.
Labels sharing a target are grouped, each with its own arrow. Tree pointers
use a gap between the target's children, or a position below a leaf, so their
arrows do not cross other tree nodes. Whole-object pointers
show a labelled arrow and a document link to the target object. They can also
target pointers, including themselves; the target is the object itself and is
not dereferenced. Document ``name`` values remain separate from object keys.
Arrows toward invisible graph nodes retain
an undisplayed target without revealing its value.

Pointer descriptions identify the target, its current value, and its displayed
array index when applicable. Visual arrow symbols are hidden from assistive
technology; the equivalent text description remains available. Pointer
positions are determined separately in each scene, including omitted ``at``
defaults.

Fallback behavior
-----------------

HTML without JavaScript retains pointer arrows and descriptions. Text and PDF
include the pointer's position as prose; graph diagrams also include the arrow.
A null pointer is described as null. No pointer is dereferenced or evaluated.

Examples
--------

Example 1: Point to a keyed item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-scene::

            .. tb-pointer:: current
               :at: values.item[second]

            .. tb-array:: values

               first = 8
               second = 13
               third = 21

   .. tb-tab:: Rendered

      .. tb-scene::

         .. tb-pointer:: current
            :at: values.item[second]

         .. tb-array:: values

            first = 8
            second = 13
            third = 21

Example 2: An iterator at the end
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-scene::

            .. tb-array:: values
               :orientation: vertical

               3 5 7

            .. tb-pointer:: current
               :kind: iterator
               :range: values
               :at: values.end

   .. tb-tab:: Rendered

      .. tb-scene::

         .. tb-array:: values
            :orientation: vertical

            3 5 7

         .. tb-pointer:: current
            :kind: iterator
            :range: values
            :at: values.end

For a complete traversal example, see :ref:`tb-stack`.

Example 3: Point to a graph node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``network.node[b]`` draws a labelled arrow pointing directly to node ``b``,
whose value is ``13``. This serves the same purpose as an array pointer:
identifying the current element visually. The list style arranges the graph
horizontally and places the pointer below its target node.

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-scene::

            .. tb-pointer:: current
               :at: network.node[b]

            .. tb-graph:: network
               :style: list

               a[8] -> b[13] -> c[21]

   .. tb-tab:: Rendered

      .. tb-scene::

         .. tb-pointer:: current
            :at: network.node[b]

         .. tb-graph:: network
            :style: list

            a[8] -> b[13] -> c[21]

Example 4: Point to a whole object or another pointer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The bare key ``network`` selects the complete graph. The bare key ``current``
selects the pointer object itself. These targets show links to the objects.

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-scene::

            .. tb-pointer:: address
               :at: current

            .. tb-pointer:: current
               :at: network

            .. tb-graph:: network

               a[8] -> b[13] -> c[21]

   .. tb-tab:: Rendered

      .. tb-scene::

         .. tb-pointer:: address
            :at: current

         .. tb-pointer:: current
            :at: network

         .. tb-graph:: network

            a[8] -> b[13] -> c[21]

Example 5: Track multiple tree positions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pointers and local indicators can share a tree. Here ``head`` and ``previous``
both point to the root, while ``current`` points to its left child. Each label
has its own arrow below its target.

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-scene::

            .. tb-graph:: tree
               :style: tree
               :indicators: head=root

               root[8] -left-> child[3]
               root -right-> other[12]
               child -right-> inserted[6]

            .. tb-pointer:: previous
               :at: tree.node[root]

            .. tb-pointer:: current
               :at: tree.node[child]

   .. tb-tab:: Rendered

      .. tb-scene::

         .. tb-graph:: tree
            :style: tree
            :indicators: head=root

            root[8] -left-> child[3]
            root -right-> other[12]
            child -right-> inserted[6]

         .. tb-pointer:: previous
            :at: tree.node[root]

         .. tb-pointer:: current
            :at: tree.node[child]
