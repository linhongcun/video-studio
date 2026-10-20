// Prep-only test composition for the EP.05 WorldMap component. Example data only — NOT the storyboard.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {StoryboardComponent} from './components/StoryboardComponent';
import {ShotElement} from './storyboard';
import {FONT, P} from './theme';

export const GALLERY = {width: 1920, height: 1080, fps: 30, durationInFrames: 180};
const NODES = ['东京', '新加坡', '孟买', '法兰克福', '伦敦', '纽约', '圣保罗', '悉尼', '芝加哥'];
export const GALLERY_ELEMENT: ShotElement = {
  id: 'gallery-map', component: 'WorldMapPage', x: 120, y: 140, w: 1680, h: 700, z: 1,
  title: '原理演示', url: 'shop.example/demo', showPadlock: true, pageTitle: '所有人直接找源站', badges: ['原理演示', '示例数据', '慢放演示'],
  viewKeyframes: [{frame: 0, centerLon: 150, centerLat: 22, lonSpan: 330}, {frame: 100, centerLon: 150, centerLat: 22, lonSpan: 330}, {frame: 135, centerLon: 122.5, centerLat: 30.6, lonSpan: 18}],
  dots: [
    {id: 'you', city: '上海', label: '你在上海', labelPos: 'left', color: 'primary', size: 14, appearFrame: 0, pulse: true},
    {id: 'origin', city: '美国西海岸', label: '源站', labelPos: 'bottom', color: 'success', size: 16, appearFrame: 4, pulse: true, colorKeyframes: [{frame: 75, color: 'danger'}], highlightFrame: 75},
    ...NODES.map((city, i) => ({id: `n${i}`, city, color: 'secondary', size: 9, appearFrame: 20 + i * 3})),
    {id: 'near', city: '杭州', label: '上海附近的节点', labelPos: 'bottom', labelAppearFrame: 135, color: 'secondary', size: 11, appearFrame: 47, pulse: true, pulseStartFrame: 135},
  ],
  lines: [
    {id: 'sh-origin', from: 'you', to: 'origin', startFrame: 8, drawFrames: 24, color: 'primary', width: 5, bulge: .2, label: '来回一趟 约 140 ms', labelColor: 'accent', labelDy: -40, dimFrame: 105, dimOpacity: .25,
      packets: [{startFrame: 34, travelFrames: 24, mode: 'roundtrip', repeat: 2, everyFrames: 52}]},
    {id: 'ldn-origin', from: '伦敦', to: 'origin', startFrame: 30, drawFrames: 20, color: 'secondary', width: 3, bulge: .12, dimFrame: 100},
    {id: 'sp-origin', from: '圣保罗', to: 'origin', startFrame: 34, drawFrames: 20, color: 'secondary', width: 3, bulge: .15, dimFrame: 100},
    {id: 'bj-origin', from: '北京', to: 'origin', startFrame: 38, drawFrames: 20, color: 'secondary', width: 3, dashed: true, dimFrame: 100},
    {id: 'sh-near', from: 'you', to: 'near', startFrame: 135, drawFrames: 12, color: 'success', width: 6, bulge: .25,
      packets: [{startFrame: 148, travelFrames: 8, mode: 'roundtrip', repeat: 3, everyFrames: 10}]},
  ],
  labels: [
    {id: 'timer-old', text: '约 140 ms', at: {lon: 124.2, lat: 32.2}, anchor: 'left', color: 'text2', size: 34, appearFrame: 136, strike: true, strikeFrame: 145},
    {id: 'timer-new', text: '约 10 ms', at: {lon: 124.2, lat: 31.1}, anchor: 'left', color: 'success', size: 40, weight: 900, appearFrame: 150},
  ],
};
export const MapGallery: React.FC = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{background: P.bg, color: P.text, fontFamily: FONT}}>
    <div style={{position: 'absolute', left: GALLERY_ELEMENT.x, top: GALLERY_ELEMENT.y, width: GALLERY_ELEMENT.w, height: GALLERY_ELEMENT.h}}>
      <StoryboardComponent e={GALLERY_ELEMENT} frame={frame} siblings={[GALLERY_ELEMENT]} />
    </div>
    <div style={{position: 'absolute', left: 160, top: 900, width: 1600, height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 40, color: P.text}}>MapGallery 测试画面（示例数据，非分镜）· 第 {frame} 帧</div>
  </AbsoluteFill>;
};
