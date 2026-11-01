from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,urllib.request,datetime,base64
D=Path(__file__).resolve().parent
REV='1156b2752aaa28eafc0b4c4d387e63356793268d'
PATHS=['core/src/main/scala/kafka/server/ReplicaManager.scala','core/src/main/scala/kafka/cluster/Partition.scala','server/src/main/java/org/apache/kafka/server/purgatory/DelayedProduce.java','core/src/main/scala/kafka/server/KafkaApis.scala','core/src/main/scala/kafka/server/ReplicaFetcherThread.scala','core/src/main/scala/kafka/server/AbstractFetcherThread.scala','server/src/main/java/org/apache/kafka/server/replica/Replica.java','storage/src/main/java/org/apache/kafka/storage/internals/log/UnifiedLog.java','clients/src/main/java/org/apache/kafka/common/config/TopicConfig.java','clients/src/main/java/org/apache/kafka/clients/producer/ProducerConfig.java','metadata/src/main/java/org/apache/kafka/controller/ReplicationControlManager.java','metadata/src/main/java/org/apache/kafka/controller/PartitionChangeBuilder.java','server/src/main/java/org/apache/kafka/server/config/ReplicationConfigs.java','storage/src/main/java/org/apache/kafka/storage/internals/log/LogConfig.java','LICENSE','NOTICE']
def fetch(path):
 name=path.rsplit('/',1)[-1];rawURL=f'https://raw.githubusercontent.com/apache/kafka/{REV}/{path}';metaURL=f'https://api.github.com/repos/apache/kafka/contents/{path}?ref={REV}'
 out=[]
 for url,filename in [(rawURL,name),(metaURL,name+'.metadata.json')]:
  started=datetime.datetime.now(datetime.timezone.utc).isoformat();req=urllib.request.Request(url,headers={'User-Agent':'video-studio-kafka-source-audit','Accept':'application/vnd.github+json' if 'api.github' in url else 'text/plain'})
  with urllib.request.urlopen(req,timeout=50) as r: data=r.read();status=r.status;headers=dict(r.headers)
  (D/filename).write_bytes(data);out.append({'url':url,'retrievedAtUTC':started,'status':status,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'localFile':filename,'etag':headers.get('ETag'),'lastModified':headers.get('Last-Modified')})
 m=json.loads((D/(name+'.metadata.json')).read_text());assert m['name']==name and m['path']==path
 assert base64.b64decode(m['content'])==(D/name).read_bytes()
 return {'upstreamPath':path,'title':name,'retrievals':out,'nameAndDecodedContentVerified':True}
rows=[]
with ThreadPoolExecutor(max_workers=4) as ex:
 futures=[(p,ex.submit(fetch,p)) for p in PATHS]
 for p,f in futures:
  try: r=f.result()
  except Exception as e:
   rows.append({'upstreamPath':p,'error':type(e).__name__+': '+str(e)});(D/'download-attempt-02.json').write_text(json.dumps(rows,indent=2)+'\n');raise
  rows.append(r);(D/'download-attempt-02.json').write_text(json.dumps(rows,indent=2)+'\n');print(p,'GET+title MATCH',flush=True)
(D/'download-manifest.json').write_text(json.dumps({'revision':REV,'repository':'https://github.com/apache/kafka','description':'Fresh official raw GET and fixed-commit GitHub Contents API raw JSON, exact bytes preserved. Download does not imply all lines were read.','files':rows},ensure_ascii=False,indent=2)+'\n')
