import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots,TEXT} from '../data';
import {C,FONT,MONO} from './theme';
import {CodeCard} from './CodeCard';
import {EpisodeHeader} from './EpisodeHeader';
import {LeetcodeBackdrop} from '../../../../_shared/leetcode-video/Frame';
declare const __HAS_VOICE_AUDIO__:boolean;

const clamp=(p:number)=>Math.max(0,Math.min(1,p));
const ease=(p:number)=>{p=clamp(p);return p*p*(3-2*p);};
const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
const at=(s:Shot,i:number,p:number)=>{
 const start=Number(s.cueFrames?.sentences?.[i]??(i?Math.round(s.durationInFrames*.5):0));
 const end=Number(s.cueFrames?.sentences?.[i+1]??s.durationInFrames-10);
 return start+(end-start)*p;
};
const phase=(s:Shot,f:number,i=0,a=.08,b=.76)=>ease((f-at(s,i,a))/Math.max(1,at(s,i,b)-at(s,i,a)));
const span=(s:Shot,f:number,a=.05,b=.8)=>clamp((f-at(s,0,a))/Math.max(1,at(s,1,b)-at(s,0,a)));
const segment=(p:number,count:number)=>{
 const z=clamp(p)*count,index=Math.min(count-1,Math.floor(z));
 return {index,progress:ease(Math.min(1,(z-index)/.58))};
};
const x=(i:number)=>330+i*170;
const letters=[...TEXT],setLetters=['a','b','c','d','e'];
const T=({x,y,children,size=31,color=C.text,anchor='start',alpha=1,weight=500,mono=false,...rest}:any)=><text x={x} y={y} fill={color} opacity={alpha} fontFamily={mono?MONO:FONT} fontSize={size} fontWeight={weight} textAnchor={anchor} {...rest}>{children}</text>;
const Head=({title,sub,kicker='无重复字符的最长子串',color=C.text}:any)=><g><EpisodeHeader detail={kicker}/><T x={120} y={184} size={52} color={color} weight={760}>{title}</T>{sub&&<T x={120} y={244} size={27} color={C.muted}>{sub}</T>}</g>;
const Note=({children,color=C.muted,alpha=1}:any)=><T x={960} y={918} anchor="middle" size={31} color={color} alpha={alpha}>{children}</T>;
const members=(l:number,r:number)=>Object.fromEntries(setLetters.map(ch=>[ch,l<=r&&TEXT.slice(l,r+1).includes(ch)?1:0]));
type BoardProps={left:number;right:number;best:number;pending?:number;duplicate?:number;duplicateAlpha?:number;membership?:Record<string,number>;showSet?:boolean;showStats?:boolean;showPointers?:boolean;statsAlpha?:number;setAlpha?:number;windowAlpha?:number;windowColor?:string;pendingColor?:string;regionLabel?:string;topPointerY?:number;bestUnderline?:boolean;currentLabel?:string;bestLabel?:string};

const Board=({left,right,best,pending=-1,duplicate=-1,duplicateAlpha=1,membership,showSet=true,showStats=true,showPointers=true,statsAlpha=1,setAlpha=1,windowAlpha=1,windowColor=C.teal,pendingColor,regionLabel='当前窗口',topPointerY=326,bestUnderline=false,currentLabel='当前长度',bestLabel='最长记录'}:BoardProps)=>{
 const empty=right<left,stored=membership??members(Math.ceil(left),Math.floor(right));
 const candidate=pending>=0&&pending<8,pointerRight=candidate?pending:right;
 const inWindow=(i:number)=>empty?0:clamp(i-left+1)*clamp(right-i+1);
 const repeated=candidate&&duplicate>=0&&duplicateAlpha>0;
 return <g data-window-left={left} data-window-right={right} data-pending={pending}>
  {!empty&&<g opacity={windowAlpha}><rect x={x(left)-78} y={388} width={(right-left)*170+156} height={168} rx={18} fill={windowColor+'0E'} stroke={windowColor} strokeWidth={3}/><T x={(x(left)+x(right))/2} y={584} color={windowColor} size={23} anchor="middle">{regionLabel}</T></g>}
  {repeated&&<g opacity={duplicateAlpha}><path d={`M ${x(duplicate)} 399 Q ${(x(duplicate)+x(pending))/2} ${topPointerY>350?355:279} ${x(pending)} 399`} fill="none" stroke={C.red} strokeWidth={3}/><rect x={(x(duplicate)+x(pending))/2-58} y={topPointerY>350?355:308} width={116} height={topPointerY>350?31:36} rx={12} fill={C.bg}/><T x={(x(duplicate)+x(pending))/2} y={topPointerY>350?379:335} color={C.red} size={topPointerY>350?22:24} anchor="middle">同一字符</T></g>}
  {letters.map((ch,i)=>{const active=inWindow(i),red=(i===duplicate||i===pending)&&repeated,pc=i===pending&&candidate,color=red?C.red:pc?(pendingColor??C.blue):active>0?windowColor:C.muted,alpha=active>0||pc?1:.38;return <g key={i} data-char-index={i}>
   <rect x={x(i)-58} y={413} width={116} height={120} rx={13} fill={C.surface} stroke={color} strokeWidth={red||pc?3:1.5} opacity={alpha}/>
   <T x={x(i)} y={490} size={56} color={color} mono anchor="middle" alpha={alpha}>{ch}</T>
   <T x={x(i)} y={620} size={24} color={C.muted} mono anchor="middle">{i}</T>
  </g>})}
  {showPointers&&right>=left&&<g opacity={windowAlpha}><path d={`M ${x(left)-10} 660 L ${x(left)+10} 660 L ${x(left)} 645 Z`} fill={C.gold}/><T x={x(left)} y={693} anchor="middle" size={24} color={C.gold}>左边界</T></g>}
  {showPointers&&pointerRight>=0&&<g><T x={x(pointerRight)} y={topPointerY} anchor="middle" color={candidate?(pendingColor??(repeated?C.red:C.blue)):C.teal} size={24}>{candidate?'待加入':'右边界'}</T><path d={`M ${x(pointerRight)-10} ${topPointerY+13} L ${x(pointerRight)+10} ${topPointerY+13} L ${x(pointerRight)} ${topPointerY+28} Z`} fill={candidate?(pendingColor??(repeated?C.red:C.blue)):C.teal}/></g>}
  {bestUnderline&&<g><path d={`M ${x(2)-58} 638 H ${x(6)+58}`} fill="none" stroke={C.gold} strokeWidth={4}/><T x={1780} y={680} anchor="end" size={23} color={C.gold}>金线：历史最长 cbade</T></g>}
  {showSet&&<g opacity={setAlpha}>
   <rect x={252} y={730} width={1058} height={148} rx={18} fill={C.surface} stroke={C.edge}/>
   <T x={282} y={768} size={24} color={C.muted}>集合 · 无顺序，固定槽仅便于观察</T>
   {setLetters.map((ch,i)=>{const p=stored[ch]??0;return <g key={ch} opacity={p} data-set-member={ch} data-set-opacity={p}>
    <rect x={416+i*150} y={789} width={88} height={66} rx={12} fill={C.teal+'14'} stroke={C.teal} strokeWidth={2}/><T x={460+i*150} y={837} anchor="middle" mono color={C.teal} size={43}>{ch}</T>
   </g>})}
   {!Object.values(stored).some(v=>v>.01)&&<T x={775} y={838} size={30} color={C.muted} anchor="middle">空集合</T>}
  </g>}
  {showStats&&<g>
   <g opacity={statsAlpha}><T x={1460} y={775} size={25} anchor="middle" color={C.muted}>{currentLabel}</T>
   <T x={1460} y={850} size={62} anchor="middle" mono>{empty?0:Math.round(right-left+1)}</T></g>
   <T x={1690} y={775} size={25} anchor="middle" color={C.muted}>{bestLabel}</T>
   <T x={1690} y={850} size={62} anchor="middle" mono color={C.gold}>{best}</T>
  </g>}
 </g>;
};

const remove=(left:number,right:number,best:number,pending:number,p:number):BoardProps=>{
 const fade=clamp(p/.34),move=ease(clamp((p-.34)/.66));
 const membership=members(left,right);membership[TEXT[left]]=1-fade;
 const duplicate=TEXT.indexOf(TEXT[pending],left);
 return {left:mix(left,left+1,move),right,best,pending,duplicate,duplicateAlpha:duplicate===left?1-fade:1,membership,statsAlpha:p<=0||p>=1?1:0};
};
const insert=(left:number,right:number,best:number,p:number,newBest=best):BoardProps=>{
 const add=clamp(p/.32),move=ease(clamp((p-.32)/.68)),membership=members(left,right);
 membership[TEXT[right+1]]=add;
 return {left,right:mix(right,right+1,move),best:p>=1?newBest:best,pending:p>=1?-1:right+1,membership,pendingColor:C.blue,statsAlpha:p<=0||p>=1?1:0};
};
const Action=({text,alpha=1,color=C.gold,left=false}:any)=><g opacity={alpha}><rect x={left?120:1150} y={273} width={640} height={73} rx={14} fill={C.bg} stroke={color+'66'}/><T x={left?440:1470} y={320} size={27} color={color} anchor="middle">{text}</T></g>;
const CodeLine=({children,alpha=1,color=C.gold}:any)=><g opacity={alpha}><rect x={350} y={276} width={1220} height={76} rx={12} fill={C.surface} stroke={C.edge}/><T x={960} y={327} size={35} anchor="middle" mono color={color}>{children}</T></g>;

const Scene=({s,f}:{s:Shot;f:number})=>{
 const t=s.visualType,p=phase(s,f),q=phase(s,f,1);
 if(t==='hook'){
  const selected=phase(s,f,0,.18,.85),unique=phase(s,f,1,.02,.42),longest=phase(s,f,1,.45,.88);
  return <><Head title="找最长、连续、无重复的一段" sub="输入示例：abcbadea · 从原字符串中选出连续片段"/><Board left={0} right={7} best={0} showSet={false} showStats={false} showPointers={false} windowAlpha={0} windowColor={C.text}/><g opacity={selected}><rect x={x(0)-78} y={388} width={2*170+156} height={168} rx={18} fill={C.teal+'0E'} stroke={C.teal} strokeWidth={3}/><T x={x(1)} y={584} color={C.teal} size={24} anchor="middle">一段连续的字符</T></g><g opacity={unique}><rect x={405} y={727} width={470} height={92} rx={18} fill={C.surface} stroke={C.teal}/><T x={640} y={786} size={36} color={C.teal} anchor="middle">这段里，没有重复字符</T></g><g opacity={longest}><rect x={1015} y={727} width={470} height={92} rx={18} fill={C.surface} stroke={C.gold}/><T x={1250} y={786} size={36} color={C.gold} anchor="middle">长度，要尽可能长</T></g></>;
 }
 if(t==='substring'){
  return <><Head title="abc 是合法候选，还能找到更长的吗？" sub="前三个字符连续且互不重复 · 示例候选长度是 3"/><Board left={0} right={7} best={0} showSet={false} showStats={false} showPointers={false} windowAlpha={0} windowColor={C.text}/><rect x={x(0)-78} y={388} width={2*170+156} height={168} rx={18} fill={C.teal+'0E'} stroke={C.teal} strokeWidth={3}/><T x={x(1)} y={584} color={C.teal} size={24} anchor="middle">连续片段 abc</T><g opacity={p}><T x={655} y={789} size={43} color={C.teal} anchor="middle">候选长度：3</T></g><g opacity={q}><T x={1295} y={789} size={36} color={C.gold} anchor="middle">继续寻找更长的合法片段</T></g><Note alpha={q}>最后只返回最长长度</Note></>;
 }
 if(t==='naive-recheck'){
  const second=f>=at(s,1,.02),start=second?1:0,read=phase(s,f,second?1:0,.04,.76);
  const end=Math.min(3,start+Math.floor(read*(4-start))),repeated=end===3;
  const firstHistory=second||read>=.99,trace=TEXT.slice(start,end+1).split('').join(' → ');
  return <><Head kicker="思路推导 · 还没有选定做法" title="每个起点重来，会反复检查同一段" sub={second?'从下标 1 重来：刚看过的 b、c 又要检查':'先从下标 0 逐个尝试，遇到重复就停'}/><Board left={start} right={end} best={0} showSet={false} showStats={false} showPointers={false} pending={repeated?3:-1} duplicate={repeated?1:-1} windowColor={repeated?C.red:C.teal} regionLabel={repeated?'待检验片段 · 有重复':'正在尝试的连续片段'}/>
   <T x={250} y={760} size={25} color={C.muted}>检查记录 · 仍是同一份原字符串</T>
   <T x={250} y={815} size={34} color={firstHistory?C.muted:repeated?C.red:C.teal} mono>起点 0：{firstHistory?'a → b → c → b · 重复停止':trace}</T>
   {second&&<T x={250} y={868} size={34} color={C.gold} mono>起点 1：{trace}{repeated?' · 再次重复停止':''}</T>}
   <Note color={C.gold} alpha={q}>能否保留已检查过的部分，减少重扫？</Note>
  </>;
 }
 if(t==='reuse-contiguous'){
  const second=f>=at(s,1,.03),move=phase(s,f,1,.03,.5),invalidStart=Math.min(1,Math.floor(phase(s,f,0,.04,.6)*2));
  const start=second?mix(1,2,move):invalidStart,valid=second&&move>=1;
  const hole=phase(s,f,0,.55,.82)*(1-q);
  return <><Head kicker="思路推导 · 回看不同起点" title="重复限制，告诉我们哪些起点能排除" sub="固定到下标 3 · 两份 b 在原下标 1 和 3"/><Board left={start} right={3} best={0} showSet={false} showStats={false} showPointers={false} pending={valid?-1:3} duplicate={valid?-1:1} duplicateAlpha={second?1-move:1} windowColor={valid?C.teal:C.red} regionLabel={valid?'从最早合法起点 2 保留连续 cb':'待检验片段 · 包含两份 b'}/>
   <T x={960} y={705} anchor="middle" size={31} color={C.red} alpha={hole}>不能只挖掉中间的旧 b：a · c b 不再连续</T>
   {[['起点 0：abcb ×',C.red],['起点 1：bcb ×',C.red],['起点 2：cb ✓',C.teal]].map(([label,color],i)=><T key={label} x={450+i*510} y={795} anchor="middle" size={31} color={color} alpha={i===2?(valid?1:0):1}>{label}</T>)}
   <T x={960} y={858} anchor="middle" size={30} color={C.teal} alpha={q}>保留连续片段，再记下它有哪些字符，避免从头重查</T>
   <Note color={C.muted} alpha={q}>这是思路推导；下一步重回空区间，正式执行</Note>
  </>;
 }
 if(t==='window'){
  const term=f>=Number(s.cueFrames?.labels?.['滑动窗口']??0);
  return <><Head kicker="正式执行 · 分析结束，重回空区间" title="左右边界，圈住连续的一段" sub={term?'滑动窗口 · 初态为空，从下标 0 开始':'按刚才的推导，保留连续合法片段'}/><Board left={0} right={-1} best={0} setAlpha={q}/><T x={960} y={374} size={36} color={C.teal} anchor="middle">{term?'滑动窗口':''}</T><Note alpha={q}>位置看边界，是否出现过看集合</Note></>;
 }
 if(t==='grow'){
  const progress=clamp((f-at(s,0,.04))/Math.max(1,at(s,0,.94)-at(s,0,.04))),z=segment(progress,3),state=insert(0,z.index-1,z.index,z.progress,z.index+1);
  return <><Head title="没有重复，就把右边字符加入" sub="从空窗口开始，依次读入 a、b、c"/><Board {...state}/><Note color={C.teal}>{z.index===2&&z.progress===1?'当前长度 3 · 最长记录 3':'读入 → 加入集合 → 扩展窗口'}</Note></>;
 }
 if(t==='duplicate')return <><Head title="新字符，已经在集合里" sub="合法窗口仍是 abc，候选字符不计入窗口"/><Board left={0} right={2} best={3} pending={3} duplicate={1}/><Note color={C.red}>先停住右边，处理重复</Note></>;
 if(t==='remove-first'){
  const move=phase(s,f,0,.06,.9),state=remove(0,2,3,3,move);
  return <><Head title="先移除左端，再移动左边界" sub="删掉 a 之后，旧 b 仍然留在窗口里"/><Board {...state}/><Action text={move<.34?'移出集合：a':move<1?'左边界：0 → 1':'还有重复，不能加入'}/><Note color={C.red} alpha={q}>只挪一格，并没有解决重复</Note></>;
 }
 if(t==='remove-old'){
  const move=phase(s,f,0,.1,.86),state=remove(1,2,3,3,move);
  return <><Head title="继续移除，直到旧字符离开" sub="移除下标 1 的旧 b，再次检查集合"/><Board {...state}/><Action text={move<.34?'移出集合：旧 b':move<1?'左边界：1 → 2':'候选 b 已不在集合里'} color={move>=1?C.teal:C.gold}/><Note alpha={q} color={C.teal}>重复消失后，才可以加入新字符</Note></>;
 }
 if(t==='insert'){
  const move=phase(s,f,0,.06,.9),state=insert(2,2,3,move);
  return <><Head title="现在，才加入新的字符" sub="左边界 2 · 右边界落到 3"/><Board {...state}/><Action text={move<.32?'加入集合：新 b':move<1?'右边界落到下标 3':'当前窗口：cb'} color={C.teal}/><Note alpha={q}>当前长度 2，最长记录仍然是 3</Note></>;
 }
 if(t==='extend-best'){
  const z=segment(span(s,f,.05,.38),3),r=3+z.index,state=insert(2,r,Math.max(3,r-1),z.progress,Math.max(3,r));
  return <><Head title="继续扩展，保留变长的窗口" sub="接下来的 a、d、e 都不在集合里"/><Board {...state} bestUnderline={z.index===2&&z.progress===1}/><Note color={C.gold}>{z.index===2&&z.progress===1?'记录最长区间：下标 2..6，长度 5':'cb → cba → cbad → cbade'}</Note></>;
 }
 if(t==='duplicate-again')return <><Head title="最后一个字符，再次出现重复" sub="窗口 cbade 保持不变，先处理候选 a"/><Board left={2} right={6} best={5} pending={7} duplicate={4}/><Note color={C.red}>右边先停住，左边继续消重</Note></>;
 if(t==='shrink-again'){
  const z=segment(span(s,f,.04,.58),3),l=2+z.index,state=remove(l,6,5,7,z.progress);
  return <><Head title="这次，要逐格移除三个字符" sub="先移除 c，再移除 b，最后移除旧 a"/><Board {...state}/><Action left text={z.progress<.34?`移出集合：${TEXT[l]}`:z.progress<1?`左边界：${l} → ${l+1}`:l===4?'旧 a 已离开，重复消失':'仍有重复，继续检查'} color={l===4&&z.progress===1?C.teal:C.gold}/><Note>集合删除哪个字符，左边界就越过哪个位置</Note></>;
 }
 if(t==='keep-best'){
  const move=phase(s,f,0,.05,.8),state=insert(5,6,5,move);
  return <><Head title="当前变短，最长记录不回退" sub="最后加入 a，当前窗口是 dea"/><Board {...state} bestUnderline={move===1}/><Note alpha={q} color={C.gold}>返回历史最大 5，不是最后的长度 3</Note></>;
 }
 if(t==='why-safe'){
  const z=segment(span(s,f,.08,.55),3),start=z.index,valid=start===2;
  return <><Head kicker="证明回看 · 首次重复" title="旧字符还在，这些起点都不合法" sub="固定右端下标 3：逐个检查可能的起点" color={C.gold}/><Board left={start} right={3} best={3} showSet={false} showStats={false} windowColor={valid?C.teal:C.red} regionLabel={valid?'最靠左的合法起点':'待检验区间，包含重复'} duplicate={valid?-1:1} pending={valid?-1:3}/>{[0,1,2].map(i=><g key={i} opacity={i<=start?1:.2}><T x={470+i*500} y={774} anchor="middle" size={30} color={i===2?C.teal:C.red}>起点 {i}：{TEXT.slice(i,4)} {i===2?'✓':'×'}</T></g>)}<Note color={valid?C.teal:C.gold}>{valid?'再往右只会更短，从最靠左的合法起点继续':'保留旧 b 的起点，都会包含两个 b'}</Note></>;
 }
 if(t==='complexity'){
  const events=[{l:0,r:0,b:1},{l:0,r:1,b:2},{l:0,r:2,b:3},{l:1,r:2,b:3},{l:2,r:2,b:3},{l:2,r:3,b:3},{l:2,r:4,b:3},{l:2,r:5,b:4},{l:2,r:6,b:5},{l:3,r:6,b:5},{l:4,r:6,b:5},{l:5,r:6,b:5},{l:5,r:7,b:5}],z=segment(span(s,f,.03,.62),events.length),now=events[z.index],before=z.index?events[z.index-1]:{l:0,r:-1,b:0};
  const state:BoardProps=now.l>before.l?remove(before.l,before.r,before.b,before.r+1,z.progress):insert(before.l,before.r,before.b,z.progress,now.b);
  return <><Head kicker="完整轨迹回看" title="每个位置，最多加入和移除各一次" sub="两个边界都只向右，移除循环不会反复扫描同一位置"/><Board {...state}/><Note color={C.teal} alpha={q}>集合操作平均 O(1) → 整体平均 O(n)</Note></>;
 }
 if(t==='code-shrink'){
  const z=segment(span(s,f,.12,.56),2),state=remove(z.index,2,3,3,z.progress);
  return <><Head kicker="代码回看 · 首次重复" title="还有重复，就继续循环" sub="只删一次不够；条件不满足时才停止"/><CodeLine>while ch in seen:</CodeLine><Board {...state} topPointerY={381}/><Note color={C.gold}>删除左端字符，再把 left 右移一格</Note></>;
 }
 if(t==='code-best'){
  const move=phase(s,f,0,.05,.8),state=insert(5,6,5,move);
  return <><Head kicker="代码回看 · 最后一个字符" title="消除重复后，再更新最长长度" sub="先加入新字符，当前合法长度是 right − left + 1"/><CodeLine color={C.teal}>best = max(best, right - left + 1)</CodeLine><Board {...state} topPointerY={381}/><Note alpha={q} color={C.gold}>max(5, 3) = 5 · 最后返回 best</Note></>;
 }
 if(t==='edge'){
  const step=Math.min(3,Math.floor(q*4));
  return <><Head kicker="独立边界示意" title="没有字符，或所有字符都一样" sub="与主示例分开：同样的规则处理边界"/>
   <rect x={245} y={350} width={610} height={490} rx={22} fill={C.surface} stroke={C.edge}/><T x={550} y={420} anchor="middle" size={31} color={C.muted}>空字符串</T><T x={550} y={575} anchor="middle" size={80} mono>""</T><T x={550} y={735} anchor="middle" size={46} color={C.gold}>长度 0</T>
   <g opacity={q}><rect x={925} y={350} width={750} height={490} rx={22} fill={C.surface} stroke={C.edge}/><T x={1300} y={420} anchor="middle" size={31} color={C.muted}>相同字符</T>{[0,1,2,3].map(i=><g key={i}><rect x={1018+i*145} y={500} width={116} height={105} rx={12} fill={C.bg} stroke={C.edge}/><T x={1076+i*145} y={575} anchor="middle" size={65} mono color={i===step?C.teal:C.muted}>a</T></g>)}<rect x={1009+step*145} y={490} width={134} height={124} rx={16} fill="none" stroke={C.teal} strokeWidth={3}/><T x={1300} y={735} anchor="middle" size={46} color={C.gold}>最长仍是 1</T></g>
  </>;
 }
 return <><Head kicker="结果回看" title="右边探索，左边消重，保留最长" sub="最长区间是下标 2..6，返回它的长度" color={C.teal}/><Board left={2} right={6} best={5} showSet={false} showStats={false} windowColor={C.gold} regionLabel="最长子串：cbade"/><T x={960} y={806} anchor="middle" size={66} weight={760} color={C.gold}>返回长度 5</T></>;
};

const ShotView=({s,hideSubtitles=false}:{s:Shot;hideSubtitles?:boolean})=>{
 const f=useCurrentFrame(),codeCardFrom=Number.isFinite(s.codeCardFrom)?Number(s.codeCardFrom):null;
 const card=codeCardFrom!==null&&f>=codeCardFrom;
 const sceneShot=codeCardFrom===null?s:{...s,durationInFrames:codeCardFrom};
 const subtitle=(s.subtitles??[]).find(item=>f>=item.from&&f<(item.to!==undefined?item.to+1:item.from+(item.duration??0)));
 return <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}><LeetcodeBackdrop/><svg width="1920" height="1080" viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}>
  
  {card?<CodeCard/>:<Scene s={sceneShot} f={f}/>}
  
  <T x={120} y={1015} size={20} color={C.muted} alpha={.65}>{card?'Python 3':'示例 abcbadea'}</T>
 </svg>{!hideSubtitles&&!card&&subtitle&&<div data-subtitle={subtitle.text} style={{position:'absolute',left:210,right:210,bottom:69,textAlign:'center',fontSize:31,lineHeight:1.45,fontWeight:500,color:C.text,textShadow:'0 2px 5px #0F172A',whiteSpace:'pre-wrap'}}>{subtitle.text}</div>}</AbsoluteFill>;
};
export const Main=({hideSubtitles=false}:{hideSubtitles?:boolean})=><AbsoluteFill>{__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>} {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} hideSubtitles={hideSubtitles}/></Sequence>)}</AbsoluteFill>;
