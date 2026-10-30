#!/usr/bin/env python3
"""Use immutable bibliography layout/media engines with Kafka style-v1 and limited BT.709."""
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
ROOT = next(p for p in GENERATOR.parents if (p / 'AGENTS.md').is_file())
LIBRARY = ROOT / 'episodes-codex/_shared/kafka-video/references.py'
PALETTE = ROOT / 'episodes-codex/_shared/kafka-covers/style-v1.json'
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
_base_verify = _scope['verify']
COLOR = {'pix_fmt': 'yuv420p', 'color_range': 'tv', 'color_space': 'bt709',
         'color_transfer': 'bt709', 'color_primaries': 'bt709'}



def color_encode_command(command):
    command = [str(part) for part in command]
    if command[0] == 'ffmpeg' and '-loop' in command and 'libx264' in command:
        command[-1:-1] = ['-vf', 'scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
                         '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709']
    return command


def run(command):
    return _scope['engine'].run(color_encode_command(command))


def adapted(function, **overrides):
    return FunctionType(function.__code__, dict(vars(_scope['engine']), __file__=str(GENERATOR),
                        THEME=PALETTE, run=run, load_references=_scope['load_references'],
                        render_cards=_scope['render_cards'], **overrides),
                        function.__name__, function.__defaults__, function.__closure__)


def check_color(args):
    for path in (args.body, args.output):
        video = _scope['engine'].stream(_scope['engine'].probe(path), 'video')
        if any(video.get(key) != value for key, value in COLOR.items()):
            raise ValueError(f'Actual limited BT.709 color profile differs: {path}')
        data = json.loads(_scope['engine'].run([
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-read_intervals', '%+#1', '-show_frames', '-show_entries',
            'frame=pix_fmt,color_range,color_space,color_transfer,color_primaries',
            '-of', 'json', str(path)]))
        frames = data.get('frames', [])
        if len(frames) != 1 or any(frames[0].get(key) != value for key, value in COLOR.items()):
            raise ValueError(f'Actual first decoded frame differs from limited BT.709: {path}')


def palette():
    colors = json.loads(PALETTE.read_text())['palette']
    mapping = {'bg': 'background', 'ink': 'text', 'muted': 'muted',
               'row': 'surface', 'border': 'edge', 'success': 'success'}
    for key in mapping.values():
        if not isinstance(colors.get(key), str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', colors[key]):
            raise ValueError(f'Missing or invalid Kafka palette color: {key}')
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
        'colorEncoding': COLOR,
    }


def append(args):
    result = _base_append(args)
    receipt_path = args.artifacts / 'reference-appendix.json'
    receipt = json.loads(receipt_path.read_text())
    receipt['bodyProductionInputs'] = (
        'Body was rendered from the Kafka MQ03 source-depth-v2 production manifest with this revision’s new narration and timing; full-range BT.601 body pictures are converted once to limited BT.709 before mixing. Previously published episode inputs are preserved outside this revision directory.')
    receipt['colorEncoding'] = COLOR
    _scope['engine'].dump(receipt_path, receipt)
    check_color(args)
    return {**result, **receipt}


def verify(args):
    result = _base_verify(args)
    receipt = json.loads((args.artifacts / 'reference-appendix.json').read_text())
    if receipt.get('colorEncoding') != COLOR:
        raise ValueError('Frozen Kafka bibliography color profile differs')
    check_color(args)
    return result


_scope.update(palette=palette, dependency_files=dependency_files,
              dependencies=dependencies, append=append, verify=verify, adapted=adapted)
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
