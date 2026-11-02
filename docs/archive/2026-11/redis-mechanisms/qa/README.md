# Independent Redis batch review tools

These tools write only to a fresh child directory of this QA archive. Production inputs, selected takes and previous failures remain untouched. Run them only after the owner reports the corresponding production stage ready. Reports retain actual input hashes; no previous episode result or image is used as a golden.

`voice-independent.py` checks current approved narration, exact selected TTS request records, actual selected-cut sample lengths and signal correspondence, sentence PCM within the real track, zero-valued gaps, body timing identity, loudness and truncation signals. Editorial and optional production receipt paths are supplied explicitly; receipt filenames/status vocabulary are not inherited from another batch. Signal flags require a bounded review decision; they do not diagnose missing words. No ASR, phoneme recognition or full semantic listening is performed.

The default editorial narration hash concatenates exact narration lines without separators. If an actual approval explicitly used newline-joined lines, pass `--approval-narration-format newline-lines`; the raw approved hash is checked against that declared definition and a separate canonical content hash is recorded. Retained and discarded parts of raw takes are measured separately so an amplitude peak in a discarded tail is not treated as part of the delivered sentence. Earlier attempts and reviewer-source snapshots remain intact when this distinction requires follow-up.

```bash
/workspace/.venvs/video-studio/bin/python docs/archive/2026-11/redis-mechanisms/qa/voice-independent.py EP_PRODUCTION --approval EP_PRODUCTION/qa-editorial.json --out-dir docs/archive/2026-11/redis-mechanisms/qa/SLUG-voice-attempt1
```

`render-preview.mjs` creates a fresh source bundle and actual integer-frame PNG/DOM evidence. Both preview and clip tools acquire `/tmp/video-studio-render.lock` themselves. A spec contains unique `samples` with integer `frame`, optional `label`, `expectedState` and `expectedText` arrays. `extraInputs` lists additional repository-relative dependencies. Samples should cover object movement, meaningful intermediate states, resets and adjacent shot boundaries. Collision candidates are retained for actual image review; automatic geometry checks cannot determine whether an overlap is meaningful. Add a separate subtitle-on attempt where needed.

```bash
node docs/archive/2026-11/redis-mechanisms/qa/render-preview.mjs --dir=EP_PRODUCTION --spec=SPEC_JSON --out-dir=NEW_QA_ATTEMPT
node docs/archive/2026-11/redis-mechanisms/qa/render-short-clip.mjs --preview-report=NEW_QA_ATTEMPT/source-preview-review.json --first=FIRST_FRAME --last=LAST_FRAME --out-dir=NEW_CLIP_ATTEMPT
```

Clips are bounded to 450 frames, use the audited bundle, retain the exact original voice sample interval, and fully decode the produced short MP4. They are source previews; formal color-converted output is reviewed separately. The tool rejects changed production inputs or bundle files.

`encoded-independent.py` verifies final video/receipt identity, actual format and color metadata, bibliography mapping and body/reference frame ranges. It decodes complete video and AAC while retaining selected exact decoder-frame PNGs, including each shot, article figures and every reference page boundary. It does not render a new full video.

```bash
/workspace/.venvs/video-studio/bin/python docs/archive/2026-11/redis-mechanisms/qa/encoded-independent.py EP_PRODUCTION --out-dir NEW_ENCODED_ATTEMPT
/workspace/.venvs/video-studio/bin/python docs/archive/2026-11/redis-mechanisms/qa/contact-sheets.py --report REVIEW_JSON --out-dir NEW_CONTACT_ATTEMPT
```

Machine screening, actual image/continuous-motion review, sound semantics and user feedback remain separate records. `visualReviewed` stays false until a reviewer actually examines the retained evidence and writes a separate review decision. A failed attempt never overwrites inputs or earlier reports.
