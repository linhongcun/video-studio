#!/usr/bin/env python3
"""Independent limited-range BT.709 appendix adapter v2; old generators are unchanged."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
from types import FunctionType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIBRARY = HERE.parent / 'redis-video/references.py'
spec = importlib.util.spec_from_file_location('redis_original_bibliography', LIBRARY)
original = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original)
engine = original.engine
PALETTE = HERE.parent / 'redis-video/style-v1.json'
DEFAULT_FONT, DEFAULT_BOLD = original.DEFAULT_FONT, original.DEFAULT_BOLD
COLOR = {'pix_fmt': 'yuv420p', 'color_range': 'tv', 'color_space': 'bt709',
         'color_transfer': 'bt709', 'color_primaries': 'bt709'}


def run(command):
    command = [str(part) for part in command]
    if command[0] == 'ffmpeg' and '-loop' in command and 'libx264' in command:
        command[-1:-1] = ['-vf', 'scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
                         '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709']
    return engine.run(command)


def adapted(function, **overrides):
    return FunctionType(function.__code__, dict(vars(engine), __file__=str(Path(__file__).resolve()),
                        THEME=PALETTE, run=run, load_references=original.load_references,
                        render_cards=original.render_cards, **overrides),
                        function.__name__, function.__defaults__, function.__closure__)


def dependencies():
    return {**original.dependencies(), 'redisPaletteAdapter': str(LIBRARY.relative_to(ROOT)),
            'redisPaletteAdapterSHA256': engine.sha(LIBRARY),
            'colorAdapter': str(Path(__file__).resolve().relative_to(ROOT)),
            'colorAdapterSHA256': engine.sha(Path(__file__).resolve())}


def check_identity(receipt, args):
    doc = original.load_references(args.references)
    if receipt.get('presentation') != original.PRESENTATION or receipt.get('layout') != original.LAYOUT \
            or receipt.get('bibliography') != original._scope['bibliography'].bibliography(doc) \
            or receipt.get('sourceTitles') != original._scope['bibliography'].original.source_titles(doc) \
            or receipt.get('quotations') != original._scope['bibliography'].original.quotations(doc) \
            or receipt.get('dependencies') != dependencies() or receipt.get('colorEncoding') != COLOR:
        raise ValueError('Independent BT.709 bibliography identity differs')
    for media in (args.body, args.output):
        video = engine.stream(engine.probe(media), 'video')
        if any(video.get(key) != value for key, value in COLOR.items()):
            raise ValueError(f'Expected limited BT.709 in {media}: {video}')


def append(args):
    if args.seconds != 5:
        raise ValueError('Bibliography requires five seconds per page')
    doc = original.load_references(args.references)
    result = adapted(engine.append)(args)
    path = args.artifacts / 'reference-appendix.json'
    receipt = json.loads(path.read_text())
    bibliography = original._scope['bibliography']
    receipt.update(presentation=original.PRESENTATION, layout=original.LAYOUT,
                   bibliography=bibliography.bibliography(doc),
                   sourceTitles=bibliography.original.source_titles(doc),
                   quotations=bibliography.original.quotations(doc), dependencies=dependencies(),
                   colorEncoding=COLOR,
                   bodyProductionInputs='Body is the independently frozen limited-range BT.709 color normalization of the preserved redis-style render. Complete AAC, original timings and historical freezes retain their identities.')
    engine.dump(path, receipt)
    check_identity(receipt, args)
    return {**result, **receipt}


def verify(args):
    receipt = json.loads((args.artifacts / 'reference-appendix.json').read_text())
    check_identity(receipt, args)
    recorded = json.loads((args.artifacts / 'reference-appendix-media-check.json').read_text())
    with tempfile.TemporaryDirectory(prefix='redis-bt709-verify-') as temporary:
        def verify_media(*values):
            return engine.verify_media(*values[:-1], Path(temporary) / 'check.json')
        report = adapted(engine.verify, verify_media=verify_media)(args)
    if {k: v for k, v in report.items() if k != 'checkedAtUTC'} != \
            {k: v for k, v in recorded.items() if k != 'checkedAtUTC'}:
        raise ValueError('Full media verification differs from saved report')
    return report
