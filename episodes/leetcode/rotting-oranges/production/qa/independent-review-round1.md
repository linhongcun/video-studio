# Independent Editorial & Logic Review (Round 1) — EP.63 LC.994 `rotting-oranges`

- **Executor**: Independent `research` subagent (`60129680-4f9e-4b7f-9462-aec4a3d2afd3`, read-only)
- **Date**: 2026-11-22
- **Reviewed Input SHAs**:
  - `script.md`: `70352eabe51c8f71cbb57aa7b54c7d7e44ff20fa4ec166055bdf9bc40ba567d0`
  - `article.mdx`: `c5008ebdf5758ee0242f1ee98b87fbe7b0c04172479d5694831a1902f5061d82`
  - `plan.json`: `dceb4effaad75298927bbf2fb0bdd7241e87bc714a27c504fd4f3f872ed75360`
  - `references.json`: `f71c492a2afe9eee65117c5c3d563b75b06cb8eac0c75f710abe3d1cfb350302`
  - `solution.py`: `bc451a8045fcd8e0097f7f6bbda34ff1e886aa8a04f116b93df2b52429395ce1`
  - `trace/main-example.json`: `841971f6b5ce1332051fb4ce2a8857a4332af77e19e1ca961c5e1c54f39b1aae`
- **Verdict**: `REVISE` (blocking issues found in both Review A and Review B; fixed before TTS & re-reviewed in Round 2).

## Summary of Blocking Findings

### Review A (Script, Plan, Trace & Pronunciation)
1. **Shot 07 (`impossible`) factual & trace mismatch**: `plan.json` used `[0,2,5,9,13]` & `[16]` instead of `layer_end` snapshots `[0,3,6,10,13]` & `[15,17]`; narration claimed queue was already empty right after 4 minutes infected the 5 reachable oranges, whereas in `solution.py` `(2,2)` is still in `queue` at the end of minute 4 and pops in the final pass with no fresh neighbors to empty the queue.
2. **Shot 02 geometric misnomer**: Called `(2,2)` on a `3×4` grid `"右下角"`, whereas `(2,3)` is the bottom-right corner.
3. **Over-length sentences (58–86 chars)**: All 18 sentences exceeded comfortable 1–2 line subtitle bounds, creating coarse cue sync and an auditory tongue-twister in Shot 05.
4. **Missing prerequisites in Shots 01 & 03**: Shot 01 omitted spoken 0-based indexing + concrete coordinate mapping, `"同时"` simultaneous spread, and empty `0` blocking; Shot 03 omitted counting initial `fresh = 7`, explicit `"从队头取出"`, and qualifying `"距离"` as distance from the nearest initial rotten orange.
5. **`pronunciation.md` inaccuracies**: Contained phantom phrases (`为负一`, `只能`) and omitted real polyphone risks (`重置`, `处理`, full `háng` coordinate set, `额外空间`, `第一` non-sandhi).

### Review B (Article Structure & Source Evidence)
1. **`article.mdx` Shot 07 / Official Example 2 contradiction**: Claimed queue was already empty after 4 minutes instead of after `(2,2)` pops with no fresh neighbors.
2. **`SourceQuote` `supports` scope overstatement (R2 & R3)**: Narrowed R2 to `O(1)` two-ended operations and aligned R3 quote & `supports` strictly to verbatim content.
3. **Unmarked planned `<Figure>` slots**: Added explicit pending/planned MDX notes pending final aligned audio & post-render screenshot extraction.
4. **Exhaustive test coverage mismatch**: `article.mdx` claimed all shapes `1×1` through `3×2`, while `tests/test_solution.py` omitted `(1,3)` and `(3,1)`.
