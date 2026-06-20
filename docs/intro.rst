Introduction
============

``sphinx-touchbook`` is a Sphinx extension project for authors who want interactive textbook pages without giving up the strengths of ordinary Sphinx documents. The goal is to let authors write semantic directives in reStructuredText, build static HTML for the web, and still produce useful non-interactive output for text and PDF-oriented builders.

The project starts from a simple premise: interactive textbook content should be compiled, not hand-written as fragile HTML fragments. Authors describe educational intent. The Sphinx extension turns that intent into semantic docutils nodes. Python generators render those nodes for each builder. In HTML, JavaScript Web Components progressively enhance the generated custom elements.

Goals
-----

The project is designed around a few practical goals:

- Keep author syntax concise and teachable.
- Preserve Sphinx features such as nested markup, code highlighting, cross references, and multiple builders.
- Generate accessible HTML that works before JavaScript runs.
- Make every component testable without requiring a complete textbook project.
- Keep interactive behavior reusable outside Sphinx when possible.
- Treat PDF, text, and no-JS HTML output as first-class fallbacks, not afterthoughts.

Architecture
------------

Interactive textbook components use three layers:

1. Python Sphinx extension layer
   Roles, directives, domains, transforms, and docutils nodes parse author content and store semantic data. This layer does not implement browser behavior.

2. Python generator layer
   Builder-specific renderers turn semantic nodes into HTML, text, LaTeX-oriented output, or other builder output. In HTML, each directive emits exactly one custom element.

3. JavaScript Web Component layer
   Custom elements implement browser behavior by hydrating the rendered HTML, its attributes, and its fallback content.

Some components may use optional stateless services for work that cannot reasonably happen in the browser, such as compiling code or evaluating symbolic math. Those services are not part of the required static publishing path.

Design philosophy
-----------------

Each directive should describe an educational concept rather than a JavaScript library call. A data-structure animation directive should describe the operation sequence. A future renderer might use SVG, Canvas, JSAV, D3, or another library. The textbook source should not need to change simply because a rendering library changes.

The same rule applies to executable examples. The directive should describe editable, runnable source code. Whether the code runs through a local WebAssembly compiler, a hosted execution service, or a future backend is an implementation detail.

Custom elements are the HTML contract. A directive such as ``tb-reveal`` maps to one ``<tb-reveal>`` element. Controls, fallback content, and configuration belong inside that element. This keeps generated HTML understandable, testable, and reusable.

Progressive enhancement
-----------------------

Every component should start as useful static content. JavaScript may improve the experience, but it should not be the only way to reach essential content.

For example, ``tb-reveal`` emits a native ``details`` and ``summary`` fallback inside the custom element. Without JavaScript, readers can still open the disclosure. With JavaScript, the Web Component replaces that fallback with the enhanced inline or modal behavior.

This approach also supports non-HTML builders. A reveal block can become labeled static content in text output and a readable block in PDF-oriented output. The reader loses the interaction, but not the information.

Testing approach
----------------

The test strategy follows the same layer boundaries:

- Sphinx directive tests check parsing, options, diagnostics, and semantic node fields.
- Python generator tests check custom element output, fallback content, assets, and non-HTML builder behavior.
- Web Component tests check browser behavior, accessibility state, keyboard behavior, and service failure handling.
- Documentation builds act as end-to-end tests for author-facing examples.

Routine tests should use small temporary Sphinx projects. They should not require a real textbook repository.

Author guide structure
----------------------

Each component page documents the author syntax, options, accessibility behavior, fallback behavior, and examples. The examples are real Sphinx source that builds as part of this guide, so the guide is both a manual for authors and a regression test for the project.
