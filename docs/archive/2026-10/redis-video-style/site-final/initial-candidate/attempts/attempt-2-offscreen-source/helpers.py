from pathlib import Path
import hashlib,json,re,subprocess,urllib.request,yaml
def sha_file(p):
    d=hashlib.sha256()
    with p.open('rb') as f:
        while block:=f.read(1024*1024):d.update(block)
    return d.hexdigest()

def git_blob(rev,path):
    return subprocess.check_output(['git','rev-parse',f'{rev}:{path}'],cwd=root,text=True).strip()

def full_http_sha(url):
    d=hashlib.sha256();size=0
    with urllib.request.urlopen(urllib.request.Request(url,headers={'Accept-Encoding':'identity'}),timeout=60) as r:
        assert r.status == 200,(url,r.status)
        length=int(r.headers['Content-Length']) if r.headers.get('Content-Length') else None
        while block:=r.read(1024*1024):d.update(block);size+=len(block)
        assert length is None or length==size,(url,length,size)
        return {'url':url,'sha256':d.hexdigest(),'bytes':size,'status':r.status}

def article_data(text):
    frontmatter=yaml.safe_load(text.split('---',2)[1]) if text.startswith('---\n') else {}
    assert isinstance(frontmatter,dict)
    headings=[{'level':len(level),'title':title.strip(),'id':ident} for level,title,ident in re.findall(r'^(#{2,3})\s+(.+?)\s+\{#([\w-]+)\}\s*$',text,re.M)]
    figures=[]
    for tag in re.findall(r'<Figure\b[^>]+>',text,re.S):
        src=re.search(r'\bsrc="([^"]+)"',tag);seek=re.search(r'\bseekTo=\{([0-9.]+)\}',tag)
        assert src and seek,tag
        figures.append({'src':src.group(1),'seek':float(seek.group(1))})
    assert headings and figures
    return {'frontmatter':frontmatter,'headings':headings,'figures':figures}

def overflow(page):
    d=page.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
    assert d['scroll']<=d['client']+1,d
    return d

def visible_video(page):
    v=page.locator('video')
    v.evaluate('(v)=>v.scrollIntoView({block:"center",inline:"nearest"})')
    page.wait_for_timeout(120)
    box=v.bounding_box();assert box
    size=page.viewport_size
    assert box['x']>=-1 and box['y']>=-1 and box['x']+box['width']<=size['width']+1 and box['y']+box['height']<=size['height']+1,(box,size)
    return box

def seek_paused(page,t):
    visible_video(page)
    presented=page.locator('video').evaluate('''async(v,t)=>{
      v.pause();
      // Move away first when repeating the same seek; a paused unchanged frame may not emit a callback.
      if(Math.abs(v.currentTime-t)<.075){v.currentTime=Math.max(0,t-.15);await new Promise((r,j)=>{const n=setTimeout(()=>j(new Error('reset seek timeout')),10000);v.addEventListener('seeked',()=>{clearTimeout(n);r()},{once:true})})}
      const frame=await new Promise((resolve,reject)=>{
        const timer=setTimeout(()=>reject(new Error('No presented frame at '+t)),10000);
        const capture=(now,m)=>{if(Math.round(m.mediaTime*30)===Math.round(t*30)){clearTimeout(timer);resolve({mediaTime:m.mediaTime,presentedFrames:m.presentedFrames})}else v.requestVideoFrameCallback(capture)};
        v.requestVideoFrameCallback(capture);v.currentTime=t;
      });
      await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      return frame;
    }''',t)
    page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&v.readyState>=3&&Math.abs(v.currentTime-t)<.05}',arg=t)
    page.wait_for_timeout(350)
    state=page.locator('video').evaluate('(v)=>({time:v.currentTime,active:[...v.textTracks].flatMap(t=>[...(t.activeCues??[])].map(c=>c.text))})')
    state['presentedFrame']=presented
    return state

def links(locator):return locator.evaluate_all('(as)=>[...new Set(as.map(a=>a.getAttribute("href")).filter(Boolean))]')
