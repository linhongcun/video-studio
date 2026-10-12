# 第八期新图标：厨师、备菜台、菜盘（绿/橙）、点单、计时牌、数据库圆柱。全部自绘（可商用）、无文字
# 复用（自绘）：warehouse（第五期）、store（第五期）、counter-idle（第六期）、fridge、spinner（第七期）
import os
T=dict(bg="#0B1020",surface="#111827",s2="#1F2937",border="#243045",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",primary="#22D3EE",secondary="#3B82F6",success="#22C55E",accent="#F59E0B",danger="#F87171")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets");os.makedirs(OUT,exist_ok=True)
def svg(name,body,vb="0 0 512 512"):
    open(os.path.join(OUT,name),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{vb.split()[2]}" height="{vb.split()[3]}">\n{body}\n</svg>\n')
def dish(cx,cy,r,c): return f'<g><ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*0.42:.0f}" fill="{T["text"]}"/><ellipse cx="{cx}" cy="{cy-r*0.08:.0f}" rx="{r*0.62:.0f}" ry="{r*0.24:.0f}" fill="{c}"/></g>'
svg("chef.svg",f'''<g id="hat" fill="{T['text']}"><circle cx="200" cy="70" r="44"/><circle cx="256" cy="52" r="52"/><circle cx="312" cy="70" r="44"/><rect x="196" y="70" width="120" height="60" rx="10"/></g>
<circle id="head" cx="256" cy="170" r="56" fill="{T['accent']}"/><path id="body" d="M140 480 V310 C140 240 372 240 372 310 V480Z" fill="{T['text']}"/>
<g fill="{T['muted']}"><circle cx="256" cy="320" r="10"/><circle cx="256" cy="370" r="10"/></g>''')
svg("prep-table.svg",f'''<rect id="top" x="20" y="150" width="760" height="40" rx="12" fill="{T['text2']}"/><rect x="20" y="186" width="760" height="10" fill="{T['muted']}"/>
<g fill="{T['muted']}"><rect x="60" y="196" width="24" height="190" rx="8"/><rect x="716" y="196" width="24" height="190" rx="8"/></g><rect x="60" y="300" width="680" height="16" rx="8" fill="{T['s2']}"/>
{dish(140,130,80,T['success'])}{dish(330,130,80,T['primary'])}{dish(520,130,80,T['accent'])}{dish(690,130,64,T['success'])}''',vb="0 0 800 400")
svg("dish-green.svg",dish(256,280,220,T['success']))
svg("dish-amber.svg",dish(256,280,220,T['accent']))
svg("ticket.svg",f'<path d="M120 40 H392 V470 L360 440 L328 470 L296 440 L264 470 L232 440 L200 470 L168 440 L120 470Z" fill="{T["text"]}"/>'+"".join(f'<rect x="160" y="{100+i*70}" width="{190 if i%2 else 150}" height="24" rx="12" fill="{T["muted"]}"/>' for i in range(4)))
svg("timer.svg",f'<circle cx="256" cy="280" r="190" fill="{T["s2"]}" stroke="{T["accent"]}" stroke-width="28"/><rect x="216" y="40" width="80" height="50" rx="12" fill="{T["accent"]}"/><path d="M256 280 V170" stroke="{T["text"]}" stroke-width="26" stroke-linecap="round"/><path d="M256 280 L330 320" stroke="{T["text"]}" stroke-width="20" stroke-linecap="round"/>')
svg("db.svg",f'''<g fill="{T['secondary']}" stroke="{T['primary']}" stroke-width="10"><path d="M96 110 V400 C96 460 416 460 416 400 V110"/><ellipse cx="256" cy="110" rx="160" ry="56"/></g>
<g fill="none" stroke="{T['primary']}" stroke-width="10"><path d="M96 210 C96 270 416 270 416 210"/><path d="M96 310 C96 370 416 370 416 310"/></g>''')
print(sorted(os.listdir(OUT)))
