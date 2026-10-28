from pathlib import Path
import argparse, hashlib, json, subprocess
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser()
parser.add_argument('--root',required=True)
parser.add_argument('--candidate',required=True)
parser.add_argument('--base',required=True)
parser.add_argument('--out',required=True)
args=parser.parse_args()
root=Path(args.root)
out=Path(args.out)
out.mkdir(parents=True,exist_ok=True)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==args.candidate
report={'candidate':args.candidate,'base':args.base,'startedAt':datetime.now(timezone.utc).isoformat(),'scope':'Supplemental actual-visible reference-page screenshots from the exact unchanged final build. Scroll into the viewport before seeking, then require a new requestVideoFrameCallback at the requested media time and settled readyState. No full media decode or HTTP hash repetition.','captures':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    report['chromiumVersion']=browser.version
    for width,height in [(1440,1000),(390,844)]:
        for slug in ['db-index','db-transaction','db-lock','db-replication']:
            directory=root/'episodes'/slug
            meta=json.loads((directory/'meta.json').read_text())
            receipt=json.loads((directory/meta['referenceAppendix']['manifest']).read_text())
            page=browser.new_page(viewport={'width':width,'height':height},reduced_motion='reduce')
            response=page.goto(args.base+'/episodes/'+slug+'/',wait_until='networkidle')
            assert response and response.status==200
            video=page.locator('video')
            video.scroll_into_view_if_needed()
            page.wait_for_function('document.querySelector("video").readyState>=1')
            page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
            fps=float(receipt['fps'])
            time=(receipt['appendix']['from']+receipt['appendix']['framesPerPage']/2)/fps
            presented=video.evaluate('''async (v,t)=>{
              v.pause();
              const frame=await new Promise((resolve,reject)=>{
                const timer=setTimeout(()=>reject(new Error('Missing visible presented frame')),10000);
                const capture=(now,m)=>{if(Math.abs(m.mediaTime-t)<.075){clearTimeout(timer);resolve({mediaTime:m.mediaTime,presentedFrames:m.presentedFrames})}else v.requestVideoFrameCallback(capture)};
                v.requestVideoFrameCallback(capture);v.currentTime=t;
              });
              await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
              return frame;
            }''',time)
            page.wait_for_function('(t)=>{const v=document.querySelector("video");return !v.seeking&&v.readyState>=3&&Math.abs(v.currentTime-t)<.05}',arg=time)
            page.wait_for_timeout(500)
            state=video.evaluate('''v=>({time:v.currentTime,paused:v.paused,readyState:v.readyState,active:[...v.textTracks].flatMap(t=>[...(t.activeCues??[])].map(c=>c.text)),box:{top:v.getBoundingClientRect().top,bottom:v.getBoundingClientRect().bottom,height:v.getBoundingClientRect().height},viewport:innerHeight})''')
            assert state['paused'] and not state['active'] and state['box']['top']>=-1 and state['box']['bottom']<=state['viewport']+1, (slug,width,state)
            name=slug+'-references-visible-'+str(width)+'.png'
            page.screenshot(path=str(out/name))
            report['captures'].append({'slug':slug,'width':width,'height':height,'expectedTime':time,'presentedFrame':presented,'state':state,'screenshot':name,'screenshotSHA256':hashlib.sha256((out/name).read_bytes()).hexdigest()})
            page.close()
    browser.close()
report['status']='passed'
report['finishedAt']=datetime.now(timezone.utc).isoformat()
(out/'visible-reference-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':report['status'],'captures':len(report['captures'])}))
