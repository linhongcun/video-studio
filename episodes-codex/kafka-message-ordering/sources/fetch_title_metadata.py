from pathlib import Path
import json,urllib.request,urllib.parse,datetime,hashlib,base64,concurrent.futures
D=Path(__file__).resolve().parent.parent;commit='1156b2752aaa28eafc0b4c4d387e63356793268d';rows=json.loads((D/'sources/download-manifest.json').read_text())['sources'];paths={Path(x['path']).name:x['path']for x in rows};names=['BuiltInPartitioner.java','RecordAccumulator.java','CompletedFetch.java','KafkaConsumer.java','KafkaProducer.java','StringSerializer.java','UnifiedLog.java','FetchCollector.java','ProducerConfig.java']
def get(name):
 path=paths[name];url='https://api.github.com/repos/apache/kafka/contents/'+path+'?ref='+commit;req=urllib.request.Request(url,headers={'Accept':'application/vnd.github+json','User-Agent':'video-studio-source-title-review'})
 with urllib.request.urlopen(req,timeout=45)as r:raw=r.read();status=r.status
 v=json.loads(raw);assert v['name']==name and v['path']==path
 if v.get('encoding')=='base64':assert base64.b64decode(v['content'])==(D/'sources'/name).read_bytes()
 dest=D/'sources/title-metadata'/(name+'.json');dest.write_bytes(raw)
 return {'name':v['name'],'sourcePath':v['path'],'sourceBlobSHA':v['sha'],'apiURL':url,'httpStatus':status,'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rawResponseFile':str(dest.relative_to(D)),'rawResponseSHA256':hashlib.sha256(raw).hexdigest(),'decodedContentMatchesPreviouslyReadFixedCommitSource':True}
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:result=list(pool.map(get,names))
(D/'sources/title-metadata/fetch-evidence.json').write_text(json.dumps({'commit':commit,'method':'Fresh GitHub Contents API raw JSON .name at fixed commit; response unmodified, base64 content checked against existing raw source bytes.','responses':result},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'freshResponses':len(result),'names':[x['name']for x in result],'allSourceBytesMatch':True}))
