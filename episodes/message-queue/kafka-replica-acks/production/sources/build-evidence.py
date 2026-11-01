from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent;D=S.parent;R=next(p for p in D.parents if (p/'AGENTS.md').is_file());C='1156b2752aaa28eafc0b4c4d387e63356793268d';date='2026-11-01'
manifest=json.loads((S/'download-manifest.json').read_text());paths={x['title']:x['upstreamPath']for x in manifest['files']}
def lines(file,a,b):return '\n'.join((S/file).read_text().splitlines()[a-1:b])
def excerpt(file,fragment):
 ls=(S/file).read_text().splitlines();i=next(i for i,x in enumerate(ls,1)if fragment in x);return {'text':ls[i-1].strip(),'locator':f'{file} line{i}','evidence':str((S/file).relative_to(R))}
def block(file,a,b):return {'text':lines(file,a,b).strip(),'locator':f'{file} lines{a}–{b}','evidence':str((S/file).relative_to(R))}
def src(id,file,support,spans,q):
 m=S/(file+'.metadata.json');meta=json.loads(m.read_text());assert meta['name']==file
 return {'id':id,'organization':'Apache Kafka','title':file,'titleEvidence':{'locator':f'Fixed commit GitHub Contents API .name = {file}; {meta["url"]}','evidence':str(m.relative_to(R))},'version':'Apache Kafka / Java4.4.0; fixed commit '+C,'url':f'https://github.com/apache/kafka/blob/{C}/{paths[file]}','supports':support,'sections':'; '.join(f'{file}:{a}–{b}'for a,b in spans),'verification':{'status':'verified','checkedAt':date,'method':'Fresh fixed-commit official raw GET and raw Contents API response; .name/path/base64 decoded bytes verified. Read only listed execution/config contexts; not all downloaded files or all lines. Apache Kafka official repository/NOTICE supports institution; no public individual author attribution in these files, so author omitted.','sourceUrl':f'https://raw.githubusercontent.com/apache/kafka/{C}/{paths[file]}','evidence':str((S/'source-evidence.json').relative_to(R)),'commit':C,'sha256':hashlib.sha256((S/file).read_bytes()).hexdigest()},'quotation':q}
rs=[src('R1','Partition.scala',['acksall下当前ISR不足minISR会在appendAsLeader之前拒绝；足够才追加。','本例稳定集合共同进度决定HW，HW达到requiredOffset后还检查minISR；underMinISR不推进HW。','Follower下一次Fetch报告的位置更新Leader已知进度，不把实际Follower追加视为Leader已即时知晓。'],[(244,248),(767,817),(947,1040),(1219,1243),(1280,1323)],block('Partition.scala',968,979)),
src('R2','ReplicaManager.scala',['Produce请求追加后以lastOffset+1创建所需位置。','acksall且本地追加成功才安装DelayedProduce；acks1不进入这项复制等待并可回复。'],[(635,677),(835,849),(878,917),(1356,1367),(1395,1440)],excerpt('ReplicaManager.scala','result.logAppendSummary.lastOffset + 1')),
src('R3','ReplicaFetcherThread.scala',['Follower处理Fetch响应时在自己的日志追加相同记录；再从响应学习HW，不搬走Leader记录。'],[(59,61),(111,150)],block('ReplicaFetcherThread.scala',132,145)),
src('R4','DelayedProduce.java',['每个待确认分区调用完成判据；满足条件或产生错误才退出等待，完成后回调返回状态。'],[(110,119),(140,173),(185,195)],block('DelayedProduce.java',148,155)),
src('R5','PartitionChangeBuilder.java',['ELR关闭且非同步选主关闭的本例，新的clean leader必须在目标ISR且满足可用资格；不是数据副本投票。'],[(254,281),(286,322)],{'text':lines('PartitionChangeBuilder.java',320,321).strip(),'locator':'PartitionChangeBuilder.java lines320–321','evidence':str((S/'PartitionChangeBuilder.java').relative_to(R))})]
a=[src('A1','Replica.java',['Leader把Follower Fetch报告的offset metadata存为ReplicaState；随后才能据该已知位置评估共同进度。'],[(46,101)],{'text':lines('Replica.java',93,101).strip(),'locator':'Replica.java lines93–101','evidence':str((S/'Replica.java').relative_to(R))}),
src('A2','UnifiedLog.java',['本地追加的flush由独立flushInterval条件触发；不能从acksall这一等待条件推断所有副本每次都fsync。'],[(1268,1302),(2250,2296)],excerpt('UnifiedLog.java','if (localLog.unflushedMessages() >= config().flushInterval) flush(false);')),
src('A3','TopicConfig.java',['配置文档明确RF3且ISR3时acksall须三份确认，即使minISR小于3；ELR开启会改变语义，因此本例显式关闭。'],[(218,232)],block('TopicConfig.java',219,232))]
extra=[('KafkaApis.scala',401,419),('KafkaApis.scala',546,559),('AbstractFetcherThread.scala',373,395),('ProducerConfig.java',131,150),('ProducerConfig.java',370,378),('ReplicationControlManager.java',2095,2144),('TopicConfig.java',58,73),('Replica.java',105,144)]
evidence=[]
for x in rs+a:
 file=x['title']
 for span in x['sections'].split('; '):
  ar=span.split(':')[-1].split('–');lo,hi=map(int,ar);evidence.append({'source':x['id'],'file':str((S/file).relative_to(R)),'lines':[lo,hi],'permalink':x['url']+f'#L{lo}-L{hi}','text':lines(file,lo,hi)})
for file,lo,hi in extra:evidence.append({'source':'supporting-context','file':str((S/file).relative_to(R)),'lines':[lo,hi],'permalink':f'https://github.com/apache/kafka/blob/{C}/{paths[file]}#L{lo}-L{hi}','text':lines(file,lo,hi)})
record={'checkedAt':date,'commit':C,'scope':'Actual selected execution/config scopes listed; source download count is not a full source-read claim. No broker experiment performed by this builder.','authorInstitution':{'organization':'Apache Kafka','individualAuthor':'No explicit public individual author byline in selected source files; omitted rather than attributing Git committers.','evidence':str((S/'NOTICE').relative_to(R)),'text':lines('NOTICE',1,5)},'claims':evidence}
(S/'source-evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
for file,sources in [('references.json',rs),('article-sources.json',a)]:
 for x in sources:assert x['quotation']['text']in(S/x['title']).read_text()
 value={'schemaVersion':1,'presentation':'title-author','episode':'kafka-replica-acks','heading':'参考资料','checkedAt':date,'timezone':'Asia/Shanghai','sources':sources};(D/file).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print('five video / three article sources, titles+continuous quotations exact; evidence scopes',len(evidence))
