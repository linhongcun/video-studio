#!/usr/bin/env python3
"""Compile three unchanged fixed Kafka sources and exercise assignment/local eligibility."""
from pathlib import Path
import argparse,subprocess,json,hashlib,os,datetime
D=Path(__file__).resolve().parents[1];E=D/'experiment'
p=argparse.ArgumentParser(__doc__);p.add_argument('--libs',type=Path,default=Path('/tmp/mq-source-depth-runtime/kafka_2.13-4.4.0/libs'));args=p.parse_args()
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
manifest=json.loads((D/'sources/download-manifest.json').read_text());declared={Path(r['upstreamPath']).name:r['sha256'] for r in manifest['sources']}
names=['RangeAssignor.java','AbstractPartitionAssignor.java','SubscriptionState.java'];assert all(sha(D/'sources'/n)==declared[n] for n in names)
jars=sorted(args.libs.glob('*.jar'));assert jars;cp=os.pathsep.join(str(p.resolve()) for p in jars);classes=E/'classes';classes.mkdir(exist_ok=True)
compile_command=['java','com.sun.tools.javac.Main','-proc:none','-cp',cp,'-d',str(classes),*[str(D/'sources'/n) for n in names],str(E/'RangeExecution.java')]
r=subprocess.run(compile_command,capture_output=True,text=True);(E/'compiler.stdout.txt').write_text(r.stdout);(E/'compiler.stderr.txt').write_text(r.stderr);assert r.returncode==0,r.stderr
run_command=['java','-cp',str(classes)+os.pathsep+cp,'RangeExecution'];r=subprocess.run(run_command,capture_output=True,text=True);(E/'actual.stdout.txt').write_text(r.stdout);(E/'actual.stderr.txt').write_text(r.stderr);assert r.returncode==0,r.stderr
assert r.stdout.count('LOADED\t')==3 and all(str(classes.resolve()) in line for line in r.stdout.splitlines() if line.startswith('LOADED\t'))
assert 'PASS\treal-unmodified-RangeAssignor-and-SubscriptionState' in r.stdout
report={'passed':True,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceCommit':manifest['commit'],'compiledSourceSHA256':{n:sha(D/'sources'/n) for n in names},'driverSHA256':sha(E/'RangeExecution.java'),'runScriptSHA256':sha(Path(__file__)),'compileCommand':[x if x!=cp else '<explicit-classpath-below>' for x in compile_command],'runCommand':[x if x!=str(classes)+os.pathsep+cp else '<new-compiled-classes-first>:<explicit-classpath-below>' for x in run_command],'classpath':[{'path':str(p),'sha256':sha(p)} for p in jars],'actualLoadedClassLocations':[l for l in r.stdout.splitlines() if l.startswith('LOADED\t')],'stdoutSHA256':sha(E/'actual.stdout.txt'),'cases':['notify:two partitions/three shuffled members -> [0],[1],[]','points:two partitions/one independent member -> [0,1]','three partitions/three members -> [0],[1],[2]','all installed members: no valid position -> no fetchable; seek0 -> assigned subset; pause -> no fetchable'],'scope':'Actual unchanged Java implementation of RangeAssignor, AbstractPartitionAssignor and SubscriptionState compiled against verified official 4.4.0 distribution libraries. In-memory algorithm/state experiment; no Broker, group protocol, or actual Fetch network run started by this script.'}
(E/'actual-execution.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':True,'compiledSources':names,'actualLoadedClassLocations':report['actualLoadedClassLocations'],'scope':report['scope']},ensure_ascii=False))
