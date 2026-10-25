#!/usr/bin/env python3
"""Check claim-input rejection, copyfit, media preservation and repeat safety."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('append_references', DIRECTORY/'append_references.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture(count=3):
    return {'schemaVersion': 1, 'episode': 'test-fixture', 'checkedAt': '2026-10-25',
            'sources': [{'id': f'R{i+1}', 'organization': 'Test fixture',
                         'title': f'测试资料 {i+1}', 'version': '2026',
                         'url': 'https://example.com/test-fixture', 'sections': '§1',
                         'supports': ['测试论点，非实际发布引用'],
                         'verification': {'status': 'verified', 'checkedAt': '2026-10-25',
                                          'evidence': 'synthetic test fixture'}}
                        for i in range(count)]}


class ReferenceInputs(unittest.TestCase):
    def test_rejects_missing_evidence_and_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'references.json'
            for mutation in ('unverified', 'duplicate', 'no-claim', 'bad-date', 'bad-url'):
                doc = fixture()
                if mutation == 'unverified':
                    doc['sources'][0]['verification']['status'] = 'pending'
                elif mutation == 'duplicate':
                    doc['sources'][1]['id'] = 'R1'
                elif mutation == 'no-claim':
                    doc['sources'][0]['supports'] = []
                elif mutation == 'bad-date':
                    doc['sources'][0]['verification']['checkedAt'] = '2026-02-31'
                elif mutation == 'bad-url':
                    doc['sources'][0]['url'] = 'javascript:alert(1)'
                path.write_text(json.dumps(doc))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    MODULE.load_references(path)

    def test_multi_page_and_overflow_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            cards = MODULE.render_cards(fixture(4), Path(tmp), 1280, 720,
                                        MODULE.DEFAULT_FONT, MODULE.DEFAULT_BOLD)
            self.assertEqual(len(cards), 2)
            doc = fixture()
            doc['sources'][0]['displaySupport'] = '超长支撑说明' * 100
            with self.assertRaisesRegex(ValueError, 'COPYFIT'):
                MODULE.render_cards(doc, Path(tmp), 1280, 720,
                                    MODULE.DEFAULT_FONT, MODULE.DEFAULT_BOLD)

    def test_full_media_preservation_and_repeat_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            body, final, refs = temp/'body.mp4', temp/'final.mp4', temp/'references.json'
            refs.write_text(json.dumps(fixture(4), ensure_ascii=False))
            subprocess.run([
                'ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                'testsrc2=size=1280x720:rate=30:duration=1', '-f', 'lavfi', '-i',
                'sine=frequency=440:sample_rate=48000:duration=1',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
                '-profile:v', 'main', '-level', '4.0', '-video_track_timescale', '90000',
                '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(body),
            ], check=True)
            command = [
                'python3', str(DIRECTORY/'append_references.py'), 'append',
                '--body', str(body), '--references', str(refs), '--output', str(final),
                '--artifacts', str(temp/'artifacts'), '--seconds', '0.2',
            ]
            result = json.loads(subprocess.check_output(command))
            self.assertEqual(result['bodyFrames'], 30)
            self.assertEqual(result['finalVideoFrames'], 42)
            report = json.loads((temp/'artifacts/reference-appendix-media-check.json').read_text())
            self.assertTrue(report['bodyDecodedFramesAndTimestampsEqual'])
            self.assertTrue(report['audioPacketsAndTimingEqual'])
            before = MODULE.sha(final)
            self.assertEqual(json.loads(subprocess.check_output(command))['status'], 'already-current')
            self.assertEqual(before, MODULE.sha(final))
            # A final output used as a new body must be rejected, even with a new output path.
            bad = copy.copy(command)
            bad[bad.index('--body') + 1] = str(final)
            bad[bad.index('--output') + 1] = str(temp/'doubled.mp4')
            failure = subprocess.run(bad, capture_output=True, text=True)
            self.assertNotEqual(failure.returncode, 0)
            self.assertIn('already has a reference appendix', failure.stderr)
            final.write_bytes(b'external change')
            failure = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(failure.returncode, 0)
            self.assertIn('changed outside this tool', failure.stderr)


if __name__ == '__main__':
    unittest.main()
