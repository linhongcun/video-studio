#!/usr/bin/env python3
"""Render the independent clarity revision with the existing bibliography pipeline."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import FunctionType

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'AGENTS.md').is_file())
PIPELINE = ROOT / 'episodes/_shared/render_with_references.py'
spec = importlib.util.spec_from_file_location('pirate_canonical_render_pipeline', PIPELINE)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)

def run(directory, verify_only=False):
    if directory.resolve() != HERE:
        raise ValueError('Use this entry only for this pirate-gold clarity revision')
    subprocess.run([sys.executable, str(HERE / 'freeze.py'), '--verify'], check=True)
    # Keep source checking, frozen input checks, body rendering and full media
    # verification in the canonical implementation. Only choose this adapter.
    adapted = FunctionType(pipeline.run.__code__,
                           dict(vars(pipeline),APPENDER=HERE/'references-adapter.py'),
                           pipeline.run.__name__,pipeline.run.__defaults__,
                           pipeline.run.__closure__)
    result = adapted(directory,verify_only)
    subprocess.run([sys.executable, str(HERE / 'freeze.py'), '--verify'], check=True)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('episode',type=Path)
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    print(json.dumps(run(args.episode,args.verify),ensure_ascii=False,indent=2))
