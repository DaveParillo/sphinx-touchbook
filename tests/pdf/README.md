# Tagged PDF integration fixture

Run from the Touchbook repository with its source installed (or `PYTHONPATH=src`).
The tested toolchain is Sphinx 9.1, TeX Live 2026, LuaLaTeX, and pypdf.

```sh
python -m sphinx -E -W -b latex tests/pdf build/tagged-pdf
cd build/tagged-pdf
latexmk -lualatex -interaction=nonstopmode -halt-on-error fixture.tex
cd ../..
python tests/pdf/audit.py build/tagged-pdf/fixture.pdf --check-fixture
```

The audit checks metadata, standard structure roles, link objects, header cells,
image descriptions, decorative-image exclusion, code/caption association, and
page tab order. Presence checks do not prove complete reading order, artifact
coverage, or PDF/UA conformance. Check the TeX log for tagpdf warnings and render
the PDF for visual review. A conformance validator and screen-reader review are
still required for published books.

The fixture generates its PNG and long-table input from `conf.py`. They are
ignored build inputs, not repository assets. Unit tests copy the fixture into
a temporary directory before generating them.

`tests/test_pdf.py::test_palette_contrast` measures every resolved token color
against both supported backgrounds; it does not merely check selected colors.
The default profile's minimum ratio is about 4.58:1 on highlighted gray and
higher on white. Re-run this test after changing the palette or Pygments version.
