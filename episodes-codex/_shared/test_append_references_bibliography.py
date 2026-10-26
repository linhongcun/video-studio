"""Check title/credit-only rendering and actual CLI migration of a short body."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SHARED = Path(__file__).resolve().parent
ROOT = SHARED.parents[1]
SPEC = importlib.util.spec_from_file_location('bibliography', SHARED/'append_references_bibliography.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class Bibliography(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='.bibliography-test-', dir=ROOT/'episodes-codex')
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        proof = self.directory/'evidence.md'
        proof.write_text('Original Source Title\nAn intact research quotation.\nActual Author\n')
        evidence = str(proof.relative_to(ROOT))
        source = {'id': 'R1', 'organization': 'Test Institution', 'title': 'Original Source Title',
                  'version': '2026', 'sections': 'Section 1',
                  'url': 'https://example.com/original-test-source', 'supports': ['Internal claim mapping'],
                  'titleEvidence': {'locator': 'Title, line 1', 'evidence': evidence},
                  'quotation': {'text': 'An intact research quotation.', 'locator': 'Line 2', 'evidence': evidence},
                  'verification': {'status': 'verified', 'checkedAt': '2026-10-26', 'evidence': evidence}}
        self.doc = {'schemaVersion': 1, 'presentation': 'title-author', 'episode': 'bibliography-fixture',
                    'checkedAt': '2026-10-26', 'sources': [source]}

    def write_doc(self, doc):
        path = self.directory/'references.json'
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2)+'\n')
        return path

    def test_only_explicit_nonempty_author_overrides_organization(self):
        self.assertEqual(M.bibliography(self.doc)[0]['credit'], 'Test Institution')
        doc = copy.deepcopy(self.doc)
        doc['sources'][0]['author'] = 'Actual Author'
        self.assertEqual(M.load_references(self.write_doc(doc))['sources'][0]['author'], 'Actual Author')
        self.assertEqual(M.bibliography(doc)[0]['credit'], 'Actual Author')
        for value in ['', '  ', None, [], 42]:
            doc['sources'][0]['author'] = value
            with self.subTest(author=value), self.assertRaisesRegex(ValueError, 'explicit author'):
                M.load_references(self.write_doc(doc))

    def test_research_fields_never_change_visible_bibliography(self):
        a, b = self.directory/'a', self.directory/'b'
        a.mkdir(); b.mkdir()
        before = M.render_cards(self.doc, a, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)[0]
        doc = copy.deepcopy(self.doc)
        doc['checkedAt'] = '2030-01-01'; doc['heading'] = 'Ignored custom heading'
        source = doc['sources'][0]
        source.update(version='Other version', sections='Other locator', note='Invisible note', supports=['Another claim'])
        source['quotation'].update(text='Other research-only quote', locator='Other quote locator')
        after = M.render_cards(doc, b, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)[0]
        self.assertEqual(before.read_bytes(), after.read_bytes(), 'Only original title and credit may affect entry text')
        doc['sources'][0]['title'] = 'Changed Actual Title'
        changed = M.render_cards(doc, b, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)[0]
        self.assertNotEqual(before.read_bytes(), changed.read_bytes())

    def test_four_entries_per_page_and_copyfit_never_truncates(self):
        doc = copy.deepcopy(self.doc)
        doc['sources'] = [dict(copy.deepcopy(doc['sources'][0]), id=f'R{i+1}') for i in range(5)]
        paths = M.render_cards(doc, self.directory, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)
        self.assertEqual(len(paths), 2)
        doc['sources'][0]['title'] = 'Original Title Without Any Truncation ' * 100
        with self.assertRaisesRegex(ValueError, 'COPYFIT complete original title'):
            M.render_cards(doc, self.directory, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)
        doc = copy.deepcopy(self.doc)
        doc['sources'][0]['author'] = 'A complete author credit ' * 100
        with self.assertRaisesRegex(ValueError, 'COPYFIT complete author'):
            M.render_cards(doc, self.directory, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)

    def test_actual_cli_old_quote_receipt_migration_preservation_and_idempotency(self):
        frozen = {path: path.read_bytes() for path in (M.OLD_ENGINE, M.ORIGINAL_RENDERER)}
        body, output = self.directory/'body.mp4', self.directory/'final.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                        'testsrc2=size=1280x720:rate=30:duration=0.2', '-f', 'lavfi', '-i',
                        'sine=frequency=440:sample_rate=48000:duration=0.2',
                        '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
                        '-profile:v', 'main', '-level:v', '4.0', '-video_track_timescale', '90000',
                        '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(body)], check=True)
        doc = copy.deepcopy(self.doc)
        doc['sources'] = [dict(copy.deepcopy(doc['sources'][0]), id=f'R{i+1}') for i in range(4)]
        legacy = copy.deepcopy(doc); legacy['presentation'] = 'original-title-quote'
        refs = self.write_doc(legacy)
        flags = ['--body', str(body), '--references', str(refs), '--output', str(output),
                 '--artifacts', str(self.directory/'artifacts'), '--seconds', '0.2']
        old = json.loads(subprocess.check_output([sys.executable, str(M.ORIGINAL_RENDERER), 'append', *flags]))
        self.assertEqual(old['finalVideoFrames'], 18, 'Four quote entries occupy two legacy pages')
        self.write_doc(doc)
        command = [sys.executable, str(M.GENERATOR)]
        receipt = json.loads(subprocess.check_output([*command, 'append', *flags]))
        self.assertEqual(receipt['bodyFrames'], 6)
        self.assertEqual(receipt['finalVideoFrames'], 12, 'Four bibliographic entries replace the old two-page appendix')
        self.assertEqual(receipt['inputs']['bodySHA256'], old['inputs']['bodySHA256'])
        self.assertEqual(receipt['bibliography'], M.bibliography(doc))
        self.assertEqual(receipt['layout'], M.LAYOUT)
        self.assertEqual(receipt['sourceTitles'], M.original.source_titles(doc))
        self.assertEqual(receipt['quotations'], M.original.quotations(doc))
        self.assertEqual(receipt['inputs']['generatorSHA256'], M.engine.sha(M.GENERATOR))
        self.assertEqual(receipt['dependencies'], M.dependencies())
        before = M.engine.sha(output)
        again = json.loads(subprocess.check_output([*command, 'append', *flags]))
        self.assertEqual(again['status'], 'already-current')
        self.assertEqual(M.engine.sha(output), before)
        verified = json.loads(subprocess.check_output([*command, 'verify', *flags]))
        self.assertTrue(verified['bodyDecodedFramesAndTimestampsEqual'])
        self.assertTrue(verified['audioPacketsAndTimingEqual'])
        self.assertTrue(verified['outputVideoTimelineContinuous'])
        receipt_path = self.directory/'artifacts/reference-appendix.json'
        altered = json.loads(receipt_path.read_text()); altered['bibliography'][0]['credit'] = 'Invented credit'
        receipt_path.write_text(json.dumps(altered))
        bad = subprocess.run([*command, 'verify', *flags], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('titles/credits differ', bad.stderr)
        for path, content in frozen.items():
            self.assertEqual(path.read_bytes(), content, 'Old renderers must remain byte-for-byte unchanged')


if __name__ == '__main__':
    unittest.main()
