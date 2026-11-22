# Independent Editorial & Logic Review (Round 2) — EP.63 LC.994 `rotting-oranges`

- **Executor**: Independent `research` subagent (`60129680-4f9e-4b7f-9462-aec4a3d2afd3`, read-only)
- **Date**: 2026-11-22
- **Reviewed Input SHAs (Round 2 PASS)**:
  - `script.md`: `3d06b83d59dc38869c70ca26829c070c7e3b96422dafb74b3d9776cfe4bd8b49`
  - `article.mdx`: `c15c3e5ac0a2b30087d6ac63cedbddf3978a86ff03565365065f8b28e86622c6`
  - `plan.json`: `015eb6f9e48342a7f27ea4a5f598e24de2548fd590f16eb9130c1fb9b99bfbd6`
  - `references.json`: `a6ed9100e4fbe72924c63ad605121881fa397ed91207b6dd2043074e567af3e8`
  - `pronunciation.md`: `6c7794f024aea324e0ca97a4c55e8c6fc14c2e824b34cc3c7caf5f3547f0f48f`
  - `solution.py`: `bc451a8045fcd8e0097f7f6bbda34ff1e886aa8a04f116b93df2b52429395ce1`
  - `trace/main-example.json`: `5074c76c08d07f88006a0fcccfa231246521b7fd62bbba4203b63aabf5f5994e`
- **Verdict**: `PASS` (all Round 1 blocking findings in Review A & Review B resolved; ready for TTS recording).

## Verification Summary

### Review A (Script, Plan, Storyboard, Pronunciation, Trace)
1. **Shot 10 (`impossible`) trace & narrative alignment**: Resolved. `script.md`, `storyboard-design.md`, and `plan.json` accurately state that 4 minutes infect the 5 reachable oranges, then `(2,2)` pops with no fresh neighbors to empty the queue while `(2,0)` stays isolated (`-1`). Event IDs `[0, 3, 6, 10, 13]` and `[15, 17]` match `trace/main-example.json` `impossible.events` exactly.
2. **Shot 03 `(2,2)` position wording**: Resolved (`"下方的二行二列"`, avoiding bottom-right corner misnomer on `3×4` grid).
3. **Sentence length, subtitle bounds & cue alignment**: Resolved. 12 shots × 2 sentences (24 sentences total, 41–58 chars each); every `plan.json` `cue` / `endCue` matches its sentence prefix in `script.md`, and all `main.events` IDs `[0..15]` match `trace/main-example.json`.
4. **Prerequisites & L058/L039/FIFO clarity**: Resolved. Shots 01–02 establish 0-based row/col indexing, concrete `(0,0)=2` / `(0,1)=1` crate mapping, simultaneous 4-neighbor spread, empty blocking, diagonal restriction, goal, and `-1`. Shots 03–04 motivate multi-source enqueueing, initial `fresh = 7`, FIFO pop-front / push-back, and per-minute layer locking before naming `多源广度优先搜索`.
5. **`pronunciation.md`**: Resolved; phantom entries removed and real polyphone risks documented.

### Review B (Article Structure, Source Evidence & Tests)
1. **Opening vs `## 小结` & standalone readability**: Resolved. Opening core question and `## 小结` align strictly; Official Example 2 minute-4/queue-empty trace matches `solution.py`.
2. **Verbatim `SourceQuote` & `supports` scope**: Resolved. All 3 `references.json` quotations match `research/source-evidence.json` verbatim; R2 (`deque` `O(1)` two-ended ops) and R3 (BFS lead + queue tracking) `supports` claims stay strictly within cited text.
3. **Planned `<Figure>` slots**: Marked explicitly as planned pending final audio alignment and post-render screenshot extraction.
4. **Oracle test coverage & `stopReason`**: Resolved. `(1,3)` and `(3,1)` added to `tests/test_solution.py` (1,614 exhaustive small grids + 3,000 random grids up to `6×6`); `noFresh.stopReason` fixed to `all_rotten_initial`.

## Post-Review Pre-Freeze Non-Blocking Nits Applied (Before TTS & Freeze)
Three minor non-blocking wording nits flagged in Round 2 were fixed immediately prior to `prep.py` and TTS generation (zero changes to spoken narration text in `script.md`):
1. `article.mdx:148` & `tests/test_solution.py:58`: tightened `"全部 8 种不超 6 格形状"` to `"8 种 m, n ≤ 3 且不超 6 格的小网格形状"` (`article.mdx` SHA -> `16e523fc6708724ba5244c9bc7a5f638050f1e9310569cd12b9edac9c2e731aa`, `tests/test_solution.py` SHA -> `e64385362810e749ac8cdeb3fd51be55315a662622b4843de9c636c6e2572245`).
2. `pronunciation.md:10, 15`: removed shot `08` from `还 hái` (`06, 09, 12`) and added `去重` (`12`) to `重 chóng` (`pronunciation.md` SHA -> `e8cc08644b88aeff1422efdf8e347d9039274ecb826e7cfc2ec5d67883f00e7b`).
3. `script.md:2`: updated header comment range `40–54 字/句` -> `41–58 字/句` (no spoken `旁白：` line changed; `script.md` SHA -> `a3ee436008bfda43511b48fc395cb136d673942252f7526082b932bd09218523`).
