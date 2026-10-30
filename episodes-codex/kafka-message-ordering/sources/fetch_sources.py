from pathlib import Path
import concurrent.futures,urllib.request,hashlib,json,datetime
D=Path(__file__).resolve().parent
commit='1156b2752aaa28eafc0b4c4d387e63356793268d'
paths=['clients/src/main/java/org/apache/kafka/clients/producer/KafkaProducer.java','clients/src/main/java/org/apache/kafka/clients/producer/internals/BuiltInPartitioner.java','clients/src/main/java/org/apache/kafka/clients/producer/internals/RecordAccumulator.java','clients/src/main/java/org/apache/kafka/clients/producer/internals/Sender.java','clients/src/main/java/org/apache/kafka/clients/producer/ProducerConfig.java','clients/src/main/java/org/apache/kafka/common/utils/Utils.java','clients/src/main/java/org/apache/kafka/common/serialization/StringSerializer.java','clients/src/main/java/org/apache/kafka/clients/consumer/internals/FetchCollector.java','clients/src/main/java/org/apache/kafka/clients/consumer/internals/CompletedFetch.java','clients/src/main/java/org/apache/kafka/clients/consumer/internals/AbstractFetch.java','clients/src/main/java/org/apache/kafka/clients/consumer/internals/ClassicKafkaConsumer.java','clients/src/main/java/org/apache/kafka/clients/consumer/ConsumerRecords.java','clients/src/main/java/org/apache/kafka/clients/producer/internals/ProducerBatch.java','clients/src/main/java/org/apache/kafka/common/record/internal/MemoryRecordsBuilder.java','clients/src/main/java/org/apache/kafka/clients/consumer/internals/Fetch.java','clients/src/main/java/org/apache/kafka/clients/consumer/KafkaConsumer.java','storage/src/main/java/org/apache/kafka/storage/internals/log/UnifiedLog.java','storage/src/main/java/org/apache/kafka/storage/internals/log/LogValidator.java','storage/src/main/java/org/apache/kafka/storage/internals/log/LocalLog.java','LICENSE','NOTICE']
def download(path):
 url=f'https://raw.githubusercontent.com/apache/kafka/{commit}/{path}'
 with urllib.request.urlopen(url,timeout=45)as r:b=r.read();status=r.status
 dest=D/Path(path).name;dest.write_bytes(b)
 return {'path':path,'file':str(dest.name),'url':url,'status':status,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'checkedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with concurrent.futures.ThreadPoolExecutor(max_workers=5)as pool:rows=list(pool.map(download,paths))
(D/'download-manifest.json').write_text(json.dumps({'commit':commit,'sources':rows},indent=2)+'\n')
print('downloaded',len(rows),'fixed sources',sum(x['bytes']for x in rows),'bytes')
