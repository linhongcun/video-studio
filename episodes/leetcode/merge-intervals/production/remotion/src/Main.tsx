import React, {type ReactNode} from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {LeetcodeBackdrop, LeetcodeHeader} from '../../../../../_shared/leetcode-video/Frame';
import {C, FONT} from '../../../../../_shared/leetcode-video/theme';
import {CodeCard} from './CodeCard';
import {EVENTS, Interval, Shot, STORYBOARD, TRACE, TraceEvent, traceEventsFor, shots} from './data';
import {actionProgress, clamp, ease} from './timeline';

declare const __HAS_VOICE_AUDIO__: boolean;

const COLORS = ['#7DB5FF', '#56E4D3', '#BEADFF', '#F6A5C9', '#FFCC70', '#95D69B'];
const CARD_X = 130;
const CARD_Y = 300;
const CARD_WIDTH = 250;
const CARD_GAP = 288;
const AXIS_TOP = 405;
const AXIS_BOTTOM = 800;
const SUBTITLE_TOP = 962;
const x = (value: number) => 260 + (value / 15) * 1420;
const titles: Record<string, string> = {
  input: '输入映射到数轴',
  'touching-rule': '端点规则：两端都包含',
  order: '乱序输入，按起点排序',
  begin: '从起点最早的一段开始',
  nested: '嵌套不缩短终点',
  overlap: '重叠时扩展当前终点',
  touching: '端点相接仍然合并',
  separate: '出现空隙，输出当前段',
  'separate-finish': '再次分离，然后结束扫描',
  close: '两条规则与最终结果',
};

type SvgTextProps = {
  x: number;
  y: number;
  children: ReactNode;
  size?: number;
  color?: string;
  anchor?: 'start' | 'middle' | 'end';
  weight?: number;
};

function SvgText({
  x: textX,
  y,
  children,
  size = 26,
  color = C.text,
  anchor = 'start',
  weight,
}: SvgTextProps) {
  return (
    <text
      x={textX}
      y={y}
      fill={color}
      fontFamily={FONT}
      fontSize={size}
      fontWeight={weight}
      textAnchor={anchor}
    >
      {children}
    </text>
  );
}

function NumberAxis() {
  return (
    <g>
      {Array.from({length: 16}, (_, value) => (
        <g key={value}>
          <line x1={x(value)} y1={AXIS_TOP} x2={x(value)} y2={AXIS_BOTTOM} stroke={C.edge} />
          <SvgText x={x(value)} y={835} size={22} color={C.muted} anchor="middle">
            {value}
          </SvgText>
        </g>
      ))}
    </g>
  );
}

type SegmentProps = {
  interval: Interval;
  y: number;
  color: string;
  label: string;
  geometry?: readonly [number, number];
  opacity?: number;
  emphasizeStart?: boolean;
  emphasizeEnd?: boolean;
};

function Segment({
  interval,
  y: lineY,
  color,
  label,
  geometry = interval,
  opacity = 1,
  emphasizeStart = false,
  emphasizeEnd = false,
}: SegmentProps) {
  const [start, end] = geometry;
  return (
    <g opacity={opacity}>
      <line
        x1={x(start)}
        y1={lineY}
        x2={x(end)}
        y2={lineY}
        stroke={color}
        strokeWidth={12}
        strokeLinecap="round"
      />
      <circle cx={x(start)} cy={lineY} r={8} fill={color} />
      <circle cx={x(end)} cy={lineY} r={8} fill={color} />
      {emphasizeStart && (
        <circle cx={x(start)} cy={lineY} r={17} fill="none" stroke={C.gold} strokeWidth={3} />
      )}
      {emphasizeEnd && (
        <circle cx={x(end)} cy={lineY} r={17} fill="none" stroke={C.gold} strokeWidth={3} />
      )}
      <SvgText x={x(start)} y={lineY - 18} size={24} color={color}>
        {label} [{interval[0]},{interval[1]}]
      </SvgText>
    </g>
  );
}

function adjacentSwaps(order: number[]): [number, number][] {
  const slots = order.map((_, index) => index);
  const swaps: [number, number][] = [];
  for (let target = 0; target < order.length; target++) {
    for (let current = slots.indexOf(order[target]); current > target; current--) {
      swaps.push([current - 1, current]);
      [slots[current - 1], slots[current]] = [slots[current], slots[current - 1]];
    }
  }
  return swaps;
}

type IntervalCardsProps = {
  visibleIds?: number[];
  order?: number[];
  moveProgress?: number;
  revealProgress?: number;
};

function IntervalCards({
  visibleIds,
  order,
  moveProgress = 0,
  revealProgress = 1,
}: IntervalCardsProps) {
  const sortedOrder = order ?? EVENTS.find((event) => event.kind === 'begin')?.order ?? [0, 1, 2, 3, 4, 5];
  const swaps = adjacentSwaps(sortedOrder);
  const progress = clamp(moveProgress);
  const activeStep = progress * swaps.length;
  const completedSteps = Math.min(swaps.length, Math.floor(activeStep));
  const stepProgress = activeStep - completedSteps;
  const slots = TRACE.input.map((_, index) => index);

  for (let index = 0; index < completedSteps; index++) {
    const [left, right] = swaps[index];
    [slots[left], slots[right]] = [slots[right], slots[left]];
  }

  return (
    <g>
      {TRACE.input.map((interval, id) => {
        if (visibleIds && !visibleIds.includes(id)) return null;
        const slot = slots.indexOf(id);
        let cardX = CARD_X + slot * CARD_GAP;
        let cardY = CARD_Y;
        if (completedSteps < swaps.length) {
          const [left, right] = swaps[completedSteps];
          if (slot === left || slot === right) {
            const destination = slot === left ? right : left;
            cardX = CARD_X + (slot + (destination - slot) * stepProgress) * CARD_GAP;
            cardY += (slot === left ? -1 : 1) * Math.sin(Math.PI * stepProgress) * 58;
          }
        }
        const opacity = id === 0 || !visibleIds ? 1 : revealProgress;
        return (
          <g key={id} data-source-id={id} opacity={opacity}>
            <rect
              x={cardX}
              y={cardY}
              width={CARD_WIDTH}
              height={52}
              rx={10}
              fill={C.surface}
              stroke={COLORS[id]}
              strokeWidth={2}
            />
            <SvgText x={cardX + CARD_WIDTH / 2} y={cardY + 34} size={24} color={COLORS[id]} anchor="middle">
              I{id} [{interval[0]},{interval[1]}]
            </SvgText>
          </g>
        );
      })}
    </g>
  );
}

function IntroScene({shot, frame}: {shot: Shot; frame: number}) {
  const mapProgress = actionProgress(shot, frame, 'map');
  const revealProgress = actionProgress(shot, frame, 'reveal');
  const sourceY = 390;
  const axisY = 500;
  const sourceStart = 208;
  const sourceEnd = 322;
  const startX = sourceStart + (x(8) - sourceStart) * mapProgress;
  const endX = sourceEnd + (x(10) - sourceEnd) * mapProgress;
  const lineY = sourceY + (axisY - sourceY) * mapProgress;
  const revealedIds = revealProgress > 0 ? [0, 1, 2, 3, 4, 5] : [0];
  return (
    <>
      <NumberAxis />
      <IntervalCards visibleIds={revealedIds} revealProgress={revealProgress} />
      <SvgText x={CARD_X + 125} y={CARD_Y + 78} size={18} color={C.gold} anchor="middle">
        nums[0]
      </SvgText>
      <line x1={startX} y1={lineY} x2={endX} y2={lineY} stroke={COLORS[0]} strokeWidth={12} strokeLinecap="round" />
      <circle cx={startX} cy={lineY} r={8} fill={COLORS[0]} />
      <circle cx={endX} cy={lineY} r={8} fill={COLORS[0]} />
      <SvgText x={startX} y={lineY - 18} size={24} color={COLORS[0]} anchor="middle">8</SvgText>
      <SvgText x={endX} y={lineY - 18} size={24} color={COLORS[0]} anchor="middle">10</SvgText>
      {revealProgress > 0 && TRACE.input.slice(1).map((interval, index) => (
        <g key={index + 1}>
          <Segment
            interval={interval}
            y={555 + index * 48}
            color={COLORS[index + 1]}
            label={`I${index + 1}`}
          />
        </g>
      ))}
      <SvgText x={130} y={900} size={26} color={C.gold}>
        合并所有重叠区间，同时保持覆盖范围不变
      </SvgText>
    </>
  );
}

function TouchingRuleScene({shot, frame}: {shot: Shot; frame: number}) {
  const mergeProgress = actionProgress(shot, frame, 'merge');
  const first = TRACE.input[3];
  const second = TRACE.input[4];
  const targetEnd = first[1] + (second[1] - first[1]) * mergeProgress;
  const shownEnd = mergeProgress < 0.5 ? first[1] : second[1];
  return (
    <>
      <NumberAxis />
      <IntervalCards />
      <line
        x1={x(5)}
        y1={526}
        x2={x(5)}
        y2={704}
        stroke={C.gold}
        strokeWidth={3}
        strokeDasharray="8 8"
      />
      <Segment
        interval={[first[0], shownEnd]}
        geometry={[first[0], targetEnd]}
        y={560}
        color={COLORS[3]}
        label="I3"
        emphasizeEnd
      />
      <Segment
        interval={second}
        y={675}
        color={COLORS[4]}
        label="I4"
        opacity={1 - mergeProgress}
        emphasizeStart
      />
      <SvgText x={x(5)} y={515} size={22} color={C.gold} anchor="middle">5</SvgText>
    </>
  );
}

function OrderScene({shot, frame}: {shot: Shot; frame: number}) {
  const moveProgress = actionProgress(shot, frame, 'sort');
  return (
    <>
      <NumberAxis />
      <IntervalCards moveProgress={moveProgress} />
      {TRACE.input.map((interval, id) => (
        <g key={id}>
          <Segment
            interval={interval}
            y={470 + id * 55}
            color={COLORS[id]}
            label={`I${id}`}
          />
        </g>
      ))}
    </>
  );
}

function previousEvent(event: TraceEvent): TraceEvent | undefined {
  const index = EVENTS.indexOf(event);
  return index > 0 ? EVENTS[index - 1] : undefined;
}

function CompletedSegments({intervals}: {intervals: Interval[]}) {
  return (
    <>
      {intervals.map((interval, index) => (
        <g key={index}>
          <Segment
            interval={interval}
            y={455 + index * 62}
            color={C.teal}
            label="输出"
          />
        </g>
      ))}
    </>
  );
}

type BoardState = {
  completed: Interval[];
  current?: Interval;
  incoming?: Interval;
  currentGeometry?: readonly [number, number];
  currentY?: number;
  incomingY?: number;
  showCurrent?: boolean;
  showIncoming?: boolean;
  currentLabel?: Interval;
};

function Board({shot, frame}: {shot: Shot; frame: number}) {
  const events = traceEventsFor(shot);
  const primary = events[0];
  if (!primary) return null;

  let state: BoardState = {
    completed: previousEvent(primary)?.completed ?? [],
    current: primary.kind === 'begin' ? primary.current ?? undefined : primary.before,
    incoming: primary.incoming,
    currentY: 675,
    incomingY: 765,
    showCurrent: true,
    showIncoming: Boolean(primary.incoming),
  };

  if (primary.kind === 'begin') {
    state.showCurrent = actionProgress(shot, frame, 'begin') > 0;
    state.completed = primary.completed ?? [];
  } else if (primary.kind === 'merge') {
    const progress = actionProgress(shot, frame, 'merge');
    const before = primary.before;
    const after = primary.current;
    if (before && after) {
      state.currentGeometry = [
        before[0] + (after[0] - before[0]) * progress,
        before[1] + (after[1] - before[1]) * progress,
      ];
      state.currentLabel = progress < 0.5 ? before : after;
      state.current = state.currentLabel;
    }
    state.showIncoming = progress < 0.98;
    state.completed = previousEvent(primary)?.completed ?? [];
  } else if (primary.kind === 'separate') {
    const separateEnd = shot.visualType === 'separate-finish' ? 0.4 : 0.92;
    const progress = actionProgress(shot, frame, 'separate', 0, separateEnd);
    const previousCompleted = previousEvent(primary)?.completed ?? [];
    state.completed = progress >= 0.98 ? primary.completed ?? [] : previousCompleted;
    state.current = progress >= 0.98 ? primary.current ?? undefined : primary.before;
    state.incoming = primary.incoming;
    state.currentY = progress >= 0.98 ? 675 : 675 + (455 + previousCompleted.length * 62 - 675) * progress;
    state.incomingY = progress >= 0.98 ? 765 : 765 - 90 * progress;
    state.showCurrent = true;
    state.showIncoming = progress < 0.98;
    if (shot.visualType === 'separate-finish' && events[1]) {
      const finishProgress = actionProgress(shot, frame, 'finish', 0.52, 0.95);
      const finish = events[1];
      if (finishProgress >= 0.98) {
        state.completed = finish.completed ?? [];
        state.showCurrent = false;
        state.showIncoming = false;
      }
    }
  } else if (primary.kind === 'finish') {
    const progress = actionProgress(shot, frame, 'finish');
    const previous = previousEvent(primary);
    const previousCurrent = previous?.current ?? undefined;
    const previousCompleted = previous?.completed ?? [];
    state.completed = progress >= 0.98 ? primary.completed ?? [] : previousCompleted;
    state.current = previousCurrent;
    state.currentY = progress >= 0.98
      ? 675
      : 675 + (455 + previousCompleted.length * 62 - 675) * progress;
    state.showCurrent = progress < 0.98 && Boolean(previousCurrent);
  }

  return (
    <g>
      <NumberAxis />
      {primary.kind === 'begin' && primary.order && (
        <IntervalCards order={primary.order} moveProgress={1} />
      )}
      <SvgText x={120} y={455} size={22} color={C.teal}>已完成</SvgText>
      <SvgText x={120} y={675} size={22} color={C.gold}>当前段</SvgText>
      <SvgText x={120} y={765} size={22} color={C.muted}>下一段</SvgText>
      <CompletedSegments intervals={state.completed} />
      {state.showCurrent && state.current && (
        <Segment
          interval={state.currentLabel ?? state.current}
          geometry={state.currentGeometry}
          y={state.currentY ?? 675}
          color={C.gold}
          label="当前"
        />
      )}
      {state.showIncoming && state.incoming && (
        <Segment
          interval={state.incoming}
          y={state.incomingY ?? 765}
          color={COLORS[primary.id ?? 0]}
          label="下一段"
        />
      )}
    </g>
  );
}

type SceneProps = {shot: Shot; hideSubtitles: boolean};

function Scene({shot, hideSubtitles}: SceneProps) {
  const frame = useCurrentFrame();
  const code = shot.codeCardFrom !== undefined && frame >= shot.codeCardFrom;
  const visibleCues = shot.elements?.filter((element) => element.appearFrame <= frame) ?? [];
  const activeActions = (shot.actionCues ?? []).filter((action) => {
    const cueFrame = shot.cueFrames?.labels?.[action.cue];
    return cueFrame !== undefined && frame >= cueFrame;
  });
  const activeAction = activeActions.length ? activeActions[activeActions.length - 1] : undefined;
  const cueText = activeAction?.cue ?? (visibleCues.length ? visibleCues[visibleCues.length - 1].text : undefined);
  if (code) return <CodeCard />;

  return (
    <AbsoluteFill style={{background: C.bg}}>
      <LeetcodeBackdrop />
      <LeetcodeHeader slug="merge-intervals" identity={{number: 56, method: '普通数组'}} detail={shot.chapterTitle} />
      <svg
        width={1920}
        height={1080}
        viewBox="0 0 1920 1080"
        style={{position: 'absolute', inset: 0}}
      >
        <SvgText x={130} y={215} size={42} weight={600}>
          {titles[shot.visualType] ?? shot.chapterTitle ?? ''}
        </SvgText>
        <SvgText x={1785} y={215} size={23} color={C.gold} anchor="end">示例</SvgText>
        {cueText && <SvgText x={130} y={267} size={23} color={C.gold}>{cueText}</SvgText>}
        {shot.visualType === 'input' && <IntroScene shot={shot} frame={frame} />}
        {shot.visualType === 'touching-rule' && <TouchingRuleScene shot={shot} frame={frame} />}
        {shot.visualType === 'order' && <OrderScene shot={shot} frame={frame} />}
        {['begin', 'nested', 'overlap', 'touching', 'separate', 'separate-finish', 'close'].includes(shot.visualType)
          && <Board shot={shot} frame={frame} />}
        {shot.visualType === 'begin' && (
          <SvgText x={130} y={900} size={24}>从起点最早的一段开始</SvgText>
        )}
        {shot.visualType === 'close' && (
          <>
            <SvgText x={130} y={900} size={25}>
              起点不超过当前终点：合并；大于当前终点：输出并重开
            </SvgText>
            <SvgText x={130} y={934} size={22} color={C.muted}>
              排序 O(n log n) · 扫描 O(n) · 额外空间 O(n)
            </SvgText>
          </>
        )}
        {!hideSubtitles && (shot.subtitles ?? []).map((subtitle, index) => (
          frame >= subtitle.from && frame <= (subtitle.to ?? subtitle.from + (subtitle.duration ?? 90))
            ? (
              <g key={index}>
                <rect x={180} y={SUBTITLE_TOP} width={1560} height={70} rx={12} fill="#0B1220" />
                <SvgText x={960} y={1007} size={27} anchor="middle">{subtitle.text}</SvgText>
              </g>
            )
            : null
        ))}
      </svg>
    </AbsoluteFill>
  );
}

type MainProps = {hideSubtitles?: boolean};

export function Main({hideSubtitles = false}: MainProps) {
  return (
    <AbsoluteFill>
      {shots.map((shot) => (
        <Sequence key={shot.id} from={shot.from} durationInFrames={shot.durationInFrames}>
          <Scene shot={shot} hideSubtitles={hideSubtitles} />
        </Sequence>
      ))}
      {__HAS_VOICE_AUDIO__ && !STORYBOARD.meta.pendingAudio && (
        <Audio src={staticFile('audio/voice.wav')} />
      )}
    </AbsoluteFill>
  );
}
