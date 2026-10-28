#!/usr/bin/env python3
"""Use the immutable bibliography engines with this MySQL series palette."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import FunctionType

sys.dont_write_bytecode = True
GENERATOR = Path(__file__).resolve()
ROOT = GENERATOR.parents[3]
LIBRARY = GENERATOR.parent.parent / 'puzzles-video/references.py'
PALETTE = GENERATOR.parent.parent / 'mysql-covers/catalog.json'
_spec = importlib.util.spec_from_file_location('frozen_palette_bibliography_core', LIBRARY)
_library = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_library)
_scope = dict(vars(_library), __file__=str(GENERATOR), GENERATOR=GENERATOR,
              ROOT=ROOT, PALETTE=PALETTE)
for _name, _value in vars(_library).items():
    if isinstance(_value, FunctionType) and _value.__module__ == _library.__name__:
        _scope[_name] = FunctionType(_value.__code__, _scope, _value.__name__,
                                     _value.__defaults__, _value.__closure__)
_base_append = _scope['append']


def palette():
    colors = json.loads(PALETTE.read_text())['palette']
    mapping = {'bg': 'background', 'ink': 'text', 'muted': 'muted',
               'row': 'surface', 'border': 'edge', 'success': 'mint'}
    for key in mapping.values():
        if not isinstance(colors.get(key), str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', colors[key]):
            raise ValueError(f'Missing or invalid MySQL palette color: {key}')
    return {key: colors[value] for key, value in mapping.items()}


def dependency_files():
    bibliography = _scope['bibliography']
    return [GENERATOR, LIBRARY, PALETTE, _scope['BIBLIOGRAPHY'],
            bibliography.ORIGINAL_RENDERER, bibliography.OLD_ENGINE]


def dependencies():
    engine, bibliography = _scope['engine'], _scope['bibliography']
    return {
        **bibliography.dependencies(),
        'bibliographyRenderer': str(_scope['BIBLIOGRAPHY'].relative_to(ROOT)),
        'bibliographyRendererSHA256': engine.sha(_scope['BIBLIOGRAPHY']),
        'palette': str(PALETTE.relative_to(ROOT)),
        'paletteSHA256': engine.sha(PALETTE),
        'paletteAdapterLibrary': str(LIBRARY.relative_to(ROOT)),
        'paletteAdapterLibrarySHA256': engine.sha(LIBRARY),
    }


def append(args):
    result = _base_append(args)
    receipt_path = args.artifacts / 'reference-appendix.json'
    receipt = json.loads(receipt_path.read_text())
    receipt['bodyProductionInputs'] = (
        'Body was rendered from the independent mysql-style revision manifest; '
        'complete baseline narration, original timing and historical freezes '
        'retain their original identities.')
    _scope['engine'].dump(receipt_path, receipt)
    return {**result, **receipt}


_scope.update(palette=palette, dependency_files=dependency_files,
              dependencies=dependencies, append=append)
for _name, _value in _scope.items():
    if not _name.startswith('_') and (isinstance(_value, FunctionType) or _name in
            ('engine', 'DEFAULT_FONT', 'DEFAULT_BOLD', 'PRESENTATION', 'LAYOUT')):
        globals()[_name] = _value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('append', 'verify'))
    for name in ('body', 'references', 'output', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=5)
    parser.add_argument('--font', type=Path, default=DEFAULT_FONT)
    parser.add_argument('--bold-font', type=Path, default=DEFAULT_BOLD)
    args = parser.parse_args()
    print(json.dumps(append(args) if args.action == 'append' else verify(args),
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
