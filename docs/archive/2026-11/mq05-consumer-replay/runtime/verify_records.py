"""Read-only verification of this finalized new runtime index and accepted raw evidence."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def obs(text,kind):return[json.loads(s.split(' ',2)[2])for s in text.splitlines()if s.startswith('OBS '+kind+' ')]
def main():
 index=read(R/'runtime-files-sha256.json');assert index
 for rel,h in index.items():
  p=(R/rel).resolve();assert p.is_relative_to(R)and p.is_file()and sha(p)==h,rel
 summary=read(R/'experiment-summary.json');p=R/summary['acceptedReport'];assert sha(p)==summary['acceptedReportSHA256'];report=read(p);assert report['pass']and report['allObservedAssertionsPass']and len(report['cases'])==3 and report['ownedTempDataRemoved'];O=p.parent
 assert all(x['stopped']for x in report['cleanup'])and all(x['closed']for x in report['ports']);commands=read(O/'commands.json');assert all(c['exitCode']==c['expectedExitCode']for c in commands);assert sum(c['expectedExitCode']==86 for c in commands)==3
 checks=[]
 for f in O.glob('*.stdout.txt'):checks.extend(obs(f.read_text(),'ASSERT'))
 assert len(checks)==report['assertions']==91 and all(c['data']['pass']for c in checks)
 for c in report['cases']:
  name=c['id'];want=1 if name=='early-commit'else 0;setup=(O/(name+'-setup.stdout.txt')).read_text();topicid=obs(setup,'TOPIC_IDENTITY')[-1]['data']['topicId'];initial=obs(setup,'INITIAL_DURABLE_OFFSET')[-1]['data'];assert initial['committed']==0
  metadata=(O/(name+'-setup.stderr.txt')).read_text();assert any(c['topic']in line and topicid in line and 'replicaNodes=[1]'in line and'isrNodes=[1]'in line for line in metadata.splitlines())
  restored=obs((O/(name+'-B-restart.stdout.txt')).read_text(),'ASSIGNED_RESTORED')[-1]['data'];assert restored['storedBrokerOffset']==restored['positionBeforeRecordDelivery']==want and restored['explicitSeekUsed']is False
  fetch=(O/(name+'-B-restart.stderr.txt')).read_text();assert c['actualFetchWitnessLines']and all(line in fetch and'Sending FETCH request'in line and'fetchOffset='+str(want)in line and topicid in line for line in c['actualFetchWitnessLines'])
  assert c['physicalLogRecords']==1 and sha(R/c['physicalLogCopy'])==c['physicalLogSHA256'];dump=(O/(name+'-physical-log.stdout.txt')).read_text();records=[line for line in dump.splitlines()if re.search(r'^\s*\|\s*offset:\s*0\b',line)];assert len(records)==1 and'E01'in records[0]and'7042'in records[0]and'isvalid: true'in dump.lower()
  for key in ['afterA','afterB']:assert c[key]['logStart']==0 and c[key]['LEO']==1
 assert summary['primaryProbeJVMs']==15 and summary['intentionalHalts']==3
 print(json.dumps({'pass':True,'readOnly':True,'indexedFiles':len(index),'acceptedCases':3,'actualAssertions':91,'actualProbeJVMs':15,'reportSHA256':sha(p),'indexSHA256':sha(R/'runtime-files-sha256.json')},indent=2))
if __name__=='__main__':main()
