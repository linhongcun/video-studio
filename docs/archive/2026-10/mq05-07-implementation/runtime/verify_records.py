"""Read-only verification of recorded evidence identities; does not rerun services."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=json.loads((R/'runtime-files-sha256.json').read_text())
for row in index['files']:
 p=R/row['file'];assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['file']
summary=json.loads((R/'experiment-summary.json').read_text());total=0
for item in summary['experiments']:
 D=R/item['directory'];result=json.loads((D/'result.json').read_text());assert result['status']=='pass'
 for row in json.loads((D/'files-sha256.json').read_text()):
  p=D/row['file'];assert p.is_file() and sha(p)==row['sha256'],p
 count=sum(line.startswith('ASSERT PASS ') for p in D.glob('*.stdout.txt') for line in p.read_text().splitlines());assert count==item['actualPrintedAssertions'],(item['episode'],count)
 cleanup=json.loads((D/'cleanup.json').read_text())
 assert all(x['stopped'] for x in cleanup['processes']) if 'processes' in cleanup else cleanup['brokerStopped']
 for p in cleanup.get('removedOwnedPaths',[]):assert not Path(p).exists(),p
 total+=count
assert total==summary['actualPrintedAssertions']==121
print(json.dumps({'status':'pass','readOnly':True,'indexedFiles':len(index['files']),'realRuntimeAssertions':total,'experiments':3,'note':'Identity, recorded assertion counts and stopped-process cleanup evidence verified; this does not rerun Kafka/PostgreSQL or replace source/causal review.'}))
