# 第三期新图标：全部手绘、无文字，配色沿用第二期
import os
T=dict(bg="#0B1020",surface="#111827",s2="#1F2937",border="#243045",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",primary="#22D3EE",secondary="#3B82F6",success="#22C55E",accent="#F59E0B",danger="#F87171")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets");os.makedirs(OUT,exist_ok=True)
def svg(name,body,vb="0 0 512 512"):
    open(os.path.join(OUT,name),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{vb.split()[2]}" height="{vb.split()[3]}">\n{body}\n</svg>\n')
lines=lambda x0,x1,ys,c:"".join(f'<rect x="{x0}" y="{y}" width="{x1-x0}" height="12" rx="6" fill="{c}"/>' for y in ys)
# 电话簿：翻开的厚书，左页“名字”行（青）、右页“号码”行（橙），书脊居中
svg("phonebook.svg",f'''<g id="cover"><rect x="24" y="96" width="464" height="340" rx="24" fill="{T['secondary']}"/></g>
<g id="pageL"><path d="M48 112 Q150 92 252 120 V420 Q150 396 48 412Z" fill="{T['text']}"/>{lines(84,220,[160,200,240,280,320,360],T['primary'])}</g>
<g id="pageR"><path d="M260 120 Q362 92 464 112 V412 Q362 396 260 420Z" fill="{T['text']}"/>{lines(292,428,[160,200,240,280,320,360],T['accent'])}</g>
<rect id="spine" x="250" y="112" width="12" height="312" rx="6" fill="{T['s2']}"/>''')
# 小本子：竖版线圈本，带书签，右下打勾位
svg("notebook.svg",f'''<rect id="cover" x="112" y="56" width="300" height="400" rx="24" fill="{T['primary']}"/>
<rect id="page" x="140" y="84" width="248" height="344" rx="14" fill="{T['text']}"/>
<g id="rings" fill="none" stroke="{T['s2']}" stroke-width="12" stroke-linecap="round">{"".join(f'<path d="M100 {y} h56"/>' for y in (120,190,260,330,400))}</g>
{lines(184,356,[140,190,240,290],T['muted'])}
<path id="bookmark" d="M330 56 v110 l24 -20 l24 20 v-110z" fill="{T['accent']}"/>
<path id="check" d="M196 360 l36 36 l72 -80" fill="none" stroke="{T['success']}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>''')
# hosts 便签：黄色方形便签，折角，顶部胶带
svg("hosts-note.svg",f'''<path id="paper" d="M88 88 H424 V352 L344 432 H88Z" fill="{T['accent']}"/>
<path id="fold" d="M424 352 L344 352 L344 432Z" fill="#B45309"/>
<rect id="tape" x="196" y="60" width="120" height="48" rx="6" fill="{T['text2']}" opacity="0.85"/>
{lines(128,384,[168,228,288],T['bg'])}''')
# 沙漏（TTL）：上沙 id=sand-top、下沙 id=sand-bottom、细流 id=stream，Knoll 用 drain 0→1 驱动
svg("hourglass.svg",f'''<rect id="capTop" x="116" y="40" width="280" height="36" rx="14" fill="{T['secondary']}"/>
<rect id="capBottom" x="116" y="436" width="280" height="36" rx="14" fill="{T['secondary']}"/>
<path id="glass" d="M150 76 H362 C362 180 282 220 268 256 C282 292 362 332 362 436 H150 C150 332 230 292 244 256 C230 220 150 180 150 76Z" fill="{T['surface']}" stroke="{T['primary']}" stroke-width="10"/>
<path id="sand-top" d="M176 120 H336 C330 180 270 214 256 246 C242 214 182 180 176 120Z" fill="{T['accent']}"/>
<rect id="stream" x="251" y="246" width="10" height="150" fill="{T['accent']}"/>
<path id="sand-bottom" d="M178 420 C200 380 312 380 334 420Z" fill="{T['accent']}"/>''')
# 地球：经纬线，配色 secondary/primary
svg("globe.svg",f'''<circle id="earth" cx="256" cy="256" r="210" fill="{T['s2']}" stroke="{T['primary']}" stroke-width="10"/>
<g fill="{T['secondary']}" opacity="0.9"><path d="M120 170 q40 -50 110 -30 q30 40 -10 70 q-50 10 -60 50 q-40 -30 -40 -90z"/><path d="M290 130 q60 -10 100 40 q-10 50 -60 40 q-40 20 -50 -20z"/><path d="M270 280 q70 -10 90 50 q-30 70 -80 60 q-20 -50 -10 -110z"/><path d="M150 300 q40 0 50 40 q-20 40 -50 30z"/></g>
<g fill="none" stroke="{T['primary']}" stroke-width="4" opacity="0.6"><ellipse cx="256" cy="256" rx="90" ry="210"/><path d="M46 256 H466"/><path d="M76 160 H436"/><path d="M76 352 H436"/></g>''')
# 任播点：叠在 globe.svg 上的许多小亮点（不标数量，示意“许多台机器”）
import random;random.seed(3);pts=[]
while len(pts)<70:
    x,y=random.uniform(60,452),random.uniform(60,452)
    if (x-256)**2+(y-256)**2<190**2: pts.append((x,y))
svg("anycast-dots.svg",f'<g id="dots" fill="{T["accent"]}">'+"".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9"/>' for x,y in pts)+'</g>')
print(sorted(os.listdir(OUT)))
