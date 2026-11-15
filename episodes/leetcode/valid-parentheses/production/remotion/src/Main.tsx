import React, {type ReactNode} from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {LeetcodeBackdrop, LeetcodeHeader} from '../../../../../_shared/leetcode-video/Frame';
import {C, FONT, MONO} from '../../../../../_shared/leetcode-video/theme';
import {CodeCard} from './CodeCard';
import {MAIN, Run, Shot, STORYBOARD, TRACE, TraceEvent, replay, shots} from './data';
import {actionProgress, clamp} from './timeline';

declare const __HAS_VOICE_AUDIO__: boolean;

const TYPE_COLOR: Record<string, string> = {
  '(': '#7DB5FF', ')': '#7DB5FF',
  '[': '#BEADFF', ']': '#BEADFF',
  '{': '#F6A5C9', '}': '#F6A5C9',
};
const BAD = '#FF9B9B';
const BOX = 96;
const GAP = 20;
const ROW_Y = 330;
const SLOT_H = 72;
const SUBTITLE_TOP = 962;
const titles: Record<string, string> = {
  input: '题意：三类括号，怎样才算有效',
  question: '遇到右括号，该和谁配对？',
  method: '记住还没配对的左括号：栈',
  trace: '沿一个有效例子：左括号入栈，右括号比栈顶',
  fail: '两种失败：栈空、栈不空',
  close: '三条规则与复杂度',
};
const KIND_NAME: Record<string, string> = {'(': '左圆括号', ')': '右圆括号', '[': '左方括号', ']': '右方括号', '{': '左花括号', '}': '右花括号'};

type SvgTextProps = {x: number; y: number; children: ReactNode; size?: number; color?: string; anchor?: 'start' | 'middle' | 'end'; weight?: number; mono?: boolean};
function SvgText({x, y, children, size = 26, color = C.text, anchor = 'start', weight, mono = false}: SvgTextProps) {
  return (
    <text x={x} y={y} fill={color} fontFamily={mono ? MONO : FONT} fontSize={size} fontWeight={weight} textAnchor={anchor}>
      {children}
    </text>
  );
}

type Origin = {x: number; y: number; scale?: number};

function charX(origin: Origin, index: number) {
  return origin.x + index * (BOX + GAP);
}
function stackSlot(origin: Origin, chars: number, depth: number) {
  const x = charX(origin, chars) + 150;
  return {x, y: origin.y + 470 - (depth + 1) * SLOT_H};
}

type AnimatingEvent = {event: TraceEvent; frac: number};

type BoardProps = {
  run: Run;
  showStack?: boolean;
  done: number;
  animating?: AnimatingEvent;
  origin: Origin;
  highlightTop?: boolean;
  pointer?: number;
  pointerText?: string;
  showStackLabel?: boolean;
  title?: string;
};

function Board({run, done, animating, origin, highlightTop = false, pointer, pointerText, showStackLabel = true, showStack = true, title}: BoardProps) {
  const state = replay(run, done);
  const scale = origin.scale ?? 1;
  const n = run.chars.length;
  const event = animating?.event;
  const frac = clamp(animating?.frac ?? 0);
  const slotFor = (depth: number) => stackSlot({x: 0, y: 0}, n, depth);
  const charPos = (index: number) => ({x: index * (BOX + GAP), y: 0});
  const stackX = slotFor(0).x;
  const stackBottom = 470;
  const stackLeft = stackX - 20;
  const stackWidth = BOX + 40;
  const inStack = new Set(state.stack);
  const current = event?.index;
  const movingPush = event?.kind === 'push';
  const movingPop = event?.kind === 'pop';
  const popLeft = movingPop ? state.stack[state.stack.length - 1] : undefined;
  const showFailure = (event?.kind === 'mismatch' || event?.kind === 'empty' || event?.kind === 'leftover') && frac > 0.45;
  const failureTop = event?.kind === 'mismatch' ? state.stack[state.stack.length - 1] : undefined;
  const finished = event?.kind === 'finish' && frac > 0.4;
  const verdictText = finished
    ? '栈为空 → 有效'
    : showFailure && event?.kind === 'empty'
      ? '栈为空，没有左括号可配 → 无效'
      : showFailure && event?.kind === 'mismatch'
        ? (showStack ? '栈顶类型不同 → 无效' : '最近未配对的左括号类型不同 → 无效')
        : showFailure && event?.kind === 'leftover'
          ? '读完后栈不为空 → 无效'
          : undefined;

  return (
    <g transform={`translate(${origin.x} ${origin.y}) scale(${scale})`}>
      {title && <SvgText x={0} y={-36} size={24} color={C.muted}>{title}</SvgText>}
      {run.chars.map((ch, index) => {
        const base = charPos(index);
        const isMoving = movingPush && current === index;
        const target = isMoving ? slotFor(state.stack.length) : base;
        const bx = base.x + (target.x - base.x) * (isMoving ? frac : 0);
        const by = base.y + (target.y - base.y) * (isMoving ? frac : 0);
        const matched = state.matched.has(index) || (movingPop && frac > 0.6 && (index === current || index === popLeft));
        const failed = state.failed.has(index) || (showFailure && (index === current || index === failureTop)) || (showFailure && event?.kind === 'leftover' && inStack.has(index));
        const color = failed ? BAD : matched ? C.teal : TYPE_COLOR[ch];
        const stacked = inStack.has(index) && !failed && !matched;
        const isCurrent = current === index && event?.kind !== 'finish' && event?.kind !== 'leftover' && !isMoving;
        const pending = !matched && !failed && !stacked && !isCurrent && !(pointer === index) && index > (animating ? (current ?? -1) : (done === 0 ? -1 : run.events[Math.min(done, run.events.length) - 1].index));
        return (
          <g key={index} opacity={pending ? 0.42 : 1}>
            {isMoving && <rect x={base.x} y={base.y} width={BOX} height={BOX} rx={14} fill="none" stroke={C.edge} strokeDasharray="8 8" strokeWidth={2} />}
            <rect x={bx} y={by} width={BOX} height={BOX} rx={14} fill={matched ? '#123B3A' : failed ? '#3A1C22' : C.surface} stroke={color} strokeWidth={isCurrent || pointer === index ? 5 : 3} />
            <SvgText x={bx + BOX / 2} y={by + 66} size={54} color={color} anchor="middle" mono weight={700}>{ch}</SvgText>
            {!isMoving && <SvgText x={base.x + BOX / 2} y={BOX + 30} size={20} color={C.muted} anchor="middle">第{index + 1}个</SvgText>}
            {matched && !isMoving && <SvgText x={base.x + BOX - 10} y={18} size={20} color={C.teal} anchor="end">✓</SvgText>}
            {(isCurrent || pointer === index) && (
              <path d={`M ${base.x + BOX / 2} ${-16} l -14 -22 h 28 z`} fill={C.gold} />
            )}
          </g>
        );
      })}
      {pointer !== undefined && pointerText && (
        <SvgText x={charPos(pointer).x + BOX / 2} y={-50} size={24} color={C.gold} anchor="middle">{pointerText}</SvgText>
      )}
      {showStack && showStackLabel && (
        <>
          <SvgText x={stackLeft + stackWidth / 2} y={stackBottom - 4 * SLOT_H - 40} size={26} color={C.gold} anchor="middle" weight={600}>栈</SvgText>
          <path d={`M ${stackLeft} ${stackBottom - 4 * SLOT_H - 10} V ${stackBottom + 12} H ${stackLeft + stackWidth} V ${stackBottom - 4 * SLOT_H - 10}`} fill="none" stroke={C.edge} strokeWidth={3} />
          <SvgText x={stackLeft + stackWidth / 2} y={stackBottom + 44} size={20} color={C.muted} anchor="middle">底</SvgText>
        </>
      )}
      {!showStack && state.stack.map((index, depth) => (
        <g key={`open-${index}`}><SvgText x={charPos(index).x + BOX / 2} y={BOX + 62} size={20} color={depth === state.stack.length - 1 && highlightTop ? C.gold : C.muted} anchor="middle">{depth === state.stack.length - 1 ? '最近未配对' : '未配对'}</SvgText></g>
      ))}
      {showStack && state.stack.map((index, depth) => {
        const slot = slotFor(depth);
        const ch = run.chars[index];
        const popping = movingPop && depth === state.stack.length - 1;
        const failed = (showFailure && (event?.kind === 'leftover' || index === failureTop)) || state.failed.has(index);
        const color = failed ? BAD : TYPE_COLOR[ch];
        const dy = popping ? -70 * frac : 0;
        const opacity = popping ? 1 - frac : 1;
        return (
          <g key={`slot-${index}`} opacity={opacity}>
            <rect x={slot.x} y={slot.y + dy + 6} width={BOX} height={SLOT_H - 12} rx={10} fill={failed ? '#3A1C22' : C.surface} stroke={color} strokeWidth={3} />
            <SvgText x={slot.x + BOX / 2} y={slot.y + dy + 50} size={40} color={color} anchor="middle" mono weight={700}>{ch}</SvgText>
            {depth === state.stack.length - 1 && !popping && (
              <SvgText x={slot.x + BOX + 16} y={slot.y + dy + 44} size={22} color={highlightTop ? C.gold : C.muted}>栈顶</SvgText>
            )}
            {depth === state.stack.length - 1 && highlightTop && !popping && (
              <rect x={slot.x - 6} y={slot.y} width={BOX + 12} height={SLOT_H} rx={14} fill="none" stroke={C.gold} strokeWidth={3} />
            )}
          </g>
        );
      })}
      {showStack && state.stack.length === 0 && !movingPush && (
        <SvgText x={stackLeft + stackWidth / 2} y={stackBottom - 30} size={24} color={finished || state.verdict === 'valid' ? C.teal : showFailure && event?.kind === 'empty' ? BAD : C.muted} anchor="middle">空</SvgText>
      )}
      {verdictText && (
        <SvgText x={0} y={300} size={30} color={finished ? C.teal : BAD} weight={600}>{verdictText}</SvgText>
      )}
    </g>
  );
}

function actionState(shot: Shot, frame: number, run: Run) {
  const actions = shot.actionCues ?? [];
  const withEvents = actions.filter((action) => (action.events ?? []).length > 0);
  const first = withEvents.length ? Math.min(...withEvents.map((action) => Math.min(...(action.events ?? [])))) : run.events.length;
  let done = first;
  let animating: AnimatingEvent | undefined;
  for (const action of withEvents) {
    const events = action.events ?? [];
    const p = actionProgress(shot, frame, action.id, 0, 0.9);
    if (p <= 0) break;
    const stepFloat = p >= 0.999 ? events.length : p * events.length;
    const completed = Math.min(events.length, Math.floor(stepFloat));
    done = events[0] + completed;
    if (completed < events.length) {
      animating = {event: run.events[events[completed]], frac: stepFloat - completed};
      break;
    }
  }
  return {done, animating};
}

function statusLine(run: Run, done: number, animating?: AnimatingEvent) {
  const event = animating?.event ?? (done > 0 ? run.events[done - 1] : undefined);
  if (!event) return '';
  const ch = event.char ?? '';
  if (event.kind === 'push') return `${KIND_NAME[ch]} ${ch} 入栈`;
  if (event.kind === 'pop') return `${KIND_NAME[ch]} ${ch} 与栈顶 ${event.top} 同类 → 配对，弹出`;
  if (event.kind === 'mismatch') return `${KIND_NAME[ch]} ${ch} 与栈顶 ${event.top} 类型不同`;
  if (event.kind === 'empty') return `${KIND_NAME[ch]} ${ch} 到来时栈为空`;
  if (event.kind === 'leftover') return '字符串读完，栈里还有左括号';
  return '字符串读完，栈为空';
}

function InputScene({shot, frame}: {shot: Shot; frame: number}) {
  const reveal = actionProgress(shot, frame, 'reveal');
  const kinds: [string, string, string][] = [['(', ')', '圆括号'], ['[', ']', '方括号'], ['{', '}', '花括号']];
  const examples: [string, boolean, string][] = [['()[]{}', true, '有效：每对同类，先开后闭'], ['(]', false, '无效：类型不同'], ['([)]', false, '无效：顺序错误，方括号未闭合时圆括号先闭合']];
  return (
    <>
      {kinds.map(([open, close, name], i) => {
        const x0 = 230 + i * 540;
        return (
          <g key={name}>
            {[open, close].map((ch, j) => (
              <g key={ch}>
                <rect x={x0 + j * 120} y={300} width={BOX} height={BOX} rx={14} fill={C.surface} stroke={TYPE_COLOR[ch]} strokeWidth={3} />
                <SvgText x={x0 + j * 120 + BOX / 2} y={366} size={54} color={TYPE_COLOR[ch]} anchor="middle" mono weight={700}>{ch}</SvgText>
              </g>
            ))}
            <SvgText x={x0 + 108} y={445} size={26} color={C.muted} anchor="middle">{name}</SvgText>
          </g>
        );
      })}
      {examples.map(([s, ok, note], i) => {
        const appear = clamp(reveal * 3 - i);
        return (
          <g key={s} opacity={appear}>
            {s.split('').map((ch, j) => (
              <g key={j}>
                <rect x={230 + j * 74} y={540 + i * 120} width={62} height={62} rx={10} fill={C.surface} stroke={TYPE_COLOR[ch]} strokeWidth={2} />
                <SvgText x={230 + j * 74 + 31} y={584 + i * 120} size={36} color={TYPE_COLOR[ch]} anchor="middle" mono weight={700}>{ch}</SvgText>
              </g>
            ))}
            <SvgText x={760} y={583 + i * 120} size={30} color={ok ? C.teal : BAD} weight={600}>{ok ? '✓' : '✗'}</SvgText>
            <SvgText x={810} y={583 + i * 120} size={27} color={ok ? C.teal : C.text}>{note}</SvgText>
          </g>
        );
      })}
      <SvgText x={130} y={900} size={26} color={C.gold}>同类配对 + 正确顺序 + 每个右括号都有对应左括号</SvgText>
    </>
  );
}

function QuestionScene({shot, frame}: {shot: Shot; frame: number}) {
  const run = TRACE.cases.question;
  const compare = actionProgress(shot, frame, 'compare');
  const origin = {x: 130, y: 340};
  const mismatch = run.events[2];
  return (
    <>
      <Board run={run} done={2} origin={origin} pointer={2} pointerText="该和谁配对？" highlightTop={compare > 0} showStack={false} animating={compare > 0 ? {event: mismatch, frac: compare} : undefined} />
      <SvgText x={130} y={900} size={26} color={C.gold}>
        {compare > 0.45 ? '最近一个还没配对的是 [，它必须先闭合，外层 ( 才能闭合；) 只能和 [ 比较，类型不同 → 无效' : '前面有 ( 和 [ 两个左括号还没配对'}
      </SvgText>
    </>
  );
}

function MethodScene({shot, frame}: {shot: Shot; frame: number}) {
  const run = TRACE.cases.question;
  const collect = actionProgress(shot, frame, 'collect');
  const name = actionProgress(shot, frame, 'name');
  const origin = {x: 130, y: 340};
  const {done, animating} = (() => {
    const stepFloat = collect >= 0.999 ? 2 : collect * 2;
    const completed = Math.floor(stepFloat);
    return {done: completed, animating: completed < 2 ? {event: run.events[completed], frac: stepFloat - completed} : undefined};
  })();
  return (
    <>
      <Board run={run} done={done} animating={animating} origin={origin} highlightTop={collect >= 0.999} />
      <SvgText x={1120} y={420} size={28} color={C.text}>还没配对的左括号都放进去</SvgText>
      <SvgText x={1120} y={468} size={28} color={C.gold}>最近放进去的在最上面，先取出来比较</SvgText>
      <g opacity={name}>
        <SvgText x={1120} y={560} size={34} color={C.teal} weight={700}>栈 · 后进先出</SvgText>
        <SvgText x={1120} y={620} size={27} color={C.text}>左括号：入栈</SvgText>
        <SvgText x={1120} y={664} size={27} color={C.text}>右括号：与栈顶比较，同类则弹出</SvgText>
      </g>
      <SvgText x={130} y={900} size={26} color={C.gold}>只需记住未配对的左括号，并且总能取到最近的一个</SvgText>
    </>
  );
}

function TraceScene({shot, frame}: {shot: Shot; frame: number}) {
  const run = MAIN;
  const {done, animating} = actionState(shot, frame, run);
  const highlightTop = (shot.actionCues ?? []).some((action) => (action.events ?? []).length === 0 && actionProgress(shot, frame, action.id, 0, 0.5) > 0 && (action.id === 'top' || action.id === 'newtop'));
  const origin = {x: 130, y: 340};
  return (
    <>
      <Board run={run} done={done} animating={animating} origin={origin} highlightTop={highlightTop} />
      <SvgText x={130} y={900} size={26} color={C.gold}>{statusLine(run, done, animating)}</SvgText>
    </>
  );
}

function FailScene({shot, frame}: {shot: Shot; frame: number}) {
  const empty = actionProgress(shot, frame, 'empty');
  const leftover = actionProgress(shot, frame, 'leftover');
  const runState = (run: Run, p: number) => {
    const k = run.events.length;
    const stepFloat = p >= 0.999 ? k : p * k;
    const completed = Math.min(k, Math.floor(stepFloat));
    return {done: completed, animating: completed < k && p > 0 ? {event: run.events[completed], frac: stepFloat - completed} : undefined};
  };
  const left = runState(TRACE.cases.empty, empty);
  const right = runState(TRACE.cases.leftover, leftover);
  return (
    <>
      <Board run={TRACE.cases.empty} {...left} origin={{x: 130, y: 400, scale: 0.9}} title="右括号到来时栈为空" />
      <g opacity={leftover > 0 ? 1 : 0.35}>
        <Board run={TRACE.cases.leftover} {...right} origin={{x: 1010, y: 400, scale: 0.9}} title="读完后栈里还剩左括号" />
      </g>
      <SvgText x={130} y={900} size={26} color={C.gold}>
        {leftover > 0.45 ? '没有左括号可配，或左括号始终没有闭合，都返回无效' : '右括号来时栈为空 → 没有可配对的左括号'}
      </SvgText>
    </>
  );
}

function CloseScene({shot, frame}: {shot: Shot; frame: number}) {
  const complexity = actionProgress(shot, frame, 'complexity');
  const run = MAIN;
  return (
    <>
      <Board run={run} done={run.events.length} origin={{x: 130, y: 320, scale: 0.8}} showStackLabel />
      <SvgText x={1180} y={360} size={28} color={C.gold} weight={600}>1. 左括号入栈</SvgText>
      <SvgText x={1180} y={410} size={28} color={C.gold} weight={600}>2. 右括号：栈空或栈顶类型不同 → 无效</SvgText>
      <SvgText x={1180} y={450} size={28} color={C.gold} weight={600}>   同类 → 弹出</SvgText>
      <SvgText x={1180} y={500} size={28} color={C.gold} weight={600}>3. 读完后栈为空 → 有效</SvgText>
      <g opacity={complexity}>
        <SvgText x={1180} y={590} size={25} color={C.text} mono>{"pairs = {')': '(', ']': '[', '}': '{'}"}</SvgText>
        <SvgText x={1180} y={640} size={25} color={C.muted}>每个字符处理一次 · 时间 O(n)</SvgText>
        <SvgText x={1180} y={680} size={25} color={C.muted}>栈最多装下全部左括号 · 额外空间 O(n)</SvgText>
      </g>
      <SvgText x={130} y={900} size={26} color={C.gold}>右括号只和最近一个未配对的左括号比较，这就是栈</SvgText>
    </>
  );
}

type SceneProps = {shot: Shot; hideSubtitles: boolean};

function Scene({shot, hideSubtitles}: SceneProps) {
  const frame = useCurrentFrame();
  const code = shot.codeCardFrom !== undefined && frame >= shot.codeCardFrom;
  if (code) return <CodeCard />;
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <LeetcodeBackdrop />
      <LeetcodeHeader slug="valid-parentheses" identity={{number: 20, method: '栈'}} detail={shot.chapterTitle} />
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', inset: 0}}>
        <SvgText x={130} y={215} size={42} weight={600}>{titles[shot.visualType] ?? shot.chapterTitle ?? ''}</SvgText>
        <SvgText x={1785} y={215} size={23} color={C.gold} anchor="end">示例</SvgText>
        {shot.visualType === 'input' && <InputScene shot={shot} frame={frame} />}
        {shot.visualType === 'question' && <QuestionScene shot={shot} frame={frame} />}
        {shot.visualType === 'method' && <MethodScene shot={shot} frame={frame} />}
        {shot.visualType === 'trace' && <TraceScene shot={shot} frame={frame} />}
        {shot.visualType === 'fail' && <FailScene shot={shot} frame={frame} />}
        {shot.visualType === 'close' && <CloseScene shot={shot} frame={frame} />}
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
