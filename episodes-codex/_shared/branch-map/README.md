# Shared branch navigation

`index.ts` is the shared production implementation for the four transaction films. It has no React import or package dependency: each caller imports its own React and calls `createBranchNavigator(React)`. Original scene content is the detail child; subtitles remain outside the camera. The detail frame is 1920×900 at its original coordinates, with the camera clipped above y160 and below y900.

```tsx
import React from 'react';
import {createBranchNavigator} from '../../../_shared/branch-map';
import type {BranchMapSpec} from '../../../_shared/branch-map';
const Navigator = createBranchNavigator(React);
// Within the shot, with its real local frame and unchanged duration:
<Navigator spec={navigationSpec(shot, frame)} shotId={shot.id}
  frame={frame} durationInFrames={shot.durationInFrames}
  foreground={sentenceInitialTermTitle}>
  <Scene shot={shot} frame={frame}/>
</Navigator>
```

A supplied `foreground` is outside the camera and suppresses the default overview heading. Remove the corresponding title from `Scene`; do not duplicate it. This keeps sentence-initial labels aligned to the existing onset and visible for their required duration. Keep brand/corner labels outside the camera, but remove the old chapter/progress strip around y96–140: the shared breadcrumb occupies x430..1370, y77..151.

## Spec

- `nodes`: stable center coordinates `x/y`, `id`, Chinese `label`, optional width (default240), `kind` (`step`, `decision`, `success`, `failure`, `unknown`) and color. Prefer at most7–8 sparse nodes. The node detail window has the 1920:900 ratio. A flow, return edge or unknown state need not form a binary tree.
- `edges`: `id`, `from`, `to`, optional Chinese `label`, `via` coordinate pairs, `labelAt`, `dashed`, color. Ports follow the actual first/last segment using rectangle-ray intersection, so return edges do not run through the source. A self-loop can provide `via`; otherwise a visible return loop is generated below the node. Position labels clear of nodes and other labels.
- `shots`: binds a real or virtual shot ID to `focus`, optional `mode:'overview'`, highlighted node/edge IDs and `crumb`. `overviewTitle`/`overviewHint` override the spec defaults and keep a concrete conflict in the opening two seconds.
- `enter:{hold,zoom}` holds the same overview then zooms into the selected node. `exit:{zoom,hold}` returns to that overview before the shot ends. Omit both for a stable detailed view across consecutive shots in the same branch. Do not overlay a zoom on a mechanism event or a mandatory label: producers select explicit safe windows.

The selected node's screen position moves monotonically from its overview position to the screen center while scale changes continuously. Map text fades before it becomes giant background noise; node outlines persist longer as spatial anchors. Nonactive paths remain visible in overview. `actualNavState` returns phase/progress/camera/opacity for audit. `navigationEvents` provides start, quarter, middle, three-quarter, end and hold samples.

## Reusable preview helper

Run from the repository root (or use absolute paths), always keeping the temporary directory on the workspace:

```sh
export TMPDIR=/workspace/.video-studio-tmp
node episodes-codex/_shared/branch-map/qa.mjs --dir=episodes-codex/tx-2pc --out=/workspace/.video-studio-branch-qa/tx-2pc-final
node episodes-codex/_shared/branch-map/qa.mjs --dir=episodes-codex/tx-2pc --out=/workspace/.video-studio-branch-qa/tx-2pc-transition --range=1600:1760 --no-captions
```

`--audit-only` writes the same planned frame/state schedule without opening Chrome, useful for checking virtual shot IDs and label/camera timing.

The range example is illustrative: choose real boundaries from the current storyboard. `--frames=470,479,488,497,506` requests only specific actual frames. Without explicit frames/range the helper samples every shot, mechanism event, navigation quarter/hold and all label cue−1/cue/cue+62 points. Captioned stills and silent clips are separate inputs; do not compare silent images against captioned final MP4 frames.

The per-film `src/branch-map.ts` can export `navigationSpec`, `branchMapFor`, `getBranchMapSpec` or `branchMapSpec`. Films with internal virtual navigation segments instead export `navigationState(shot,frame)` and `navigationFrameSamples(shot)`, the latter returning `[name, realShotLocalFrame]` pairs. This supports Outbox's two narrative segments in shot13 while preserving its audio, subtitles and duration. Optional `navigationSampleFrames` adds local samples to the generic schedule.

`frames.json` records shared navigator and local source SHA values and rejects sources changed while previewing. Continuous ranges span real shot boundaries and include exact camera events relative to the clip, so reviewers need not rely on widely spaced contact points that miss a short zoom.

Use the one global render lock for clips (`flock /tmp/video-studio-render.lock`) and permit only one active Chrome/render in this environment. Start with a five-frame prototype and one real cross-shot range. After independent review, stop writes to production `index.ts` before expanding all four films. Any further production change invalidates their preview source fingerprints; notify root and all affected producers first. Changes only to this QA helper or documentation do not change the already inspected camera implementation.
