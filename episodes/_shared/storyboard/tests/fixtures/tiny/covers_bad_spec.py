"""BAD fixture: a cover element in the bottom 15% -> make_covers must refuse to write covers.json."""
import covers_spec as base
BANNED = base.BANNED


def build():
    C = base.build(); C['sizes']['16x9']['elements'][1]['y'] = 900
    return C
