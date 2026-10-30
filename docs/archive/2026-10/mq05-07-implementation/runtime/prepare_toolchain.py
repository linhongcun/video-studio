"""Download from the explicitly allowed official Debian current package source.

The denied snapshot host is not retried. Signed APT metadata and package hashes
are checked by APT in a task-owned configuration/cache. No system install.
"""
from pathlib import Path
import datetime,hashlib,json,os,subprocess
R=Path(__file__).resolve().parent/'dependencies'
W=Path('/tmp/mq05-07-runtime/apt-allowed');W.mkdir(parents=True,exist_ok=True)
for d in ['lists/partial','cache/archives/partial','debs']:(W/d).mkdir(parents=True,exist_ok=True)
sources=W/'allowed.sources'
sources.write_text('Types: deb\nURIs: https://deb.debian.org/debian\nSuites: trixie\nComponents: main\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\n')
options=['-o','Dir::Etc::sourcelist='+str(sources),'-o','Dir::Etc::sourceparts=-','-o','Dir::State::lists='+str(W/'lists'),'-o','Dir::Cache='+str(W/'cache'),'-o','APT::Sandbox::User=agent','-o','Debug::NoLocking=true']
commands=[]
def run(name,args):
 with (R/(name+'.stdout.txt')).open('wb') as out,(R/(name+'.stderr.txt')).open('wb') as err:
  proc=subprocess.run(args,cwd=W/'debs',stdout=out,stderr=err)
 commands.append({'name':name,'argv':args,'exitCode':proc.returncode,'finishedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 (R/'toolchain-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
 print(name,proc.returncode,flush=True)
 if proc.returncode:raise RuntimeError('Toolchain step failed; see '+name)
run('allowed-apt-update',['apt-get',*options,'update'])
out=(R/'allowed-apt-update.stdout.txt').read_text()+(R/'allowed-apt-update.stderr.txt').read_text()
assert 'Failed to fetch' not in out and 'Err:' not in out,'Do not mistake APT exit0 for metadata success'
run('allowed-package-metadata',['apt-cache',*options,'show','bison','flex','m4'])
run('allowed-download-build-tools',['apt-get',*options,'download','bison','flex','m4'])
T=Path('/tmp/mq05-07-runtime/toolchain');T.mkdir(exist_ok=True)
packages=[]
for p in sorted((W/'debs').glob('*.deb')):
 run('extract-'+p.name,['dpkg-deb','-x',str(p),str(T)])
 packages.append({'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
(R/'toolchain-packages.json').write_text(json.dumps({'source':'https://deb.debian.org/debian trixie main','systemInstall':False,'taskToolchain':str(T),'packages':packages},indent=2)+'\n')
env=dict(os.environ,PATH=str(T/'usr/bin')+':'+os.environ['PATH'],BISON_PKGDATADIR=str(T/'usr/share/bison'))
for name in ['bison','flex','m4']:
 with (R/(name+'-version.txt')).open('wb') as out:subprocess.run([name,'--version'],env=env,stdout=out,check=True)
print('USER_TOOLCHAIN_READY',flush=True)
