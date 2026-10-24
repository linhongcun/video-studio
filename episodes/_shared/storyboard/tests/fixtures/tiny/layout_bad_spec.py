"""BAD fixture: same as layout_spec but shot 1's text drops into the subtitle band (y + h > 900) -> validate must fail."""
import layout_spec as base
from layout_spec import NSHOT, BROWSER, BOXSHOTS


def build(ctx):
    base.build(ctx)
    for e in ctx.L['1']['elements']:
        if e['id'] == 'hello': e['y'] = 860
