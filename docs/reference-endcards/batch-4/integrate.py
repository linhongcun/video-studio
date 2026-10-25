"""Reuse the verified appendix publication copier with this batch's inputs."""
import importlib.util
from pathlib import Path

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('batch4_publication_engine', OUT.parent/'batch-3/integrate.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
engine.OUT = OUT

if __name__ == '__main__':
    engine.main()
