import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Shot} from './data';
import {C,MONO} from './theme';
import config from '../../production.json';
import {T,Node,Page,Result,Spinner,go,mix,CaptionlessBrand} from './Primitives';

const stages=['找地址','TCP 建连','TLS 安全','HTTP 交换','页面渲染'];
const stageFor=(slug:string)=>({url:0,dns:0,tcp:1,syn:1,synack:1,ack:1,'why-third':1,tls:2,request:3,response:3,resources:3,parse:4,paint:4}[slug]??-1);
const Pill:React.FC<{x:number;y:number;w?:number;label:string;color?:string;alpha?:number;small?:boolean}>=({x,y,w=260,label,color=C.blue,alpha=1,small=false})=><div style={{position:'absolute',left:x,top:y,width:w,height:small?45:60,border:`1px solid ${color}66`,background:`${color}0B`,borderRadius:8,opacity:alpha}}><T x={w/2} y={small?7:10} center size={small?23:28} color={color} w={w-20}>{label}</T></div>;
export const StageNav:React.FC<{slug:string}>=({slug})=>{
 const current=stageFor(slug);if(slug==='hook'||slug==='overview')return null;
 return <>
 <svg fill="none" width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d="M335 122V115H695V122" stroke={C.edge} strokeWidth={2}/></svg><T x={515} y={89} center size={18} color={C.muted}>建连接</T>
 {stages.map((label,i)=><React.Fragment key={label}><T x={130+i*205} y={137} size={23} color={i===current?C.gold:i<current?C.teal:C.muted}>{label}</T>{i<4&&<T x={301+i*205} y={136} size={24} color={C.edge}>→</T>}</React.Fragment>)}
 {current>=0&&<div style={{position:'absolute',left:130+current*205,top:178,width:145,height:2,background:C.gold}}/>}
 </>;
};

const Arrow:React.FC<{y:number;reverse?:boolean;p:number;color?:string;label?:string;sub?:string;alpha?:number}>=({y,reverse=false,p,color=C.blue,label,sub,alpha=1})=>{
 const x1=reverse?1490:430,x2=reverse?430:1490,tip=mix(x1,x2,p),dir=reverse?-1:1;
 return <div style={{opacity:alpha}}>
 <svg fill="none" width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}>
 <path d={`M${x1} ${y}H${x2}`} stroke={C.edge} strokeWidth={2}/>
 {p>0&&<><path d={`M${x1} ${y}H${tip}`} stroke={color} strokeWidth={4}/><path d={`M${tip-dir*12} ${y-8}L${tip} ${y}L${tip-dir*12} ${y+8}`} stroke={color} strokeWidth={4} fill="none"/></>}
 {p>0&&p<1&&<circle cx={tip} cy={y} r={8} fill={color}/>}
 </svg>
 {label&&<T x={960} y={y-56} center size={31} color={color} mono alpha={p>0?1:0}>{label}</T>}
 {sub&&<T x={960} y={y+16} center size={23} color={C.muted} alpha={p===1?1:0}>{sub}</T>}
 </div>;
};

const Endpoint:React.FC<{x:number;label:string;status:string;color:string}>=({x,label,status,color})=><>
 <div style={{position:'absolute',left:x-225,top:318,width:450,height:102,borderTop:`3px solid ${color}`,background:C.surface,borderRadius:5}}/>
 <T x={x} y={330} center size={36} color={color}>{label}</T>
 <T x={x} y={383} center size={22} color={C.muted}>{status}</T>
 </>;

const TcpTimeline:React.FC<{phase:number;f:number;b:number;duration:number;replay?:boolean;numberCue?:number}>=({phase,f,b,duration,replay=false,numberCue})=>{
 // One packet per shot. The preceding packet remains at its received state.
 const moveFrom=Math.min(24,Math.max(8,b*.12));
 const travel=Math.max(38,b-moveFrom+6);
 const progress=go(f,moveFrom,travel);
 const p1=phase>1?1:progress,p2=phase>2?1:phase===2?progress:0;
 const thirdFrom=replay?Math.max(18,b):moveFrom;
 const p3=phase===3?go(f,thirdFrom,replay?58:travel):0;
 const client=phase<2?'等待服务端回应':phase===2?(p2===1?'ESTABLISHED · 已建立':'等待服务端回应'):'ESTABLISHED · 已建立';
 const server=phase===1?(p1===1?'收到 SYN · 记下客户端序号':'等待连接'):phase===2?(p2>0?'等待最终确认':'已收到客户端起始序号'):(p3===1?'ESTABLISHED · 已建立':'等待最终确认');
 return <>
 <Endpoint x={430} label="浏览器" status={client} color={C.blue}/><Endpoint x={1490} label="服务端" status={server} color={p3===1?C.teal:C.gold}/>
 <svg fill="none" width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d="M430 426V790M1490 426V790" stroke={C.edge} strokeDasharray="7 9" strokeWidth={2}/></svg>
 <Arrow y={485} p={p1} label="SYN · seq = 1000" color={C.blue} sub={phase===1?'客户端起始序号':undefined}/>
 {phase>=2&&<Arrow y={615} reverse p={p2} label="SYN + ACK · seq = 5000 · ack = 1001" color={C.gold} sub={phase===2?'给出服务端起始序号，同时确认客户端 SYN':undefined}/>}
 {phase===2&&<T x={960} y={513} center size={24} color={C.gold} alpha={f>=(numberCue??b)?1:0}>确认号：1000 + 1 = 1001 · SYN 占一个序号</T>}
 {phase>=3&&<T x={960} y={642} center size={24} color={C.teal} alpha={f>=(replay?b:24)?1:0}>5000 + 1 = 5001</T>}
 {phase>=3&&<Arrow y={745} p={p3} label="ACK · seq = 1001 · ack = 5001" color={C.teal} sub={p3===1?'服务端收到确认，连接建立':undefined}/>}
 {replay&&<Pill x={1370} y={218} w={360} small label="局部回看 · 第三次确认" color={C.gold}/>}
 </>;
};

const CodePanel:React.FC<{response?:boolean;f:number;b:number}>=({response=false,f,b})=>{
 const showDetails=go(f,b,35),sent=go(f,b+32,58);
 return <>
 <div style={{position:'absolute',left:130,top:338,width:1150,height:390,background:'#0B1424',border:`1px solid ${C.edge}`,borderRadius:12,borderTop:`3px solid ${response?C.teal:C.blue}`}}/>
 <T x={166} y={358} size={22} color={C.muted}>HTTP/1.1 {response?'响应节选':'请求示意'} · TLS 解密后的明文视图</T>
 {!response?<>
 <T x={166} y={425} size={37} mono><span style={{color:C.blue}}>GET</span>{' /products/42 HTTP/1.1'}</T>
 <T x={166} y={502} size={37} mono alpha={showDetails}><span style={{color:C.gold}}>Host:</span>{' shop.example'}</T>
 <T x={166} y={611} size={25} color={C.muted} alpha={showDetails}>方法 + 路径 + 版本</T>
 <T x={166} y={654} size={25} color={C.muted} alpha={showDetails}>目标域名放在 Host 字段</T>
 </>:<>
 <T x={166} y={425} size={37} mono>{'HTTP/1.1 '}<span style={{color:C.teal}}>200 OK</span></T>
 <T x={166} y={502} size={37} mono alpha={showDetails}><span style={{color:C.gold}}>Content-Type:</span>{' text/html'}</T>
 <T x={166} y={585} size={34} color={C.muted} mono alpha={showDetails}>{'<html> ... </html>'}</T>
 <T x={166} y={654} size={25} color={C.muted} alpha={showDetails}>结果状态 + 内容类型 + 页面正文</T>
 </>}
 <Node x={1510} y={468} w={360} label="服务端" value={sent===1?(response?'HTML 已返回':'收到页面请求'):(response?'返回 HTML 中':'等待请求')} color={response?C.teal:C.gold}/>
 <svg fill="none" width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d={response?'M1320 705H1650':'M1320 705H1650'} stroke={C.edge} strokeWidth={2}/><path d={response?`M1650 705H${1650-330*sent}`:`M1320 705H${1320+330*sent}`} stroke={response?C.teal:C.blue} strokeWidth={4}/>{sent>0&&sent<1&&<circle cx={response?1650-330*sent:1320+330*sent} cy={705} r={9} fill={response?C.teal:C.blue}/>}</svg>
 <T x={1490} y={754} center size={24} color={C.muted}>{response?'服务端 → 浏览器':'浏览器 → 服务端'}</T>
 <Result y={828} alpha={sent} color={response?C.teal:C.blue}>{response?'HTML 返回了，页面还需要浏览器处理':'请求终于开始表达：我要哪个资源'}</Result>
 </>;
};

const BigFlow:React.FC<{f:number;b:number;recap?:boolean}>=({f,b,recap=false})=>{
 const labels=[['找地址','DNS 找到连接目标'],['建连接','TCP → TLS'],['取资源','HTTP 请求与响应'],['画页面','结构 → 布局 → 像素']];
 return <>
 {labels.map(([tag,desc],i)=>{
 const alpha=recap?1:go(f,18+i*28,28),x=130+i*435;
 return <React.Fragment key={tag}><div style={{position:'absolute',left:x,top:432,width:355,height:200,borderTop:`3px solid ${[C.blue,C.gold,C.blue,C.teal][i]}`,borderBottom:`1px solid ${C.edge}`,background:C.surface,opacity:alpha,borderRadius:5}}><T x={177} y={34} center size={42} color={[C.blue,C.gold,C.blue,C.teal][i]}>{tag}</T><T x={177} y={118} center size={26} color={C.muted}>{desc}</T></div>{i<3&&<T x={x+395} y={506} center size={30} color={C.edge} alpha={alpha}>→</T>}</React.Fragment>;
 })}
 <Result y={714} color={C.muted} alpha={go(f,b,40)}>{recap?'三次握手完成 TCP 建连，后面的过程还要继续':'本次：没有可用缓存、没有现成连接 · HTTPS / HTTP/1.1'}</Result>
 </>;
};

export const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),id=Number(s.id),d=s.durationInFrames,b=s.cueFrames?.sentences?.[1]??d*.5;
 const slug=config.shots[id-1]?.[0]??'recap';
 const a=go(f,18,52),p=go(f,b+8,60),heading=config.shots[id-1]?.[1]??'';
 const firstCue=config.terms.filter(([,number])=>number===id).map(([, ,key])=>s.cueFrames?.[key as string]??1)[0]??0;
 const h=<T x={130} y={211} size={53} w={1640} alpha={f>=firstCue?1:0}>{heading}</T>;
 if(slug==='hook')return <>{h}<Page y={332} w={1390} x={265} h={465}/><T x={960} y={835} center size={31} color={C.gold} alpha={go(f,b,35)}>一次商品页加载，为什么要先握手三次？</T></>;
 if(slug==='overview')return <>{h}<BigFlow f={f} b={b}/></>;
 if(slug==='url')return <>{h}
 <div style={{position:'absolute',left:130,top:350,width:1660,height:135,background:C.surface,border:`1px solid ${C.edge}`,borderRadius:10}}/>
 <T x={175} y={390} size={45} mono><span style={{color:C.teal}}>https://</span><span style={{color:C.blue}}>shop.example</span><span style={{color:C.gold}}>/products/42</span></T>
 {[{x:130,w:450,label:'协议',value:'HTTPS',note:'默认端口 443',color:C.teal},{x:625,w:535,label:'域名',value:'shop.example',note:'DNS 要查的名字',color:C.blue},{x:1205,w:585,label:'路径',value:'/products/42',note:'HTTP 要请求的资源',color:C.gold}].map((v,i)=><div key={v.label} style={{position:'absolute',left:v.x,top:545,width:v.w,height:220,background:C.surface,borderTop:`3px solid ${v.color}`,borderRadius:5,opacity:i===2?p:a}}><T x={30} y={23} size={25} color={C.muted}>{v.label}</T><T x={30} y={73} size={38} color={v.color} mono>{v.value}</T><T x={30} y={150} size={26} color={C.muted}>{v.note}</T></div>)}
 <Result y={817} alpha={p} color={C.muted}>域名用来找地址，路径用来指定页面</Result>
 </>;
 if(slug==='dns')return <>{h}<Node x={420} y={460} w={480} label="要查的域名" value="shop.example" color={C.blue}/><Node x={1500} y={460} w={480} label="DNS 解析结果" value={p===1?'203.0.113.10':'等待地址'} color={p===1?C.teal:C.muted}/>
 <svg fill="none" width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d="M675 492H1245" stroke={C.edge} strokeWidth={2}/><path d={`M675 492H${675+a*570}`} stroke={C.blue} strokeWidth={4}/>{a>0&&a<1&&<circle cx={675+a*570} cy={492} r={8} fill={C.blue}/>}</svg>
 <Pill x={675} y={650} w={570} label="本次连接目标 · 203.0.113.10 : 443" color={C.teal} alpha={p}/><Result y={822} alpha={p}>只查域名，不把商品路径交给 DNS</Result>
 </>;
 if(slug==='tcp')return <>{h}
 <T x={960} y={349} center size={39} color={C.blue}>可靠、有序的字节流</T>
 {[0,1,2,3,4].map(i=><div key={i} style={{position:'absolute',left:535+i*176,top:431,width:145,height:90,background:C.surface,border:`1px solid ${C.blue}88`,borderRadius:8,opacity:go(f,12+i*8,25)}}><T x={72} y={23} center mono size={30} color={C.blue}>{i+1}</T></div>)}
 <T x={960} y={554} center size={25} color={C.muted}>每个字节有序号，接收端按顺序交付</T>
 <Pill x={255} y={661} w={590} label="浏览器起始序号 · 1000" alpha={p} color={C.blue}/><Pill x={1075} y={661} w={590} label="服务端起始序号 · 5000" alpha={p} color={C.gold}/>
 <Result y={818} color={C.muted} alpha={p}>建立连接时，先交换并确认双方的起始序号</Result>
 </>;
 if(slug==='syn')return <>{h}<TcpTimeline phase={1} f={f} b={b} duration={d}/><Result y={835} color={C.blue} alpha={p}>第一次：客户端声明自己的起始序号</Result></>;
 if(slug==='synack')return <>{h}<TcpTimeline phase={2} f={f} b={b} duration={d} numberCue={s.cueFrames?.ackNumberLabel}/><Result y={835} color={C.gold} alpha={p}>ack = 1001：下一步期望从 1001 开始</Result></>;
 if(slug==='ack')return <>{h}<TcpTimeline phase={3} f={f} b={b} duration={d}/><Result y={850} alpha={p}>第三次：确认已收到服务端起始序号</Result></>;
 if(slug==='why-third')return <>{h}<TcpTimeline phase={3} f={f} b={b} duration={d} replay/>
 <T x={960} y={850} center size={30} color={f<b+58?C.gold:C.teal}>{f<b+58?'服务端还在等：我的起始序号，你收到了吗？':'最后这个 ACK，补上服务端需要的确认'}</T>
 </>;
 if(slug==='tls')return <>{h}<T x={960} y={287} center size={21} color={C.muted}>已建立的 TCP 之上 · TLS 握手过程简化</T>
 <Endpoint x={430} label="浏览器" status={p===1?'已验证身份 · 密钥就位':'准备验证网站身份'} color={C.blue}/><Endpoint x={1490} label="服务端" status={p===1?'密钥就位':'提供证书 · 参与密钥协商'} color={C.teal}/>
 <Arrow y={526} reverse p={go(f,18,Math.max(35,b*.4))} color={C.gold} label="验证证书 · 对应 shop.example"/>
 <Arrow y={687} p={go(f,b*.48,Math.max(35,b*.45))} color={C.teal} label="密钥协商 → 受保护的通信"/>
 <Result y={824} color={p===1?C.teal:C.muted}>TCP 保证可靠有序 · TLS 验证身份并保护内容</Result>
 </>;
 if(slug==='request')return <>{h}<CodePanel f={f} b={b}/></>;
 if(slug==='response')return <>{h}<CodePanel f={f} b={b} response/></>;
 if(slug==='resources'){
 const t0=Math.max(16,b*.1),step=Math.max(28,Math.min(48,(d-90)/5));
 const styleOut=go(f,t0,step),styleBack=go(f,t0+step+8,step);
 const imageStart=t0+2*step+28,imageOut=go(f,imageStart,Math.max(step,d-imageStart+48));
 const active=imageOut>0?'图片请求在途':(styleBack>0?'样式响应':'样式请求');
 const travel=imageOut>0?imageOut:(styleBack>0?styleBack:styleOut);
 const reverse=imageOut>0?false:styleBack>0;
 const x1=reverse?1245:675,x2=reverse?675:1245;
 return <>{h}<Node x={420} y={445} w={480} label="浏览器" value="HTML 中发现样式、图片引用" color={C.blue}/><Node x={1500} y={445} w={480} label="同一个网站" value="已有连接继续传输" color={C.teal}/>
 <T x={960} y={536} center size={28} color={C.muted}>复用同一条 TCP + TLS 连接</T>
 <svg fill="none" width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d="M675 634H1245" stroke={C.edge} strokeWidth={18} strokeLinecap="round"/><path d={`M${x1} 634H${mix(x1,x2,travel)}`} stroke={imageOut>0?C.gold:C.blue} strokeWidth={4}/>{travel>0&&travel<1&&<circle cx={mix(x1,x2,travel)} cy={634} r={10} fill={imageOut>0?C.gold:C.blue}/>}</svg>
 <T x={960} y={583} center size={30} color={imageOut>0?C.gold:C.blue}>{active}</T>
 <Pill x={230} y={701} w={390} label={styleBack===1?'样式已返回':'发现 styles.css'} color={styleBack===1?C.teal:C.blue}/>
 <Pill x={1300} y={701} w={390} label={imageOut>0?'图片获取中':'发现 product.jpg'} color={C.gold} alpha={styleBack===1?1:.25}/>
 <Result y={839} alpha={p}>HTTP/1.1 示例 · 按先后传输，不重新三次握手</Result>
 </>;
 }
 if(slug==='parse'){
 const cssFrom=s.cueFrames?.cssomLabel??b,cssVisible=f>=cssFrom?1:0;
 return <>{h}<Pill x={1415} y={222} w={365} small label="图片获取中 · 同一商品页" color={C.gold}/>
 <div style={{position:'absolute',left:130,top:335,width:750,height:430,background:C.surface,borderRadius:10,border:`1px solid ${C.edge}`}}/>
 <T x={170} y={362} size={27} color={C.blue}>HTML → DOM · 内容结构</T>
 <svg fill="none" width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><path d="M505 485V535H255V565M505 535V565M505 535H755V565" stroke={C.edge} strokeWidth={3}/></svg>
 <Pill x={405} y={440} w={200} label="商品页" color={C.blue} alpha={a}/>
 {[{x:170,t:'标题',color:C.blue},{x:420,t:'价格',color:cssVisible?C.gold:C.blue},{x:670,t:'按钮',color:cssVisible?C.teal:C.blue}].map(v=><Pill key={v.t} x={v.x} y={565} w={170} label={v.t} color={v.color} alpha={a}/>)}
 <T x={305} y={696} center size={26} color={C.muted} alpha={a}>页面里有哪些内容</T>
 <div style={{position:'absolute',left:1040,top:335,width:750,height:430,background:C.surface,borderRadius:10,border:`1px solid ${C.edge}`,opacity:cssVisible}}/>
 <T x={1080} y={362} size={27} color={C.gold} alpha={cssVisible}>CSS → CSSOM · 样式规则</T>
 <Pill x={1150} y={449} w={530} label="价格：金色 · 48 px" color={C.gold} alpha={cssVisible}/><Pill x={1150} y={557} w={530} label="按钮：青色 · 圆角" color={C.teal} alpha={cssVisible}/>
 <T x={1415} y={696} center size={26} color={C.muted} alpha={cssVisible}>同色对应：规则作用于目标元素</T>
 <svg fill="none" width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none',opacity:cssVisible}}><path d="M1140 479H1010V783H505V635" stroke={C.gold} strokeWidth={2} fill="none"/><path d="M1140 587H1050V799H755V635" stroke={C.teal} strokeWidth={2} fill="none"/><path d="M498 643L505 635L512 643" stroke={C.gold} strokeWidth={2} fill="none"/><path d="M748 643L755 635L762 643" stroke={C.teal} strokeWidth={2} fill="none"/></svg>
 <Result y={842} alpha={cssVisible}>结合内容与样式，计算每个元素怎样显示</Result>
 </>;
 }
 if(slug==='paint'){
 const image=go(f,b+30,70);
 return <>{h}<Page x={555} y={331} w={1210} h={461} progress={.42+.58*a} loading={false} image={image}/>
 <T x={130} y={416} size={33} color={C.blue}>布局</T><T x={130} y={468} size={24} color={C.muted}>位置和大小</T><T x={130} y={601} size={33} color={C.teal} alpha={p}>绘制与合成</T><T x={130} y={653} size={24} color={C.muted} alpha={p}>变成屏幕像素</T>
 {image<1&&<Spinner x={785} y={567} color={C.gold} size={36}/>}
 <Result y={837} alpha={p}>资源陆续到达，页面也可以逐步出现</Result>
 </>;
 }
 if(slug==='variants')return <>{h}
 <div style={{position:'absolute',left:130,top:352,width:790,height:395,background:C.surface,borderTop:`3px solid ${C.blue}`,borderRadius:6}}/>
 <T x={175} y={380} size={34} color={C.blue}>缓存与连接复用</T><T x={175} y={463} size={31}>有可用缓存 → 少一次网络获取</T><T x={175} y={543} size={31}>有现成连接 → 不重新握手</T><T x={175} y={617} size={25} color={C.muted}>HTTP/2：同一连接里的并发流</T><svg fill="none" width={1920} height={1080} style={{position:'absolute',inset:0,pointerEvents:'none'}}><rect x={470} y={669} width={390} height={60} rx={12} stroke={C.edge} fill="none" strokeWidth={2}/>{[684,714].map((y,i)=><g key={y}><path d={`M490 ${y}H840`} stroke={i?C.gold:C.blue} strokeWidth={2}/><circle cx={490+350*go(f,Math.max(40,b*.25),Math.max(55,b*.58))} cy={y} r={6} fill={i?C.gold:C.blue}/></g>)}</svg><T x={175} y={671} size={23} color={C.blue}>流 1</T><T x={175} y={704} size={23} color={C.gold}>流 3</T>
 <div style={{position:'absolute',left:1000,top:352,width:790,height:395,background:C.surface,borderTop:`3px solid ${C.gold}`,borderRadius:6,opacity:p}}/>
 <T x={1045} y={380} size={34} color={C.gold} alpha={p}>HTTP/3 走另一条连接路径</T><T x={1045} y={484} size={39} mono alpha={p}>HTTP/3 → QUIC → UDP</T><T x={1045} y={578} size={28} color={C.muted} alpha={p}>QUIC 集成 TLS 1.3 握手</T><T x={1045} y={646} size={28} color={C.muted} alpha={p}>不经过这套 TCP 三次握手</T>
 <Result y={826} alpha={p} color={C.muted}>“输入网址”是一类过程，并非每次都重走全部步骤</Result>
 </>;
 return <>{h}<BigFlow f={f} b={b} recap/><T x={960} y={800} center size={34} color={C.gold} alpha={p}>慢在找地址、建连接、等响应，还是画页面？</T><CaptionlessBrand alpha={go(f,d-60,35)}/></>;
};
