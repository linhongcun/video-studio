import {MysqlBackdrop,MysqlHeader} from '../../../../_shared/mysql-video/Frame';
import React from 'react';
import {AbsoluteFill,Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {C,FONT} from './theme';
import {Shot,VIDEO,shots} from '../data';
import {Text,Term,Check,Path,Balance,Anchor,Op,Operate,go,linear,mix,sent,mark} from './MotionParts';
import {OtherScenes} from './OtherScenes';
declare const __HAS_VOICE_AUDIO__:boolean;
const Scene:React.FC<{shot:Shot}>=({shot})=>{
 const f=useCurrentFrame(),d=shot.durationInFrames,id=Number(shot.id),s1=sent(shot,1,d*.5);
 if(id===3){const phase=go(f,0,Math.max(24,d*.16)),swap=go(f,d*.42,Math.max(24,d*.18)),a=go(f,d*.12,d*.18),b=go(f,d*.65,d*.18);return <>
 <Text>先看两次修改的目标</Text>
 <Balance x={mix(790,365,swap)} y={535} owner="你的账户" old={1000} value={800} p={a} color={C.gold} scale={mix(1.2,.55,swap)} opacity={mix(phase,.5,swap)} state="修改目标"/>
 <Balance x={mix(1510,1130,swap)} y={535} owner="对方账户" old={500} value={700} p={b} color={C.gold} scale={mix(.55,1.2,swap)} opacity={mix(.3,1,swap)} state="修改目标"/>
 <Operate f={f} start={d*.09} len={d*.25} x={790} y={495} text="−200"/>
 {swap>.8&&<Operate f={f} start={d*.61} len={d*.23} x={1130} y={495} text="+200"/>}
 </>}
 if(id===7){const split=go(f,5,40),pending=go(f,44,20),change=go(f,70,42),hold=go(f,s1+85,32);return <>
 <Text opacity={1-go(f,s1+90,30)}>先执行扣款</Text>
 <Balance x={740} y={mix(535,315,split)} owner={split<.55?'你的账户':''} value={1000} scale={mix(1.2,.42,split)}/>
 <Text x={740} y={245} center size={23} color={C.muted} opacity={go(f,32,20)}>已确认</Text>
 <Balance x={740} y={535} owner="你的账户" old={1000} value={800} p={change} color={C.gold} scale={1.2} opacity={pending} state="本次修改 · 待确认"/>
 <Balance x={1450} y={535} owner="对方账户" value={500} scale={.48} opacity={.35}/>
 <Operate f={f} gutter start={44} len={55} x={740} y={495} text="−200"/>
 <Path d="M740 410V382" p={hold} color={C.gold} opacity={.7}/>
 {hold>.5&&<Text x={740} y={730} center size={34} color={C.gold} opacity={hold}>还没确认</Text>}
 </>}
 if(id===8){const focus=go(f,0,38),pending=go(f,35,20),change=go(f,65,45),pair=go(f,d-65,45),leftX=mix(mix(740,355,focus),620,pair),rightX=mix(mix(1450,1110,focus),1300,pair);return <>
 <Text opacity={1-go(f,d-60,25)}>再执行入账</Text>
 <Balance x={leftX} y={535} owner="你的账户" value={800} color={C.gold} scale={mix(mix(1.2,.5,focus),.9,pair)} opacity={mix(.5,1,pair)} state="待确认"/>
 <Balance x={rightX} y={mix(535,315,focus)} owner={focus<.5?'对方账户':''} value={500} scale={mix(.48,.42,focus)}/>
 <Text x={rightX} y={245} center size={23} color={C.muted} opacity={go(f,25,18)}>已确认</Text>
 <Balance x={rightX} y={535} owner="对方账户" old={500} value={700} p={change} color={C.gold} scale={mix(1.2,.9,pair)} opacity={pending} state="待确认"/>
 <Balance x={leftX} y={315} owner="" value={1000} scale={.42} opacity={pair}/>
 <Text x={leftX} y={245} center size={23} color={C.muted} opacity={pair}>已确认</Text>
 <Operate f={f} gutter start={40} len={55} x={1110} y={495} text="+200"/>
 {pair>.5&&<Path d="M620 720H1300" p={pair} color={C.gold} opacity={.55}/>}
 </>}
 if(id===9){const at=Math.max(50,s1-30),travel=go(f,at,60),done=f>=at+60,settle=go(f,at+60,45),digits=1-go(f,at+20,20);return <>
 <Term name="提交" f={f} at={mark(shot,'commitLabel')}/>
 <Path d="M620 410V340M1300 410V340" p={linear(f,25,55)} color={C.gold} opacity={.5*(1-settle)}/>
 {[{x:620,owner:'你的账户',old:1000,value:800},{x:1300,owner:'对方账户',old:500,value:700}].map(q=><React.Fragment key={q.x}>
 <Text x={q.x} y={245} center size={23} color={C.muted} opacity={1-settle}>已确认</Text>
 <Balance x={q.x} y={mix(315,535,settle)} owner={settle>.65?q.owner:''} value={done?q.value:q.old} scale={mix(.42,1.15,settle)} color={done?C.teal:C.text} state={settle>.7?'已确认':''}/>
 {!done&&<Balance x={q.x} y={mix(535,405,travel)} owner={q.owner} value={q.value} scale={mix(.9,.55,travel)} color={C.gold} state="待确认" opacity={digits}/>}
 {!done&&f>=at+20&&<div style={{position:'absolute',left:q.x-6,top:mix(405,322,travel)-6,width:12,height:12,borderRadius:'50%',background:C.gold,opacity:go(f,at+20,12)}}/>}
 </React.Fragment>)}
 <Path d="M620 780H1300" p={linear(f,at+100,30)} color={C.teal} opacity={done?1:0}/><Check x={960} y={780} p={go(f,at+110,24)}/>
 </>}
 if(id===11){const withdrawAt=Math.max(48,s1+10),withdraw=go(f,withdrawAt,65),settle=go(f,withdrawAt+65,55);return <>
 <Term name="回滚" f={f} at={mark(shot,'rollbackLabel')}/><Text x={960} y={270} center size={31} color={C.teal} opacity={go(f,18,22)*(1-go(f,withdrawAt+55,20))}>应用请求撤销</Text>
 <Path d="M960 315Q820 320 740 400" p={linear(f,25,40)} color={C.teal} opacity={1-withdraw}/>
 <Balance x={mix(740,620,settle)} y={mix(315,535,settle)} owner={settle>.65?'你的账户':''} value={1000} color={settle>.5?C.teal:C.text} scale={mix(.42,1.15,settle)} state={settle>.7?'原余额保留':''}/>
 <Text x={740} y={245} center size={23} color={C.muted} opacity={1-settle}>已确认</Text>
 <Balance x={mix(740,980,withdraw)} y={mix(535,380,withdraw)} owner="你的账户" value={800} color={C.gold} scale={mix(1.15,.5,withdraw)} opacity={1-withdraw} state="撤销本次修改"/>
 <Balance x={mix(1435,1300,settle)} y={535} owner="对方账户" value={500} scale={mix(.65,1.15,settle)} color={settle>.95?C.teal:C.text} opacity={.6+.4*settle}/>
 <Op text="−200" x={mix(740,390,withdraw)} y={mix(355,300,withdraw)} opacity={go(f,withdrawAt,10)*(1-withdraw)} color={C.gold}/>
 </>}
 return <OtherScenes shot={shot} f={f}/>;
};
export type MainProps={showSubtitles?:boolean;hideSubtitles?:boolean};
const ShotView:React.FC<{shot:Shot;showSubtitles:boolean}>=({shot,showSubtitles})=>{
 const f=useCurrentFrame(),sub=shot.subtitles?.find(s=>f>=s.from&&f<=(s.to??s.from+(s.duration??1)-1));
 return <AbsoluteFill data-mysql-canvas="true" style={{background:C.bg,color:C.text,fontFamily:FONT,overflow:'hidden'}}>
 <MysqlBackdrop/><MysqlHeader ep="EP.16" scope="MySQL 8.4 · InnoDB"/>
 <div style={{position:'absolute',right:100,top:103,fontSize:18,color:C.muted}}>同一数据库 · 示例数据 · 非真实转账</div>
 <Scene shot={shot}/>
 {showSubtitles&&sub&&<div data-subtitle style={{position:'absolute',left:130,right:130,top:925,height:110,display:'flex',alignItems:'center',justifyContent:'center',fontSize:42,fontWeight:500,lineHeight:1.3,textAlign:'center',background:`${C.bg}F7`,borderRadius:14}}>{sub.text}</div>}
 </AbsoluteFill>;
};
export const Main:React.FC<MainProps>=({showSubtitles=true,hideSubtitles=false})=><AbsoluteFill style={{background:C.bg,fontFamily:FONT}}>
 {typeof __HAS_VOICE_AUDIO__!=='undefined'&&__HAS_VOICE_AUDIO__&&<Audio src={staticFile('audio/voice.wav')}/>}
 {shots.map(shot=><Sequence key={shot.id} name={shot.id} from={shot.from} durationInFrames={shot.durationInFrames}><ShotView shot={shot} showSubtitles={showSubtitles&&!hideSubtitles}/></Sequence>)}
</AbsoluteFill>;
