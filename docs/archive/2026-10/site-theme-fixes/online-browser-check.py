import json,pathlib,re,hashlib,traceback,os,datetime,xml.etree.ElementTree as ET
from urllib.parse import quote
from playwright.sync_api import sync_playwright
R=pathlib.Path(__file__).resolve().parents[4];O=pathlib.Path('/tmp/theme-online-ui');O.mkdir(exist_ok=True)
B='https://linhongcun.github.io/video-studio/'
deployment=json.loads((O/'deployment-confirmed.json').read_text())
assert deployment['conclusion']=='success' and re.fullmatch('[0-9a-f]{40}',deployment['headSha'])
assert deployment['release']=='v0.83.0'
JS=r'''(() => {
 const rgba=s=>{const n=s.match(/[\d.]+/g)?.map(Number)??[0,0,0,0];return [n[0],n[1],n[2],n.length>3?n[3]:1]};
 const over=(a,b)=>{const t=a[3]+b[3]*(1-a[3]);return t?[0,1,2].map(i=>(a[i]*a[3]+b[i]*b[3]*(1-a[3]))/t).concat(t):[0,0,0,0]};
 const lum=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((v,n,i)=>v+n*[.2126,.7152,.0722][i],0);
 const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
 const bg=e=>{let a=[];for(let n=e;n;n=n.parentElement)a.unshift(n);return a.reduce((b,n)=>over(rgba(getComputedStyle(n).backgroundColor),b),[255,255,255,1])};
 const sample=e=>{const s=getComputedStyle(e),b=bg(e),c=over(rgba(s.color),b);return {color:s.color,background:s.backgroundColor,effectiveBackground:b,ratio:ratio(c,b),size:s.fontSize,opacity:s.opacity}};
 window.__contrast={rgba,over,lum,ratio,bg,sample};
})()'''
raw=(R/'episodes/redis-skiplist/article.mdx').read_text();block=re.search(r'<svg\b.*?</svg>',raw,re.S).group();block=re.sub(r'style=\{\{.*?\}\}','',block,flags=re.S);svg=ET.fromstring(block)
def art(n):return {'tag':n.tag,'attrs':dict(sorted(n.attrib.items())),'text':(n.text or '').strip(),'children':[art(c) for c in n]}
expectedArt=art(svg)
report={'scope':'production canonical URL via inherited proxy and native Chromium CA verification; computed WCAG contrast including alpha compositing; viewport emulation, no physical mobile claim','deployment':deployment,'startedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[],'screenshots':[],'errors':[],'baseline':'dadb53ede6615aa384b3572f8950e3d449a8870d'}
def ok(name,data=None):report['checks'].append({'name':name,'detail':data})
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'],proxy={'server':os.environ['HTTPS_PROXY']})
 for width,height,theme in [(1440,1000,'light'),(390,844,'dark')]:
  label=f'{width}-{theme}';ctx=browser.new_context(viewport={'width':width,'height':height},color_scheme=theme);ctx.add_init_script(f"localStorage.setItem('vs:theme','{theme}');");page=ctx.new_page();page.set_default_timeout(20000)
  def go(route):
   page.goto(B+route,wait_until='domcontentloaded',timeout=45000);page.evaluate(JS);assert page.locator('html').get_attribute('data-theme')==theme
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),route
   assert 'v0.83.0' in page.locator('footer').inner_text(), 'production version mismatch'
  def shot(name,locator=None):
   path=O/f'{label}-{name}.png';(locator.screenshot(path=str(path)) if locator else page.screenshot(path=str(path)));report['screenshots'].append(str(path))
  try:
   go('');hero=page.locator('.home-hero');cs=hero.evaluate('e=>{const s=getComputedStyle(e);return {background:s.backgroundColor,image:s.backgroundImage,border:s.borderTopWidth,lum:__contrast.lum(__contrast.bg(e))}}')
   assert cs['lum']>.8 if theme=='light' else cs['lum']<.1,cs
   assert cs['image']=='none' and float(cs['border'].replace('px',''))>=1,cs
   rows=hero.evaluate('''root=>{const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),out=[];let t;while(t=w.nextNode()){const e=t.parentElement,s=getComputedStyle(e);if(t.textContent.trim()&&parseFloat(s.fontSize)<24&&s.visibility!=='hidden'&&e.getClientRects().length&&s.display!=='none')out.push({text:t.textContent.trim(),tag:e.tagName,...__contrast.sample(e)})}return out}''')
   assert rows and all(r['ratio']>=4.5 for r in rows),[r for r in rows if r['ratio']<4.5]
   ok(label+':hero-palette+all-small-text',{'palette':cs,'textSamples':len(rows),'minimumContrast':min(r['ratio'] for r in rows),'samples':rows});shot('hero',hero)
   muted=page.evaluate('''()=>['--c-bg','--c-surface','--c-surface-2'].map(token=>{const e=document.createElement('span');e.style.cssText=`color:var(--c-muted);background:var(${token})`;document.body.append(e);const r={token,...__contrast.sample(e)};e.remove();return r})''')
   assert all(r['ratio']>=4.5 for r in muted),muted;ok(label+':muted-on-three-surfaces',muted)
   go('library/');card=page.locator('a.card').first;img=card.locator('.cover img');original=img.get_attribute('src')
   for cover in ['missing','white','black']:
    card.locator('.cover').evaluate('(e,c)=>e.style.backgroundColor=c',{'missing':'','white':'white','black':'black'}[cover])
    src='data:image/png;base64,invalid' if cover=='missing' else 'data:image/svg+xml,'+quote(f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080"><rect width="1920" height="1080" fill="{cover}"/></svg>')
    img.evaluate('(e,src)=>{e.loading="eager";e.src=src}',src)
    if cover!='missing':img.evaluate('e=>e.decode()')
    for action in ['hover','keyboard-focus']:
     if action=='hover':card.hover()
     else:
      page.mouse.move(0,0);card.focus();page.keyboard.press('Tab');page.keyboard.press('Shift+Tab');assert card.evaluate('e=>e.matches(":focus-visible")')
     page.wait_for_timeout(220);play=card.locator('.play');state=play.evaluate('e=>({...__contrast.sample(e),width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height,focus:e.closest("a").matches(":focus-visible")})')
     assert float(state['opacity'])>.99 and state['ratio']>=3,state
     ok(label+f':card-{cover}-{action}',state)
     if action=='keyboard-focus':shot('card-'+cover,card)
    img.evaluate('(e,src)=>e.src=src',original)
   go('episodes/redis-skiplist/');sourceHrefs=page.locator('.source-links a').evaluate_all('els=>els.map(e=>e.href)');assert len(sourceHrefs)==3 and all('/'+deployment['headSha']+'/' in h for h in sourceHrefs),sourceHrefs;ok(label+':deployed-merge-source-reference',sourceHrefs);diagram=page.locator('svg[aria-labelledby="skip-search-title skip-search-desc"]');assert diagram.count()==1
   actual=diagram.evaluate('''e=>{const tree=n=>({tag:n.localName,attrs:Object.fromEntries(Array.from(n.attributes).filter(a=>a.name!=='style'&&!a.name.startsWith('data-astro-')).map(a=>[a.name,a.value]).sort()),text:Array.from(n.childNodes).filter(c=>c.nodeType===3).map(c=>c.textContent).join('').trim(),children:Array.from(n.children).map(tree)});return tree(e)}''')
   assert actual==expectedArt,'SVG artwork attributes/text/children changed'
   frame=diagram.evaluate('e=>{const s=getComputedStyle(e);return {borderWidth:s.borderTopWidth,border:s.borderTopColor,shadow:s.boxShadow,padding:s.padding,background:s.backgroundColor,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}}')
   assert float(frame['borderWidth'].replace('px',''))>=1 or frame['shadow']!='none' or float(frame['padding'].split()[0].replace('px',''))>0,frame
   ok(label+':redis-native-SVG-frame+art-preserved',{'frame':frame,'artSha256':hashlib.sha256(json.dumps(actual,sort_keys=True,ensure_ascii=False).encode()).hexdigest()});diagram.scroll_into_view_if_needed();shot('redis-svg',diagram.locator('..'))
   go('search/?q='+quote('哈希'));page.wait_for_selector('.pagefind-ui__result mark');marks=page.locator('.pagefind-ui__result mark').evaluate_all('els=>els.map(e=>({text:e.textContent,...__contrast.sample(e)}))')
   assert marks and all(r['background'] not in ['rgb(255, 255, 0)','yellow'] and r['ratio']>=4.5 for r in marks),marks
   ok(label+':real-pagefind-hash-highlight',{'markCount':len(marks),'minimumContrast':min(r['ratio'] for r in marks),'samples':marks});page.locator('.pagefind-ui__result').first.scroll_into_view_if_needed();shot('search-hash')
  except Exception as e:report['errors'].append({'context':label,'error':str(e),'trace':traceback.format_exc(),'url':page.url});shot('failure')
  finally:ctx.close()
 # System theme follows media changes, picker overrides it, and chosen preference survives reload.
 for width,height in [(1440,1000),(390,844)]:
  ctx=browser.new_context(viewport={'width':width,'height':height},color_scheme='light');page=ctx.new_page();page.goto(B,wait_until='domcontentloaded')
  try:
   assert page.locator('html').get_attribute('data-theme')=='light';page.emulate_media(color_scheme='dark');page.wait_for_function('document.documentElement.dataset.theme==="dark"')
   page.locator('.theme-trigger').click();page.locator('[data-theme-opt="light"]').click();assert page.locator('html').get_attribute('data-theme')=='light';page.reload(wait_until='domcontentloaded');assert page.locator('html').get_attribute('data-theme')=='light'
   page.locator('.theme-trigger').click();page.locator('[data-theme-opt="system"]').click();assert page.locator('html').get_attribute('data-theme')=='dark';page.emulate_media(color_scheme='light');page.wait_for_function('document.documentElement.dataset.theme==="light"')
   ok(f'{width}:system-media+picker+reload-persistence')
  except Exception as e:report['errors'].append({'context':str(width)+'-theme-switch','error':str(e)})
  ctx.close()
 browser.close()
report['finishedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();report['passed']=not report['errors'];(O/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'screenshots':len(report['screenshots']),'errors':report['errors'],'report':str(O/'report.json')},ensure_ascii=False))
