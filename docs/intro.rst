Introduction
============

``sphinx-touchbook`` is a `Sphinx <https://www.sphinx-doc.org/>`__
extension project for authors who want interactive textbook pages without
giving up the strengths of ordinary Sphinx documents.
The goal is to let authors create content in
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext>`__,
build static HTML for the web, and still produce useful
non-interactive output for text and PDF-oriented builders.

The project starts from a simple premise: interactive textbook content should
be compiled, not hand-written as fragile HTML fragments. Authors describe
educational intent. The Sphinx extension turns that intent into docutils nodes.
Python generators render those nodes for each builder.
In HTML, JavaScript components add interactive behaviors to the generated
custom elements.

Goals
-----

The project is designed around a few practical goals:

- Keep author syntax concise and teachable.
- Preserve Sphinx features such as nested markup, code highlighting, cross
  references, and multiple builders.
- Generate accessible HTML that works before JavaScript runs.
- Make every component testable without requiring a complete textbook project.
- Keep interactive behavior reusable outside Sphinx when possible.
- Treat non-HTML, and non-JavaScript HTML output as first-class features, not
  afterthoughts.

Architecture
------------

Interactive textbook components use three layers:

1. Python Sphinx extension layer
   Roles, directives, domains, transforms, and docutils nodes parse author
   content and store semantic data. This layer does not implement browser
   behavior.

2. Python generator layer
   Builder-specific renderers turn semantic nodes into HTML, text,
   LaTeX-oriented output, or other builder output. In HTML, each directive
   emits exactly one custom element.

3. JavaScript component layer
   Custom elements implement browser behavior by hydrating the rendered HTML,
   its attributes, and its fallback content.

Some components may use optional stateless services for work that cannot
reasonably happen in the browser, such as compiling code or evaluating
symbolic math.

Every component should start as useful static content. JavaScript may improve
the experience, but it should not be the only way to reach essential content.

For example, ``tb-reveal`` emits a native ``details`` and ``summary`` fallback
inside the custom element. Without JavaScript, readers can still open the
disclosure.

The same approach supports non-HTML builders.
A ``tb-code`` block can be treated as the standard Sphinx
``code-block`` it's based upon in non-HTML output.
A ``tb-reveal`` does not have the HTML disclosure control in text or PDF
formats, but the content is rendered.
The reader loses the interaction, but not the information.

Testing approach
----------------

The test strategy follows the architecture:

- Sphinx directive tests check parsing, options, diagnostics, and semantic node fields.
- Python generator tests check custom element output, fallback content, assets,
  and non-HTML builder behavior.
- JavaScript component tests check browser behavior, accessibility state,
  keyboard behavior, and service failure handling.
- Documentation builds act as end-to-end tests for author-facing examples.

Routine tests should use small temporary Sphinx projects. They should not
require a real textbook repository.

