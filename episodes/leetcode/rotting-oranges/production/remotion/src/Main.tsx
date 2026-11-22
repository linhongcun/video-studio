import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {LeetcodeBackdrop, LeetcodeHeader} from '../../../../../_shared/leetcode-video/Frame';
import {C, FONT, MONO} from '../../../../../_shared/leetcode-video/theme';
import {STORYBOARD, TRACE, shots, type Run, type Shot, type TraceEvent} from './data';
import {actionProgress, clamp, easeOutCubic} from './timeline';
import {CodeCard} from './CodeCard';
import {CrateCell, FreshOrangeGlyph, LayerQueueBar, PAL, RottenOrangeGlyph, SpreadOverlay, T} from './OrangesArt';

declare const __HAS_VOICE_AUDIO__: boolean;

function currentEvent(shot: Shot, frame: number, run: Run) {
  const acts = (shot.actionCues ?? []).filter((a) => a.events?.length);
  const subs = shot.subtitles ?? [];
  const shotEnd = Math.min(shot.durationInFrames - 6, (subs.length ? subs[subs.length - 1].to! : shot.durationInFrames - 1) - 4);
  let idx = acts.length ? acts[0].events![0] : run.events.length - 1;
  let frac = 0;
  for (let i = 0; i < acts.length; i++) {
    const a = acts[i];
    const start = shot.cueFrames?.labels?.[a.cue] ?? 0;
    const end = i + 1 < acts.length ? (shot.cueFrames?.labels?.[acts[i + 1].cue] ?? shotEnd) : shotEnd;
    if (frame < start) break;
    const list = a.events!;
    const p = clamp((frame - start) / Math.max(1, end - start));
    idx = list[Math.min(list.length - 1, Math.floor(p * list.length))];
    frac = p >= 1 ? 1 : p * list.length - Math.floor(p * list.length);
    if (frame < end) break;
  }
  return {e: run.events[idx], frac, idx};
}

function splitSubtitle(text: string) {
  const chunks = text.match(/[^，；：。！？]+[，；：。！？]?/g) ?? [text];
  const lines: string[] = [];
  let line = '';
  for (const c of chunks) {
    if (line.length + c.length > 42 && line) {
      lines.push(line);
      line = '';
    }
    line += c;
  }
  if (line) lines.push(line);
  return lines.flatMap((l) => l.match(/.{1,42}/g) ?? []);
}

/* Shot 01: Numeric grid -> 0-based indices, 0/1/2 values & 4-dir simultaneous spread rules */
function InputShot({shot, frame}: {shot: Shot; frame: number}) {
  const p1 = actionProgress(shot, frame, 'first', 0, 0.85);
  const p2 = actionProgress(shot, frame, 'second', 0, 0.85);
  const grid = TRACE.main.initialGrid;
  const leftCell = 116;
  const leftGap = 14;
  const lx = 180;
  const ly = 322;

  return (
    <g>
      <T x={lx} y={272} size={26} color={C.muted} weight={600}>
        输入矩阵 grid（3 行 × 4 列，行列从 0 开始编号）
      </T>
      {[0, 1, 2, 3].map((c) => (
        <T key={`lc-${c}`} x={lx + c * (leftCell + leftGap) + leftCell / 2} y={ly - 14} size={22} color={C.gold} anchor="middle" mono weight={700}>
          c={c}
        </T>
      ))}
      {[0, 1, 2].map((r) => (
        <T key={`lr-${r}`} x={lx - 22} y={ly + r * (leftCell + leftGap) + leftCell / 2 + 8} size={22} color={C.gold} anchor="end" mono weight={700}>
          r={r}
        </T>
      ))}
      {grid.map((row, r) =>
        row.map((val, c) => {
          const x = lx + c * (leftCell + leftGap);
          const y = ly + r * (leftCell + leftGap);
          const col = val === 2 ? '#FDA4AF' : val === 1 ? PAL.freshGlow : '#64748B';
          const bg = val === 2 ? '#341A26' : val === 1 ? '#291D14' : '#0D1526';
          return (
            <g key={`m-${r}-${c}`}>
              <rect x={x} y={y} width={leftCell} height={leftCell} rx={16} fill={bg} stroke={val === 0 ? '#24344D' : col} strokeWidth={val === 0 ? 2 : 3} />
              <T x={x + leftCell / 2} y={y + leftCell / 2 + 16} size={46} color={col} anchor="middle" mono weight={700}>
                {val}
              </T>
            </g>
          );
        }),
      )}

      {/* Right: Rules & 0/1/2 meaning cards */}
      <g opacity={0.3 + 0.7 * p1}>
        <rect x={820} y={306} width={960} height={240} rx={22} fill={C.surface} stroke={C.edge} strokeWidth={2} />
        <T x={860} y={358} size={28} color={C.text} weight={700}>
          每个格子的三种状态值
        </T>
        <g>
          <rect x={860} y={388} width={52} height={42} rx={10} fill="#0D1526" stroke="#475569" strokeWidth={2} />
          <T x={886} y={418} size={28} color="#94A3B8" anchor="middle" mono weight={700}>0</T>
          <T x={934} y={417} size={26} color={C.text}>空位（会挡住腐烂继续扩散）</T>
        </g>
        <g>
          <rect x={860} y={442} width={52} height={42} rx={10} fill="#291D14" stroke={PAL.freshGlow} strokeWidth={2} />
          <T x={886} y={472} size={28} color={PAL.freshGlow} anchor="middle" mono weight={700}>1</T>
          <T x={934} y={471} size={26} color={C.text}>新鲜橘子</T>
        </g>
        <g>
          <rect x={860} y={496} width={52} height={42} rx={10} fill="#341A26" stroke="#FDA4AF" strokeWidth={2} />
          <T x={886} y={526} size={28} color="#FDA4AF" anchor="middle" mono weight={700}>2</T>
          <T x={934} y={525} size={26} color={C.text}>腐烂橘子（起点可能不止一个）</T>
        </g>
      </g>

      <g opacity={0.25 + 0.75 * p2}>
        <rect x={820} y={574} width={960} height={246} rx={22} fill="#123137" stroke={C.teal} strokeWidth={3} />
        <T x={860} y={628} size={30} color={C.teal} weight={700}>
          扩散规则与题目目标
        </T>
        <T x={860} y={678} size={26} color={C.text}>
          • 每分钟所有烂橘子同时向上、下、左、右传染相邻一格
        </T>
        <T x={860} y={724} size={26} color={PAL.bad}>
          • 空位 0 阻断传播，斜对角方向不会传染
        </T>
        <T x={860} y={774} size={27} color={C.gold} weight={600}>
          • 目标：求全部新鲜橘子腐烂的最少分钟数
        </T>
      </g>
    </g>
  );
}

/* Shot 02: Cell-by-cell mapping into Orange Crate + highlight (0,0) & (0,1) + -1 return */
function MappingShot({shot, frame}: {shot: Shot; frame: number}) {
  const p1 = actionProgress(shot, frame, 'first', 0, 0.85);
  const p2 = actionProgress(shot, frame, 'second', 0, 0.85);
  const grid = TRACE.main.initialGrid;
  const leftCell = 112;
  const leftGap = 12;
  const lx = 175;
  const ly = 328;
  const rightCell = 124;
  const rightGap = 14;
  const rx = 1090;
  const ry = 314;

  return (
    <g>
      <T x={lx} y={272} size={26} color={C.muted} weight={600}>
        输入矩阵 grid（3 行 × 4 列）
      </T>
      {[0, 1, 2, 3].map((c) => (
        <T key={`lc-${c}`} x={lx + c * (leftCell + leftGap) + leftCell / 2} y={ly - 14} size={20} color="#7F93AE" anchor="middle" mono>
          c={c}
        </T>
      ))}
      {[0, 1, 2].map((r) => (
        <T key={`lr-${r}`} x={lx - 22} y={ly + r * (leftCell + leftGap) + leftCell / 2 + 8} size={20} color="#7F93AE" anchor="end" mono>
          r={r}
        </T>
      ))}
      {grid.map((row, r) =>
        row.map((val, c) => {
          const x = lx + c * (leftCell + leftGap);
          const y = ly + r * (leftCell + leftGap);
          const isDemo = r === 0 && (c === 0 || c === 1);
          const col = val === 2 ? '#FDA4AF' : val === 1 ? PAL.freshGlow : '#64748B';
          const bg = val === 2 ? '#341A26' : val === 1 ? '#291D14' : '#0D1526';
          return (
            <g key={`m-${r}-${c}`}>
              <rect x={x} y={y} width={leftCell} height={leftCell} rx={16} fill={bg} stroke={isDemo ? C.gold : val === 0 ? '#24344D' : col} strokeWidth={isDemo ? 4 : val === 0 ? 2 : 3} />
              <T x={x + leftCell / 2} y={y + leftCell / 2 + 16} size={46} color={col} anchor="middle" mono weight={700}>
                {val}
              </T>
            </g>
          );
        }),
      )}

      <rect x={150} y={732} width={520} height={112} rx={16} fill={C.surface} stroke={C.gold} strokeWidth={2} />
      <T x={182} y={778} size={25} color={C.gold} mono weight={600}>
        (0,0) = 2 → 左上角烂橘子
      </T>
      <T x={182} y={818} size={25} color={PAL.freshGlow} mono weight={600}>
        (0,1) = 1 → 右邻新鲜橘子
      </T>

      <g>
        <path d="M 730 510 H 950" stroke={C.gold} strokeWidth={5} strokeLinecap="round" />
        <path d="M 932 494 L 962 510 L 932 526" fill="none" stroke={C.gold} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" />
        <T x={845} y={486} size={24} color={C.gold} anchor="middle" weight={600}>
          逐格对应
        </T>
        <T x={845} y={554} size={21} color={C.muted} anchor="middle">
          最少分钟数 / -1
        </T>
      </g>

      <g>
        <T x={rx} y={272} size={26} color={C.teal} weight={600}>
          橘子箱网格（上下左右扩散，斜角不传染）
        </T>
        {grid.map((row, r) =>
          row.map((val, c) => {
            const idx = r * 4 + c;
            const cellP = clamp((p1 * 12 - idx * 0.45) / 2.2);
            return (
              <CrateCell
                key={`rc-${r}-${c}`}
                x={rx + c * (rightCell + rightGap)}
                y={ry + r * (rightCell + rightGap)}
                size={rightCell}
                r={r}
                c={c}
                val={val}
                rotMinute={null}
                isSource={r === 0 && c === 0}
                highlightTeal={r === 0 && c === 1}
                showValueTag
                orangeOpacity={0.25 + 0.75 * cellP}
              />
            );
          }),
        )}
        {p1 > 0.45 && (
          <g opacity={clamp((p1 - 0.45) / 0.35)}>
            <line x1={rx + 96} y1={ry + 62} x2={rx + 150} y2={ry + 62} stroke={C.teal} strokeWidth={5} strokeLinecap="round" />
            <path d={`M ${rx + 138} ${ry + 52} L ${rx + 154} ${ry + 62} L ${rx + 138} ${ry + 72}`} fill="none" stroke={C.teal} strokeWidth={4.5} strokeLinecap="round" />
            <line x1={rx + 62} y1={ry + 96} x2={rx + 62} y2={ry + 150} stroke={C.teal} strokeWidth={5} strokeLinecap="round" />
            <path d={`M ${rx + 52} ${ry + 138} L ${rx + 62} ${ry + 154} L ${rx + 72} ${ry + 138}`} fill="none" stroke={C.teal} strokeWidth={4.5} strokeLinecap="round" />
            <line x1={rx + 94} y1={ry + 94} x2={rx + 156} y2={ry + 156} stroke={PAL.bad} strokeWidth={4} strokeDasharray="6 5" />
            <circle cx={rx + 126} cy={ry + 126} r={14} fill="#2A121C" stroke={PAL.bad} strokeWidth={2.5} />
            <path d={`M ${rx + 120} ${ry + 120} L ${rx + 132} ${ry + 132} M ${rx + 132} ${ry + 120} L ${rx + 120} ${ry + 132}`} stroke={PAL.bad} strokeWidth={2.5} strokeLinecap="round" />
          </g>
        )}
        <g opacity={0.35 + 0.65 * p2}>
          <rect x={rx} y={732} width={538} height={112} rx={16} fill={C.surface} stroke={C.teal} strokeWidth={2.5} />
          <T x={rx + 28} y={778} size={25} color={C.teal} weight={600}>
            全部烂完 → 返回最少分钟数
          </T>
          <T x={rx + 28} y={818} size={24} color={PAL.bad} weight={600}>
            有任何新鲜橘子永远烂不到 → 返回 -1
          </T>
        </g>
      </g>
    </g>
  );
}

/* Shot 02: Why single-source first fails vs simultaneous multi-source start */
function ContrastShot({shot, frame}: {shot: Shot; frame: number}) {
  const p1 = actionProgress(shot, frame, 'first', 0, 0.9);
  const p2 = actionProgress(shot, frame, 'second', 0, 0.88);
  const grid = TRACE.main.initialGrid;
  const dTL = TRACE.contrastSingleSource.fromTopLeft;
  const cell = 136;
  const gap = 16;
  const ox = 150;
  const oy = 310;
  const step = cell + gap;
  const center = (r: number, c: number): [number, number] => [ox + c * step + cell / 2, oy + r * step + cell / 2];

  const wrongStep = p1 * 3; // 0..3 steps from (0,0) -> (1,0) -> (2,0) -> (2,1)
  const showConflict = p1 > 0.55;
  const conflictP = clamp((p1 - 0.55) / 0.35);

  return (
    <g>
      <T x={ox} y={272} size={26} color={C.gold} weight={600}>
        只从 (0,0) 一路算到底 vs (2,2) 同时出发
      </T>

      {grid.map((row, r) =>
        row.map((val, c) => {
          const is21 = r === 2 && c === 1;
          const is22 = r === 2 && c === 2;
          const is00 = r === 0 && c === 0;
          const tlDist = dTL[r][c];
          let badge: {text: string; color: string; bg?: string} | undefined;
          if (val === 2 && p2 > 0.35) {
            badge = {text: 'T=0', color: C.gold, bg: '#3A2D15'};
          } else if (is21 && showConflict) {
            badge = p2 > 0.4 ? {text: 'T=1 ✓', color: C.teal, bg: '#133238'} : {text: '3分≠1分', color: PAL.bad, bg: '#3B1424'};
          } else if (tlDist !== null && tlDist > 0 && wrongStep >= tlDist - 0.15 && p2 < 0.4) {
            badge = {text: `单源:${tlDist}`, color: '#FDBA74', bg: '#2B1F14'};
          }
          return (
            <CrateCell
              key={`c-${r}-${c}`}
              x={ox + c * step}
              y={oy + r * step}
              size={cell}
              r={r}
              c={c}
              val={val}
              isSource={(is00 && p2 > 0.2) || (is22 && (showConflict || p2 > 0.2))}
              highlightBad={is21 && showConflict && p2 < 0.4}
              highlightTeal={is21 && p2 >= 0.4}
              customBadge={badge}
            />
          );
        }),
      )}

      {/* Animated wrong single-source path (0,0)->(1,0)->(2,0)->(2,1) */}
      {(() => {
        const pts: [number, number][] = [center(0, 0), center(1, 0), center(2, 0), center(2, 1)];
        return (
          <g opacity={p2 > 0.5 ? 0.22 : 0.9}>
            {[0, 1, 2].map((seg) => {
              const sp = clamp(wrongStep - seg);
              if (sp <= 0) return null;
              const [x1, y1] = pts[seg];
              const [x2, y2] = pts[seg + 1];
              const ex = x1 + (x2 - x1) * sp;
              const ey = y1 + (y2 - y1) * sp;
              return <line key={seg} x1={x1} y1={y1} x2={ex} y2={ey} stroke={PAL.bad} strokeWidth={5} strokeDasharray="10 7" strokeLinecap="round" />;
            })}
          </g>
        );
      })()}

      {/* Immediate real 1-minute arrow (2,2)->(2,1) */}
      {showConflict && (
        <g opacity={conflictP}>
          {(() => {
            const [x1, y1] = center(2, 2);
            const [x2, y2] = center(2, 1);
            const sx = x1 - 42;
            const tx = x2 + 46;
            const ex = sx + (tx - sx) * easeOutCubic(conflictP);
            return (
              <>
                <line x1={sx} y1={y1} x2={ex} y2={y2} stroke={C.teal} strokeWidth={7} strokeLinecap="round" />
                <path d={`M ${ex + 16} ${y2 - 11} L ${ex} ${y2} L ${ex + 16} ${y2 + 11}`} fill="none" stroke={C.teal} strokeWidth={6} strokeLinecap="round" />
              </>
            );
          })()}
        </g>
      )}

      {/* Right comparison panel */}
      <g>
        <rect x={830} y={310} width={950} height={175} rx={20} fill={C.surface} stroke={PAL.bad} strokeWidth={2.5} />
        <T x={866} y={362} size={30} color={PAL.bad} weight={700}>
          单源先算到底：时间直接算错
        </T>
        <T x={866} y={408} size={25} color={C.text}>
          只从 (0,0) 走三步到 (2,1) → 误判第 3 分钟
        </T>
        <T x={866} y={448} size={25} color={C.teal}>
          实际 (2,2) 就在身旁 → 第 1 分钟就已经传染！
        </T>

        <g opacity={0.25 + 0.75 * p2}>
          <rect x={830} y={512} width={950} height={145} rx={20} fill={C.surface} stroke={C.edge} strokeWidth={2} />
          <T x={866} y={562} size={28} color="#FDBA74" weight={700}>
            每个烂橘子各扫全图再取最小：反复扫描 k 遍
          </T>
          <T x={866} y={610} size={24} color={C.muted}>
            k 个烂橘子把同一张网格重复遍历 k 次 → O(k · m · n)
          </T>

          <rect x={830} y={684} width={950} height={152} rx={20} fill="#123137" stroke={C.teal} strokeWidth={3.5} />
          <T x={866} y={736} size={31} color={C.teal} weight={700}>
            思路落地：所有初始烂橘子同站第 0 分钟
          </T>
          <T x={866} y={786} size={25} color={C.text}>
            把 (0,0) 和 (2,2) 一起放进同一个起点集合，同步往外扩散
          </T>
        </g>
      </g>
    </g>
  );
}

/* Shot 03: Introduce FIFO Queue + len(queue) layer locking -> Name Multi-Source BFS */
function QueueIntroShot({shot, frame}: {shot: Shot; frame: number}) {
  const p1 = actionProgress(shot, frame, 'first', 0, 0.9);
  const p2 = actionProgress(shot, frame, 'second', 0, 0.85);
  const grid = TRACE.main.initialGrid;
  const cell = 114;
  const gap = 12;
  const ox = 135;
  const oy = 326;
  const step = cell + gap;

  return (
    <g>
      <T x={ox} y={276} size={25} color={C.muted} weight={600}>
        第 0 分钟双起点：(0,0) 与 (2,2)
      </T>
      {grid.map((row, r) =>
        row.map((val, c) => (
          <CrateCell
            key={`q-${r}-${c}`}
            x={ox + c * step}
            y={oy + r * step}
            size={cell}
            r={r}
            c={c}
            val={val}
            rotMinute={val === 2 ? 0 : null}
            isSource={val === 2}
          />
        )),
      )}

      {/* Right: FIFO Queue & Layer-Lock diagram */}
      <g>
        <rect x={710} y={290} width={1080} height={355} rx={22} fill={C.surface} stroke={C.edge} strokeWidth={2} />
        <T x={750} y={342} size={30} color={C.text} weight={700}>
          先进先出队列 + 每分钟锁定当前层长度
        </T>

        {/* Queue pipeline */}
        <T x={750} y={406} size={22} color={C.gold} weight={600}>
          队头出队 ←
        </T>
        <T x={1750} y={406} size={22} color={C.teal} anchor="end" weight={600}>
          ← 新烂橘子排到队尾
        </T>

        {/* Layer 0 bracket */}
        <g opacity={0.3 + 0.7 * clamp(p1 * 1.4)}>
          <rect x={750} y={428} width={332} height={118} rx={16} fill="rgba(255,204,112,0.08)" stroke={C.gold} strokeWidth={3} />
          <T x={916} y={456} size={20} color={C.gold} anchor="middle" weight={700}>
            第 0 层 · 锁定 len(queue) = 2
          </T>
          <rect x={776} y={474} width={128} height={54} rx={12} fill="#101B2E" stroke={C.gold} strokeWidth={2.5} />
          <T x={840} y={510} size={27} color={C.gold} anchor="middle" mono weight={700}>(0,0)</T>
          <rect x={926} y={474} width={128} height={54} rx={12} fill="#101B2E" stroke={C.gold} strokeWidth={2.5} />
          <T x={990} y={510} size={27} color={C.gold} anchor="middle" mono weight={700}>(2,2)</T>
        </g>

        {/* Divider + Layer 1 preview */}
        <g opacity={clamp((p1 - 0.35) / 0.45)}>
          <line x1={1106} y1={422} x2={1106} y2={554} stroke="#94A3B8" strokeWidth={3} strokeDasharray="7 6" />
          <rect x={1130} y={428} width={620} height={118} rx={16} fill="rgba(86,228,211,0.08)" stroke={C.teal} strokeWidth={2.5} strokeDasharray="8 6" />
          <T x={1440} y={456} size={20} color={C.teal} anchor="middle" weight={700}>
            下一层（留给第 2 分钟）
          </T>
          {['(1,0)', '(0,1)', '(1,2)', '(2,1)'].map((lbl, j) => (
            <g key={lbl}>
              <rect x={1156 + j * 146} y={474} width={126} height={54} rx={12} fill="#101B2E" stroke={C.teal} strokeWidth={2} />
              <T x={1219 + j * 146} y={510} size={25} color={C.teal} anchor="middle" mono weight={700}>
                {lbl}
              </T>
            </g>
          ))}
        </g>

        <T x={750} y={608} size={25} color={C.muted}>
          规则：这一分钟只弹出锁定的这一批；新传染的排在队尾，绝不插队提前扩散
        </T>
      </g>

      {/* Bottom method reveal card (only appears in Sentence 1!) */}
      <g opacity={p2}>
        <rect x={710} y={678} width={1080} height={164} rx={22} fill="#123137" stroke={C.teal} strokeWidth={3.5} />
        <T x={750} y={736} size={36} color={C.gold} weight={750}>
          多源广度优先搜索（多源 BFS）
        </T>
        <T x={750} y={784} size={26} color={C.text}>
          每一层严格对应 1 分钟 · 到最近烂橘子距离相同的橘子在同一分钟被碰到
        </T>
        <T x={750} y={822} size={22} color={C.teal}>
          初始烂橘子全在深度 0 → 第 d 层首次碰到 = 最早第 d 分钟腐烂
        </T>
      </g>
    </g>
  );
}

/* Status banner helper derived strictly from real TraceEvent (L010 / L073) */
function eventCaption(e: TraceEvent): [string, string] {
  if (e.kind === 'init') return [`初始状态：${e.initialRotten?.length ?? 0} 个烂橘子入队，共 ${e.fresh} 个新鲜橘子`, C.gold];
  if (e.kind === 'layer_start') return [`第 ${e.layerMinute} 分钟开始：锁定当前层长度 len(queue) = ${e.layerSize}`, C.gold];
  if (e.kind === 'expand') {
    const [r, c] = e.source!;
    const rots = e.infected ?? [];
    const hasCollision = (e.checks ?? []).some((ch) => ch.outcome === 'already_rotten' && (ch.existingMinute ?? 0) >= 2);
    if (rots.length > 0) {
      const coords = rots.map(([ir, ic]) => `(${ir},${ic})`).join('、');
      return [`出队 (${r},${c})：传染 ${coords} 并立刻标 2 入队，fresh = ${e.fresh}`, C.teal];
    }
    if (hasCollision) {
      return [`出队 (${r},${c})：邻居已在本分钟标为 2 → 直接跳过，不重复入队`, PAL.skip];
    }
    return [`出队 (${r},${c})：四邻均无新鲜橘子，本步无新入队`, C.muted];
  }
  if (e.kind === 'layer_end') return [`第 ${e.completedMinute} 层处理完成：minutes → ${e.minutes}，剩余 fresh = ${e.fresh}`, C.teal];
  if (e.value === -1) return [`队列已空但 fresh = ${e.fresh} > 0 → 有橘子永远烂不到，返回 -1`, PAL.bad];
  if (e.stopReason === 'all_rotten_queue_nonempty') {
    return [`fresh 已清零，队列虽非空也立刻停止 → 返回 ${e.value} 分钟`, C.gold];
  }
  return [`全部腐烂，返回 ${e.value} 分钟`, C.teal];
}

/* Shots 04, 05, 06: Live Multi-Source Trace Board on Main 3×4 Grid */
function TraceBoardShot({shot, frame, showStopGuard = false}: {shot: Shot; frame: number; showStopGuard?: boolean}) {
  const run = TRACE.main;
  const {e, frac} = currentEvent(shot, frame, run);
  const cell = 132;
  const gap = 14;
  const ox = 152;
  const oy = 294;
  const step = cell + gap;
  const infectedSet = new Set((e.infected ?? []).map(([r, c]) => `${r},${c}`));
  const [caption, captionColor] = eventCaption(e);
  const isStopMoment = showStopGuard && e.kind === 'result';

  return (
    <g>
      {/* Left: 3×4 Orange Crate */}
      {e.grid.map((row, r) =>
        row.map((val, c) => {
          const isSrc = e.kind === 'expand' && e.source?.[0] === r && e.source?.[1] === c;
          const justInf = e.kind === 'expand' && infectedSet.has(`${r},${c}`);
          return (
            <CrateCell
              key={`tb-${r}-${c}`}
              x={ox + c * step}
              y={oy + r * step}
              size={cell}
              r={r}
              c={c}
              val={val}
              rotMinute={e.rotTime[r][c]}
              isSource={isSrc}
              justInfected={justInf}
              infectProgress={frac}
            />
          );
        }),
      )}

      {/* Four-direction check arrows */}
      {e.kind === 'expand' && e.source && e.checks && (
        <SpreadOverlay
          ox={ox}
          oy={oy}
          cellSize={cell}
          gap={gap}
          rows={run.rows}
          cols={run.cols}
          source={e.source}
          checks={e.checks}
          progress={frac}
        />
      )}

      {/* Right side: Live explanation card */}
      <g>
        <rect
          x={840}
          y={266}
          width={955}
          height={446}
          rx={22}
          fill={C.surface}
          stroke={isStopMoment ? C.gold : C.edge}
          strokeWidth={isStopMoment ? 3.5 : 2}
        />
        {!isStopMoment ? (
          <>
            <T x={880} y={322} size={25} color={C.muted} weight={600}>
              当前执行状态
            </T>
            <T x={880} y={376} size={30} color={captionColor} weight={700}>
              {caption}
            </T>
            <line x1={880} y1={408} x2={1755} y2={408} stroke={C.edge} strokeWidth={1.5} />

            {/* Structured check list for current expand event */}
            {e.kind === 'expand' && e.checks ? (
              <g>
                <T x={880} y={450} size={23} color={C.muted}>
                  四邻检查（源点 ({e.source![0]},{e.source![1]})）：
                </T>
                {e.checks.map((ch, j) => {
                  const dirLabel = {up: '上', down: '下', left: '左', right: '右'}[ch.dir];
                  const outcomeMap = {
                    rot: [`(${ch.to[0]},${ch.to[1]}) 新鲜 → 立刻改 2 并入队`, C.teal],
                    oob: [`(${ch.to[0]},${ch.to[1]}) 越出网格边界 → 跳过`, PAL.bad],
                    empty: [`(${ch.to[0]},${ch.to[1]}) 是空位 0 → 阻断跳过`, '#94A3B8'],
                    already_rotten: [
                      `(${ch.to[0]},${ch.to[1]}) 已在第 ${ch.existingMinute} 分钟变 2 → 跳过不重复入队`,
                      PAL.skip,
                    ],
                  } as const;
                  const [desc, col] = outcomeMap[ch.outcome];
                  return (
                    <g key={j}>
                      <rect x={880} y={472 + j * 54} width={44} height={38} rx={9} fill="#101B2E" stroke={col} strokeWidth={2} />
                      <T x={902} y={499 + j * 54} size={22} color={col} anchor="middle" weight={700}>
                        {dirLabel}
                      </T>
                      <T x={944} y={499 + j * 54} size={24} color={col}>
                        {desc}
                      </T>
                    </g>
                  );
                })}
              </g>
            ) : (
              <g>
                <T x={880} y={468} size={27} color={C.text}>
                  {e.kind === 'layer_start'
                    ? `本轮循环：for _ in range(${e.layerSize})，只处理当前层节点`
                    : `本层全部出队完成，分钟计数器 +1 → minutes = ${e.minutes}`}
                </T>
                <T x={880} y={528} size={25} color={C.muted}>
                  {e.kind === 'layer_start'
                    ? '新传染入队的橘子统一排到队尾，等待下一分钟处理'
                    : e.fresh > 0
                      ? `还有 ${e.fresh} 个新鲜橘子，继续处理下一层`
                      : '所有新鲜橘子已全部腐烂，准备检查循环停止条件'}
                </T>
                <rect x={880} y={576} width={875} height={96} rx={16} fill="#101B2E" stroke={C.teal} strokeWidth={2} />
                <T x={914} y={634} size={28} color={C.teal} mono weight={600}>
                  minutes = {e.minutes}  ·  fresh = {e.fresh}  ·  len(queue) = {e.queue.length}
                </T>
              </g>
            )}
          </>
        ) : (
          /* Shot 06 Sentence 1: Dedicated stop-condition spotlight! */
          <g>
            <T x={880} y={322} size={32} color={C.gold} weight={750}>
              防多算最后一分钟的关键守卫
            </T>
            <rect x={880} y={356} width={875} height={92} rx={16} fill="#2E2514" stroke={C.gold} strokeWidth={2.5} />
            <T x={914} y={396} size={26} color={C.gold} mono weight={700}>
              queue = [(0, 3)]   ← 队列并不为空！
            </T>
            <T x={914} y={432} size={24} color={C.text}>
              如果只写 while queue: 会白跑第 4 层，错误返回 4
            </T>

            <rect x={880} y={470} width={875} height={110} rx={16} fill="#123137" stroke={C.teal} strokeWidth={3} />
            <T x={914} y={518} size={29} color={C.teal} mono weight={700}>
              while queue and fresh &gt; 0:
            </T>
            <T x={914} y={560} size={25} color={C.text}>
              此时 fresh == 0 → 条件为假，循环立刻停止，正确返回 3
            </T>

            <T x={880} y={644} size={26} color={C.muted}>
              结论：全部 7 个新鲜橘子最少 3 分钟腐烂完毕
            </T>
          </g>
        )}
      </g>

      {/* Bottom Layered Queue Dock */}
      <LayerQueueBar
        queue={e.queue}
        remainingInLayer={e.kind === 'expand' ? e.remainingInLayer : e.kind === 'layer_start' ? e.layerSize : undefined}
        activeSource={e.kind === 'expand' ? e.source : null}
        fresh={e.fresh}
        minutes={e.minutes}
        highlightStop={isStopMoment}
      />
    </g>
  );
}

/* Shot 07: Explicit reset to Official Example 2 -> Isolated orange returns -1 */
function ImpossibleShot({shot, frame}: {shot: Shot; frame: number}) {
  const run = TRACE.impossible;
  const {e, frac} = currentEvent(shot, frame, run);
  const cell = 148;
  const gap = 16;
  const ox = 180;
  const oy = 264;
  const step = cell + gap;
  const isEnd = e.kind === 'result' || e.id >= 15;

  return (
    <g>
      {e.grid.map((row, r) =>
        row.map((val, c) => {
          const isIsolated = r === 2 && c === 0;
          const isWall = (r === 1 && c === 0) || (r === 2 && c === 1);
          return (
            <CrateCell
              key={`imp-${r}-${c}`}
              x={ox + c * step}
              y={oy + r * step}
              size={cell}
              r={r}
              c={c}
              val={val}
              rotMinute={e.rotTime[r][c]}
              isSource={e.kind === 'expand' && e.source?.[0] === r && e.source?.[1] === c}
              highlightBad={isEnd && (isIsolated || isWall)}
            />
          );
        }),
      )}

      {/* Show diagonal blocked arrow from (1,1) to (2,0) at the end */}
      {isEnd && (
        <g>
          <line
            x1={ox + step + 30}
            y1={oy + step + cell - 30}
            x2={ox + cell - 26}
            y2={oy + 2 * step + 26}
            stroke={PAL.bad}
            strokeWidth={5}
            strokeDasharray="8 6"
          />
          <circle cx={ox + cell + 8} cy={oy + 2 * step - 8} r={16} fill="#361321" stroke={PAL.bad} strokeWidth={3} />
          <path
            d={`M ${ox + cell + 1} ${oy + 2 * step - 15} L ${ox + cell + 15} ${oy + 2 * step - 1} M ${ox + cell + 15} ${oy + 2 * step - 15} L ${ox + cell + 1} ${oy + 2 * step - 1}`}
            stroke={PAL.bad}
            strokeWidth={3}
            strokeLinecap="round"
          />
        </g>
      )}

      {/* Right explanation card */}
      <g>
        <rect x={760} y={264} width={1040} height={476} rx={22} fill={C.surface} stroke={isEnd ? PAL.bad : C.edge} strokeWidth={isEnd ? 3.5 : 2} />
        <T x={800} y={322} size={30} color={C.gold} weight={700}>
          明确重置 · 官方示例 2（3 × 3）
        </T>
        <T x={800} y={372} size={25} color={C.muted} mono>
          grid = [[2, 1, 1], [0, 1, 1], [1, 0, 1]]
        </T>
        <line x1={800} y1={402} x2={1760} y2={402} stroke={C.edge} strokeWidth={1.5} />

        <T x={800} y={456} size={28} color={C.text}>
          前 4 分钟传染 5 个可达橘子；随后 (2,2) 出队无新染、队列变空
        </T>
        <T x={800} y={510} size={26} color={isEnd ? PAL.bad : C.muted} weight={isEnd ? 600 : 400}>
          左下角 (2,0) 被上方 (1,0)=0 与右侧 (2,1)=0 彻底隔离
        </T>
        <T x={800} y={554} size={25} color={isEnd ? C.text : C.muted}>
          腐烂只能上下左右传播，不能沿斜对角跨过空位
        </T>

        <rect
          x={800}
          y={598}
          width={960}
          height={108}
          rx={16}
          fill={isEnd ? '#331521' : '#101B2E'}
          stroke={isEnd ? PAL.bad : C.edge}
          strokeWidth={isEnd ? 3 : 2}
        />
        <T x={838} y={644} size={28} color={isEnd ? PAL.bad : C.muted} mono weight={700}>
          {isEnd ? 'queue 已空，fresh = 1 > 0 → 返回 -1' : `前 4 分钟扩散：已传染 ${6 - e.fresh} 个，fresh = ${e.fresh}`}
        </T>
        <T x={838} y={684} size={22} color={C.muted}>
          {isEnd ? '并非扩散顺序问题，而是 (2,0) 永远无法被任何烂橘子碰到' : '等待 (2,2) 最终出队后检查剩余新鲜橘子'}
        </T>
      </g>

      <LayerQueueBar
        queue={e.queue}
        activeSource={e.kind === 'expand' ? e.source : null}
        fresh={e.fresh}
        minutes={Math.min(4, e.minutes)}
        blocked={isEnd}
      />
    </g>
  );
}

/* Shot 08: Three boundary mini-crates */
function EdgeShot({shot, frame}: {shot: Shot; frame: number}) {
  const p1 = actionProgress(shot, frame, 'first', 0, 0.85);
  const p2 = actionProgress(shot, frame, 'second', 0, 0.85);

  const MiniGrid = ({
    grid,
    rot,
    ox,
    oy,
    cell,
  }: {
    grid: number[][];
    rot?: (number | null)[][];
    ox: number;
    oy: number;
    cell: number;
  }) => (
    <g>
      {grid.map((row, r) =>
        row.map((val, c) => (
          <CrateCell
            key={`${r}-${c}`}
            x={ox + c * (cell + 10)}
            y={oy + r * (cell + 10)}
            size={cell}
            r={r}
            c={c}
            val={val}
            rotMinute={rot ? rot[r][c] : null}
            showCoords={false}
          />
        )),
      )}
    </g>
  );

  const ex1End = TRACE.officialEx1.events[TRACE.officialEx1.events.length - 1];

  return (
    <g>
      {/* Card 1: Official Ex 3 [[0,2]] -> 0 */}
      <g opacity={0.25 + 0.75 * p1}>
        <rect x={125} y={272} width={530} height={585} rx={22} fill={C.surface} stroke={C.teal} strokeWidth={2.5} />
        <T x={160} y={326} size={28} color={C.teal} weight={700}>
          官方示例 3 · 无新鲜橘子
        </T>
        <T x={160} y={366} size={22} color={C.muted} mono>
          grid = [[0, 2]]
        </T>
        <MiniGrid grid={TRACE.noFresh.initialGrid} rot={[[null, 0]]} ox={260} oy={430} cell={125} />
        <T x={390} y={632} size={24} color={C.text} anchor="middle">
          初始 fresh == 0
        </T>
        <T x={390} y={672} size={22} color={C.muted} anchor="middle">
          while 循环一次都不执行
        </T>
        <rect x={225} y={736} width={330} height={74} rx={16} fill="#123137" stroke={C.teal} strokeWidth={2.5} />
        <T x={390} y={784} size={34} color={C.teal} anchor="middle" mono weight={750}>
          返回 0
        </T>
      </g>

      {/* Card 2: No rotten [[1,0,1]] -> -1 */}
      <g opacity={0.2 + 0.8 * clamp((p1 - 0.25) / 0.65)}>
        <rect x={695} y={272} width={530} height={585} rx={22} fill={C.surface} stroke={PAL.bad} strokeWidth={2.5} />
        <T x={730} y={326} size={28} color={PAL.bad} weight={700}>
          边界补例 · 没有烂橘子
        </T>
        <T x={730} y={366} size={22} color={C.muted} mono>
          grid = [[1, 0, 1]]
        </T>
        <MiniGrid grid={TRACE.noRotten.initialGrid} ox={785} oy={442} cell={110} />
        <T x={960} y={632} size={24} color={C.text} anchor="middle">
          初始 queue 为空，fresh = 2
        </T>
        <T x={960} y={672} size={22} color={C.muted} anchor="middle">
          循环不执行，末尾仍有新鲜橘子
        </T>
        <rect x={795} y={736} width={330} height={74} rx={16} fill="#331521" stroke={PAL.bad} strokeWidth={2.5} />
        <T x={960} y={784} size={34} color={PAL.bad} anchor="middle" mono weight={750}>
          返回 -1
        </T>
      </g>

      {/* Card 3: Official Ex 1 [[2,1,1],[1,1,0],[0,1,1]] -> 4 */}
      <g opacity={0.2 + 0.8 * p2}>
        <rect x={1265} y={272} width={530} height={585} rx={22} fill={C.surface} stroke={C.gold} strokeWidth={2.5} />
        <T x={1300} y={326} size={28} color={C.gold} weight={700}>
          官方示例 1 · 单个初始烂橘子
        </T>
        <T x={1300} y={366} size={20} color={C.muted} mono>
          [[2,1,1],[1,1,0],[0,1,1]]
        </T>
        <MiniGrid grid={ex1End.grid} rot={ex1End.rotTime} ox={1395} oy={396} cell={84} />
        <T x={1530} y={708} size={23} color={C.text} anchor="middle">
          0 / 1 / 多源共用同一循环
        </T>
        <rect x={1365} y={736} width={330} height={74} rx={16} fill="#362B14" stroke={C.gold} strokeWidth={2.5} />
        <T x={1530} y={784} size={34} color={C.gold} anchor="middle" mono weight={750}>
          返回 4
        </T>
      </g>
    </g>
  );
}

/* Shot 09: Executive Summary & Complexity before 5s CodeCard */
function CloseShot({shot, frame}: {shot: Shot; frame: number}) {
  const p1 = actionProgress(shot, frame, 'first', 0, 0.85);
  const p2 = actionProgress(shot, frame, 'second', 0, 0.75);
  const pillars = [
    ['1', '初始烂橘子全部入队', '同步站在第 0 分钟出发，避免单源错算与重复扫描', C.gold],
    ['2', '每轮锁定 len(queue)', '严格按层推进，一层恰好对应 1 分钟', C.teal],
    ['3', '入队瞬间改成 2', '两路相遇立即跳过，避免重复入队与重复扣减 fresh', PAL.skip],
    ['4', 'while queue and fresh > 0', 'fresh 清零立刻停下，绝不多算最后一层', PAL.freshGlow],
  ];

  return (
    <g>
      {pillars.map(([num, title, desc, col], j) => (
        <g key={num} opacity={0.25 + 0.75 * clamp((p1 * 4 - j * 0.65) / 1.1)}>
          <rect x={130} y={272 + j * 144} width={1040} height={122} rx={18} fill={C.surface} stroke={col} strokeWidth={2.5} />
          <circle cx={188} cy={333 + j * 144} r={26} fill="#101B2E" stroke={col} strokeWidth={2.5} />
          <T x={188} y={343 + j * 144} size={28} color={col} anchor="middle" mono weight={750}>
            {num}
          </T>
          <T x={236} y={319 + j * 144} size={30} color={col} weight={700}>
            {title}
          </T>
          <T x={236} y={362 + j * 144} size={23} color={C.text}>
            {desc}
          </T>
        </g>
      ))}

      {/* Right complexity & method cards */}
      <g opacity={0.2 + 0.8 * p2}>
        <rect x={1210} y={272} width={580} height={175} rx={22} fill="#123137" stroke={C.teal} strokeWidth={3} />
        <T x={1250} y={336} size={38} color={C.teal} weight={750}>
          多源广度优先搜索
        </T>
        <T x={1250} y={388} size={24} color={C.text}>
          Multi-Source BFS · 按层同步扩散
        </T>
        <FreshOrangeGlyph cx={1660} cy={365} r={28} />
        <RottenOrangeGlyph cx={1736} cy={365} r={28} />

        <rect x={1210} y={474} width={580} height={164} rx={22} fill={C.surface} stroke={C.gold} strokeWidth={2.5} />
        <T x={1250} y={534} size={24} color={C.muted}>时间复杂度</T>
        <T x={1250} y={592} size={46} color={C.gold} mono weight={750}>O(m · n)</T>
        <T x={1485} y={588} size={23} color={C.text}>每格最多进出队列一次</T>

        <rect x={1210} y={664} width={580} height={164} rx={22} fill={C.surface} stroke={C.edge} strokeWidth={2.5} />
        <T x={1250} y={724} size={24} color={C.muted}>额外空间复杂度</T>
        <T x={1250} y={782} size={46} color={C.teal} mono weight={750}>O(m · n)</T>
        <T x={1485} y={778} size={23} color={C.text}>状态副本与队列占用</T>
      </g>
    </g>
  );
}

const SLUG_MAP: Record<string, string> = {
  '01': 'input',
  '02': 'mapping',
  '03': 'why-together',
  '04': 'layer-queue',
  '05': 'min1-src1',
  '06': 'min1-src2',
  '07': 'min2-spread',
  '08': 'min2-collide',
  '09': 'min3-stop',
  '10': 'impossible',
  '11': 'edge',
  '12': 'close',
};

const TITLES: Record<string, string> = {
  input: '腐烂的橘子：全部烂完最少要几分钟？',
  mapping: '从数字网格到橘子箱：输入与返回值',
  'why-together': '为什么不能逐个烂橘子单独算？',
  'layer-queue': '队列按层推进：一层刚好等于一分钟',
  'min1-src1': '第 1 分钟：先出队 (0,0)，越界直接跳过',
  'min1-src2': '第 1 分钟：再出队 (2,2)，本层完成记 1 分钟',
  'min2-spread': '第 2 分钟：锁定层长 4，两路继续向外推进',
  'min2-collide': '第 2 分钟：两路波纹相遇，入队即改 2 去重',
  'min3-stop': '第 3 分钟收尾：队列非空为何立刻停止？',
  impossible: '重置示例：队列变空后仍有孤立橘子',
  edge: '三组边界：零源、单源与无新鲜橘子',
  close: '核心收束：多源入队、按层推进与防多算',
};

const TAG_LABELS: Record<number, string> = {
  10: '重置 · 官方示例 2',
  11: '三组关键边界',
  12: '总结与复杂度',
};

function Scene({shot, hideSubtitles}: {shot: Shot; hideSubtitles: boolean}) {
  const frame = useCurrentFrame();
  const n = Number(shot.id);
  if (shot.codeCardFrom !== undefined && frame >= shot.codeCardFrom) {
    return <CodeCard />;
  }
  const slug = SLUG_MAP[shot.id] ?? shot.id;
  const body =
    n === 1 ? (
      <InputShot shot={shot} frame={frame} />
    ) : n === 2 ? (
      <MappingShot shot={shot} frame={frame} />
    ) : n === 3 ? (
      <ContrastShot shot={shot} frame={frame} />
    ) : n === 4 ? (
      <QueueIntroShot shot={shot} frame={frame} />
    ) : n >= 5 && n <= 8 ? (
      <TraceBoardShot shot={shot} frame={frame} />
    ) : n === 9 ? (
      <TraceBoardShot shot={shot} frame={frame} showStopGuard />
    ) : n === 10 ? (
      <ImpossibleShot shot={shot} frame={frame} />
    ) : n === 11 ? (
      <EdgeShot shot={shot} frame={frame} />
    ) : (
      <CloseShot shot={shot} frame={frame} />
    );

  return (
    <AbsoluteFill style={{background: C.bg}}>
      <LeetcodeBackdrop />
      <LeetcodeHeader
        slug="rotting-oranges"
        identity={{number: 994, method: '广度优先搜索'}}
        detail={shot.chapterTitle}
      />
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
        <T x={125} y={214} size={40} weight={700}>
          {TITLES[slug] ?? shot.id}
        </T>
        <T x={1795} y={212} size={22} color={C.gold} anchor="end" weight={600}>
          {TAG_LABELS[n] ?? '3×4 双源教学示例'}
        </T>
        {body}
        {!hideSubtitles &&
          (shot.subtitles ?? []).map((s, i) => {
            const to = s.to ?? s.from + (s.duration ?? 90);
            if (frame < s.from || frame > to) return null;
            const lines = splitSubtitle(s.text);
            const top = 1022 - lines.length * 38;
            return (
              <g data-subtitle="true" key={i}>
                <rect x={140} y={top - 30} width={1640} height={lines.length * 38 + 22} rx={12} fill="#0B1220" stroke="#1E293B" strokeWidth={1.5} />
                {lines.map((l, j) => (
                  <T key={j} x={960} y={top + j * 38} size={26} anchor="middle">
                    {l}
                  </T>
                ))}
              </g>
            );
          })}
      </svg>
    </AbsoluteFill>
  );
}

export function Main({hideSubtitles = false}: {hideSubtitles?: boolean}) {
  return (
    <AbsoluteFill>
      {shots.map((s) => (
        <Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}>
          <Scene shot={s} hideSubtitles={hideSubtitles} />
        </Sequence>
      ))}
      {__HAS_VOICE_AUDIO__ && !STORYBOARD.meta.pendingAudio && <Audio src={staticFile('audio/voice.wav')} />}
    </AbsoluteFill>
  );
}
