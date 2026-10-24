#!/usr/bin/env python3
"""layout spec -> layout.json.

  python3 -B episodes/_shared/storyboard/layout.py --spec SPEC.py --episode-dir EPDIR [--inputs MAP.json] [--out layout.json]

The spec module defines NSHOT, BROWSER (browser shot numbers), BOXSHOTS (box-card shots) and build(ctx), which calls
ctx.part(n, direction, elements, box=...) once per script shot. Helpers: layout_kit (C, TM, W, T, S, wid) and
ctx.reveal / ctx.cue0 / ctx.SHOT0 / ctx.SHOTLEN (from words.json). Output: json indent=2."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit
from layout_kit import LayoutCtx


def run(spec, inp, out):
    ctx = LayoutCtx(inp.json('words.json'), spec.NSHOT, spec.BROWSER, spec.BOXSHOTS)
    spec.build(ctx)
    L = ctx.done()
    kit.write_json(out, L, 2)
    print('layout ok', len(L), 'box', [k for k, v in L.items() if v['box']], 'browser', [k for k, v in L.items() if v['frame'] == 'browser'])
    return L


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    kit.add_input_args(ap); ap.add_argument('--out')
    a = ap.parse_args(argv)
    run(kit.load_spec(a.spec, 'layout'), kit.inputs_from(a), a.out or kit.default_out(a, 'layout.json'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
