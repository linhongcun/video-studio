import React from 'react';
import {AbsoluteFill} from 'remotion';
import covers from '@covers';
import {C, FONT} from './theme';

export const coverSizes = {'16x9': {width: 1920, height: 1080}, '4x3': {width: 1440, height: 1080}, '3x4': {width: 1080, height: 1440}};
const routes = [
  ['2PC / XA', '准备后决定'], ['AT', '日志与撤销'], ['TCC', '业务先预留'],
  ['Saga', '提交后补偿'], ['可靠消息', '异步再处理'],
];
export const Cover: React.FC<{size?: string}> = ({size = '16x9'}) => {
  const s = covers.sizes[size], portrait = size === '3x4', wide = size === '16x9';
  const x = s.content.x, w = s.content.w;
  return <AbsoluteFill style={{background: C.bg, color: C.text, fontFamily: FONT}}>
    <div style={{position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 85% 15%, #17556D88, transparent 65%)'}} />
    <div style={{position: 'absolute', left: s.watermarkZone.x, top: s.watermarkZone.y, color: C.muted, fontSize: 27}}>IT小村 / 分布式 · EP.21</div>
    <div style={{position: 'absolute', left: x, top: portrait ? 230 : 205, width: w, fontSize: wide ? 108 : portrait ? 92 : 82, fontWeight: 800, lineHeight: 1.3, letterSpacing: -2}}>
      分布式事务<br /><span style={{color: C.teal}}>到底怎么选？</span>
    </div>
    <div style={{position: 'absolute', left: x, top: portrait ? 565 : 485, fontSize: wide ? 35 : 28, color: C.muted}}>五条常见路线，讲清机制与边界</div>
    <div style={{position: 'absolute', left: x, top: portrait ? 700 : 600, width: w, height: portrait ? 390 : 225, borderTop: `2px solid ${C.teal}`, borderBottom: `2px solid ${C.edge}`, display: 'flex', flexDirection: portrait ? 'column' : 'row', justifyContent: 'space-around'}}>
      {routes.map(([name, action], i) => <div key={name} style={{display: 'flex', flexDirection: portrait ? 'row' : 'column', alignItems: 'center', justifyContent: portrait ? 'space-between' : 'center', padding: portrait ? '0 25px' : 0, gap: portrait ? 0 : 22}}>
        <div style={{fontSize: wide ? 37 : portrait ? 34 : 26, fontWeight: 700, color: i === 2 ? C.teal : C.text}}>{name}</div>
        <div style={{fontSize: wide ? 27 : portrait ? 30 : 21, color: C.muted}}>{action}</div>
      </div>)}
    </div>
    <div style={{position: 'absolute', left: x, top: portrait ? 1230 : 875, fontSize: portrait ? 26 : 21, color: C.muted}}>先看业务约束，再选协作机制</div>
  </AbsoluteFill>;
};
