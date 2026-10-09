from io import StringIO
from textwrap import indent
from pathlib import Path
import json
import subprocess
import sys

from bs4 import BeautifulSoup
from docutils import nodes
from docutils.frontend import get_default_settings
from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
import pytest

from sphinx_touchbook.directives.stack import (
    TbStackDirective, TbSceneDirective, TbPointerDirective,
)
from sphinx_touchbook.directives.array import TbArrayDirective
from sphinx_touchbook.directives.graph import TbGraphDirective
from sphinx_touchbook.nodes import TbStackNode, TbSceneNode, TbPointerNode, TbArrayNode, TbGraphNode


def parse_rst(source):
    settings = get_default_settings(Parser)
    settings.warning_stream = StringIO()
    document = new_document('stack.rst', settings)
    registered = {'tb-stack': TbStackDirective, 'tb-scene': TbSceneDirective,
                  'tb-pointer': TbPointerDirective, 'tb-array': TbArrayDirective, 'tb-graph': TbGraphDirective}
    previous = {name: directives._directives.get(name) for name in registered}
    for name, directive in registered.items():
        directives.register_directive(name, directive)
    try:
        Parser().parse(source, document)
    finally:
        for name, directive in previous.items():
            if directive is None:
                directives._directives.pop(name, None)
            else:
                directives._directives[name] = directive
    return document


def scene(content='', options=''):
    return '.. tb-scene::\n' + options + '\n' + '\n'.join('   ' + line for line in content.splitlines()) + '\n'


def stack(*scenes):
    return '.. tb-stack::\n   :name: example\n   :class: first second\n   :caption: Manual walkthrough\n\n' + '\n'.join(
        '\n'.join('   ' + line for line in item.splitlines()) for item in scenes) + '\n'


def pointer(at=None, key='current', extra=''):
    return ('.. tb-pointer:: ' + key + '\n'
            + (f'   :at: {at}\n' if at is not None else '') + extra)


ARRAY = '.. tb-array:: values\n\n   2 4 6\n'
KEYED_ARRAY = '.. tb-array:: values\n\n   a = 2\n   b = 4\n'
GRAPH = '.. tb-graph:: graph\n\n   a[2] -> b[4]\n   hidden[99] {invisible}\n'


def valid_document(source):
    document = parse_rst(source)
    assert not list(document.findall(nodes.system_message)), document.astext()
    return document


def test_complete_scenes_explicit_positions_forward_references_and_common_options():
    source = stack(scene(pointer('values.begin') + '\n' + ARRAY),
                       scene(ARRAY + '\n' + pointer('values.slot[2]')),
                       scene(pointer('values.begin') + '\n' + ARRAY))
    node = next(valid_document(source).findall(TbStackNode))
    assert node['ids'] == ['example'] and node['classes'] == ['first', 'second']
    assert [child['number'] for child in node.children] == [1, 2, 3]
    pointers = list(node.findall(TbPointerNode))
    assert [item['position']['index'] for item in pointers] == [0, 2, 0]
    assert [item['at'] for item in pointers] == ['values.begin', 'values.slot[2]', 'values.begin']


@pytest.mark.parametrize('at,index', [
    ('values.begin', 0), ('values.slot[1]', 1), ('values.end', 3), ('none', None),
])
def test_explicit_pointer_positions(at, index):
    node = next(valid_document(scene(ARRAY + '\n' + pointer(at))).findall(TbPointerNode))
    assert (node['position']['index'] if node['position'] else None) == index


def test_item_references_follow_reordered_keys_and_empty_arrays_adopt_mode():
    result = valid_document(stack(scene(KEYED_ARRAY + '\n' + pointer('values.item[b]')),
        scene('.. tb-array:: values\n\n   b = 4\n   a = 2\n\n' + pointer('values.item[b]')),
        scene('.. tb-array:: values\n\n' + pointer('values.end'))))
    assert [node['position']['index'] for node in result.findall(TbPointerNode)] == [1, 0, 0]
    assert [node['mode'] for node in result.findall(TbArrayNode)] == ['keyed', 'keyed', 'keyed']
    assert list(result.findall(TbPointerNode))[-1]['position']['end']


def test_unplaced_pointer_needs_no_target_and_does_not_inherit_objects():
    result = valid_document(stack(scene(pointer('none')), scene(ARRAY + '\n' + pointer('values.begin'))))
    pointers = list(result.findall(TbPointerNode))
    assert pointers[0]['position'] is None and pointers[1]['position']['index'] == 0
    assert len(list(result.children[0].children[0].findall(TbArrayNode))) == 0


@pytest.mark.parametrize('content,message', [
    (pointer('values.slot[3]') + '\n' + ARRAY, 'Slot index out of bounds'),
    (pointer('values.slot[-1]') + '\n' + ARRAY, 'Invalid position reference'),
    (pointer('values.item[a]') + '\n' + ARRAY, 'keyed array'),
    (pointer('values.item[missing]') + '\n' + KEYED_ARRAY, 'Unknown array item'),
    (pointer('values.node[a]') + '\n' + ARRAY, 'requires a graph'),
    (pointer('graph.slot[0]') + '\n' + GRAPH, 'requires an array'),
    (pointer('graph.node[missing]') + '\n' + GRAPH, 'Unknown graph node'),
    (pointer('missing.begin') + '\n' + ARRAY, 'Unknown scene object'),
    (pointer(), 'requires :at:'),
    (pointer('values') + '\n' + ARRAY, 'Invalid position reference'),
    ('.. tb-array::\n\n   1 2', 'require an object key'),
    (ARRAY + '\n' + ARRAY, 'Duplicate scene object key'),
    (ARRAY + '\n' + pointer('values.begin', key='values'), 'Duplicate scene object key'),
    ('.. container::\n\n   ' + ARRAY.replace('\n', '\n   '), 'immediate children'),
    (scene(), 'nested scenes'),
    (stack(scene()), 'nested scenes or stacks'),
])
def test_invalid_scene_references_and_structure(content, message):
    document = parse_rst(scene(content))
    assert list(document.findall(nodes.system_message))
    assert message in document.astext()


@pytest.mark.parametrize('source,message', [
    ('.. tb-stack::', 'one or more immediate tb-scene'),
    (stack(scene()) + '\n', None),
    ('.. tb-stack::\n\n   Not a scene.', 'no other content'),
    (pointer('none'), 'tb-scene parent'),
    (stack(scene(ARRAY), scene('.. tb-graph:: values\n\n   a[1]')), 'changes type'),
    (stack(scene(ARRAY), scene(KEYED_ARRAY)), 'mixes keyed and unkeyed'),
    (stack(scene(ARRAY), scene(pointer('values.begin'))), 'Unknown scene object'),
])
def test_stack_validation(source, message):
    document = parse_rst(source)
    if message is None:
        assert not list(document.findall(nodes.system_message))
    else:
        assert list(document.findall(nodes.system_message))
        assert message in document.astext()


def build_sphinx(tmp_path, builder, source):
    srcdir, outdir = tmp_path/'src', tmp_path/builder
    srcdir.mkdir()
    (srcdir/'conf.py').write_text('extensions=["sphinx_touchbook"]\nhtml_theme="alabaster"\n')
    (srcdir/'index.rst').write_text('Test\n====\n\n' + source)
    result = subprocess.run([sys.executable, '-m', 'sphinx', '-E', '-W', '-b', builder, str(srcdir), str(outdir)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return outdir


@pytest.mark.parametrize('orientation', ['horizontal', 'vertical'])
def test_html_places_pointer_roots_once_and_emits_complete_safe_config(tmp_path, orientation):
    source = stack(scene(ARRAY.replace('values\n', f'values\n   :orientation: {orientation}\n') + '\n'
                + pointer('values.slot[1]', extra='   :name: current-start\n   :class: mark\n')),
                scene(ARRAY + '\n' + pointer('values.end')),
                scene('.. code-block:: text\n\n   </script><script>unsafe & literal</script>'))
    out = build_sphinx(tmp_path, 'html', source)
    soup = BeautifulSoup((out/'index.html').read_text(), 'html.parser')
    root = soup.find('tb-stack', id='example')
    assert len(soup.find_all('tb-stack')) == 1
    scenes = root.find_all('tb-scene')
    assert len(scenes) == 3 and all(not item.has_attr('hidden') for item in scenes)
    assert len(root.find_all('tb-array')) == len(root.find_all('tb-pointer')) == 2
    pointer_element = root.find('tb-pointer', id='current-start')
    assert 'mark' in pointer_element['class'] and pointer_element.find_parent('tb-array') is not None
    assert pointer_element['data-at'] == 'values.slot[1]'
    assert 'index 1' in pointer_element.get_text()
    assert root.select('.tb-array__end')
    script = root.find('script', type='application/json', recursive=False)
    data = json.loads(script.string)
    assert data['version'] == 1
    assert data['scenes'][0]['objects'][1]['position']['index'] == 1
    assert data['scenes'][1]['objects'][1]['position']['end']
    assert len(soup.find_all('script', string=lambda value: value and 'unsafe & literal' in value)) == 0
    buttons = root.select('.tb-stack__controls button')
    assert [button['data-action'] for button in buttons] == ['first', 'previous', 'next', 'last']
    assert [button['aria-label'] for button in buttons] == ['First scene', 'Previous scene', 'Next scene', 'Last scene']
    assert all(button['title'] == button['aria-label'] for button in buttons)
    assert [button.svg['class'] for button in buttons] == [
        ['bi', 'bi-chevron-double-left'], ['bi', 'bi-chevron-left'],
        ['bi', 'bi-chevron-right'], ['bi', 'bi-chevron-double-right'],
    ]
    assert all(button.svg['aria-hidden'] == 'true' and button.svg['focusable'] == 'false'
               and button.svg.find('path') for button in buttons)
    controls = root.select_one('.tb-stack__controls')
    assert controls.has_attr('hidden')
    assert controls.find_next_sibling('div')['class'] == ['tb-stack__scenes']
    assert controls.select_one('.tb-stack__scene-caption').find_next_sibling('div')['class'] == ['tb-stack__navigation']
    assert all(button.parent['class'] == ['tb-stack__navigation'] for button in buttons)
    assert controls.select_one('.tb-stack__status')['role'] == 'status'
    assert all(not item.select_one('.tb-scene__caption').has_attr('hidden') for item in scenes)
    assert (out/'_static'/'tb-stack.js').exists()


def test_empty_array_and_unplaced_pointer_html_preserve_single_roots(tmp_path):
    source = stack(scene('.. tb-array:: values\n\n' + pointer('values.begin')),
                       scene(pointer('none')))
    out = build_sphinx(tmp_path, 'html', source)
    soup = BeautifulSoup((out/'index.html').read_text(), 'html.parser')
    assert len(soup.find_all('tb-pointer')) == 2
    assert 'values.end' in soup.find('tb-pointer').get_text()
    assert 'current has no target' in soup.find_all('tb-pointer')[1].get_text()


@pytest.mark.parametrize('builder', ['text', 'latex'])
def test_static_builders_keep_all_scenes_code_and_pointer_positions(tmp_path, builder):
    source = stack(scene('.. code-block:: python\n\n   message = "Hello" + "world"'),
                       scene(ARRAY + '\n' + pointer('values.slot[1]')),
                       scene(ARRAY + '\n' + pointer('values.end')))
    out = build_sphinx(tmp_path, builder, source)
    file = out/'index.txt' if builder == 'text' else next(out.glob('*.tex'))
    output = file.read_text()
    assert all(f'Scene {number}' in output for number in (1, 2, 3))
    assert 'message' in output and 'Hello' in output and 'world' in output
    assert 'current points to values at index 1' in output
    assert 'values.end' in output
    assert 'data-action' not in output and 'application/json' not in output


@pytest.mark.parametrize('style', ['graph', 'list', 'tree', 'array', 'ring'])
@pytest.mark.parametrize('builder', ['html', 'latex'])
def test_graph_pointer_uses_existing_layout_and_keeps_semantic_description(tmp_path, style, builder):
    source = scene(GRAPH.replace('graph\n', f'graph\n   :style: {style}\n') + '\n'
                   + pointer('graph.node[b]', extra='   :label: Here\n'))
    out = build_sphinx(tmp_path, builder, source)
    if builder == 'html':
        soup = BeautifulSoup((out/'index.html').read_text(), 'html.parser')
        assert len(soup.find_all('tb-scene')) == len(soup.find_all('tb-pointer')) == 1
        assert 'graph node b' in soup.find('tb-pointer').get_text()
        svg = next((out/'_images').glob('tb-graph*.svg')).read_text()
        assert '>Here<' in svg
        assert '99' not in soup.find('tb-scene').get_text()
    else:
        output = next(out.glob('*.tex')).read_text()
        assert 'Here points to graph node b' in output
        assert list(out.glob('tb-graph*.pdf'))


def test_tree_scene_accepts_multiple_pointers_and_local_indicators():
    document = valid_document(scene(GRAPH.replace('graph\n', 'graph\n   :style: tree\n   :indicators: head=a current=b\n') + '\n'
                                    + pointer('graph.node[a]', key='one') + '\n' + pointer('graph.node[b]', key='two')))
    assert len(list(document.findall(TbPointerNode))) == 2
    graph = next(document.findall(TbGraphNode))
    assert graph['indicators'] == [{'key': 'head', 'target': 'a'}, {'key': 'current', 'target': 'b'}]




def test_graph_positions_and_local_indicators_resolve_the_same_targets():
    for body in ("", "a[8]\nb[13]\nend[21]"):
        content = (".. tb-graph:: values\n   :style: array\n"
                   "   :indicators: first=.begin finish=values.end unplaced=none\n\n"
                   + indent(body, "   ") + "\n\n" + pointer('values.begin', key='first')
                   + "\n" + pointer('values.end', key='finish') + "\n" + pointer('none'))
        document = valid_document(scene(content))
        graph = next(document.findall(TbGraphNode))
        pointers = list(document.findall(TbPointerNode))
        from sphinx_touchbook.generators.stack import graph_pointer_indicators
        markers = graph_pointer_indicators(graph)
        assert markers[:2] == markers[2:]
        assert pointers[0]['position']['index'] == 0
        assert pointers[1]['position']['index'] == len(graph['nodes'])
        assert pointers[1]['position']['end']
        assert pointers[2]['position'] is None
        assert graph['indicators'][-1] == {'key': 'unplaced', 'target': None}
