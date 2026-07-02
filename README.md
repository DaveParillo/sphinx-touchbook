# sphinx-touchbook
[![Tests](https://img.shields.io/github/actions/workflow/status/daveparillo/sphinx-touchbook/publish-authorguide.yml?branch=main&label=tests)](https://github.com/daveparillo/sphinx-touchbook/actions/workflows/publish-authorguide.yml)
[![Author Guide](https://img.shields.io/github/actions/workflow/status/daveparillo/sphinx-touchbook/publish-authorguide.yml?branch=main&label=docs)](https://github.com/daveparillo/sphinx-touchbook/actions/workflows/publish-authorguide.yml)
[![License](https://img.shields.io/github/license/daveparillo/sphinx-touchbook)](LICENSE)

`sphinx-touchbook` is a Sphinx extension project for authors who want
interactive textbook pages without giving up ordinary Sphinx documents.
Authors write semantic reStructuredText directives, Sphinx parses them into
docutils nodes, Python generators render builder-specific output, and
JavaScript components progressively enhance the generated HTML.

This project is inspired by
[Runestone Interactive](https://github.com/RunestoneInteractive),
which pioneered interactive textbook components for computer science education.
`sphinx-touchbook` is a Sphinx-oriented port of that general idea: it keeps
authoring and builds inside Sphinx while Runestone's main project has moved
away from Sphinx-based authoring and toward PreTeXt-authored books.

The focus of this project is 'Sphinx-native' interactive books and nothing else.
Runestone is a much more sophisticated environment with instructor resources,
student tracking, and LMS integration.
If you want those features then you should consider Runestone as a resource.

## Setup

To build documents Python is required.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python package with test, documentation build and publish to pypi
dependencies:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -e '.[test,docs,publish]'
```

To test documents Node.js with `npm` is required.

Install JavaScript test dependencies:

```bash
npm ci
```

## Build Documents

Build the author guide as HTML:

```bash
python3 -m sphinx -b html docs build/authorguide --fail-on-warning
```

The generated site starts at:

```text
build/authorguide/index.html
```

To build LaTeX or PDF requires either a local LaTeX installation
compatible with Sphinx, or a docker image:

Build LaTeX source locally:

```bash
python3 -m sphinx -b latex docs build/latex --fail-on-warning
```

Build the author guide PDF with the Sphinx LaTeX container:

```bash
docker run --rm \
  -v "$PWD:/docs" \
  -w /docs \
  sphinxdoc/sphinx-latexpdf:latest \
  sh -c 'python3 -m pip install ".[docs]" && python -m sphinx -M latexpdf docs build/latexpdf --fail-on-warning'
```


See the author guide in `docs/` for directive syntax, options, examples,
accessibility notes, and fallback behavior.

## Run Tests

Run the Python directive and generator tests:

```bash
python3 -m pytest tests/test_*.py
```

Run isolated JavaScript component tests:

```bash
npm run test:web-components
```

## Build install package

```bash
  python3 -m build
  python3 -m twine check dist/*
```

