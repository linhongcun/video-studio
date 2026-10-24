"""tiny fixture covers spec: title + sample badge, 16x9 and 4x3."""
TITLE = '你好世界'
BANNED = ('熔断',)


def build():
    def title(x, y, w): return {'id': 'title', 'type': 'text', 'text': TITLE, 'x': x, 'y': y, 'w': w, 'h': 120, 'fontSize': 80, 'color': '#FFFFFF'}
    def badge(x, y): return {'id': 'sample', 'type': 'text', 'component': 'CornerBadge', 'sampleData': True, 'text': '示例数据', 'x': x, 'y': y, 'w': 180, 'h': 54, 'fontSize': 32}
    return {'rule': 'synthetic', 'title': TITLE,
            'sizes': {'16x9': {'width': 1920, 'height': 1080, 'bottom15Y': 918, 'watermarkZone': [1680, 30, 1880, 100], 'elements': [title(96, 200, 900), badge(96, 400)]},
                      '4x3': {'width': 1440, 'height': 1080, 'bottom15Y': 918, 'centerRegion': [315, 1125], 'watermarkZone': [1200, 30, 1400, 100], 'elements': [title(315, 200, 800), badge(315, 400)]}}}


def check(C):
    assert C['title'] == TITLE
