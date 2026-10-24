import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT,MONO,PAGE} from './theme';
import {Shot,VIDEO,shots} from './data';

declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ramp=(f:number,start:number,len=18)=>clamp((f-start)/len);
const ease=(x:number)=>1-Math.pow(1-clamp(x),3);
const money=(n:number)=>n.toLocaleString('en-US');
const sentence=(s:Shot,i:number,fallback:number)=>Number(s.cueFrames?.sentences?.[i]??fallback);
const cue=(s:Shot,k:string,fallback:number)=>Number(s.cueFrames?.[k]??fallback);

const Title:React.FC<{children:React.ReactNode}>=({children})=><div style={{position:'absolute',left:110,top:149,fontSize:64,fontWeight:750,lineHeight:1.2,letterSpacing:-1.8}}>{children}</div>;
const Note:React.FC<{children:React.ReactNode;color?:string;y?:number;x?:number}>=({children,color=C.muted,y=862,x=110})=><div style={{position:'absolute',left:x,top:y,color,fontSize:27,lineHeight:1.4}}>{children}</div>;
const Pill:React.FC<{children:React.ReactNode;x:number;y:number;color?:string;opacity?:number}>=({children,x,y,color=C.teal,opacity=1})=><div style={{position:'absolute',left:x,top:y,color,opacity,border:`1px solid ${color}77`,background:`${color}12`,padding:'10px 24px',borderRadius:12,fontSize:28,fontWeight:700,lineHeight:1.35}}>{children}</div>;

const Transfer:React.FC<{y?:number;label?:string;tone?:string}>=({y=247,label='同一笔转账',tone=C.gold})=><div style={{position:'absolute',left:110,top:y,width:1700,height:66,display:'flex',alignItems:'center',gap:25,borderBottom:`1px solid ${C.edge}`,boxSizing:'border-box'}}>
 <span style={{fontSize:25,color:C.muted}}>{label}</span><span style={{fontSize:30}}>你</span><svg width="68" height="25" viewBox="0 0 68 25"><path d="M0 12H62m-12-10 12 10-12 10" stroke={tone} strokeWidth="2.5" fill="none"/></svg><span style={{fontSize:30}}>对方</span><span style={{fontFamily:MONO,color:tone,fontSize:38,fontWeight:700}}>200</span><span style={{fontSize:26,color:C.muted}}>元</span><span style={{marginLeft:'auto',fontSize:25,color:C.muted}}>同一数据库中的两个账户</span>
 </div>;

type AccountProps={x:number;y:number;name:string;value:number;color?:string;state?:string;emphasis?:boolean;opacity?:number};
const Account:React.FC<AccountProps>=({x,y,name,value,color=C.text,state='已确认',emphasis=false,opacity=1})=><div style={{position:'absolute',left:x,top:y,width:790,height:242,background:PAGE.bg,border:`1.5px solid ${emphasis?color:C.edge}`,borderRadius:22,boxSizing:'border-box',padding:'25px 32px',opacity}}>
 <div style={{display:'flex',alignItems:'center',gap:14}}><div style={{width:9,height:9,borderRadius:'50%',background:emphasis?color:C.muted}}/><div style={{fontSize:30,color:C.muted}}>{name}</div><div style={{marginLeft:'auto',fontSize:23,color:emphasis?color:C.muted}}>{state}</div></div>
 <div style={{display:'flex',alignItems:'baseline',gap:20,marginTop:28}}><span style={{fontSize:80,fontWeight:650,fontFamily:MONO,color,letterSpacing:-4,lineHeight:1.15}}>{money(value)}</span><span style={{fontSize:31,color:C.muted}}>元</span></div>
 <div style={{position:'absolute',left:32,right:32,bottom:20,height:2,background:emphasis?`${color}66`:C.edge}}/>
 </div>;

const Pair:React.FC<{values?:[number,number];y?:number;states?:[string,string];tones?:[string,string];active?:[boolean,boolean];caption?:string}>=({values=[1000,500],y=368,states=['已确认','已确认'],tones=[C.text,C.text],active=[false,false],caption='已确认余额'})=><>
 <div style={{position:'absolute',left:110,top:y-39,fontSize:25,color:C.muted,letterSpacing:1}}>{caption}</div>
 <Account x={110} y={y} name="你的账户" value={values[0]} state={states[0]} color={tones[0]} emphasis={active[0]}/>
 <Account x={1020} y={y} name="对方账户" value={values[1]} state={states[1]} color={tones[1]} emphasis={active[1]}/>
 </>;

const Preview:React.FC<{values:[number,number];debit?:boolean;credit?:boolean;opacity?:number;y?:number;label?:string;strike?:boolean}>=({values,debit=true,credit=false,opacity=1,y=652,label='本次修改预览 · 尚未确认生效',strike=false})=><div style={{position:'absolute',left:110,top:y,width:1700,height:190,boxSizing:'border-box',border:`1px solid ${C.gold}66`,borderRadius:18,background:'#2B251D',opacity,padding:'20px 30px'}}>
 <div style={{fontSize:25,color:C.gold,marginBottom:18,display:'flex',alignItems:'center',gap:12}}><span style={{display:'inline-block',width:8,height:8,borderRadius:'50%',background:C.gold}}/>{label}</div>
 <div style={{display:'flex',gap:112}}>{[0,1].map(i=><div key={i} style={{width:704,display:'flex',alignItems:'baseline',gap:24,position:'relative'}}>
  <span style={{fontSize:26,color:C.muted,minWidth:130}}>{i===0?'你的账户':'对方账户'}</span><span style={{fontFamily:MONO,fontSize:58,fontWeight:650,color:C.gold,letterSpacing:-2,textDecoration:strike?'line-through':undefined,textDecorationColor:C.red}}>{money(values[i])}</span><span style={{fontSize:26,color:C.muted}}>元</span>
  <span style={{marginLeft:'auto',fontSize:25,color:(i===0?debit:credit)?C.gold:C.muted}}>{i===0?(debit?'−200':'未修改'):(credit?'+200':'尚未入账')}</span>
 </div>)}</div>
 </div>;

const StepRail:React.FC<{active?:number;failed?:boolean;completed?:boolean;y?:number;grouped?:boolean;planning?:boolean}>=({active=0,failed=false,completed=false,y=682,grouped=false,planning=false})=><div style={{position:'absolute',left:110,top:y,width:1700,height:126,boxSizing:'border-box',border:grouped?`1px solid ${C.teal}88`:'none',background:grouped?'#102E3422':'transparent',borderRadius:20,display:'flex',alignItems:'center',gap:40,padding:grouped?'15px 30px':'0'}}>
 {[0,1].map((i)=><React.Fragment key={i}>{i===1&&<svg width="130" height="35"><path d="M0 17H120m-14-14 14 14-14 14" stroke={C.muted} strokeWidth="3" fill="none"/></svg>}<div style={{flex:1,height:78,display:'flex',alignItems:'center',gap:25,borderBottom:`2px solid ${failed&&i===1?C.red:completed||active===i?C.teal:C.edge}`,color:failed&&i===1?C.red:completed||active===i?C.text:C.muted}}><span style={{fontFamily:MONO,fontSize:27,color:failed&&i===1?C.red:C.muted}}>0{i+1}</span><span style={{fontSize:33}}>{i===0?'你的账户减 200':'对方账户加 200'}</span><span style={{marginLeft:'auto',fontSize:28,color:planning?C.muted:failed&&i===1?C.red:C.teal}}>{planning?(i===0?'第一步':'第二步'):failed&&i===1?'×':completed||active>i?'✓':active===i?'进行中':''}</span></div></React.Fragment>)}
 </div>;

const ErrorBar:React.FC<{text:string;y?:number;opacity?:number}>=({text,y=854,opacity=1})=><div style={{position:'absolute',left:110,top:y,width:1700,fontSize:28,color:C.red,opacity,display:'flex',alignItems:'center',gap:15}}><span style={{display:'inline-flex',width:28,height:28,borderRadius:'50%',border:`2px solid ${C.red}`,alignItems:'center',justifyContent:'center',fontSize:22}}>!</span>{text}</div>;

const Scene:React.FC<{shot:Shot}>=({shot})=>{
 const f=useCurrentFrame(),d=shot.durationInFrames,id=parseInt(shot.id);
 const s1=sentence(shot,1,d*.5),s2=sentence(shot,2,d*.75);
 const tTransaction=cue(shot,'transactionLabel',1),tCommit=cue(shot,'commitLabel',1),tRollback=cue(shot,'rollbackLabel',1);
 if(id===1)return <>
  <Title>扣了钱，对方没到账？</Title><Transfer label="两步分开生效的例子"/>
  <Pair values={[800,500]} states={['扣款已生效','入账未完成']} tones={[C.gold,C.red]} active={[true,true]}/>
  <StepRail active={1} failed/>
  <ErrorBar text="只完成了一半：一边减少，另一边没有增加"/>
 </>;
 if(id===2)return <>
  <Title>从同一数据库里的两个账户说起</Title><Transfer label="回到示例起点"/>
  <Pair/>
  <div style={{position:'absolute',left:110,top:664,width:1700,height:132,border:`1px solid ${C.edge}`,borderRadius:20,background:C.surface,display:'flex',alignItems:'center',padding:'0 36px',boxSizing:'border-box',gap:30}}>
   <span style={{fontSize:29,color:C.muted}}>同一个数据库</span><span style={{height:42,width:1,background:C.edge}}/><span style={{fontSize:34}}>这次只演示：改这两条账户记录</span>
  </div>
  <Note>教学示例，不代表真实跨行支付流程</Note>
 </>;
 if(id===3){const second=f>=s1;return <>
  <Title>一次转账，要改两处数据</Title><Transfer/>
  <Pair values={[1000,500]} states={['原来余额','原来余额']} caption="原来余额 · 下面说明两次修改的目标" active={[!second,second]} tones={[second?C.text:C.gold,second?C.gold:C.text]}/>
  <StepRail planning active={second?1:0}/>
  <Note color={C.gold}>{second?'对方加 200，目标余额 700 元':'你减 200，目标余额 800 元'}</Note>
 </>}
 if(id===4){const changed=f>=Math.max(24,Math.round(s1*.6));return <>
  <Title>如果两步，各自单独生效</Title><Transfer/>
  <Pair values={[changed?800:1000,500]} active={[changed,false]} states={[changed?'扣款已生效':'原来余额','尚未入账']} tones={[changed?C.gold:C.text,C.text]}/>
  <StepRail active={changed?1:0}/>
  <Note color={C.gold}>{changed?'第一步已经确认，第二步还没完成':'先执行扣款，再执行入账'}</Note>
 </>}
 if(id===5){const failed=f>=Math.min(30,Math.round(s1*.75));return <>
  <Title>第二步失败，留下了半个结果</Title><Transfer/>
  <Pair values={[800,500]} states={['扣款已生效',failed?'入账失败':'等待入账']} tones={[C.gold,failed?C.red:C.text]} active={[true,failed]}/>
  <StepRail active={1} failed={failed}/>
  <ErrorBar text={failed?'先前单独生效的扣款，不会因为这一步失败自动撤销':'第二步还没完成，第一步已经改变了数据'}/>
 </>}
 if(id===6)return <>
  <Title>把两处修改，作为一个整体处理</Title><Transfer label="换一种处理方式"/>
  <Pair/>
  <StepRail grouped active={-1}/>
  {f>=tTransaction&&<Pill x={110} y={850}>事务</Pill>}
  <Note x={690} color={C.teal}>同一笔操作里的修改，一起确认或一起撤回</Note>
 </>;
 if(id===7){const changed=f>=s1;return <>
  <Title>先扣款，修改还在这一笔操作里</Title><Transfer/>
  <Pair/>
  <Preview values={[changed?800:1000,500]} debit={changed}/>
  <Note color={C.gold}>下方是本次修改预览，上方已确认余额保持原样</Note>
 </>}
 if(id===8){const changed=f>=s1;return <>
  <Title>再入账，两处修改都准备好了</Title><Transfer/>
  <Pair/>
  <Preview values={[800,changed?700:500]} credit={changed}/>
  <Note color={C.gold}>{changed?'两步都已执行，但这笔操作还没有确认生效':'继续修改对方账户，上方已确认余额仍未改变'}</Note>
 </>}
 if(id===9){const commitAt=Math.min(d-55,Math.max(tCommit+20,s1));const committed=f>=commitAt;return <>
  <Title>两步都成功，一起确认生效</Title><Transfer tone={committed?C.teal:C.gold}/>
  <Pair values={committed?[800,700]:[1000,500]} active={[committed,committed]} tones={committed?[C.teal,C.teal]:[C.text,C.text]} states={committed?['本次转账已确认','本次转账已确认']:['原来余额','原来余额']}/>
  {!committed&&<Preview values={[800,700]} credit/>}
  {committed&&<div style={{position:'absolute',left:110,top:672,width:1700,height:140,background:'#123832',border:`1px solid ${C.teal}77`,borderRadius:20,display:'flex',alignItems:'center',padding:'0 35px',boxSizing:'border-box',gap:32}}><span style={{fontSize:49,color:C.teal}}>✓</span><span style={{fontSize:34}}>本次操作完成：两处修改一起成为正式结果</span></div>}
  {f>=tCommit&&<Pill x={110} y={852}>提交</Pill>}
 </>}
 if(id===10){const debitAt=Math.max(24,Math.round(s1*.75));const deducted=f>=debitAt;const failed=f>=s1+28;return <>
  <Title>再看一次：第二步出了问题</Title><Transfer label="重新演示一笔失败操作"/>
  <Pair/>
  <Preview values={[deducted?800:1000,500]} debit={deducted} label={failed?'本次修改预览 · 入账失败，等待应用处理':deducted?'本次修改预览 · 扣款已执行，尚未确认':'另一个失败示例 · 从相同起点开始'}/>
  <ErrorBar text={failed?'应用发现入账失败，决定撤销本次操作':'这是从 1,000 / 500 重新开始的另一笔示例'}/>
 </>}
 if(id===11){const withdrawAt=Math.min(d-55,Math.max(tRollback+22,s1+24));const withdrawn=f>=withdrawAt;return <>
  <Title>撤销这一笔操作里的全部修改</Title><Transfer label="应用请求撤销这笔事务"/>
  <Pair tones={withdrawn?[C.teal,C.teal]:[C.text,C.text]} active={[withdrawn,withdrawn]}/>
  {!withdrawn&&<Preview values={[800,500]} strike opacity={1-ease(ramp(f,withdrawAt-22,22))}/>}
  {withdrawn&&<div style={{position:'absolute',left:110,top:670,width:1700,height:138,border:`1px solid ${C.teal}77`,borderRadius:20,background:'#11312F',padding:'0 34px',display:'flex',alignItems:'center',gap:28,boxSizing:'border-box'}}><span style={{fontSize:42,color:C.teal}}>↶</span><span style={{fontSize:34}}>本次未确认的修改已撤销，原余额保留</span></div>}
  {f>=tRollback&&<Pill x={110} y={852} color={C.teal}>回滚</Pill>}
 </>}
 if(id===12){const stopped=f>=s1;return <>
  <Title>还没提交，数据库突然停止</Title><Transfer label="重新演示：提交之前发生故障"/>
  <Pair/>
  <Preview values={[800,500]} opacity={stopped?.32:1} label="本次修改预览 · 未提交"/>
  {stopped&&<div style={{position:'absolute',left:400,top:680,width:1120,height:125,background:'#36212C',border:`1px solid ${C.red}88`,borderRadius:18,display:'flex',alignItems:'center',justifyContent:'center',gap:24}}><span style={{fontSize:42,color:C.red}}>!</span><span style={{fontSize:36,color:C.red}}>数据库进程崩溃 · 未提交</span></div>}
  <Note color={stopped?C.red:C.muted}>{stopped?'操作还没有提交，不能把半笔修改作为已确认结果':'故障发生点：这笔事务提交之前'}</Note>
 </>}
 if(id===13){const recovered=f>=s1;return <>
  <Title>重启恢复，撤回未提交的修改</Title><Transfer label="恢复刚才那笔未提交操作"/>
  <Pair active={[recovered,recovered]} tones={recovered?[C.teal,C.teal]:[C.text,C.text]}/>
  {!recovered&&<Preview values={[800,500]} opacity={.65*(1-ramp(f,Math.max(10,s1-32),32))} strike label="恢复中 · 撤销上一次未提交的修改"/>}
  {recovered&&<div style={{position:'absolute',left:110,top:668,width:1700,height:146,border:`1px solid ${C.teal}`,borderRadius:20,background:'#123832',padding:'0 35px',display:'flex',alignItems:'center',gap:40,boxSizing:'border-box'}}>
   <span style={{fontSize:32,color:C.muted}}>数据库重启</span><svg width="90" height="30"><path d="M0 15h80m-13-12 13 12-13 12" fill="none" stroke={C.teal} strokeWidth="3"/></svg><span style={{fontSize:34,color:recovered?C.teal:C.muted}}>{recovered?'未提交事务回滚完成':'恢复中，处理未提交事务…'}</span><span style={{marginLeft:'auto',fontSize:32,color:C.teal}}>{recovered?'✓':''}</span>
  </div>}
  <Note color={C.teal}>已确认余额仍是原值，不留下只有一边改变的结果</Note>
 </>}
 if(id===14){const crossed=f>=s1;return <>
  <Title>这一笔事务，只留下完整的结果</Title>
  <div style={{position:'absolute',left:110,top:310,width:790,height:382,background:'#102C30',border:`1px solid ${C.teal}77`,borderRadius:22,padding:38,boxSizing:'border-box'}}><div style={{fontSize:31,color:C.teal}}>两步都成功 · 提交</div><div style={{display:'flex',gap:45,marginTop:45}}>{[800,700].map((v,i)=><div key={v} style={{flex:1}}><div style={{fontSize:25,color:C.muted}}>{i===0?'你的账户':'对方账户'}</div><div style={{fontSize:65,fontFamily:MONO,marginTop:18,color:C.teal,fontWeight:650}}>{money(v)}</div></div>)}</div><div style={{fontSize:27,color:C.muted,marginTop:40}}>两处修改一起成为正式结果</div></div>
  <div style={{position:'absolute',left:1020,top:310,width:790,height:382,background:C.surface,border:`1px solid ${C.edge}`,borderRadius:22,padding:38,boxSizing:'border-box'}}><div style={{fontSize:31,color:C.text}}>没有完成 · 回滚</div><div style={{display:'flex',gap:45,marginTop:45}}>{[1000,500].map((v,i)=><div key={v} style={{flex:1}}><div style={{fontSize:25,color:C.muted}}>{i===0?'你的账户':'对方账户'}</div><div style={{fontSize:65,fontFamily:MONO,marginTop:18,fontWeight:650}}>{money(v)}</div></div>)}</div><div style={{fontSize:27,color:C.muted,marginTop:40}}>本次修改全部撤销，保留原值</div></div>
  <div style={{position:'absolute',left:110,top:738,width:1700,height:100,border:`1px solid ${C.red}66`,background:'#30212B',borderRadius:18,display:'flex',alignItems:'center',justifyContent:'center',gap:30,opacity:crossed?1:.35}}><span style={{fontSize:34,color:C.red}}>×</span><span style={{fontSize:33,color:C.red}}>不会把 800 / 500 这种半笔状态确认为最终结果</span></div>
  <Note>只讨论同一事务中的这两处修改</Note>
 </>}
 if(id===15)return <>
  <Title>记住：这里讲的是同一个数据库</Title><Transfer/>
  <Pair values={[800,700]} active={[true,true]} tones={[C.teal,C.teal]}/>
  <div style={{position:'absolute',left:110,top:668,width:1700,height:148,background:C.surface,border:`1px solid ${C.edge}`,borderRadius:22,padding:'25px 34px',boxSizing:'border-box'}}><div style={{fontSize:33,color:C.text}}>现实转账，还可能经过多个系统。</div><div style={{fontSize:27,color:C.muted,marginTop:17}}>本片只解释：一笔数据库事务里的两处修改如何一起生效。</div></div>
  <Note>不能仅凭这个示例判断真实支付系统的到账状态</Note>
 </>;
 const nextAt=Math.max(24,Math.round(s1*.5));const next=f>=nextAt,brand=f>=s1;
 return <>
  <Title>{next?'下一期：两个人抢最后一件货，听谁的？':'修改成一整笔，还要防止同时争抢'}</Title>
  {!next?<Pair values={[800,700]} active={[true,true]} tones={[C.teal,C.teal]}/>:<div style={{position:'absolute',left:110,top:342,width:1700,height:446,background:C.surface,border:`1px solid ${C.edge}`,borderRadius:24,padding:'45px 60px',boxSizing:'border-box',opacity:ease(ramp(f,nextAt,15))}}><div style={{fontSize:28,color:C.muted,marginBottom:24}}>下一个问题</div><div style={{fontSize:65,fontWeight:750,lineHeight:1.5}}>两个人抢最后一件货，<br/><span style={{color:C.gold}}>听谁的？</span></div><div style={{position:'absolute',right:90,top:86,width:320,height:240,border:`1px solid ${C.gold}77`,borderRadius:18,padding:'25px 34px',boxSizing:'border-box'}}><div style={{fontSize:27,color:C.muted}}>库存（示例）</div><div style={{fontFamily:MONO,fontSize:112,lineHeight:1.2,color:C.gold,marginTop:10,fontWeight:700}}>1</div></div></div>}
  {brand&&<div style={{position:'absolute',left:110,top:854,fontSize:32,color:C.muted,fontWeight:600}}>IT小村 · 原创</div>}
 </>;
};

const ShotView:React.FC<{shot:Shot}>=({shot})=>{
 const f=useCurrentFrame();
 const sub=shot.subtitles?.find(s=>f>=s.from&&f<=(s.to??s.from+(s.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 88% 8%, #173B4D66, transparent 56%)'}}/>
  <div style={{position:'absolute',left:110,top:67,fontSize:24,letterSpacing:3,color:C.muted}}>数据库<span style={{color:C.edge,margin:'0 18px'}}>/</span><span style={{color:C.teal}}>EP.16</span></div>
  <div style={{position:'absolute',right:110,top:65,fontSize:27,fontWeight:650}}>IT小村<span style={{display:'inline-block',width:8,height:8,borderRadius:'50%',background:C.teal,marginLeft:13,verticalAlign:'middle'}}/></div>
  <div style={{position:'absolute',right:110,top:112,fontSize:19,color:C.muted,letterSpacing:1}}>示例数据 · 同一数据库 · 非真实转账</div>
  <Scene shot={shot}/>
  {sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:42,fontWeight:500,lineHeight:1.3,textAlign:'center',background:`${C.bg}F7`,borderRadius:14}}>{sub.text}</div>}
  <div style={{position:'absolute',left:110,right:110,bottom:22,height:2,background:C.edge}}><div style={{height:2,width:`${((shot.from+f)/VIDEO.durationInFrames)*100}%`,background:C.teal}}/></div>
 </AbsoluteFill>;
};

export const Main=()=> <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(shot=><Sequence key={shot.id} name={shot.id} from={shot.from} durationInFrames={shot.durationInFrames}><ShotView shot={shot}/></Sequence>)}
</AbsoluteFill>;
