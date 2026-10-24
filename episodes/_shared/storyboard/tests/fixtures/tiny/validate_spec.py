"""tiny fixture validate spec."""
TITLE = '你好世界'; EPISODE = 0; SLUG = 'tiny'
WAVLEN = 120; NSHOT = 2; NSENT = 2; MIN = 30; MAX = 90; TR = 10
Q = '你好世界之后，下一句该说什么？评论区说说。'; NEXT = (1, '下期见')
KNOLL = [(0, 60), (60, 120)]
NARRATION_FILE = 'narration.py'
BROWSER_SHOTS = [2]; BOX_SHOTS = []
URL_DOMAIN = 'shop.example'
FAKE_TEXT = ('终端', '熔断'); FILM_BANNED = ('熔断',)
SAMPLE_RE = r'(世界)'; SAMPLE_MARK = '示例'
TERMS = (('朋友', 2),)
SAMPLE_UNTIL = 3
SCREEN_STRIP = r'。$'
MIN_QUOTES = 1; ARTICLE_NEEDS = ('你好', '示例')


def checks(v):
    e = v.E(1)['hello']
    v.check(e['cueText'] == '你好' and v.kf(e, 'lit')['cueText'] == '世界', '镜 1 hello 挂「你好」、「世界」变色')
    v.check(v.E(1)['tick']['timingRole'] == 'timer', '镜 1 tick 由计时器驱动')
    v.check(v.pages(2)[0]['appearFrame'] == 0, '镜 2 网页第 0 帧在场')
