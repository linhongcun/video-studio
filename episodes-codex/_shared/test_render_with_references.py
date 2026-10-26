"""Exercise the new entry point with a short real H.264/AAC body, never TTS."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
WRAPPER = Path(__file__).with_name('render_with_references.py')
SHARED = WRAPPER.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


class RenderWithReferences(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='.reference-wrapper-test-', dir=ROOT/'episodes-codex')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.remotion = self.directory/'remotion'
        self.remotion.mkdir()
        self.evidence = self.directory/'evidence.md'
        self.evidence.write_text('Synthetic integration-test evidence, not a published reference.\n'
                                 'Reference-render integration fixture\n')
        self.references = {
            'schemaVersion': 1, 'presentation': 'title-author',
            'episode': self.directory.name, 'checkedAt': '2026-10-25',
            'sources': [{'id': 'R1', 'organization': 'Synthetic test fixture',
                         'title': 'Reference-render integration fixture', 'version': '2026',
                         'url': 'https://example.com/synthetic-reference', 'sections': '§1',
                         'supports': ['Synthetic supported claim, not actual video content'],
                         'titleEvidence': {'locator': 'Fixture original title, line 2',
                                           'evidence': str(self.evidence.relative_to(ROOT))},
                         'verification': {'status': 'verified', 'checkedAt': '2026-10-25',
                                          'evidence': str(self.evidence.relative_to(ROOT))}}],
        }
        write(self.directory/'references.json', self.references)
        (self.directory/'article.mdx').write_text('Synthetic test article\nhttps://example.com/synthetic-reference\n')
        write(self.directory/'storyboard.json', {
            'meta': {'width': 1280, 'height': 720, 'fps': 30, 'durationInFrames': 6,
                     'unvoicedEndCard': {'kind': 'full-python-solution', 'from': 4, 'durationInFrames': 2}},
        })
        self.package = {'name': 'synthetic-reference-wrapper-test', 'version': '1.0.0', 'scripts': {
            'render': 'python3 ../../_shared/render_with_references.py ..',
            'render:body': 'python3 make-body.py',
        }}
        write(self.remotion/'package.json', self.package)
        (self.remotion/'make-body.py').write_text('''from pathlib import Path
import subprocess
d = Path(__file__).resolve().parent
(d.parent/'body-started').write_text('body command was executed')
(d/'out').mkdir(exist_ok=True)
# Six frames: four body frames, then a pre-existing two-frame code-card fixture.
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
 'color=c=0x0f172a:size=1280x720:rate=30:duration=0.2', '-f', 'lavfi', '-i',
 'sine=frequency=440:sample_rate=48000:duration=0.2', '-vf',
 "drawtext=text='CODE CARD':fontsize=60:fontcolor=white:x=100:y=250:enable='gte(n,4)'",
 '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
 '-profile:v', 'high', '-level:v', '4.0', '-video_track_timescale', '90000',
 '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(d/'out/body.mp4')], check=True)
''')
        self.freeze()

    def freeze(self):
        files = [self.directory/name for name in ('references.json', 'article.mdx', 'evidence.md', 'storyboard.json')]
        files += [self.remotion/'package.json', self.remotion/'make-body.py', WRAPPER,
                  SHARED/'append_references_bibliography.py', SHARED/'append_references_original.py',
                  SHARED/'append_references.py',
                  SHARED/'requirements-reference-appendix.txt',
                  ROOT/'episodes/_shared/theme/pageTheme.ts', ROOT/'site/scripts/check-references.mjs']
        write(self.directory/'source-sha256.json', {os.path.relpath(p, self.directory): sha(p) for p in files})

    def execute(self, *arguments):
        return subprocess.run([sys.executable, str(WRAPPER), str(self.directory), *arguments],
                              cwd=ROOT, capture_output=True, text=True, timeout=40)

    def test_invalid_sources_fail_before_body_starts(self):
        self.references['sources'] = []
        write(self.directory/'references.json', self.references)
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('sources must not be empty', result.stderr)
        self.assertFalse((self.directory/'body-started').exists())

    def test_changed_frozen_input_fails_before_body_starts(self):
        with (self.remotion/'make-body.py').open('a') as handle:
            handle.write('\n# A changed source after freezing.\n')
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Frozen input changed', result.stderr)
        self.assertFalse((self.directory/'body-started').exists())

    def test_historical_source_presentation_is_rejected_before_body_starts(self):
        self.references['presentation'] = 'original-title-quote'
        write(self.directory/'references.json', self.references)
        self.freeze()
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("presentation 'title-author'", result.stderr)
        self.assertFalse((self.directory/'body-started').exists())

    def test_recursive_render_body_is_rejected_without_starting_real_body(self):
        self.package['scripts']['render:body'] = 'npm run render'
        write(self.remotion/'package.json', self.package)
        self.freeze()
        result = self.execute()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Recursive render:body', result.stderr)
        self.assertFalse((self.directory/'body-started').exists())

    def test_complete_body_including_code_card_gets_appendix_and_verified_delivery(self):
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout[-4000:])
        receipt = json.loads((self.directory/'reference-appendix.json').read_text())
        media = json.loads((self.directory/'reference-appendix-media-check.json').read_text())
        rendered = json.loads((self.directory/'render-result.json').read_text())
        self.assertEqual(receipt['bodyFrames'], 6)
        self.assertEqual(receipt['appendix']['from'], 6, 'references must follow the complete body, including code card')
        self.assertEqual(receipt['appendix']['durationInFrames'], 150)
        self.assertEqual(receipt['finalVideoFrames'], 156)
        self.assertEqual(receipt['outputSHA256'], sha(self.directory/'video.mp4'))
        self.assertEqual(receipt['presentation'], 'title-author')
        self.assertEqual(receipt['sourceTitles'], [{'id': 'R1', 'title': 'Reference-render integration fixture'}])
        self.assertEqual(receipt['quotations'], [])
        self.assertEqual(receipt['bibliography'], [{'id': 'R1', 'title': 'Reference-render integration fixture',
                                                  'credit': 'Synthetic test fixture'}])
        self.assertEqual(receipt['layout'], {'kind': 'title-author-single-column', 'maxItemsPerPage': 4,
                                             'renderedFields': ['title', 'credit'], 'quotesRendered': False})
        self.assertEqual(receipt['inputs']['generatorSHA256'], sha(SHARED/'append_references_bibliography.py'))
        self.assertEqual(receipt['dependencies']['oldEngineSHA256'], sha(SHARED/'append_references.py'))
        self.assertEqual(receipt['dependencies']['originalRendererSHA256'], sha(SHARED/'append_references_original.py'))
        self.assertEqual(rendered['publicationMetadata']['referenceAppendix']['from'], 6)
        self.assertEqual(rendered['publicationMetadata']['finalVideoFrames'], 156)
        self.assertTrue(media['bodyDecodedFramesAndTimestampsEqual'])
        self.assertTrue(media['audioPacketsAndTimingEqual'])
        for name in ('reference-appendix.json', 'reference-appendix-media-check.json'):
            self.assertEqual((self.directory/name).read_bytes(),
                             (self.directory/'revisions/reference-endcards'/name).read_bytes())
        marker = (self.directory/'body-started').stat().st_mtime_ns
        verified = self.execute('--verify')
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertEqual(marker, (self.directory/'body-started').stat().st_mtime_ns, '--verify must not rerender body')
        # A stale copied publication record must not be silently accepted.
        rendered['publicationMetadata']['finalVideoFrames'] = 155
        write(self.directory/'render-result.json', rendered)
        invalid = self.execute('--verify')
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn('publication metadata differs', invalid.stderr)

    def test_templates_keep_sources_pending_and_render_body_separate(self):
        template = json.loads((ROOT/'episodes-codex/_template/references.example.json').read_text())
        self.assertEqual(template['sources'][0]['verification']['status'], 'pending')
        scripts = json.loads((ROOT/'episodes-codex/_template/reference-scripts.json').read_text())['scripts']
        self.assertIn('render_with_references.py', scripts['render'])
        self.assertEqual(scripts['render:body'], 'npm run render:voice && npm run render:mix')
        self.assertIn('--out out/body.mp4', scripts['render:mix'])
        self.assertNotEqual(scripts['render'], scripts['render:body'])


if __name__ == '__main__':
    unittest.main()
