"""tiny fixture build spec (2 shots, 120 frames)."""
FPS = 30; MIN = 30; MAX = 90; TR = 10; WAVLEN = 120; NSHOT = 2
MAX_EXC = {}
KNOLL = [(0, 60), (60, 120)]
SHA = {}
NARRATION_FILE = 'narration.py'
PUNCT = '，。：；？！、,:;?!…「」 -'
TITLE = '你好世界'; Q = '你好世界之后，下一句该说什么？评论区说说。'
CHAPTERS = [('open', '开场', '#22D3EE'), ('end', '结尾', '#F472B6')]
def ch_of(n): return 'open' if n == 1 else 'end'
SUB = {'id': 'subtitle', 'type': 'text', 'x': 160, 'y': 900, 'w': 1600, 'h': 80, 'text': '', 'fontSize': 40, 'color': '#E5E7EB', 'align': 'center', 'role': 'subtitle', 'binding': 'subtitles', 'z': 20}
NEWCOMP_FIELDS = {}


def meta(ctx):
    return {'title': TITLE, 'episode': 0, 'slug': 'tiny', 'draft': True, 'provisionalTiming': False,
            'timingSource': f'voice.wav sha256 {ctx.WAV_SHA[:8]} / words.json {ctx.WORDS_SHA[:8]}（合成自测音）',
            'onsetRule': {'module': 'episodes/_shared/onset_rule.py', 'window': [-6, 2], 'frameFormula': 'max(1, floor(onsetLocal) − 2) + d'},
            'width': 1920, 'height': 1080, 'fps': FPS, 'durationInFrames': ctx.g,
            'durationExceptions': [{'shot': n, 'frames': v, 'max': MAX, 'reason': 'test'} for n, v in ctx.MAX_EXC.items()],
            'boxShots': ctx.BOXP, 'mapShots': [], 'devtoolsShots': [], 'chapters': ctx.chapters,
            'covers': ctx.COVERS, 'discussionQuestion': Q, 'nextEpisode': {'episode': 1, 'title': '下期', 'teaser': '下期见'}}


ASSETS = {'new': [], 'reuse': [], 'procedural': {'description': 'synthetic fixture'}}
