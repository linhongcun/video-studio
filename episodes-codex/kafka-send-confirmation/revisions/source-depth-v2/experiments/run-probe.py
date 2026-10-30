from pathlib import Path
import hashlib,json,subprocess,urllib.request,datetime
HERE=Path(__file__).resolve().parent
D=HERE.parent
dep=json.loads((HERE/'dependency.json').read_text())
jar=HERE/'vendor/kafka-clients-4.4.0.jar'
if not jar.exists():
    jar.parent.mkdir(exist_ok=True)
    with urllib.request.urlopen(dep['url'],timeout=60) as response:
        jar.write_bytes(response.read())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(jar)==dep['sha256']
sources=[D/'sources/ProducerStateEntry.java',D/'sources/BatchMetadata.java']
before={str(p.relative_to(D)):sha(p)for p in sources}
classes=HERE/'classes';classes.mkdir(exist_ok=True)
command=['java','-m','jdk.compiler/com.sun.tools.javac.Main','-cp',str(jar),'-d',str(classes),*[str(p)for p in sources],str(HERE/'ProducerStateEntryProbe.java')]
subprocess.run(command,check=True)
raw=subprocess.check_output(['java','-cp',str(classes)+':'+str(jar),'org.apache.kafka.storage.internals.log.ProducerStateEntryProbe'],text=True)
result=json.loads(raw)
assert result['passed']and before=={str(p.relative_to(D)):sha(p)for p in sources}
result.update(checkedAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourcesSHA256=before,dependency=dep,javaVersion=subprocess.run(['java','-version'],capture_output=True,text=True).stderr.splitlines()[0],limitation='Source-level unit execution of the two unmodified official classes. Input RecordBatch is a dynamic proxy fixture, not serialized records. ProducerStateManager lookup, broker append/network, acks and failure injection are read-source/teaching-model evidence, not executed by this fixture.')
(HERE/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
