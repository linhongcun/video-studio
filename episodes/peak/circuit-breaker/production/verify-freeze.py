
# Resolve episode storage independently of its series and revision depth.
import sys as _layout_sys
from pathlib import Path as _LayoutPath
_layout_root = next(parent for parent in _LayoutPath(__file__).resolve().parents
                    if (parent / 'AGENTS.md').is_file() and (parent / 'site/package.json').is_file())
_layout_sys.path.insert(0, str(_layout_root / 'episodes/_shared'))
from episode_paths import production_directory, publication_directory, resolve_repo_path, episode_slug, resolve_frozen_path
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
m=json.loads((D/'source-sha256.json').read_text())
bad=[p for p,h in m.items() if not (resolve_frozen_path(D/'source-sha256.json', p)).is_file() or hashlib.sha256((resolve_frozen_path(D/'source-sha256.json', p)).read_bytes()).hexdigest()!=h]
print('freeze verify', 'PASS' if not bad else 'FAIL', len(m), 'inputs',bad)
raise SystemExit(bool(bad))
