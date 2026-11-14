import hashlib
import shutil
from pathlib import Path

EP = Path(__file__).resolve().parents[1]
source = EP / 'storyboard.json'
target = EP / 'remotion/src/placeholders/storyboard.json'
shutil.copy2(source, target)
if source.read_bytes() != target.read_bytes():
    raise SystemExit('Remotion storyboard synchronization failed.')
digest = hashlib.sha256(source.read_bytes()).hexdigest()
print(f'Remotion storyboard synchronized: {digest}')
