#!/usr/bin/env python3
"""Append a plain original-title and author/organization bibliography.

The two older renderers remain frozen. Their validators/wrapping and the
original media append/verification code are reused through private dependency
injection. Only titles and explicit authors (otherwise organizations) are drawn.
Research quotations stay bound to the receipt but never appear on the video.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import FunctionType

from PIL import Image, ImageDraw, ImageFont


GENERATOR = Path(__file__).resolve()
ROOT = GENERATOR.parents[2]
ORIGINAL_RENDERER = GENERATOR.with_name('append_references_original.py')
_spec = importlib.util.spec_from_file_location('frozen_original_title_renderer', ORIGINAL_RENDERER)
original = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(original)
engine = original.engine
OLD_ENGINE = original.OLD_ENGINE
DEFAULT_FONT, DEFAULT_BOLD = original.DEFAULT_FONT, original.DEFAULT_BOLD
PRESENTATION = 'title-author'
LAYOUT = {'kind': 'title-author-single-column', 'maxItemsPerPage': 4,
          'renderedFields': ['title', 'credit'], 'quotesRendered': False}


def credit(source):
    if 'author' in source:
        if not isinstance(source['author'], str) or not source['author'].strip():
            raise ValueError(f"{source['id']}: an explicit author must be a nonempty original credit")
        return source['author']
    return source['organization']


def bibliography(doc):
    return [{'id': s['id'], 'title': s['title'], 'credit': credit(s)} for s in doc['sources']]


def load_references(path):
    # Reuse the original-title/evidence validator with only its presentation
    # constant selected privately. Do not mutate its module globals or bytes.
    validate = FunctionType(original.load_references.__code__,
                            dict(vars(original), PRESENTATION=PRESENTATION),
                            original.load_references.__name__)
    doc = validate(path)
    for source in doc['sources']:
        credit(source)
    return doc


def render_cards(doc, directory, width, height, font_path, bold_path):
    if width < 1280 or height < 720 or abs(height / width - 9 / 16) > 0.002:
        raise ValueError('Bibliography layout requires 16:9 video at least 1280×720')
    colors, scale = engine.palette(), width / 1920
    font = lambda size, bold=False: ImageFont.truetype(
        str(bold_path if bold else font_path), max(1, round(size * scale)), index=2)
    xy = lambda x, y: (round(x * scale), round(y * scale))
    items = bibliography(doc)
    pages = [items[i:i + 4] for i in range(0, len(items), 4)]
    paths = []
    for page_index, sources in enumerate(pages):
        image = Image.new('RGB', (width, height), colors['bg'])
        draw = ImageDraw.Draw(image)
        draw.text(xy(116, 76), '参考资料', font=font(64, True), fill=colors['ink'])
        top = 280
        for source in sources:
            title_lines = original.wrap_original('《' + source['title'] + '》', draw,
                                                  font(44), round(1668 * scale))
            if len(title_lines) > 3:
                raise ValueError(f"COPYFIT complete original title too long: {source['id']}; never truncate it")
            for index, line in enumerate(title_lines):
                draw.text(xy(120, top + index * 58), line, font=font(44), fill=colors['ink'])
            last_y = top + (len(title_lines) - 1) * 58
            after_title = 120 * scale + draw.textlength(title_lines[-1], font=font(44)) + 42 * scale
            if after_title + draw.textlength(source['credit'], font=font(36)) <= 1800 * scale:
                draw.text((round(after_title), round((last_y + 8) * scale)),
                          source['credit'], font=font(36), fill=colors['muted'])
                bottom = last_y + 58
            else:
                credit_lines = original.wrap_original(source['credit'], draw, font(36), round(1668 * scale))
                if len(credit_lines) > 2:
                    raise ValueError(f"COPYFIT complete author/organization too long: {source['id']}")
                for index, line in enumerate(credit_lines):
                    draw.text(xy(120, last_y + 58 + index * 48), line,
                              font=font(36), fill=colors['muted'])
                bottom = last_y + 58 + len(credit_lines) * 48
            if bottom > 880:
                raise ValueError(f"COPYFIT bibliography exceeds player-safe bounds: {source['id']}")
            top = bottom + 48
        path = directory / f'references-{page_index + 1:02}.png'
        image.save(path)
        paths.append(path)
    return paths


def adapted(function):
    return FunctionType(function.__code__, dict(vars(engine), __file__=str(GENERATOR),
                        load_references=load_references, render_cards=render_cards),
                        function.__name__, function.__defaults__, function.__closure__)


def dependencies():
    return {'oldEngine': str(OLD_ENGINE.relative_to(ROOT)), 'oldEngineSHA256': engine.sha(OLD_ENGINE),
            'originalRenderer': str(ORIGINAL_RENDERER.relative_to(ROOT)),
            'originalRendererSHA256': engine.sha(ORIGINAL_RENDERER)}


def verify_identity(receipt, doc):
    if receipt.get('presentation') != PRESENTATION or receipt.get('layout') != LAYOUT:
        raise ValueError('Bibliography receipt presentation/layout differs')
    if receipt.get('bibliography') != bibliography(doc):
        raise ValueError('Bibliography receipt original titles/credits differ')
    if receipt.get('sourceTitles') != original.source_titles(doc) or receipt.get('quotations') != original.quotations(doc):
        raise ValueError('Bibliography research title/quotation identities differ')
    if receipt.get('dependencies') != dependencies():
        raise ValueError('Frozen bibliography renderer dependencies changed')
    if receipt['inputs'].get('generatorSHA256') != engine.sha(GENERATOR):
        raise ValueError('Frozen bibliography generator changed')
    if len(receipt['appendix']['pages']) != (len(doc['sources']) + 3) // 4:
        raise ValueError('Bibliography pagination differs from four-source layout')


def append(args):
    doc = load_references(args.references)
    path = args.artifacts / 'reference-appendix.json'
    if path.exists():
        old = json.loads(path.read_text())
        if old.get('presentation') == PRESENTATION and old.get('dependencies') != dependencies():
            raise ValueError('Bibliography dependency changed; preserve previous receipt before regenerating')
    result = adapted(engine.append)(args)
    receipt = json.loads(path.read_text())
    unmarked = result['status'] == 'already-current' and 'presentation' not in receipt
    if unmarked and any(k in receipt for k in ('bibliography', 'sourceTitles', 'quotations', 'layout', 'dependencies')):
        raise ValueError('Incomplete mixed bibliography identity; preserve receipt before regenerating')
    if result['status'] != 'already-current' or unmarked:
        receipt.update(presentation=PRESENTATION, layout=LAYOUT, bibliography=bibliography(doc),
                       sourceTitles=original.source_titles(doc), quotations=original.quotations(doc),
                       dependencies=dependencies())
        engine.dump(path, receipt)
    verify_identity(receipt, doc)
    return {**result, **receipt}


def verify(args):
    doc = load_references(args.references)
    verify_identity(json.loads((args.artifacts / 'reference-appendix.json').read_text()), doc)
    return adapted(engine.verify)(args)


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
