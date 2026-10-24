import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Shot} from './data';
import {C} from './theme';
import config from '../../production.json';
import {T,Node,Link,Packet,Page,Result,go,mix,CaptionlessBrand} from './Primitives';
const Endpoints:React.FC<{left?:string;right?:string;rightColor?:string}>=({left='浏览器',right='网站',rightColor=C.teal})=><><Node x={370} label={left} value="发送这一端" color={C.blue}/><Node x={1550} label={right} value="接收这一端" color={rightColor}/></>;
export const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),id=Number(s.id),d=s.durationInFrames,b=s.cueFrames?.sentences?.[1]??d*.5,a=go(f,18,55),p=go(f,b+12,70),end=go(f,d-65,40);
 let title=config.shots[id-1][1];for(const[term,n,key]of config.terms)if(n===id&&f>=(s.cueFrames?.[key]??1))title=term as string;const h=<T size={57}>{title}</T>;
 if(id===1)return <>{h}<Page login progress={1} loading={false} url="https://shop.example/login"/><T x={960} y={835} center size={30} color={C.gold} alpha={p}>密码离开网页后，会经过什么？</T></>;
 if(id===2)return <>{h}<Endpoints rightColor={C.gold}/><Link x1={565} x2={1350} p={a} color={C.gold}/><Packet text="密码：示例口令" x1={565} x2={1350} p={a} color={C.gold} always/>
 <T x={960} y={700} center size={37} color={C.red} alpha={p}>观察到的内容：示例口令</T><Result y={800} alpha={p} color={C.muted}>没有传输加密保护的示意</Result></>;
 if(id===3){const tam=go(f,65,45);return <>{h}<Endpoints rightColor={C.red}/><Link x1={565} x2={1350} p={a} color={C.red}/><Packet text={tam===1?'目标：已被替换':'目标：原始内容'} x1={565} x2={1350} p={a} color={tam===1?C.red:C.gold} always/>
 <T x={960} y={700} center size={37} color={C.red} alpha={p}>缺少可靠验证，改动可能未被发现</T><Result color={C.muted} alpha={p}>本镜仍是无保护的示意</Result></>}
 if(id===4)return <>{h}<Endpoints/><Link x1={565} x2={1350} p={a} color={C.gold}/><Packet text="先核验网站身份" x1={565} x2={1050} p={p} color={C.gold} always/>
 <Result color={C.gold} alpha={p}>密码暂不发送 · 先确认对方是谁</Result></>;
 if(id===5){const steps=[go(f,15,35),go(f,65,35),go(f,b+12,35)];return <>{h}<Node x={450} label="本页域名" value="与证书身份对应" color={C.blue}/><div style={{position:'absolute',left:920,top:330,width:700,height:405,border:`2px solid ${C.edge}`,borderRadius:12,padding:'32px 42px'}}>
 <div style={{fontSize:38,color:C.gold,marginBottom:25}}>网站证书信息</div>{['域名匹配','仍在有效期内','可信的验证关系'].map((t,i)=><div key={t} style={{fontSize:31,color:steps[i]===1?C.teal:C.muted,marginTop:18,opacity:steps[i]}}>{steps[i]===1?'✓　':'　　'}{t}</div>)}</div><Link x1={635} x2={875} p={a}/><Result alpha={p}>核验通过，才能继续建立正常连接</Result></>}
 if(id===6)return <>{h}<Endpoints right="身份不匹配" rightColor={C.red}/><Link x1={565} x2={960} p={a} color={C.red}/><T x={960} y={430} center size={80} color={C.red} alpha={a}>×</T>
 <T x={960} y={660} center size={43} color={C.red} alpha={p}>浏览器发出证书警告</T><Result color={C.muted} alpha={p}>此时不能把连接当成正常可信连接</Result></>;
 if(id===7)return <>{h}<Endpoints/><Link x1={565} x2={1350} p={a} color={C.gold}/><Link x1={1350} x2={565} p={p} y={650} color={C.blue}/><Packet text="公开协商数据" x1={565} x2={1350} p={a} color={C.gold}/><Packet text="公开协商数据" x1={1350} x2={565} p={p} y={580} color={C.blue}/>
 <T x={370} y={720} center size={29} color={C.teal} alpha={p}>本端导出密钥</T><T x={1550} y={720} center size={29} color={C.teal} alpha={p}>本端导出密钥</T><Result alpha={p}>不把密钥作为普通明文传送</Result></>;
 if(id===8){const encrypted=go(f,15,35),travel=go(f,65,85),decrypt=go(f,Math.max(150,b+10),35);return <>{h}<Endpoints/><Link x1={565} x2={1350} p={travel}/><Packet text={encrypted===1?'◇ · ▧ · ○':'示例口令'} x1={565} x2={1350} p={travel} always color={C.teal}/>
 <T x={370} y={700} center size={30} color={C.blue}>先加密</T><T x={1550} y={700} center size={30} color={C.teal} alpha={decrypt}>解密后：示例口令</T><Result color={C.muted} alpha={decrypt}>中间观察到密文，接收端处理原内容</Result></>}
 if(id===9){const travel=go(f,25,85);return <>{h}<Node x={370} label="浏览器" value={p===1?'还原页面内容':'等待返回'} color={C.blue}/><Node x={1550} label="网站" value="先加密响应" color={C.teal}/><Link x1={1350} x2={565} p={travel}/><Packet text="○ · ◇ · ▧" x1={1350} x2={565} p={travel} color={C.teal}/>
 <Result alpha={p}>响应方向反过来，传输保护仍然存在</Result></>}
 if(id===10){const modify=go(f,55,30),travel=go(f,15,80);return <>{h}<Endpoints right={p===1?'验证拒绝':'网站'} rightColor={p===1?C.red:C.teal}/><Link x1={565} x2={1180} p={travel} color={modify===1?C.red:C.teal}/><Packet text={modify===1?'◇ · × · ○':'◇ · ▧ · ○'} x1={565} x2={1180} p={travel} color={modify===1?C.red:C.teal} always/>
 <T x={1550} y={715} center size={34} color={C.red} alpha={p}>验证失败 ×</T><Result color={C.red} alpha={p}>数据被拒绝 · 不作为正常内容接受</Result></>}
 if(id===11)return <>{h}<div style={{position:'absolute',left:570,top:345,width:780,height:365,border:`3px dashed ${C.teal}`,borderRadius:20,opacity:a}}/><Endpoints/><Link x1={565} x2={1350} p={a}/><Packet text="受保护的传输" x1={565} x2={1350} p={a}/>
 <T x={960} y={730} center size={28} color={C.teal} alpha={a}>保护范围：两个端点之间</T><Result color={C.gold} alpha={p}>网站信誉、服务端存储，仍需另外判断</Result></>;
 return <>{h}{[{x:390,t:'核验身份',v:'确认是这个域名'},{x:960,t:'加密传输',v:'中间难以读明文'},{x:1530,t:'验证完整性',v:'发现传输中的篡改'}].map((q,i)=><Node key={q.t} x={q.x} label={q.t} value={q.v} color={[C.blue,C.gold,C.teal][i]} alpha={go(f,10+i*55,40)}/>)}<Link x1={575} x2={775} p={go(f,65,45)}/><Link x1={1145} x2={1345} p={go(f,120,45)}/><Result color={C.muted} alpha={p}>加密网址，不是网站信誉保证</Result><CaptionlessBrand alpha={end}/></>;
};
