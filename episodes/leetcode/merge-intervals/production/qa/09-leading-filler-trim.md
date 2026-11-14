# 09 trailing filler handling

The shared `prep.py` adds a trailing `好。` to each TTS submission. The existing `09-gap-1-a.wav` (815,786 bytes, 48 kHz mono, SHA-256 `b53f6a1022537afe6a488c9a9c7c3c7f7623cf3ed1683ac5797625c1a1e3b952`) contains a trailing `好` after `八到十因此独立成段`; `describe_audio` reported a short pause before it.

A trim-only sample was made from the original with FFmpeg, ending at sample 374,400 (7.800 s). The original is preserved. The sample is `voice/takes/09-gap-1-a-trim.wav` (748,878 bytes, SHA-256 `09d84038b4a3a3ca1a54ceb1d001af8bc8ed751bfbf1941d01fccc990836daa0`). It is rejected: `describe_audio` still reported a trailing `好`, while the shared `take_asr.py` + `common.cut` path omitted `八到十因此独立成段` from its transcript.

## Separator-based derivative

Shared sentence ASR on the raw `09-gap-1-a.wav` returned `段。` at 222.6–228.6 frames and trailing `好。` at 240.6–247.8 frames (30 fps, sentence-relative). The final script character ends at sample 365,760 (7.620 s at 48 kHz). A 0.4 s silence (19,200 samples) was inserted there. To ensure the new body-to-tail gap is the last internal gap seen by the unchanged shared `common.cut`, the derivative ends 30 ms after the ASR tail-word end (sample 397,920); this removes only post-word tail, not scripted speech. The original raw take remains untouched.

The derivative `voice/takes/09-gap-1-a-separated-v2.wav` is 834,284 bytes, SHA-256 `8bdf2c83ec84a211e2d1b261df27aa099b606f21d0d341fd71a2d7695e91ab9a`. Shared `take_asr.py` + `common.cut` returned the complete body ending `八到十因此独立成段。` with no trailing `好`. It is selected as `09-gap-1` in `voice/picks.json`.

No new 09 TTS was sent. The 04/07 revised-text candidates are generated separately; all other 17 picks remain `a`.

## Final assembled sentence

The selected output `voice/sentences/09-gap-1.wav` is 728,592 bytes, SHA-256 `7aeac02bf71d899d375987821825a168819c27f5097443155057e3532d889c7c`. `describe_audio` on the final built sentence returned `12到14的起点，12大于当前终点时，两段隔着空隙，8到10因此独立成段。` and did not report a trailing `好`. The raw take remains unchanged; no new 09 TTS was sent.
