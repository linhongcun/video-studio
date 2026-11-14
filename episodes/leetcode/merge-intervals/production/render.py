#!/usr/bin/env python3
"""LC56 default render entry: shared production gates, local BT.709 appendix."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
from types import FunctionType

EP = Path(__file__).resolve().parent
ROOT = next(p for p in EP.parents if (p / 'AGENTS.md').is_file())
SHARED = ROOT / 'episodes/_shared/render_with_references.py'
APPENDER = EP / 'references_bt709.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


shared = load('lc56_shared_render_gates', SHARED)
appender = load('lc56_local_bibliography', APPENDER)


def verify_freeze(directory):
    # Keep every canonical required-source/output-exclusion check. Additionally
    # bind this entry and the complete actual palette/color adapter closure.
    shared.verify_freeze(directory)
    manifest = shared.read(directory / 'source-sha256.json')
    frozen = {shared.resolve_frozen_path(directory / 'source-sha256.json', rel): expected
              for rel, expected in manifest.items()}
    for path in [Path(__file__).resolve(), *appender.dependency_files()]:
        if frozen.get(path.resolve()) != shared.digest(path):
            raise ValueError(f'Unfrozen LC56 rendering dependency: {path.relative_to(ROOT)}')


def run(directory, verify_only=False):
    # The shared run still performs sources/freeze/body/receipt/delivery checks;
    # only its appender path and additional input verification are selected here.
    entry = FunctionType(shared.run.__code__,
                         dict(vars(shared), APPENDER=APPENDER, verify_freeze=verify_freeze),
                         shared.run.__name__, shared.run.__defaults__, shared.run.__closure__)
    return entry(directory, verify_only)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(EP, args.verify), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
