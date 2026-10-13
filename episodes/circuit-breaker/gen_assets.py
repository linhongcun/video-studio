# 第十二期新图标（自绘、可商用、无文字）：电闸箱（全合 / 一路跳闸）、单个空气开关（合 / 断）、火花、空调、台灯、插座、电表
# 复用（自绘）：phone / phone-busy / ticket / server（第十一期）、gate（第十期）、queue / guest（第九期）、fridge（第七期）、timer（第八期）、hourglass（第三期 DNS）
import os
T=dict(bg="#0B1020",s2="#1F2937",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",primary="#22D3EE",secondary="#3B82F6",success="#22C55E",accent="#F59E0B",danger="#F87171")
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets");os.makedirs(OUT,exist_ok=True)
def svg(n,b,vb="0 0 512 512"): open(os.path.join(OUT,n),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{vb.split()[2]}" height="{vb.split()[3]}">\n{b}\n</svg>\n')
def sw(x,y,on=True,c=None):  # 一个空气开关：外壳 + 拨杆（上 = 合，下 = 断）+ 指示灯
    c=c or (T["success"] if on else T["danger"])
    lever=f'<rect x="{x+22}" y="{y+40 if on else y+120}" width="46" height="70" rx="10" fill="{T["text"]}"/>'
    return f'<rect x="{x}" y="{y}" width="90" height="230" rx="12" fill="{T["s2"]}" stroke="{c}" stroke-width="8"/><rect x="{x+18}" y="{y+30}" width="54" height="170" rx="10" fill="{T["bg"]}"/>'+lever+f'<circle cx="{x+45}" cy="{y+214}" r="9" fill="{c}"/>'
box=lambda inner:f'<rect x="20" y="40" width="472" height="432" rx="26" fill="#111827" stroke="{T["text2"]}" stroke-width="12"/><rect x="50" y="70" width="412" height="40" rx="10" fill="{T["muted"]}"/>'+inner+f'<rect x="50" y="400" width="412" height="40" rx="10" fill="{T["muted"]}"/>'
svg("breaker-box.svg",box("".join(sw(56+i*102,140) for i in range(4))))
svg("breaker-tripped.svg",box("".join(sw(56+i*102,140,on=(i!=3)) for i in range(4))+f'<path d="M420 120 L440 92 L452 118 L476 96" stroke="{T["accent"]}" stroke-width="10" fill="none" stroke-linecap="round"/>'))
svg("switch-on.svg",sw(4,4),vb="0 0 98 238")
svg("switch-off.svg",sw(4,4,on=False),vb="0 0 98 238")
svg("spark.svg",f'<path d="M256 40 L300 200 L460 150 L330 270 L430 430 L256 330 L110 450 L180 280 L50 180 L210 200 Z" fill="{T["accent"]}"/><path d="M256 140 L280 230 L360 210 L300 270 L340 340 L256 300 L190 350 L220 280 L160 230 L236 230 Z" fill="#FDE68A"/>')
svg("aircon.svg",f'<rect x="30" y="140" width="452" height="190" rx="30" fill="{T["text"]}"/><rect x="60" y="270" width="392" height="18" rx="9" fill="{T["muted"]}"/><circle cx="420" cy="185" r="12" fill="{T["success"]}"/><path d="M120 360 C110 400 140 420 120 460 M256 360 C246 400 276 420 256 460 M392 360 C382 400 412 420 392 460" stroke="{T["primary"]}" stroke-width="16" fill="none" stroke-linecap="round"/>')
svg("lamp.svg",f'<path d="M150 60 H362 L420 240 H92 Z" fill="{T["accent"]}"/><rect x="240" y="240" width="32" height="190" fill="{T["text2"]}"/><rect x="150" y="430" width="212" height="40" rx="12" fill="{T["text2"]}"/>')
svg("socket.svg",f'<rect x="76" y="76" width="360" height="360" rx="50" fill="{T["text"]}"/><rect x="186" y="170" width="28" height="90" rx="10" fill="{T["bg"]}"/><rect x="298" y="170" width="28" height="90" rx="10" fill="{T["bg"]}"/><circle cx="256" cy="340" r="26" fill="{T["bg"]}"/>')
svg("meter.svg",f'<path d="M60 340 A196 196 0 0 1 452 340" fill="none" stroke="{T["s2"]}" stroke-width="56"/><path d="M60 340 A196 196 0 0 1 256 144" fill="none" stroke="{T["success"]}" stroke-width="56"/><path d="M256 144 A196 196 0 0 1 395 201" fill="none" stroke="{T["accent"]}" stroke-width="56"/><path d="M395 201 A196 196 0 0 1 452 340" fill="none" stroke="{T["danger"]}" stroke-width="56"/><path d="M256 340 L400 230" stroke="{T["text"]}" stroke-width="18" stroke-linecap="round"/><circle cx="256" cy="340" r="30" fill="{T["text"]}"/><rect x="60" y="400" width="392" height="40" rx="12" fill="{T["muted"]}"/>')
