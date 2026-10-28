import React from 'react';
import {LeetcodeBackdrop,LeetcodeHeader} from '../../../../_shared/leetcode-video/Frame';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
import {event,INPUT,Motion,playback,shotMotion,shots,still} from '../data';
declare const __HAS_VOICE_AUDIO__:boolean;
const ID_COLOR:Record<number,string>={1:C.blue,2:C.gold,3:C.teal};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const smooth=(p:number)=>p*p*(3-2*p);
const ink=(value:number)=>ID_COLOR[value]??C.text;
const Text=({x,y,children,size=34,fill=C.text,anchor='start',weight=500,...other}:any)=><text x={x} y={y} fontFamily={FONT} fontSize={size} fill={fill} textAnchor={anchor} fontWeight={weight} {...other}>{children}</text>;
const Card=({value,x,y,scale=1,opacity=1,outline=false}:any)=><g transform={`translate(${x},${y}) scale(${scale})`} opacity={opacity} data-card-id={outline?undefined:value}>
 <rect width={150} height={130} rx={19} fill={outline?'none':C.surface} stroke={outline?C.edge:ink(value)} strokeWidth={outline?2:4}/>
 {!outline&&<><rect x={18} y={17} width={8} height={95} rx={4} fill={ink(value)}/><Text x={84} y={91} size={75} fill={ink(value)} anchor="middle" weight={750}>{value}</Text></>}
</g>;
const MiniRow=({row,x,y,scale=.57,opacity=1}:any)=><g opacity={opacity} data-output-copy="true">{row.map((value:number,i:number)=><Card key={i} value={value} x={x+i*110*scale/.57} y={y} scale={scale}/>)}</g>;
const chapterList=[['problem','题目目标'],['derive','怎样入手'],['walk','选择与撤销'],['code','写成程序']];
const Header=({shot}:any)=><foreignObject x={0} y={0} width={1920} height={150}><LeetcodeHeader slug="permutations" detail={<span style={{display:'inline-flex',gap:55}}>{chapterList.map(([id,title])=><span key={id} style={{color:shot.chapterId===id?C.gold:C.muted,fontWeight:shot.chapterId===id?750:450}}>{title}</span>)}</span>}/></foreignObject>;
const titles:Record<string,string>={
 '01':'同一组数字，排出所有顺序','02':'每张恰好一次，所有顺序都要','03':'每一位，尝试还没用过的数字','04':'怎样从一个答案，走向下一个？','05':'从空排列出发','06':'逐个检查，填满三个位置','07':'先存副本，再撤销','08':'这一位试完，退回上一个分叉','09':'撤销以后，这张卡又能用了','10':'换一个开头，继续同样的选择','11':'最后一个开头，也要试完','12':'每种顺序，都有自己的选择路径','13':'把选择与恢复写进程序','14':'六种顺序，全部保留'};
const pos=(value:number,path:number[])=>{const index=path.indexOf(value);return index<0?{x:250+(value-1)*230,y:350}:{x:250+index*230,y:610};};
const explanation=(motion:Motion)=>{
 const e=motion.progress>=1?motion.next:motion.previous;const n=motion.next;
 if(n.action==='choose')return motion.moving?`把 ${n.candidate} 放进第 ${n.path.length} 位`:n.path.length===INPUT.length?'已填满，下一步保存副本':`${n.candidate} 已在第 ${n.path.length} 位，继续下一位`;
 if(n.action==='unchoose')return motion.moving?`撤销 ${n.candidate}，回到可选择的位置`:`${n.candidate} 已恢复未用，可以在后面的分支再选`;
 if(n.action==='save-copy')return motion.moving?'排满了，先复制进答案列表':`已保存第 ${n.answers.length} 份副本，工作卡还在原位`;
 if(n.action==='skip-used')return`${n.candidate} 在当前排列中已经使用 → 跳过`;
 if(n.action==='check')return`检查候选 ${n.candidate}：${e.used[(n.candidate??1)-1]?'当前已用':'当前未用'}`;
 if(n.action==='done')return'工作排列已清空，六份答案副本仍保留';
 return'每次只选当前未用的数字';
};
const Board=({motion,note,retrospect=false}:any)=>{
 const p=smooth(motion.progress);const old=motion.previous;const next=motion.next;
 const state=motion.progress>=1?next:old;const answers=state.answers;
 const saveMotion=next.action==='save-copy'&&motion.moving;
 return <g data-observed-event={next.index} data-observed-action={next.action}>
  <Text x={250} y={310} size={28} fill={C.muted}>可选数字 · 原题输入 [1,2,3]</Text>
  {INPUT.map((value:number,i:number)=><g key={`pool-${value}`}><Card value={value} x={250+i*230} y={350} outline/>{state.used[i]&&<Text x={325+i*230} y={425} size={23} fill={C.muted} anchor="middle">在第 {state.path.indexOf(value)+1} 位</Text>}</g>)}
  <Text x={250} y={831} size={28} fill={C.muted}>正在尝试的排列</Text>
  {[0,1,2].map(i=><g key={`slot-${i}`}><rect x={250+i*230} y={610} width={150} height={130} rx={19} fill="none" stroke={C.edge} strokeWidth={2} strokeDasharray="8 9"/><Text x={325+i*230} y={792} size={24} anchor="middle" fill={C.muted}>第 {i+1} 位</Text></g>)}
  {INPUT.map((value:number)=>{const a=pos(value,old.path),b=pos(value,next.path);return <Card key={`active-${value}`} value={value} x={mix(a.x,b.x,p)} y={mix(a.y,b.y,p)}/>;})}
  {next.action==='skip-used'&&<g><rect x={230+(next.candidate!-1)*230} y={334} width={190} height={162} rx={23} fill="none" stroke={C.red} strokeWidth={4}/><Text x={325+(next.candidate!-1)*230} y={525} fill={C.red} size={26} anchor="middle">当前已用 · 跳过</Text></g>}
  <rect x={1215} y={300} width={585} height={510} rx={26} fill={C.surface} stroke={C.edge} strokeWidth={2}/>
  <Text x={1260} y={355} size={27} fill={C.teal}>已保存的答案副本</Text><Text x={1750} y={355} size={27} anchor="end">{answers.length} / 6</Text>
  {answers.slice(-2).map((row:number[],i:number)=>{const shrinking=saveMotion&&answers.length>=2;const y=shrinking?(i===0?430:mix(560,430,p)):430+i*130;return <MiniRow key={row.join(',')} row={row} x={1320} y={y} opacity={shrinking&&i===0?1-p:1}/>;})}
  {answers.length>2&&<Text x={1260} y={760} size={24} fill={C.muted}>前 {answers.length-2} 份已保留，继续找下一种</Text>}
  {saveMotion&&<g data-output-copy="in-flight">{next.path.map((value:number,i:number)=><Card key={i} value={value} x={mix(250+i*230,1320+i*110,p)} y={mix(610,next.answers.length<=1?430:560,p)} scale={mix(1,.57,p)}/>)}</g>}
  <Text x={250} y={870} size={32} fill={retrospect?C.gold:next.action==='skip-used'?C.red:C.text}>{note??explanation(motion)}</Text>
  {retrospect&&<Text x={250} y={916} size={27} fill={C.muted}>第三位的既有检查：1 已用　2 已用　3 已试过</Text>}
 </g>;
};
const Results=({coverage=false}:any)=><g>
 <Text x={960} y={310} size={31} anchor="middle" fill={C.muted}>{coverage?'先看第一个不同的位置，每条选择各有结果':'返回全部六项 · 每一项都是独立列表'}</Text>
 {[1,2,3].map((value,i)=><g key={value}>
  {coverage&&<><Text x={390+i*560} y={390} size={40} fill={ink(value)} anchor="middle">{value} 开头</Text><path d={`M ${390+i*560} 415 V 445 M ${330+i*560} 445 H ${450+i*560}`} fill="none" stroke={ink(value)} strokeWidth={3}/></>}
  {event(82).answers.slice(i*2,i*2+2).map((row:number[],j:number)=><MiniRow key={j} row={row} x={260+i*560} y={coverage?480+j*175:400+j*210} scale={.66}/>)}
 </g>)}
 <Text x={960} y={880} size={35} fill={C.teal} anchor="middle">全部 6 种 · 不重复 · 输出先后不限</Text>
</g>;
const Intro=({shot,frame}:any)=>{
 const second=shot.cueFrames?.sentences?.[1]??shot.durationInFrames/2;
 if(shot.id==='01')return <>
  <Text x={960} y={305} size={34} fill={C.muted} anchor="middle">输入 [1,2,3]　→　把三个数字排成不同顺序</Text>
  {[1,2,3].map((v,i)=><Card key={v} value={v} x={600+i*240} y={390}/>)}
  <Text x={960} y={635} size={42} anchor="middle">每张都要用，每张只用一次</Text>
  {[0,1,2].map(i=><g key={i}><rect x={600+i*240} y={720} width={150} height={100} rx={17} fill="none" stroke={C.edge} strokeDasharray="7 8"/><Text x={675+i*240} y={780} size={26} anchor="middle" fill={C.muted}>第{i+1}位</Text></g>)}
 </>;
 if(shot.id==='02')return <>
  <Text x={220} y={335} size={28} fill={C.muted}>合法顺序</Text><MiniRow row={[1,2,3]} x={230} y={395} scale={.8}/><MiniRow row={[1,3,2]} x={230} y={600} scale={.8}/>
  <Text x={1040} y={335} size={28} fill={C.red}>不合法的尝试</Text><MiniRow row={[1,1,2]} x={1040} y={395} scale={.8}/>
  <Text x={1040} y={580} size={33} fill={C.red}>重复了 1，漏掉了 3</Text>
  {frame>=second&&<><Text x={1040} y={710} size={37} fill={C.teal}>返回全部排列的列表</Text><Text x={1040} y={770} size={30} fill={C.muted}>共 6 项 · 输出顺序不限</Text></>}
 </>;
 if(shot.id==='03')return <>
  <Text x={120} y={275} size={26} fill={C.gold}>思路分析</Text>
  <Text x={960} y={335} size={31} anchor="middle" fill={C.muted}>第一位的三个入口都需要尝试</Text>
  {[1,2,3].map((v,i)=><g key={v}><Card value={v} x={540+i*320} y={400} scale={.85}/><Text x={604+i*320} y={565} size={28} anchor="middle" fill={i===0?C.text:C.muted}>{v} 开头</Text></g>)}
  {frame>=second&&<><path d="M604 590 V625 M460 625 H750 M460 625 V675 M750 625 V675" stroke={C.edge} strokeWidth={4} fill="none"/><Text x={460} y={735} size={45} fill={C.gold} anchor="middle">2</Text><Text x={750} y={735} size={45} fill={C.teal} anchor="middle">3</Text><Text x={1120} y={695} size={35} fill={C.red}>1 已在前面 → 不再选</Text><Text x={1120} y={755} size={30} fill={C.muted}>记住当前使用情况</Text></>}
 </>;
 // Analysis draws from recorded snapshots, then explicitly resets in shot 05.
 const phase=frame<second?playback(12,14,Math.min(1,frame/Math.max(1,second-20))):still(14);
 return <><Text x={120} y={275} size={26} fill={C.gold}>思路分析{frame>=second?' · 回溯':''}</Text><Board motion={phase} note={frame>=second?'选择 → 继续 → 排满保存 → 撤销再试':'要尝试别的顺序，先撤销最后的选择'}/>{frame>shot.durationInFrames-55&&<g><rect x={210} y={840} width={1540} height={86} fill={C.bg}/><Text x={960} y={896} anchor="middle" fill={C.gold} size={35}>清空分析标记，下面从空排列正式开始</Text></g>}</>;
};
const Implementation=({shot,frame}:any)=>{
 const second=shot.cueFrames?.sentences?.[1]??shot.durationInFrames/2;
 if(frame<second)return <>
  <Text x={180} y={325} size={29} fill={C.muted}>选择以后，必须成对恢复</Text>
  {['used[i] = True','path.append(nums[i])','dfs()','path.pop()','used[i] = False'].map((line,i)=><text key={i} x={210} y={410+i*82} fontFamily={MONO} fontSize={42} fill={i>=3?C.teal:C.gold} xmlSpace="preserve">{line}</text>)}
  <Text x={1060} y={400} size={32} fill={C.teal}>撤销 3 后的真实状态</Text><MiniRow row={event(14).path} x={1060} y={470} scale={.8}/><Text x={1060} y={660} size={31}>当前排列 [1,2]</Text><Text x={1060} y={720} size={31}>3 恢复为未用</Text><Text x={1060} y={780} size={28} fill={C.muted}>已保存的 [1,2,3] 不变</Text>
 </>;
 return <>
  <Text x={960} y={370} size={43} anchor="middle">n! 份答案　×　每份 n 个数字</Text>
  <Text x={960} y={495} size={60} anchor="middle" fill={C.gold}>时间 O(n · n!)</Text>
  <Text x={960} y={640} size={44} anchor="middle" fill={C.teal}>额外工作空间 O(n)</Text>
  <Text x={960} y={715} size={31} anchor="middle" fill={C.muted}>当前排列、使用记录、递归深度各最多 n</Text>
  <Text x={960} y={795} size={30} anchor="middle" fill={C.muted}>不含输出 · 全部结果另占 O(n · n!)</Text>
  <Text x={960} y={870} size={28} anchor="middle" fill={C.muted}>原题 1 ≤ n ≤ 6，最多 720 种排列</Text>
 </>;
};
const Subtitle=({shot,frame}:any)=>{
 const sub=shot.subtitles?.find((s:any)=>frame>=s.from&&frame<=(s.to??s.from+s.duration-1));if(!sub)return null;
 const text=sub.text;let lines:string[]=[];let remaining=text;while(remaining.length>40){let cut=40;for(let i=40;i>=27;i--)if('，。；'.includes(remaining[i])){cut=i+1;break;}lines.push(remaining.slice(0,cut));remaining=remaining.slice(cut);}if(remaining)lines.push(remaining);
 return <g data-subtitle="true"><rect x={80} y={953} width={1760} height={lines.length>1?104:75} rx={15} fill={C.bg} opacity={.96}/>{lines.map((line,i)=><Text key={i} x={960} y={990+i*43} size={31} anchor="middle" fill={C.text}>{line}</Text>)}</g>;
};
const Scene=({shot,hideSubtitles}:any)=>{
 const frame=useCurrentFrame();const second=shot.cueFrames?.sentences?.[1]??shot.durationInFrames/2;
 const code=shot.codeCardFrom!==undefined&&frame>=shot.codeCardFrom;
 return <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{background:C.bg}}>
  <rect width={1920} height={1080} fill={C.bg}/>
  {code?<CodeCard/>:<>
   <Header shot={shot}/><Text x={120} y={200} size={51} weight={760}>{titles[shot.id]}</Text>
   {Number(shot.id)<=4?<Intro shot={shot} frame={frame}/>:Number(shot.id)<=11?
    <Board motion={shotMotion(shot,frame)} retrospect={shot.id==='08'&&frame<second} note={shot.id==='08'&&frame<second?'第三位没有其他候选，下一步再撤销第二位':undefined}/>:shot.id==='12'?<Results coverage/>:shot.id==='13'?<Implementation shot={shot} frame={frame}/>:<Results/>}
   {!hideSubtitles&&<Subtitle shot={shot} frame={frame}/>}
  </>}
 </svg>;
};
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=><AbsoluteFill style={{background:C.bg}}><LeetcodeBackdrop/>
 {__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(shot=><Sequence key={shot.id} from={shot.from} durationInFrames={shot.durationInFrames}><Scene shot={shot} hideSubtitles={hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
