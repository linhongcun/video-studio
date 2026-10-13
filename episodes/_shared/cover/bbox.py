# 输出每个 SVG 的可见内容框（SVG 用户坐标），与 Miyazaki make_covers.py 的 svgimg（cairosvg 渲染后 getbbox）一致
import sys,io,json,re,cairosvg
from PIL import Image
out={}
for p in sys.argv[1:]:
    s=open(p).read();m=re.search(r'viewBox="([^"]+)"',s)
    if m: vb=[float(v) for v in m.group(1).replace(',',' ').split()]
    else:  # 没有 viewBox：按 width/height（无单位 px）
        num=lambda k:float(re.search(k+r'="([0-9.]+)',s).group(1));vb=[0,0,num('width'),num('height')]
    im=Image.open(io.BytesIO(cairosvg.svg2png(url=p,output_width=2000))).convert('RGBA');k=vb[2]/im.width;x0,y0,x1,y1=im.getbbox()
    out[p]=[vb[0]+x0*k,vb[1]+y0*k,(x1-x0)*k,(y1-y0)*k]
print(json.dumps(out))
