import React from 'react';
import {Shot} from './data';
import {C} from './theme';
import {Arrow,Head,Node,Note,T,clamp,ease,mix,phase} from './primitives';

const roleColor:Record<string,string>={天:C.teal,地:C.blue,人:C.gold};
const Role=({name,x,y,alpha=1,rank,scale=1,color}:any)=><g opacity={alpha}>
 {rank&&<T x={x} y={y-66*scale} size={28} color={color??roleColor[name]??C.muted} anchor="middle">{rank}</T>}
 <Node id={'lower-'+name+'-'+x+'-'+y} label={name} x={x} y={y} color={color??roleColor[name]??C.text} scale={scale}/>
</g>;
const ProofHead=({title,sub='六场最优性证明 · 独立计数与反例',color=C.text}:any)=><Head kicker="最少场数 · 为什么六场不能保证" title={title} sub={sub} color={color}/>;
const Formula=({x=960,y=830,children,color=C.gold,size=48,alpha=1}:any)=><T x={x} y={y} size={size} color={color} anchor="middle" weight={750} alpha={alpha}>{children}</T>;
const Part=({p,a=0,b=1,children}:any)=><g opacity={clamp((p-a)/Math.max(.001,b-a))}>{children}</g>;

// This map stays in the same place in 22, 23 and 25. It describes possibilities,
// not two consecutive races or two runs that have both occurred.
const BranchMap=({active='both',alpha=1,compact=false}:any)=>{
 const y=compact?304:321,cardY=compact?367:388,w=500,h=77;
 const left=active==='left'||active==='both',right=active==='right'||active==='both';
 return <g opacity={alpha} data-lower-branch-map="true">
  <T x={960} y={y} size={30} color={C.muted} anchor="middle">地和人，之后会不会同场？</T>
  <path d={`M 960 ${y+15} V ${y+30} M 960 ${y+30} H 560 V ${cardY-7} M 960 ${y+30} H 1360 V ${cardY-7}`} stroke={C.edge} strokeWidth={3} fill="none"/>
  <rect x={310} y={cardY} width={w} height={h} rx={16} fill={left?C.gold+'12':C.surface} stroke={left?C.gold:C.edge} strokeWidth={left?3:1.5}/>
  <rect x={1110} y={cardY} width={w} height={h} rx={16} fill={right?C.blue+'12':C.surface} stroke={right?C.blue:C.edge} strokeWidth={right?3:1.5}/>
  <T x={560} y={cardY+51} size={33} color={left?C.gold:C.muted} anchor="middle">后来同场</T>
  <T x={1360} y={cardY+51} size={33} color={right?C.blue:C.muted} anchor="middle">始终不同场</T>
 </g>;
};

const World=({name,order,x,y,alpha=1,highlight=false}:any)=>{
 const colors=order.map((name:string)=>roleColor[name]??C.muted);
 return <g opacity={alpha} data-fixed-world={name}>
  <rect x={x} y={y} width={790} height={283} rx={20} fill={C.surface} stroke={highlight?C.blue:C.edge} strokeWidth={highlight?2.5:1.5}/>
  <T x={x+395} y={y+48} size={29} color={C.muted} anchor="middle">{name}：开赛前就已固定</T>
  {order.map((name:string,i:number)=>{
   const cx=x+110+i*180,cy=y+153;
   return <g key={name}><T x={cx} y={y+106} size={24} color={colors[i]} anchor="middle">{i<3?'真实第'+(i+1):'更慢者'}</T><Node id={name+'-'+x} label={name==='其他22'?'22匹':name} x={cx} y={cy} color={colors[i]}/>{i<3&&<T x={cx+90} y={cy+12} size={32} color={C.muted} anchor="middle">›</T>}</g>;
  })}
  <T x={x+395} y={y+246} size={26} color={C.muted} anchor="middle">这是观众看到的真实顺序，排赛者并不知道</T>
 </g>;
};

export const LowerBoundScene=({s,f}:{s:Shot;f:number})=>{
 const t=s.visualType,p=phase(s,f),q=phase(s,f,1);
 if(t==='lower-bound-intro'){
  const focus=phase(s,f,1,.08,.7),firstColor=focus<.5?C.gold:C.text,secondColor=focus>=.5?C.teal:C.gold;
  return <><ProofHead title="七场能做到，六场为什么不够？" sub="先看必要条件：怎样才能确认唯一冠军？"/>
   <T x={960} y={340} size={32} color={C.muted} anchor="middle">假如还有两匹马，从没在任何一场落败</T>
   <Node id="unbeaten-example-1" label="未败1" x={650} y={505} color={firstColor} scale={1.5}/>
   <Node id="unbeaten-example-2" label="未败2" x={1270} y={505} color={secondColor} scale={1.5}/>
   <path d="M 800 505 H 1120" stroke={C.gold} strokeWidth={3} strokeDasharray="10 12"/>
   <T x={960} y={466} size={33} color={C.gold} anchor="middle">谁更快，仍不能确定</T>
   <Part p={focus} a={.5} b={.9}><T x={1270} y={402} size={34} color={C.teal} anchor="middle">它也可能是总第一</T><T x={960} y={650} size={31} color={C.muted} anchor="middle">把一个未败者放到所有马之前，不会改变已有赛果</T></Part>
   <Formula y={786} size={43} alpha={q}>要确认冠军，其余24匹都必须至少输过1次</Formula>
   <Note>本节一次落败 = 某一场没拿第一；不按“败给几匹”计数</Note>
  </>;
 }
 if(t==='loss-budget'){
  const reveal=phase(s,f,0,.13,.92)*4,budget=phase(s,f,1,.02,.88),firstDim=mix(1,.36,budget);
  return <><ProofHead title="六场，最多只有24次落败" sub="先数落败次数，再数能覆盖多少匹不同的马"/>
   {[0,1,2,3,4].map(i=><g key={i} opacity={firstDim}>
    <Node id={'rank-example-'+i} label={'第'+(i+1)} x={480+i*240} y={397} color={i===0?C.teal:C.gold}/>
    <T x={480+i*240} y={492} size={30} color={i===0?C.teal:C.gold} anchor="middle" alpha={i===0?1:clamp(reveal-i+1)}>{i===0?'未败':'记1次落败'}</T>
   </g>)}
   <Part p={budget} a={0} b={.2}><T x={960} y={590} size={30} color={C.muted} anchor="middle">每场最多4次 × 6场</T></Part>
   {[0,1,2,3,4,5].map(r=><g key={r} opacity={clamp(budget*6-r)}>
    <T x={330+r*250} y={654} size={25} color={C.muted} anchor="middle">第{r+1}场</T>
    {[0,1,2,3].map(i=><circle key={i} cx={300+r*250+(i%2)*60} cy={696+Math.floor(i/2)*52} r={17} fill={C.gold+'22'} stroke={C.gold} strokeWidth={2}/>)}
   </g>)}
   <Formula y={841} size={50} alpha={budget}>上限：6 × 4 = 24 次落败</Formula>
   <Note color={C.gold} alpha={q}>只有24次，必须分别落在24匹不同的非冠军身上</Note>
  </>;
 }
 if(t==='no-repeat-loss'){
  const duplicate=phase(s,f,0,.18,.82),committed=duplicate>.6;
  return <><ProofHead title="有人输两次，就会挤掉另一个名额" sub="这是六场确认冠军的必要条件，不是新增比赛规则"/>
   <T x={820} y={302} size={28} color={C.muted} anchor="middle">24个落败位置：每个本应对应一匹不同的马</T>
   {Array.from({length:24},(_,i)=>{const row=Math.floor(i/6),col=i%6,x=340+col*175,y=360+row*112,last=i===23,label=last&&committed?'1':String(i+1),red=committed&&(i===0||last);return <g key={i}>
    <rect x={x-61} y={y-35} width={122} height={70} rx={13} fill={red?C.red+'12':C.surface} stroke={red?C.red:C.edge} strokeWidth={red?3:1.5}/><T x={x} y={y+13} size={35} color={red?C.red:C.text} anchor="middle" weight={700}>{label}</T>
   </g>;})}
   <Part p={duplicate} a={.4} b={.7}><T x={1550} y={398} size={30} color={C.red} anchor="middle">马1 占了两个位置</T><T x={1550} y={489} size={45} color={C.gold} anchor="middle">24次落败</T><T x={1550} y={568} size={39} color={C.red} anchor="middle">至多23匹落败</T><T x={1550} y={652} size={37} color={C.gold} anchor="middle">至少2匹未败</T></Part>
   <Part p={q} a={.08} b={.7}><rect x={320} y={811} width={1280} height={72} rx={15} fill={C.gold+'0C'} stroke={C.gold+'88'}/><T x={960} y={859} size={33} color={C.gold} anchor="middle">六场要保证成功，任何马都不能输第二次</T></Part>
   <Note>重复落败并不犯规；它会使六场的判断信息不够</Note>
  </>;
 }
 if(t==='hard-case'){
  const top=phase(s,f,0,.1,.85),truth=phase(s,f,1,.04,.75);
  return <><ProofHead title="任意首场，都可能遇到这种情况" sub="独立反例 · 真实速度开赛前就固定，排赛者并不知道"/>
   <rect x={180} y={325} width={1010} height={390} rx={24} fill={C.surface} stroke={C.edge}/><T x={685} y={379} size={31} color={C.muted} anchor="middle">排赛者任意选出的首场5匹</T>
   <rect x={1270} y={325} width={500} height={390} rx={24} fill={C.surface} stroke={C.edge}/><T x={1520} y={379} size={31} color={C.muted} anchor="middle">首场之外</T>
   <Role name="天" x={300} y={535} rank={top>.2?'真实总第1':null}/><Role name="人" x={510} y={535} rank={top>.5?'真实总第3':null}/>
   {['慢1','慢2','慢3'].map((name,i)=><Role key={name} name={name} x={720+i*200} y={535} color={C.muted}/>)}
   <Role name="地" x={1520} y={535} rank={top>.8?'真实总第2':null}/><T x={1520} y={657} size={29} color={C.muted} anchor="middle">另有19匹更慢的马</T>
   <Formula y={811} size={43} alpha={truth}>天 › 地 › 人 › 其他22匹</Formula>
   <Note color={C.gold}>真实顺序只告诉观众；排赛者只能看比赛名次</Note>
  </>;
 }
 if(t==='meet-again'){
  const loss1=phase(s,f,0,.05,.38),loss2=phase(s,f,0,.48,.95),twice=loss2>.95;
  return <><ProofHead title="如果地和人同场，人会再次落败" sub="独立反例的固定顺序：天 › 地 › 人 › 其他22匹"/>
   <BranchMap active="left" compact/>
   <Arrow from={{x:480,y:652}} to={{x:960,y:652}} color={C.gold} progress={loss1}/><Arrow from={{x:1440,y:652}} to={{x:960,y:652}} color={C.red} progress={loss2}/>
   <Role name="天" x={480} y={652}/><Role name="人" x={960} y={652} color={twice?C.red:C.gold}/><Role name="地" x={1440} y={652}/>
   <T x={480} y={559} size={29} color={C.gold} anchor="middle" alpha={loss1}>首场：天赢人</T><T x={1440} y={559} size={29} color={C.red} anchor="middle" alpha={loss2}>若再同场：地也赢人</T>
   <T x={960} y={768} size={37} color={twice?C.red:C.gold} anchor="middle">人：累计落败 {twice?2:loss1>.95?1:0} 次</T>
   <Formula y={845} size={39} color={C.red} alpha={q}>至少2匹未败，连唯一冠军都无法确认</Formula>
   <Note>24次中出现重复，至多覆盖23匹不同的马</Note>
  </>;
 }
 if(t==='swap-speeds'){
  const other=phase(s,f,0,.38,.9),common=phase(s,f,1,.05,.8);
  return <><ProofHead title="如果始终不同场：比较两套固定世界" sub="同一个反例的另一条路 · 不是比赛中途改变速度"/>
   <BranchMap active="right" compact/>
   <World name="世界甲" order={['天','地','人','其他22']} x={140} y={493}/>
   <World name="世界乙" order={['天','人','地','其他22']} x={990} y={493} alpha={other} highlight/>
   <Formula y={846} size={36} alpha={common}>两套世界里：天都更快，其他22匹都更慢</Formula>
   <Note color={C.gold}>两套速度从开赛前就固定，只对照地与人的相对位置</Note>
  </>;
 }
 if(t==='same-results'){
  const first=phase(s,f,0,.02,.27),choice=phase(s,f,0,.3,.63),again=phase(s,f,0,.66,.95),answers=phase(s,f,1,.06,.79);
  return <><ProofHead title="赛果相同，下一场的选择也相同" sub="条件：地与人从未同场 · 同一排赛策略只能依据已有比赛记录"/>
   <T x={525} y={310} size={30} color={C.blue} anchor="middle">世界甲：天 › 地 › 人 › 其他22</T><T x={1395} y={310} size={30} color={C.blue} anchor="middle">世界乙：天 › 人 › 地 › 其他22</T>
   {[150,1020].map(left=><g key={left}>
    <rect x={left} y={340} width={750} height={411} rx={20} fill={C.surface} stroke={C.edge}/>
    <Part p={first}><T x={left+375} y={385} size={26} color={C.muted} anchor="middle">首场：同样5匹，同样名次</T><T x={left+375} y={443} size={34} color={C.gold} anchor="middle">天 › 人 › 慢1 › 慢2 › 慢3</T></Part>
    <Part p={choice}><path d={`M ${left+375} 463 v 31 l -7 -7 m 7 7 l 7 -7`} fill="none" stroke={C.blue} strokeWidth={3}/><T x={left+375} y={541} size={31} color={C.blue} anchor="middle">相同记录 → 同一策略</T><T x={left+375} y={596} size={32} color={C.blue} anchor="middle">下一场，选出同一组马</T></Part>
    <Part p={again}><path d={`M ${left+375} 615 v 25 l -7 -7 m 7 7 l 7 -7`} fill="none" stroke={C.blue} strokeWidth={3}/><T x={left+375} y={683} size={26} color={C.muted} anchor="middle">地、人不同场，其余相对顺序都没变</T><T x={left+375} y={730} size={30} color={C.text} anchor="middle">下一场仍同结果，后续每场同理</T></Part>
   </g>)}
   <T x={960} y={444} size={37} color={C.blue} anchor="middle" alpha={first}>=</T><T x={960} y={572} size={37} color={C.blue} anchor="middle" alpha={choice}>=</T><T x={960} y={716} size={37} color={C.blue} anchor="middle" alpha={again}>=</T>
   <g opacity={answers}><T x={525} y={825} size={39} color={C.gold} anchor="middle">正确前三：天、地、人</T><T x={1395} y={825} size={39} color={C.gold} anchor="middle">正确前三：天、人、地</T></g>
   <Note color={C.gold}>{answers>.5?'同样记录无法分清正确答案，不能保证排出第二、第三':'相同记录 → 相同选择 → 相同赛果，逐场继续'}</Note>
  </>;
 }

 const outcome=phase(s,f,0,.06,.88),conclusion=phase(s,f,1,.03,.86);
 return <><ProofHead title="两条路都不够，最少就是七场" sub="六场必须保证任何固定速度都能解出；一个无法解决的情况就足够否定"/>
  <BranchMap active="both" compact/>
  <Part p={outcome} a={0} b={.45}><T x={560} y={527} size={31} color={C.red} anchor="middle">重复落败 → 至少2匹未败</T></Part>
  <Part p={outcome} a={.48} b={.95}><T x={1360} y={527} size={31} color={C.red} anchor="middle">相同记录 → 分不清第二、第三</T></Part>
  <Part p={conclusion} a={0} b={.3}><T x={600} y={650} size={43} color={C.red} anchor="middle">六场不能保证</T><T x={1320} y={650} size={43} color={C.teal} anchor="middle">七场方案足够</T></Part>
  <Formula y={776} size={76} alpha={clamp((conclusion-.3)/.45)}>最少 7 场</Formula>
  <Formula y={857} size={42} color={C.teal} alpha={clamp((conclusion-.55)/.45)}>5 + 1 + 1 = 7</Formula>
  <T x={960} y={915} size={25} color={C.muted} anchor="middle">IT小村 · 原创</T>
 </>;
};
