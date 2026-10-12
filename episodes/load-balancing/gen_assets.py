# 第六期新图标：导购 / 柜台（空闲·忙·休息）/ 客人 / 排队 / 健康检查。全部自绘（可商用，无第三方授权）、无文字，配色沿用前几期
# 复用第五期（cdn/assets，自绘）：store.svg、map.svg、warehouse.svg
import os
T=dict(bg="#0B1020",surface="#111827",s2="#1F2937",border="#243045",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",primary="#22D3EE",secondary="#3B82F6",success="#22C55E",accent="#F59E0B",danger="#F87171")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets");os.makedirs(OUT,exist_ok=True)
def svg(name,body,vb="0 0 512 512"):
    open(os.path.join(OUT,name),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{vb.split()[2]}" height="{vb.split()[3]}">\n{body}\n</svg>\n')
def person(x,y,s,c):  # 简笔客人：圆头 + 圆角身体
    return f'<g><circle cx="{x}" cy="{y}" r="{28*s}" fill="{c}"/><path d="M{x-44*s} {y+120*s} C{x-44*s} {y+52*s} {x+44*s} {y+52*s} {x+44*s} {y+120*s} Z" fill="{c}"/></g>'
# 导购：站立人物，胸前圆形徽章，右手平伸指路
svg("greeter.svg",f'''<g id="body" fill="{T['secondary']}"><circle cx="220" cy="120" r="64"/><path d="M120 470 V290 C120 220 320 220 320 290 V470 Z"/></g>
<rect id="vest" x="170" y="250" width="100" height="220" rx="20" fill="{T['primary']}"/>
<circle id="badge" cx="220" cy="300" r="22" fill="{T['accent']}"/>
<g id="arm"><path d="M300 280 L440 230" stroke="{T['secondary']}" stroke-width="40" stroke-linecap="round"/><circle cx="452" cy="226" r="26" fill="{T['text']}"/></g>''')
# 柜台：桌台 + 收银屏 + 状态灯（idle 绿 / busy 橙红+单据堆 / closed 灰+卷帘）
def counter(name,lamp,extra="",desk=T['surface'],stroke=T['primary']):
    svg(name,f'''<rect id="screen" x="300" y="120" width="140" height="110" rx="12" fill="{T['s2']}" stroke="{stroke}" stroke-width="6"/><rect x="356" y="230" width="28" height="50" fill="{T['muted']}"/>
<rect id="desk" x="48" y="280" width="416" height="180" rx="16" fill="{desk}" stroke="{stroke}" stroke-width="8"/><rect x="48" y="280" width="416" height="36" rx="12" fill="{stroke}"/>
<circle id="lamp" cx="120" cy="190" r="44" fill="{lamp}"/>{extra}''')
counter("counter-idle.svg",T['success'])
counter("counter-busy.svg",T['danger'],extra="".join(f'<rect x="{190+i*6}" y="{214-i*22}" width="80" height="18" rx="4" fill="{T["accent"]}"/>' for i in range(4)))
counter("counter-closed.svg",T['muted'],desk=T['s2'],stroke=T['muted'],extra=f'<g id="shutter">'+"".join(f'<rect x="64" y="{330+i*28}" width="384" height="14" rx="6" fill="{T["muted"]}"/>' for i in range(4))+'</g>')
svg("person.svg",person(256,150,2.2,T['text2']))
svg("queue.svg","".join(person(90+i*190,90,1.15,[T['text2'],T['primary'],T['text2'],T['accent'],T['text2']][i]) for i in range(5)),vb="0 0 1000 260")
# 健康检查：心形 + 心电折线
svg("health.svg",f'''<path id="heart" d="M256 456 C120 360 48 280 48 190 C48 120 104 72 168 72 C208 72 240 96 256 128 C272 96 304 72 344 72 C408 72 464 120 464 190 C464 280 392 360 256 456Z" fill="{T['success']}"/>
<path id="pulse" d="M88 250 H190 L220 190 L260 320 L296 230 L318 250 H424" fill="none" stroke="{T['bg']}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>''')
print(sorted(os.listdir(OUT)))
