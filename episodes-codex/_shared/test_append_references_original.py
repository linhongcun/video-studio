"""Exercise original titles, verbatim-only cards and reuse of the frozen engine."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest


SHARED = Path(__file__).resolve().parent
ROOT = SHARED.parents[1]
SPEC = importlib.util.spec_from_file_location('original_refs', SHARED/'append_references_original.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class OriginalTitles(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='.original-reference-test-', dir=ROOT/'episodes-codex')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.evidence = self.directory/'evidence.md'
        self.evidence.write_text('Original Source Title\nAn exact short passage from the test source.\n')
        proof = str(self.evidence.relative_to(ROOT))
        self.doc = {'schemaVersion': 1, 'presentation': M.PRESENTATION,
                    'episode': 'synthetic-original-title', 'checkedAt': '2026-10-25',
                    'sources': [{'id': 'R1', 'organization': 'Synthetic fixture',
                                 'title': 'Original Source Title', 'version': '2026',
                                 'url': 'https://example.com/original-title-test', 'sections': '§1',
                                 'supports': ['Internal summary must never appear on a source card'],
                                 'titleEvidence': {'locator': 'Title, line 1', 'evidence': proof},
                                 'quotation': {'text': 'An exact short passage from the test source.',
                                               'locator': '§1, line 2', 'evidence': proof},
                                 'verification': {'status': 'verified', 'checkedAt': '2026-10-25',
                                                  'evidence': proof}}]}

    def save(self, doc):
        path = self.directory/'references.json'
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2)+'\n')
        return path

    def test_old_display_fields_and_unlocated_quotes_are_rejected(self):
        for mutation in ('old-presentation', 'displayTitle', 'displaySupport', 'no-title-evidence',
                         'no-quote-locator', 'missing-quote-evidence'):
            doc = copy.deepcopy(self.doc)
            if mutation == 'old-presentation':
                doc.pop('presentation')
            elif mutation in ('displayTitle', 'displaySupport'):
                doc['sources'][0][mutation] = ''
            elif mutation == 'no-title-evidence':
                doc['sources'][0].pop('titleEvidence')
            elif mutation == 'no-quote-locator':
                doc['sources'][0]['quotation'].pop('locator')
            else:
                doc['sources'][0]['quotation']['evidence'] = 'nonexistent-evidence-file.md'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                M.load_references(self.save(doc))

    def test_full_title_is_never_replaced_by_internal_summary(self):
        first = self.directory/'first'; second = self.directory/'second'
        first.mkdir(); second.mkdir()
        doc = copy.deepcopy(self.doc)
        doc['sources'] = [dict(copy.deepcopy(doc['sources'][0]), id=f'R{i+1}') for i in range(3)]
        a = M.render_cards(doc, first, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)
        doc['sources'][0]['supports'] = ['A completely different internal summary']
        b = M.render_cards(doc, second, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)
        self.assertEqual(len(a), 2, 'At most two original sources belong on each page')
        self.assertEqual(a[0].read_bytes(), b[0].read_bytes(), 'Research summaries must not alter source cards')
        doc['sources'][0]['title'] = 'The Original Source Title Must Never Be Truncated ' * 80
        with self.assertRaisesRegex(ValueError, 'COPYFIT complete original title'):
            M.render_cards(doc, second, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)
        doc = copy.deepcopy(self.doc)
        doc['sources'][0]['quotation']['text'] *= 100
        with self.assertRaisesRegex(ValueError, 'COPYFIT verbatim quotation'):
            M.render_cards(doc, second, 1280, 720, M.DEFAULT_FONT, M.DEFAULT_BOLD)

    def test_real_short_body_engine_reuse_receipt_and_repeat_safety(self):
        engine_sha = M.engine.sha(M.OLD_ENGINE)
        engine_file = M.engine.__file__
        body, output = self.directory/'body.mp4', self.directory/'final.mp4'
        subprocess.run([
            'ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
            'testsrc2=size=1280x720:rate=30:duration=0.2', '-f', 'lavfi', '-i',
            'sine=frequency=440:sample_rate=48000:duration=0.2',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
            '-profile:v', 'main', '-level:v', '4.0', '-video_track_timescale', '90000',
            '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(body),
        ], check=True)
        doc = copy.deepcopy(self.doc)
        doc['sources'] = [dict(copy.deepcopy(doc['sources'][0]), id=f'R{i+1}') for i in range(3)]
        args = SimpleNamespace(body=body, output=output, references=self.save(doc),
                               artifacts=self.directory/'artifacts', seconds=0.2,
                               font=M.DEFAULT_FONT, bold_font=M.DEFAULT_BOLD)
        receipt = M.append(args)
        self.assertEqual(receipt['bodyFrames'], 6)
        self.assertEqual(receipt['finalVideoFrames'], 18)
        self.assertEqual(receipt['presentation'], M.PRESENTATION)
        self.assertEqual(receipt['sourceTitles'], M.source_titles(doc))
        self.assertEqual(receipt['quotations'], M.quotations(doc))
        self.assertEqual(receipt['inputs']['generatorSHA256'], M.engine.sha(M.GENERATOR))
        self.assertNotEqual(receipt['inputs']['generatorSHA256'], engine_sha)
        self.assertEqual(receipt['dependencies']['oldEngineSHA256'], engine_sha)
        self.assertEqual(M.engine.sha(M.OLD_ENGINE), engine_sha)
        self.assertEqual(M.engine.__file__, engine_file, 'Adapter must not mutate the imported frozen engine namespace')
        self.assertEqual(M.append(args)['status'], 'already-current')
        # Recover a process interruption between the frozen engine's receipt
        # write and the adapter's identity write, without touching media bytes.
        path = args.artifacts/'reference-appendix.json'
        interrupted = json.loads(path.read_text())
        for key in ('presentation', 'sourceTitles', 'quotations', 'dependencies'):
            interrupted.pop(key)
        path.write_text(json.dumps(interrupted))
        media_sha = M.engine.sha(output)
        recovered = M.append(args)
        self.assertEqual(recovered['status'], 'already-current')
        self.assertEqual(recovered['presentation'], M.PRESENTATION)
        self.assertEqual(M.engine.sha(output), media_sha)
        verified = M.verify(args)
        self.assertTrue(verified['bodyDecodedFramesAndTimestampsEqual'])
        self.assertTrue(verified['audioPacketsAndTimingEqual'])
        self.assertTrue(verified['outputVideoTimelineContinuous'])
        # A stale engine dependency must fail before any new media operation.
        saved = json.loads(path.read_text())
        saved['dependencies']['oldEngineSHA256'] = '0' * 64
        path.write_text(json.dumps(saved))
        with self.assertRaisesRegex(ValueError, 'engine dependency changed'):
            M.verify(args)

    def test_migrates_known_v1_output_from_original_body_without_double_append(self):
        body, output = self.directory/'body.mp4', self.directory/'final.mp4'
        subprocess.run([
            'ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
            'color=c=0x0f172a:size=1280x720:rate=30:duration=0.2', '-f', 'lavfi', '-i',
            'sine=frequency=440:sample_rate=48000:duration=0.2',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
            '-profile:v', 'main', '-level:v', '4.0', '-video_track_timescale', '90000',
            '-c:a', 'aac', '-ar', '48000', '-ac', '2', str(body),
        ], check=True)
        doc = copy.deepcopy(self.doc)
        doc['sources'] = [dict(copy.deepcopy(doc['sources'][0]), id=f'R{i+1}') for i in range(3)]
        legacy = copy.deepcopy(doc)
        legacy.pop('presentation')
        for source in legacy['sources']:
            source['displayTitle'] = 'Synthetic legacy summary title'
        args = SimpleNamespace(body=body, output=output, references=self.save(legacy),
                               artifacts=self.directory/'artifacts', seconds=0.2,
                               font=M.DEFAULT_FONT, bold_font=M.DEFAULT_BOLD)
        before = M.engine.append(args)
        self.assertEqual(before['finalVideoFrames'], 12, 'Legacy three-source card is one page')
        self.assertEqual(before['outputSHA256'], M.engine.sha(output))
        self.save(doc)
        after = M.append(args)
        self.assertEqual(after['status'], 'appended')
        self.assertEqual(after['bodyFrames'], 6, 'Migration must preserve the pre-appendix body identity')
        self.assertEqual(after['finalVideoFrames'], 18, 'Two v2 pages replace the v1 page rather than stacking')
        self.assertEqual(after['inputs']['bodySHA256'], before['inputs']['bodySHA256'])
        self.assertNotEqual(after['outputSHA256'], before['outputSHA256'])
        self.assertEqual(after['sourceTitles'], M.source_titles(doc))
        self.assertTrue(M.verify(args)['bodyDecodedFramesAndTimestampsEqual'])


if __name__ == '__main__':
    unittest.main()
