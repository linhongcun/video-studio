# 08/09 semantic cue alignment

The first section below preserves the targeted scratch run made before the 04/07 rebuild. Its absolute frames belong only to the old timeline. The final-build section records the replacement cues after the shared build; do not reuse scratch absolute frames.

## Method and quality

- Input: only `08-gap-2.wav` and `09-gap-1.wav`, copied with their build rows to `/home/ubuntu/.cache/lc56-targeted-asr`.
- Source assembled voice: 14,041,644 bytes, SHA-256 `9afcc7a5ece7d3f4ae9d36b97a1e7a12679da8413ec7d9a66cffa14af099681f`.
- Shared entrypoints: `episodes/_shared/voice/asr.py`, `onsets.py`, `lastword_fix.py`, and `cues_rule.py`. No local onset or character-alignment algorithm was added.
- Environment: `faster-whisper==1.2.1`, `ctranslate2==4.8.3`, `Systran/faster-whisper-medium`, CPU/float32, 8 threads, beam size 5, `zh`, prompt `以下是普通话的句子。`.
- ASR coverage: 08 `0.84`; 09 `0.71875`. Both transcripts normalize spoken Chinese numerals to Arabic numerals. The shared character aligner interpolated the 09 `八` from the normalized `8`; this makes that cue less certain than 08 and is retained as a quality limitation.

## Shared outputs

| Cue | ASR transcript excerpt | ASR onset | `cues_rule.py` onset | Sentence-relative offset | Source / note |
|---|---|---:|---:|---:|---|
| 08 `把一到六写入结果` | `…更后面的段也接不回来；把1到6写入结果…` | 2975.5 | 2974.5 | 206.59 frames (6.886 s) | `onset_rule:pause`, −1 frame from ASR; cue character `把` is aligned at 2975.5 |
| 09 `八到十因此独立成段` | `…两段隔着空隙，8到10因此独立成段。好。` | 3251.9 | 3256.9 | 168.78 frames (5.626 s) | `onset_rule:pause`, +5 frames; normalized `8` maps to interpolated `八`; cue ends the sentence |


## Final voice build

- Assembled voice: 14,035,244 bytes, SHA-256 `d79b00ac4dffac3c2ce8bade78c0409756fa1f8940b1b0b548f896adb09373b4`, 48 kHz mono, 7,017,600 samples, 4,386 frames at 30 fps.
- Current shared ASR: `faster-whisper==1.2.1`, `ctranslate2==4.8.3`, `Systran/faster-whisper-medium`, CPU/float32, 8 threads, beam 5, `zh`, prompt `以下是普通话的句子。`. Full-track transcript ratio was 0.8330; cue-line coverage was 08 sentence 2 `0.84`, 09 sentence 1 `0.72`, and 09 sentence 2 `0.81`.
- Cues use shared `onsets.py`, `lastword_fix.py`, and `cues_rule.py`; no local onset or alignment algorithm was added. `cues_rule.py` reports 9 cues, maximum rule/ASR difference 5.75 frames; selfcheck reports no cue outside −6..+2 and no short-shot failure. `words.json` remains sentence-envelope timing (`wordAlignment: false`); ASR word spans are estimates, not forced alignment.

| Cue | ASR position | Shared cue onset | Sentence-relative offset | Notes |
|---|---:|---:|---:|---|
| 08 `把一到六写入结果` | 2996.9 | 2995.9 | 206.6 frames from sentence start 2789.3 | Rule onset is 1 frame before ASR. |
| 08 end bound `从八到十开始新段` | 3041.3 | 3039.3 | 250.0 frames from sentence start 2789.3 | Rule onset is 2 frames before ASR; retained sentence-end cue flag. |
| 09 `八到十因此独立成段` | ASR phrase onset 3273.3; ASR `8` token 3279.3 | 3278.3 | 168.8 frames from sentence start 3109.5 | Shared pause onset is 1 frame before the ASR `8` token. The cue ends sentence 1 and retains `CHECK: cue is last word of sentence`; spoken `八` is normalized as `8`. |
| 09 `把当前的十二到十四写入结果` | 3432.2 | 3432.2 | 84.6 frames from sentence start 3347.6 | ASR `把` onset matches the shared cue; retains the sentence-end cue flag. |

The rebuilt storyboard places 08 at global frame 2995.9. Its end bound is the 3039.3 onset minus six frames; the state transition completes by integer frame 3028, before the next phrase starts at ASR frame 3041.3. For 09, the separate action starts at global frame 3278.3 and is bounded by second-sentence frame 3347 minus six, so the `[8,10]` result and current `[12,14]` state are complete before frame 3341. The finish action begins at frame 3432.2 and reaches the completed state at frame 3503, just after the ASR final-word boundary at 3501.2. Separate is complete well before finish begins; the actions do not overlap.

Actual Remotion stills with `hideSubtitles: true` were rendered and inspected:

- 08 cue/transition/result: `remotion/out/lc56-08-before.png`, `lc56-08-cue.png`, `lc56-08-mid.png`, `lc56-08-pre-complete.png` (frame 3027), `lc56-08-complete.png` (frame 3028), `lc56-08-before-next-phrase.png`.
- 09 separate and finish: `remotion/out/lc56-09-before-separate.png`, `lc56-09-cue.png`, `lc56-09-mid-separate.png`, `lc56-09-after-separate.png`, `lc56-09-second-minus1.png`, `lc56-09-second-cue.png`, `lc56-09-second-plus1.png`, `lc56-09-before-finish.png`, `lc56-09-finish-cue.png`, `lc56-09-finish-mid.png`, `lc56-09-finish-complete.png`, `lc56-09-finish-after.png`.

At second-sentence frames 3346/3347/3348, all three inspected stills show `[1,6]` and `[8,10]` completed and `[12,14]` current. The finish cue begins later at frame 3432; its transition is separate from the earlier `[8,10]` output.
