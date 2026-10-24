"""EP.14 degradation (slug degradation-v1) build spec — ported from the episode-dir build_sb.py v1.0.0 (frozen storyboard 6265993b).
Run:  python3 -B episodes/_shared/storyboard/build_sb.py --spec episodes/_shared/storyboard/examples/degradation/build_spec.py \
        --episode-dir episodes/degradation --inputs episodes/_shared/storyboard/examples/degradation/repo-inputs.json \
        --layout OUT/layout.json --covers OUT/covers.json --out OUT/storyboard.json
Inputs: script.md 629b5042 (narration), words.json 36bccee8, voice.wav 9e70470c, voice/cues.json 751217cb and voice/shot_frames.json
f8f03b6c (sha pinning only), narration.py 013cfb9b. The meta strings below are frozen data (they describe the episode as released,
including the episodes-codex paths used at the time) — keep them byte-for-byte or the storyboard sha changes."""
FPS = 30; MAX = 300; MIN = 180; TR = 10; WAVLEN = 5152; NSHOT = 20
MAX_EXC = {1: 314}   # 配音 9e70470c：镜 1 = 314 帧（开场冲突＋问题句，Knoll 帧表定稿），唯一段长例外；其余 19 镜在 180..300 内
KNOLL = [(0, 314), (314, 595), (595, 865), (865, 1131), (1131, 1395), (1395, 1650), (1650, 1905), (1905, 2148), (2148, 2382), (2382, 2632), (2632, 2858), (2858, 3115), (3115, 3375), (3375, 3601), (3601, 3827), (3827, 4103), (4103, 4363), (4363, 4630), (4630, 4883), (4883, 5152)]
SHA = {'narration.py': '013cfb9b', 'voice.wav': '9e70470c', 'words.json': '36bccee8', 'voice/cues.json': '751217cb', 'voice/shot_frames.json': 'f8f03b6c'}
WORDS_SCRIPT_SHA = '629b5042'; WORDS_AUDIO_SHA = '9e70470c'
NARRATION_FILE = 'narration.py'
PUNCT = '，。：；？！、,:;?!…「」 -'
TITLE = '搜索页和结算页，为什么两个价不一样？'
Q = '要是搜索页和结算页都把红包计算一起关掉，下单还能不能顺利完成？评论区说说。'
CHAPTERS = [('hook', '开场', '#22D3EE'), ('prices', '一、两个价分别怎么算', '#F97316'), ('turn-off', '二、为什么关掉搜索页的红包计算', '#22C55E'),
            ('degrade', '三、核心链路与降级', '#A78BFA'), ('after', '四、降级之后还能做什么', '#F472B6'), ('ending', '结尾', '#22D3EE')]
def ch_of(n): return 'hook' if n <= 2 else 'prices' if n <= 5 else 'turn-off' if n <= 9 else 'degrade' if n <= 12 else 'after' if n <= 16 else 'ending'
SUB_MAX = 22; SUB_MERGE = 16
SUB = {'id': 'subtitle', 'type': 'text', 'x': 160, 'y': 900, 'w': 1600, 'h': 80, 'text': '', 'fontSize': 40, 'color': '#E5E7EB', 'align': 'center', 'role': 'subtitle', 'binding': 'subtitles', 'z': 20}
NEWCOMP_FIELDS = {}


def meta(ctx):
    return {'title': TITLE, 'episode': 14, 'slug': 'degradation-v1', 'release': 'v1.1.0', 'draft': True,
          'provisional': False, 'provisionalTiming': False, 'pendingAudio': False, 'provisionalReason': None,
          'timingSource': f'voice.wav sha256 {ctx.WAV_SHA[:8]}… / words.json {ctx.WORDS_SHA[:8]}… / script.md {ctx.SCRIPT_SHA[:8]}（旁白逐字 = 629b5042 = narration.py 013cfb9b，配音依据不变；本版只改画面/屏幕文字/标注表/封面文字）；整条配音按原位置铺开，不插停顿（总长 = voice.wav {WAVLEN} 帧，镜头区间 = Knoll 定的绝对帧 = words.json shots[] = voice/shot_frames.json）；标签、状态帧带 cueLog/cueText 的帧按开口规则（video-studio/episodes-codex/_shared/onset_rule.py）向下取整 −2 帧（+d），窗口 −6..+2 小数帧；timerLog 与 timerDriven 的帧由画面节奏驱动、不对旁白（镜 3、4 地址栏逐字输入每帧一字、输完 3 帧回车；镜 4 按下加购 20 帧后新开标签；镜 6 请求数与资源每 8 帧一档同帧同步；镜 14 按下后 20 帧出成功页；点击波纹 20 帧长满）；Knoll 按 shots[].voice 放句（wavStart..wavEnd 剪出，放在 from+localStart），或直接整轨铺在第 0 帧（两者等价）',
          'onsetRule': {'module': '/workspace/video-studio/episodes-codex/_shared/onset_rule.py', 'checker': '/workspace/video-studio/episodes-codex/_shared/label_onset_strict.py', 'window': [-6, 2], 'frameFormula': 'max(1, floor(onsetLocal) − 2) + d'},
          'width': 1920, 'height': 1080, 'fps': FPS, 'durationInFrames': ctx.g,
          'durationExceptions': [{'shot': n, 'frames': v, 'max': MAX, 'reason': 'Knoll 帧表定稿（开场冲突＋问题句），不剪配音'} for n, v in ctx.MAX_EXC.items()],
          'style': '真网页只用于 browser 镜（1、3、4、13、14、17、19）：shop.example/search 搜索结果页与 shop.example/checkout 结算页（BrowserChrome 新页型 shopPrice：view search / checkout / success；搜索页两行商品＋加购；结算页商品、地址、红包抵扣行（hidden / shown / applied）、应付、提交订单；点击波纹）；镜 1、17 左右两扇窗口对照；讲解画面（无边框文字流程、计数、对照、片尾）一律 canvas，无外壳无网址；全片不开开发者工具；不画任何实物、不画假软件窗口，不用比喻',
          'font': 'Noto Sans SC', 'monoFont': 'Noto Sans Mono', 'palette': {'bg': '#0B1020', 'panel': '#111827', 'text': '#E5E7EB', 'muted': '#94A3B8'},
          'safeArea': {'margin': 80, 'subtitleBand': [900, 980], 'contentMaxY': 880, 'watermarkClearZone': [1680, 30, 1880, 100]},
          'poster': {'shotId': None, 'source': 'covers.poster', 'note': 'poster = 封面 3x4 构图'},
          'boxShots': ctx.BOXP, 'boxShotRule': '脚本 629b5042：方框加文字仅镜 10、11、18、20，4/20 = 20%', 'mapShots': [], 'devtoolsShots': [], 'sampleDataLabel': '示例数据',
          'uiPolicy': '通用样式，不照抄品牌界面，不点名真实电商平台、云厂商、开源库；域名只用 shop.example（RFC 2606 保留）；卫衣搜索到手价 199 元、红包抵扣 −20 元、结算应付 179 元、运动裤 129 元（背景行）、示例路 1 号、请求数 10–40 与资源 100%–40% 均为示例数据，画面上一律带（示例）',
          'chapters': ctx.chapters,
          'covers': ctx.COVERS, 'discussionQuestion': Q,
          'description': '大促时，搜索页标的到手价没算红包，加购到结算页，红包抵扣才算上，价格反而更低：算到手价要去问商品价格、优惠券和红包几个服务，人一多，搜索页一遍遍去算红包，会和结算页抢红包服务的资源。所以网站提前关掉搜索页里的红包计算，把资源留给结算页。从加购到提交订单再付款这一段叫核心链路；主动关掉不太要紧的功能、把有限资源留给核心链路，叫降级。' + Q,
          'nextEpisode': {'episode': 15, 'title': '加个索引，为啥就快了？', 'teaser': '下期，加个索引，为啥就快了？'}}


ASSETS = {'new': [], 'reuse': [], 'procedural': {'description': 'component 字段为 Knoll 组件名；新页型 shopPrice（BrowserChrome）与新属性见 knoll-props.md；沿用 ripples / backTabs / afterTabs / readAlong / dimPage / fadeOut / CornerBadge / CalloutTag / highlighted+pulse / strike / padLeft / dimFrom / rect 宽度状态；所有位置、状态帧、文字均在本文件，代码不写死'}}
