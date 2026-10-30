"""Compile PostgreSQL18.0 from the pinned official source in user-owned paths."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
R=Path(__file__).resolve().parent;W=Path('/tmp/mq05-07-runtime')
commit='3d6a828938a5fa0444275d3d2f67b64ec3199eb7'
source=W/('postgres-'+commit);tool=W/'toolchain'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
O=R/'builds'/('pg18-'+stamp);O.mkdir(parents=True)
B=W/('pg18-build-'+stamp);B.mkdir()
prefix=W/'pg18-install'
env=dict(os.environ,PATH=str(tool/'usr/bin')+':'+os.environ['PATH'],BISON_PKGDATADIR=str(tool/'usr/share/bison'),M4=str(tool/'usr/bin/m4'))
shutil.copy2(__file__,O/'build_postgres.py')
commands=[];status='failed';error=None
def run(name,args,timeout=1200):
 with (O/(name+'.stdout.txt')).open('wb') as out,(O/(name+'.stderr.txt')).open('wb') as err:
  result=subprocess.run([str(x) for x in args],cwd=B,env=env,stdout=out,stderr=err,timeout=timeout)
 commands.append({'name':name,'argv':[str(x) for x in args],'exitCode':result.returncode,'finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 (O/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 print(name,'exit',result.returncode,flush=True)
 if result.returncode:raise RuntimeError(name+' failed; see '+str(O))
try:
 assert source.is_dir() and (tool/'usr/bin/bison').is_file() and (tool/'usr/bin/flex').is_file()
 run('configure',[source/'configure','--prefix='+str(prefix),'--without-readline','--without-icu','--without-zlib'])
 run('make',['make','-j4'])
 run('install',['make','install'])
 run('postgres-version',[prefix/'bin/postgres','--version'])
 run('psql-version',[prefix/'bin/psql','--version'])
 assert '18.0' in (O/'postgres-version.stdout.txt').read_text()
 bins=[]
 for p in list((prefix/'bin').iterdir())+list((prefix/'lib').glob('libpq.so*')):
  if p.is_file():bins.append({'path':str(p.relative_to(prefix)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 (O/'installed-files-sha256.json').write_text(json.dumps(bins,indent=2)+'\n');status='pass'
except BaseException as exc:error=repr(exc);raise
finally:
 result={'status':status,'error':error,'commit':commit,'version':'18.0','sourceArchiveSHA256':hashlib.sha256((W/('postgres-'+commit+'.tar.gz')).read_bytes()).hexdigest(),'prefix':str(prefix),'buildDirectory':str(B),'outputDirectory':str(O),'systemInstall':False,'finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (O/'result.json').write_text(json.dumps(result,indent=2)+'\n');(R/'postgres-build-latest.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result),flush=True)
