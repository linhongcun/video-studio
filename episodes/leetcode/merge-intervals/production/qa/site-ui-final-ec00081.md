# LC56 final site UI acceptance

**Status:** Passed

**Tested site HEAD:** `ec00081afb16d8d7907fd9661035c2e60a8dd73b`

**Site-derived article SHA-256:** `f15d4ed76923d301224312dd8cceb16a0f54a0f6e1ca65b7663813c272c64ba2`

**Production/publication video:** `b8a7cd91627d81173ccaeaad8eb3c61da0d16be1a29328e1ef6c965e6de3a2e2` (5,784,500 bytes)

## Current acceptance

The reported final UI check on the tested HEAD passed all four article rewatch controls. They scrolled to the player and started playback at `question` 0s, `sorting` 26.833s, `scan` 39.300s, and `close` 117.433s.

Mobile emulation passed at 390×844 in Chromium with touch enabled and hover disabled: SourceQuote open/close and focus return, light/dark themes, reading the article body, figures, code, and references, and no whole-page overflow.

The UI result was provided for this closeout; this agent did not rerun browser interactions. The previously reported desktop checks were reused, not repeated: video play/pause, fullscreen, chapters and code-card/appendix; SourceQuote hover/click and keyboard close; SVG original-viewer behavior.

## Scope and limitations

This confirms the reported UI state against the site tested at the HEAD and media SHA above. The mobile check was emulation, not a physical device; iOS/Safari was not tested. The full video was not replayed during this pass.

The historical v2 independent-review report remains unchanged; its statement that that review did not operate the browser remains accurate. The frozen production README still contains its pre-acceptance article-UI-pending note and was not edited because `README.md` is a frozen input. This record and `publication/site-integration.json` carry the later passed UI status. The candidate remains undeployed (`deployed: false`).
