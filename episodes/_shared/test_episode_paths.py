"""Check moved episode paths and byte-preserving historical evidence lookup."""
from pathlib import Path
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch

import episode_paths as paths


class EpisodePaths(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / 'AGENTS.md').write_text('fixture')
        (self.root / 'site').mkdir()
        (self.root / 'site/package.json').write_text('{}')
        self.episode = self.root / 'episodes/network/example'
        (self.episode / 'production/research').mkdir(parents=True)
        (self.episode / 'publication').mkdir()
        (self.episode / 'publication/meta.json').write_text('{"slug":"example"}')
        self.evidence = self.episode / 'production/research/evidence.txt'
        self.evidence.write_bytes(b'original evidence\n')
        original = paths.repo_root
        self.root_finder = original
        self.mock = patch.object(paths, 'repo_root', side_effect=lambda start=None: self.root if start is None else original(start))
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def test_root_and_unique_series_episode(self):
        self.assertEqual(self.root_finder(self.evidence), self.root)
        self.assertEqual(paths.production_directory('example'), self.episode / 'production')
        self.assertEqual(paths.publication_directory('example'), self.episode / 'publication')
        self.assertEqual(paths.episode_slug(self.evidence), 'example')
        duplicate = self.root / 'episodes/other/example/publication'
        duplicate.mkdir(parents=True)
        (duplicate / 'meta.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Expected one publication record'):
            paths.production_directory('example')

    def test_original_and_current_references_resolve_to_same_bytes(self):
        for name in ('episodes-codex/example/research/evidence.txt',
                     '/workspace/video-studio/episodes-codex/example/research/evidence.txt',
                     'episodes/network/example/production/research/evidence.txt'):
            with self.subTest(name=name):
                self.assertEqual(paths.resolve_repo_path(name), self.evidence)
                self.assertEqual(paths.resolve_repo_path(name).read_bytes(), b'original evidence\n')
        self.assertEqual(paths.resolve_repo_path('episodes/example/meta.json'), self.episode / 'publication/meta.json')
        self.assertEqual(paths.resolve_repo_path('episodes-codex/_shared/tool.py'), self.root / 'episodes/_shared/tool.py')

    def test_escape_and_unknown_slug_are_rejected(self):
        for name in ('../outside', '/tmp/outside', 'episodes-codex/../outside',
                     'episodes-codex/example/../../../../../../outside'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                paths.resolve_repo_path(name)
        for slug in ('../example', 'unknown', '*'):
            with self.subTest(slug=slug), self.assertRaises(ValueError):
                paths.production_directory(slug)
        (self.episode / 'production/research/escape').symlink_to('/tmp', target_is_directory=True)
        with self.assertRaises(ValueError):
            paths.resolve_repo_path('episodes-codex/example/research/escape/outside')

    def test_historical_manifest_maps_locations_without_accepting_new_bytes(self):
        manifest = self.episode / 'production/source-sha256.json'
        original = b'{"research/evidence.txt": "original expected hash"}\n'
        manifest.write_bytes(original)
        archive = self.root / 'docs/archive/2026-11/episode-layout'
        archive.mkdir(parents=True)
        ledger = {'pathPrefixes': {'episodes-codex/example': 'episodes/network/example/production'},
                  'legacyManifests': {manifest.relative_to(self.root).as_posix(): {
                      'oldPath': 'episodes-codex/example/source-sha256.json',
                      'sha256': hashlib.sha256(original).hexdigest()}}}
        (archive / 'migration.json').write_text(json.dumps(ledger))
        self.assertEqual(paths.resolve_frozen_path(manifest, 'research/evidence.txt'), self.evidence)
        with self.assertRaises(ValueError):
            paths.resolve_frozen_path(manifest, '../../../../outside')
        # Edited/new freezes use their actual directory, without treating their
        # new bytes as the historical record registered by the migration.
        manifest.write_bytes(b'{"new": "freeze"}\n')
        self.assertEqual(paths.resolve_frozen_path(manifest, 'research/evidence.txt'), self.evidence)
        self.assertEqual(paths.resolve_frozen_path(manifest, '../../../_shared/tool.py'),
                         self.root / 'episodes/_shared/tool.py')


if __name__ == '__main__':
    unittest.main()
