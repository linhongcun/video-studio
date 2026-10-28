#!/usr/bin/env python3
"""Render purple reference cards with the frozen bibliography/media engines.

Only the palette is selected here.  The original title/credit layout and the
full body-frame, AAC-packet and decoded-PCM checks run from the existing engines
with private globals; none of their files or module globals are changed.

Both CLI actions accept --body, --references, --output and --artifacts.  ``verify``
reads production artifacts without replacing receipts or their media reports.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import tempfile
from types import FunctionType, SimpleNamespace


GENERATOR = Path(__file__).resolve()
ROOT = GENERATOR.parents[3]
PALETTE = GENERATOR.parent.parent / 'puzzles-covers/catalog.json'
BIBLIOGRAPHY = GENERATOR.parent.parent / 'append_references_bibliography.py'
_spec = importlib.util.spec_from_file_location('puzzles_frozen_bibliography', BIBLIOGRAPHY)
bibliography = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bibliography)
engine = bibliography.engine
DEFAULT_FONT, DEFAULT_BOLD = bibliography.DEFAULT_FONT, bibliography.DEFAULT_BOLD
PRESENTATION, LAYOUT = bibliography.PRESENTATION, bibliography.LAYOUT
load_references = bibliography.load_references


def palette() -> dict[str, str]:
    """Use the cover catalog itself, also imported by the new series canvas."""
    document = json.loads(PALETTE.read_text())
    colors = document['palette']
    mapping = {'bg': 'background', 'ink': 'text', 'muted': 'muted',
               'row': 'surface', 'border': 'edge', 'success': 'teal'}
    for key in mapping.values():
        if not isinstance(colors.get(key), str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', colors[key]):
            raise ValueError(f'Missing or invalid puzzles palette color: {key}')
    return {key: colors[value] for key, value in mapping.items()}


def dependency_files() -> list[Path]:
    """Actual renderer files for the revision's independent input manifest."""
    return [GENERATOR, PALETTE, BIBLIOGRAPHY, bibliography.ORIGINAL_RENDERER,
            bibliography.OLD_ENGINE]


def dependencies() -> dict:
    return {
        **bibliography.dependencies(),
        'bibliographyRenderer': str(BIBLIOGRAPHY.relative_to(ROOT)),
        'bibliographyRendererSHA256': engine.sha(BIBLIOGRAPHY),
        'palette': str(PALETTE.relative_to(ROOT)),
        'paletteSHA256': engine.sha(PALETTE),
    }


def render_cards(doc, directory, width, height, font_path, bold_path):
    # The frozen layout only calls engine.palette().  A private namespace changes
    # colors while retaining its original title wrapping, spacing and COPYFIT.
    renderer = FunctionType(
        bibliography.render_cards.__code__,
        dict(vars(bibliography), engine=SimpleNamespace(palette=palette)),
        bibliography.render_cards.__name__, bibliography.render_cards.__defaults__,
        bibliography.render_cards.__closure__,
    )
    return renderer(doc, directory, width, height, font_path, bold_path)


def adapted(function, **overrides):
    return FunctionType(
        function.__code__,
        dict(vars(engine), __file__=str(GENERATOR), THEME=PALETTE,
             load_references=load_references, render_cards=render_cards, **overrides),
        function.__name__, function.__defaults__, function.__closure__,
    )


def verify_identity(receipt, doc) -> None:
    if receipt.get('presentation') != PRESENTATION or receipt.get('layout') != LAYOUT:
        raise ValueError('Purple bibliography receipt presentation/layout differs')
    if receipt.get('bibliography') != bibliography.bibliography(doc):
        raise ValueError('Purple bibliography original titles/credits differ')
    if receipt.get('sourceTitles') != bibliography.original.source_titles(doc) \
            or receipt.get('quotations') != bibliography.original.quotations(doc):
        raise ValueError('Purple bibliography research source identities differ')
    if receipt.get('dependencies') != dependencies():
        raise ValueError('Frozen purple bibliography renderer/palette dependency changed')
    if receipt.get('inputs', {}).get('generatorSHA256') != engine.sha(GENERATOR):
        raise ValueError('Frozen purple bibliography adapter changed')
    if receipt.get('inputs', {}).get('themeSHA256') != engine.sha(PALETTE):
        raise ValueError('Frozen purple bibliography palette changed')
    if receipt.get('inputs', {}).get('secondsPerPage') != 5 \
            or len(receipt['appendix']['pages']) != (len(doc['sources']) + 3) // 4:
        raise ValueError('Purple bibliography requires four sources/page and five seconds/page')


def append(args) -> dict:
    if args.seconds != 5:
        raise ValueError('The current reference-card specification requires five seconds per page')
    palette()  # Validate the shared input before starting any media operation.
    doc = load_references(args.references)
    receipt_path = args.artifacts / 'reference-appendix.json'
    if receipt_path.exists():
        previous = json.loads(receipt_path.read_text())
        # A fresh revision path is required when any inherited renderer or
        # palette changes.  Never replace evidence for an earlier rendering.
        if previous.get('presentation') == PRESENTATION \
                and previous.get('dependencies') != dependencies():
            raise ValueError('Purple bibliography dependencies changed; preserve previous artifacts first')
    result = adapted(engine.append)(args)
    receipt = json.loads(receipt_path.read_text())
    unmarked = result['status'] == 'already-current' and 'presentation' not in receipt
    if unmarked and any(key in receipt for key in
                        ('bibliography', 'sourceTitles', 'quotations', 'layout', 'dependencies')):
        raise ValueError('Incomplete mixed bibliography identity; preserve this receipt first')
    if result['status'] != 'already-current' or unmarked:
        receipt.update(
            presentation=PRESENTATION, layout=LAYOUT,
            bibliography=bibliography.bibliography(doc),
            sourceTitles=bibliography.original.source_titles(doc),
            quotations=bibliography.original.quotations(doc), dependencies=dependencies(),
            bodyProductionInputs='Body was rendered from the independent cover-continuity revision manifest; original narration/timing/source freezes remain unchanged and retain their historical identities.',
        )
        engine.dump(receipt_path, receipt)
    verify_identity(receipt, doc)
    return {**result, **receipt}


def verify(args) -> dict:
    """Run the inherited full media verification without writing production files."""
    if args.seconds != 5:
        raise ValueError('The current reference-card specification requires five seconds per page')
    palette()
    doc = load_references(args.references)
    receipt = json.loads((args.artifacts / 'reference-appendix.json').read_text())
    verify_identity(receipt, doc)
    recorded = json.loads((args.artifacts / 'reference-appendix-media-check.json').read_text())
    if recorded.get('passed') is not True:
        raise ValueError('Recorded appendix media verification is absent or failed')
    with tempfile.TemporaryDirectory(prefix='puzzles-reference-verify-') as temporary:
        def verify_media(*values):
            # Keep the frozen full-file verifier, but redirect its sole write.
            return engine.verify_media(*values[:-1], Path(temporary) / 'media-check.json')

        report = adapted(engine.verify, verify_media=verify_media)(args)
    # checkedAtUTC changes on each independent verification.  Every semantic
    # field from the original saved media report must reproduce exactly.
    if {key: value for key, value in report.items() if key != 'checkedAtUTC'} != \
            {key: value for key, value in recorded.items() if key != 'checkedAtUTC'}:
        raise ValueError('Recorded purple appendix media report differs from full verification')
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('append', 'verify'))
    for name in ('body', 'references', 'output', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=5)
    parser.add_argument('--font', type=Path, default=DEFAULT_FONT)
    parser.add_argument('--bold-font', type=Path, default=DEFAULT_BOLD)
    args = parser.parse_args()
    result = append(args) if args.action == 'append' else verify(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
