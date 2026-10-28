import {MysqlBackdrop,MysqlHeader} from '../../../../_shared/mysql-video/Frame';
import React from 'react';
import {AbsoluteFill,Audio,Sequence,interpolate,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT,MONO,PAGE} from './theme';
import {INDEX,ORDERS,Shot,VIDEO,shots} from '../data';

declare const __HAS_VOICE_AUDIO__:boolean;
const clamp=(v:number,a=0,b=1)=>Math.max(a,Math.min(b,v));
const ramp=(f:number,start:number,length=18)=>clamp((f-start)/length);
const ease=(v:number)=>1-Math.pow(1-clamp(v),3);
const Title:React.FC<{children:React.ReactNode;small?:boolean}>=({children,small})=><div style={{position:'absolute',left:110,top:150,fontSize:small?56:64,fontWeight:750,letterSpacing:-2,lineHeight:1.18}}>{children}</div>;
const Note:React.FC<{children:React.ReactNode;x?:number;y?:number;color?:string}>=({children,x=110,y=830,color=C.muted})=><div style={{position:'absolute',left:x,top:y,color,fontSize:27,lineHeight:1.5}}>{children}</div>;
const Tag:React.FC<{children:React.ReactNode;x:number;y:number;w?:number;color?:string}>=({children,x,y,w,color=C.teal})=><div style={{position:'absolute',left:x,top:y,width:w,display:'flex',alignItems:'center',justifyContent:'center',border:`1px solid ${color}66`,background:`${color}12`,color,borderRadius:12,padding:'12px 24px',fontSize:30,fontWeight:700}}>{children}</div>;
const Query:React.FC<{x?:number;y?:number;width?:number;compact?:boolean}>=({x=110,y=245,width=1700,compact=false})=><div style={{position:'absolute',left:x,top:y,width,height:compact?64:76,display:'flex',alignItems:'center',gap:20,background:C.surface,border:`1px solid ${C.edge}`,borderRadius:15,padding:'0 28px',boxSizing:'border-box'}}>
 <svg width="25" height="25" viewBox="0 0 24 24" fill="none"><circle cx="10" cy="10" r="6" stroke={C.muted} strokeWidth="2"/><path d="m15 15 5 5" stroke={C.muted} strokeWidth="2"/></svg>
 <span style={{fontSize:compact?24:28,color:C.muted}}>查找订单号</span><span style={{fontFamily:MONO,fontSize:compact?31:38,color:C.gold,fontWeight:700}}>7042</span><span style={{marginLeft:'auto',fontSize:22,color:C.muted}}>示例数据</span>
 </div>;

type TableProps={x?:number;y?:number;width?:number;active?:number;found?:boolean;read?:number;dim?:boolean;columns?:boolean;label?:boolean;scale?:number;focusColumn?:boolean};
const Table:React.FC<TableProps>=({x=110,y=350,width=1700,active=-1,found=false,read=0,dim=false,columns=true,label=true,scale=1,focusColumn=false})=>{
 const rowH=52*scale,headH=57*scale;
 const cols=columns?['标识','订单号','商品','金额/元','状态']:['标识','订单号','商品'];
 const weights=columns?[.1,.2,.3,.17,.23]:[.16,.36,.48];
 return <div style={{position:'absolute',left:x,top:y,width,opacity:dim?.32:1}}>
 {label&&<div style={{position:'absolute',left:0,top:-44,fontSize:23,color:C.muted,letterSpacing:3}}>订单表</div>}
 <div style={{border:`1px solid ${C.edge}`,borderRadius:16,overflow:'hidden',background:PAGE.bg,boxShadow:'0 20px 60px #00000018'}}>
 <div style={{display:'flex',height:headH,alignItems:'center',background:C.header,color:C.muted,fontSize:25*scale}}>{cols.map((col,i)=><div key={col} style={{width:weights[i]*100+'%',paddingLeft:i===0?22:0,boxSizing:'border-box'}}>{col}</div>)}</div>
 {ORDERS.map((o,i)=>{
 const target=found&&i===5;
 const current=active===i;
 const viewed=i<read;
 const tone=target?C.teal:current?C.gold:C.text;
 return <div key={o.id} data-row={i+1} style={{height:rowH,display:'flex',position:'relative',alignItems:'center',borderTop:`1px solid ${C.edge}88`,background:target?C.success:current?C.active:viewed?C.row:PAGE.bg,color:tone,fontSize:27*scale,fontWeight:target||current?700:450}}>
 <div style={{position:'absolute',inset:0,borderLeft:`4px solid ${target?C.teal:current?C.gold:'transparent'}`,pointerEvents:'none'}}/>
 {[String(i+1).padStart(2,'0'),o.id,o.item,...(columns?[o.amount,o.status]:[])].map((v,j)=><div key={j} style={{width:weights[j]*100+'%',paddingLeft:j===0?22:0,boxSizing:'border-box',fontFamily:j<2?MONO:FONT,color:j===0&&!current&&!target?C.muted:undefined,opacity:focusColumn&&j!==1?.27:1}}>{v}</div>)}
 {target&&<div style={{position:'absolute',right:16,fontSize:24}}>✓</div>}
 </div>})}
 </div></div>;
};

const IndexTable:React.FC<{x?:number;y?:number;width?:number;active?:number;focus?:[number,number];line?:boolean;label?:string;opacity?:number}>=({x=110,y=350,width=590,active=-1,focus,line=true,label='按订单号排列',opacity=1})=><div style={{position:'absolute',left:x,top:y,width,opacity}}>
 <div style={{position:'absolute',left:0,top:-44,fontSize:23,color:C.muted,letterSpacing:2}}>{label}</div>
 <div style={{border:`1px solid ${C.teal}55`,borderRadius:16,background:C.index,overflow:'hidden'}}>
 <div style={{height:57,display:'flex',alignItems:'center',padding:'0 28px',fontSize:width<400?19:24,color:C.muted,background:C.header}}><span style={{width:'52%'}}>订单号</span><span>{width<400?'对应记录':'对应记录（示意）'}</span></div>
 {INDEX.map((d,i)=>{const on=active===i,muted=focus&&(i<focus[0]||i>focus[1]);return <div key={d.id} style={{height:52,display:'flex',alignItems:'center',padding:'0 28px',fontSize:28,fontFamily:MONO,borderTop:`1px solid ${C.teal}20`,background:on?C.success:undefined,color:on?C.teal:C.text,opacity:muted?.2:1,fontWeight:on?750:450}}><span style={{width:'52%'}}>{d.id}</span><span style={{display:'flex',alignItems:'center',gap:26}}>{line&&<span style={{color:C.teal,fontSize:23}}>→</span>}{String(d.row).padStart(2,'0')}</span></div>})}
 </div></div>;

const Pointer:React.FC<{x:number;y:number;color?:string}>=({x,y,color=C.gold})=><svg style={{position:'absolute',left:x,top:y}} width="32" height="28" viewBox="0 0 32 28"><path d="M0 4h16V0l16 14-16 14v-6H0Z" fill={color}/></svg>;
const Connector:React.FC<{progress:number}>=({progress})=><svg width="1920" height="1080" style={{position:'absolute',inset:0,pointerEvents:'none'}}><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto"><path d="M0 0L10 5L0 10Z" fill={C.teal}/></marker></defs><path d="M700 589 C820 589 820 693 933 693" fill="none" stroke={C.teal} strokeWidth="4" strokeLinecap="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1-clamp(progress)} markerEnd={progress>.97?'url(#arrow)':undefined}/></svg>;
const Subhead:React.FC<{children:React.ReactNode;x?:number;y?:number;accent?:boolean}>=({children,x=110,y=835,accent})=><div style={{position:'absolute',left:x,top:y,color:accent?C.teal:C.muted,fontSize:28,fontWeight:500}}>{children}</div>;

const getCue=(s:Shot,key:string,fallback:number)=>Number(s.cueFrames?.[key]??fallback);
const Scene:React.FC<{shot:Shot}>=({shot})=>{
 const f=useCurrentFrame(),d=shot.durationInFrames,id=parseInt(shot.id),p=clamp(f/d);
 const scanStart=getCue(shot,'scanStart',28);
 const scanPhase=clamp((f-scanStart)/Math.max(1,d-scanStart-28));
 const scanned=Math.min(8,Math.floor(scanPhase*8)+1);
 const scanRow=Math.min(7,Math.floor(scanPhase*8));
 const termScan=getCue(shot,'scanLabel',22),termIndex=getCue(shot,'indexLabel',24),locate=getCue(shot,'locate',Math.round(d*.53));
 if(id===1)return <>
  <Title>加个索引，为啥就快了？</Title>
  <Query/>
  <Table y={375} active={Math.min(7,Math.floor(f/31))} read={Math.min(8,Math.floor(f/31))}/>
  <Tag x={1435} y={150} color={C.gold}>还在查找…</Tag>
 </>;
 if(id===2)return <>
  <Title>一张表，存着一笔笔订单</Title>
  <Table y={325} active={f>d*.45?5:-1}/>
  {f<=d*.45&&<div style={{position:'absolute',left:105,top:320,width:1710,height:483,border:`2px solid ${C.teal}`,borderRadius:19,opacity:.5}}/>}
  {f>d*.45&&<><Pointer x={62} y={326+57+5*52+12}/><Tag x={1260} y={845} color={C.gold}>一行 = 一笔订单</Tag></>}
  <Note y={842}>示例 · 订单号、商品、金额与状态放在同一行</Note>
 </>;
 if(id===3)return <>
  <Title>这次，只找这一笔</Title><Query/><Table y={375} focusColumn/>
  <div style={{position:'absolute',left:960,top:777,width:680,height:2,background:C.edge}}/>
  <Note y={866}>查询条件：订单号相同</Note>
 </>;
 if(id===4){const row=Math.min(5,Math.floor(scanPhase*6));return <>
  <Title>先看：逐行检查</Title><Query/><Table y={375} active={row} read={row} found={row===5}/>
  <Pointer x={62} y={376+57+row*52+12}/>
  <Note y={866} color={row===5?C.teal:C.gold}>{row===5?'订单号相同，找到一条匹配记录':'读出订单号 → 比较是否相同 → 继续'}</Note>
 </>}
 if(id===5){const second=shot.cueFrames?.sentences?.[1]??d*.5;const row=f<second?5:f<second+(d-second)*.4?6:7;return <>
  <Title>检查完整张表</Title><Table y={340} found read={row+1} active={f>d*.9?-1:row}/>
  {f<=d*.9&&<Pointer x={62} y={341+57+row*52+12}/>}
  {f>=termScan&&<Tag x={110} y={845} color={C.gold}>全表扫描</Tag>}
  <Note x={800} y={851}>不是每一行都要返回，但每一行都要检查</Note>
 </>}
 if(id===6){const growth=ease(ramp(f,35,Math.max(30,d-85)));return <>
  <Title>记录越多，需要检查的行越多</Title>
  <Table x={110} y={350} width={900} columns={false} active={Math.min(7,Math.floor(f/26))} read={Math.min(8,Math.floor(f/26))}/>
  <div style={{position:'absolute',left:1130,top:345,width:650,height:480,border:`1px solid ${C.edge}`,borderRadius:16,overflow:'hidden',padding:'25px 30px',boxSizing:'border-box'}}>
   <div style={{fontSize:26,color:C.muted,marginBottom:20}}>更多订单记录 · 示意</div>
   <div style={{display:'grid',gridTemplateColumns:'repeat(10,1fr)',gap:8}}>{Array.from({length:100},(_,i)=><div key={i} style={{height:24,borderRadius:3,background:i<growth*100?C.edge:C.surface,opacity:i<growth*100?1:.35}}/>)}</div>
  </div>
  <svg style={{position:'absolute',left:1030,top:530}} width="75" height="60"><path d="M0 30h60m-18-18 18 18-18 18" fill="none" stroke={C.muted} strokeWidth="3"/></svg>
  <Note y={855}>要找的还是一笔，沿途却要读更多无关记录</Note>
 </>}
 if(id===7){const build=ramp(f,30,Math.max(30,d-85));return <>
  <Title>换个办法：先准备一份定位结构</Title>
  <IndexTable x={110} y={350} opacity={.3+.7*build} label="按订单号排列 · 结构示意"/>
  <Table x={940} y={350} width={870} columns={false}/>
  {INDEX.map((o,i)=>{const appear=ramp(f,30+i*(Math.max(40,d-85)/8),16);return <svg key={o.id} width="1920" height="1080" style={{position:'absolute',inset:0,opacity:.15*appear}}><path d={`M700 ${433+i*52}C800 ${433+i*52} 840 ${433+(o.row-1)*52} 940 ${433+(o.row-1)*52}`} stroke={C.teal} strokeWidth="1.5" fill="none"/></svg>})}
  <Note y={855}>编号仅表示逻辑对应关系，不是物理地址</Note>
 </>}
 if(id===8)return <>
  <Title>为订单号，准备查找结构</Title>
  <IndexTable y={350} label="按订单号排列 · 结构示意"/>
  <Table x={940} y={350} width={870} columns={false}/>
  {f>=termIndex&&<Tag x={110} y={845}>索引</Tag>}
  <Note x={950} y={851}>数据仍在原表里，编号表示对应关系</Note>
 </>;
 if(id===9){const stage=f<locate*.55?0:f<locate?1:2;return <>
  <Title>先在索引里，缩小查找范围</Title><Query x={940} width={870}/>
  <IndexTable y={350} active={stage===2?3:-1} focus={stage===0?[0,7]:stage===1?[0,3]:[3,3]} label="订单号有序 · 定位过程示意"/>
  <Table x={940} y={350} width={870} columns={false} dim/>
  <div style={{position:'absolute',left:735,top:stage===2?574:455,color:C.teal,fontSize:27,fontWeight:650}}>{stage===2?'对应记录 →':'缩小范围'}</div>
  <Note y={855}>这里只演示定位关系，实际索引结构可能不同</Note>
 </>}
 if(id===10){const linked=ramp(f,locate-24,28);return <>
  <Title>顺着位置，读取那笔订单</Title>
  <IndexTable y={350} active={3}/><Table x={940} y={350} width={870} columns found={f>=locate}/>
  <Connector progress={linked}/>
  <Note y={855} color={C.teal}>{f>=locate?'订单 7042 · 耳机 · 199 元 · 待发货':'逻辑定位信息 → 对应订单记录'}</Note>
 </>}
 if(id===11){const t=clamp((f-28)/Math.max(1,d-85)),done=t>.91;return <>
  <Title>同一笔订单，两条查找路径</Title>
  <Tag x={110} y={260} w={790} color={C.gold}>全表扫描</Tag><Tag x={1020} y={260} w={790}>索引</Tag>
  <Table x={110} y={398} width={790} columns={false} label={false} active={done?-1:Math.min(7,Math.floor(t*8))} read={Math.floor(t*8)} found={t>5/8} scale={.88}/>
  <IndexTable x={1020} y={398} width={360} active={t>.3?3:-1} label=""/>
  <div style={{position:'absolute',left:1390,top:590,fontSize:30,color:C.teal,opacity:ramp(f,Math.round(d*.4),18)}}>→</div>
  <div style={{position:'absolute',left:1430,top:545,width:380,height:190,background:C.success,border:`1px solid ${C.teal}`,borderRadius:16,padding:25,boxSizing:'border-box',lineHeight:1.2,opacity:ramp(f,Math.round(d*.43),18)}}><div style={{fontSize:24,color:C.teal,marginBottom:12}}>对应的订单记录</div><div style={{fontSize:38,fontFamily:MONO,fontWeight:700}}>7042</div><div style={{fontSize:25,marginTop:8}}>耳机 · 待发货</div></div>
  <Subhead x={110} y={883}>逐行检查原表</Subhead><Subhead x={1020} y={883} accent>先定位，再读取目标记录</Subhead>
 </>}
 if(id===12){const second=shot.cueFrames?.sentences?.[1]??d*.35;const fill=ramp(f,second,Math.max(30,d-second-35));return <>
  <Title>有索引，也要看怎么查</Title>
  <div style={{position:'absolute',left:110,top:320,width:790,height:470,border:`1px solid ${C.edge}`,borderRadius:22,background:C.surface,padding:44,boxSizing:'border-box'}}>
   <div style={{fontSize:30,color:C.teal,marginBottom:38}}>只找一小部分记录</div><div style={{display:'grid',gridTemplateColumns:'repeat(8,1fr)',gap:12}}>{Array.from({length:40},(_,i)=><div key={i} style={{height:42,borderRadius:5,background:i===21&&f>24?C.teal:C.row,border:i===21?`2px solid ${C.teal}`:undefined}}/>)}</div>
   <div style={{fontSize:31,marginTop:36}}>索引可能减少读取</div>
  </div>
  <div style={{position:'absolute',left:1020,top:320,width:790,height:470,border:`1px solid ${C.edge}`,borderRadius:22,background:C.surface,padding:44,boxSizing:'border-box'}}>
   <div style={{fontSize:30,color:C.gold,marginBottom:38}}>要取出大部分记录</div><div style={{display:'grid',gridTemplateColumns:'repeat(8,1fr)',gap:12}}>{Array.from({length:40},(_,i)=><div key={i} style={{height:42,borderRadius:5,background:i<Math.floor(35*fill)?C.gold+'66':C.row}}/>)}</div>
   <div style={{fontSize:31,marginTop:36}}>直接扫描也可能更合适</div>
  </div>
  <Note y={845}>读取范围示意 · 数据库会根据实际情况选择执行方式</Note>
 </>}
 if(id===13){const middle=d*.42,finish=d*.7;return <>
  <Title>快，来自少读无关记录</Title>
  <div style={{position:'absolute',left:110,top:310,width:1700,height:490,border:`1px solid ${C.edge}`,borderRadius:24,background:C.surface}}>
   <div style={{position:'absolute',left:60,top:80,fontSize:30,color:C.muted}}>查找订单</div><div style={{position:'absolute',left:60,top:160,fontSize:65,fontFamily:MONO,fontWeight:700,color:C.gold}}>7042</div>
   <div style={{position:'absolute',left:520,top:80,fontSize:30,color:C.teal,opacity:.25+.75*ramp(f,20,20)}}>索引</div><div style={{position:'absolute',left:520,top:170,fontSize:43,opacity:ramp(f,30,20)}}>定位记录</div>
   <div style={{position:'absolute',left:1110,top:80,fontSize:30,color:C.teal}}>订单表</div><div style={{position:'absolute',left:1110,top:166,fontSize:49,opacity:ramp(f,middle,20)}}>耳机</div><div style={{position:'absolute',left:1110,top:250,fontSize:30,color:C.muted,opacity:ramp(f,middle,20)}}>199 元 · 待发货</div>
   <svg width="1700" height="490" style={{position:'absolute',inset:0}}><path d="M290 195h145m-20-14 20 14-20 14" fill="none" stroke={C.teal} strokeWidth="4" opacity={ramp(f,20,20)}/><path d="M835 195h160m-20-14 20 14-20 14" fill="none" stroke={C.teal} strokeWidth="4" opacity={ramp(f,middle,20)}/></svg>
   <div style={{position:'absolute',left:60,top:375,fontSize:29,color:C.muted,opacity:ramp(f,finish,18)}}>结果没变，查找路径变了。</div>
  </div>
  <Note y={845}>示例数据 · 核心是减少不必要的读取</Note>
 </>}
 const nextStart=shot.cueFrames?.sentences?.[1]??d*.25,brandStart=shot.cueFrames?.sentences?.[2]??d*.7;
 return <>
  <Title>{f<nextStart?'找得到数据，还得改得对':'下一期：扣了钱，对方没到账？'}</Title>
  {f<nextStart?<Table y={340} found/>:<div style={{position:'absolute',left:110,top:340,width:1700,height:420,border:`1px solid ${C.edge}`,borderRadius:24,background:C.surface,display:'flex',alignItems:'center',padding:'0 80px',boxSizing:'border-box',opacity:ease(ramp(f,nextStart,15))}}>
   <div><div style={{fontSize:27,color:C.muted,marginBottom:22}}>下一期</div><div style={{fontSize:66,fontWeight:750,lineHeight:1.5}}>扣了钱，<br/><span style={{color:C.gold}}>对方没到账？</span></div></div>
   <div style={{marginLeft:'auto',display:'flex',alignItems:'center',gap:35,fontSize:28}}><div style={{padding:'35px 50px',border:`1px solid ${C.edge}`,borderRadius:16,color:C.gold}}>扣款</div><span style={{color:C.muted}}>→</span><div style={{padding:'35px 50px',border:`1px solid ${C.edge}`,borderRadius:16,color:C.teal}}>到账？</div></div>
  </div>}
  <div style={{position:'absolute',top:843,left:110,fontSize:32,fontWeight:600,color:C.muted,opacity:ramp(f,brandStart,16)}}>IT小村 · 原创</div>
 </>;
};

export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot,captions})=>{
 const f=useCurrentFrame();
 const sub=shot.subtitles?.find(s=>f>=s.from&&f<=(s.to??s.from+(s.duration??1)-1));
 return <AbsoluteFill data-mysql-canvas="true" style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
 <MysqlBackdrop/><MysqlHeader ep="EP.15" scope="MySQL 8.4 · InnoDB"/>
  <div style={{position:'absolute',right:110,top:112,fontSize:19,color:C.muted,letterSpacing:1}}>示例数据 · 结构示意 · 非性能实测</div>
  <Scene shot={shot}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:42,fontWeight:500,lineHeight:1.3,textAlign:'center',background:`${C.bg}F7`,borderRadius:14}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=> <AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(shot=><Sequence key={shot.id} name={shot.id} from={shot.from} durationInFrames={shot.durationInFrames}><ShotView shot={shot} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
