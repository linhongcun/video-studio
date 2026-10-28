import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT} from './theme';
import {Shot,shots} from '../data';
import {Txt,Result,Record,Link,DotFlow,Status,go,clamp,mix} from './ui';
import {RedisBackdrop,RedisHeader} from '../../../../_shared/redis-cache-video/Frame';
declare const __HAS_VOICE_AUDIO__:boolean;
const A=320,K=950,D=1560;
const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),id=Number(s.id),d=s.durationInFrames,t=s.cueFrames?.sentences?.[1]??d*.48;
 const title=(v:string,alpha=1)=><Txt size={54} w={1640} alpha={alpha}>{v}</Txt>;
 if(id===1){const pile=Math.min(5,Math.floor(f/27));return <>
  {title('同一商品，怎么越多人看越慢？')}
  <Record x={A} label="商品页请求" value={f>75?'等待':'199'} detail="都要看同一个价格" color={C.blue}/>
  <Record x={D} label="价格原记录 · 商品7042" value={199} detail="重复读取同一项" color={C.gold}/>
  <DotFlow f={f} x1={520} x2={1350} start={8} count={5}/>
  {Array.from({length:pile},(_,i)=><div key={i} style={{position:'absolute',left:1250-i*53,top:608,width:35,height:35,border:`2px solid ${C.gold}`,borderRadius:8,background:C.surface}}/>)}
  <Result alpha={go(f,t,30)} color={C.red}>价格没变，请求却一遍遍到数据库</Result>
 </>}
 if(id===2){const query=go(f,t-8,45),back=go(f,t+45,45),at=s.cueFrames?.term??1;return <>
  {f>=at&&title('数据库：保存网站数据')}
  <Record x={A} label="应用" value={back===1?199:undefined} detail={back===1?'交给页面':'正在查询'} color={C.blue} alpha={.35+.65*go(f,t-45,35)}/>
  <Record x={D} database={f>=at} label={f>=at?"数据库":"原记录"} value={f>=165?199:undefined} detail={f>=110?"商品7042 · 价格（元）":"保存商品等数据"} color={C.gold} alpha={go(f,at,30)}/>
  <Link x1={520} x2={1350} p={query}/><Link x1={1350} x2={520} p={back} color={C.gold} value="199" y={590}/>
  <Result alpha={back}>这一次读取：数据库处理 1 次</Result>
 </>}
 if(id===3){const n=Math.min(3,Math.floor(Math.max(0,f-15)/50)+1);return <>
  {title('重复查询，也占用处理能力')}
  <Record x={A} label="应用" value={n} detail="相同商品请求 · 示例" color={C.blue}/>
  <Record x={D} database label="数据库 · 商品7042" value={199} detail="同一份原数据" color={C.gold}/>
  <DotFlow f={f} x1={520} x2={1350} start={15} count={3}/>
  <Status x={950} y={425} color={C.gold}>同样的查询，再来一次</Status>
  <Result alpha={go(f,t,30)}>重复读取和其他工作，使用同一份处理能力</Result>
 </>}
 if(id===4){const back=go(f,10,40),copy=go(f,60,45),keep=copy===1,probe=go(f,t,45);return <>
  {title('把查到的结果，临时留一份')}
  <Record x={A} label="应用" value={back===1?199:undefined} detail={probe===1?"下一次先检查副本":"刚从原记录查回"} color={C.blue}/>
  <Record x={K} label="临时副本" value={keep?199:undefined} empty={!keep} detail="商品7042 · 元" color={C.teal} alpha={go(f,5,25)} focus={1}/>
  <Record x={D} database label="数据库" value={199} detail="原记录仍在" alpha={.5}/>
  <Link x1={1350} x2={520} p={back} color={C.gold} value="199" y={730}/><Link x1={520} x2={755} p={copy} color={C.teal} value="199"/>
  <Link x1={520} x2={755} p={probe}/>
  <Result alpha={probe}>下一次先找这一份</Result>
 </>}
 if(id===5){const at=s.cueFrames?.term??1,local=go(f,t-8,35);return <>
  {f>=at&&title('服务端缓存')}
  <Record x={A} label="应用" value="" detail="服务器这一侧" color={C.blue}/>
  <Record x={K} label="临时保留" value={199} detail={local===1?'本地内存 / 共享缓存':'同一商品价格'} color={C.teal} focus={1}/>
  <Record x={D} database label="数据库" value={199} detail="原记录" alpha={.3}/>
  <Link x1={520} x2={755} p={go(f,35,40)} color={C.teal}/>
  <Result alpha={local}>复用的是数据结果，不是把数据库搬走</Result>
 </>}
 if(id===6){const check=go(f,15,40),query=go(f,t-10,50),back=go(f,t+45,50),at=s.cueFrames?.term??1;return <>
  {title('新的示例：这一项缓存先清空')}
  <Record x={A} label="应用" detail={back===1?'取回199':'本次读取'} value={back===1?199:undefined} color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" empty detail="未找到" color={C.muted} focus={check}/>
  <Record x={D} database label="数据库" value={199} detail="仍要查询原记录" color={C.gold} alpha={.3+.7*query}/>
  <Link x1={520} x2={755} p={check}/><Link x1={520} x2={1350} p={query} color={C.gold} y={730}/><Link x1={1350} x2={520} p={back} color={C.gold} value="199" y={730}/>
  <Result alpha={back}>没找到，就继续取原数据</Result>
 </>}
 if(id===7){const put=go(f,20,48),deliver=go(f,80,48);return <>
  {title('取回后，先把这一项留好')}
  <Record x={A} label="应用" value={199} detail={deliver===1?'返回给页面':'刚取回的结果'} color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={put===1?199:undefined} empty={put<1} detail={put===1?'已填充临时副本':'尚未填充'} color={C.teal} focus={put}/>
  <Record x={D} database label="数据库" value={199} detail="原记录不变" alpha={.45}/>
  <Link x1={520} x2={755} p={put} color={C.teal} value="199"/>
  <Txt x={A} y={730} center size={30} color={C.blue} alpha={deliver}>页面得到199</Txt>
  <Result alpha={go(f,t,30)}>同一个商品，两份读取位置</Result>
 </>}
 if(id===8){const check=go(f,15,45),back=go(f,t,50),at=s.cueFrames?.term??1;return <>
  {f>=at&&title('缓存命中')}
  <Record x={A} label="应用" value={back===1?199:undefined} detail={back===1?'返回页面':'新的相同请求'} color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} detail="这份可以直接用" color={C.teal} focus={1}/>
  <Record x={D} database label="数据库" value={199} detail="这次不用查" alpha={.22}/>
  <Link x1={520} x2={755} p={check}/><Link x1={755} x2={520} p={back} color={C.teal} value="199" y={590}/>
  <Result alpha={back}>这次读取，停在缓存这一侧</Result>
 </>}
 if(id===9){const active=Math.min(3,Math.floor(Math.max(0,f-10)/65)+1);return <>
  {title('后面的相同请求，继续走短路径')}
  <Record x={A} label="应用" value={199} detail={`第${active}个相同请求 · 示例`} color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} detail="复用已填好的结果" color={C.teal} focus={1}/>
  <Record x={D} label="数据库读取次数" value="1 次" detail="自06起累计 · 示例" color={C.gold} alpha={.55}/>
  {[0,1,2].map(i=><Link key={i} x1={755} x2={520} p={clamp((f-25-i*65)/40)} color={C.teal} value="199" y={520}/>)}
  <Result alpha={go(f,t,30)}>减少重复读取，不是数据库突然变快</Result>
 </>}
 if(id===10){const gone=go(f,15,40),query=go(f,t-10,35),back=go(f,t+30,35),fill=go(f,t+70,35);return <>
  {title('临时副本不在了，还能重新取回')}
  <Record x={A} label="应用" value={back===1?199:undefined} detail="相同商品再读取" color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} empty={gone===1&&fill<1} detail={fill===1?'重新填好':'到期 / 被清理'} color={C.teal} focus={fill}/>
  <Record x={D} database label="数据库" value={199} detail="原记录始终在" color={C.gold}/>
  <Link x1={520} x2={1350} p={query} color={C.gold} y={730}/><Link x1={1350} x2={520} p={back} color={C.teal} value="199" y={730}/><Link x1={520} x2={755} p={fill} color={C.teal} value="199"/>
  <Result alpha={fill}>失效的是副本，原数据没有被删掉</Result>
 </>}
 if(id===11){const change=go(f,t,45);return <>
  {title('收益取决于：这一份能不能反复用')}
  <Record x={A} label={change===1?'不同内容':'同一商品'} value={change===1?'?':199} detail={change===1?'每次都未找到':'反复读取'} color={change===1?C.gold:C.blue}/>
  <Record x={K} cache="redis" label="缓存" value={199} detail={change===1?'检查，也有成本':'这份能复用'} color={C.teal}/>
  <Record x={D} database label="数据库" value={change===1?'查询':199} detail="仍然是数据来源" alpha={.35+.55*change}/>
  <DotFlow f={f} x1={520} x2={755} start={10} count={3} color={C.teal}/><Link x1={1145} x2={1350} p={change} color={C.gold}/>
  <Result color={C.gold} alpha={change}>命中很少时，多一步未必划算</Result>
 </>}
 const update=go(f,t,40),brand=go(f,d-45,25);return <>
  {title('缓存省下重复读取，也留下副本问题',1-brand)}
  <div style={{opacity:1-brand}}><Record x={K} cache="redis" label="缓存 · 商品7042" value={199} detail="这一份还没改" color={C.gold}/><Record x={D} database label="数据库" value={update===1?179:199} detail="原记录改了价格" color={C.teal}/><Status x={470} y={460} color={C.blue}>同一件商品</Status></div>
  <Result color={C.gold} alpha={update*(1-brand)}>数据库改好了，缓存里的旧价格呢？</Result>
  <Txt x={960} y={460} center size={70} alpha={brand}>IT小村 · 原创</Txt>
 </>;
};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot,captions})=>{const f=useCurrentFrame(),sub=shot.subtitles?.find(q=>f>=q.from&&f<=(q.to??q.from));return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}><svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position:'absolute',inset:0}}><RedisBackdrop/><RedisHeader ep={8} title={Number(shot.id)>5||(Number(shot.id)===5&&f>=(shot.cueFrames?.term??1))?'服务端缓存':'应用场景'} chapter="商品查询"/></svg>{Number(shot.id)>=6&&<Txt x={100} y={120} size={22} color={C.muted} w={310}>本例：Redis 共享缓存</Txt>}<Scene shot={shot}/>{captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,fontSize:41,lineHeight:1.4,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center',background:`${C.bg}FA`,borderRadius:12}}>{sub.text}</div>}</AbsoluteFill>};
export const Main:React.FC<{hideSubtitles?:boolean}>=({hideSubtitles=false})=><AbsoluteFill style={{background:C.bg}}>{typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/ >}{shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={!hideSubtitles}/></Sequence>)}</AbsoluteFill>;
