#!/usr/bin/env python3
"""Render exact original source titles and optional verbatim excerpts.

The frozen legacy module remains byte-for-byte unchanged. Its append/verify
functions run with a private globals mapping that selects this layout and
validator and identifies this file as the generator. All media concatenation,
body frame/PTS comparison, original AAC copying, and PCM checks remain the
legacy implementation; they are not copied into this file.

  python append_references_original.py append --body original.mp4 \
    --references references.json --output video.mp4 --artifacts revisions/references

schemaVersion=1, presentation='original-title-quote'. Every source retains the
complete original title and titleEvidence={locator,evidence}. Optional
quotation={text,locator,evidence} is a verbatim source excerpt, never a summary.
The deprecated displayTitle/displaySupport fields are rejected. supports and
sections remain research metadata and are not rendered as source quotations.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
from types import FunctionType

from PIL import Image, ImageDraw, ImageFont


GENERATOR = Path(__file__).resolve()
ROOT = GENERATOR.parents[2]
OLD_ENGINE = GENERATOR.with_name('append_references.py')
PRESENTATION = 'original-title-quote'

_spec = importlib.util.spec_from_file_location('reference_appendix_frozen_engine', OLD_ENGINE)
engine = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(engine)
DEFAULT_FONT, DEFAULT_BOLD = engine.DEFAULT_FONT, engine.DEFAULT_BOLD


def evidence_path(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label}: missing evidence file')
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'{label}: evidence must be an existing repository file')
    return path


def load_references(path: Path) -> dict:
    doc = engine.load_references(path)
    if doc.get('presentation') != PRESENTATION:
        raise ValueError(f'references.json requires presentation {PRESENTATION!r}')
    for source in doc['sources']:
        if any(key in source for key in ('displayTitle', 'displaySupport')):
            raise ValueError(f"{source['id']}: remove displayTitle/displaySupport; render the complete original title")
        title_evidence = source.get('titleEvidence')
        if not isinstance(title_evidence, dict) or not isinstance(title_evidence.get('locator'), str) \
                or not title_evidence['locator'].strip():
            raise ValueError(f"{source['id']}: titleEvidence requires an original-title locator")
        evidence_path(title_evidence.get('evidence'), f"{source['id']} original title")
        if 'quotation' in source:
            quotation = source['quotation']
            if not isinstance(quotation, dict) or any(
                not isinstance(quotation.get(key), str) or not quotation[key].strip()
                for key in ('text', 'locator', 'evidence')
            ):
                raise ValueError(f"{source['id']}: quotation requires verbatim text, locator and evidence")
            evidence_path(quotation['evidence'], f"{source['id']} quotation")
    return doc


def source_titles(doc):
    return [{'id': source['id'], 'title': source['title']} for source in doc['sources']]


def quotations(doc):
    return [{'id': source['id'], **source['quotation']}
            for source in doc['sources'] if 'quotation' in source]


def wrap_original(text, draw, font, width):
    """Wrap at word boundaries while retaining every non-whitespace character."""
    lines = []
    for paragraph in text.split('\n'):
        line = ''
        for token in re.findall(r'\S+\s*', paragraph):
            if line and draw.textlength((line + token).rstrip(), font=font) > width:
                lines.append(line.rstrip())
                line = ''
            if draw.textlength(token.rstrip(), font=font) > width:
                pieces = engine.wrapped(token.rstrip(), draw, font, width)
                lines.extend(pieces[:-1])
                line = pieces[-1] + (' ' if token[-1].isspace() else '')
            else:
                line += token
        lines.append(line.rstrip())
    if re.sub(r'\s+', '', ''.join(lines)) != re.sub(r'\s+', '', text):
        raise ValueError('Original source text changed during line wrapping')
    return lines


def render_cards(doc: dict, directory: Path, width: int, height: int,
                 font_path: Path, bold_path: Path) -> list[Path]:
    if width < 1280 or height < 720 or abs(height / width - 9 / 16) > 0.002:
        raise ValueError('Original-title reference layout requires 16:9 video at least 1280×720')
    colors, scale = engine.palette(), width / 1920
    font = lambda size, bold=False: ImageFont.truetype(
        str(bold_path if bold else font_path), max(1, round(size * scale)), index=2)
    xy = lambda x, y: (round(x * scale), round(y * scale))
    pages = [doc['sources'][i:i + 2] for i in range(0, len(doc['sources']), 2)]
    paths = []
    for page_index, sources in enumerate(pages):
        image = Image.new('RGB', (width, height), colors['bg'])
        draw = ImageDraw.Draw(image)
        draw.text(xy(116, 58), doc.get('heading', '参考资料'), font=font(60, True), fill=colors['ink'])
        hint = '原始题名 · 可暂停阅读 · 完整出处见配套图文'
        checked = f"资料核验：{doc['checkedAt']}"
        if draw.textlength(hint, font=font(28)) > (1330 - 119 - 60) * scale:
            raise ValueError('COPYFIT original-title reading hint overlaps access date')
        if draw.textlength(checked, font=font(25)) > (1808 - 1330) * scale:
            raise ValueError('COPYFIT original-title access date is too wide')
        draw.text(xy(119, 145), hint, font=font(28), fill=colors['muted'])
        draw.text(xy(1330, 147), checked, font=font(25), fill=colors['muted'])
        draw.text(xy(1698, 90), f'{page_index + 1} / {len(pages)}', font=font(30), fill=colors['muted'])
        for index, source in enumerate(sources):
            top = 220 + index * 346
            draw.rounded_rectangle((*xy(112, top), *xy(1808, top + 320)),
                                   radius=round(16 * scale), fill=colors['row'])
            draw.text(xy(142, top + 18), f"[{source['id']}]", font=font(27, True), fill=colors['success'])
            note = f" · {source['note']}" if source.get('note') else ''
            metadata = f"{source['organization']} · {source['version']}{note}"
            if draw.textlength(metadata, font=font(25)) > 1490 * scale:
                raise ValueError(f"COPYFIT source organization/version too wide: {source['id']}")
            draw.text(xy(263, top + 18), metadata, font=font(25), fill=colors['muted'])
            title_lines = wrap_original(source['title'], draw, font(34, True), round(1490 * scale))
            if len(title_lines) > 3:
                raise ValueError(f"COPYFIT complete original title exceeds 3 lines: {source['id']}; do not shorten or replace it")
            for line_index, line in enumerate(title_lines):
                draw.text(xy(263, top + 54 + line_index * 40), line, font=font(34, True), fill=colors['ink'])
            label_top = top + 54 + len(title_lines) * 40 + 10
            quotation = source.get('quotation')
            locator = quotation['locator'] if quotation else source['titleEvidence']['locator']
            label = ('原文摘录 · ' if quotation else '出处位置 · ') + locator
            if draw.textlength(label, font=font(21)) > 1490 * scale:
                raise ValueError(f"COPYFIT original source locator too wide: {source['id']}")
            draw.text(xy(263, label_top), label, font=font(21), fill=colors['success'])
            if quotation:
                quote_lines = wrap_original('“' + quotation['text'] + '”', draw, font(25), round(1490 * scale))
                if len(quote_lines) > 3:
                    raise ValueError(f"COPYFIT verbatim quotation exceeds 3 lines: {source['id']}; choose a shorter actual passage")
                quote_top = label_top + 30
                if quote_top + len(quote_lines) * 31 > top + 312:
                    raise ValueError(f"COPYFIT original title plus quotation exceeds card bounds: {source['id']}")
                for line_index, line in enumerate(quote_lines):
                    draw.text(xy(263, quote_top + line_index * 31), line, font=font(25), fill=colors['ink'])
        output = directory / f'references-{page_index + 1:02}.png'
        image.save(output)
        paths.append(output)
    return paths


def adapted(function):
    """Reuse frozen code with private dependency injection, without editing it."""
    globals_map = dict(vars(engine), __file__=str(GENERATOR),
                       load_references=load_references, render_cards=render_cards)
    return FunctionType(function.__code__, globals_map, function.__name__,
                        function.__defaults__, function.__closure__)


def verify_identity(receipt, doc):
    if receipt.get('presentation') != PRESENTATION:
        raise ValueError('Appendix receipt uses a different source presentation')
    if receipt.get('sourceTitles') != source_titles(doc) or receipt.get('quotations') != quotations(doc):
        raise ValueError('Appendix receipt original source titles/quotations differ from references')
    dependencies = receipt.get('dependencies', {})
    if dependencies.get('oldEngine') != str(OLD_ENGINE.relative_to(ROOT)) \
            or dependencies.get('oldEngineSHA256') != engine.sha(OLD_ENGINE):
        raise ValueError('Frozen original appendix media engine dependency changed')
    if receipt['inputs'].get('generatorSHA256') != engine.sha(GENERATOR):
        raise ValueError('Frozen original-title appendix generator changed')


def append(args):
    doc = load_references(args.references)
    receipt_path = args.artifacts / 'reference-appendix.json'
    if receipt_path.exists():
        previous = json.loads(receipt_path.read_text())
        if previous.get('presentation') == PRESENTATION:
            dependencies = previous.get('dependencies', {})
            if dependencies.get('oldEngineSHA256') != engine.sha(OLD_ENGINE):
                raise ValueError('Original media engine changed; preserve the old receipt before regenerating')
    result = adapted(engine.append)(args)
    receipt = json.loads(receipt_path.read_text())
    # The frozen engine writes its media receipt before this adapter adds the
    # layout identity. Recover that narrow interruption window only when the
    # engine has already matched the current body/references/generator/output.
    unmarked_current = result['status'] == 'already-current' and 'presentation' not in receipt
    if unmarked_current and any(key in receipt for key in ('sourceTitles', 'quotations', 'dependencies')):
        raise ValueError('Incomplete mixed appendix identity; preserve this receipt before regenerating')
    if result['status'] != 'already-current' or unmarked_current:
        receipt.update(presentation=PRESENTATION, sourceTitles=source_titles(doc), quotations=quotations(doc),
                       dependencies={'oldEngine': str(OLD_ENGINE.relative_to(ROOT)),
                                     'oldEngineSHA256': engine.sha(OLD_ENGINE)})
        engine.dump(receipt_path, receipt)
    verify_identity(receipt, doc)
    return {**result, **receipt}


def verify(args):
    doc = load_references(args.references)
    receipt = json.loads((args.artifacts / 'reference-appendix.json').read_text())
    verify_identity(receipt, doc)
    return adapted(engine.verify)(args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('append', 'verify'))
    parser.add_argument('--body', required=True, type=Path)
    parser.add_argument('--references', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--artifacts', required=True, type=Path)
    parser.add_argument('--seconds', type=float, default=5)
    parser.add_argument('--font', type=Path, default=DEFAULT_FONT)
    parser.add_argument('--bold-font', type=Path, default=DEFAULT_BOLD)
    args = parser.parse_args()
    print(json.dumps(append(args) if args.action == 'append' else verify(args), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
