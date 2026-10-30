"""Fetch pinned official PG/JDBC inputs; verify explicitly reused Kafka bytes.

Uses inherited proxy and CA verification. Writes only this batch's archive and
task-owned temporary dependency area; never edits historical runtime evidence.
"""
from pathlib import Path
import datetime, hashlib, json, tarfile
import urllib.request, urllib.error

R=Path(__file__).resolve().parent
REPO=next(p for p in R.parents if (p/'AGENTS.md').is_file())
W=Path('/tmp/mq05-07-runtime');W.mkdir(parents=True,exist_ok=True)
O=R/'dependencies';O.mkdir(exist_ok=True)
sha=lambda data:hashlib.sha256(data).hexdigest()
records=[]
def get(name,url):
 t=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(url,timeout=180) as response:
   data=response.read();status=response.status;effective=response.url
 except Exception as error:
  records.append({'name':name,'url':url,'retrievedAt':t,'error':repr(error)})
  (O/'download-evidence.json').write_text(json.dumps(records,indent=2)+'\n')
  raise
 record={'name':name,'url':url,'effectiveURL':effective,'status':status,'retrievedAt':t,'bytes':len(data),'sha256':sha(data)}
 records.append(record);(O/'download-evidence.json').write_text(json.dumps(records,indent=2)+'\n')
 target=W/name;target.write_bytes(data)
 return target,data

prior=REPO/'docs/archive/2026-10/mq-source-depth-remake/runtime/distribution-verification.json'
old=json.loads(prior.read_text());artifact=Path('/tmp/mq-source-depth-runtime/kafka_2.13-4.4.0.tgz')
actual=hashlib.sha512(artifact.read_bytes()).hexdigest()
assert old['match'] and actual.lower()==old['expectedSha512'].lower()
K=artifact.parent/'kafka_2.13-4.4.0';checked=[]
with tarfile.open(artifact,'r:gz') as archive:
 for member in archive:
  parts=Path(member.name).parts
  if not member.isfile() or len(parts)<3 or parts[1] not in {'libs','bin'}:continue
  raw=archive.extractfile(member).read();target=artifact.parent/member.name
  assert sha(target.read_bytes())==sha(raw),target
  checked.append({'path':str(target.relative_to(K)),'bytes':len(raw),'sha256':sha(raw)})
(O/'kafka-reuse-verification.json').write_text(json.dumps({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reuse':True,'artifact':str(artifact),'expectedSha512':old['expectedSha512'],'actualSha512':actual,'match':True,'priorOfficialVerification':str(prior.relative_to(REPO)),'priorVerificationSHA256':sha(prior.read_bytes()),'extractedBinAndLibFiles':checked,'scope':'Freshly rehashes official previously downloaded distribution and each reused extracted bin/lib file. No fresh Kafka distribution GET is claimed.'},indent=2)+'\n')
commit='3d6a828938a5fa0444275d3d2f67b64ec3199eb7'
_,raw=get('postgres-REL_18_0-ref.json','https://api.github.com/repos/postgres/postgres/git/ref/tags/REL_18_0')
ref=json.loads(raw)
assert ref['object']['sha']==commit,ref
get('postgres-'+commit+'.tar.gz','https://codeload.github.com/postgres/postgres/tar.gz/'+commit)
(O/'postgres-ref.json').write_bytes(raw)
jar,data=get('postgresql-42.7.8.jar','https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.8/postgresql-42.7.8.jar')
for algorithm in ['sha512','sha256','sha1']:
 try:
  _,digest=get('postgresql-42.7.8.jar.'+algorithm,'https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.8/postgresql-42.7.8.jar.'+algorithm)
 except urllib.error.HTTPError as error:
  if error.code==404:continue
  raise
 expected=digest.decode().strip().split()[0].lower();actual=hashlib.new(algorithm,data).hexdigest()
 assert actual==expected
 (O/'jdbc-verification.json').write_text(json.dumps({'version':'42.7.8','sha256':sha(data),'repositoryChecksumAlgorithm':algorithm,'expected':expected,'actual':actual,'match':True,'scope':'Official TLS Maven artifact plus its provided repository checksum; no stronger repository checksum is claimed.'},indent=2)+'\n')
 break
else:raise RuntimeError('No official repository checksum was available')
print(json.dumps({'kafkaReusedFilesVerified':len(checked),'postgresCommit':commit,'downloads':len(records),'jdbcVerified':True,'temporaryDirectory':str(W)}))
