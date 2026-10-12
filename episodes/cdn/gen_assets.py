# 第五期新图标：总仓 / 门店 / 地图。全部手绘（本仓库自绘，可商用，无第三方授权问题）、无文字，配色沿用前几期
# 复用第三期（dns/assets，同为自绘）：phonebook.svg（查号台）、globe.svg
import os
T=dict(bg="#0B1020",surface="#111827",s2="#1F2937",border="#243045",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",primary="#22D3EE",secondary="#3B82F6",success="#22C55E",accent="#F59E0B",danger="#F87171")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets");os.makedirs(OUT,exist_ok=True)
def svg(name,body,vb="0 0 512 512"):
    open(os.path.join(OUT,name),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{vb.split()[2]}" height="{vb.split()[3]}">\n{body}\n</svg>\n')
# 总仓：大仓库，人字顶，三扇卷帘门（中间一扇可开），门前堆货箱
doors="".join(f'<g id="door{i}"><rect x="{96+i*120}" y="300" width="100" height="160" rx="6" fill="{T["s2"]}" stroke="{T["secondary"]}" stroke-width="6"/>'+"".join(f'<rect x="{106+i*120}" y="{318+j*28}" width="80" height="8" rx="4" fill="{T["muted"]}"/>' for j in range(5))+'</g>' for i in range(3))
svg("warehouse.svg",f'''<path id="roof" d="M40 200 L256 70 L472 200 Z" fill="{T['secondary']}"/>
<rect id="body" x="64" y="196" width="384" height="276" rx="10" fill="{T['surface']}" stroke="{T['primary']}" stroke-width="8"/>
<rect id="sign" x="196" y="216" width="120" height="56" rx="10" fill="{T['primary']}"/>
{doors}
<g id="boxes" fill="{T['accent']}"><rect x="20" y="420" width="44" height="44" rx="4"/><rect x="448" y="420" width="44" height="44" rx="4"/><rect x="452" y="376" width="36" height="40" rx="4"/></g>''')
# 门店：小店，条纹遮阳篷，橱窗货架（id=shelf，三层，id=goods 货品可单独隐去表示“没货”），门
goods="".join(f'<rect x="{300+c*40}" y="{262+r*60}" width="28" height="36" rx="4" fill="{[T["primary"],T["accent"],T["success"]][r]}"/>' for r in range(3) for c in range(3))
svg("store.svg",f'''<rect id="wall" x="64" y="176" width="384" height="300" rx="10" fill="{T['surface']}" stroke="{T['primary']}" stroke-width="8"/>
<g id="awning">{"".join(f'<path d="M{48+i*69} 120 h69 v56 q-34.5 34 -69 0z" fill="{[T["secondary"],T["text"]][i%2]}"/>' for i in range(6))}</g>
<rect id="door" x="104" y="268" width="130" height="208" rx="8" fill="{T['s2']}" stroke="{T['secondary']}" stroke-width="6"/><circle cx="210" cy="376" r="9" fill="{T['text2']}"/>
<g id="shelf"><rect x="280" y="236" width="140" height="196" rx="8" fill="{T['bg']}" stroke="{T['secondary']}" stroke-width="6"/>{"".join(f'<rect x="286" y="{298+r*60}" width="128" height="6" fill="{T["muted"]}"/>' for r in range(3))}</g>
<g id="goods">{goods}</g>''')
# 门店（空货架版）：同 store.svg，但没有 goods（第五章“没货”）
svg("store-empty.svg",open(os.path.join(OUT,"store.svg")).read().split('\n',1)[1].rsplit('<g id="goods">',1)[0].rstrip())
# 地图：抽象陆块 + 海洋网格，宽幅 1600×560，不画国界、不标地名（地名由分镜文字层叠加）
svg("map.svg",f'''<rect id="sea" x="0" y="0" width="1600" height="560" rx="28" fill="{T['surface']}" stroke="{T['border']}" stroke-width="4"/>
<g id="grid" stroke="{T['border']}" stroke-width="2">{"".join(f'<path d="M{x} 20 V540"/>' for x in range(160,1600,160))}{"".join(f'<path d="M20 {y} H1580"/>' for y in range(112,560,112))}</g>
<g id="land" fill="{T['s2']}" stroke="{T['muted']}" stroke-width="3">
<path d="M40 90 q120 -60 260 -30 q120 30 150 110 q10 90 -60 140 q-40 80 -140 90 q-120 0 -170 -80 q-60 -120 -40 -230z"/>
<path d="M330 360 q60 -20 100 30 q20 60 -30 110 q-60 20 -80 -40z"/>
<path d="M1180 70 q160 -40 300 20 q80 70 50 170 q-40 90 -130 140 q-90 40 -160 -30 q-60 -80 -100 -150 q-10 -100 40 -150z"/>
<path d="M1420 400 q60 0 90 40 q0 60 -60 80 q-50 -10 -50 -60z"/></g>''',vb="0 0 1600 560")
# 卡车（总仓→门店送货）
svg("truck.svg",f'''<rect id="box" x="32" y="150" width="300" height="200" rx="14" fill="{T['accent']}"/>
<path id="cab" d="M340 210 h90 l60 70 v70 h-150z" fill="{T['secondary']}"/><path d="M362 226 h58 l40 50 h-98z" fill="{T['bg']}"/>
<g id="wheels" fill="{T['s2']}" stroke="{T['text2']}" stroke-width="10"><circle cx="110" cy="368" r="40"/><circle cx="400" cy="368" r="40"/></g>''')
print(sorted(os.listdir(OUT)))
