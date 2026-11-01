// Canvas navigation colors; the caller retains its shared pageTheme background.
export type BranchNodeKind = 'step' | 'decision' | 'success' | 'failure' | 'unknown';
export type BranchPoint = [number, number];
export type BranchMapNode = {id: string; label: string; x: number; y: number; w?: number; kind?: BranchNodeKind; color?: string};
export type BranchMapEdge = {id: string; from: string; to: string; label?: string; via?: BranchPoint[]; color?: string; dashed?: boolean; labelAt?: BranchPoint};
export type BranchMapShot = {
  focus: string; mode?: 'overview' | 'focus'; activeNodes?: string[]; activeEdges?: string[];
  crumb?: string; enter?: {hold: number; zoom: number}; exit?: {zoom: number; hold: number};
  overviewTitle?: string; overviewHint?: string;
};
export type BranchMapSpec = {
  title: string; overviewTitle?: string; overviewHint?: string;
  nodes: BranchMapNode[]; edges: BranchMapEdge[]; shots: Record<string, BranchMapShot>;
};
export type BranchNavProps = {spec: BranchMapSpec; shotId: string; frame: number; durationInFrames: number; children?: any; foreground?: any};
import {C as THEME} from './theme';
export const BRANCH_COLORS = {bg:THEME.bg,ink:THEME.text,muted:THEME.muted,edge:THEME.edge,blue:THEME.blue,teal:THEME.teal,gold:THEME.gold,red:THEME.red};
const clamp = (v: number) => Math.max(0, Math.min(1, v));
const smooth = (v: number) => {const p = clamp(v); return p * p * (3 - 2 * p)};
const ramp = (v: number, a: number, b: number) => smooth((v - a) / Math.max(.001, b - a));
const nodeColor = (n: BranchMapNode) => n.color ?? ({step: BRANCH_COLORS.blue, decision: BRANCH_COLORS.gold, success: BRANCH_COLORS.teal, failure: BRANCH_COLORS.red, unknown: BRANCH_COLORS.gold}[n.kind ?? 'step']);

export {actualNavState,navigationEvents} from '../branch-map';
import {actualNavState} from '../branch-map';

/** No React dependency/type package in the shared directory: the caller supplies React. */
export function createBranchNavigator(React: {createElement: (...args: any[]) => any; Fragment: any}) {
  const h = React.createElement, C = BRANCH_COLORS;
  const text = (value: any, x: number, y: number, size: number, color = C.ink, extra: any = {}) => {const {key, ...style} = extra; return h('div', {key, style: {position: 'absolute', left: x, top: y, fontSize: size, lineHeight: 1.3, color, fontWeight: 600, ...style}}, value)};
  return function BranchNavigator({spec, shotId, frame, durationInFrames, children, foreground}: BranchNavProps) {
    const state = actualNavState(spec, shotId, frame, durationInFrames), b = state.binding;
    const node = spec.nodes.find(n => n.id === state.focusId)!;
    const nodes = new Map(spec.nodes.map(n => [n.id, n]));
    const activeNodes = new Set(state.activeNodes), activeEdges = new Set(state.activeEdges);
    const world: any[] = [];
    for (const edge of spec.edges) {
      const from = nodes.get(edge.from), to = nodes.get(edge.to); if (!from || !to) continue;
      const selfLoop = from.id === to.id;
      const via: BranchPoint[] = edge.via ?? (selfLoop ? [[from.x + (from.w ?? 240) / 2 + 70, from.y + 130], [from.x - (from.w ?? 240) / 2 - 70, from.y + 130]] : []);
      const port = (n: BranchMapNode, toward: BranchPoint): BranchPoint => {
        const dx = toward[0] - n.x, dy = toward[1] - n.y;
        const halfW = (n.w ?? 240) / 2, halfH = (n.w ?? 240) * 900 / 1920 / 2;
        const t = Math.min(Math.abs(dx) > .001 ? halfW / Math.abs(dx) : Infinity, Math.abs(dy) > .001 ? halfH / Math.abs(dy) : Infinity);
        return Number.isFinite(t) ? [n.x + dx * t, n.y + dy * t] : [n.x + halfW, n.y];
      };
      const start = port(from, via[0] ?? [to.x, to.y]);
      const end = port(to, via[via.length - 1] ?? [from.x, from.y]);
      const points: BranchPoint[] = [start, ...via, end];
      const on = activeEdges.has(edge.id), color = on ? (edge.color ?? nodeColor(to)) : THEME.link;
      const commands = points.map((p, i) => `${i ? 'L' : 'M'}${p[0]} ${p[1]}`).join(' ');
      const prev = points[points.length - 2], angle = Math.atan2(end[1] - prev[1], end[0] - prev[0]);
      const arrow = `M${end[0] - 11 * Math.cos(angle - .45)} ${end[1] - 11 * Math.sin(angle - .45)}L${end[0]} ${end[1]}L${end[0] - 11 * Math.cos(angle + .45)} ${end[1] - 11 * Math.sin(angle + .45)}`;
      world.push(h('svg', {key: `edge-${edge.id}`, width: 1920, height: 900, style: {position: 'absolute', inset: 0, opacity: state.mapOpacity * (on ? 1 : .94)}}, h('path', {d: commands, fill: 'none', stroke: color, strokeWidth: on ? 4 : 2.5, strokeDasharray: edge.dashed ? '10 7' : undefined, strokeLinejoin: 'round'}), h('path', {d: arrow, fill: 'none', stroke: color, strokeWidth: on ? 4 : 2.5, strokeLinecap: 'round'})));
      if (edge.label) {
        const p = edge.labelAt ?? (selfLoop && via.length ? [(via[0][0] + via[via.length - 1][0]) / 2, (via[0][1] + via[via.length - 1][1]) / 2] : [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2 - 21]);
        world.push(text(edge.label, p[0], p[1], 21, on ? color : C.muted, {key: `label-${edge.id}`, transform: 'translate(-50%,-50%)', padding: '4px 10px', borderRadius: 7, background: C.bg, whiteSpace: 'nowrap', opacity: state.mapTextOpacity}));
      }
    }
    for (const n of spec.nodes) {
      const w = n.w ?? 240, height = w * 900 / 1920, on = activeNodes.has(n.id), color = nodeColor(n);
      world.push(h('div', {key: `node-${n.id}`, 'data-branch-node': n.id, style: {position: 'absolute', left: n.x - w / 2, top: n.y - height / 2, width: w, height, boxSizing: 'border-box', border: `${on ? 3 : 1.5}px solid ${on ? color : THEME.link}`, borderRadius: n.kind === 'decision' ? 28 : n.kind === 'success' || n.kind === 'failure' ? 45 : 15, background: on ? THEME.redSoft : C.bg, opacity: state.mapOpacity * (on ? 1 : .9), display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '12px 18px', textAlign: 'center', color: on ? color : THEME.muted, whiteSpace: 'pre-line', fontSize: 27, lineHeight: 1.32, fontWeight: 650}}, h('span', {style: {opacity: state.mapOpacity > .001 ? state.mapTextOpacity / state.mapOpacity : 0}}, n.label)));
    }
    const localWidth = node.w ?? 240, localScale = localWidth / 1920;
    world.push(h('div', {key: 'actual-detail', 'data-branch-detail': state.focusId, style: {position: 'absolute', left: node.x - localWidth / 2, top: node.y - localWidth * 900 / 1920 / 2, width: 1920, height: 900, transform: `scale(${localScale})`, transformOrigin: '0 0', opacity: state.detailOpacity}}, children));
    const mapHeading = b.overviewTitle ?? spec.overviewTitle ?? spec.title;
    const hint = b.overviewHint ?? spec.overviewHint ?? '先看整体，再进入当前步骤';
    return h('div', {className: 'branch-navigator', 'data-nav-phase': state.phase, 'data-nav-progress': state.progress, style: {position: 'absolute', left: 0, top: 0, width: 1920, height: 900, pointerEvents: 'none'}},
      h('div', {style: {position: 'absolute', inset: 0, overflow: 'hidden', clipPath: 'inset(160px 0 0 0)'}}, h('div', {style: {position: 'absolute', width: 1920, height: 900, transformOrigin: '0 0', transform: `translate(${state.camera.tx}px,${state.camera.ty}px) scale(${state.camera.scale})`}}, ...world)),
      !foreground && text(mapHeading, 130, 186, 39, C.ink, {width: 1660, opacity: state.headingOpacity}),
      h('div', {style: {position: 'absolute', left: 768, top: 35, width: 900, height: 74, boxSizing: 'border-box', borderLeft: `3px solid ${nodeColor(node)}`, padding: '0 18px', color: C.ink}},
        text(state.progress > .6 ? '当前位置' : '先看全局', 18, 0, 14, C.muted),
        text(state.progress > .6 ? state.crumb : hint, 18, 20, 20, state.progress > .6 ? nodeColor(node) : C.ink, {width: 865, whiteSpace: 'pre-line'})),
      foreground ? h('div', {style: {position: 'absolute', inset: 0, zIndex: 30}}, foreground) : null);
  };
}
