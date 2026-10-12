import json,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
import os;H=os.environ.get("SB","/workspace/miyazaki-backup/dns/");d=json.load(open(H+"storyboard.json"))
FT=lambda s:ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',int(s))
def val(sh,eid,prop,f,dflt):
    v=dflt
    for a in sh['animations']:
        if a['elementId']!=eid or a['property']!=prop: continue
        k=a['keyframes']
        if f<k[0]['frame']: 
            if v==dflt: v=k[0]['value']  # 首帧前按首个关键帧取值（Remotion clamp）
            continue
        if f>=k[-1]['frame']: v=k[-1]['value']
        else: v=k[0]['value']+(k[-1]['value']-k[0]['value'])*(f-k[0]['frame'])/(k[-1]['frame']-k[0]['frame'])
    return v
def render(sid,f,out):
    sh=[s for sc in d['scenes'] for s in sc['shots'] if s['id']==sid][0]
    F=Image.new('RGBA',(1920,1080),'#0B1020')
    for e in sh['elements']:
        if e.get('role')=='subtitle': continue
        op=val(sh,e['id'],'opacity',f,1); x=val(sh,e['id'],'x',f,e['x']); y=val(sh,e['id'],'y',f,e['y'])
        if op<=0: continue
        L=Image.new('RGBA',(1920,1080),(0,0,0,0));dr=ImageDraw.Draw(L)
        if e['type']=='image' and e.get('placeholder'):
            for k in range(0,int(e['w']),24): dr.line([x+k,y,x+min(k+12,e['w']),y],fill='#9CA3AF',width=3);dr.line([x+k,y+e['h'],x+min(k+12,e['w']),y+e['h']],fill='#9CA3AF',width=3)
            for k in range(0,int(e['h']),24): dr.line([x,y+k,x,y+min(k+12,e['h'])],fill='#9CA3AF',width=3);dr.line([x+e['w'],y+k,x+e['w'],y+min(k+12,e['h'])],fill='#9CA3AF',width=3)
            dr.text((x+e['w']/2,y+e['h']/2-24),'EP.01 画面占位',font=FT(32),fill='#9CA3AF',anchor='mm');dr.text((x+e['w']/2,y+e['h']/2+24),e['src'],font=FT(24),fill='#6B7280',anchor='mm')
        elif e['type']=='image':
            subprocess.run(['rsvg-convert','-w',str(e['w']),'-h',str(e['h']),'--keep-aspect-ratio',H+e['asset'],'-o','/tmp/dnsi.png'],check=True)
            im=Image.open('/tmp/dnsi.png').convert('RGBA')
            if e.get('tint'):
                c=Image.new('RGBA',im.size,e['tint']);c.putalpha(im.getchannel('A'));im=c
            L.alpha_composite(im,(int(x+(e['w']-im.width)/2),int(y+(e['h']-im.height)/2)))
        elif e['type']=='text':
            ax={'center':'ma','right':'ra'}.get(e.get('align'),'la');xx={'ma':x+e['w']/2,'ra':x+e['w'],'la':x}[ax]
            dr.text((xx,y),e['text'],font=FT(e['fontSize']),fill=e['color'],anchor=ax)
        elif e['type']=='rect':
            dr.rounded_rectangle([x,y,x+e['w'],y+e['h']],e.get('radius',0),fill=e['color'],outline=e.get('stroke'),width=3)
            dr.text((x+e['w']/2,y+e['h']/2),e.get('label',''),font=FT(e.get('fontSize',40)),fill='#E5E7EB',anchor='mm')
        elif e['type']=='line':
            dr.line([x,y,x+e['w'],y+e['h']],fill=e['color'],width=4)
        elif e['type']=='arrow':
            p=val(sh,e['id'],'drawProgress',f,1);cy=y+e['h']/2
            if e.get('direction')=='l': x0,x1=x+e['w'],x+e['w']-e['w']*p
            else: x0,x1=x,x+e['w']*p
            dr.line([x0,cy,x1,cy],fill=e['color'],width=6)
            if p>0: dr.text((x+e['w']/2,y-4),e.get('label',''),font=FT(e.get('fontSize',32)),fill=e['color'],anchor='md')
        elif e['type']=='icon':
            dr.ellipse([x,y,x+e['w'],y+e['h']],outline=e['color'],width=6);dr.text((x+e['w']/2,y+e['h']/2),e['id'],font=FT(24),fill=e['color'],anchor='mm')
        if op<1: L.putalpha(L.getchannel('A').point(lambda a:int(a*op)))
        F.alpha_composite(L)
    dr=ImageDraw.Draw(F);dr.rectangle([80,80,1840,1000],outline='#333');dr.rectangle([160,900,1760,980],outline='#555');dr.line([80,880,1840,880],fill='#553')
    F.convert('RGB').save(out);print(out,f)
for a in sys.argv[1:]:
    sid,f=a.split(':');render(sid,int(f),H+f'check-{sid}-{f}.png')
