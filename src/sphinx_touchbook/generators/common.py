"""Shared builder helpers."""

from __future__ import annotations

from html import escape

from docutils import nodes


def html_class_attr(node: nodes.Element) -> str:
    classes = node.get("classes", [])
    if not classes:
        return ""
    value = " ".join(escape(name, quote=True) for name in classes)
    return f' class="{value}"'


def html_additional_targets(node: nodes.Element) -> str:
    ids = node.get("ids", [])
    if len(ids) < 2:
        return ""
    return "".join(f'<span id="{escape(node_id, quote=True)}"></span>\n' for node_id in ids[1:])


def latex_targets(translator, node: nodes.Element) -> None:
    if node.get("ids"):
        translator.body.append(translator.hypertarget_to(node, anchor=True))


def tagged_listing(translator, source: str, language: str, caption: str,
                   options: dict | None = None, location=None) -> None:
    """Keep a highlighted listing and its caption in one PDF structure."""
    options = options or {}
    translator.body.append('\n\\par\\tagstructbegin{tag=Code}\n')
    if caption:
        translator.body.append(
            '\\tagstructbegin{tag=Caption}\\tagpdfparaOff'
            '\\tagmcbegin{tag=Caption}\\noindent\\textbf{' +
            translator.encode(caption) +
            '}\\par\\tagmcend\\tagpdfparaOn\\tagstructend\n')
    # latex-lab tags the native Verbatim environment and each code line.
    # An extra marked-content wrapper interferes with those paragraph hooks.
    translator.body.append(translator.highlighter.highlight_block(
        source, language, location=location,
        opts=translator.config.highlight_options.get(language, {}),
        linenos=options.get('linenos', False),
        force=options.get('force', False),
        **options.get('highlight_args', {})))
    translator.body.append('\\tagstructend\n')
