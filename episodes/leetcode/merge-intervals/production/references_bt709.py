#!/usr/bin/env python3
"""LC56 bibliography: canonical LeetCode layout with actual limited BT.709.

Only private function namespaces are adapted. Shared historical renderer files
and globals remain unchanged; title/credit wrapping and full media checks stay
in the canonical engines.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import FunctionType

sys.dont_write_bytecode = True
GENERATOR = Path(__file__).resolve()
ROOT = next(p for p in GENERATOR.parents if (p / 'AGENTS.md').is_file())
LIBRARY = ROOT / 'episodes/_shared/leetcode-video/references.py'
PALETTE = LIBRARY.with_name('style-v1.json')
spec = importlib.util.spec_from_file_location('lc56_canonical_leetcode_bibliography', LIBRARY)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
engine = original.engine
bibliography = original._scope['bibliography']
DEFAULT_FONT, DEFAULT_BOLD = original.DEFAULT_FONT, original.DEFAULT_BOLD
PRESENTATION, LAYOUT = original.PRESENTATION, original.LAYOUT
load_references, render_cards = original.load_references, original.render_cards
COLOR = {'pix_fmt': 'yuv420p', 'color_range': 'tv', 'color_space': 'bt709',
         'color_transfer': 'bt709', 'color_primaries': 'bt709'}
CARD_FILTER = ('scale=in_range=pc:out_range=tv:out_color_matrix=bt709,'
               'format=yuv420p,setparams=range=limited:color_primaries=bt709:'
               'color_trc=bt709:colorspace=bt709')


def run(command):
    command = [str(part) for part in command]
    if command[0] == 'ffmpeg' and '-loop' in command and 'libx264' in command:
        if '-vf' in command:
            raise ValueError('Unexpected inherited card filter; review the frozen renderer')
        # PNG is full-range RGB. scale converts its samples to limited BT.709;
        # setparams and codec flags declare the same conversion on the stream.
        command[-1:-1] = ['-vf', CARD_FILTER, '-pix_fmt', 'yuv420p',
                         '-color_range', 'tv', '-colorspace', 'bt709',
                         '-color_primaries', 'bt709', '-color_trc', 'bt709']
    return engine.run(command)


def adapted(function, **overrides):
    return FunctionType(function.__code__,
                        dict(vars(engine), __file__=str(GENERATOR), THEME=PALETTE,
                             run=run, load_references=load_references,
                             render_cards=render_cards, **overrides),
                        function.__name__, function.__defaults__, function.__closure__)


def dependency_files():
    return [GENERATOR, *original.dependency_files()]


def dependencies():
    return {**original.dependencies(),
            'leetcodePaletteAdapter': str(LIBRARY.relative_to(ROOT)),
            'leetcodePaletteAdapterSHA256': engine.sha(LIBRARY),
            'colorAdapter': str(GENERATOR.relative_to(ROOT)),
            'colorAdapterSHA256': engine.sha(GENERATOR)}


def check_color(path):
    video = engine.stream(engine.probe(path), 'video')
    if any(video.get(key) != value for key, value in COLOR.items()):
        raise ValueError(f'Expected actual limited BT.709 in {path}: {video}')


def verify_identity(receipt, args):
    doc = load_references(args.references)
    if (receipt.get('presentation') != PRESENTATION or receipt.get('layout') != LAYOUT
            or receipt.get('bibliography') != bibliography.bibliography(doc)
            or receipt.get('sourceTitles') != bibliography.original.source_titles(doc)
            or receipt.get('quotations') != bibliography.original.quotations(doc)
            or receipt.get('dependencies') != dependencies()
            or receipt.get('colorEncoding') != COLOR):
        raise ValueError('LC56 limited BT.709 bibliography identity differs')
    inputs = receipt.get('inputs', {})
    if (inputs.get('generatorSHA256') != engine.sha(GENERATOR)
            or inputs.get('themeSHA256') != engine.sha(PALETTE)
            or inputs.get('secondsPerPage') != 5
            or len(receipt['appendix']['pages']) != (len(doc['sources']) + 3) // 4):
        raise ValueError('LC56 bibliography generator/palette/pagination differs')
    check_color(args.body)
    check_color(args.output)


def append(args):
    if args.seconds != 5:
        raise ValueError('Bibliography requires five seconds per page')
    check_color(args.body)
    doc = load_references(args.references)
    path = args.artifacts / 'reference-appendix.json'
    if path.exists():
        previous = json.loads(path.read_text())
        if previous.get('presentation') == PRESENTATION and previous.get('dependencies') != dependencies():
            raise ValueError('Bibliography dependencies changed; preserve previous artifacts before rendering')
    result = adapted(engine.append)(args)
    receipt = json.loads(path.read_text())
    if result['status'] != 'already-current' or 'presentation' not in receipt:
        receipt.update(presentation=PRESENTATION, layout=LAYOUT,
                       bibliography=bibliography.bibliography(doc),
                       sourceTitles=bibliography.original.source_titles(doc),
                       quotations=bibliography.original.quotations(doc),
                       dependencies=dependencies(), colorEncoding=COLOR,
                       bodyProductionInputs='LC56 body and complete Python card were rendered from this new episode production freeze as limited BT.709; the bibliography uses the canonical LeetCode palette and title/credit layout. Full body frames, timestamps, AAC packets and decoded PCM are verified by the inherited append engine.')
        engine.dump(path, receipt)
    verify_identity(receipt, args)
    return {**result, **receipt}


def verify(args):
    if args.seconds != 5:
        raise ValueError('Bibliography requires five seconds per page')
    receipt = json.loads((args.artifacts / 'reference-appendix.json').read_text())
    verify_identity(receipt, args)
    recorded = json.loads((args.artifacts / 'reference-appendix-media-check.json').read_text())
    if recorded.get('passed') is not True:
        raise ValueError('Saved full appendix media verification is absent or failed')
    with tempfile.TemporaryDirectory(prefix='lc56-bt709-verify-') as temporary:
        def verify_media(*values):
            return engine.verify_media(*values[:-1], Path(temporary) / 'media-check.json')
        report = adapted(engine.verify, verify_media=verify_media)(args)
    if ({k: v for k, v in report.items() if k != 'checkedAtUTC'} !=
            {k: v for k, v in recorded.items() if k != 'checkedAtUTC'}):
        raise ValueError('Saved LC56 media verification differs from full verification')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('append', 'verify'))
    for name in ('body', 'references', 'output', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=5)
    parser.add_argument('--font', type=Path, default=DEFAULT_FONT)
    parser.add_argument('--bold-font', type=Path, default=DEFAULT_BOLD)
    args = parser.parse_args()
    print(json.dumps(append(args) if args.action == 'append' else verify(args), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
