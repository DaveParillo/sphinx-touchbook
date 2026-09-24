"""Regression checks for the opt-in PDF profile (no TeX installation needed)."""

import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from sphinx.errors import ConfigError

from sphinx_touchbook.pdf import PDFStyle, configure_pdf, contrast_ratio


def test_palette_contrast():
    assert contrast_ratio('000000', 'ffffff') == 21
    for token, style in PDFStyle:
        if style['color']:
            for background in ('ffffff', 'e6e6e6'):
                assert contrast_ratio(style['color'], background) >= 4.5, token


def test_disabled_profile_does_not_change_configuration():
    config = SimpleNamespace(tb_pdf_tagging=False)
    configure_pdf(None, config)
    assert vars(config) == {'tb_pdf_tagging': False}


def test_language_rejects_tex_injection():
    config = SimpleNamespace(tb_pdf_tagging=True, tb_pdf_language='en-US}\\input{x}')
    with pytest.raises(ConfigError, match='language tag'):
        configure_pdf(None, config)


@pytest.mark.parametrize('builder', ['html', 'text', 'latex'])
def test_tagged_fixture_generators(tmp_path, builder):
    source = tmp_path / 'source'
    shutil.copytree(Path(__file__).parent / 'pdf', source)
    output = tmp_path / builder
    result = subprocess.run(
        [sys.executable, '-m', 'sphinx', '-E', '-W', '-b', builder,
         str(source), str(output)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    if builder == 'latex':
        text = (output / 'fixture.tex').read_text()
        assert text.startswith(r'\DocumentMetadata{lang=en-US,tagging=on}')
        assert r'pdfdisplaydoctitle=true' in text
        assert r'page/tabsorder=structure' in text
        assert r'\tagstructbegin{tag=Code}' in text
        assert r'\tagstructbegin{tag=Caption}' in text
        assert r'\textbf{Run It}' in text
        assert r'\subsubsection*{Run It}' not in text
        assert 'alt={A blue square supplied as a runtime file}' in text
        assert r'\TBIncludeGraphics[artifact,' in text
        assert r'\footnote[1]{' in text
    elif builder == 'html':
        text = (output / 'index.html').read_text()
        assert 'alt="A blue square supplied as a runtime file"' in text
        assert text.count('<tb-file ') == 2
    else:
        text = ' '.join((output / 'index.txt').read_text().split())
        assert 'A blue square supplied as a runtime file' in text
