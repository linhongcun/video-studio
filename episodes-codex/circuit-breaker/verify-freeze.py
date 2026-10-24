from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
m=json.loads((D/'source-sha256.json').read_text())
bad=[p for p,h in m.items() if not (D/p).is_file() or hashlib.sha256((D/p).read_bytes()).hexdigest()!=h]
print('freeze verify', 'PASS' if not bad else 'FAIL', len(m), 'inputs',bad)
raise SystemExit(bool(bad))
