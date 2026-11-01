P05 binary-opening local site QA passed for v0.68.3; first release remains v0.67.0.

Actual build: 114 HTML, 41 Pagefind indexed courses, 41 published courses. Footer/package/lock are v0.68.3. The three extra HTML routes are tags/TCP/, tags/TLS/, and tags/分布式ID/. The old 全局唯一ID tag URL remains an intentional compatibility redirect in astro.config.mjs:76. No course was added by this patch.

Both actual Chromium viewports (1440×1000 and 390×844) passed 24 exact VTT captions, four chapter and article seeks, revised shots03/04 playback, final-frame/natural-ended playback, five-puzzle navigation, normal proof/bounds anchors without video seek, 8 example events, 12 budget rows, 5 threshold boundaries, footnote wrapping and overflow checks. See qa-site.json and qa-site-reading.json.

Date evidence: actual video completed 2026-10-25T11:56:02.858115+00:00; metadata updatedAt is 2026-10-25T11:56:02.858+00:00 after explicit truncation to milliseconds (115 microseconds discarded). The source remains actual render completion, not build/mtime. Created/published retain 2026-10-25 and firstRelease v0.67.0; edition displays 2026-10-25 19:56:02 版. JSON-LD and RSS first publication passed. See qa-site-dates.json.

All 169 frozen production inputs verified unchanged; current frozen article SHA256 is 10405dcb797c9c778b1214091346f7ffaedb5654ef028a0d54990572a49a2e11. Six upstream course meta/article/video byte sets match origin/main, including built videos. Draft EP35–37 have no built/public episode directories, navigation links, RSS URLs or own Pagefind fragment URLs; retired Agent directories remain absent. See qa-site-protection.json. Complete build/shared-check logs and script hashes are in qa-site-build.json.

Scope: local browser, delivery and built-site checks; no online GET, external publication or git operation by this task. Frozen media/article/covers were not edited. Old candidate/baseline evidence was not overwritten.
