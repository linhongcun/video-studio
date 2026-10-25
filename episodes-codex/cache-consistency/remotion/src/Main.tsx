import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT} from './theme';
import {Shot,shots} from './data';
import {Txt,Result,Record,Link,DotFlow,Status,SeriesHeader,go,clamp} from './ui';
import {createBranchNavigator} from '../../../_shared/branch-map';
import {navigationContext} from './branch-map';
import {windowAt} from './motion';
declare const __HAS_VOICE_AUDIO__:boolean;
const BranchNavigator=createBranchNavigator(React);
const A=320,K=950,D=1560;
const motion=(s:Shot,f:number,name:string)=>{const [a,b]=windowAt(s,name);return go(f,a,b-a);};
const Scene:React.FC<{shot:Shot}>=({shot:s})=>{
 const f=useCurrentFrame(),id=Number(s.id),d=s.durationInFrames,t=s.cueFrames?.sentences?.[1]??d*.5;
 const title=(v:string,alpha=1)=><Txt size={54} w={1640} alpha={alpha}>{v}</Txt>;
 if(id===1){const check=motion(s,f,'check'),back=motion(s,f,'back');return <>
  {title('后台179，页面怎么还是199？')}
  <Record x={A} label="页面读到" value={199} detail={back===1?'刷新后，还是旧价格':'刷新请求'} color={C.red}/>
  <Record x={K} cache="redis" label="缓存" value={199} detail="这一份还旧着" color={C.gold}/>
  <Record x={D} database label="数据库" value={179} detail="后台已经改好" color={C.teal}/>
  <Link x1={520} x2={755} p={check}/><Link x1={755} x2={520} p={back} value="199" color={C.gold} y={590}/>
  <Result color={C.red} alpha={go(f,t,30)}>新的请求，为什么还拿到旧的结果？</Result>
 </>}
 if(id===2){const k=motion(s,f,'cache'),back=motion(s,f,'back');return <>
  {title('同一商品，两份读取位置')}
  <Record x={A} label="应用" value={back===1?199:undefined} detail="本次返回给页面" color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} detail="临时副本" color={C.teal} alpha={k}/>
  <Record x={D} database label="数据库 · 商品7042" value={199} detail="原记录 · 元" color={C.text}/>
  <Link x1={755} x2={520} p={back} value="199" color={C.teal}/>
  <Result alpha={back}>这次走缓存，没有再查数据库</Result>
 </>}
 if(id===3){const write=motion(s,f,'write'),done=write===1;return <>
  {title('先改原记录，副本不会同时改好')}
  <Record x={A} label="应用" detail={done?'写入已确认':'管理员发起修改'} color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} detail="旧副本未更新" color={C.gold} alpha={.5+.5*go(f,t,25)}/>
  <Record x={D} database label="数据库 · 商品7042" value={done?179:199} detail={done?'新价格已保存':'原价格'} color={done?C.teal:C.text} focus={1}/>
  <Link x1={520} x2={1350} p={write} value="179" color={C.teal} y={730}/>
  <Result color={C.gold} alpha={go(f,t,25)}>改的是这一份，不是同时改了所有副本</Result>
 </>}
 if(id===4){const check=motion(s,f,'check'),back=motion(s,f,'back');return <>
  {title('刷新请求，再次命中旧副本')}
  <Record x={A} label="应用" value={back===1?199:undefined} detail={back===1?'页面仍然得到199':'页面刷新'} color={back===1?C.red:C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} detail="命中的还是旧值" color={C.gold} focus={1}/>
  <Record x={D} database label="数据库 · 商品7042" value={179} detail="本次读路径没经过这里" color={C.teal} alpha={.25}/>
  <Link x1={520} x2={755} p={check}/><Link x1={755} x2={520} p={back} value="199" color={C.gold} y={590}/>
  <Result color={C.red} alpha={back}>刷新不等于绕过应用的缓存</Result>
 </>}
 if(id===5){const write=motion(s,f,'write'),remove=motion(s,f,'remove');return <>
  <Txt x={130} y={265} size={26} color={C.gold}>重新演示：从库199／缓存199开始，先保存新价</Txt>
  <Record x={A} label="应用" detail="重新演示正确顺序" color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} empty={remove===1} detail={remove===1?'旧副本已撤掉':'旧副本'} color={C.gold}/>
  <Record x={D} database label="数据库 · 商品7042" value={write===1?179:199} detail={write===1?'先写成功':'原记录'} color={C.teal}/>
  <Link x1={520} x2={1350} p={write} color={C.teal} value="179" y={730}/><Link x1={520} x2={755} p={remove} color={C.red} value="删除"/>
  <Result alpha={remove}>先改原记录，再让对应缓存失效</Result>
 </>}
 if(id===6){const confirm=motion(s,f,'confirm'),remove=motion(s,f,'remove');return <>
  {title('回看这两步：先写成功，再撤旧副本')}
  <Txt x={130} y={265} size={26} color={C.gold}>回看起点：库199／缓存199，再按同一顺序演示</Txt>
  <Record x={A} label="应用" detail={remove===1?'删除已完成':'处理本次修改'} color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} empty={remove===1} detail={remove===1?"未找到":"删除对应这一项"} color={C.gold}/>
  <Record x={D} database label="数据库 · 商品7042" value={confirm===1?179:199} detail={confirm===1?'✓ 原记录已确认':'原价格 · 回看起点'} color={C.teal} focus={confirm}/>
  <Link x1={520} x2={755} p={remove} color={C.red} value="删除"/>
  <Result alpha={remove}>删的是副本，179元的原记录还在</Result>
 </>}
 if(id===7){const miss=motion(s,f,'miss'),query=motion(s,f,'query'),back=motion(s,f,'back'),fill=motion(s,f,'fill');return <>
  {title('下一次读：没有，就重新取')}
  <Record x={A} label="应用" value={back===1?179:undefined} detail={back===1?'拿到新结果':'本次读取'} color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={179} empty={fill<1} detail={fill===1?'新副本已填好':'未找到'} color={C.teal} focus={fill}/>
  <Record x={D} database label="数据库 · 商品7042" value={179} detail="读取原记录" color={C.teal}/>
  <Link x1={520} x2={755} p={miss}/><Link x1={520} x2={1350} p={query} y={730}/><Link x1={1350} x2={520} p={back} value="179" color={C.teal} y={730}/><Link x1={520} x2={755} p={fill} value="179" color={C.teal}/>
  <Result alpha={fill}>取回179，再填回同一个商品的缓存</Result>
 </>}
 if(id===8){const read=motion(s,f,'read'),back=motion(s,f,'back');return <>
  {title('再往后的读取，使用新的副本')}
  <Record x={A} label="应用" value={back===1?179:undefined} detail="页面得到新价格" color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={179} detail="新副本" color={C.teal} focus={1}/>
  <Record x={D} database label="数据库 · 商品7042" value={179} detail="原记录一直都在" alpha={.4}/>
  <Link x1={520} x2={755} p={read}/><Link x1={755} x2={520} p={back} value="179" color={C.teal} y={590}/>
  <Result alpha={go(f,t,25)}>副本重建完成，这次读到了新价格</Result>
 </>}
 if(id===9){const remove=motion(s,f,'remove'),read=motion(s,f,'read'),back=motion(s,f,'back'),fill=motion(s,f,'fill');return <>
  {title('换个错误顺序：先删，还没改')}
  <Txt x={130} y={265} size={26} color={C.red}>对照起点：库199／缓存199；写者先删，尚未写库</Txt>
  <Record x={A} label="另一个读取" value={back===1?199:undefined} detail="插入两步之间" color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} empty={remove===1&&fill<1} detail={fill===1?'旧值又被填回':remove===1?'副本已撤下':f<windowAt(s,'remove')[0]?'旧副本尚未删':'正在删除旧副本'} color={fill===1?C.red:C.gold}/>
  <Record x={D} database label="数据库 · 商品7042" value={199} detail="这时还没有修改" color={C.gold}/>
  <Link x1={520} x2={1350} p={read} y={730}/><Link x1={1350} x2={520} p={back} value="199" color={C.gold} y={730}/><Link x1={520} x2={755} p={fill} value="199" color={C.gold}/>
  <Result alpha={fill} color={C.red}>空缓存被旧的199重新填满</Result>
 </>}
 if(id===10){const write=motion(s,f,'write'),read=motion(s,f,'read');return <>
  {title('随后改库，旧副本却已经回来了')}
  <Txt x={130} y={265} size={26} color={C.red}>{write===1?'写者确认179已保存；读者留下的旧副本199仍在':'写者随后继续：把179写入库；旧199已被读者填回'}</Txt>
  <Record x={A} label="应用" value={read===1?199:undefined} detail={read===1?'又读到旧价格':'写操作继续'} color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} detail="刚才回填的旧值" color={C.red} focus={1}/>
  <Record x={D} database label="数据库 · 商品7042" value={write===1?179:199} detail={write===1?'新价格已保存':'仍是旧价格'} color={write===1?C.teal:C.gold}/>
  <Link x1={520} x2={1350} p={write} value="179" color={C.teal} y={730}/><Link x1={755} x2={520} p={read} value="199" color={C.red}/>
  <Result color={C.red} alpha={read}>这就是先删后改可能出现的交错</Result>
 </>}
 if(id===11){const fail=motion(s,f,'fail');return <>
  {title('先写后删，也不是强一致保证')}
  <Txt x={130} y={265} size={26} color={C.gold}>另一种结果：本次写库已成功，旧副本199仍在</Txt>
  <Record x={A} label="应用" detail={fail===1?'需要重试与额外治理':'先写成功'} color={C.blue}/>
  <Record x={K} cache="redis" label="缓存 · 商品7042" value={199} detail={fail===1?'× 删除失败，旧副本仍在':'等待失效'} color={C.red}/>
  <Record x={D} database label="数据库 · 商品7042" value={179} detail="已经保存新价格" color={C.teal}/>
  <Link x1={520} x2={690} p={fail} color={C.red} value="删除"/>
  <Txt x={705} y={460} size={64} color={C.red} center alpha={fail}>×</Txt>
  <Result color={C.gold} alpha={fail}>还要考虑失败，以及读写之间的交错</Result>
 </>}
 const gone=motion(s,f,'gone'),back=motion(s,f,'back'),fill=motion(s,f,'fill'),brand=go(f,d-50,25);return <>
  {title('临时副本有期限，也要有更新策略',1-brand)}
  <Txt x={130} y={265} size={26} color={C.gold} alpha={1-brand}>图示另一次读取：到期只影响副本，未命中才回源</Txt>
  <div style={{opacity:1-brand}}>
   <Record x={A} label="应用" detail="再次读取" color={C.blue}/><Record x={K} cache="redis" label="缓存 · 商品7042" value={fill===1?179:199} empty={gone===1&&fill<1} detail={fill===1?'重新得到新副本':gone===1?'到期失效':'有效期正在走完'} color={fill===1?C.teal:C.gold}/><Record x={D} database label="数据库 · 商品7042" value={179} detail="原记录" color={C.teal} alpha={.6}/>
   <div style={{position:'absolute',left:780,top:705,width:340,height:7,background:C.edge}}><div style={{width:`${100*(1-gone)}%`,height:7,background:C.gold}}/></div>
   <Link x1={1350} x2={520} p={back} value="179" color={C.teal} y={730}/><Link x1={520} x2={755} p={fill} value="179" color={C.teal}/>
  </div>
  <Result color={C.gold} alpha={go(f,t,30)*(1-brand)}>过期限制使用期限，不能替代更新处理</Result>
  <Txt x={960} y={460} center size={70} alpha={brand}>IT小村 · 原创</Txt>
 </>;
};
const ShotView:React.FC<{shot:Shot;captions:boolean}>=({shot,captions})=>{
 const f=useCurrentFrame(),sub=shot.subtitles?.find(q=>f>=q.from&&f<=(q.to??q.from)),nav=navigationContext(shot,f);
 const foreground=shot.id==='05'?<Txt size={54} w={1640} alpha={f>=(shot.cueFrames?.term??1)?1:0}>缓存失效</Txt>:undefined;
 return <AbsoluteFill style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
  <div style={{position:'absolute',inset:0,background:'radial-gradient(ellipse at 80% 10%,#1A425E55,transparent 65%)'}}/>
  <SeriesHeader ep={9}/><Txt x={100} y={110} size={22} color={C.muted} w={310}>本例：Redis 共享缓存</Txt><BranchNavigator {...nav} foreground={foreground}><Scene shot={shot}/></BranchNavigator>
  {shot.id==='12'&&<Txt x={960} y={880} center size={24} color={C.muted} alpha={go(f,shot.durationInFrames-50,25)}>IT小村 · 原创</Txt>}
  {captions&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,fontSize:41,lineHeight:1.4,display:'flex',alignItems:'center',justifyContent:'center',textAlign:'center',background:`${C.bg}FA`,borderRadius:12}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export const Main:React.FC<{hideSubtitles?:boolean}>=({hideSubtitles=false})=><AbsoluteFill style={{background:C.bg}}>{typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/ >}{shots.map(s=><Sequence key={s.id} from={s.from} durationInFrames={s.durationInFrames}><ShotView shot={s} captions={!hideSubtitles}/></Sequence>)}</AbsoluteFill>;
