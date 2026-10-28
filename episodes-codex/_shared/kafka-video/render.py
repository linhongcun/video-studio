#!/usr/bin/env python3
"""Use the existing checked render pipeline with Kafka-colored bibliography cards."""
import argparse
import importlib.util
import json
from pathlib import Path
from types import FunctionType

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent/'render_with_references.py'
spec = importlib.util.spec_from_file_location('kafka_canonical_render_pipeline', PIPELINE)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)

def run(directory, verify_only=False):
    # Keep source checking, frozen input checks, body rendering and full media
    # verification in the canonical implementation. Only choose this adapter.
    adapted = FunctionType(pipeline.run.__code__,
                           dict(vars(pipeline),APPENDER=HERE/'references.py'),
                           pipeline.run.__name__,pipeline.run.__defaults__,
                           pipeline.run.__closure__)
    return adapted(directory,verify_only)

if __name__=='__main__':
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('episode',type=Path)
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    print(json.dumps(run(args.episode,args.verify),ensure_ascii=False,indent=2))
