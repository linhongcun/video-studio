#!/usr/bin/env python3
"""covers spec -> covers.json (16x9 / 4x3 / 3x4 cover layouts).

  python3 -B episodes/_shared/storyboard/make_covers.py --spec SPEC.py [--episode-dir EPDIR] [--out covers.json]

The spec module defines:
  build()          -> the covers dict (rule, title, seriesTag, ..., sizes{name: {width, height, bottom15Y, watermarkZone, elements}})
  finalize(C)      optional; may assert and add computed records (e.g. BrowserChrome addressFit) before the generic checks
  check(C)         optional; episode-specific asserts after the generic checks
  HEADER, FIRST_ROW_GAP   optional (default 80 / 24): page header height and min gap to the first page row
  BANNED           optional list of words that must not appear anywhere in covers.json
Generic checks (assert, so a bad cover never gets written): every element above bottom15Y and inside width, off the
watermarkZone, inside centerRegion when the size has one (4x3), the sampleData CornerBadge outside every BrowserChrome,
and the first page row >= FIRST_ROW_GAP below the page header. Output: json indent=1."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit


def overlap(a, b): return a['x'] < b['x'] + b['w'] and b['x'] < a['x'] + a['w'] and a['y'] < b['y'] + b['h'] and b['y'] < a['y'] + a['h']


def generic_checks(C, header=80, first_gap=24, banned=()):
    for name, sz in C['sizes'].items():
        wz = sz['watermarkZone']; cr = sz.get('centerRegion')
        for e in sz['elements']:
            assert e['y'] + e['h'] <= sz['bottom15Y'], (name, e['id'], '进底部 15%')
            assert e['x'] + e['w'] <= sz['width'], (name, e['id'], '出画')
            assert e['x'] >= wz[2] or e['x'] + e['w'] <= wz[0] or e['y'] >= wz[3] or e['y'] + e['h'] <= wz[1], (name, e['id'], '压水印')
            if cr: assert cr[0] <= e['x'] and e['x'] + e['w'] <= cr[1], (name, e['id'], e['x'], e['w'], '出 centerRegion')
        pages = [e for e in sz['elements'] if e.get('component') == 'BrowserChrome']
        badges = [e for e in sz['elements'] if e.get('component') == 'CornerBadge' and e.get('sampleData')]
        for pg in pages:
            for sb in badges: assert not overlap(sb, pg), (name, sb['id'], '示例数据角标压在页面上')
            if pg.get('boxes'):
                first = min(v[1] for v in pg['boxes'].values())
                assert first - (pg['y'] + 3 + header) >= first_gap, (name, pg['id'], f'首行离页头 < {first_gap}')
    txt = json.dumps(C, ensure_ascii=False)
    for w in banned: assert w not in txt, ('封面出现禁词', w)


def run(spec, out):
    C = spec.build()
    if hasattr(spec, 'finalize'): spec.finalize(C)
    generic_checks(C, getattr(spec, 'HEADER', 80), getattr(spec, 'FIRST_ROW_GAP', 24), getattr(spec, 'BANNED', ()))
    if hasattr(spec, 'check'): spec.check(C)
    kit.write_json(out, C, 1); print('covers ok')
    return C


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--spec', required=True); ap.add_argument('--episode-dir'); ap.add_argument('--out')
    a = ap.parse_args(argv)
    run(kit.load_spec(a.spec, 'covers'), a.out or kit.default_out(a, 'covers.json'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
