.. _tb-animation:

tb-animation
============

The ``tb-animation`` directive presents a sequence of complete instructional
scenes. Readers choose when to advance using four buttons:
``<<`` (first), ``<`` (previous), ``>`` (next), and ``>>`` (last).
HTML shows one scene at a time. Navigation replaces the current scene with the
chosen scene; there is no automatic playback or expression evaluation.

Declare every object and value present in each scene, including unchanged
content. An omitted object is absent from that scene. Navigation can move
backward or jump directly to the first or last scene without replaying steps.

Synopsis
--------

The general format of the ``tb-animation`` directive is:

.. code-block:: rst

   .. tb-animation::
      :optional parameter: value

      .. tb-scene::
         :optional parameter: value

         + --- Complete scene content ---
         |
         | prose, code, keyed arrays or graphs, and pointers
         |
         + ------------------------------

      .. tb-scene::

         + --- Next complete scene ---
         |
         | declare all content for this scene
         |
         + ---------------------------

The animation body contains one or more immediate ``tb-scene`` directives and
no other content. Scenes may be empty. Scenes and animations cannot be nested
inside a scene, including through other containers.

Options
-------

**caption**
   ``String``. Optional.
   Plain-text caption displayed above the animation.

**class**
   ``String`` or ``List``. Optional.
   Space-separated CSS classes for this animation.
   See :ref:`common` for details.

**name**
   ``String``. Optional.
   Sphinx reference target for this animation.
   See :ref:`common` for details.

Scenes and identity
-------------------

Use :ref:`tb-scene` for each complete step. Its caption describes that step and
appears beside the scene count in the navigation controls.

Arrays, graphs, and pointers require object keys inside a scene. Reusing a key
across scenes identifies the same object, independently of values and displayed
positions. Object types and pointer kinds must remain consistent. Arrays use
one consistent keyed or unkeyed mode across the animation; empty arrays adopt
the mode of their nonempty declarations. Equal values do not establish identity.

Use :ref:`tb-pointer` to mark an array position or graph node. References resolve
only against objects declared in the same scene, including forward references.
Ordinary ``code-block`` displays code or expressions; :ref:`tb-code` supplies
runnable code when needed. No new code-listing directive is required.

Accessibility behavior
----------------------

Navigation uses native buttons with labels for first, previous, next, and last
scene. Buttons are disabled at the corresponding endpoints. Keyboard users can
Tab to the controls and activate them with Enter or Space. The scene count and
caption are announced after navigation; the status is not a focus target.
If navigation disables the focused button, focus moves to an available previous
or next button.

Document links to named content in an inactive scene reveal that scene.
Each named occurrence retains its own Sphinx reference target. Object keys
are separate from document names; use different ``:name:`` values when naming
occurrences of the same object in different scenes.

Fallback behavior
-----------------

HTML without JavaScript shows every scene in order and hides the navigation
controls. Text and PDF show every scene, with captions, code, arrays, pointer
positions, and graph descriptions or diagrams. Each scene is independently
renderable. Reduced-motion preferences require no special settings because
navigation changes scenes immediately.

Examples
--------

Example 1: String joining and concatenation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example unfolds a join expression into concatenation and its final value,
using ordinary code blocks for each authored expression.

.. tb-group::
   :name: animation-join-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-animation::

            .. tb-scene::

               Join the words with a space between them.

               .. code-block:: python

                  words = ["Hello", "world"]
                  message = " ".join(words)

            .. tb-scene::

               Substitute the list of words.

               .. code-block:: python

                  message = " ".join(["Hello", "world"])

            .. tb-scene::

               Insert the separator between the two strings.

               .. code-block:: python

                  message = "Hello" + " " + "world"

            .. tb-scene::

               The concatenated strings form the final message.

               .. code-block:: python

                  message = "Hello world"

   .. tb-tab:: Rendered

      .. tb-animation::

         .. tb-scene::

            Join the words with a space between them.

            .. code-block:: python

               words = ["Hello", "world"]
               message = " ".join(words)

         .. tb-scene::

            Substitute the list of words.

            .. code-block:: python

               message = " ".join(["Hello", "world"])

         .. tb-scene::

            Insert the separator between the two strings.

            .. code-block:: python

               message = "Hello" + " " + "world"

         .. tb-scene::

            The concatenated strings form the final message.

            .. code-block:: python

               message = "Hello world"

Example 2: Increment each array element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The iterator marks the current element. Each scene repeats the complete array
and pointer declaration. The final scene uses ``values.end`` to show that the
traversal has finished; the end position does not designate an element.

.. tb-group::
   :name: animation-increment-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-animation::
            :name: array-increment
            :caption: Add one to every element

            .. tb-scene::
               :caption: Start at the first element.

               .. tb-array:: values
                  :highlight: values.slot[0]

                  2 4 6

               .. tb-pointer:: current
                  :kind: iterator
                  :range: values

            .. tb-scene::
               :caption: Increment 2 to 3 and advance to the second element.

               .. tb-array:: values
                  :highlight: values.slot[1]

                  3 4 6

               .. tb-pointer:: current
                  :kind: iterator
                  :range: values
                  :at: values.slot[1]

            .. tb-scene::
               :caption: Increment 4 to 5 and advance to the third element.

               .. tb-array:: values
                  :highlight: values.slot[2]

                  3 5 6

               .. tb-pointer:: current
                  :kind: iterator
                  :range: values
                  :at: values.slot[2]

            .. tb-scene::
               :name: array-increment-done
               :caption: Increment 6 to 7. The iterator is now at the end.

               .. tb-array:: values

                  3 5 7

               .. tb-pointer:: current
                  :kind: iterator
                  :range: values
                  :at: values.end

   .. tb-tab:: Rendered

      .. tb-animation::
         :name: array-increment
         :caption: Add one to every element

         .. tb-scene::
            :caption: Start at the first element.

            .. tb-array:: values
               :highlight: values.slot[0]

               2 4 6

            .. tb-pointer:: current
               :kind: iterator
               :range: values

         .. tb-scene::
            :caption: Increment 2 to 3 and advance to the second element.

            .. tb-array:: values
               :highlight: values.slot[1]

               3 4 6

            .. tb-pointer:: current
               :kind: iterator
               :range: values
               :at: values.slot[1]

         .. tb-scene::
            :caption: Increment 4 to 5 and advance to the third element.

            .. tb-array:: values
               :highlight: values.slot[2]

               3 5 6

            .. tb-pointer:: current
               :kind: iterator
               :range: values
               :at: values.slot[2]

         .. tb-scene::
            :name: array-increment-done
            :caption: Increment 6 to 7. The iterator is now at the end.

            .. tb-array:: values

               3 5 7

            .. tb-pointer:: current
               :kind: iterator
               :range: values
               :at: values.end



Tree
----

.. tb-animation::
   :name: percolate-up
   :caption: Insert a new value into a binary search tree and put it in its
             proper location

   .. tb-scene::
      :caption: New element pushed onto heap

      If the new value is less than its parent, it must be moved into a valid position.

      .. tb-graph:: tree
         :style: tree
         :indicators: push=b
         :highlight: tree.node[b]

         root['a'] -left-> d['d']
         root -right-> c['c']
         d -left-> h['h']
         d -right-> e['e']
         h -left-> k['k']
         h -right-> i['i']
         e -left-> j['j']
         e -right-> b['b']
         c -left-> f['f']
         c -right-> g['g']


   .. tb-scene::
      :caption: Make the first move

      First we swap the value at position 'b' with the value at position 'e'.

      .. tb-graph:: tree
         :style: tree
         :highlight: tree.node[b]

         root['a'] -left-> d['d']
         root -right-> c['c']
         d -left-> h['h']
         d -right-> b['b']
         h -left-> k['k']
         h -right-> i['i']
         b -left-> j['j']
         b -right-> e['e']
         c -left-> f['f']
         c -right-> g['g']


   .. tb-scene::
      :caption: Make the next move

      The value at position 'd' is still larger than 'b', so we are not done.

      .. tb-graph:: tree
         :style: tree
         :highlight: tree.node[b]

         root['a'] -left-> b['b']
         root -right-> c['c']
         b -left-> h['h']
         b -right-> d['d']
         h -left-> k['k']
         h -right-> i['i']
         d -left-> j['j']
         d -right-> e['e']
         c -left-> f['f']
         c -right-> g['g']


   .. tb-scene::
      :caption: Percolate up is done

      Now that 'a' is less than 'b' and all of the children of 'b' are greater
      than 'b', the heap property has been restored and we are done.

      .. tb-graph:: tree
         :style: tree

         root['a'] -left-> b['b']
         root -right-> c['c']
         b -left-> h['h']
         b -right-> d['d']
         h -left-> k['k']
         h -right-> i['i']
         d -left-> j['j']
         d -right-> e['e']
         c -left-> f['f']
         c -right-> g['g']
