"""Route later small batches through the unchanged batch-3 QA implementation.

Each invocation gets isolated module globals and explicit batch targets. No
historical script is edited, and discovering all older reference videos is
never used by these entry points.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def configure_batch(directory, allowed):
    directory = Path(directory).resolve()
    module = _load("reference_batch_adapter_" + directory.name, HERE / "batch-3/_qa.py")
    module.OUT = directory

    def targets():
        selected = module.read(directory / "startup.json")["selection"]
        module.ONLINE.require(selected == list(allowed), f"Unexpected {directory.name} selection")
        return selected

    module.targets = targets
    module.ONLINE.published_targets = targets
    module.ONLINE.REPORT = directory / "online-verification.json"
    return module


def browser_engine(adapter):
    # The preserved browser file imports its adapter as `_qa`. Bind that import
    # only while loading this isolated module, then restore the caller's state.
    previous = sys.modules.get("_qa")
    sys.modules["_qa"] = adapter
    try:
        return _load("reference_browser_" + adapter.OUT.name, HERE / "batch-3/check-browser.py")
    finally:
        if previous is None:
            sys.modules.pop("_qa", None)
        else:
            sys.modules["_qa"] = previous
