import React from 'react';
import {progress} from '../animation';
import {P} from '../theme';
import {BrowserChrome} from './BrowserChrome';
import {browserHeaderHeight, browserPageBox} from './browserLayout';
import {latestKey} from './pageState';
import {colorToken, Copy, stateAt, textWidth, UIProps} from './ui';

type Node = {id: string; x: number; y: number; w: number; h: number; [key: string]: any};
type Point = {x: number; y: number};
type Packet = {path: string[]; hops: {startFrame: number; travelFrames: number}[]; [key: string]: any};
/** Return endpoints in travel order, including for right-to-left responses. */
export function nodeLinkEndpoints(from: Node, to: Node): [Point, Point] {
  const forward = from.x <= to.x;
  return [{x: from.x + (forward ? from.w : 0), y: from.y + from.h / 2}, {x: to.x + (forward ? 0 : to.w), y: to.y + to.h / 2}];
}
export function packetAt(packet: Packet, nodes: Node[], frame: number) {
  const first = packet.hops[0], last = packet.hops[packet.hops.length - 1];
  if (!first || frame < first.startFrame || frame >= last.startFrame + last.travelFrames + 8) return null;
  let hopIndex = 0;
  for (let i = 1; i < packet.hops.length; i++) if (frame >= packet.hops[i].startFrame) hopIndex = i;
  const hop = packet.hops[hopIndex], from = nodes.find(n => n.id === packet.path[hopIndex]), to = nodes.find(n => n.id === packet.path[hopIndex + 1]);
  if (!from || !to) return null;
  const [a, b] = nodeLinkEndpoints(from, to), p = hop.travelFrames <= 0 ? 1 : progress(frame, hop.startFrame, hop.travelFrames);
  return {x: a.x + (b.x - a.x) * p, y: a.y + (b.y - a.y) * p, hopIndex, progress: p, traveling: frame <= hop.startFrame + hop.travelFrames};
}

export const NodeDiagramPage: React.FC<UIProps> = props => {
  const {frame} = props, e = stateAt(props.e, frame), nodes: Node[] = e.nodes ?? [];
  const local = ({x, y}: Point) => ({x: x - e.x - 3, y: y - e.y - 3 - browserHeaderHeight(e)});
  return <BrowserChrome {...props} e={{...e, pageBlank: true}}>
    <svg data-diagram-links width="100%" height="100%" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
      {(e.links ?? []).map(link => {
        const from = nodes.find(n => n.id === link.from), to = nodes.find(n => n.id === link.to);
        if (!from || !to || frame < link.startFrame) return null;
        const [a, b] = nodeLinkEndpoints(from, to).map(local), p = link.drawFrames <= 0 ? 1 : progress(frame, link.startFrame, link.drawFrames);
        const dim = latestKey(link.keys, frame)?.dim ?? false;
        return <line key={link.id} data-diagram-link={link.id} x1={a.x} y1={a.y} x2={a.x + (b.x - a.x) * p} y2={a.y + (b.y - a.y) * p} stroke={colorToken(link.color)} strokeWidth={link.width} strokeLinecap="round" opacity={dim ? .3 : 1} strokeDasharray={dim ? '10 10' : undefined} />;
      })}
    </svg>
    {nodes.map(node => {
      if (frame < (node.appearFrame ?? 0)) return null;
      const key: Record<string, any> = latestKey(node.keys, frame) ?? {}, tone = e.tones?.[key.tone ?? 'normal'] ?? {};
      const fade = progress(frame, node.appearFrame ?? 0, 6);
      const browser = node.kind === 'browserIcon', contentHeight = node.h - 24;
      const linesHeight = e.nodeFontSize * 1.2 + (key.sub ? e.nodeSubSize * 1.2 : 0) + (key.status ? e.statusSize * 1.2 : 0);
      const textScale = Math.min(1, contentHeight / linesHeight);
      return <div key={node.id} data-diagram-node={node.id} data-tone={key.tone} style={{...browserPageBox(e, [node.x, node.y, node.w, node.h]), boxSizing: 'border-box', borderRadius: 12, border: `${browser ? 2 : 4}px solid ${browser ? P.text2 : colorToken(tone.border)}`, background: browser ? P.bg : colorToken(tone.bg), color: colorToken(tone.text), opacity: fade * (tone.opacity ?? 1), display: 'flex', flexDirection: browser ? 'row' : 'column', alignItems: 'center', justifyContent: 'center', padding: '8px 12px', gap: browser ? 12 : 0}}>
        {browser ? <>
          <svg aria-hidden width={24} height={28} viewBox="0 0 32 36" fill="none" stroke={P.text2} strokeWidth={3} style={{flexShrink: 0}}><path d="M8 15V10a8 8 0 0 1 16 0v5" /><rect x={4} y={14} width={24} height={20} rx={5} /></svg>
          <Copy mono size={e.nodeSubSize} width={node.w - 64} height={contentHeight} style={{whiteSpace: 'nowrap', color: P.text}}>{node.text}</Copy>
        </> : <>
          <Copy size={e.nodeFontSize * textScale} width={node.w - 32} height={e.nodeFontSize * 1.2 * textScale} style={{fontWeight: 700, textAlign: 'center', whiteSpace: 'nowrap'}}>{node.text}</Copy>
          {key.sub && <Copy mono size={e.nodeSubSize * textScale} width={node.w - 32} height={e.nodeSubSize * 1.2 * textScale} style={{color: P.primary, textAlign: 'center', whiteSpace: 'nowrap'}}>{key.sub}</Copy>}
          {key.status && <Copy size={e.statusSize * textScale} width={node.w - 32} height={e.statusSize * 1.2 * textScale} style={{color: colorToken(key.statusColor), textAlign: 'center', whiteSpace: 'nowrap'}}>{key.status}</Copy>}
        </>}
      </div>;
    })}
    {(e.packets ?? []).map((packet: Packet) => {
      const position = packetAt(packet, nodes, frame);
      if (!position) return null;
      const point = local(position), color = colorToken(packet.color);
      const showLabel = packet.label && position.traveling && position.progress >= packet.labelFrom && position.progress <= packet.labelTo && (!packet.labelHops || packet.labelHops.includes(position.hopIndex));
      const labelWidth = textWidth(packet.label ?? '', packet.labelSize) + 20, labelHeight = packet.labelSize * 1.2 + 8;
      return <React.Fragment key={packet.id}>
        <div data-diagram-packet={packet.id} style={{position: 'absolute', left: point.x - packet.size / 2, top: point.y - packet.size / 2, width: packet.size, height: packet.size, borderRadius: '50%', background: color, boxShadow: `0 0 ${packet.size}px ${color}`}} />
        {showLabel && <div data-packet-label={packet.id} style={{position: 'absolute', left: point.x - labelWidth / 2, top: point.y + packet.labelDy - labelHeight / 2, width: labelWidth, height: labelHeight, padding: '4px 10px', boxSizing: 'border-box', borderRadius: labelHeight / 2, background: P.bg, color: colorToken(packet.labelColor)}}><Copy size={packet.labelSize} width={labelWidth - 20} height={labelHeight - 8} style={{whiteSpace: 'nowrap', textAlign: 'center'}}>{packet.label}</Copy></div>}
      </React.Fragment>;
    })}
  </BrowserChrome>;
};
