import React from 'react';
import {C, FONT, MONO} from '../../../../../_shared/leetcode-video/theme';
import type {NeighborCheck} from './data';
import {clamp, easeOutCubic} from './timeline';

export const PAL = {
  freshOuter: '#EA580C',
  freshMain: '#FB923C',
  freshGlow: '#FDBA74',
  leaf: '#34D399',
  leafDark: '#059669',
  rottenOuter: '#4C1D3D',
  rottenMain: '#7E3454',
  rottenSpot: '#3B1429',
  rottenLeaf: '#94A3B8',
  slotBg: '#101B2E',
  slotBorder: '#2A3D58',
  bad: '#FB7185',
  skip: '#A5B4FC',
  mutedDark: '#64748B',
};

export const T = ({
  x,
  y,
  children,
  size = 28,
  color = C.text,
  anchor = 'start',
  mono = false,
  weight = 500,
  ...rest
}: any) => (
  <text
    x={x}
    y={y}
    fill={color}
    fontFamily={mono ? MONO : FONT}
    fontSize={size}
    fontWeight={weight}
    textAnchor={anchor}
    {...rest}
  >
    {children}
  </text>
);

export function FreshOrangeGlyph({cx, cy, r, opacity = 1}: {cx: number; cy: number; r: number; opacity?: number}) {
  return (
    <g opacity={opacity}>
      <ellipse cx={cx} cy={cy + r * 0.92} rx={r * 0.72} ry={r * 0.16} fill="#070D19" opacity={0.55} />
      <circle cx={cx} cy={cy} r={r} fill={PAL.freshOuter} />
      <circle cx={cx - r * 0.04} cy={cy - r * 0.04} r={r * 0.9} fill={PAL.freshMain} />
      <ellipse
        cx={cx - r * 0.32}
        cy={cy - r * 0.34}
        rx={r * 0.28}
        ry={r * 0.16}
        transform={`rotate(-28 ${cx - r * 0.32} ${cy - r * 0.34})`}
        fill={PAL.freshGlow}
        opacity={0.75}
      />
      <path
        d={`M ${cx} ${cy - r * 0.85} Q ${cx + r * 0.06} ${cy - r * 1.15} ${cx + r * 0.16} ${cy - r * 1.18}`}
        fill="none"
        stroke="#854D0E"
        strokeWidth={Math.max(2.5, r * 0.1)}
        strokeLinecap="round"
      />
      <path
        d={`M ${cx + r * 0.06} ${cy - r * 0.98} Q ${cx + r * 0.56} ${cy - r * 1.24} ${cx + r * 0.62} ${cy - r * 0.82} Q ${cx + r * 0.32} ${cy - r * 0.72} ${cx + r * 0.06} ${cy - r * 0.98} Z`}
        fill={PAL.leaf}
        stroke={PAL.leafDark}
        strokeWidth={1.2}
      />
    </g>
  );
}

export function RottenOrangeGlyph({cx, cy, r, opacity = 1}: {cx: number; cy: number; r: number; opacity?: number}) {
  return (
    <g opacity={opacity}>
      <ellipse cx={cx} cy={cy + r * 0.92} rx={r * 0.72} ry={r * 0.16} fill="#070D19" opacity={0.55} />
      <circle cx={cx} cy={cy} r={r} fill={PAL.rottenOuter} stroke="#BE4B72" strokeWidth={2.2} />
      <circle cx={cx - r * 0.04} cy={cy - r * 0.04} r={r * 0.86} fill={PAL.rottenMain} />
      <circle cx={cx - r * 0.32} cy={cy - r * 0.18} r={r * 0.22} fill={PAL.rottenSpot} opacity={0.8} />
      <circle cx={cx + r * 0.28} cy={cy + r * 0.24} r={r * 0.18} fill={PAL.rottenSpot} opacity={0.85} />
      <circle cx={cx + r * 0.18} cy={cy - r * 0.34} r={r * 0.12} fill={PAL.rottenSpot} opacity={0.75} />
      <path
        d={`M ${cx - r * 0.04} ${cy - r * 0.86} Q ${cx + r * 0.08} ${cy - r * 1.12} ${cx + r * 0.22} ${cy - r * 1.05}`}
        fill="none"
        stroke={PAL.rottenLeaf}
        strokeWidth={Math.max(2.2, r * 0.09)}
        strokeLinecap="round"
      />
      <path
        d={`M ${cx + r * 0.06} ${cy - r * 0.95} Q ${cx + r * 0.42} ${cy - r * 0.98} ${cx + r * 0.48} ${cy - r * 0.7} Q ${cx + r * 0.22} ${cy - r * 0.72} ${cx + r * 0.06} ${cy - r * 0.95} Z`}
        fill="#64748B"
      />
    </g>
  );
}

export type CrateCellProps = {
  key?: React.Key;
  x: number;
  y: number;
  size: number;
  r: number;
  c: number;
  val: number;
  rotMinute?: number | null;
  isSource?: boolean;
  justInfected?: boolean;
  infectProgress?: number;
  highlightBad?: boolean;
  highlightTeal?: boolean;
  showCoords?: boolean;
  showValueTag?: boolean;
  customBadge?: {text: string; color: string; bg?: string};
  orangeOpacity?: number;
};

export function CrateCell({
  x,
  y,
  size,
  r,
  c,
  val,
  rotMinute,
  isSource = false,
  justInfected = false,
  infectProgress = 1,
  highlightBad = false,
  highlightTeal = false,
  showCoords = true,
  showValueTag = false,
  customBadge,
  orangeOpacity = 1,
}: CrateCellProps) {
  const cx = x + size / 2;
  const cy = y + size / 2 + 4;
  const glyphR = size * 0.29;
  const morph = justInfected ? easeOutCubic(clamp((infectProgress - 0.35) / 0.55)) : val === 2 ? 1 : 0;
  const ringR = justInfected ? glyphR + size * 0.24 * easeOutCubic(infectProgress) : 0;
  const ringOpacity = justInfected ? Math.max(0, 1 - infectProgress) * 0.85 : 0;

  const stroke = isSource
    ? C.gold
    : highlightBad
      ? PAL.bad
      : justInfected && morph > 0.3
        ? C.teal
        : highlightTeal
          ? C.teal
          : val === 0
            ? '#24344D'
            : PAL.slotBorder;
  const strokeW = isSource || highlightBad || (justInfected && morph > 0.2) || highlightTeal ? 4 : 2;
  const fill = isSource
    ? '#25261F'
    : highlightBad
      ? '#2F1722'
      : val === 0
        ? '#0B1323'
        : PAL.slotBg;

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={size}
        height={size}
        rx={18}
        fill={fill}
        stroke={stroke}
        strokeWidth={strokeW}
        strokeDasharray={val === 0 && !highlightBad ? '8 6' : undefined}
      />
      {showCoords && (
        <T x={x + 11} y={y + 23} size={16} color={isSource ? C.gold : '#7F93AE'} mono>
          ({r},{c})
        </T>
      )}
      {val === 0 && (
        <g opacity={0.7}>
          <T x={cx} y={size < 95 ? cy + 8 : cy + 4} size={Math.max(22, size * 0.24)} color="#475569" anchor="middle" mono weight={700}>
            0
          </T>
          {size >= 95 && (
            <T x={cx} y={y + size - 24} size={15} color="#64748B" anchor="middle">
              空位
            </T>
          )}
        </g>
      )}
      {val === 1 && <FreshOrangeGlyph cx={cx} cy={cy} r={glyphR} opacity={orangeOpacity} />}
      {val === 2 && (
        <g opacity={orangeOpacity}>
          {justInfected && morph < 1 && <FreshOrangeGlyph cx={cx} cy={cy} r={glyphR} opacity={1 - morph} />}
          <RottenOrangeGlyph cx={cx} cy={cy} r={glyphR} opacity={justInfected ? morph : 1} />
          {ringOpacity > 0.02 && (
            <circle cx={cx} cy={cy} r={ringR} fill="none" stroke={C.teal} strokeWidth={4} opacity={ringOpacity} />
          )}
        </g>
      )}
      {showValueTag && val > 0 && (
        <g>
          <rect x={x + size - 36} y={y + 8} width={28} height={24} rx={7} fill="#0F172A" stroke={val === 2 ? '#BE4B72' : PAL.freshMain} strokeWidth={1.5} />
          <T x={x + size - 22} y={y + 26} size={16} color={val === 2 ? '#FDA4AF' : PAL.freshGlow} anchor="middle" mono weight={700}>
            {val}
          </T>
        </g>
      )}
      {val === 2 && rotMinute !== null && rotMinute !== undefined && (!justInfected || morph > 0.55) && !customBadge && (
        <g>
          <rect
            x={x + size - 58}
            y={y + size - 32}
            width={50}
            height={24}
            rx={8}
            fill={rotMinute === 0 ? '#3A2D15' : '#133238'}
            stroke={rotMinute === 0 ? C.gold : C.teal}
            strokeWidth={1.5}
          />
          <T
            x={x + size - 33}
            y={y + size - 15}
            size={15}
            color={rotMinute === 0 ? C.gold : C.teal}
            anchor="middle"
            mono
            weight={700}
          >
            T={rotMinute}
          </T>
        </g>
      )}
      {customBadge && (() => {
        const bw = Math.max(60, customBadge.text.length * 14 + 14);
        return (
          <g>
            <rect
              x={x + size - bw - 8}
              y={y + size - 33}
              width={bw}
              height={25}
              rx={8}
              fill={customBadge.bg ?? '#1E293B'}
              stroke={customBadge.color}
              strokeWidth={1.8}
            />
            <T x={x + size - bw / 2 - 8} y={y + size - 15} size={15} color={customBadge.color} anchor="middle" mono weight={700}>
              {customBadge.text}
            </T>
          </g>
        );
      })()}
    </g>
  );
}

export function SpreadOverlay({
  ox,
  oy,
  cellSize,
  gap,
  rows,
  cols,
  source,
  checks,
  progress,
}: {
  ox: number;
  oy: number;
  cellSize: number;
  gap: number;
  rows: number;
  cols: number;
  source: [number, number];
  checks: NeighborCheck[];
  progress: number;
}) {
  const step = cellSize + gap;
  const [sr, sc] = source;
  const sx = ox + sc * step + cellSize / 2;
  const sy = oy + sr * step + cellSize / 2;
  const p = easeOutCubic(clamp(progress / 0.72));

  return (
    <g>
      {checks.map((ch, i) => {
        const [tr, tc] = ch.to;
        const dr = tr - sr;
        const dc = tc - sc;

        if (ch.outcome === 'rot') {
          const x1 = sx + dc * (cellSize * 0.34);
          const y1 = sy + dr * (cellSize * 0.34);
          const tx = ox + tc * step + cellSize / 2 - dc * (cellSize * 0.34);
          const ty = oy + tr * step + cellSize / 2 - dr * (cellSize * 0.34);
          const ex = x1 + (tx - x1) * p;
          const ey = y1 + (ty - y1) * p;
          const ang = Math.atan2(ty - y1, tx - x1);
          const bx = ex - 14 * Math.cos(ang);
          const by = ey - 14 * Math.sin(ang);
          return (
            <g key={i}>
              <line x1={x1} y1={y1} x2={ex} y2={ey} stroke={C.teal} strokeWidth={6} strokeLinecap="round" />
              {p > 0.15 && (
                <path
                  d={`M ${bx + 8 * Math.sin(ang)} ${by - 8 * Math.cos(ang)} L ${ex} ${ey} L ${bx - 8 * Math.sin(ang)} ${by + 8 * Math.cos(ang)}`}
                  fill="none"
                  stroke={C.teal}
                  strokeWidth={5}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              )}
            </g>
          );
        }

        if (ch.outcome === 'oob') {
          const edgeX = sx + dc * (cellSize * 0.5 + 8);
          const edgeY = sy + dr * (cellSize * 0.5 + 8);
          const x1 = sx + dc * (cellSize * 0.28);
          const y1 = sy + dr * (cellSize * 0.28);
          const ex = x1 + (edgeX - x1) * p;
          const ey = y1 + (edgeY - y1) * p;
          const perpX = -dr * 18;
          const perpY = dc * 18;
          const labelX = edgeX + dc * 48;
          const labelY = edgeY + dr * 22 + (dr === 0 ? 5 : dr < 0 ? -4 : 18);
          return (
            <g key={i} opacity={0.92}>
              <line x1={x1} y1={y1} x2={ex} y2={ey} stroke={PAL.bad} strokeWidth={4} strokeDasharray="6 5" />
              {p > 0.6 && (
                <>
                  <line
                    x1={edgeX - perpX}
                    y1={edgeY - perpY}
                    x2={edgeX + perpX}
                    y2={edgeY + perpY}
                    stroke={PAL.bad}
                    strokeWidth={4.5}
                    strokeLinecap="round"
                  />
                  <T x={labelX} y={labelY} size={17} color={PAL.bad} anchor="middle" weight={600}>
                    越界跳过
                  </T>
                </>
              )}
            </g>
          );
        }

        if (ch.outcome === 'empty') {
          const x1 = sx + dc * (cellSize * 0.34);
          const y1 = sy + dr * (cellSize * 0.34);
          const tx = ox + tc * step + cellSize / 2 - dc * (cellSize * 0.5 + 2);
          const ty = oy + tr * step + cellSize / 2 - dr * (cellSize * 0.5 + 2);
          const ex = x1 + (tx - x1) * p;
          const ey = y1 + (ty - y1) * p;
          return (
            <g key={i} opacity={0.85}>
              <line x1={x1} y1={y1} x2={ex} y2={ey} stroke="#94A3B8" strokeWidth={3.5} strokeDasharray="6 5" />
              {p > 0.65 && (
                <g transform={`translate(${tx}, ${ty})`}>
                  <circle r={11} fill="#1E293B" stroke="#94A3B8" strokeWidth={2} />
                  <path d="M -4.5 -4.5 L 4.5 4.5 M 4.5 -4.5 L -4.5 4.5" stroke="#94A3B8" strokeWidth={2.3} strokeLinecap="round" />
                </g>
              )}
            </g>
          );
        }

        // already_rotten: emphasize collision skip cleanly when target rotted in same or earlier minute
        const x1 = sx + dc * (cellSize * 0.34);
        const y1 = sy + dr * (cellSize * 0.34);
        const tx = ox + tc * step + cellSize / 2 - dc * (cellSize * 0.38);
        const ty = oy + tr * step + cellSize / 2 - dr * (cellSize * 0.38);
        const ex = x1 + (tx - x1) * p;
        const ey = y1 + (ty - y1) * p;
        const isSameMinuteCollision = ch.existingMinute !== null && ch.existingMinute !== undefined && ch.existingMinute >= 2;
        return (
          <g key={i} opacity={isSameMinuteCollision ? 0.95 : 0.42}>
            <line
              x1={x1}
              y1={y1}
              x2={ex}
              y2={ey}
              stroke={PAL.skip}
              strokeWidth={isSameMinuteCollision ? 4.5 : 2.5}
              strokeDasharray="7 6"
            />
            {isSameMinuteCollision && p > 0.65 && (
              <g transform={`translate(${(x1 + tx) / 2}, ${(y1 + ty) / 2})`}>
                <rect x={-52} y={-15} width={104} height={28} rx={9} fill="#1E1B4B" stroke={PAL.skip} strokeWidth={2} />
                <T x={0} y={5} size={16} color={PAL.skip} anchor="middle" weight={600}>
                  已为 2 跳过
                </T>
              </g>
            )}
          </g>
        );
      })}
    </g>
  );
}

export function LayerQueueBar({
  queue,
  remainingInLayer,
  activeSource,
  fresh,
  minutes,
  highlightStop = false,
  blocked = false,
}: {
  queue: [number, number][];
  remainingInLayer?: number;
  activeSource?: [number, number] | null;
  fresh: number;
  minutes: number;
  highlightStop?: boolean;
  blocked?: boolean;
}) {
  const curCount = remainingInLayer !== undefined ? Math.min(remainingInLayer, queue.length) : queue.length;
  const barBorder = highlightStop ? C.gold : blocked ? PAL.bad : C.edge;
  return (
    <g>
      <rect x={120} y={782} width={1680} height={114} rx={18} fill={C.surface} stroke={barBorder} strokeWidth={highlightStop || blocked ? 3.5 : 2} />
      <T x={148} y={824} size={22} color={highlightStop ? C.gold : blocked ? PAL.bad : C.muted} weight={600}>
        先进先出队列
      </T>
      <T x={148} y={864} size={18} color="#7F93AE">
        队头出 · 队尾进
      </T>

      {activeSource && (
        <g>
          <rect x={312} y={798} width={132} height={82} rx={14} fill="#362B14" stroke={C.gold} strokeWidth={3} />
          <T x={378} y={824} size={16} color={C.gold} anchor="middle" weight={600}>
            当前出队
          </T>
          <T x={378} y={861} size={26} color={C.gold} anchor="middle" mono weight={700}>
            ({activeSource[0]},{activeSource[1]})
          </T>
        </g>
      )}

      {/* Queue items */}
      {(() => {
        const startX = activeSource ? 468 : 316;
        const itemW = 92;
        const itemGap = 12;
        if (queue.length === 0) {
          return (
            <g>
              <rect x={startX} y={806} width={220} height={66} rx={12} fill="#101B2E" stroke={blocked ? PAL.bad : '#334155'} strokeWidth={2} strokeDasharray="6 5" />
              <T x={startX + 110} y={848} size={24} color={blocked ? PAL.bad : C.muted} anchor="middle" weight={600}>
                队列已空
              </T>
            </g>
          );
        }
        return (
          <g>
            {curCount > 0 && remainingInLayer !== undefined && (
              <g>
                <rect
                  x={startX - 8}
                  y={794}
                  width={curCount * (itemW + itemGap) - itemGap + 16}
                  height={90}
                  rx={14}
                  fill="rgba(255,204,112,0.06)"
                  stroke={C.gold}
                  strokeWidth={2}
                  strokeDasharray="6 4"
                />
                <T x={startX + (curCount * (itemW + itemGap) - itemGap) / 2} y={814} size={15} color={C.gold} anchor="middle" weight={600}>
                  {curCount === 1 ? '本层(1)' : `本层待处理 (${curCount})`}
                </T>
              </g>
            )}
            {queue.length > curCount && remainingInLayer !== undefined && (
              <g>
                <rect
                  x={startX + curCount * (itemW + itemGap) - 4}
                  y={794}
                  width={(queue.length - curCount) * (itemW + itemGap) - itemGap + 16}
                  height={90}
                  rx={14}
                  fill="rgba(86,228,211,0.07)"
                  stroke={C.teal}
                  strokeWidth={2}
                />
                <T
                  x={startX + curCount * (itemW + itemGap) + ((queue.length - curCount) * (itemW + itemGap) - itemGap) / 2 + 4}
                  y={814}
                  size={15}
                  color={C.teal}
                  anchor="middle"
                  weight={600}
                >
                  下一层 ({queue.length - curCount})
                </T>
              </g>
            )}
            {queue.slice(0, 7).map(([qr, qc], j) => {
              const isCur = remainingInLayer === undefined || j < curCount;
              const ix = startX + j * (itemW + itemGap) + (remainingInLayer !== undefined && !isCur ? 4 : 0);
              const iy = remainingInLayer !== undefined ? 824 : 813;
              const ih = remainingInLayer !== undefined ? 50 : 54;
              const col = highlightStop ? C.gold : isCur ? C.gold : C.teal;
              return (
                <g key={`${qr}-${qc}-${j}`}>
                  <rect x={ix} y={iy} width={itemW} height={ih} rx={11} fill="#101B2E" stroke={col} strokeWidth={2.5} />
                  <T x={ix + itemW / 2} y={iy + ih / 2 + 9} size={24} color={col} anchor="middle" mono weight={700}>
                    ({qr},{qc})
                  </T>
                </g>
              );
            })}
          </g>
        );
      })()}

      {/* Right-side live telemetry cards */}
      <g>
        <rect x={1358} y={798} width={196} height={82} rx={14} fill="#101B2E" stroke={fresh === 0 ? C.teal : PAL.freshMain} strokeWidth={2.5} />
        <T x={1456} y={825} size={17} color={C.muted} anchor="middle">
          新鲜橘子 fresh
        </T>
        <T x={1456} y={865} size={34} color={fresh === 0 ? C.teal : PAL.freshGlow} anchor="middle" mono weight={700}>
          {fresh}
        </T>
      </g>
      <g>
        <rect x={1574} y={798} width={196} height={82} rx={14} fill="#101B2E" stroke={C.gold} strokeWidth={2.5} />
        <T x={1672} y={825} size={17} color={C.muted} anchor="middle">
          累计分钟 minutes
        </T>
        <T x={1672} y={865} size={34} color={C.gold} anchor="middle" mono weight={700}>
          {minutes}
        </T>
      </g>
    </g>
  );
}
