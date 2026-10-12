# 第四期新图标：手牌 / 存包柜 / 小偷。全部手绘、无文字，配色沿用前几期
import os
T=dict(bg="#0B1020",surface="#111827",s2="#1F2937",border="#243045",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",primary="#22D3EE",secondary="#3B82F6",success="#22C55E",accent="#F59E0B",danger="#F87171")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets");os.makedirs(OUT,exist_ok=True)
def svg(name,body,vb="0 0 512 512"):
    open(os.path.join(OUT,name),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{vb.split()[2]}" height="{vb.split()[3]}">\n{body}\n</svg>\n')
# 手牌：橙色圆角牌，顶部穿绳孔+挂绳，中间一块深色“编号区”（编号由 storyboard 文字层叠加，不画进图标）
svg("tag.svg",f'''<path id="string" d="M256 20 C200 20 190 70 236 96" fill="none" stroke="{T['text2']}" stroke-width="10" stroke-linecap="round"/>
<rect id="body" x="96" y="80" width="320" height="400" rx="40" fill="{T['accent']}"/>
<circle id="hole" cx="256" cy="130" r="22" fill="{T['bg']}"/>
<rect id="numArea" x="136" y="210" width="240" height="120" rx="16" fill="{T['bg']}"/>
<g id="numBars" fill="{T['accent']}"><rect x="160" y="252" width="40" height="36" rx="6"/><rect x="216" y="252" width="40" height="36" rx="6"/><rect x="272" y="252" width="40" height="36" rx="6"/><rect x="328" y="252" width="24" height="36" rx="6"/></g>
<rect id="stripe" x="136" y="370" width="240" height="20" rx="10" fill="#B45309"/>''')
# 存包柜：3×3 格，每格有把手，中间一格门打开（id=openDoor）露出里面的包（id=bag）
cells="".join(f'<g id="cell{r*3+c}"><rect x="{56+c*140}" y="{56+r*140}" width="120" height="120" rx="12" fill="{T["s2"]}" stroke="{T["secondary"]}" stroke-width="6"/><rect x="{56+c*140+92}" y="{56+r*140+48}" width="12" height="28" rx="6" fill="{T["text2"]}"/></g>' for r in range(3) for c in range(3) if (r,c)!=(1,1))
svg("locker.svg",f'''<rect id="frame" x="36" y="36" width="440" height="440" rx="24" fill="{T['surface']}" stroke="{T['primary']}" stroke-width="8"/>
{cells}
<g id="openCell"><rect x="196" y="196" width="120" height="120" rx="12" fill="{T['bg']}" stroke="{T['secondary']}" stroke-width="6"/>
<path id="bag" d="M222 300 V248 Q256 232 290 248 V300Z" fill="{T['primary']}"/><path d="M240 246 Q256 222 272 246" fill="none" stroke="{T['primary']}" stroke-width="8"/></g>
<path id="openDoor" d="M196 196 L160 212 V300 L196 316Z" fill="{T['s2']}" stroke="{T['secondary']}" stroke-width="6"/>''')
# 小偷：沿用第二期 eavesdropper 剪影（灰身、深色帽、红眼），加黑色眼罩条和伸出的手
svg("thief.svg",f'''<g id="figure" fill="{T['muted']}"><circle cx="230" cy="170" r="88"/><path d="M70 470 C70 340 144 284 230 284 C316 284 390 340 390 470 Z"/>
<path d="M124 150 C134 80 326 80 336 150 L374 160 L86 160 Z" fill="{T['s2']}"/></g>
<rect id="mask" x="150" y="172" width="160" height="40" rx="20" fill="{T['s2']}"/>
<g id="eyes"><ellipse cx="200" cy="192" rx="16" ry="9" fill="{T['danger']}"/><ellipse cx="262" cy="192" rx="16" ry="9" fill="{T['danger']}"/></g>
<g id="hand"><path d="M350 340 L452 296" stroke="{T['muted']}" stroke-width="40" stroke-linecap="round"/><circle cx="460" cy="292" r="30" fill="{T['muted']}"/></g>''')
print(sorted(os.listdir(OUT)))
