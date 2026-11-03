import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {PuzzleCanvas, PuzzleHeader} from '../../../../../_shared/puzzles-video/Frame';
import {C, FONT, MONO} from './theme';
import {Shot, shots} from './data';
import {EXAMPLE_DAYS, dateLabel, allDifferent, P22, P23, percent, tween, clamp} from './model';
declare const __HAS_VOICE_AUDIO__: boolean;

type TextProps = {x:number; y:number; children:React.ReactNode; size?:number; color?:string; anchor?:'start'|'middle'|'end'; alpha?:number; weight?:number; width?:number; mono?:boolean; [key:string]:any};
const T = ({x,y,children,size=32,color=C.text,anchor='start',alpha=1,weight=550,width,mono=false,...rest}:TextProps) => <text data-text data-max-width={width} x={x} y={y} fontSize={size} fill={color} fontFamily={mono?MONO:FONT} fontWeight={weight} textAnchor={anchor} opacity={alpha} {...rest}>{children}</text>;
const Box = ({x,y,w,h,color=C.edge,alpha=1,children,...rest}:any) => <g opacity={alpha} {...rest}><rect x={x} y={y} width={w} height={h} rx={22} fill={C.surface} stroke={color} strokeWidth={2}/>{children}</g>;
const Head = ({title,sub}:any) => <PuzzleHeader number="P07" kicker="生日悖论" title={title} sub={sub}/>;
const Note = ({children,color=C.muted,alpha=1}:any) => <T x={960} y={879} size={29} color={color} anchor="middle" alpha={alpha} width={1700} data-note>{children}</T>;
const Fraction = ({x,y,numerator=364,denominator=365,color=C.coral,scale=1,alpha=1,label}:any) => <g transform={`translate(${x} ${y}) scale(${scale})`} opacity={alpha} data-fraction={`${numerator}/${denominator}`}>
  {label&&<T x={0} y={-60} size={25} anchor="middle" color={C.muted}>{label}</T>}
  <T x={0} y={-10} size={47} anchor="middle" color={color} mono>{numerator}</T>
  <path d="M-65 10H65" stroke={color} strokeWidth={3}/><T x={0} y={65} size={47} anchor="middle" color={color} mono>{denominator}</T>
</g>;

/** The same numbered person always identifies the same fixed birthday record. */
const Person = ({x,y,id,color=C.violet,scale=1,alpha=1,date,unknown=false,focus=false,personLabel,birthdayAlpha=1}:any) => <g transform={`translate(${x} ${y}) scale(${scale})`} opacity={alpha} data-person={id} data-birthday={date??'not-revealed'}>
  {focus&&<rect x={-88} y={-64} width={176} height={218} rx={24} fill={C.coral} fillOpacity={.075} stroke={C.coral} strokeWidth={2}/>}
  <circle cx={0} cy={-18} r={28} fill={C.surface} stroke={color} strokeWidth={3}/>
  <path d="M-52 80V59C-52 25 52 25 52 59V80Z" fill={C.surface} stroke={color} strokeWidth={3}/>
  <T x={0} y={-9} size={24} anchor="middle" color={color} mono weight={750}>{id}</T>
  <T x={0} y={119} size={25} anchor="middle" color={color}>{personLabel??`${id}号`}</T>
  {(date||unknown)&&<g opacity={birthdayAlpha}><rect x={-95} y={145} width={190} height={59} rx={14} fill={C.bg} stroke={date?color:C.edge} strokeWidth={2}/><T x={0} y={185} size={28} anchor="middle" color={date?color:C.muted}>{date??'尚未查看'}</T></g>}
</g>;

const groupPosition = (index:number) => ({x:260+(index%8)*195,y:367+Math.floor(index/8)*160});
const Group23 = ({highlight=[4,17],me=false,alpha=1}:any) => <g data-people-count={23} opacity={alpha}>{Array.from({length:23},(_,i)=>{
  const p=groupPosition(i),focus=highlight.includes(i+1);return <Person key={i} {...p} id={i+1} scale={.7} color={me&&i===0?C.teal:focus?C.coral:C.violet} personLabel={me&&i===0?'1号：你':undefined} alpha={focus||!me||i===0?1:.4}/>;
})}</g>;

/** Exactly 365 cells. Coral cells are previously occupied dates in the conditional example. */
const Calendar = ({x=1170,y=369,occupied=0,alpha=1,options=true,current=0}:any) => {
  const occupiedDays = EXAMPLE_DAYS.slice(0,occupied);
  return <g data-calendar-count={365} data-occupied-count={occupied} data-allowed-count={365-occupied} transform={`translate(${x} ${y})`} opacity={alpha}>
    <T x={264} y={-30} size={27} anchor="middle" color={C.muted}>365个日期 · 每格一天</T>
    {Array.from({length:365},(_,i)=>{const blocked=occupiedDays.includes(i as never),isCurrent=current>0&&i===EXAMPLE_DAYS[current-1];return <rect key={i} data-day={i} data-occupied={blocked?'true':'false'} x={(i%25)*22} y={Math.floor(i/25)*22} width={16} height={16} rx={3} fill={blocked?C.coral:options?C.teal:C.violet} opacity={blocked?1:options?.56:.23} stroke={isCurrent?C.text:'none'} strokeWidth={2}/>;})}
    <T x={0} y={376} size={27} color={C.coral} width={260}>会重复：{occupied}天</T>
    <T x={540} y={376} size={27} color={C.teal} anchor="end" width={260}>不重复：{365-occupied}天</T>
  </g>;
};

const ConditionalBanner = ({count,current}:any) => <g data-conditional-example data-previous-distinct={count} data-inspecting-person={current}>
  <rect x={120} y={270} width={1680} height={48} rx={12} fill={C.violet} fillOpacity={.09}/>
  <T x={150} y={304} size={24} color={C.violet}>此前均不同 · 条件示例</T>
  <T x={1770} y={304} size={24} color={C.muted} anchor="end">{count===0?'第1人没有需要避开的日期':`查看${current}号前，已有${count}个不同日期`}</T>
</g>;

const DetailedPeople = ({stage,revealed,current,showFormula=false}:any) => <g data-detail-stage={stage}>
  {[1,2,3].map((id)=><Person key={id} x={260+(id-1)*300} y={435} id={id} color={id===current?C.coral:id<=revealed?C.teal:C.muted} date={id<=revealed?dateLabel(EXAMPLE_DAYS[id-1]):undefined} unknown={id===current&&id>revealed} alpha={id<=Math.max(current,revealed)?1:.28} focus={id===current}/>) }
  <T x={560} y={744} size={25} anchor="middle" color={C.muted} width={840}>生日记录逐个揭示，不是人主动挑选日期</T>
  {showFormula&&<T x={560} y={810} size={30} anchor="middle" color={C.teal} width={840}>这几个具体日期只是示例，计算与日期名称无关</T>}
</g>;

const DistinctStage = ({s,f,n}: {s:Shot;f:number;n:number}) => {
  const a=s.voice?.[0]?.localStart??10,b=s.voice?.[0]?.localEnd??s.durationInFrames*.45,c=s.voice?.[1]?.localStart??s.durationInFrames*.53,e=s.voice?.[1]?.localEnd??s.durationInFrames-20;
  const current=n-4,previous=current-1,revealAt=n===5?c+(e-c)*.4:a+(b-a)*.76,revealed=f>=revealAt?current:previous;
  const titles=['先看第1人：生日在哪天都可以','再看第2人：只有1天会重复','前两人不同，第3人就要避开2天'];
  return <><Head title={titles[n-5]} sub="只沿着‘生日全部不同’的条件计算；具体月日是固定的教学示例"/>
    <ConditionalBanner count={previous} current={current}/><DetailedPeople stage={current} current={current} revealed={revealed}/>
    <Calendar occupied={previous} current={revealed===current?current:0}/>
    {n===5?<g opacity={tween(f,c+8,c+35)}><T x={1402} y={814} size={36} color={C.teal} anchor="middle">365 / 365 = 1</T></g>:<g opacity={tween(f,c+4,c+25)}><T x={1175} y={812} size={27} color={C.muted}>{n===6?'第2人不重复':'前两人不同后，第3人不重复'}</T><T x={1745} y={812} size={37} color={C.coral} anchor="end" mono>{365-previous} / 365</T></g>}
    <Note>{n===5?'第一个人的365种生日，都符合‘目前没有重复’':`只计算这一关不重复的机会：365天中，排除${previous}天`}</Note>
  </>;
};

const Complement = ({numeric=false,reveal=false,progress=1}:any) => {
  const split=numeric?allDifferent(23):.5,x=210,y=420,w=1500,h=230,left=w*split;
  return <g data-complement data-all-different={numeric?allDifferent(23):'unknown'} data-collision={numeric?P23:'unknown'}>
    <T x={960} y={348} size={32} anchor="middle" color={C.muted}>所有可能，一共100%</T>
    <rect x={x} y={y} width={w} height={h} rx={20} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
    <path d={`M${x+20} ${y}H${x+left}V${y+h}H${x+20}Q${x} ${y+h} ${x} ${y+h-20}V${y+20}Q${x} ${y} ${x+20} ${y}Z`} fill={C.teal} fillOpacity={.15}/>
    <path d={`M${x+left} ${y}H${x+w-20}Q${x+w} ${y} ${x+w} ${y+20}V${y+h-20}Q${x+w} ${y+h} ${x+w-20} ${y+h}H${x+left}Z`} fill={C.coral} fillOpacity={reveal?.23:.07}/>
    <path d={`M${x+left} ${y}V${y+h}`} stroke={C.edge} strokeWidth={2}/>
    <T x={x+left/2} y={y+74} size={39} color={C.teal} anchor="middle">全部不同</T>
    <T x={x+left+(w-left)/2} y={y+74} size={39} color={C.coral} anchor="middle">至少两人相同</T>
    {numeric&&<><T x={x+left/2} y={y+170} size={59} color={C.teal} anchor="middle" mono alpha={progress}>≈ {percent(allDifferent(23))}</T><T x={x+left+(w-left)/2} y={y+170} size={59} color={C.coral} anchor="middle" mono alpha={reveal?1:0}>≈ {percent(P23)}</T></>}
    {!numeric&&<><T x={x+left/2} y={y+151} size={29} color={C.muted} anchor="middle">先算这一边</T><T x={x+left+(w-left)/2} y={y+151} size={29} color={C.muted} anchor="middle">再用100%减掉左边</T></>}
  </g>;
};

const Scene = ({s,f}:{s:Shot;f:number}) => {
  const n=parseInt(s.id,10),d=s.durationInFrames,a=s.voice?.[0]?.localStart??10,b=s.voice?.[0]?.localEnd??d*.45,c=s.voice?.[1]?.localStart??d*.53,e=s.voice?.[1]?.localEnd??d-20;
  const late=tween(f,c+4,c+26);
  if(n===1)return <><Head title="只有23人，同生日的概率就能过半？" sub="问题：至少任意两人同生日，要多少人才有超过50%的机会？"/>
    <T x={960} y={296} size={24} color={C.muted} anchor="middle">题意示例 · 只显示一种可能，尚未计算概率</T>
    <Group23 highlight={f<c?[]:[4,17]}/><T x={960} y={810} size={32} anchor="middle" color={f<c?C.violet:C.coral}>{f<c?'23个人 · 一年有365天':'同生日：只比月日，不比较年份'}</T>
    {f>=c&&<><T x={570} y={852} size={25} color={C.muted} anchor="middle">4号：5月12日</T><T x={1350} y={852} size={25} color={C.muted} anchor="middle">17号：5月12日</T></>}
  </>;
  if(n===2)return <><Head title="先说清楚：按什么条件计算？" sub="理想模型 · 一年365天 · 忽略闰日"/>
    <Person x={350} y={477} id={1} scale={1.25} color={C.violet}/><Person x={690} y={477} id={2} scale={1.25} color={C.violet}/>
    <Calendar x={1140} y={353} occupied={0} options={false}/>
    <T x={520} y={735} size={33} anchor="middle" color={C.violet}>每人都可能落在任意一天</T>
    <T x={1410} y={808} size={33} anchor="middle" color={C.violet} alpha={late}>每个日期的机会都相同</T>
    <Note alpha={late}>彼此独立：一个人的生日，不改变另一个人的生日分布</Note>
  </>;
  if(n===3)return <><Head title={f<c?'只找与你同生日，比较范围很小':'题目允许任意两人，不必有你'} sub="两种不同的问题：‘有人和我相同’与‘任何两个人相同’"/>
    <Group23 highlight={f<c?[1,4]:[4,17]} me/>
    <T x={1030} y={820} size={34} anchor="middle" color={C.coral}>{f<c?'只和‘你’这一个日期比较':'4号与17号同为5月12日，也符合题目'}</T>
    <Note>{f<c?'别人之间的重复，还没有算进来':'不要把‘任意两人’缩成‘有人和我’'}</Note>
  </>;
  if(n===4){const switched=f>=c;return <><Head title={switched?'把所有可能分成两边，就好算了':'直接数重复，会有许多重叠情况'} sub={switched?'全部不同，或至少两人相同：两边没有遗漏，也不会同时发生':'下面只展示两种情况，并不是完整列举'} />
    {!switched?<><Box x={180} y={350} w={730} h={400}><T x={545} y={413} size={32} anchor="middle" color={C.coral}>两个人相同</T>{[1,2,3].map((id)=><Person key={id} x={325+(id-1)*220} y={515} id={id} scale={.7} date={id<3?'5月12日':'9月28日'} color={id<3?C.coral:C.violet}/>)}</Box><Box x={1010} y={350} w={730} h={400}><T x={1375} y={413} size={32} anchor="middle" color={C.coral}>三个人相同</T>{[1,2,3].map((id)=><Person key={id} x={1155+(id-1)*220} y={515} id={id} scale={.7} date="5月12日" color={C.coral}/>)}</Box></>:<Complement/>}
    <Note color={switched?C.coral:C.muted}>{switched?'至少两人相同 = 100% − 全部不同':'换个方向，只追踪‘全部不同’这一种条件'}</Note>
  </>;}
  if(n>=5&&n<=7)return <DistinctStage s={s} f={f} n={n}/>;
  if(n===8){const firstPassed=f>=a+(b-a)*.3,secondPassed=f>=a+(b-a)*.76;return <><Head title="全部不同，要把两关连续通过" sub="第1人的概率是1；接着，第2人不重复，第3人也不重复"/>
    <ConditionalBanner count={2} current={3}/><DetailedPeople stage={3} current={3} revealed={3}/>
    <Box x={1130} y={355} w={640} h={375} color={C.edge}>
      <T x={1450} y={401} size={27} anchor="middle" color={C.muted}>连续通过，不是二选一</T>
      <Fraction x={1280} y={535} numerator={364} label="第2人不重复" color={firstPassed?C.teal:C.muted}/>
      <T x={1448} y={555} size={46} anchor="middle" color={C.coral} alpha={secondPassed?1:.2}>×</T>
      <Fraction x={1617} y={535} numerator={363} label="此前不同后，第3人" color={secondPassed?C.teal:C.muted}/>
      <T x={1450} y={689} size={24} anchor="middle" color={C.muted}>两个分数分别对应这一关的条件</T>
    </Box>
    <g opacity={late}><T x={1420} y={811} size={37} anchor="middle" color={C.coral} mono>364/365 × 363/365</T></g>
    <Note color={C.teal}>两个条件都成立，三个人才会全部不同</Note>
  </>;}
  if(n===9){
    const dateAlpha=1-tween(f,a,a+15),zoomStart=a+18,zoomEnd=a+50,zoom=tween(f,zoomStart,zoomEnd),newPeopleAlpha=tween(f,zoomEnd,zoomEnd+16),holdEnd=a+(b-a)*.72;
    // First establish the fourth person's 362/365 at readable speed. Only the
    // subsequent repetitions are accelerated; all dates keep their identities.
    const count=f<holdEnd?3:f<c?Math.min(22,4+Math.floor(clamp((f-holdEnd)/Math.max(1,c-holdEnd-10))*18)):22;
    return <><Head title="同样的方法，一直算到第23人" sub="前面的人若都不同，新人就要避开所有已占日期"/>
      <ConditionalBanner count={count} current={count+1}/>
      <g data-distinct-example-count={count}>{Array.from({length:23},(_,i)=>{
        const id=i+1,large={x:260+i*300,y:435},small={x:200+(i%6)*150,y:405+Math.floor(i/6)*105},isOld=i<3;
        const x=isOld?large.x+(small.x-large.x)*zoom:small.x,y=isOld?large.y+(small.y-large.y)*zoom:small.y,scale=isOld?1+(.5-1)*zoom:.5;
        return <Person key={id} id={id} x={x} y={y} scale={scale} color={id===count+1?C.coral:id<=count?C.teal:C.muted} alpha={isOld?1:newPeopleAlpha*(id<=count+1?1:.12)} focus={id===count+1} date={isOld?dateLabel(EXAMPLE_DAYS[i]):undefined} birthdayAlpha={dateAlpha}/>;
      })}</g>
      <Calendar occupied={count}/>
      <T x={590} y={825} size={29} anchor="middle" color={C.muted}>{count===3?'先算第4人：365 − 3 = 362天，概率362/365':'重复步骤加快展示；所有已知日期保持不变'}</T>
      <g opacity={late}><T x={1410} y={812} size={40} color={C.coral} anchor="middle" mono>343 / 365</T></g>
      <Note color={f>=c?C.coral:C.muted}>{f>=c?'第23人：365 − 22 = 343个日期不会重复':'第4人避开3天，第5人避开4天，依次继续'}</Note>
    </>;
  }
  if(n===10){const reveal=f>=c+8;return <><Head title="先算全部不同，再得到同生日的机会" sub="365天、均匀且相互独立的理想模型；不是现实出生数据统计"/>
    <T x={960} y={295} size={34} color={C.violet} anchor="middle" mono>364/365 × 363/365 × … × 343/365</T>
    <Complement numeric reveal={reveal} progress={tween(f,a+15,a+(b-a)*.45)}/>
    <T x={960} y={775} size={48} color={C.coral} anchor="middle" mono alpha={late}>100% − 49.27% ≈ 50.73%</T>
    <Note color={C.coral} alpha={late}>23人：至少任意两人同生日的概率，刚刚超过一半</Note>
  </>;}
  if(n===11){const x22=710,x23=1220,base=793,range=460,max=.6,y50=base-range*.5/max;
    return <><Head title="22人还没过半，23人才刚刚跨过" sub="人数增加，已经出现的重复不会消失；同生日的概率不会下降"/>
      <T x={x22} y={340} size={55} color={C.violet} anchor="middle" mono>{percent(P22)}</T><T x={x23} y={340} size={55} color={C.coral} anchor="middle" mono>{percent(P23)}</T>
      <path d={`M330 ${base}H1630`} stroke={C.edge} strokeWidth={3}/>
      <path d={`M330 ${y50}H1630`} stroke={C.teal} strokeWidth={3} strokeDasharray="10 10"/>
      <T x={310} y={y50+10} size={31} color={C.teal} anchor="end" mono>50%</T><T x={310} y={base+10} size={28} color={C.muted} anchor="end" mono>0%</T>
      <rect data-probability-bar="22" data-probability={P22} x={x22-150} y={base-range*P22/max} width={300} height={range*P22/max} rx={15} fill={C.violet} fillOpacity={.3} stroke={C.violet} strokeWidth={3}/>
      <rect data-probability-bar="23" data-probability={P23} x={x23-150} y={base-range*P23/max} width={300} height={range*P23/max} rx={15} fill={C.coral} fillOpacity={.35} stroke={C.coral} strokeWidth={3}/>
      <T x={x22} y={base+49} size={31} anchor="middle" color={C.violet}>22人</T><T x={x23} y={base+49} size={31} anchor="middle" color={C.coral}>23人</T>
      <Note color={C.coral} alpha={late}>最少23人；概率过半，不保证每一组都有人同生日</Note>
    </>;
  }
  throw Error('Unknown birthday-paradox shot '+s.id);
};

const ShotView = ({s,hideSubtitles,auditLayout}: {s:Shot;hideSubtitles:boolean;auditLayout:boolean}) => {
  const f=useCurrentFrame(),ref=useRef<SVGSVGElement>(null),caption=s.subtitles?.find(q=>f>=q.from&&f<(q.to!==undefined?q.to+1:q.from+(q.duration??0)));
  useLayoutEffect(()=>{if(!auditLayout||!ref.current)return;ref.current.querySelectorAll<SVGTextElement>('[data-max-width]').forEach(el=>{
    const limit=Number(el.dataset.maxWidth),box=el.getBBox();if(limit&&box.width>limit+2)console.error('COPYFIT',s.id,f,el.textContent,box.width,limit);
  });},[auditLayout,s.id,f]);
  return <AbsoluteFill data-shot={s.id} data-local-frame={f} style={{background:C.bg,fontFamily:FONT,color:C.text,overflow:'hidden'}}>
    <svg ref={ref} data-audit-scene width={1920} height={1080} viewBox="0 0 1920 1080"><PuzzleCanvas/><Scene s={s} f={f}/><T x={1795} y={83} size={26} color={C.muted} anchor="end">{parseInt(s.id,10)===11?'IT小村 · 原创':'IT小村'}</T></svg>
    {!hideSubtitles&&caption&&<div data-subtitle style={{position:'absolute',left:140,right:140,top:927,minHeight:92,display:'flex',alignItems:'center',justifyContent:'center',fontSize:32,lineHeight:1.5,textAlign:'center',background:C.bg+'F5',padding:'0 15px',borderRadius:14,boxSizing:'border-box'}}>{caption.text}</div>}
  </AbsoluteFill>;
};
export type MainProps = {hideSubtitles?:boolean;showSubtitles?:boolean;auditLayout?:boolean};
export const Main = ({hideSubtitles=false,showSubtitles=true,auditLayout=false}:MainProps) => <AbsoluteFill style={{background:C.bg}}>
  {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
  {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles||!showSubtitles} auditLayout={auditLayout}/></Sequence>)}
</AbsoluteFill>;
