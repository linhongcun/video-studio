import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots} from './data';
import {C,FONT} from './theme';
import {at} from './motion';
import {Title,Note,Reset,Text,Actor,Graph,Path,Packet,Transfer,Check,Cross,Evidence,ease,lerp,clamp} from './objects';
declare const __HAS_VOICE_AUDIO__:boolean;
const phase=(s:Shot,f:number,i:number,a=.06,b=.72)=>ease(f,at(s,i,a),at(s,i,b)-at(s,i,a));
const reached=(s:Shot,f:number,i:number,r=.6)=>f>=at(s,i,r);
const termAt=(s:Shot,key:string)=>Number(s.cueFrames?.labels?.[key]??Math.max(1,Number(s.cueFrames?.sentences?.[0]??9)-2));
const FlatOrder=({x=1460,y=350,known=false,used=false,focus=false,alpha=1}:{x?:number;y?:number;known?:boolean;used?:boolean;focus?:boolean;alpha?:number})=><Actor x={x} y={y} w={520} h={310} name="订单 8124" caption={used?'本单资料 · 标注信息来源':'示例订单 · 当前实际状态'} active={focus} color={focus?C.gold:C.text} alpha={alpha} lines={[known?'签收：3 天':'签收：尚未查询',used?'使用：用户补充未使用':known?'使用：未知':'使用：尚未查询','退款：未执行']}/>;
const Advice=({x=510,y=350,ready=false,alpha=1}:{x?:number;y?:number;ready?:boolean;alpha?:number})=><Actor x={x} y={y} w={620} h={310} name={ready?'回复建议':'回复内容'} caption={ready?'依据已查询资料与用户陈述':'问题：这单能申请退款吗？'} active color={ready?C.teal:C.gold} alpha={alpha} lines={ready?['按当前资料，可以申请','建议 ≠ 退款到账']:['可以申请退款']}/>;
const flow=({s,f,i,text,x1,x2,color=C.gold,start=.06,end=.72,y=700,w=340}:{s:Shot;f:number;i:number;text:string;x1:number;x2:number;color?:string;start?:number;end?:number;y?:number;w?:number})=><Transfer text={text} x1={x1} x2={x2} p={phase(s,f,i,start,end)} color={color} y={y} w={w} alpha={f>=at(s,i,start)?1:0}/>;
const ChoiceRow=({text,y,active=false,alpha=1}:{text:string;y:number;active?:boolean;alpha?:number})=><div style={{position:'absolute',left:1090,top:y,width:560,height:66,background:active?`${C.teal}12`:C.bg,borderLeft:`3px solid ${active?C.teal:C.edge}`,opacity:alpha}}><Text x={20} y={12} w={520} size={29} color={active?C.teal:C.text}>{text}</Text></div>;

const Scene:React.FC<{s:Shot;f:number}>=({s,f})=>{
 const id=Number(s.id);
 if(id===1){
  const p=phase(s,f,0,.15,.65),q=phase(s,f,1,.08,.6);
  return <><Title>会回答，就能办事？</Title><Advice/><FlatOrder focus={q>.3}/>
   <Path x1={850} x2={1130} y={520} p={p} color={C.gold} dashed/>
   <Cross x={1000} y={520} alpha={p}/><Packet x={1000} y={685} w={540} color={C.gold} alpha={q}>建议给出了，订单没有变化</Packet>
   <Note>一句“可以申请”，究竟代表什么？</Note></>;
 }
 if(id===2){
  const p=phase(s,f,0,.05,.65),q=phase(s,f,1,.06,.65);
  return <><Title>先看同一笔退款咨询</Title><Reset>同一订单 · 同一个问题</Reset>
   <FlatOrder/><Packet x={lerp(-330,560,p)} y={365} w={770} color={C.blue}>用户：这单能申请退款吗？</Packet>
   <Actor x={370} y={530} w={320} h={200} name="申请建议" lines={[q>.5?'需要依据':'待判断']} color={C.gold} active={q>.2}/>
   <Actor x={790} y={530} w={320} h={200} name="退款执行" lines={['未发生']} color={C.muted}/>
   <Note alpha={q}>先把“给出建议”和“改变订单”分开</Note></>;
 }
 if(id===3){
  const p=phase(s,f,0,.03,.65),q=phase(s,f,1,.03,.7);
  return <><Title>本片只查询资料，最后给建议</Title><Reset>教学示例 · 不连接真实退款系统</Reset>
   <Actor x={400} name="查订单" caption="只读" lines={['读取订单 8124']} active color={C.teal} alpha={p}/>
   <Actor x={960} name="查规则" caption="只读" lines={['读取对应示例规则']} active color={C.teal} alpha={p}/>
   <Actor x={1520} name="执行退款" caption="本片未提供" lines={['退款：未执行']} color={C.muted} alpha={q}/>
   <Path x1={400} x2={960} y={700} p={p} color={C.teal}/>
   <Cross x={1300} y={700} alpha={q}/><Note alpha={q}>查询和规则都是示例，写操作没有接入</Note></>;
 }
 if(id===4){
  const visible=f>=termAt(s,'模型'),p=phase(s,f,0,.1,.65),q=phase(s,f,1,.05,.65);
  return <><Title>{visible?'模型：接收信息，生成回复':'谁在生成这段回复？'}</Title>
   <Actor x={510} y={355} w={650} h={290} name={visible?'模型':'回答的生成方'} caption="本次提供的信息" lines={p>.45?['这单能申请退款吗？','回复：可以先核对申请条件']:['等待输入']} active={visible} color={C.blue}/>
   <FlatOrder focus={q>.5}/>
   {flow({s,f,i:0,text:'用户提供的问题',x1:160,x2:510,color:C.blue,start:.03,end:.34,y:700,w:360})}
   <Text x={1170} y={695} w={570} size={29} center color={C.gold} alpha={q}>查询记录：空</Text>
   <Note alpha={q}>没有本单的查询结果，不能靠回复确认本单状态</Note></>;
 }
 if(id===5){
  const p=phase(s,f,0,.1,.7),q=phase(s,f,1,.05,.7);
  return <><Title>一般说明，不等于这一单的事实</Title>
   <Actor x={510} y={355} w={650} h={290} name="模型" caption="一般说明" lines={['申请通常需要满足条件']} color={C.muted} alpha={1-p*.65}/>
   <FlatOrder focus={q>.1}/>
   <Packet x={lerp(510,1000,q)} y={690} w={630} color={C.gold} alpha={q}>判断订单 8124，需要本单资料</Packet>
   <Note alpha={q}>签收多久？是否使用？都要有信息来源</Note></>;
 }
 if(id===6){
  const p=phase(s,f,0,.03,.7),q=phase(s,f,1,.06,.6);
  return <><Title>应用把可用的查询能力交给模型</Title>
   <Actor x={370} name="模型" lines={reached(s,f,0,.65)?['收到问题','收到能力说明']:['等待输入']} active color={C.blue}/>
   <Actor x={960} name="执行程序" caption="应用的一部分" lines={['用户的问题','可用查询说明']} active={p<.6} color={C.gold} alpha={p}/>
   <Actor x={1550} name="查询入口" caption="两种只读能力" lines={['查订单','查规则']} active color={C.teal} alpha={q}/>
   {flow({s,f,i:0,text:'问题 + 查询能力说明',x1:960,x2:370,color:C.blue,start:.08,end:.65,w:470})}
   <Note alpha={q}>本例只提供查询，未提供退款执行能力</Note></>;
 }
 if(id===7){
  const visible=f>=termAt(s,'工具'),p=phase(s,f,1,.03,.38),q=phase(s,f,1,.43,.8);
  return <><Title>{visible?'工具：让程序查询外部信息':'请求和执行，要分开看'}</Title>
   <Graph model={['提出调用请求']} program={q>.1?['执行查询']:['接收请求']} tool={['订单 / 规则']} toolName={visible?'查询工具':'查询入口'} focus={q>.1?'tool':p>.1?'program':'model'} color={C.gold}/>
   {f>=at(s,1,.03)&&f<at(s,1,.43)?<Transfer text="调用请求" x1={370} x2={960} p={p} color={C.gold}/>:f>=at(s,1,.43)?<Transfer text="程序执行查询" x1={960} x2={1550} p={q} color={C.teal}/>:null}
   <Note>模型提出要做什么，执行程序负责真正调用</Note></>;
 }
 if(id===8){
  const checked=reached(s,f,1,.45),p=phase(s,f,0,.05,.75),q=phase(s,f,1,.5,.85);
  return <><Title>第一步：请求查询订单 8124</Title>
   <Graph model={['请求：查订单 8124']} program={f>=at(s,1,.05)?[reached(s,f,1,.2)?'订单编号：通过':'订单编号：检查中',checked?'读取权限：通过':'读取权限：待检查']:[p>=.99?'请求待校验':'等待调用请求']} tool={q>=.99?['接收本单查询']:['等待合法查询']} toolName="订单查询" focus={checked?'tool':p>.5?'program':'model'} color={C.teal}/>
   {f<at(s,1,.5)?<Transfer text="订单编号 8124" x1={370} x2={960} p={p} color={C.gold} alpha={f>=at(s,0,.05)?1:0}/>:<Transfer text="校验通过 · 执行查询" x1={960} x2={1550} p={q} color={C.teal} w={440}/>}
   <Note alpha={phase(s,f,1,.08,.5)}>编号和读取权限通过以后，查询才会执行</Note></>;
 }
 if(id===9){
  const p=phase(s,f,0,.04,.7),q=phase(s,f,1,.04,.55);
  return <><Title>查询返回：已签收，仍有未知信息</Title>
   <Graph model={['等待查询结果']} program={reached(s,f,0,.85)?['接收到订单结果']:['查询结果返回中']} tool={['签收：3 天',q>.25?'使用：未知':'使用：待显示','退款：未执行']} toolName="订单 8124" focus={q>.2?'tool':'program'} color={q>.2?C.gold:C.teal}/>
   {flow({s,f,i:0,text:'订单结果：签收 3 天',x1:1550,x2:960,color:C.teal,w:430,start:.3,end:.85})}
   <Note alpha={q} color={C.gold}>记录没有使用情况，不能直接填成“未使用”</Note></>;
 }
 if(id===10){
  const p=phase(s,f,0,.02,.72),q=phase(s,f,1,.05,.65);
  return <><Title>结果回到模型，才有下一步的依据</Title>
   <Graph model={p>=.99?[q>.45?'下一步：查规则':'收到订单结果','签收 3 天 · 使用未知']:['等待本单事实']} program={['传递查询结果']} tool={['签收：3 天','使用：未知','退款：未执行']} toolName="订单 8124" focus={p>.5?'model':'program'} color={C.blue}/>
   {flow({s,f,i:0,text:'签收 3 天 · 使用未知',x1:960,x2:370,color:C.blue,w:450})}
   <Note alpha={q}>还缺什么？本例接下来选择查询退款规则</Note></>;
 }
 if(id===11){
  const first=phase(s,f,0,.04,.8),second=phase(s,f,1,.05,.8),returned=second>=.99;
  return <><Title>下一步：读取对应的退款规则</Title>
   <Graph model={returned?['收到规则原文']:['请求：查退款规则']} program={returned?['规则结果已回传']:second>0?[second<.5?'接收规则结果':'向模型回传结果']:first>.5?['执行规则查询']:['接收查询请求']} tool={first>=.99?['原文已返回']:['对应订单的示例政策']} toolName="规则查询" focus={returned?'model':first>.6?'tool':'program'} color={C.teal}/>
   {f<at(s,1,.05)?first<.5?<Transfer text="查退款规则请求" x1={370} x2={960} p={first*2} color={C.gold} w={370}/>:<Transfer text="程序执行规则查询" x1={960} x2={1550} p={(first-.5)*2} color={C.teal} w={430}/>:second<.5?<Transfer text="规则原文" x1={1550} x2={960} p={second*2} color={C.blue} w={370}/>:<Transfer text="规则结果回传" x1={960} x2={370} p={(second-.5)*2} color={C.blue} w={370}/>}
   <Note>查询与回传都经过执行程序，模型没有直接改动订单</Note></>;
 }
 if(id===12){
  const p=phase(s,f,0,.04,.75),q=phase(s,f,1,.04,.7);
  return <><Title>时间条件满足，使用情况还缺证据</Title><Reset>以下为示例政策，不代表实际商家规则</Reset>
   <Actor x={500} y={365} w={600} h={330} name="订单 8124" caption="已查询到的事实" lines={['签收：3 天','使用：未知','申请资格：待判断']} active color={C.gold}/>
   <Evidence x={1110} y={350} w={650} title="示例退款规则 · 同时满足" rows={p>.6?['签收 7 天内','未使用 → 可以申请']:['签收 7 天内']} highlight={q>.2?0:-1} alpha={p}/>
   <Check x={1740} y={445} alpha={q}/>
   <Packet x={1425} y={655} w={630} color={C.gold} alpha={q}>时间：已满足　使用：待补充</Packet>
   <Note alpha={q} color={C.gold}>已知一项条件，不代表全部条件已经满足</Note></>;
 }
 if(id===13){
  const p=phase(s,f,0,.03,.8),q=phase(s,f,1,.05,.65);
  return <><Title>缺信息，就先问用户</Title>
   <Graph model={['选择：询问使用情况']} program={['把询问交给用户']} tool={q>.2?['等待用户补充']:['尚未回答']} toolName="用户" toolCaption="补充缺失信息" focus={q>.2?'tool':'model'} color={C.gold}/>
   <Transfer text="商品有没有使用过？" x1={370} x2={1550} p={p} color={C.blue} alpha={f>=at(s,0,.03)?1:0} w={460}/>
   <Note alpha={q} color={C.gold}>这一轮停在等待补充，没有继续编造事实</Note></>;
 }
 if(id===14){
  const visible=f>=termAt(s,'智能体'),p=phase(s,f,0,.03,.8),q=phase(s,f,1,.03,.7);
  const step=Math.min(2,Math.floor(p*3)),segments=[[370,960,'请求'],[960,1550,'执行'],[1550,370,'结果反馈']] as const;
  const seg=segments[step],sp=clamp(p*3-step);
  return <><Title>{visible?'智能体：连接选择、执行与结果反馈':'这些步骤，怎样连接起来？'}</Title><Reset>回看已发生的查询过程 · 当前仍等待用户补充</Reset>
   <Graph model={['依据已得到的信息','当前：等待用户补充']} program={['校验并执行允许动作']} tool={['提供查询结果']} toolName="查询与外部输入" toolCaption="查询结果与用户反馈" focus={step===0?'model':step===1?'program':'tool'} color={C.teal}/>
   {visible&&<svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><rect x={130} y={315} width={1660} height={445} rx={23} stroke={C.teal} strokeWidth={2} fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1-p}/></svg>}
   {visible&&<Transfer text={seg[2]} x1={seg[0]} x2={seg[1]} p={sp} color={step===2?C.blue:C.gold} y={690} w={330}/>}
   <Note alpha={q}>在应用允许的动作中，根据返回结果继续选择</Note></>;
 }
 if(id===15){
  const p=phase(s,f,0,.05,.75),q=phase(s,f,1,.06,.65),arrived=p>=.99;
  return <><Title>用户补充以后，带着已有信息继续</Title>
   <Graph model={arrived?['签收 3 天','规则 + 用户补充']:['等待用户回答']} program={['合并本轮可用信息']} tool={['用户补充：未使用']} toolName="用户回答" toolCaption="补充缺失信息" focus={arrived?'model':'program'} color={C.blue}/>
   <Transfer text="用户补充：没有使用过" x1={1550} x2={370} p={p} color={C.blue} w={480} alpha={f>=at(s,0,.05)?1:0}/>
   <Note alpha={q}>未使用来自用户陈述；订单和规则查询结果继续保留</Note></>;
 }
 if(id===16){
  const p=phase(s,f,0,.07,.65),q=phase(s,f,1,.06,.6);
  return <><Title>建议有了依据，退款仍未执行</Title>
   <Advice ready alpha={p}/><FlatOrder known used focus={q>.3}/>
   <Check x={525} y={705} alpha={p}/>
   <Text x={1170} y={705} w={580} size={29} color={C.gold} center alpha={q}>实际退款状态保持不变</Text>
   <Note alpha={q}>按当前查询与用户陈述，可以申请；这不是退款到账</Note></>;
 }
 if(id===17){
  const p=phase(s,f,0,.05,.75),q=phase(s,f,1,.05,.7);
  return <><Title>预写程序路径，也能有条件分支</Title><Reset>切到架构对比示意 · 不重演一次退款</Reset>
   <Actor x={320} y={390} w={310} h={180} name="查订单" lines={['预先规定']} active color={C.blue}/>
   <Actor x={780} y={390} w={310} h={180} name="查规则" lines={['预先规定']} active={p>.35} color={C.blue}/>
   <Actor x={1190} y={390} w={310} h={180} name="判断使用情况" lines={['预先写好分支']} active={q>.1} color={C.gold}/>
   <Path x1={485} x2={610} y={480} p={p} color={C.blue}/><Path x1={945} x2={1020} y={480} p={p} color={C.blue}/>
   <svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:q}}><path d="M1355 480 H1420 V375 H1480 M1420 480 V625 H1480" fill="none" stroke={C.gold} strokeWidth={3}/></svg>
   <Packet x={1620} y={343} w={300} color={C.teal} alpha={q}>已知：给建议</Packet>
   <Packet x={1620} y={593} w={300} color={C.gold} alpha={q}>未知：先询问</Packet>
   <Note alpha={q}>能不能查资料、有多少分支，都不是这一区分的关键</Note></>;
 }
 if(id===18){
  const p=phase(s,f,0,.06,.7),q=phase(s,f,1,.08,.7);
  return <><Title>关键是：下一步由谁决定？</Title><Reset>同一问题 · 比较控制方式</Reset>
   <Actor x={500} y={350} w={650} h={330} name="预先规定路径" caption="程序定义查询与条件分支" lines={['查订单 → 查规则','使用情况未知 → 询问']} active={p<.6} color={C.blue}/>
   <Text x={1090} y={350} w={650} size={34} color={C.teal} weight={650}>模型根据结果选择</Text>
   <ChoiceRow text="查规则" y={425} active={p>.35&&q<.3}/><ChoiceRow text="询问用户" y={505} active={q>.3}/><ChoiceRow text="信息足够时给建议" y={585}/>
   <Packet x={960} y={710} w={1470} color={C.gold} alpha={q}>应用仍控制：可用动作、读取权限与运行次数</Packet>
   <Note alpha={q}>允许动态选择，也要有应用程序的边界</Note></>;
 }
 if(id===19){
  const p=phase(s,f,0,.05,.7),q=phase(s,f,1,.04,.7);
  return <><Title>模型说“完成”，还要核对系统结果</Title><Reset>回到本片订单 8124 · 仍只做查询与建议</Reset>
   <Actor x={440} y={355} w={520} h={300} name="申请建议" caption="本次已完成的目标" lines={['有查询与陈述依据','建议：可以申请']} active color={C.teal}/>
   <Actor x={1010} y={355} w={440} h={300} name="执行退款" caption="本片未提供写入能力" lines={['没有执行动作']} color={C.muted} alpha={p}/>
   <Actor x={1550} y={355} w={490} h={300} name="订单 8124" caption="实际结果" lines={['退款：未执行']} active={q>.3} color={C.gold}/>
   <Path x1={1230} x2={1290} y={520} p={p} color={C.muted} dashed/><Cross x={1260} y={520} alpha={p}/>
   <Packet x={960} y={700} w={1100} color={C.gold} alpha={q}>建议完成 ≠ 退款完成</Packet>
   <Note alpha={q}>真正改变订单，需要另有允许的动作，并核对实际结果</Note></>;
 }
 const p=phase(s,f,0,.05,.8),q=phase(s,f,1,.03,.65),step=Math.min(2,Math.floor(p*3));
 const names=['查询请求','程序执行','结果返回'];
 return <><Title>沿着请求、执行和结果去检查</Title>
  <Graph model={['选择下一步']} program={['实际执行查询']} tool={['返回可核对资料']} toolName="查询结果" focus={step===0?'model':step===1?'program':'tool'} color={C.teal} alpha={1-q}/>
  <Packet x={lerp(370,1550,p)} y={690} w={380} color={C.teal} alpha={1-q}>{names[step]}</Packet>
  <div style={{position:'absolute',left:lerp(1940,300,q),top:380,width:1320,height:300,background:C.bg,borderTop:`3px solid ${C.teal}`,borderBottom:`2px solid ${C.edge}`}}>
   <Text x={35} y={35} w={1250} size={37} color={C.teal} center>本片确实完成：有依据的申请建议</Text>
   <Text x={35} y={125} w={1250} size={37} color={C.gold} center>本片没有执行：退款</Text>
   <Text x={35} y={217} w={1250} size={27} color={C.muted} center>能否办成事，要由实际结果证明</Text>
  </div>
  <Note color={C.teal}>看清模型做了什么，也看清执行程序真正做了什么</Note>
  <Text x={620} y={884} w={680} size={23} color={C.muted} center alpha={q}>IT小村 · 原创</Text>
 </>;
};

const chapters:Record<string,[number,string]>={conflict:[1,'回答了，还是办好了'],roles:[2,'回答与执行的分工'],loop:[3,'拿到结果，再选下一步'],choice:[4,'谁决定下一步'],verify:[5,'怎样才算真的完成']};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot:s,captions})=>{
 const f=useCurrentFrame(),[n,label]=chapters[s.chapterId]??[1,'概念入门'];
 const sub=s.subtitles?.find(v=>f>=v.from&&f<=(v.to??v.from+(v.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 85% 5%, #173B5555, transparent 62%)'}}/>
  <Text x={100} y={54} w={900} size={24} color={C.muted}>人工智能 · 概念入门</Text>
  <Text x={100} y={98} w={1250} size={21} color={C.teal}>{String(n).padStart(2,'0')} / 05 · {label}</Text>
  <div style={{position:'absolute',left:100,top:140,display:'flex',gap:9}}>{[1,2,3,4,5].map(i=><div key={i} style={{width:i===n?65:26,height:4,borderRadius:4,background:i===n?C.teal:C.edge}}/>)}</div>
  <Text x={1700} y={54} w={150} size={25}>IT小村</Text><Text x={1480} y={103} w={370} size={19} color={C.muted} center>示例数据 · 订单 8124</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,minHeight:100,display:'flex',alignItems:'center',justifyContent:'center',fontSize:40,fontWeight:500,lineHeight:1.4,textAlign:'center',background:`${C.bg}F8`,borderRadius:12,padding:'7px 15px',boxSizing:'border-box'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
