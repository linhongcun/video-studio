import React from 'react';
import {useCurrentFrame} from 'remotion';
import {Shot} from './data';
import {C} from './theme';
import config from '../../production.json';
import {T,Node,Link,Packet,Page,Result,Spinner,go,mix,clamp,CaptionlessBrand} from './Primitives';
export const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),id=Number(s.id),d=s.durationInFrames,b=s.cueFrames?.sentences?.[1]??d*.5;
 const a=go(f,18,55),p=go(f,b+10,65),end=go(f,d-65,40);
 let heading=config.shots[id-1][1];for(const [term,number,key]of config.terms){if(number===id&&f>=(s.cueFrames?.[key]??1))heading=term as string;}
 const h=<T size={57}>{heading}</T>;
 if(id===1)return <>{h}<Page loading/><T x={960} y={835} center size={30} color={C.muted} alpha={go(f,b,30)}>回车已经按下 · 页面仍在等待</T></>;
 if(id===2)return <>{h}<Page x={120} y={335} w={850} h={410} loading/>
 <T x={1090} y={420} size={39} color={C.gold} alpha={a}>没有可直接使用的页面</T><T x={1090} y={515} size={39} color={C.blue} alpha={p}>没有现成连接</T><T x={1090} y={630} size={27} color={C.muted} alpha={p}>只跟着这一个商品页</T></>;
 if(id===3)return <>{h}<Node x={430} label="本地缓存" value={a===1?'没有可直接用的资源':'检查已有资源'} color={C.gold}/><Node x={1490} label="网络" value="继续请求资源" alpha={p}/>
 <Link x1={610} x2={1305} p={p}/><Packet text="商品页" x1={610} x2={1305} p={p}/><Result alpha={a}>有可用资源就复用 · 这次继续向外请求</Result></>;
 if(id===4)return <>{h}<Node x={425} label="示例域名" value="网址里的名字" color={C.gold}/><Node x={1490} label="服务器地址" value={p===1?'203.0.113.10':'等待查询结果'} color={p===1?C.teal:C.muted}/>
 <Link x1={610} x2={1305} p={a}/><Packet text="查询" x1={610} x2={1305} p={a}/><Packet text="203.0.113.10" x1={1305} x2={610} p={p} y={630} color={C.teal}/><Result alpha={p}>先找到地址，再继续连接</Result></>;
 if(id===5)return <>{h}<Node x={430} label="浏览器" value="同一个商品页"/><Node x={1490} label="网站" value={p===1?'安全协商完成':'正在建立连接'} color={p===1?C.teal:C.gold}/>
 <Link x1={610} x2={1305} p={a} color={p===1?C.teal:C.gold}/><Packet text="连接与安全协商" x1={610} x2={1305} p={a} color={C.gold}/><Link x1={1305} x2={610} y={650} p={p}/><Result alpha={p}>连接可以开始承载网页内容</Result></>;
 if(id===6)return <>{h}<Node x={430} label="浏览器" value="我要这个商品页"/><Node x={1490} label="网站" value={p===1?'收到请求':'等待请求'} color={C.gold}/>
 <Link x1={610} x2={1305} p={p}/><Packet text="商品页请求" x1={610} x2={1305} p={p} always={p===0}/><Result alpha={p}>这次要取哪个资源，随请求一起送达</Result></>;
 if(id===7)return <>{h}<Node x={430} label="浏览器" value={p===1?'收到响应':'等待响应'}/><Node x={1490} label="网站" value={a===1?'处理完成':'处理中'} color={a===1?C.teal:C.gold}/>
 <Link x1={1305} x2={610} p={p}/><Packet text="状态与页面内容" x1={1305} x2={610} p={p} color={C.teal}/><Result alpha={p}>响应返回 · 开始处理收到的内容</Result></>;
 if(id===8){const q=go(f,70,55),r=go(f,b+35,55);return <>{h}<Node x={430} label="页面结构" value="发现其他资源" color={C.teal}/>
 <Node x={1450} y={355} label="样式" value={q===1?'已获取':'继续请求'} color={C.blue} alpha={a}/><Node x={1450} y={645} label="图片" value={r===1?'请求仍在进行':'准备请求'} color={C.gold} alpha={p}/>
 <Link x1={620} x2={1250} y={390} p={q}/><Packet text="样式" x1={1250} x2={620} p={q} y={330}/>
 <Link x1={620} x2={1250} y={680} p={r} color={C.gold}/><Packet text="图片请求" x1={620} x2={1250} p={r} y={620} color={C.gold}/></>}
 if(id===9)return <>{h}<Page x={490} w={1120} progress={.2+.3*p} loading={false}/>
 <T x={130} y={400} size={34} color={C.blue} alpha={a}>内容</T><T x={130} y={515} size={34} color={C.gold} alpha={p}>样式</T>
 <Link x1={255} x2={450} y={455} p={a}/><Link x1={255} x2={450} y={570} p={p} color={C.gold}/><Result alpha={p}>同一组内容 · 算出位置和大小</Result></>;
 if(id===10)return <>{h}<Page x={490} w={1120} progress={.55+.45*a} loading={false} image={0}/><Result alpha={p}>先绘制已有内容，再逐步补全</Result></>;
 if(id===11){const img=go(f,b+10,75);return <>{h}<Page x={490} w={1120} progress={1} loading={false} image={img}/>
 {img<1&&<Spinner x={702} y={545} size={42} color={C.gold}/>}
 <Result color={img===1?C.teal:C.gold}>页面已经出现{img===1?' · 图片也已补齐':' · 图片继续加载'}</Result></>}
 return <>{h}{[{x:390,t:'找到地址',v:'先知道去哪里'},{x:960,t:'收回资源',v:'内容经网络返回'},{x:1530,t:'画出页面',v:'变成屏幕上的画面'}].map((q,i)=><Node key={q.t} x={q.x} label={q.t} value={q.v} color={[C.blue,C.gold,C.teal][i]} alpha={go(f,10+i*50,40)}/>)}
 <Link x1={575} x2={775} p={go(f,60,45)}/><Link x1={1145} x2={1345} p={go(f,110,45)}/><Result alpha={go(f,b,40)} color={C.muted}>缓存和连接可复用时，可以少做一些工作</Result><CaptionlessBrand alpha={end}/></>;
};
