.. _tb-graph:

tb-graph
========

Use ``tb-graph`` to display a directed graph, tree, linked list, array, or ring.
Declare nodes with explicit keys and values, then connect them with arrows. The
same syntax supports all these structures without choosing a graph type.
Diagrams work without JavaScript and have readable descriptions.

Synopsis
--------

The general format of the ``tb-graph`` directive is:

.. code-block:: rst

   .. tb-graph:: [optional object key]
      :optional parameter: value

      + --- Graph data ---
      |
      | node declarations and directed relationships
      |
      + ------------------

The optional argument identifies this graph when ``highlight`` or qualified
``overlay`` references target its nodes. It is separate from ``name``, which
creates a Sphinx reference target.
An empty body displays an empty graph.

Options
-------

**caption**
   ``String``. Optional.
   Plain-text caption displayed with the graph, only when provided.

**class**
   ``String``. Optional.
   Space-separated CSS class names. This is a
   `Docutils common option
   <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   See :ref:`common` for details.

**description**
   ``String``. Optional.
   Plain-text explanation of the diagram. Use it to describe the instructional
   meaning, such as why a node is highlighted or what an insertion changes.
   It replaces the automatically generated text description in HTML, text,
   and PDF. Long descriptions can continue on indented option lines.
   Describe the relevant values and connections as well as their meaning.

**highlight**
   ``String``. Optional.
   Space-separated references to nodes in this graph, such as
   ``tree.node[root] tree.node[child]``. Requires an explicit object key,
   here ``tree``. All references must resolve to declared nodes. Highlighted
   nodes have thicker borders. Highlighting an invisible node does not show it.

**indicators**
   ``String``. Optional. None by default.
   Space-separated ``label=node-key`` pairs, such as
   ``head=a current=b tail=c``. Each pair adds a labelled arrow pointing to
   that node or array cell. Every style supports multiple indicators.
   Labels follow the same identifier rules as node keys and must be unique
   within the directive. Targets must be declared, visible nodes in this graph;
   forward declarations and unused cells are allowed. Multiple indicators may
   point to the same target.
   An object-key argument is not required.
   Pairs may continue on indented option lines. Do not add spaces around ``=``.

**label**
   ``String``. Optional.
   Plain-text object label. Displayed only when explicitly provided.

**name**
   ``String``. Optional.
   Sphinx reference target for this graph occurrence. It does not supply an
   object key. This is a
   `Docutils common option
   <https://docutils.sourceforge.io/docs/ref/rst/directives.html#common-options>`__.
   See :ref:`common` for details.

**overlay**
   ``String``. Optional. None by default.
   Draw outlines around groups of declared, visible node keys. Each line
   specifies one overlay, with one or more space-separated targets such as
   ``parent child``. Bare local keys work without a graph object key.
   Qualified local references, such as ``tree.node[parent]``, also work when
   the graph has that object key. Repeated targets count once within a group.
   Every graph style supports overlays, including array value cells.
   Overlays do not change node placement and can encompass other objects
   between their targets. See `Overlay groups`_ for multiple overlays and
   individual settings.

**overlay-layer**
   ``String``. Optional. Defaults to ``foreground``.
   Default layer for overlays: in front of the graph (``foreground``) or
   behind it (``background``). Requires ``overlay``. Outlines are unfilled;
   graph objects cover portions of background outlines.

**overlay-padding**
   ``Number``. Optional. Defaults to ``8`` points.
   Default minimum space between target bounds and their enclosing outlines.
   Accepts finite numbers from ``0`` to ``1000``. Requires ``overlay``.

**overlay-shape**
   ``String``. Optional. Defaults to ``ellipse``.
   Default outline shape for overlays: ``ellipse``, ``circle``, or
   ``rectangle``. ``box`` is an alias for ``rectangle``. Ellipses follow the
   orientation of the target group; circles have equal width and height;
   rectangles enclose an area parallel to the diagram edges. Requires
   ``overlay``. This option does not change graph node shapes; use a named
   style for those.

**show-indices**
   ``Flag``. Optional. Disabled by default.
   Show zero-based indices alongside values in the ``array`` style or a style
   based on it. Indices follow node declaration order, including invisible
   cells. This flag has no effect on other styles.

**style**
   ``String``. Optional. Defaults to ``graph``.
   Choose a presentation preset: ``list`` uses horizontal light-blue boxes
   with arrowheads; ``tree`` uses vertical light-blue circles with straight
   connectors and no arrowheads. ``graph`` uses unfilled ellipses with directed
   arrows. ``array`` shows adjacent table cells horizontally, with only values
   visible by default. ``ring`` uses Graphviz's circular ``circo`` layout and
   unfilled ellipse nodes. Books can define additional style names in
   ``tb_graph_styles``.
   The graph data syntax and node identities are the same for every style.

Style configuration
-------------------

``tb_graph_styles`` in ``conf.py`` customizes built-in presets or adds named
styles. Settings describe presentation; authors do not write DOT attributes.
For example:

.. code-block:: python

   tb_graph_styles = {
       "list": {"fill": "#e0f2fe", "font-size": 14},
       "plain-list": {"base": "list", "fill": None},
       "vertical-array": {"base": "array", "orientation": "vertical"},
       "tree": {
           "fill": "#dcfce7", "highlight-fill": "#fde68a",
           "level-spacing": 0.4,
       },
   }

Select the custom preset with ``:style: plain-list``. Custom styles inherit
the configured built-in base. Unknown style names and settings are errors.

.. list-table:: Style settings
   :header-rows: 1
   :widths: 30 70

   * - Setting
     - Accepted values
   * - ``base``
     - ``graph``, ``list``, ``tree``, ``array``, or ``ring``.
       Custom styles default to ``graph``;
       built-in overrides default to their own preset.
   * - ``orientation``
     - ``horizontal`` or ``vertical``. Does not affect ``ring`` layout.
   * - ``shape``
     - ``box``, ``rectangle``, ``circle``, or ``ellipse``.
   * - ``fill``
     - Color name or ``#rrggbb``; ``None`` leaves nodes unfilled.
   * - ``highlight-fill``
     - Color name or ``#rrggbb`` for highlighted nodes. Defaults to ``None``,
       which preserves their normal fill. The thicker border remains.
       Invisible nodes remain invisible even when highlighted.
   * - ``unused-fill``
     - Color name or ``#rrggbb`` for unused array cells, represented by an empty
       quoted value. Defaults to light grey (``#eeeeee``) for ``array``.
       ``None`` leaves unused cells unfilled. ``highlight-fill`` takes
       precedence when an unused cell is highlighted. Other styles ignore
       this setting.
   * - ``font``
     - Font family name; defaults to ``sans-serif``.
   * - ``font-size``
     - Positive number in points; defaults to ``14``.
   * - ``connectors``
     - ``straight`` or ``curved``.
   * - ``arrows``
     - ``normal``, ``vee``, or ``none``.
   * - ``relationship-labels``
     - Boolean. Defaults to ``True`` for ``graph``, otherwise ``False``.
   * - ``node-spacing``
     - Positive minimum sibling spacing in inches; defaults to ``0.25``.
       For ``ring``, controls minimum node separation.
   * - ``level-spacing``
     - Positive minimum level spacing in inches; defaults to ``0.3`` for
       ``tree``, otherwise ``0.5``.

Array and ring presentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``array`` places cells in node declaration order, independently of edges or
forward references. It displays values without keys, indices, or connectors.
All cells in one array have the same width and height, sized to fit the longest
value. The first and last cells have rounded outer corners; interior joins
remain straight. An empty quoted value, such as ``spare['']``, represents an
unused cell and receives a light-grey fill. Use ``unused-fill`` to change it.

Use ``:show-indices:`` to add an index row below a horizontal array or an index
column to the left of a vertical array. Choose vertical orientation through a
named style in ``tb_graph_styles``. Invisible nodes reserve undisplayed cells;
their values and indices remain hidden. Highlight borders and
``highlight-fill`` apply to individual value cells.

Array styles preserve relationship data, but omit relationships from the
diagram and its automatic description. Node shape, connector, arrow, and
spacing settings do not affect the table. For sequence-specific features such
as ranges and slot references, use :ref:`tb-array`.

``ring`` selects Graphviz's
`circo layout <https://graphviz.org/docs/layouts/circo/>`_ for HTML and PDF.
Declare the closing edge explicitly to show a cycle; the style does not create
edges. Orientation and level spacing do not affect circular layout.

Indicators
~~~~~~~~~~

Use ``:indicators:`` to point out positions such as the head, tail, or current
value. All styles support indicators. Indicator labels appear above horizontal
arrays and to the right of vertical arrays. Lists place labels below their
nodes; general graphs and rings place labels near their targets automatically.
Labels sharing a target are arranged together with separate arrows. Rings
reserve extra separation when indicators are present to keep labels readable.
Indicators annotate targets without adding semantic nodes or relationships.
Their targets follow node identity rather than the displayed value or index.

Tree styles, including book styles based on ``tree``, support multiple
indicators and scene pointers. They may point to different nodes or share
a target, including the root or an internal node. Labels sharing a target
sit side by side, each with its own arrow. Each label group occupies a gap
between the target's children, reusing the tree's
invisible balancing space where available. A leaf's label appears directly
below it. Arrows point back toward their targets without crossing other tree
nodes. Horizontal tree styles use the corresponding gap to the right.
The indicator arrow remains visible even when relationship arrowheads are
disabled by the style.

The automatic text description identifies each indicator's target and value,
including cell indices for arrays. If you provide ``:description:``, include
the indicator meanings and
positions in your explanation.

Tree spacing
~~~~~~~~~~~~

The ``tree`` preset inserts invisible spacing nodes to center parents above
their children. Missing binary children reserve space on the appropriate
side: use ``-left->`` and ``-right->`` to specify that side. Other child edges
use source order; a lone unnamed child occupies the left position. Authors
do not need to declare these spacing nodes. They have no semantic identity
and do not appear in descriptions.

Presets change presentation without enforcing structural tree rules. Tree
spacing applies to components that are trees; cyclic components and components
with shared children retain ordinary automatic layout. Nodes grow to fit their
values rather than clipping long labels.

Data syntax
-----------

Declare a node as ``key[value]``. Values are numbers or single-quoted or
double-quoted strings. Numeric spelling is preserved. Strings support Unicode,
empty values, an escaped enclosing quote, and an escaped backslash. Other
escapes, including ``\n``, are rejected. Keep each string on one physical line.
The data body contains literal values, not nested RST or Graphviz source.

Keys are case-sensitive identifiers beginning with a letter or underscore,
followed by letters, digits, underscores, or hyphens. The key ``null`` is
reserved. Node keys supply identity; values may repeat.

Use ``->`` for a directed edge or ``-key->`` for a named relationship:

.. code-block:: text

   a['10'] -> b['20'] -> c['30']

   root['8'] -left-> child['3']
   root -right-> other['12']

Spaces or tabs are required on both sides of each edge operator. Do not put
whitespace inside the operator or between a node key and its opening bracket.
Blank lines and ``#`` comments outside strings are ignored. Each nonempty
line is one complete declaration or edge chain. Semicolons are unsupported.

Declare every node exactly once in the graph. Bare references can precede or
follow that declaration. Repeating a value declaration is an error, even
when its value agrees. An undeclared endpoint is an error.

Named relationships are unique per source node: one node cannot have two
``-left->`` edges. Different source nodes may reuse a relationship name.
Parallel edges between the same ordered pair require distinct names; do not
mix an unnamed edge with named parallel edges. Duplicate edges are errors.
Cycles, self-edges, disconnected nodes, and empty graphs are allowed.

Invisible components
--------------------

Place ``{invisible}`` after a node declaration to hide the node. Place it
between an edge operator and its destination to hide that edge:

.. code-block:: text

   value['10'] -next-> unseen[''] {invisible}
   value -spacing-> {invisible} spacer[''] {invisible}

Invisible components still participate in layout. Hiding a node does not hide
its incident edges. Edges always connect declared nodes; they cannot connect
to ``null``. To draw an edge toward an undisplayed endpoint, declare an
invisible node and connect a visible edge to it.

Invisible edges and isolated invisible nodes are omitted from descriptions.
A visible edge reaching an invisible node is described as reaching an
``undisplayed endpoint``; that node's hidden key and value are omitted.

Overlay groups
--------------

Each line of ``overlay`` defines a separate group. The directive's
``overlay-shape``, ``overlay-layer``, and ``overlay-padding`` options supply
defaults for all groups. Override any setting by adding
``:overlay-shape: value``, ``:overlay-layer: value``, or
``:overlay-padding: value`` after the target keys on that line:

.. code-block:: rst

   :overlay: parent child
             other :overlay-shape: circle :overlay-layer: background :overlay-padding: 4
   :overlay-shape: rectangle
   :overlay-padding: 12

This draws a rectangle around ``parent`` and ``child`` with 12 points of
padding, and a circle behind ``other`` with 4 points of padding. Settings on
one line do not affect the next group. Write target keys before settings;
each setting can appear once per line. Continue each group on its own line
inside one ``overlay`` option; do not repeat the directive option.
Within each layer, later groups are drawn over earlier groups.

Build requirements
------------------

Install `Graphviz <https://graphviz.org/download/>`_ on the computer that builds
HTML or LaTeX. The ``dot`` executable must be available on ``PATH``; ring styles
also require ``circo`` on ``PATH``. PDF asset
generation also requires Graphviz's Cairo PDF renderer. Graphs with an
``overlay`` require librsvg's ``rsvg-convert`` on ``PATH`` for PDF export.
Install ``librsvg2-bin`` on Debian/Ubuntu or ``librsvg`` with Homebrew.
HTML annotations require only Graphviz. Readers need neither Graphviz,
librsvg, nor JavaScript.

Touchbook loads Sphinx's Graphviz support automatically. If ``dot`` is installed
outside ``PATH``, set ``graphviz_dot`` in ``conf.py``:

.. code-block:: python

   graphviz_dot = "/path/to/dot"

Graphs use automatic layout. Select presentation with ``:style:``. Raw DOT,
engine names, coordinates, and arbitrary Graphviz attributes are not accepted
in the directive.

Click questions
---------------

Use a graph as the source of :ref:`tb-click` to ask students to select nodes.
``tb-hit`` and ``tb-miss`` select local visible node keys for every graph style.
Relationships and indicator labels remain ordinary diagram content.
See :ref:`tb-click` for a tree question example.

Accessibility behavior
----------------------

HTML provides a diagram and a keyboard-accessible ``Text description``
disclosure. The automatic description explains connections using displayed
values, identifies tree roots and leaves, and notes highlights and isolated
nodes. Duplicate values include node keys to distinguish their identities.
Use ``:description:`` to provide the explanation readers need for the lesson.
Object labels and captions appear only when explicitly provided.
Invisible components have no controls. Tree styles place named ``left`` and
``right`` children on their corresponding sides. Relationship names remain
in descriptions even when a style omits them from the diagram.
Overlays are described by shape and target values and keys, including
when ``description`` supplies the main explanation. Outlines do not capture
clicks or keyboard focus.

Fallback behavior
-----------------

HTML displays a static SVG without JavaScript. Text displays the graph
description. PDF includes a vector diagram and the same description, with
captions and labels outside the image. Empty graphs display ``Empty graph.``
Array styles render the same adjacent cells and optional indices in HTML and
PDF; text describes their order and values.
Overlay outlines appear in HTML and PDF. Text describes the nodes they
surround. The diagram expands to keep the complete outline visible.

If Graphviz cannot render a diagram, the build warns and retains the readable
description. Builds with ``--fail-on-warning`` fail on that warning.

Examples
--------

Example 1: An independent graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph::

            a['10'] -> b['20'] -> c['30']

   .. tb-tab:: Rendered

      .. tb-graph::

         a['10'] -> b['20'] -> c['30']

Example 2: Named tree relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph:: tree
            :style: tree
            :indicators: root=root current=inserted
            :caption: A tree with an inserted node
            :description: The root 8 has left child 3 and right child 12.
               Node 6, highlighted, is the right child of 3. Its position
               preserves the binary search tree ordering: 3 < 6 < 8.
               The root indicator points to node 8; current points to node 6.
            :highlight: tree.node[inserted]

            root['8'] -left-> child['3']
            root -right-> other['12']
            child -right-> inserted['6']

   .. tb-tab:: Rendered

      .. tb-graph:: tree
         :style: tree
         :indicators: root=root current=inserted
         :caption: A tree with an inserted node
         :description: The root 8 has left child 3 and right child 12.
            Node 6, highlighted, is the right child of 3. Its position
            preserves the binary search tree ordering: 3 < 6 < 8.
            The root indicator points to node 8; current points to node 6.
         :highlight: tree.node[inserted]

         root['8'] -left-> child['3']
         root -right-> other['12']
         child -right-> inserted['6']

Example 3: Forward references and cycles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph::
            :label: A cycle and a disconnected node

            a['first'] -> b -> c['third'] -> a
            b['second']
            separate['disconnected']

   .. tb-tab:: Rendered

      .. tb-graph::
         :label: A cycle and a disconnected node
         :indicators: start=a current=b

         a['first'] -> b -> c['third'] -> a
         b['second']
         separate['disconnected']

Example 4: An undisplayed endpoint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph::
            :style: plain-list

            value['10'] -next-> unseen[''] {invisible}

   .. tb-tab:: Rendered

      .. tb-graph::
         :style: plain-list

         value['10'] -next-> unseen[''] {invisible}

Example 5: An empty graph and reference target
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph::
            :name: graph-reference-example
            :class: sample-graph

   .. tb-tab:: Rendered

      .. tb-graph::
         :name: graph-reference-example
         :class: sample-graph

Refer to the last example with :ref:`this graph <graph-reference-example>`.

Example 6: A horizontal doubly linked list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph::
            :style: list
            :indicators: current=b

            head['head'] -> a[8] -> b[13] -> c[21] -> tail['tail']
            tail -> c -> b -> a -> head

   .. tb-tab:: Rendered

      .. tb-graph::
         :style: list
         :indicators: current=b

         head['head'] -> a[8] -> b[13] -> c[21] -> tail['tail']
         tail -> c -> b -> a -> head

Example 7: Adjacent array values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph:: values
            :style: array
            :highlight: values.node[b]
            :indicators: v=b

            a[8]
            b[13]
            c[21]

   .. tb-tab:: Rendered

      .. tb-graph:: values
         :style: array
         :highlight: values.node[b]
         :indicators: v=b

         a[8]
         b[13]
         c[21]

Example 8: Array indices
~~~~~~~~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph::
            :style: array
            :show-indices:

            a['red']
            b['green']
            c['blue']
            spare1['']
            spare2['']

   .. tb-tab:: Rendered

      .. tb-graph::
         :style: array
         :show-indices:

         a['red']
         b['green']
         c['blue']
         spare1['']
         spare2['']

Example 9: A ring
~~~~~~~~~~~~~~~~~

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph::
            :style: ring
            :indicators: head=a tail=d

            a[8] -> b[13] -> c[21] -> d[34] -> e[''] -> f[''] -> a

   .. tb-tab:: Rendered

      .. tb-graph::
         :style: ring
         :indicators: head=a tail=d

         a[8] -> b[13] -> c[21] -> d[34] -> e[''] -> f[''] -> a

Example 10: Outline a comparison
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default ellipse groups the parent and child being compared. Their thicker
borders identify both values. Use ``:overlay-layer: background`` to place the
outline behind the graph, or ``:overlay-padding: 12`` to leave more space
around it.
See :ref:`tb-stack` Example 3 for outlines that follow swapped nodes.

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph:: heap
            :style: tree
            :highlight: heap.node[parent] heap.node[child]
            :overlay: parent child
            :description: Compare 13 with its left child 8 before swapping.

            parent[13] -left-> child[8]
            parent -right-> other[20]

   .. tb-tab:: Rendered

      .. tb-graph:: heap
         :style: tree
         :highlight: heap.node[parent] heap.node[child]
         :overlay: parent child
         :description: Compare 13 with its left child 8 before swapping.

         parent[13] -left-> child[8]
         parent -right-> other[20]

Example 11: Multiple overlay shapes and layers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An ellipse groups the parent and its left child. A rectangle separately
marks the right subtree behind the diagram. A circle marks its leaf in front.
The smaller padding applies only to that circle.

.. tb-group::

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-graph::
            :style: tree
            :overlay: parent child
                      other leaf :overlay-shape: rectangle :overlay-layer: background
                      leaf :overlay-shape: circle :overlay-padding: 4

            parent[13] -left-> child[8]
            parent -right-> other[20]
            other -right-> leaf[24]

   .. tb-tab:: Rendered

      .. tb-graph::
         :style: tree
         :overlay: parent child
                   other leaf :overlay-shape: rectangle :overlay-layer: background
                   leaf :overlay-shape: circle :overlay-padding: 4

         parent[13] -left-> child[8]
         parent -right-> other[20]
         other -right-> leaf[24]
