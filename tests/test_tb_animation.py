from io import StringIO
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

from sphinx_touchbook.directives.animation import (
    TbAnimationDirective, TbSceneDirective, TbPointerDirective, normalize_scene,
)
from sphinx_touchbook.generators.animation import scene_model
from sphinx_touchbook.directives.array import TbArrayDirective
from sphinx_touchbook.directives.graph import TbGraphDirective
from sphinx_touchbook.nodes import TbAnimationNode, TbSceneNode, TbPointerNode, TbArrayNode


def parse_rst(source):
    settings = get_default_settings(Parser)
    settings.warning_stream = StringIO()
    document = new_document('animation.rst', settings)
    registered = {'tb-animation': TbAnimationDirective, 'tb-scene': TbSceneDirective,
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


def animation(*scenes):
    return '.. tb-animation::\n   :name: example\n   :class: first second\n   :caption: Manual walkthrough\n\n' + '\n'.join(
        '\n'.join('   ' + line for line in item.splitlines()) for item in scenes) + '\n'


def pointer(at=None, bounds=None, kind='pointer', key='current', extra=''):
    return ('.. tb-pointer:: ' + key + '\n   :kind: ' + kind + '\n'
            + (f'   :at: {at}\n' if at is not None else '')
            + (f'   :range: {bounds}\n' if bounds is not None else '') + extra)


ARRAY = '.. tb-array:: values\n\n   2 4 6\n'
KEYED_ARRAY = '.. tb-array:: values\n\n   a = 2\n   b = 4\n'
GRAPH = '.. tb-graph:: graph\n\n   a[2] -> b[4]\n   hidden[99] {invisible}\n'


def valid_document(source):
    document = parse_rst(source)
    assert not list(document.findall(nodes.system_message)), document.astext()
    return document


def test_complete_scenes_defaults_forward_references_and_common_options():
    source = animation(scene(pointer(bounds='values') + '\n' + ARRAY),
                       scene(ARRAY + '\n' + pointer('values.slot[2]')),
                       scene(pointer(bounds='values') + '\n' + ARRAY))
    node = next(valid_document(source).findall(TbAnimationNode))
    assert node['ids'] == ['example'] and node['classes'] == ['first', 'second']
    assert [child['number'] for child in node.children] == [1, 2, 3]
    pointers = list(node.findall(TbPointerNode))
    assert [item['position']['index'] for item in pointers] == [0, 2, 0]
    assert [item['at'] for item in pointers] == ['values.begin', 'values.slot[2]', 'values.begin']


@pytest.mark.parametrize('at,bounds,kind,index', [
    (None, 'values', 'iterator', 0),
    ('values.end', 'values', 'iterator', 3),
    (None, 'values.slot[1], values.end', 'iterator', 1),
    ('values.end', 'values.slot[1], values.slot[2]', 'pointer', 3),
    (None, 'values.end, values.end', 'iterator', 3),
    ('null', 'values', 'pointer', None),
])
def test_pointer_and_iterator_boundaries(at, bounds, kind, index):
    node = next(valid_document(scene(ARRAY + '\n' + pointer(at, bounds, kind))).findall(TbPointerNode))
    assert (node['position']['index'] if node['position'] else None) == index


def test_item_references_follow_reordered_keys_and_empty_arrays_adopt_mode():
    result = valid_document(animation(scene(KEYED_ARRAY + '\n' + pointer('values.item[b]')),
        scene('.. tb-array:: values\n\n   b = 4\n   a = 2\n\n' + pointer('values.item[b]')),
        scene('.. tb-array:: values\n\n' + pointer(bounds='values'))))
    assert [node['position']['index'] for node in result.findall(TbPointerNode)] == [1, 0, 0]
    assert [node['mode'] for node in result.findall(TbArrayNode)] == ['keyed', 'keyed', 'keyed']
    assert list(result.findall(TbPointerNode))[-1]['position']['end']


def test_null_pointer_needs_no_target_and_does_not_inherit_objects():
    result = valid_document(animation(scene(pointer(bounds='null')), scene(ARRAY + '\n' + pointer(bounds='values'))))
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
    (pointer(bounds='values.slot[2], values.slot[1]') + '\n' + ARRAY, 'ordered bounds'),
    (pointer(bounds='values.begin, other.end') + '\n' + ARRAY + '\n.. tb-array:: other\n\n   1', 'same array'),
    (pointer(bounds='values.item[a], values.end') + '\n' + KEYED_ARRAY, 'cannot be a bound'),
    (pointer(bounds='null', kind='iterator'), 'non-null'),
    (pointer('null', 'values', 'iterator') + '\n' + ARRAY, 'non-null'),
    (pointer('values.slot[0]', 'values.slot[1], values.end', 'iterator') + '\n' + ARRAY, 'outside its declared range'),
    (pointer('graph.node[a]', 'values', 'iterator') + '\n' + ARRAY + '\n' + GRAPH, 'outside its declared range'),
    (pointer(), 'requires :at: or :range:'),
    (pointer('values.begin', kind='iterator') + '\n' + ARRAY, 'require :range:'),
    ('.. tb-array::\n\n   1 2', 'require an object key'),
    (ARRAY + '\n' + ARRAY, 'Duplicate scene object key'),
    (ARRAY + '\n' + pointer('values.begin', key='values'), 'Duplicate scene object key'),
    ('.. container::\n\n   ' + ARRAY.replace('\n', '\n   '), 'immediate children'),
    (scene(), 'nested scenes'),
    (animation(scene()), 'nested scenes or animations'),
])
def test_invalid_scene_references_and_structure(content, message):
    document = parse_rst(scene(content))
    assert list(document.findall(nodes.system_message))
    assert message in document.astext()


@pytest.mark.parametrize('source,message', [
    ('.. tb-animation::', 'one or more immediate tb-scene'),
    (animation(scene()) + '\n', None),
    ('.. tb-animation::\n\n   Not a scene.', 'no other content'),
    (pointer('null'), 'tb-scene parent'),
    (animation(scene(ARRAY), scene('.. tb-graph:: values\n\n   a[1]')), 'changes type'),
    (animation(scene(ARRAY), scene(KEYED_ARRAY)), 'mixes keyed and unkeyed'),
    (animation(scene(ARRAY + '\n' + pointer(bounds='values')),
               scene(ARRAY + '\n' + pointer(bounds='values', kind='iterator'))), 'changes kind'),
    (animation(scene(ARRAY), scene(pointer('values.begin'))), 'Unknown scene object'),
])
def test_animation_validation(source, message):
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
    source = animation(scene(ARRAY.replace('values\n', f'values\n   :orientation: {orientation}\n') + '\n'
                + pointer('values.slot[1]', extra='   :name: current-start\n   :class: mark\n')),
                scene(ARRAY + '\n' + pointer('values.end')),
                scene('.. code-block:: text\n\n   </script><script>unsafe & literal</script>'))
    out = build_sphinx(tmp_path, 'html', source)
    soup = BeautifulSoup((out/'index.html').read_text(), 'html.parser')
    root = soup.find('tb-animation', id='example')
    assert len(soup.find_all('tb-animation')) == 1
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
    buttons = root.select('.tb-animation__controls button')
    assert [button.get_text() for button in buttons] == ['<<', '<', '>', '>>']
    assert [button['aria-label'] for button in buttons] == ['First scene', 'Previous scene', 'Next scene', 'Last scene']
    assert root.select_one('.tb-animation__controls').has_attr('hidden')
    assert (out/'_static'/'tb-animation.js').exists()


def test_empty_array_and_null_pointer_html_preserve_single_roots(tmp_path):
    source = animation(scene('.. tb-array:: values\n\n' + pointer(bounds='values')),
                       scene(pointer(bounds='null')))
    out = build_sphinx(tmp_path, 'html', source)
    soup = BeautifulSoup((out/'index.html').read_text(), 'html.parser')
    assert len(soup.find_all('tb-pointer')) == 2
    assert 'values.end' in soup.find('tb-pointer').get_text()
    assert 'current is null' in soup.find_all('tb-pointer')[1].get_text()


@pytest.mark.parametrize('builder', ['text', 'latex'])
def test_static_builders_keep_all_scenes_code_and_pointer_positions(tmp_path, builder):
    source = animation(scene('.. code-block:: python\n\n   message = "Hello" + "world"'),
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


def test_tree_scene_retains_single_annotation_limit():
    document = parse_rst(scene(GRAPH.replace('graph\n', 'graph\n   :style: tree\n') + '\n'
                              + pointer('graph.node[a]', key='one') + '\n' + pointer('graph.node[b]', key='two')))
    assert 'at most one pointer or indicator' in document.astext()


@pytest.mark.parametrize('content,target', [
    (ARRAY, 'values'),
    (GRAPH, 'graph'),
    (pointer('null', key='other'), 'other'),
    ('', 'current'),
])
def test_bare_keys_target_whole_objects_with_forward_references(content, target):
    document = valid_document(scene(pointer(target) + '\n' + content))
    current = next(document.findall(TbPointerNode))
    assert current['position']['type'] == 'object'
    assert current['position']['object'] == target
    assert 'index' not in current['position'] and 'value' not in current['position']
    target_node = next(item for item in current.parent.children if item.get('key') == target)
    assert current['position']['target_id'] == target_node['ids'][0]


def test_registry_accepts_other_keyed_object_types_and_preserves_normalized_identity():
    document = valid_document(scene(pointer('null')))
    scene_node = next(document.findall(TbSceneNode))
    current = next(scene_node.findall(TbPointerNode))
    current['at_source'] = 'note'
    target = nodes.container(key='note', label='An explanation')
    target += nodes.paragraph(text='Native explanatory content.')
    scene_node += target
    normalize_scene(scene_node, document)
    assert current['position']['target_id'] == target['ids'][0]
    assert current['position']['label'] == 'An explanation'
    model = scene_model(scene_node)
    assert model['objects'][1]['type'] == 'object'
    assert model['objects'][1]['key'] == 'note'


def test_pointer_object_cycles_do_not_dereference_destinations():
    document = valid_document(scene(pointer('second', key='first') + '\n' + pointer('first', key='second')))
    assert [node['position']['object'] for node in document.findall(TbPointerNode)] == ['second', 'first']


@pytest.mark.parametrize('content,message', [
    (pointer('missing'), 'Unknown scene object'),
    (ARRAY + '\n' + pointer('values', 'values', 'iterator'), 'outside its declared range'),
    (ARRAY + '\n' + pointer(bounds='values, values.end'), 'Array bounds require'),
    (ARRAY.replace('values\n', 'values\n   :name: named-values\n') + '\n' + pointer('named-values'), 'Unknown scene object'),
])
def test_object_target_validation_preserves_scopes_and_iterator_positions(content, message):
    document = parse_rst(scene(content))
    assert list(document.findall(nodes.system_message))
    assert message in document.astext()


@pytest.mark.parametrize('builder', ['html', 'text', 'latex'])
def test_whole_object_targets_have_links_or_prose_in_each_builder(tmp_path, builder):
    source = animation(scene(pointer('graph', key='current') + '\n'
                       + pointer('current', key='address') + '\n'
                       + pointer('values', key='array_address') + '\n' + ARRAY + '\n' + GRAPH))
    out = build_sphinx(tmp_path, builder, source)
    if builder == 'html':
        soup = BeautifulSoup((out/'index.html').read_text(), 'html.parser')
        root = soup.find('tb-scene')
        assert len(root.find_all('tb-pointer')) == 3
        for element in root.find_all('tb-pointer'):
            assert element.find_parent('tb-array') is None
            target = soup.find(id=element.find('a')['href'][1:])
            assert target['data-key'] == element['data-at']
        model = json.loads(soup.find('tb-animation').find('script', type='application/json').string)
        assert [item['position']['type'] for item in model['scenes'][0]['objects'][:3]] == ['object'] * 3
        assert not root.select('.tb-array__pointers')
        assert len(root.select('tb-graph img')) == 1
    else:
        file = out/'index.txt' if builder == 'text' else next(out.glob('*.tex'))
        output = file.read_text()
        output = ' '.join(output.split())
        assert 'current points to scene object graph.' in output
        assert 'address points to scene object current.' in output
        assert 'points to scene object values.' in output


def test_whole_tree_targets_do_not_consume_node_annotation_slots(tmp_path):
    source = scene(GRAPH.replace('graph\n', 'graph\n   :style: tree\n') + '\n'
                   + pointer('graph', key='whole') + '\n' + pointer('graph.node[b]', key='node'))
    out = build_sphinx(tmp_path, 'html', source)
    soup = BeautifulSoup((out/'index.html').read_text(), 'html.parser')
    assert len(soup.find_all('tb-pointer')) == 2
    svg = next((out/'_images').glob('tb-graph*.svg')).read_text()
    assert '>node<' in svg and '>whole<' not in svg
