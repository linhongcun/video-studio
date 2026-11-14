import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PRODUCTION = Path(__file__).resolve().parents[1]


class RenderBodyCleanCheckoutTests(unittest.TestCase):
    def run_render_body(self, existing_publication=None):
        temporary = tempfile.TemporaryDirectory(prefix='lc56-render-body-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        production = root / 'episodes/leetcode/merge-intervals/production'
        (root / 'AGENTS.md').write_text('')
        (root / 'site').mkdir()
        (root / 'site/package.json').write_text('{}')
        for relative in ('scripts/require_formal_inputs.py', 'freeze.py'):
            path = production / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('pass\n')
        checker = root / 'episodes/_shared/check_encoded_episode.py'
        checker.parent.mkdir(parents=True)
        checker.write_text('pass\n')
        shutil.copy2(PRODUCTION / 'render_body.py', production / 'render_body.py')
        output = production / 'remotion/out'
        output.mkdir(parents=True)
        (output / 'mix-report.json').write_text('{}')
        (output / 'body.mp4').write_bytes(b'new-body')
        (production / 'render-result.json').write_text('{}')
        receipt = production / 'revisions/reference-endcards/reference-appendix.json'
        receipt.parent.mkdir(parents=True)
        receipt.write_text('{}')
        if existing_publication is not None:
            (production / 'video.mp4').write_bytes(existing_publication)
        npm = root / 'bin/npm'
        npm.parent.mkdir()
        npm.write_text('#!/bin/sh\nexit 0\n')
        npm.chmod(0o755)
        environment = dict(os.environ, PATH=f'{npm.parent}:{os.environ.get("PATH", "")}')
        result = subprocess.run(
            [sys.executable, str(production / 'render_body.py')],
            capture_output=True, text=True, env=environment)
        return production, result

    def test_clean_render_with_reference_receipt_needs_no_prior_publication(self):
        production, result = self.run_render_body()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((production / 'video.mp4').read_bytes(), b'new-body')
        self.assertFalse((production / 'remotion/out/prior-publication.mp4').exists())

    def test_existing_publication_is_restored_after_body_render(self):
        production, result = self.run_render_body(b'old-final')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((production / 'video.mp4').read_bytes(), b'old-final')
        self.assertEqual(
            (production / 'remotion/out/prior-publication.mp4').read_bytes(), b'old-final')


if __name__ == '__main__':
    unittest.main()
