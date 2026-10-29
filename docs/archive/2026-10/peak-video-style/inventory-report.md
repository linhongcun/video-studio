# Peak video style inventory

Baseline `eea5d8fab1037cb9630a14647cbada564082a74b`; read-only audit. No tracked files changed.

| EP / slug | body frames | appendix | final frames | AAC ends (historical check) | Figure seek |
|---|---:|---:|---:|---:|---:|
| EP.11 / rate-limit | 3271 | 150 / 5s | 3421 | 109.034s | 68s |
| EP.12 / idempotency | 2998 | 150 / 5s | 3148 | 99.946s | 62s |
| EP.13 / circuit-breaker | 2926 | 150 / 5s | 3076 | 97.536s | 50s |
| EP.14 / degradation | 3134 | 150 / 5s | 3284 | 104.469s | 68s |

All sourcePath values remain `episodes-codex/<slug>/remotion`. Existing body voices, captions, shot durations, numbers, mechanisms, and all current covers should remain. Use independent peak-style source and revision media/freeze; reuse the published full AAC. Keep the article text and existing Figure paths/seek times; replace Figure bytes with the corresponding new encoded frame.

Shared cover style: Noto Sans CJK SC; background #0C2B34, surface #123F48, text #ECFCFA, muted #B3D1D1, edge #35606A, cyan #64E1E2, yellow #F5D66F, coral #EF8B7D. The top three-line mark is abstract identity, not product branding or topology. Use static sparse identity in body rather than adding unrelated motion.

Circuit-breaker alone uses the shared branch navigator and an explicit per-episode branch-map/motion model. Preserve its exact transitions and camera state; recolor a private renderer/map and move only HUD styling so the current long series label does not collide. Keep three states distinct (cyan/coral/yellow) and baseline comparison muted. Other bodies share direct color aliases; blue/cyan role contrast needs actual frame review.

Each existing appendix has 2 original titles/author-or-organization lines, title-author presentation and exactly 150 frames. Generate same-color list in the default new workflow; do not edit source references/old manifests or invent a new source visit. Encoding should use actual full601→limited709 conversion and matching appendix encoding, with full audio packets/PCM and frame PTS comparison.

Preservation snapshot: 871 production files, 102 published files, 60 current cover files; all 266 repository source-sha256 manifests have exact raw snapshots (3937810 bytes) and SHA256. Git blobs bind absent sparse binaries. `preservation-baseline.json` includes original metadata for identity comparison and all individual file identities. New paths are outside the fixed baseline.

Reports distinguish existing historical media check values from fresh probing. Root is independently hydrating the four published baseline MP4s and required rendering assets; no binary assets were hydrated by this audit.
