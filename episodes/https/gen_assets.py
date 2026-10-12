import os,re
T=dict(bg="#0B1020",surface="#111827",s2="#1F2937",border="#243045",text="#E5E7EB",text2="#9CA3AF",muted="#6B7280",primary="#22D3EE",secondary="#3B82F6",success="#22C55E",accent="#F59E0B",danger="#F87171")
F='font-family="system-ui, -apple-system, \'PingFang SC\', \'Noto Sans CJK SC\', sans-serif"'
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"assets")
os.makedirs(OUT,exist_ok=True)
def svg(name,vb,body):
    open(os.path.join(OUT,name),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{vb.split()[2]}" height="{vb.split()[3]}">\n{body}\n</svg>\n')
def key(c,stroke,x=0,y=0,id="key",teeth=True):
    return f'''<g id="{id}" transform="translate({x} {y})">
 <circle cx="140" cy="256" r="84" fill="{c}"/><circle cx="140" cy="256" r="34" fill="{T['bg']}"/>
 <rect x="210" y="232" width="230" height="48" rx="10" fill="{c}"/>
 {'<rect x="350" y="276" width="30" height="56" rx="6" fill="%s"/><rect x="400" y="276" width="30" height="40" rx="6" fill="%s"/>'%(c,c) if teeth else ''}
 <circle cx="140" cy="256" r="84" fill="none" stroke="{stroke}" stroke-width="6"/></g>'''
def lock(open_):
    shackle = ('<path id="shackle" d="M176 250 V150 a80 80 0 0 1 160 0 V170" fill="none" stroke="%s" stroke-width="36" stroke-linecap="round" transform="translate(0 -40)"/>'%T['text2']) if open_ else ('<path id="shackle" d="M176 250 V170 a80 80 0 0 1 160 0 V250" fill="none" stroke="%s" stroke-width="36" stroke-linecap="round"/>'%T['text'])
    bodyc = T['muted'] if open_ else T['primary']
    return f'''{shackle}
<g id="body"><rect x="116" y="236" width="280" height="220" rx="32" fill="{bodyc}"/>
<circle cx="256" cy="326" r="26" fill="{T['bg']}"/><rect x="244" y="330" width="24" height="64" rx="10" fill="{T['bg']}"/></g>'''
svg("padlock-open.svg","0 0 512 512",lock(True))
svg("padlock-closed.svg","0 0 512 512",lock(False))
svg("key-symmetric.svg","0 0 512 512",key(T['accent'],"#FCD34D".replace("#FCD34D",T['accent'])) )
svg("keypair-public.svg","0 0 512 512",key(T['primary'],T['primary'],id="public-key")+f'<g id="tag"><circle cx="140" cy="256" r="18" fill="{T["primary"]}"/></g><text x="325" y="200" text-anchor="middle" {F} font-size="54" font-weight="700" fill="{T["primary"]}">公钥</text>')
svg("keypair-private.svg","0 0 512 512",key(T['s2'],T['secondary'],id="private-key")+f'<g fill="none" stroke="{T["secondary"]}" stroke-width="6"><rect x="210" y="232" width="230" height="48" rx="10"/><rect x="350" y="276" width="30" height="56" rx="6"/><rect x="400" y="276" width="30" height="40" rx="6"/></g><g id="shield"><path d="M140 222 l30 12 v20 c0 22 -14 36 -30 42 c-16 -6 -30 -20 -30 -42 v-20z" fill="{T["secondary"]}"/></g><text x="325" y="200" text-anchor="middle" {F} font-size="54" font-weight="700" fill="{T["secondary"]}">私钥</text>')
env_base=f'<rect id="paper" x="56" y="136" width="400" height="260" rx="20" fill="{T["surface"]}" stroke="{T["text2"]}" stroke-width="8"/>'
svg("envelope.svg","0 0 512 512",f'''<g id="letter"><rect x="116" y="56" width="280" height="250" rx="14" fill="{T['text']}"/>
<rect x="150" y="100" width="212" height="16" rx="8" fill="{T['muted']}"/><rect x="150" y="140" width="180" height="16" rx="8" fill="{T['muted']}"/><rect x="150" y="180" width="200" height="16" rx="8" fill="{T['muted']}"/></g>
<path id="flap-open" d="M56 196 L256 60 L456 196" fill="{T['s2']}" stroke="{T['text2']}" stroke-width="8" stroke-linejoin="round" opacity="0"/>
<rect x="56" y="196" width="400" height="220" rx="20" fill="{T['surface']}" stroke="{T['text2']}" stroke-width="8"/>
<path d="M60 206 L256 330 L452 206" fill="none" stroke="{T['text2']}" stroke-width="8" stroke-linejoin="round"/>''')
svg("envelope-sealed.svg","0 0 512 512",f'''{env_base}
<path id="flap" d="M60 146 L256 286 L452 146" fill="{T['s2']}" stroke="{T['text2']}" stroke-width="8" stroke-linejoin="round"/>
<g id="seal"><circle cx="256" cy="286" r="46" fill="{T['accent']}"/><circle cx="256" cy="286" r="30" fill="none" stroke="{T['bg']}" stroke-width="6"/>
<path d="M240 286 l12 12 l22 -24" fill="none" stroke="{T['bg']}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></g>
<g id="tamper-strip"><rect x="56" y="370" width="400" height="18" fill="{T['success']}" opacity="0.9"/></g>''')
svg("certificate.svg","0 0 720 512",f'''<rect id="paper" x="40" y="40" width="640" height="400" rx="20" fill="{T['surface']}" stroke="{T['primary']}" stroke-width="6"/>
<rect x="64" y="64" width="592" height="352" rx="12" fill="none" stroke="{T['border']}" stroke-width="4"/>
<text x="100" y="130" {F} font-size="34" font-weight="700" fill="{T['text']}">TLS 证书</text>
<text x="100" y="176" {F} font-size="30" fill="{T['text2']}">颁发给</text>
<text id="domain" x="100" y="226" {F} font-size="40" font-weight="700" fill="{T['primary']}">example.com</text>
<text x="100" y="286" {F} font-size="30" fill="{T['text2']}">公钥</text>
<g id="pubkey-chip"><rect x="180" y="258" width="200" height="34" rx="17" fill="{T['s2']}"/><circle cx="202" cy="275" r="9" fill="{T['primary']}"/><rect x="218" y="270" width="140" height="10" rx="5" fill="{T['primary']}"/></g>
<rect x="100" y="330" width="260" height="10" rx="5" fill="{T['muted']}"/><rect x="100" y="356" width="200" height="10" rx="5" fill="{T['muted']}"/>
<g id="ribbon"><path d="M520 370 l-30 110 l34 -20 l20 34 l24 -110z M600 370 l30 110 l-34 -20 l-20 34 l-24 -110z" fill="{T['accent']}"/></g>
<g id="seal"><circle cx="560" cy="330" r="70" fill="{T['accent']}"/><circle cx="560" cy="330" r="52" fill="none" stroke="{T['bg']}" stroke-width="5" stroke-dasharray="6 6"/>
<text x="560" y="344" text-anchor="middle" {F} font-size="40" font-weight="800" fill="{T['bg']}">CA</text></g>''')
svg("ca-badge.svg","0 0 512 512",f'''<g id="badge"><path d="M256 40 L430 104 V250 C430 360 352 432 256 472 C160 432 82 360 82 250 V104 Z" fill="{T['surface']}" stroke="{T['accent']}" stroke-width="14" stroke-linejoin="round"/>
<path d="M256 92 L384 140 V250 C384 330 328 386 256 418 C184 386 128 330 128 250 V140 Z" fill="{T['accent']}"/></g>
<text x="256" y="248" text-anchor="middle" {F} font-size="132" font-weight="800" fill="{T['bg']}">CA</text>
<path id="check" d="M196 334 l40 40 l84 -84" fill="none" stroke="{T['bg']}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>''')
svg("eavesdropper.svg","0 0 512 512",f'''<g id="figure" fill="{T['muted']}"><circle cx="256" cy="170" r="88"/><path d="M96 470 C96 340 170 284 256 284 C342 284 416 340 416 470 Z"/>
<path d="M150 150 C160 80 352 80 362 150 L400 160 L112 160 Z" fill="{T['s2']}"/></g>
<g id="eyes"><ellipse cx="222" cy="190" rx="18" ry="10" fill="{T['danger']}"/><ellipse cx="290" cy="190" rx="18" ry="10" fill="{T['danger']}"/></g>''')
def blob(cx,cy,r,c,id): return f'<circle id="{id}" cx="{cx}" cy="{cy}" r="{r}" fill="{c}"/>'
lbl=lambda x,y,s,c,sz=26: f'<text x="{x}" y="{y}" text-anchor="middle" {F} font-size="{sz}" font-weight="600" fill="{c}">{s}</text>'
arrow=lambda x1,y1,x2,y2,c: f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{c}" stroke-width="6" stroke-linecap="round" marker-end="url(#ah)"/>'
def ecdhe(step):
    L=lambda x,y,t,c,sz=38: lbl(x,y,t,c,max(sz,38))
    parts=[f'<defs><marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="{T['text2']}"/></marker></defs>',
      L(260,70,"浏览器",T['text'],48)+L(1340,70,"服务器",T['text'],48)]
    if step>=1: parts.append(f'<g id="shared-param">{blob(800,170,70,T["primary"],"param")}{L(800,285,"公开参数",T["text2"])}</g>')
    if step>=2: parts.append(f'<g id="left-secret">{blob(110,400,60,T["danger"],"a-secret")}{L(110,505,"浏览器私有",T["text2"])}</g><g id="right-secret">{blob(1490,400,60,T["success"],"b-secret")}{L(1490,505,"服务器私有",T["text2"])}</g>')
    if step>=3: parts.append(f'<g id="mix" stroke="{T["muted"]}" stroke-width="4" stroke-dasharray="8 8" fill="none"><path d="M740 200 L450 350"/><path d="M860 200 L1150 350"/></g><g id="left-public">{blob(390,400,64,T["secondary"],"a-pub")}<circle cx="390" cy="400" r="64" fill="{T["danger"]}" opacity="0.45"/>{L(390,510,"浏览器公开值",T["text2"])}</g><g id="right-public">{blob(1210,400,64,T["secondary"],"b-pub")}<circle cx="1210" cy="400" r="64" fill="{T["success"]}" opacity="0.45"/>{L(1210,510,"服务器公开值",T["text2"])}</g>')
    if step>=4: parts.append(f'<g id="exchange" stroke-dasharray="14 12">{arrow(470,390,1120,390,T["text2"])}{arrow(1130,440,480,440,T["text2"])}</g>'+L(800,370,"只交换公开值",T["text2"],40))
    if step>=5: parts.append(f'<g id="eve"><circle cx="800" cy="540" r="36" fill="{T["muted"]}"/><path d="M745 630 C745 588 855 588 855 630Z" fill="{T["muted"]}"/>{L(800,690,"偷听者算不出",T["danger"],40)}</g>')
    if step>=6: parts.append(f'<g id="left-derive">{arrow(260,560,260,600,T["text2"])}{blob(260,770,80,T["accent"],"left-key")}</g><g id="right-derive">{arrow(1340,560,1340,600,T["text2"])}{blob(1340,770,80,T["accent"],"right-key")}</g>'+L(800,785,"= 同一把会话密钥 =",T["accent"],48))
    return "\n".join(parts)
svg("ecdhe-mix.svg","0 0 1600 900",ecdhe(6))
for n in range(1,7): svg(f"ecdhe-step{n}.svg","0 0 1600 900",f'<rect width="1600" height="900" fill="{T["bg"]}"/>'+ecdhe(n))
def combine():
    L=lambda x,y,t,c,sz=38: lbl(x,y,t,c,sz)
    def side(cx,recv,own,rl,ol):
        return (f'{blob(cx-180,330,64,T["secondary"],"r")}<circle cx="{cx-180}" cy="330" r="64" fill="{recv}" opacity="0.45"/>'+L(cx-180,450,rl,T["text2"])
          +L(cx,345,"+",T["text"],64)+blob(cx+180,330,60,own,"o")+L(cx+180,450,ol,T["text2"])
          +arrow(cx,500,cx,600,T["text2"])+blob(cx,700,80,T["accent"],"k")+L(cx,830,"算出会话密钥",T["accent"],40))
    return (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="{T['text2']}"/></marker></defs><rect width="1600" height="900" fill="{T["bg"]}"/>'
      +L(400,90,"浏览器",T['text'],48)+L(1200,90,"服务器",T['text'],48)+f'<path d="M800 140 V840" stroke="{T["border"]}" stroke-width="4" stroke-dasharray="10 10"/>'
      +f'<g id="left-combine">{side(400,T["success"],T["danger"],"收到的公开值","自己的私有")}</g><g id="right-combine">{side(1200,T["danger"],T["success"],"收到的公开值","自己的私有")}</g>'
      )
svg("ecdhe-combine.svg","0 0 1600 900",combine())
svg("postcard.svg","0 0 960 600",f'''<rect id="card" x="30" y="30" width="900" height="540" rx="20" fill="{T['surface']}" stroke="{T['text2']}" stroke-width="6"/>
<path d="M560 80 V520" stroke="{T['border']}" stroke-width="4"/>
<text x="70" y="110" {F} font-size="34" font-weight="700" fill="{T['text']}">明信片 · HTTP</text>
<g id="plaintext"><rect x="66" y="170" width="460" height="150" rx="12" fill="{T['s2']}"/>
<text x="86" y="230" font-family="ui-monospace, Menlo, Consolas, monospace" font-size="32" fill="{T['text']}">user=alice&amp;</text>
<text x="86" y="285" font-family="ui-monospace, Menlo, Consolas, monospace" font-size="32" fill="{T['danger']}">password=123456</text></g>
<text x="70" y="380" {F} font-size="28" fill="{T['text2']}">内容全是明文，</text><text x="70" y="425" {F} font-size="28" fill="{T['text2']}">路上谁都看得到</text>
<g id="stamp"><rect x="760" y="70" width="130" height="150" rx="6" fill="{T['accent']}" stroke="{T['text']}" stroke-width="4" stroke-dasharray="10 6"/>
<text x="825" y="160" text-anchor="middle" {F} font-size="34" font-weight="800" fill="{T['bg']}">邮票</text></g>
<g id="address"><text x="600" y="300" {F} font-size="28" fill="{T['text2']}">寄往</text><text x="600" y="350" {F} font-size="30" font-weight="700" fill="{T['primary']}">example.com</text>
<path d="M600 400 H890 M600 450 H890 M600 500 H820" stroke="{T['muted']}" stroke-width="4"/></g>''')
svg("hash-check.svg","0 0 512 512",f'''<g id="fingerprint" fill="none" stroke="{T['primary']}" stroke-width="14" stroke-linecap="round">
<path d="M150 330 C130 200 200 130 256 130 C330 130 380 190 370 300"/><path d="M190 360 C170 250 210 180 256 180 C300 180 330 220 324 300"/>
<path d="M236 380 C214 300 228 230 256 230 C284 230 288 280 282 320"/><path d="M256 280 C258 320 270 360 290 390"/></g>
<g id="badge"><circle cx="380" cy="380" r="80" fill="{T['success']}"/><path id="check" d="M342 382 l26 26 l52 -56" fill="none" stroke="{T['bg']}" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></g>''')

# 无文字的小明信片：飞行/缩小镜头里用（文字 <28px 时不显示文字，只留卡片、明文框、邮票、地址线的形状）
_pc=open(os.path.join(OUT,"postcard.svg")).read()
open(os.path.join(OUT,"postcard-mini.svg"),"w").write(re.sub(r'<text[^>]*>.*?</text>','',_pc,flags=re.S))

# 自绘扁平图标（无文字，商用安全）：咖啡杯 / 眼睛（窃听）/ 铅笔（篡改）/ 面具（伪装）
svg("coffee-cup.svg","0 0 512 512",f'''<g id="steam" fill="none" stroke="{T['text2']}" stroke-width="14" stroke-linecap="round">
<path d="M190 150 C160 120 220 90 190 50"/><path d="M256 150 C226 120 286 90 256 50"/><path d="M322 150 C292 120 352 90 322 50"/></g>
<path id="handle" d="M372 230 h28 a56 56 0 0 1 0 112 h-36" fill="none" stroke="{T['accent']}" stroke-width="28" stroke-linecap="round"/>
<path id="cup" d="M112 190 H392 L366 400 a40 40 0 0 1 -40 34 H178 a40 40 0 0 1 -40 -34 Z" fill="{T['accent']}"/>
<rect x="112" y="190" width="280" height="30" rx="10" fill="#FCD34D"/>
<rect id="saucer" x="72" y="440" width="368" height="28" rx="14" fill="{T['text2']}"/>''')
svg("eye.svg","0 0 512 512",f'''<path id="outline" d="M40 256 C120 130 392 130 472 256 C392 382 120 382 40 256 Z" fill="{T['s2']}" stroke="{T['danger']}" stroke-width="24" stroke-linejoin="round"/>
<circle id="iris" cx="256" cy="256" r="84" fill="{T['danger']}"/><circle id="pupil" cx="256" cy="256" r="38" fill="{T['bg']}"/>
<circle cx="282" cy="228" r="14" fill="{T['text']}"/>''')
svg("pencil.svg","0 0 512 512",f'''<g id="pencil" transform="rotate(-45 256 256)">
<rect x="96" y="214" width="250" height="84" fill="{T['danger']}"/><rect x="96" y="214" width="250" height="28" fill="#FCA5A5"/>
<path d="M346 214 L446 256 L346 298 Z" fill="#FDE68A"/><path d="M412 242 L446 256 L412 270 Z" fill="{T['bg']}"/>
<rect x="66" y="214" width="34" height="84" fill="{T['text2']}"/><rect x="30" y="214" width="40" height="84" rx="16" fill="#FCA5A5"/></g>
<path id="scribble" d="M80 440 C130 410 170 470 220 440 S300 420 330 440" fill="none" stroke="{T['danger']}" stroke-width="12" stroke-linecap="round"/>''')
svg("mask.svg","0 0 512 512",f'''<path id="mask" d="M48 210 C48 150 170 150 256 190 C342 150 464 150 464 210 C464 320 380 350 330 330 C300 318 280 290 256 290 C232 290 212 318 182 330 C132 350 48 320 48 210 Z" fill="{T['danger']}"/>
<ellipse cx="170" cy="240" rx="54" ry="34" fill="{T['bg']}"/><ellipse cx="342" cy="240" rx="54" ry="34" fill="{T['bg']}"/>
<path id="strap" d="M48 214 L10 196 M464 214 L502 196" stroke="{T['text2']}" stroke-width="14" stroke-linecap="round"/>''')
