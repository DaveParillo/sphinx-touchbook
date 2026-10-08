.. _tb-stack:

tb-stack
========

The ``tb-stack`` directive groups :ref:`scenes <tb-scene>` in an ordered
collection. Readers advance using basic navigation buttons for the first,
previous, next, and last scene.

Declare every object and value present in each scene, including unchanged
content. An omitted object is absent from that scene. Navigation can move
backward or jump directly to the first or last scene without replaying steps.

Synopsis
--------

The general format of the ``tb-stack`` directive is:

.. code-block:: rst

   .. tb-stack::
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

The stack body contains one or more immediate ``tb-scene`` directives and
no other content. Scenes may be empty. Scenes and stacks cannot be nested
inside a scene, including through other containers.

Options
-------

**caption**
   ``String``. Optional.
   Plain-text caption displayed above the stack.

**class**
   ``String`` or ``List``. Optional.
   Space-separated CSS classes for this stack.
   See :ref:`common` for details.

**name**
   ``String``. Optional.
   Sphinx reference target for this stack.
   See :ref:`common` for details.

Accessibility behavior
----------------------

Navigation uses native buttons with Bootstrap chevron icons, accessible labels,
and hover tooltips for first, previous, next, and last scene. Buttons are
disabled at the corresponding endpoints. Keyboard users can
Tab to the controls and activate them with Enter or Space. The scene count and
caption are announced after navigation; the status is not a focus target.
The current scene's caption appears once, above the navigation buttons.
If navigation disables the focused button, focus moves to an available previous
or next button.

Use a scene's ``:name:`` to link directly to it with a Sphinx reference.
Document links to named scenes or their content reveal the destination scene,
including when it belongs to another stack.
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example unfolds a join expression into concatenation and its final value,
using ordinary code blocks for each authored expression.

.. tb-group::
   :name: stack-join-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-stack::

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

      .. tb-stack::

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The iterator marks the current element. Each scene repeats the complete array
and pointer declaration. The final scene uses ``values.end`` to show that the
traversal has finished; the end position does not designate an element.

.. tb-group::
   :name: stack-increment-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-stack::
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

      .. tb-stack::
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



Example 2a: Increment graph array element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Very similar to the previous example, but using a :ref:`tb-graph`

.. tb-group::
   :name: stack-increment-tabs-graph-array

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-stack::
            :name: array-graph-increment
            :caption: Add one to every element

            .. tb-scene::
               :caption: Start at the first element.

               .. tb-graph:: data
                  :style: array
                  :show-indices:
                  :highlight: data.node[a]

                  a['2']
                  b['4']
                  c['6']
                  end[' '] {invisible}

               .. tb-pointer:: current
                  :at: data.node[a]

            .. tb-scene::
               :caption: Increment 2 to 3 and advance to the second element.

               .. tb-graph:: data
                  :style: array
                  :show-indices:
                  :highlight: data.node[b]

                  a['3']
                  b['4']
                  c['6']
                  end[' '] {invisible}

               .. tb-pointer:: current
                  :at: data.node[b]

            .. tb-scene::
               :caption: Increment 4 to 5 and advance to the third element.

               .. tb-graph:: data
                  :style: array
                  :show-indices:
                  :highlight: data.node[b]

                  a['3']
                  b['5']
                  c['6']
                  end[' '] {invisible}

               .. tb-pointer:: current
                  :at: data.node[c]

            .. tb-scene::
               :name: array-increment-done
               :caption: Increment 6 to 7. The iterator is now at the end.

               .. tb-graph:: data
                  :style: array
                  :show-indices:

                  a['3']
                  b['5']
                  c['7']
                  end[' '] {invisible}

               .. tb-pointer:: current
                  :at: data.end

   .. tb-tab:: Rendered

      .. tb-stack::
         :name: array-graph-increment
         :caption: Add one to every element

         .. tb-scene::
            :caption: Start at the first element.

            .. tb-graph:: data
               :style: array
               :show-indices:
               :highlight: data.node[a]

               a['2']
               b['4']
               c['6']
               end[' '] {invisible}

            .. tb-pointer:: current
               :at: data.node[a]

         .. tb-scene::
            :caption: Increment 2 to 3 and advance to the second element.

            .. tb-graph:: data
               :style: array
               :show-indices:
               :highlight: data.node[b]

               a['3']
               b['4']
               c['6']
               end[' '] {invisible}

            .. tb-pointer:: current
               :at: data.node[b]

         .. tb-scene::
            :caption: Increment 4 to 5 and advance to the third element.

            .. tb-graph:: data
               :style: array
               :show-indices:
               :highlight: data.node[b]

               a['3']
               b['5']
               c['6']
               end[' '] {invisible}

            .. tb-pointer:: current
               :at: data.node[c]

         .. tb-scene::
            :name: array-graph-increment-done
            :caption: Increment 6 to 7. The iterator is now at the end.

            .. tb-graph:: data
               :style: array
               :show-indices:

               a['3']
               b['5']
               c['7']
               end[' '] {invisible}

            .. tb-pointer:: current
               :at: data.node[end]


Example 3: Min heap insertion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ellipses identify the parent and child involved in each comparison or swap.
The outline follows the node keys in each scene, including after they change
positions. Highlighted nodes show the values exchanged in that step.

.. tb-group::
   :name: heap-insertion-tabs

   .. tb-tab:: Source

      .. code-block:: rst

         .. tb-stack::
            :name: percolate-up
            :caption: Insert a new value into a min heap and restore the heap
                      property.

            .. tb-scene::
               :caption: New element pushed onto heap

               If the new value is less than its parent, it must be moved into a valid
               position.

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
                  :highlight: tree.node[b] tree.node[e]
                  :overlay: b e

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
                  :highlight: tree.node[b] tree.node[d]
                  :overlay: b d

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

   .. tb-tab:: Rendered

      .. tb-stack::
         :name: percolate-up
         :caption: Insert a new value into a min heap and restore the heap
                   property.

         .. tb-scene::
            :caption: New element pushed onto heap

            If the new value is less than its parent, it must be moved into a valid
            position.

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
               :highlight: tree.node[b] tree.node[e]
               :overlay: b e

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
               :highlight: tree.node[b] tree.node[d]
               :overlay: b d

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

Example 4: Pre-order traversal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example prints the tree in pre-order: the current value, then the left
subtree, then the right subtree. Each scene summarizes a meaningful step;
highlighted lines show its operations, and the pointer identifies the current
call's ``node`` parameter. Scenes show every printed value and the returns to
callers that begin a right subtree.
Program output appears between the code and tree and retains everything printed
so far. The final ``print(root);`` line in the listing represents the caller.

Every leaf has two null child pointers, drawn as arrows to ``{invisible}``
endpoints. The two child calls for the first leaf, k, demonstrate the base case:
``node = nullptr`` makes the condition true, and ``return;`` ends the call
without printing. Later scenes summarize these repeated base-case calls while
preserving the order of visits and accumulated output.

This example uses a named tree style with arrowheads. Add it to your existing
``tb_graph_styles`` configuration in ``conf.py``:

.. code-block:: python

   tb_graph_styles["print-tree"] = {"base": "tree", "arrows": "vee"}

.. tb-stack::
   :name: pre-order-anim
   :caption: Print every tree value using pre-order traversal

   .. tb-scene::
      :caption: Call print(root)

      Start at the root. Before advancing, predict which value prints first.
      Each call prints its own value before visiting either subtree.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 11

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         *(empty)*

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[root]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[root]

   .. tb-scene::
      :caption: Visit a: print the root first

      The root is not null, so print a. Then call print(node->left) to enter b;
      the entire left subtree must finish before the right subtree begins.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 3,6-7

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[root]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[root]

   .. tb-scene::
      :caption: Visit b: print before descending left

      The call for b prints b, then enters its left child h. The call for a
      waits for this whole subtree to finish.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-7

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[b]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[b]

   .. tb-scene::
      :caption: Visit h: continue down the left subtree

      Print h, then enter its left child k. Each descent starts a new call with
      its own node parameter.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-7

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[h]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[h]

   .. tb-scene::
      :caption: Visit k: a leaf still makes two child calls

      Print k. Both child pointers are null; the next two scenes show how the
      base case ends those calls without printing another value.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-7

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[k]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[k]

   .. tb-scene::
      :caption: Check k.left and return from print(nullptr)

      The left-child call receives nullptr. The condition is true, so return
      immediately without printing or making further recursive calls. Execution
      resumes in the call for k.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 3-4

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k

      .. tb-graph:: tree
         :style: print-tree
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[k_left_null]
         :label: node = nullptr

   .. tb-scene::
      :caption: Check k.right and return from print(nullptr)

      The call for k now calls print(node->right). Its argument is also
      nullptr, so the same base case returns without printing. Both child calls
      are complete, so print(k) finishes.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 3-4

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k

      .. tb-graph:: tree
         :style: print-tree
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[k_right_null]
         :label: node = nullptr

   .. tb-scene::
      :caption: Resume h and enter its right subtree

      After print(k) returns, node is h again. Its left subtree is complete, so
      call print(node->right) to enter i. Predict the next printed value before
      advancing.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[h]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[h]

   .. tb-scene::
      :caption: Visit i: finish the right subtree of h

      Print i. As with k, both null-child calls return without printing; their
      repeated base-case steps are combined here. The call for i finishes,
      followed by the call for h.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[i]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[i]

   .. tb-scene::
      :caption: Resume b and enter its right subtree

      The entire subtree rooted at h is complete. Execution resumes with node
      equal to b, and print(node->right) enters d.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[b]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[b]

   .. tb-scene::
      :caption: Visit d: print before descending left

      Print d, then enter its left child j. The right child e must wait until
      the call for j finishes.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-7

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[d]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[d]

   .. tb-scene::
      :caption: Visit j: finish the left subtree of d

      Print j. Its two null-child calls return without printing, and print(j)
      finishes. These are the same base-case steps already shown for k.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d j

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[j]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[j]

   .. tb-scene::
      :caption: Resume d and enter its right subtree

      After print(j) returns, node is d again. Call print(node->right) to enter
      e.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d j

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[d]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[d]

   .. tb-scene::
      :caption: Visit e: complete the subtree rooted at b

      Print e. Both null-child calls return without printing. The completed
      calls then return from e to d, from d to b, and from b to a.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d j e

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[e]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[e]

   .. tb-scene::
      :caption: Resume a and enter its right subtree

      The whole left subtree of a is complete. Execution resumes with node
      equal to a, and print(node->right) enters c. No ancestor is printed again
      when its call resumes.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d j e

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[root]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[root]

   .. tb-scene::
      :caption: Visit c: print before descending left

      Print c, then enter its left child f. The right subtree follows only
      after f finishes.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-7

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d j e c

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[c]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[c]

   .. tb-scene::
      :caption: Visit f: finish the left subtree of c

      Print f. Both null-child calls return without printing, and print(f)
      finishes.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d j e c f

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[f]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[f]

   .. tb-scene::
      :caption: Resume c and enter its right subtree

      After print(f) returns, node is c again. Call print(node->right) to enter
      g.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d j e c f

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[c]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[c]

   .. tb-scene::
      :caption: Visit g: print the last value

      Print g. Its two null-child calls return without printing. All tree
      values have now appeared in pre-order.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 6-8

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d j e c f g

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[g]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[g]

   .. tb-scene::
      :caption: Return to the caller: traversal is complete

      The calls return from g to c and then to a. The call for a finishes and
      returns to the caller of print(root). The output contains each value
      once: the root, its complete left subtree, then its complete right
      subtree.

      .. code-block:: cpp
         :linenos:
         :emphasize-lines: 9

         template <class T>
         void print(tree<T>* node) {
           if (node == nullptr) {
             return;
           }
           std::cout << node->value << ' ';
           print(node->left);
           print(node->right);
         }

         print(root);

      .. container:: print-output

         **Program output**

         .. code-block:: text

            a b h k i d j e c f g

      .. tb-graph:: tree
         :style: print-tree
         :highlight: tree.node[root]
         :description: The root a has left subtree b(h(k, i), d(j, e))
            and right subtree c(f, g). Each leaf has left and right null
            pointers, shown by arrows to invisible endpoints.

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
         k -left-> k_left_null[''] {invisible}
         k -right-> k_right_null[''] {invisible}
         i -left-> i_left_null[''] {invisible}
         i -right-> i_right_null[''] {invisible}
         j -left-> j_left_null[''] {invisible}
         j -right-> j_right_null[''] {invisible}
         e -left-> e_left_null[''] {invisible}
         e -right-> e_right_null[''] {invisible}
         f -left-> f_left_null[''] {invisible}
         f -right-> f_right_null[''] {invisible}
         g -left-> g_left_null[''] {invisible}
         g -right-> g_right_null[''] {invisible}

      .. tb-pointer:: node
         :at: tree.node[root]
