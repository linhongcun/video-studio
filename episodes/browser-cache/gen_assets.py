# 第七期新图标：冰箱（关/开）、图片块、货包（四色）、保质期标签、转圈、笔记本电脑、购物车。全部自绘（可商用）、无文字
# 复用第五、六期（自绘）：store.svg、counter-idle.svg、person.svg
import os
T=dict(bg="#0B1020",surface="#111827",s2="#1F2937",border="#243045",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",primary="#22D3EE",secondary="#3B82F6",success="#22C55E",accent="#F59E0B",danger="#F87171")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets");os.makedirs(OUT,exist_ok=True)
def svg(name,body,vb="0 0 512 512"):
    open(os.path.join(OUT,name),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{vb.split()[2]}" height="{vb.split()[3]}">\n{body}\n</svg>\n')
def box(x,y,w,h,c):  # 货包：纸箱 + 封条
    return f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w*0.08:.0f}" fill="{c}"/><rect x="{x+w*0.42:.0f}" y="{y}" width="{w*0.16:.0f}" height="{h}" fill="{T["bg"]}" opacity="0.35"/><rect x="{x}" y="{y+h*0.18:.0f}" width="{w}" height="{h*0.08:.0f}" fill="{T["bg"]}" opacity="0.25"/></g>'
FR=f'<rect id="body" x="116" y="24" width="280" height="464" rx="28" fill="{T["text2"]}" stroke="{T["primary"]}" stroke-width="8"/><rect x="116" y="176" width="280" height="8" fill="{T["muted"]}"/>'
svg("fridge.svg",FR+f'<g id="handles" fill="{T["s2"]}"><rect x="352" y="80" width="16" height="70" rx="8"/><rect x="352" y="214" width="16" height="110" rx="8"/></g>')
svg("fridge-open.svg",f'''<rect id="body" x="60" y="24" width="300" height="464" rx="24" fill="{T['s2']}" stroke="{T['primary']}" stroke-width="8"/>
<rect id="inner" x="84" y="48" width="252" height="416" rx="12" fill="#E0F2FE"/><g fill="{T['text2']}"><rect x="84" y="176" width="252" height="8"/><rect x="84" y="316" width="252" height="8"/></g>
{box(104,110,64,62,T['primary'])}{box(196,110,64,62,T['secondary'])}{box(104,250,64,62,T['success'])}{box(196,392,90,68,T['accent'])}
<path id="door" d="M360 24 L470 60 V452 L360 488 Z" fill="{T['text2']}" stroke="{T['primary']}" stroke-width="8"/><rect x="380" y="200" width="14" height="110" rx="7" fill="{T['s2']}"/>''')
svg("photo.svg",f'<rect x="16" y="16" width="480" height="320" rx="24" fill="{T["s2"]}" stroke="{T["secondary"]}" stroke-width="8"/><circle cx="380" cy="100" r="40" fill="{T["accent"]}"/><path d="M40 320 L190 150 L290 260 L350 200 L472 320 Z" fill="{T["success"]}"/>',vb="0 0 512 352")
for n,c in (("box-cyan",T['primary']),("box-blue",T['secondary']),("box-green",T['success']),("box-amber",T['accent'])): svg(n+".svg",box(56,96,400,340,c))
svg("tag.svg",f'''<path id="tag" d="M40 160 L200 40 H460 V300 H200 Z" fill="{T['success']}"/><circle cx="150" cy="170" r="26" fill="{T['bg']}"/>
<circle id="clock" cx="330" cy="170" r="88" fill="{T['bg']}"/><path d="M330 110 V170 L372 196" fill="none" stroke="{T['success']}" stroke-width="18" stroke-linecap="round"/>''',vb="0 0 512 340")
svg("spinner.svg",f'<circle cx="256" cy="256" r="180" fill="none" stroke="{T["muted"]}" stroke-width="40"/><path d="M256 76 A180 180 0 0 1 436 256" fill="none" stroke="{T["primary"]}" stroke-width="40" stroke-linecap="round"/>')
svg("laptop.svg",f'<rect x="96" y="80" width="320" height="220" rx="16" fill="{T["s2"]}" stroke="{T["primary"]}" stroke-width="10"/><path d="M40 320 H472 L440 380 H72 Z" fill="{T["text2"]}"/>')
svg("cart.svg",f'<path d="M40 80 H120 L170 330 H420 L460 150 H140" fill="none" stroke="{T["primary"]}" stroke-width="28" stroke-linejoin="round" stroke-linecap="round"/><circle cx="200" cy="400" r="34" fill="{T["text2"]}"/><circle cx="390" cy="400" r="34" fill="{T["text2"]}"/>{box(200,180,90,110,T["accent"])}{box(300,200,90,90,T["secondary"])}')
print(sorted(os.listdir(OUT)))
