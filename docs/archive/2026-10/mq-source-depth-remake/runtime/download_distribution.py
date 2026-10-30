#!/usr/bin/env python3
"""Download official fixed version through inherited proxy; verify full SHA512.

The Apache checksum wraps groups of eight hex digits. Preserve its original
bytes and remove only ASCII whitespace after its filename/colon to compare.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime, hashlib, json, math, re, shutil, urllib.request
import sys
D=Path('/tmp/mq-source-depth-runtime')
R=Path(__file__).resolve().parent
D.mkdir(parents=True,exist_ok=True)
name='kafka_2.13-4.4.0.tgz'
base='https://archive.apache.org/dist/kafka/4.4.0/'
url=base+name
with urllib.request.urlopen(base+name+'.sha512',timeout=60) as response:
    checksum=response.read()
(D/(name+'.sha512')).write_bytes(checksum)
(R/(name+'.sha512')).write_bytes(checksum)
expected=re.sub(r'\s+','',checksum.decode().split(':',1)[1]).lower()
assert re.fullmatch(r'[0-9a-f]{128}',expected),expected
with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=60) as response:
    total=int(response.headers['Content-Length'])
    head={'status':response.status,'headers':dict(response.headers)}
parts=D/'download-parts';parts.mkdir(exist_ok=True)
workers=16
size=math.ceil(total/workers)
def download(i):
    start=i*size;end=min(total-1,start+size-1)
    target=parts/f'{i:02d}.part'
    request=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
    with urllib.request.urlopen(request,timeout=120) as response:
        actual=response.headers.get('Content-Range')
        assert response.status==206 and actual==f'bytes {start}-{end}/{total}',(response.status,actual)
        with target.open('wb') as out:
            while block:=response.read(1024*1024):out.write(block)
    assert target.stat().st_size==end-start+1
    print(f'RANGE_COMPLETE {i} bytes={target.stat().st_size}',flush=True)
    return {'part':i,'start':start,'end':end,'status':206,'contentRange':actual,'bytes':target.stat().st_size}
with ThreadPoolExecutor(max_workers=workers) as pool:
    records=[task.result() for task in as_completed([pool.submit(download,i) for i in range(workers) if i*size<total])]
target=D/name
with target.open('wb') as out:
    for i in sorted(x['part'] for x in records):
        with (parts/f'{i:02d}.part').open('rb') as part:shutil.copyfileobj(part,out)
sha=hashlib.sha512()
with target.open('rb') as inp:
    while block:=inp.read(1024*1024):sha.update(block)
actual=sha.hexdigest();assert actual==expected,(actual,expected)
result={'artifact':name,'officialUrl':url,'sha512Url':base+name+'.sha512','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'16 official-host byte-range GETs with validated Content-Range, concatenated in byte order; full artifact checked against official SHA512; inherited proxy/default TLS trust preserved.','head':head,'ranges':sorted(records,key=lambda x:x['part']),'expectedSha512':expected,'actualSha512':actual,'match':True,'artifactBytes':target.stat().st_size}
(R/'distribution-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['ranges','head']},indent=2),flush=True)
