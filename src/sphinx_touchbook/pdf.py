"""Opt-in LuaLaTeX tagging and PDF-specific presentation defaults."""

from __future__ import annotations

import re

from docutils import nodes
from pygments.styles.default import DefaultStyle
from sphinx.errors import ConfigError
from sphinx.highlighting import PygmentsBridge
from sphinx.util import logging
from sphinx.writers.latex import LaTeXTranslator

logger = logging.getLogger(__name__)


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(color):
        channels = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
                  for c in channels]
        return sum(c * w for c, w in zip(linear, (.2126, .7152, .0722)))
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + .05) / (dark + .05)


def _darken(match):
    color = match.group(1)
    channels = [int(color[i:i + 2], 16) for i in (0, 2, 4)]
    while contrast_ratio(color, 'e6e6e6') < 4.5:
        channels = [int(c * .9) for c in channels]
        color = ''.join(f'{c:02x}' for c in channels)
    return '#' + color


class PDFStyle(DefaultStyle):
    """Darkened Pygments default palette, measured against both PDF backgrounds."""

    background_color = '#ffffff'
    highlight_color = '#e6e6e6'
    styles = {token: re.sub(r'#([0-9a-fA-F]{6})', _darken, value)
              for token, value in DefaultStyle.styles.items()}


EARLY = r"""
\makeatletter
\disable@package@load{sphinxlatexstyleheadings}{%
  \newcommand\py@HeaderFamily{\spx@opt@HeaderFamily}}
\disable@package@load{sphinxpackagefootnote}{%
  \def\savenotes{}\def\endsavenotes{}%
  \let\spewnotes\endsavenotes}
\makeatother
"""

PREAMBLE = r"""
\hypersetup{pdfdisplaydoctitle=true,colorlinks=true,linkcolor=black,
            urlcolor=black,citecolor=black}
\tagpdfsetup{page/tabsorder=structure,page/exclude-header-footer=true,float/here}
\sphinxsetup{VerbatimColor={rgb}{1,1,1},
             VerbatimHighlightColor={rgb}{0.9,0.9,0.9}}
% Framed Sphinx boxes copy typeset material and its marked-content identifiers.
% Native quotations keep the content in reading order without copied boxes.
\RenewDocumentEnvironment{sphinxtopic}{}{\begin{quote}}{\end{quote}}
\RenewDocumentEnvironment{sphinxsidebar}{}{\begin{quote}}{\end{quote}}
\RenewDocumentEnvironment{sphinxadmonition}{mm}
  {\begin{quote}\noindent\textbf{#2}\par}{\end{quote}}
\renewcommand\sphinxstyletopictitle[1]{\par\noindent\textbf{#1}\par}
\renewcommand\sphinxstylesidebartitle[1]{\par\noindent\textbf{#1}\par}
\ExplSyntaxOn
\NewDocumentCommand\TBArtifactBegin{}{\tag_mc_artifact_group_begin:n{layout}}
\NewDocumentCommand\TBArtifactEnd{}{\tag_mc_artifact_group_end:}
\NewDocumentCommand\TBTagSuspend{m}{\tag_suspend:n{#1}}
\NewDocumentCommand\TBTagResume{m}{\tag_resume:n{#1}}
\ExplSyntaxOff
\newcommand\TBIncludeGraphics[2][]{%
  \begingroup
  \TBTagSuspend{tb-image-measure}%
  \sbox0{\includegraphics[draft,#1]{#2}}%
  \TBTagResume{tb-image-measure}%
  \ifdim\wd0>\linewidth
    \includegraphics[#1,width=\linewidth,keepaspectratio]{#2}%
  \else
    \includegraphics[#1]{#2}%
  \fi
  \endgroup}
"""


class TaggedLaTeXTranslator(LaTeXTranslator):
    """Retain Sphinx rendering while supplying tagging information it drops."""

    def __init__(self, *args):
        super().__init__(*args)
        self._tb_notes = {}
        self.highlighter = PygmentsBridge('latex', self.config.tb_pdf_pygments_style,
                                         latex_engine='lualatex')

    def astext(self):
        content = super().astext()
        language = self.config.tb_pdf_language
        return (rf'\DocumentMetadata{{lang={language},tagging=on}}' + '\n' + content)

    def visit_captioned_literal_block(self, node):
        from .generators.common import tagged_listing

        literal = next(node.findall(nodes.literal_block))
        caption = next(node.findall(nodes.caption))
        self.body.append(self.hypertarget_to(node, anchor=True))
        tagged_listing(self, literal.astext(), literal.get('language', 'text'),
                       caption.astext(), literal.attributes, literal)
        raise nodes.SkipNode

    def visit_literal_block(self, node):
        from .generators.common import tagged_listing

        self.body.append(self.hypertarget_to(node, anchor=True))
        if node.rawsource != node.astext():
            self.in_parsed_literal += 1
            self.body.append('\n\\par\\tagstructbegin{tag=Code}\\begin{alltt}\n')
            return
        tagged_listing(self, node.astext(), node.get('language', 'text'), '',
                       node.attributes, node)
        raise nodes.SkipNode

    def depart_literal_block(self, node):
        self.body.append('\n\\end{alltt}\\tagstructend\n')
        self.in_parsed_literal -= 1

    def visit_term(self, node):
        # Sphinx's full-width parbox label bypasses latex-lab's Lbl/LBody hooks.
        super().visit_term(node)
        self.body[-1] = r'\item[{'
        # Destinations belong in the item body, not the measured/copied label.
        self.context[-1] = '}]' + self.context[-1][:-1]

    visit_field_name = visit_term

    def render(self, template_name, variables):
        if template_name == 'longtable.tex.jinja':
            table = variables['table']
            caption = ''.join(table.caption)
            content = '\n\\sphinxthistablewithbooktabsstyle\n'
            if caption:
                # A native longtable caption becomes a header cell in latex-lab.
                # Keep it outside the alignment, with its own Caption structure.
                content += (r'\captionof{table}{' + caption + '}' +
                            variables['labels'] + '\n\\addtocounter{table}{-1}\n')
            content += r'\begin{longtable}' + table.get_colspec() + '\n'
            if not caption:
                content += r'\noalign{' + variables['labels'] + '}\n'
            head = r'\toprule' + '\n' + ''.join(table.header)
            if table.header:
                head += r'\midrule' + '\n'
            content += head + '\\endfirsthead\n' + head + '\\endhead\n'
            content += '\\bottomrule\n\\endfoot\n\\endlastfoot\n'
            return content + ''.join(table.body) + '\\bottomrule\n\\end{longtable}\n'
        if template_name == 'tabular.tex.jinja':
            table = variables['table']
            caption = ''.join(table.caption)
            content = '\n\\sphinxthistablewithbooktabsstyle\n\\begin{table}[H]\n'
            if caption:
                content += r'\caption{' + caption + '}\n'
            content += variables['labels'] + '\n'
            content += r'\begin{tabular}' + table.get_colspec() + '\n'
            content += r'\toprule' + '\n' + ''.join(table.header)
            if table.header:
                content += r'\midrule' + '\n'
            content += ''.join(table.body) + '\\bottomrule\n\\end{tabular}\n\\end{table}\n'
            return content
        return super().render(template_name, variables)

    def dispatch_visit(self, node):
        if isinstance(node, nodes.Element) and 'tb-pdf-artifact' in node.get('classes', []):
            self.body.append('\n\\TBArtifactBegin\n')
            try:
                return super().dispatch_visit(node)
            except nodes.SkipNode:
                self.body.append('\n\\TBArtifactEnd\n')
                raise
        return super().dispatch_visit(node)

    def dispatch_departure(self, node):
        super().dispatch_departure(node)
        if isinstance(node, nodes.Element) and 'tb-pdf-artifact' in node.get('classes', []):
            self.body.append('\n\\TBArtifactEnd\n')
        self.body.extend(self._tb_notes.pop(id(node), []))

    def visit_footnote(self, node):
        self.in_footnote += 1
        number = node[0].astext()
        ancestor = node.parent
        table = None
        while ancestor is not None:
            if isinstance(ancestor, nodes.table):
                table = ancestor
            ancestor = ancestor.parent
        if table is not None:
            self.body.append(r'\footnotemark[' + number + ']')
            self.pushbody([])
            node['_tb_note_table'] = id(table)
            self.body.append(r'\footnotetext[' + number + ']{')
        else:
            self.body.append(r'\footnote[' + number + ']{')

    def depart_footnote(self, node):
        self.body.append('}')
        if '_tb_note_table' in node:
            self._tb_notes.setdefault(node['_tb_note_table'], []).extend(self.popbody())
        self.in_footnote -= 1

    def visit_footnotemark(self, node):
        self.body.append(r'\footnotemark[')

    def visit_footnotetext(self, node):
        self.in_footnote += 1
        self.body.append(r'\footnotetext[' + node[0].astext() + ']{')

    def depart_footnotetext(self, node):
        self.body.append('}\\ignorespaces ')
        self.in_footnote -= 1

    def visit_image(self, node):
        start = len(self.body)
        super().visit_image(node)
        decorative = 'tb-pdf-artifact' in node.get('classes', [])
        alt = node.get('alt', '')
        if not alt and not decorative:
            logger.warning('Tagged PDF image needs :alt: or :class: tb-pdf-artifact',
                           location=node, type='touchbook', subtype='pdf_alt')
        option = 'artifact' if decorative else 'alt={' + self.encode(alt) + '}'
        for i in range(start, len(self.body)):
            self.body[i] = re.sub(
                r'\\sphinxincludegraphics(\[)?',
                lambda m: r'\TBIncludeGraphics[' + option + (',' if m[1] else ']'),
                self.body[i],
            )

    def visit_table(self, node):
        super().visit_table(node)
        self.table.has_problematic = True  # Use tabular, avoiding trial-pass tags.
        self.table.styles = [s for s in self.table.styles if s != 'colorrows']
        self.table.styles.append('nocolorrows')
        headers = sum(len(head.children) for head in node.findall(nodes.thead))
        self.table.tb_header_rows = headers
        self.body.append('\n\\begingroup\n' +
                         rf'\tagpdfsetup{{table/header-rows={{{",".join(str(i) for i in range(1, headers + 1))}}}}}' + '\n')

    def depart_table(self, node):
        super().depart_table(node)
        self.body.append('\n\\endgroup\n')


def configure_pdf(app, config):
    if not config.tb_pdf_tagging:
        return
    if not re.fullmatch(r'[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*', config.tb_pdf_language):
        raise ConfigError('tb_pdf_language must be a BCP 47 language tag, e.g. en-US')
    config.latex_engine = 'lualatex'
    config.latex_table_style = ['booktabs']
    elements = dict(config.latex_elements)
    elements['fncychap'] = ''
    elements['passoptionstopackages'] = elements.get('passoptionstopackages', '') + EARLY
    elements['maketitle'] = (r'\begingroup\tagpdfsetup{table/tagging=div}' +
                             elements.get('maketitle', r'\sphinxmaketitle') + r'\endgroup')
    elements['preamble'] = elements.get('preamble', '') + PREAMBLE
    config.latex_elements = elements
    app.set_translator('latex', TaggedLaTeXTranslator, override=True)


def setup_pdf(app):
    app.add_config_value('tb_pdf_tagging', False, 'env', types=[bool])
    app.add_config_value('tb_pdf_language', 'en-US', 'env', types=[str])
    app.add_config_value('tb_pdf_pygments_style', 'sphinx_touchbook.pdf.PDFStyle', 'env', types=[str])
    app.connect('config-inited', configure_pdf)
    app.connect('builder-inited', _pdf_builder)


def _pdf_builder(app):
    if app.builder.name == 'latex' and app.config.tb_pdf_tagging:
        app.config.pygments_style = app.config.tb_pdf_pygments_style
