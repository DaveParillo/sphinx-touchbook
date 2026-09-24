"""Inspect a tagged PDF structure (requires pypdf)."""

import json
import argparse
from collections import Counter

from pypdf import PdfReader


def audit(path):
    reader = PdfReader(path)
    root = reader.trailer['/Root']
    counts = Counter()
    roles = Counter()
    alts = []
    structures = []

    def walk(obj, parent=None):
        if isinstance(obj, list):
            for child in obj:
                walk(child, parent)
            return
        obj = obj.get_object() if hasattr(obj, 'get_object') else obj
        if not isinstance(obj, dict):
            return
        tag = str(obj.get('/S', obj.get('/Type', '')))
        if tag:
            counts[tag] += 1
            role = tag
            rolemap = root['/StructTreeRoot'].get('/RoleMap', {})
            seen = set()
            while role in rolemap and role not in seen:
                seen.add(role)
                role = str(rolemap[role])
            roles[role] += 1
        if '/Alt' in obj:
            alts.append(str(obj['/Alt']))
        if '/S' in obj:
            structures.append((tag, parent))
        walk(obj.get('/K', []), tag or parent)

    walk(root.get('/StructTreeRoot', {}))
    return {
        'language': str(root.get('/Lang')),
        'display_title': bool(root.get('/ViewerPreferences', {}).get('/DisplayDocTitle')),
        'title': reader.metadata.title,
        'tags': dict(counts),
        'roles': dict(roles),
        'alt': alts,
        'tabs': [str(page.get('/Tabs')) for page in reader.pages],
        'artifact_pages': sum(b'/Artifact' in page.get_contents().get_data()
                              for page in reader.pages),
        'structures': structures,
    }


def check_fixture(report):
    """Assert the fixture's contract, not general PDF/UA conformance."""
    assert report['language'] == 'en-US'
    assert report['display_title'] and report['title']
    assert set(report['tabs']) == {'/S'}
    for role in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'P', 'L', 'LI',
                 'Table', 'TR', 'TH', 'TD', 'Figure', 'Caption', 'Link', 'OBJR']:
        assert report['roles'].get('/' + role, 0) > 0, role
    assert report['tags']['/Table'] == 2
    assert report['tags']['/TH'] == 4
    assert report['tags']['/Figure'] == 2  # Decorative image is not a figure.
    assert report['alt'] == ['A blue test square',
                             'A blue square supplied as a runtime file']
    assert report['structures'].count(('/Caption', '/Code')) == 3
    assert report['artifact_pages'] == len(report['tabs'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf')
    parser.add_argument('--check-fixture', action='store_true')
    parser.add_argument('--details', action='store_true')
    args = parser.parse_args()
    report = audit(args.pdf)
    if args.check_fixture:
        check_fixture(report)
    if not args.details:
        report.pop('structures')
    print(json.dumps(report, indent=2))
