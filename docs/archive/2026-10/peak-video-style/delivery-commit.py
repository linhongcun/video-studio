from pathlib import Path
import json, os, subprocess, sys

ROOT = Path.cwd().resolve()
W = ROOT / 'work/peak-video-style'
BRANCH = 'delivery/peak-video-style-20261029'
DEST = 'design/peak-video-style-20261029'
def git(*args, data=None, env=None):
    return subprocess.check_output(['git', *args], input=data, cwd=ROOT, env=env).decode().strip()

statefile = W / 'delivery-state.json'
prior = json.loads(statefile.read_text()) if statefile.exists() else None
parent = prior['head'] if prior else git('rev-parse', 'HEAD')
index = W / 'delivery.index'
index.unlink(missing_ok=True)
env = {**os.environ, 'GIT_INDEX_FILE': str(index)}
git('read-tree', parent, env=env)
files = {}
package_update = '--package' in sys.argv
if prior and not package_update:
    files['publication.json'] = W / 'publication.json'
    if (W / 'delivery-final-README.md').exists(): files['README.md'] = W / 'delivery-final-README.md'
else:
    package_dir = W / 'delivery'
    manifest = json.loads((package_dir / 'package-manifest.json').read_text())
    for p in package_dir.iterdir():
        if p.is_file() and (p.suffix in ['.zip', '.json'] or p.name == 'README.md'): files[p.name] = p
    assert any(p.suffix == '.zip' for p in files.values())
for name, p in files.items():
    blob = git('hash-object', '-w', str(p))
    git('update-index', '--add', '--cacheinfo', '100644,' + blob + ',' + DEST + '/' + name, env=env)
# The inherited tree belongs to the exact already-committed candidate. In a
# partial clone its unchanged historical media may be promisor objects; avoid
# hydrating every old binary just to add this independently hashed package.
tree = git('write-tree', '--missing-ok', env=env)
message = ('docs: record peak-series style publication [skip ci]' if prior and not package_update else 'chore: package peak-series videos and series covers [skip ci]') + '\n\nCo-authored-by: Codex <codex@openai.com>\n'
commit = git('commit-tree', tree, '-p', parent, data=message.encode())
git('update-ref', 'refs/heads/' + BRANCH, commit, *( [parent] if prior else [] ))
git('push', 'origin', BRANCH)
state = {'branch': BRANCH, 'head': commit, 'packageCommit': commit if package_update or not prior else prior['packageCommit'], 'directory': DEST}
statefile.write_text(json.dumps(state, indent=2) + '\n')
print(json.dumps(state))
