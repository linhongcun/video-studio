"""Fresh official dependency downloads into this task only; inherited proxy/TLS unchanged."""
from pathlib import Path
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor
import urllib.request,hashlib,json,tarfile,re
R=Path(__file__).resolve().parent;O=R/'dependencies';W=Path('/tmp/mq05-consumer-replay-20261102');W.mkdir(exist_ok=True)
PG='3d6a828938a5fa0444275d3d2f67b64ec3199eb7';EXPECTED='f5ceba8a265ab6bb2d68362b1f6859a95e15d60ef92ba83b43fdf065b557dc18e98d6383c15b9977320e25b3a2c8b6f11decb17b0fa6c0f163423793a0eb95cb'
items=[('kafka_2.13-4.4.0.tgz','https://archive.apache.org/dist/kafka/4.4.0/kafka_2.13-4.4.0.tgz'),('kafka_2.13-4.4.0.tgz.sha512','https://archive.apache.org/dist/kafka/4.4.0/kafka_2.13-4.4.0.tgz.sha512'),('postgres-ref.json','https://api.github.com/repos/postgres/postgres/git/ref/tags/REL_18_0'),('postgres-'+PG+'.tar.gz','https://codeload.github.com/postgres/postgres/tar.gz/'+PG),('postgresql-42.7.8.jar','https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.8/postgresql-42.7.8.jar'),('postgresql-42.7.8.jar.sha1','https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.8/postgresql-42.7.8.jar.sha1')]
def get(item):
 name,url=item;start=datetime.now(timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(url,timeout=45)as response:
   raw=response.read();status=response.status;effective=response.url;headers={k:response.headers[k]for k in ['Content-Length','ETag','Last-Modified']if k in response.headers}
  (W/name).write_bytes(raw);record={'file':name,'url':url,'effectiveURL':effective,'status':status,'startedAtUTC':start,'finishedAtUTC':datetime.now(timezone.utc).isoformat(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'headers':headers}
  if name.endswith(('.json','.sha1','.sha512')):(O/name).write_bytes(raw)
 except Exception as e:record={'file':name,'url':url,'startedAtUTC':start,'error':repr(e)}
 (O/(name+'.download.json')).write_text(json.dumps(record,indent=2)+'\n');print(name,record.get('status'),record.get('bytes'),flush=True);return record
with ThreadPoolExecutor(max_workers=3)as ex:records=list(ex.map(get,items))
(O/'download-evidence.json').write_text(json.dumps(records,indent=2)+'\n');assert all(r.get('status')==200 for r in records),records
actual=hashlib.sha512((W/items[0][0]).read_bytes()).hexdigest();checksum=''.join(re.findall(r'[A-Fa-f0-9]{8,}',(W/items[1][0]).read_text())).lower();assert actual==EXPECTED and EXPECTED in checksum
K=W/'kafka_2.13-4.4.0';checks=[]
with tarfile.open(W/items[0][0],'r:gz')as tar:
 tar.extractall(W,filter='data')
 for member in tar:
  parts=Path(member.name).parts
  if member.isfile() and len(parts)>=3 and parts[1]in {'bin','libs'}:
   p=W/member.name;raw=tar.extractfile(member).read();h=hashlib.sha256(raw).hexdigest();assert hashlib.sha256(p.read_bytes()).hexdigest()==h;checks.append({'path':str(p.relative_to(K)),'bytes':p.stat().st_size,'sha256':h})
(O/'kafka-verification.json').write_text(json.dumps({'version':'4.4.0','freshOfficialGET':True,'match':True,'artifact':str(W/items[0][0]),'expectedSha512':EXPECTED,'actualSha512':actual,'checksumURL':items[1][1],'binAndLibFiles':checks},indent=2)+'\n')
assert json.loads((W/'postgres-ref.json').read_text())['object']['sha']==PG
pgarchive=W/('postgres-'+PG+'.tar.gz');assert hashlib.sha256(pgarchive.read_bytes()).hexdigest()=='b90e598761827cee3477a6159653914a7fbf02602767ea7122762fa59611513a'
with tarfile.open(pgarchive,'r:gz')as tar:tar.extractall(W,filter='data')
jar=(W/'postgresql-42.7.8.jar').read_bytes();expected=(W/'postgresql-42.7.8.jar.sha1').read_text().strip();assert hashlib.sha1(jar).hexdigest()==expected and hashlib.sha256(jar).hexdigest()=='2a32a9dcbc42d67a50ad3a0de5efd102c8d2be46720045f2cbd6689f160ab7c7'
(O/'jdbc-verification.json').write_text(json.dumps({'version':'42.7.8','sha256':hashlib.sha256(jar).hexdigest(),'repositoryChecksumAlgorithm':'sha1','expected':expected,'actual':hashlib.sha1(jar).hexdigest(),'match':True,'scope':'Fresh official TLS Maven artifact and its provided SHA1; additionally exactSHA256 matches previously recorded artifact. No stronger repository checksum claimed.'},indent=2)+'\n')
print('FRESH_DEPENDENCIES_VERIFIED',flush=True)
