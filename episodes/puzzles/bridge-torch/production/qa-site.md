P02 local site QA passed at 1440×1000 and 390×844.

6025 frames / 30 fps; 32 captions; 4 chapters. All chapter and article seeks, complete caption text/timing, start and ending playback, final frame, normal end, article-only proof, and puzzles navigation checked in Chromium. Screenshot paths and exact hashes are in qa-site.json.

Scope: delivery and browser behavior only; no claim of full human audiovisual review or measured understanding.

Build identity: v0.60.0; 102 built HTML files; Pagefind indexed 37 pages. `qa-site-build.json` records HTML/VTT/CSS/article hashes and the actual HEAD.

First attempt: desktop checks ran, then mobile document width was 404 at a 390px viewport. No per-action desktop numbers were persisted and none were reconstructed. The measured failure and original screenshot are retained in `qa-site-mobile-overflow-before.json`; the original desktop run is described separately.

Fix: only `.prose .footnotes { overflow-wrap:anywhere; }` was added to the existing page stylesheet. Plain commit identifiers in the source footnotes can now wrap. Production/published article bytes and all fourteen delivered source files remain identical. A fresh build and a complete two-viewport run produced the final `qa-site.json`. Actual post-fix footnote widths are 720/720 at desktop and 350/350 at mobile, with document widths exactly 1440 and 390 (`qa-site-footnotes-after.json`).

The site agent actually inspected the current desktop/mobile page, final-frame, proof, certificate and mobile footnote screenshots. On mobile, the wide certificate scrolls within its table; actual horizontal scrolling exposes the final potential column and goal value17 without widening the page (`qa-site-reading.json`).
