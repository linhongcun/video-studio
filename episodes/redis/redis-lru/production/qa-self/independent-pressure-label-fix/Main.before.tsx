import React from 'react';
import {AbsoluteFill,Audio,interpolate,staticFile,useCurrentFrame} from 'remotion';
import board from '@storyboard';
import model from '../../model.json';
import {RedisBackdrop,RedisHeader} from '../../../../../_shared/redis-video/Frame';
import {C,FONT,MONO} from '../../../../../_shared/redis-video/theme';

declare const __HAS_VOICE_AUDIO__:boolean;
const SHOTS=(board.scenes as any[]).flatMap(s=>s.shots);
const states=Object.fromEntries(model.states.map(s=>[s.id,s]));
const keys0='ABCDEFGH'.split('');
const idle0=Object.fromEntries(keys0.map((k,i)=>[k,90-i*10]));
const ease=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:t=>t*t*(3-2*t)});
const X=(i:number)=>160+i*200;
const poolX=(score:number)=>410+(score-20)*20;
type Entry={key:string;sampledIdle:number;sampledRound?:number};
const Txt=({x,y,size=32,fill=C.text,weight=600,anchor='start',children,opacity=1,mono=false}:any)=><text data-text="true" x={x} y={y} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} fill={fill} textAnchor={anchor} opacity={opacity}>{children}</text>;
const Arrow=({x1,y1,x2,y2,color=C.red,opacity=1,dashed=false}:any)=>{
 x1=Number(x1);y1=Number(y1);x2=Number(x2);y2=Number(y2);const length=Math.hypot(x2-x1,y2-y1)||1;const ux=(x2-x1)/length,uy=(y2-y1)/length;
 return <g opacity={opacity}><path d={`M${x1} ${y1}L${x2} ${y2}`} stroke={color} strokeWidth="4" strokeDasharray={dashed?'10 8':undefined} fill="none"/><path d={`M${x2-ux*14-uy*9} ${y2-uy*14+ux*9}L${x2} ${y2}L${x2-ux*14+uy*9} ${y2-uy*14-ux*9}`} stroke={color} strokeWidth="4" fill="none"/></g>;
};
const Badge=({x,y,w=240,text,color=C.red}:any)=>{x=Number(x);y=Number(y);w=Number(w);return <g><rect x={x} y={y} width={w} height="51" rx="12" fill={C.surface} stroke={color} strokeWidth="2"/><Txt x={x+w/2} y={y+35} size={27} fill={color} anchor="middle">{text}</Txt></g>;};

function KeyCard({name,age,x,y=348,selected=false,oldest=false,opacity=1,exists=true,subtext}:any){
 x=Number(x);y=Number(y);
 return <g data-key={name} data-existing={exists?'true':'false'} opacity={opacity}>
  <rect x={x} y={y} width="168" height="147" rx="18" fill={selected?C.redSoft:C.surface} stroke={selected?C.red:oldest?C.redDark:C.edge} strokeWidth={selected||oldest?4:2} strokeDasharray={exists?undefined:'8 6'}/>
  <Txt x={x+84} y={y+59} size={49} anchor="middle" fill={selected?C.redDark:C.text} mono>{name}</Txt>
  <Txt x={x+84} y={y+112} size={30} anchor="middle" fill={C.muted}>{exists?`${age} 秒`:'已不存在'}</Txt>
  {oldest&&<Txt x={x+84} y={y-19} size={27} anchor="middle" fill={C.redDark}>全局最旧</Txt>}
  {subtext&&<Txt x={x+84} y={y+188} size={26} anchor="middle" fill={C.muted}>{subtext}</Txt>}
 </g>;
}
function KeyRow({names=keys0,ages=idle0,selected=[],oldest=true,removed=[],dim=false}:any){
 return <g>{names.map((k:string,i:number)=><KeyCard key={`${k}-${i}`} name={k} age={ages[k]??0} x={X(i)} selected={selected.includes(k)} oldest={oldest&&k==='A'} opacity={removed.includes(k)?0:dim&&!selected.includes(k)?0.40:1}/>)}</g>;
}
function Pool({entries=[],fresh=[],selected='',ghost='',opacity=1,label='候选池 · 16项，只放大已占项',showMini=true}:any){
 return <g opacity={opacity} data-pool="true">
  <Txt x="130" y="589" size={31}>{label}</Txt>
  <Txt x="130" y="632" size={25} fill={C.muted}>采样时记录的空闲值 → 较旧</Txt>
  <path d="M365 782H1600" stroke={C.edge} strokeWidth="2"/>
  {entries.map((e:Entry,i:number)=>{
    const x=poolX(e.sampledIdle);const isFresh=fresh.includes(e.key);const focus=e.key===selected;
    return <g key={`${e.key}-${i}`} data-candidate={e.key} data-saved-score={e.sampledIdle}>
      <rect x={x} y="659" width="174" height="110" rx="15" fill={focus?C.redSoft:C.surface} stroke={focus?C.red:isFresh?C.red:C.edge} strokeWidth={focus?4:isFresh?3:2} strokeDasharray={e.key===ghost?'8 6':undefined}/>
      <Txt x={x+87} y="705" size={36} anchor="middle" fill={focus?C.redDark:C.text} mono>{e.key}</Txt>
      <Txt x={x+87} y="745" size={28} anchor="middle" fill={C.muted}>{e.sampledIdle} 秒</Txt>
      {isFresh&&<Txt x={x+87} y="807" size={23} anchor="middle" fill={C.red}>新样本</Txt>}
    </g>;
  })}
  {showMini&&<g>{Array.from({length:16},(_,i)=><rect key={i} x={560+i*47} y="840" width="35" height="16" rx="3" fill={i<entries.length?C.red:C.surface} stroke={C.edge}/>)}</g>}
 </g>;
}
function Flying({name,score,fromX,toX,p,y1=495,y2=659}:any){
 const x=interpolate(p,[0,1],[fromX,toX]);const y=interpolate(p,[0,1],[y1,y2]);
 return p>0&&p<1?<g data-moving-body="true" data-sample-flight={name}>
  <rect x={x} y={y} width="135" height="67" rx="13" fill={C.redSoft} stroke={C.red} strokeWidth="3"/>
  <Txt x={x+67.5} y={y+44} size={27} anchor="middle" mono>{name} · {score}</Txt>
 </g>:null;
}
function Headline({title,note}:any){return <g><Txt x="130" y="192" size={47} weight={800}>{title}</Txt><Txt x="132" y="247" size={28} fill={C.muted}>{note}</Txt></g>;}
function Pressure({name='I',opacity=1}:any){return <g opacity={opacity}><Badge x="1480" y="545" w="270" text={`写入 ${name} · 需要空间`}/><Arrow x1="1615" y1="597" x2="1615" y2="650"/></g>;}
function Scene({shot,f}:any){
 const id=shot.visualType;const dur=shot.durationInFrames;const second=shot.cueFrames?.sentences?.[1]??dur*.5;const p=f/dur;
 const afterFirst=['A','B','I','D','E','F','G','H'];
 const afterSecond=['A','B','I','J','E','F','G','H'];
 const first=(states['first-populated'] as any).pool as Entry[];
 const retained=(states['first-evicted'] as any).pool as Entry[];
 const combined=(states['second-populated'] as any).pool as Entry[];
 if(id==='problem')return <g data-model-state="problem-promise"><Headline title="最旧的 A，为什么还在？" note="Redis 近似 LRU · 固定访问历史与抽样的教学示例"/><KeyRow selected={['C']}/><Pressure/><Txt x="955" y="690" size={50} anchor="middle" fill={C.redDark}>A 空闲90秒，C 空闲70秒</Txt><Txt x="955" y="768" size={37} anchor="middle">却可能先删 C</Txt></g>;
 if(id==='capacity'){
  const q=ease(f,15,second-15);
  return <g data-model-state="eight-equal-cells-noTTL"><Headline title="新键要进来，先腾出内存" note="示例：8个等大键 / 8格已满；真实 maxmemory 比较字节"/><KeyRow oldest={false}/><g>{keys0.map((k,i)=><Txt key={k} x={X(i)+84} y="545" size={24} anchor="middle" fill={C.muted}>TTL 未设置</Txt>)}</g><g transform={`translate(${140*q},0)`} opacity={q}><Badge x="625" y="680" w="410" text="写入 I → 已满"/><Arrow x1="1230" y1="735" x2="1330" y2="735"/></g><Txt x="955" y="830" size={34} anchor="middle" fill={C.redDark}>容量淘汰 ≠ 到期删除</Txt></g>;
 }
 if(id==='exact'){
  const reversed=[...keys0].reverse();return <g data-model-state="exact-LRU-reference"><Headline title="精确参照：维护完整访问顺序" note="同一组键 · 当前时刻100；最后一次访问越早，空闲越久"/>{keys0.map((k,i)=><KeyCard key={k} name={k} age={idle0[k]} x={X(i)} y={348} oldest={false} subtext={`最近访问 ${10+i*10}`}/>)}<Txt x="130" y="632" size={31}>精确访问顺序：最近 → 最久没访问</Txt>{reversed.map((k,i)=><g key={k} opacity={ease(f,20+i*20,40+i*20)}><rect x={X(i)} y="675" width="168" height="126" rx="17" fill={k==='A'&&f>=second?C.redSoft:C.surface} stroke={k==='A'&&f>=second?C.red:C.edge} strokeWidth={k==='A'&&f>=second?4:2}/><Txt x={X(i)+84} y="725" size={37} anchor="middle" mono>{k}</Txt><Txt x={X(i)+84} y="771" size={27} anchor="middle">{idle0[k]} 秒</Txt></g>)}<Txt x="955" y="862" size={32} anchor="middle" fill={C.redDark} opacity={ease(f,second,second+25)}>精确 LRU 选择 A</Txt></g>;
 }
 if(id==='approximate')return <g data-model-state="reset-original-eight"><Headline title="回到同一组未淘汰的键" note="近似 LRU：记录访问时钟，淘汰时抽样比较"/><KeyRow/><g opacity={ease(f,second,second+35)}><Badge x="455" y="665" w="380" text="访问时钟 → 空闲估计"/><Badge x="1035" y="665" w="380" text="只抽部分键参与比较"/><Arrow x1="875" y1="691" x2="995" y2="691"/><Txt x="955" y="820" size={34} anchor="middle" fill={C.muted}>没有持续维护一份全局精确排名</Txt></g></g>;
 if(id==='sample'){
  const qs=[ease(f,20,70),ease(f,75,125),ease(f,130,180)];return <g data-model-state="preset-samples-CDE"><Headline title="第一轮：只看到抽中的 C、D、E" note="samples = 3 · 固定样本教学；A没有参与这次比较"/><KeyRow selected={['C','D','E']} dim/><Txt x="130" y="610" size={32}>本轮抽到的样本</Txt>{['C','D','E'].map((k,i)=><g key={k}><Flying name={k} score={idle0[k]} fromX={X(keys0.indexOf(k))} toX={650+i*230} p={qs[i]} y2={665}/><g opacity={qs[i]>.99?1:0}><KeyCard name={k} age={idle0[k]} x={650+i*230} y={665} selected/></g></g>)}</g>;
 }
 if(id==='pool'){
  const n=Math.min(3,Math.floor(Math.max(0,f-20)/55));const entries=first.filter(e=>['C','D','E'].slice(0,n).includes(e.key));return <g data-model-state={`pool-populate-${n}`}><Headline title="候选池：按采样时的空闲值排序" note="只复制候选记录，原始键仍留在数据集中"/><KeyRow selected={['C','D','E']} dim/><Pool entries={entries} selected={n===3?'C':''}/>{['C','D','E'].map((k,i)=><Flying key={k} name={k} score={idle0[k]} fromX={X(keys0.indexOf(k))} toX={poolX(idle0[k])} p={ease(f,20+i*55,75+i*55)}/>)}{n===3&&<Txt x="1690" y="706" size={27} fill={C.redDark} anchor="middle">取最大项</Txt>}</g>;
 }
 if(id==='evict'){
  const pick=ease(f,18,80);const gone=ease(f,90,140);const inserted=ease(f,150,210);
  return <g data-model-state={gone>.99?'first-evicted':'first-existence-check'}><Headline title="选中 C，腾出位置给 I" note="已有候选中的最旧者；A90仍未入池"/><KeyRow selected={['C']} removed={gone>.99?['C']:[]}/><g opacity={gone<1?1:0}><rect x={X(2)-4} y="344" width="176" height="155" rx="20" fill={C.bg} opacity={gone}/></g>{inserted>0&&<KeyCard name="I" age="0" x={X(2)} opacity={inserted}/>}<Pool entries={gone>.99?retained:first} selected={gone<1?'C':''}/><g opacity={pick}><Badge x="1500" y="575" w="250" text="C 存在 ✓"/></g><Txt x="220" y="824" size={30} fill={C.redDark} opacity={ease(f,second,second+25)}>A 保留</Txt><Txt x="1745" y="824" size={29} fill={C.muted} anchor="end">D / E 候选保留</Txt></g>;
 }
 if(id==='retained'){
  const fresh=['F','G','H'];const entries=combined.filter((e:Entry)=>retained.some((r:Entry)=>r.key===e.key)||ease(f,20+fresh.indexOf(e.key)*60,80+fresh.indexOf(e.key)*60)>.99);
  return <g data-model-state="second-populating-with-retained-DE"><Headline title="再要空间：补入新样本，保留旧候选" note="连续两轮示例：同一粗粒度时钟，期间没有额外读取"/><KeyRow names={afterFirst} ages={{...idle0,I:0}} selected={['F','G','H']} dim/><Pressure name="J"/><Pool entries={entries} fresh={fresh} selected="D"/>{fresh.map((k,i)=><Flying key={k} name={k} score={idle0[k]} fromX={X(afterFirst.indexOf(k))} toX={poolX(idle0[k])} p={ease(f,20+i*60,80+i*60)}/>)}</g>;
 }
 if(id==='reuse'){
  const gone=ease(f,second+5,second+50);return <g data-model-state={gone>.99?'second-evicted':'retained-D-selected'}><Headline title="这次选 D：它来自上轮保留" note="本轮新样本 F40 / G30 / H20，都没有旧候选 D60 更大"/><KeyRow names={gone>.99?afterSecond:afterFirst} ages={{...idle0,I:0,J:0}} selected={gone>.99?['J']:['D']}/><Pool entries={gone>.99?combined.filter((e:Entry)=>e.key!=='D'):combined} fresh={['F','G','H']} selected={gone>.99?'':'D'}/><Badge x="1490" y="576" w="270" text={gone>.99?'D 已删，J 写入':'D 存在 → 选中'}/></g>;
 }
 if(id==='ghost'){
  const check=ease(f,second,second+45);const entries=(states['second-evicted'] as any).pool as Entry[];return <g data-model-state={check>.99?'ghost-skipped-next-F':'ghost-before-existence-check'}><Headline title="另一个条件：旧池项还在，键已删除" note="应用先删E → K用完空位 → 后续写L仍需腾空间"/><g><KeyCard name="E" age="50" x="360" y="349" exists={false}/><Txt x="640" y="405" size={33}>填池后检查：E 是否仍存在？</Txt><Txt x="640" y="468" size={35} fill={C.redDark} opacity={check}>{check>.99?'不存在 → 跳过旧记录，继续找 F':'检查候选对应的真实键'}</Txt></g><Pool entries={check>.99?entries.filter(e=>e.key!=='E'):entries} selected={check>.99?'F':'E'} ghost={check>.99?'':'E'} showMini={false}/><Txt x="130" y="850" size={26} fill={C.muted}>后续新样本 I / J / K 分数均为0；这里放大填池后的候选检查</Txt></g>;
 }
 if(id==='tune'){
  const q=ease(f,second,second+35);return <g data-model-state="reset-and-compare-sample-counts"><Headline title="采样更多：机会与成本一起增加" note="回到第一次淘汰前；两组预设样本，不是命中率测量"/><g><rect x="150" y="330" width="705" height="420" rx="24" fill={C.surface} stroke={C.edge} strokeWidth="2"/><rect x="1035" y="330" width="730" height="420" rx="24" fill={C.surface} stroke={C.edge} strokeWidth="2"/><Txt x="502" y="392" size={36} anchor="middle">3个样本</Txt><Txt x="1400" y="392" size={36} anchor="middle">5个样本</Txt>{['C','D','E'].map((k,i)=><KeyCard key={k} name={k} age={idle0[k]} x={215+i*205} y={440} selected={k==='C'}/>)}{['A','C','D','E','H'].map((k,i)=><g key={k}><rect x={1080+i*128} y="455" width="112" height="132" rx="14" fill={k==='A'?C.redSoft:C.bg} stroke={k==='A'?C.red:C.edge} strokeWidth={k==='A'?3:2}/><Txt x={1136+i*128} y="505" size={38} anchor="middle" mono>{k}</Txt><Txt x={1136+i*128} y="555" size={28} anchor="middle">{idle0[k]}</Txt></g>)}<Txt x="502" y="686" size={34} anchor="middle" fill={C.redDark}>这组只见到 C70</Txt><Txt x="1400" y="686" size={34} anchor="middle" fill={C.redDark}>另一组见到了 A90</Txt><Txt x="955" y="841" size={34} anchor="middle" fill={C.muted} opacity={q}>检查更多样本要付出 CPU；不保证任何负载都提高命中率</Txt></g></g>;
 }
 if(id==='recap'){
  const labels=['访问时钟','随机抽样','保留候选','检查存在','删除腾空间'];return <g data-model-state="causal-summary"><Headline title="近似 LRU：优先选择已见候选中的旧键" note="有限维护成本；每次选择都不等于精确全局排名"/>{labels.map((t,i)=><g key={t} opacity={ease(f,10+i*28,35+i*28)}><rect x={130+i*340} y="375" width="290" height="135" rx="22" fill={C.surface} stroke={i===2?C.red:C.edge} strokeWidth={i===2?4:2}/><Txt x={275+i*340} y="454" size={35} anchor="middle" fill={i===2?C.redDark:C.text}>{t}</Txt>{i<4&&<path d={`M${430+i*340} 442H${457+i*340}l-10 -10m10 10l-10 10`} stroke={C.red} strokeWidth="4" fill="none"/>}</g>)}<g opacity={ease(f,second,second+35)}><Txt x="955" y="681" size={45} anchor="middle" fill={C.redDark}>A最旧，却可以仍然保留</Txt><Txt x="955" y="833" size={34} anchor="middle">IT小村 · 原创</Txt></g></g>;
 }
 return null;
}
function subtitleLines(text:string){
 const lines:string[]=[];let line='';let width=0;for(const ch of text){const next=/[A-Za-z0-9]/.test(ch)?0.6:1;if(width+next>36&&line){lines.push(line);line='';width=0;}line+=ch;width+=next;}if(line)lines.push(line);return lines;
}
export function Main({hideSubtitles=false,showSubtitles=true}:any={}){
 const frame=useCurrentFrame();const shot=SHOTS.find(s=>frame>=s.from&&frame<s.from+s.durationInFrames)??SHOTS[SHOTS.length-1];const local=frame-shot.from;
 const subtitle=(shot.subtitles??[]).find((s:any)=>local>=s.from&&local<=s.to)?.text??'';
 const chapter={memory:'内存与访问顺序',sampling:'抽样与候选池',retained:'跨轮保留与检查',boundary:'近似的取舍'}[shot.chapterId]??'';
 const mute=hideSubtitles||!showSubtitles||(typeof window!=='undefined'&&new URLSearchParams(window.location.search).has('noSubtitles'));
 return <AbsoluteFill style={{backgroundColor:C.bg,color:C.text,fontFamily:FONT}}>
  {__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
  <svg width="1920" height="1080" viewBox="0 0 1920 1080" data-frame={frame} data-shot={shot.id}>
   <RedisBackdrop/><RedisHeader ep={52} title="近似 LRU" chapter={chapter}/><Scene shot={shot} f={local}/>
   {!mute&&subtitle&&<g data-subtitle="true"><rect x="120" y="913" width="1680" height="133" rx="18" fill={C.surface} stroke={C.edge} strokeWidth="1.5"/>{subtitleLines(subtitle).map((line,i,ls)=><text key={i} x="960" y={ls.length===1?994:971+i*48} textAnchor="middle" fontFamily={FONT} fontSize="39" fontWeight="600" fill={C.text}>{line}</text>)}</g>}
  </svg>
 </AbsoluteFill>;
}
