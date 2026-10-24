"""tiny fixture layout spec: shot 1 canvas (cue text + state change + timer), shot 2 browser (BrowserChrome + readAlong)."""
from layout_kit import C, TM, W, T, S
NSHOT = 2
BROWSER = (2,)
BOXSHOTS = ()


def sample(): return T('sample', '示例数据', 1560, 160, 32, comp='CornerBadge', color='#FDE68A', background='#7C2D12', sampleData=True)


def build(ctx):
    ctx.part(1, '大字随「你好」出现，「世界」处变色；计时器 6 帧后出小字', [
        W('panel', 'Panel', 160, 200, 1300, 600, z=0, overlayOk=True),
        T('hello', '你好世界（示例）', 200, 300, 64, cue=C('你好'), stateCues=S((C('世界'), 'lit', {'color': '#22D3EE'}))),
        T('tick', '计时', 200, 500, 40, cue=TM('你好', 6, '自测：计时器驱动')),
        sample(),
    ])
    ctx.part(2, '网页第 0 帧在场，一行字跟读', [
        W('page', 'BrowserChrome', 160, 160, 1200, 640, z=1, page='demo', url='shop.example/bye', title='再见'),
        T('line', '再见朋友。', 300, 400, 64, z=4, cue=C('再见'), reveal=ctx.reveal(2, '再见朋友。')),
        sample(),
    ])
