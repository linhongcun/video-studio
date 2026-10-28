import argparse,concurrent.futures,datetime,hashlib,json,pathlib,time,urllib.request

parser=argparse.ArgumentParser()
parser.add_argument('--expected-commit',required=True)
parser.add_argument('--output',default='/tmp/theme-online-verification.json')
args=parser.parse_args()
root=pathlib.Path(__file__).resolve().parents[4]
baseline=json.loads((root/'docs/archive/2026-10/site-theme-fixes/preservation-baseline.json').read_text())
base='https://linhongcun.github.io/video-studio/'
report={'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'v0.83.0','expectedCommit':args.expected_commit,'base':base,'media':[],'pages':[],'errors':[]}

def fetch(path):
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(base+path,headers={'User-Agent':'video-studio-theme-verification','Cache-Control':'no-cache'}),timeout=60) as r:return r.status,r.read()
        except Exception:
            if attempt==2:raise
            time.sleep(1)

def media(item):
    path,expected=item
    status,data=fetch(path)
    digest=hashlib.sha256(data).hexdigest()
    assert status==200 and digest==expected['sha256'],(path,status,digest,expected['sha256'])
    return {'path':path,'status':status,'bytes':len(data),'sha256':digest}

selected=[item for item in baseline['selectedDigests'].items() if item[0].endswith(('.mp4','.jpg'))]
assert len(selected)==98
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    futures={pool.submit(media,item):item[0] for item in selected}
    for future in concurrent.futures.as_completed(futures):
        try:report['media'].append(future.result())
        except Exception as e:report['errors'].append({'path':futures[future],'error':repr(e)})
for path in ['', 'search/?q=%E5%93%88%E5%B8%8C', 'episodes/redis-skiplist/', 'changelog/']:
    try:
        status,data=fetch(path);html=data.decode()
        assert status==200 and '0.83.0' in html,(path,status,'version')
        if path=='episodes/redis-skiplist/':
            assert '/blob/'+args.expected_commit+'/' in html,(path,'snapshot')
            assert '<svg viewBox="0 0 640 250"' in html,(path,'diagram')
        if path=='changelog/':assert 'v0.83.0' in html and '完整记录见 GitHub Release' in html
        report['pages'].append({'path':path,'status':status,'version':'0.83.0'})
    except Exception as e:report['errors'].append({'path':path,'error':repr(e)})
try:
    status,vtt=fetch('episodes/redis-skiplist/captions.vtt')
    assert status==200 and vtt.startswith(b'WEBVTT') and b'-->' in vtt
    report['captions']={'redis-skiplist':{'status':status,'webvtt':True}}
except Exception as e:report['errors'].append({'captions':repr(e)})
report['passed']=not report['errors'] and len(report['media'])==98 and len(report['pages'])==4
pathlib.Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'fullMediaSha256Matches':len(report['media']),'pages':len(report['pages']),'errors':report['errors'],'output':args.output},ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
