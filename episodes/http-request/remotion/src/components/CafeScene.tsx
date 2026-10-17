import React from 'react';
import {Img, staticFile} from 'remotion';
import {BrowserChrome} from './BrowserChrome';
import {ScrambleText} from './ScrambleText';
import {FONT, P} from '../theme';

export type CafeSceneProps = {progress?: number; fromText?: string; toText?: string; elementStyles?: Record<string, React.CSSProperties>};

/** Shot 11: a flat café vignette around the request line, with no packet envelopes. */
export const CafeScene: React.FC<CafeSceneProps> = ({progress = 0.5, fromText = 'GET example.com', toText, elementStyles = {}}: CafeSceneProps) => (
  <div style={{position: 'relative', width: 1780, height: 920, color: P.text, fontFamily: FONT}}>
    <div style={{position: 'absolute', top: 10, left: 0, right: 0, textAlign: 'center', fontSize: 56, fontWeight: 700}}>公共 Wi-Fi 下，数据也要保护好</div>

    <svg width={1780} height={920} viewBox="0 0 1780 920" style={{position: 'absolute', inset: 0}} aria-hidden="true">
      <g data-element="wire" data-component="Line" style={elementStyles.wire}><path d="M626 400H1410" stroke={P.primary} strokeWidth={6} strokeLinecap="round" />
      <path d="m1392 386 18 14-18 14" fill="none" stroke={P.primary} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" /></g>
      <path d="M1120 600 1030 426" stroke={P.muted} strokeWidth={3} strokeDasharray="8 12" />
      <rect x={30} y={798} width={1720} height={24} rx={10} fill={P.muted} />
      <path d="M108 822v84M1672 822v84" stroke={P.panel2} strokeWidth={28} strokeLinecap="round" />
    </svg>

    <div data-element="pc" data-component="Laptop" style={{position: 'absolute', left: 26, top: 212, ...elementStyles.pc}}>
      <BrowserChrome width={600} height={414} showPadlock />
      <div style={{height: 22, background: P.panel2, borderBottom: `3px solid ${P.muted}`, borderRadius: '0 0 10px 10px'}} />
      <svg width={640} height={38} viewBox="0 0 640 38" style={{display: 'block', marginLeft: -20}} aria-hidden="true"><path d="M20 2h600l18 23q-8 11-30 11H32Q10 36 2 25Z" fill={P.panel2} stroke={P.muted} strokeWidth={3} /><path d="M248 3h144l-10 12H258Z" fill={P.muted} /></svg>
      <div style={{marginTop: 18, textAlign: 'center', fontSize: 34, color: P.text2}}>你的电脑</div>
    </div>

    <div data-element="plain" data-component="ScrambleText" style={{position: 'absolute', left: 674, top: 332, padding: '15px 20px', background: P.panel, border: `2px solid ${P.primary}`, borderRadius: 12, ...elementStyles.plain}}>
      <ScrambleText progress={progress} text={fromText} to={toText} style={{fontSize: 40}} />
    </div>

    <div data-element="srv" data-component="ServerRack" style={{position: 'absolute', left: 1410, top: 212, width: 316, ...elementStyles.srv}}>
      <div style={{padding: 20, border: `4px solid ${P.muted}`, borderRadius: 20, background: P.panel}}>
        {[0, 1, 2].map((i) => <div key={i} style={{height: 96, marginBottom: i === 2 ? 0 : 18, padding: '0 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderRadius: 10, background: P.panel2}}><div style={{width: 130, display: 'flex', flexDirection: 'column', gap: 12}}>{[0, 1].map((j) => <div key={j} style={{height: 7, borderRadius: 4, background: P.muted}} />)}</div><div style={{width: 16, height: 16, borderRadius: 8, background: i === 1 ? P.primary : P.success}} /></div>)}
      </div>
      <div style={{marginTop: 22, textAlign: 'center', fontSize: 34, color: P.text2}}>服务器</div>
    </div>

    {/* Small observer: bent arm raises the phone; eyes glance toward its screen. */}
    <svg data-element="peeker" data-component="PeekerFigure" width={480} height={350} viewBox="0 0 480 350" style={{position: 'absolute', left: 826, top: 448, ...elementStyles.peeker}} role="img" aria-label="一个人举着手机，试图查看公共 Wi-Fi 上的数据，却看不懂">
      <path d="M106 350v-62q0-72 75-72t80 72v62" fill={P.secondary} />
      <path d="m222 272 62 26 62-130" fill="none" stroke={P.secondary} strokeWidth={32} strokeLinecap="round" strokeLinejoin="round" />
      <path d="m338 184 12-27" stroke={P.text2} strokeWidth={24} strokeLinecap="round" />
      <circle cx={182} cy={159} r={57} fill={P.text2} />
      <path d="M126 156q-7-76 64-69 54 4 51 56l-39-23-34 27Z" fill={P.panel2} />
      <path d="m225 158 15 11-18 9" fill={P.text2} />
      <circle cx={212} cy={153} r={5} fill={P.bg} />
      <path d="m218 193 12-3" stroke={P.bg} strokeWidth={3} strokeLinecap="round" />
      <g transform="rotate(12 346 124)">
        <rect x={300} y={40} width={92} height={160} rx={15} fill={P.panel} stroke={P.muted} strokeWidth={4} />
        <rect x={310} y={62} width={72} height={108} rx={6} fill={P.panel2} />
        <path d="M320 99q26-25 52 0M330 111q16-15 32 0M340 122q6-6 12 0" fill="none" stroke={P.primary} strokeWidth={5} strokeLinecap="round" />
        <circle cx={346} cy={134} r={4} fill={P.primary} />
        <path d="M336 184h20" stroke={P.muted} strokeWidth={4} strokeLinecap="round" />
      </g>
      <path d="M414 8h48q14 0 14 14v40q0 14-14 14h-23l-18 18V76h-7q-14 0-14-14V22q0-14 14-14Z" fill={P.panel2} stroke={P.accent} strokeWidth={3} />
      <text x={438} y={58} textAnchor="middle" fill={P.accent} fontFamily={FONT} fontSize={44} fontWeight={700}>?</text>
    </svg>

    <Img data-element="cup" data-component="CoffeeCup" src={staticFile('assets/coffee-cup.svg')} style={{position: 'absolute', left: 660, top: 640, width: 170, height: 170, ...elementStyles.cup}} />
  </div>
);
