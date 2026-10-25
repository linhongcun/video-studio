import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {Shot,shots} from './data';
import {C,FONT,MONO} from './theme';
import {at} from './motion';
import {Text,Title,Note,Transit,Packet,Arrow,Tick,ease,clamp,lerp} from './objects';
import {Chat} from './Chat';
declare const __HAS_VOICE_AUDIO__:boolean;
const phase=(s:Shot,f:number,i:number,a:number,b:number)=>ease(f,at(s,i,a),Math.max(1,at(s,i,b)-at(s,i,a)));
const cue=(s:Shot,term:string)=>Number(s.cueFrames?.labels?.[term]??0);
const X={model:420,program:965,system:1510};
const Role=({x,label,lines=[],active=false,color=C.blue,alpha=1}:{x:number;label:string;lines?:string[];active?:boolean;color?:string;alpha?:number})=><div style={{position:'absolute',left:x-235,top:355,width:470,height:259,opacity:alpha,borderTop:`3px solid ${active?color:C.edge}`,borderBottom:`2px solid ${active?color:C.edge}`,background:active?`linear-gradient(180deg,${color}15,transparent)`:'transparent'}}>
 <Text x={10} y={24} w={450} size={34} color={active?color:C.text} center weight={700}>{label}</Text>
 {lines.map((line,i)=><Text key={i} x={12} y={107+i*52} w={446} size={29} color={active?color:C.muted} center>{line}</Text>)}
</div>;
const Roles=({model=[],program=[],system=[],focus='',modelNamed=true,formalProgram=true}:{model?:string[];program?:string[];system?:string[];focus?:string;modelNamed?:boolean;formalProgram?:boolean})=><>
 <Role x={X.model} label={modelNamed?'模型':'助手的选择与回答'} lines={model} active={focus==='model'} color={C.blue}/>
 <Role x={X.program} label={formalProgram?'咨询应用 · 应用程序':'咨询应用 · 程序'} lines={program} active={focus==='program'} color={C.gold}/>
 <Role x={X.system} label="订单系统" lines={system} active={focus==='system'} color={C.teal}/>
</>;
const transfer=(text:string,from:keyof typeof X,to:keyof typeof X,p:number,color=C.gold,w=440)=><Transit text={text} x1={X[from]} x2={X[to]} p={p} y={708} color={color} w={w}/>;
const Context=({children,color=C.muted}:{children:React.ReactNode;color?:string})=><Text x={130} y={270} w={1660} size={27} color={color}>{children}</Text>;
const StepMap=()=> <>
 {[['提出请求',350],['应用检查',755],['实际查询',1160],['交回结果',1565]].map(([label,x],i)=><React.Fragment key={String(label)}>
  {i>0&&<Arrow x1={Number(x)-260} x2={Number(x)-140} y={850} color={i===1?C.gold:C.edge}/>}
  <Text x={Number(x)-130} y={827} w={260} size={30} color={i===1?C.gold:C.muted} center weight={i===1?700:500}>{label}</Text>
 </React.Fragment>)}
 <Text x={640} y={882} w={230} size={22} color={C.gold} center>回到这个关口</Text>
</>;
const Scene=({s,f}:{s:Shot;f:number})=>{
 const id=Number(s.id);
 if(id===1){const reveal=f>=54;return <>
  <Title>谁在查这笔订单？</Title><Chat compact showState={f>=24}/>
  <div style={{position:'absolute',left:1320,top:400,width:470,height:266,borderTop:`3px solid ${reveal?C.gold:C.edge}`,borderBottom:`2px solid ${C.edge}`,background:reveal?`${C.gold}08`:'transparent'}}>
   <Text x={15} y={30} w={440} size={37} center weight={700}>订单系统</Text>
   <Text x={15} y={128} w={440} size={39} color={reveal?C.gold:C.muted} center>{reveal?'尚未收到查询':'等待查询'}</Text>
  </div>
  <Text x={1315} y={730} w={480} size={28} color={C.muted} alpha={reveal?1:0} center>停在调用请求刚生成时</Text>
  <Text x={1320} y={802} w={470} size={34} color={C.gold} alpha={reveal?1:0} center>中间还差谁动手？</Text>
 </>;}
 if(id===2){const sent=phase(s,f,0,.48,.88),focus=phase(s,f,1,.08,.35),named=f>=cue(s,'模型');return <>
  <Title>先回到这次查询的开始</Title><Context>回到开始 · 用户 A 有读取权限 · 本例为自定义只读工具</Context>
  <Roles model={sent>=1?['收到用户问题','收到查询工具说明']:['等待输入']} program={['发送问题 + 工具说明']} system={['尚未收到查询']} focus={focus>.2?'model':'program'} modelNamed={named} formalProgram={false}/>
  {f>=at(s,0,.48)&&transfer('用户问题 + 工具说明','program','model',sent,C.blue,505)}
  <div style={{opacity:focus,position:'absolute',left:180,top:753,width:1560,height:96,borderLeft:`3px solid ${C.blue}`,background:`${C.blue}0D`}}><Text x={28} y={20} w={1504} size={35} color={C.blue}>工具：查询订单　｜　需要的参数：订单号</Text></div>
 </>;}
 if(id===3){const move=phase(s,f,0,.12,.82),detail=phase(s,f,1,.08,.24),label=f>=cue(s,'工具调用请求');return <>
  <Title>请求里只有工具和参数</Title><Context>模型已得到工具说明 · 订单资料还没有查到</Context>
  <Roles model={['选择：查询订单']} program={[move>=1?'收到调用请求':'等待调用请求']} system={['尚未收到查询']} focus={move>=1?'program':'model'} formalProgram={false}/>
  {label&&transfer('工具调用请求 · 订单 8124','model','program',move,C.gold,535)}
  <div style={{opacity:detail,position:'absolute',left:180,top:775,width:1560,height:90,display:'flex',alignItems:'center',borderLeft:`3px solid ${C.gold}`,background:`${C.gold}09`}}><Text x={22} y={18} w={620} size={32} color={C.gold}>查询订单　订单号：8124</Text><div style={{position:'absolute',left:695,top:24,fontFamily:MONO,fontSize:28,color:C.muted}}>get_order(order_id="8124")</div></div>
 </>;}
 if(id===4){const formal=f>=cue(s,'应用程序'),a=f>=at(s,0,.32),b=f>=at(s,0,.56),c=f>=at(s,0,.80),handoff=phase(s,f,1,.12,.72);return <>
  <Title>咨询应用先检查，再执行</Title><Context>工具说明让模型知道“能请求什么” · 权限由应用检查</Context>
  <Roles model={['已提出查询请求']} program={[]} system={['尚未收到查询']} focus="program" formalProgram={formal}/>
  {[[a,'工具允许使用'],[b,'参数符合要求'],[c,'当前用户有读取权限']].map(([ok,text],i)=><React.Fragment key={i}><Text x={770} y={447+i*48} w={377} size={27} color={ok?C.teal:C.muted}>{ok?'✓  ':'○  '}{text}</Text></React.Fragment>)}
  <Packet x={X.program} y={671} color={C.gold} w={650}>请求：查询订单 8124</Packet>
  <Text x={535} y={784} w={860} size={38} color={C.teal} alpha={handoff} center>检查通过 → 交给真正的查询代码</Text>
 </>;}
 if(id===5){const out=phase(s,f,0,.08,.78),back=phase(s,f,1,.15,.79),created=f>=at(s,1,.15);return <>
  <Title>真正的请求，现在才发出</Title><Context>同一查询 · 用户 A · 读取权限已通过</Context>
  <Roles model={['等工具返回资料']} program={back>=1?['收到：已签收 3 天']:['运行真正的查询代码']} system={out>=1?['本次收到查询：1 次',created?'查到：已签收 3 天':'正在读取订单']:['本次收到查询：0 次']} focus={back>=1?'program':out>=1?'system':'program'}/>
  {created?transfer('查询结果：已签收 3 天','system','program',back,C.teal,520):transfer('真正查询：订单 8124','program','system',out,C.teal,490)}
  <Note color={C.teal}>{back>=1?'返回先抵达应用程序':'只读查询 · 没有退款操作'}</Note>
 </>;}
 if(id===6){const back=phase(s,f,1,.10,.80);return <>
  <Title>把结果交回这一次调用</Title><Context>结果关联到原调用 · 相同标记表示同一次查询</Context>
  <Roles model={back>=1?['收到本次查询结果']:['仍在等查询结果']} program={back>=1?['本次结果已交回']:['持有：已签收 3 天']} system={['本次收到查询：1 次']} focus={back>=1?'model':'program'}/>
  <Text x={205} y={634} w={430} size={24} color={C.blue} center>调用标识：call_demo_01</Text><Text x={750} y={634} w={430} size={24} color={C.blue} center>调用标识：call_demo_01</Text>
  {f>=at(s,1,.10)?transfer('本次结果：已签收 3 天','program','model',back,C.blue,540):<Packet x={X.program} y={674} w={540} color={C.teal}>本次结果：已签收 3 天</Packet>}
  <Note color={C.blue}>调用标识把“这次请求”和“这份结果”对应起来</Note>
 </>;}
 if(id===7){const reply=phase(s,f,0,.42,.82),evidence=phase(s,f,1,.05,.18);return <>
  <Title>查到资料以后，再回答用户</Title><Chat state="success" showReply={reply>0} replyAlpha={reply}/>
  <Text x={130} y={243} w={1660} size={26} color={C.teal} alpha={evidence}>本次执行记录：已向订单系统查询 1 次　→　返回：签收 3 天</Text>
 </>;}
 if(id===8){const start=phase(s,f,1,.10,.80);return <>
  <Title>另一次演示：新用户，没有权限</Title><Context color={C.gold}>新用户 B · 新会话 · 上一次查询资料已清空</Context>
  <Roles model={['重新提出同一查询']} program={start>=1?['检查本次读取权限']:['等待新调用请求']} system={['本次收到查询：0 次','本次订单资料：空']} focus={start>=1?'program':'model'}/>
  {f>=at(s,1,.10)&&transfer('新请求：查询订单 8124','model','program',start,C.gold,525)}
  <StepMap/>
 </>;}
 if(id===9){const denied=f>=at(s,0,.55);return <>
  <Title>检查未通过，查询就停在这里</Title><Context color={C.gold}>另一次演示 · 用户 B 没有读取这笔订单的权限</Context>
  <Roles model={['已经提出调用请求']} program={[denied?'读取权限：未通过':'检查当前用户权限',denied?'请求被程序拦住':'']} system={['本次收到查询：0 次','本次订单资料：空']} focus="program"/>
  <Packet x={X.program} y={679} w={535} color={denied?C.red:C.gold}>{denied?'权限未通过 · 未发起查询':'查询订单 8124 的请求'}</Packet>
  {denied&&<><svg width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d="M1264 683v82" stroke={C.red} strokeWidth={7} strokeLinecap="round"/></svg><Text x={1290} y={699} w={480} size={29} color={C.muted} center>没有向订单系统发出请求</Text></>}
  <Note color={denied?C.red:C.gold}>调用请求已经生成，也可能在执行前被拒绝</Note>
 </>;}
 if(id===10){const returned=phase(s,f,0,.08,.40),reply=phase(s,f,0,.56,.72);return <>
  <Title>交回的是失败，没有订单资料</Title>
  {reply<1?<><Context color={C.red}>用户 B · 新会话 · 本次没有执行订单查询</Context><Roles model={returned>=1?['收到权限失败']:['等待本次调用结果']} program={['生成本次权限失败']} system={['本次收到查询：0 次']} focus={returned>=1?'model':'program'}/>{transfer('本次失败：没有读取权限','program','model',returned,C.red,555)}</>:<Chat user="用户 B" state="denied" showReply/>}
  <Text x={130} y={243} w={1660} size={26} color={C.red} alpha={reply>=1?1:0}>没有订单资料　｜　本次执行记录：未查询　｜　失败来自应用检查</Text>
 </>;}
 const progress=phase(s,f,0,.25,.65),evidence=phase(s,f,1,.10,.25);
 return <>
  <Title>调用请求，不等于执行结果</Title><Context>回到开头那一刻 · 本例为自定义只读查询工具</Context>
  <div style={{position:'absolute',left:170,top:350,width:1580,height:150,borderLeft:`4px solid ${C.gold}`,background:`${C.gold}08`}}><Text x={28} y={23} w={1524} size={31} color={C.muted}>助手状态：准备查询订单 8124</Text><Text x={28} y={80} w={1524} size={37} weight={650}>这只能说明要查，还不能证明查过</Text></div>
  <div style={{opacity:progress}}>
   {[[420,'模型','提出调用请求',C.blue],[965,'应用程序','检查后真正执行',C.gold],[1510,'工具返回','提供本次结果',C.teal]].map(([x,name,value,color])=><div key={name} style={{position:'absolute',left:Number(x)-235,top:554,width:470,height:165,borderTop:`3px solid ${color}`,background:`${color}0B`}}><Text x={16} y={19} w={438} size={29} color={C.muted} center>{name}</Text><Text x={16} y={77} w={438} size={36} color={String(color)} center weight={650}>{value}</Text></div>)}
  </div>
  <div style={{opacity:evidence}}><Text x={170} y={779} w={1580} size={34} color={C.teal} center>看执行记录和工具返回：成功查询 1 次　｜　权限拒绝，未查询</Text><Text x={650} y={878} w={620} size={23} color={C.muted} center>IT小村 · 原创</Text></div>
 </>;
};
const ShotView=({s,captions}:{s:Shot;captions:boolean})=>{
 const f=useCurrentFrame(),sub=s.subtitles?.find(x=>f>=x.from&&f<=(x.to??x.from+(x.duration??1)-1));
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 82% 4%,#173B5544,transparent 62%)'}}/>
  <Text x={130} y={63} w={1320} size={25} color={C.muted}>Agent A02 · 教学示例 · 自定义只读查询</Text><Text x={1700} y={62} w={150} size={25}>IT小村</Text>
  <Scene s={s} f={f}/>
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:930,minHeight:100,padding:'8px 12px',boxSizing:'border-box',background:`${C.bg}F8`,fontSize:39,lineHeight:1.4,fontWeight:500,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center'}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView s={s} captions={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
