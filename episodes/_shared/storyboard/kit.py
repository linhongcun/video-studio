"""Shared plumbing for the storyboard generators (layout / make_covers / build_sb / validate).

Everything episode-specific lives in a spec module (a plain .py file) passed with --spec.
Inputs are looked up by logical name (script.md, words.json, voice.wav, voice/cues.json, ...):
  1. an --inputs JSON map {name: path}; relative paths there are relative to the repo root;
  2. otherwise <episode-dir>/<name>.
Nothing here writes into the episode dir unless an output path says so."""
import hashlib, importlib.util, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # episodes/_shared/storyboard
SHARED = HERE.parent                            # episodes/_shared
ROOT = HERE.parents[2]                          # repo root
for p in (str(HERE), str(SHARED)):
    if p not in sys.path: sys.path.insert(0, p)


def load_spec(path, name='spec'):
    path = Path(path).resolve()
    if str(path.parent) not in sys.path: sys.path.insert(0, str(path.parent))
    sp = importlib.util.spec_from_file_location(f'{name}_{path.stem}', path)
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
    mod.__spec_path__ = path
    return mod


def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Inputs:
    """Logical input name -> Path."""
    def __init__(self, episode_dir, inputs_json=None, extra=None):
        self.dir = Path(episode_dir).resolve() if episode_dir else None
        self.map = {}
        if inputs_json:
            for k, v in json.loads(Path(inputs_json).read_text()).items():
                if k.startswith('_'): continue      # "_comment" etc.
                v = Path(v); self.map[k] = v if v.is_absolute() else ROOT / v
        for k, v in (extra or {}).items(): self.map[k] = Path(v).resolve()

    def __call__(self, name):
        if name in self.map: return self.map[name]
        assert self.dir is not None, f'no --episode-dir and no --inputs entry for {name}'
        return self.dir / name

    def text(self, name): return self(name).read_text()
    def json(self, name): return json.loads(self(name).read_text())
    def exists(self, name): return self(name).exists()


def add_input_args(ap):
    ap.add_argument('--spec', required=True, help='episode spec .py')
    ap.add_argument('--episode-dir', help='default location of every input (script.md, words.json, voice.wav, ...)')
    ap.add_argument('--inputs', help='JSON map {logical name: path}; relative paths are repo-root relative')
    ap.add_argument('--input', action='append', default=[], metavar='NAME=PATH', help='override one input (repeatable)')


def inputs_from(args):
    extra = dict(x.split('=', 1) for x in args.input)
    return Inputs(args.episode_dir, args.inputs, extra)


def write_json(path, obj, indent):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=indent) + '\n')
    return path


def default_out(args, name):
    assert args.episode_dir, f'--out is required without --episode-dir ({name})'
    return Path(args.episode_dir) / name
