import React from 'react';
import {C,MONO} from './theme';
import {Shot} from './data';
import {Text,Term,Check,Cross,Path,Balance,Anchor,Op,Operate,Scope,go,linear,mix,sent,mark} from './MotionParts';

export const OtherScenes:React.FC<{shot:Shot;f:number}>=({shot,f})=>{
 const d=shot.durationInFrames,id=Number(shot.id),s1=sent(shot,1,d*.5);
 if(id===1){const travel=go(f,18,48),hit=go(f,58,14);return <>
 <Text x={960} y={164} center size={70} weight={750}>扣了钱，对方没到账？</Text>
 <Balance x={610} y={535} owner="你的账户" value={800} color={C.teal} state="扣款已生效"/>
 <Balance x={1310} y={535} owner="对方账户" value={500} color={hit>.5?C.red:C.text} state={f>60?'入账未完成':''}/>
 <Path d="M820 520H1150" p={travel} color={f>58?C.red:C.gold} opacity={.65}/>
 <Op text="+200" x={mix(880,1110,travel)} y={490} color={f>58?C.red:C.gold} opacity={1-go(f,95,25)}/>
 <Cross x={1155} y={520} p={hit}/><Check x={610} y={728} p={go(f,5,24)} color={C.teal}/>
 {f>104&&<Text x={960} y={780} center size={38} color={C.red} opacity={go(f,104,22)}>只完成了一半</Text>}
 </>}
 if(id===2){const move=go(f,35,55),other=go(f,65,35),scope=linear(f,115,55);return <>
 <Text opacity={1-go(f,58,25)}>回到示例起点</Text>
 <Balance x={mix(960,620,move)} y={535} owner="你的账户" value={1000} scale={mix(1.15,1,move)}/>
 <Balance x={mix(1530,1300,other)} y={535} owner="对方账户" value={500} opacity={other}/>
 <Scope p={scope} y={360} h={365}/>
 {f>165&&<Text x={960} y={780} center size={36} color={C.gold} opacity={go(f,165,25)}>转账 200 元</Text>}
 </>}
 if(id===4){const change=go(f,32,Math.max(35,s1*.42)),focus=go(f,s1,42);return <>
 <Text>两步各自确认</Text>
 <Balance x={mix(760,360,focus)} y={535} owner="你的账户" old={1000} value={800} p={change} color={change>.98?C.teal:C.text} scale={mix(1.2,.58,focus)} opacity={mix(1,.58,focus)} state={change>.98?'扣款已确认':''}/>
 <Balance x={mix(1490,1140,focus)} y={535} owner="对方账户" value={500} scale={mix(.5,1.2,focus)} opacity={mix(.3,1,focus)} state={focus>.95?'尚未入账':''}/>
 <Operate f={f} start={15} len={Math.max(40,s1*.55)} x={760} y={495} text="−200"/>
 <Check x={mix(760,360,focus)} y={720} p={go(f,s1*.65,24)} color={C.teal}/>
 </>}
 if(id===5){const run=go(f,8,45),failed=go(f,45,12),out=go(f,s1+30,42);return <>
 <Text color={C.red} opacity={go(f,40,15)}>第二步没做成</Text>
 <Balance x={mix(360,620,out)} y={535} owner="你的账户" value={800} color={C.teal} scale={mix(.58,1.05,out)} opacity={mix(.58,1,out)} state="已扣款"/>
 <Balance x={mix(1140,1300,out)} y={535} owner="对方账户" value={500} color={f>45?C.red:C.text} scale={mix(1.2,1.05,out)} state={out>.9?'仍未增加':''}/>
 <Path d="M620 350H1040" p={run} color={f>45?C.red:C.gold} opacity={1-go(f,s1+14,35)}/>
 <Op text="+200" x={mix(650,980,run)} y={315} color={f>45?C.red:C.gold} opacity={1-go(f,s1+12,28)}/>
 <Cross x={1040} y={350} p={failed*(1-go(f,s1+30,25))}/>
 {out>.75&&<Cross x={1300} y={730} p={go(f,s1+65,20)}/>}
 </>}
 if(id===6){const gather=go(f,28,65),draw=linear(f,55,65);return <>
 <Term name="事务" f={f} at={mark(shot,'transactionLabel')}/>
 <Balance x={620} y={400} owner="你的账户" value={1000} scale={.65}/>
 <Balance x={1300} y={400} owner="对方账户" value={500} scale={.65}/>
 <Op text="−200" x={mix(340,650,gather)} y={590} color={C.gold}/><Op text="+200" x={mix(1580,1270,gather)} y={590} color={C.gold}/>
 <Path d="M430 520V680Q430 710 460 710H1460Q1490 710 1490 680V520" p={draw} color={C.teal} width={3}/>
 {f>s1&&<Text x={960} y={760} center size={36} color={C.teal} opacity={go(f,s1,25)}>同一笔，一起决定</Text>}
 </>}
 if(id===10){const enter=go(f,5,28),change=go(f,s1*.55,40),failAt=s1+30,run=go(f,s1,45);return <>
 <Text size={40} opacity={1-go(f,s1,24)}>另一个失败示例</Text>
 <Anchor x={740} y={315} value={1000} opacity={change}/>
 <Balance x={740} y={535} owner="你的账户" old={1000} value={800} p={change} color={change>.1?C.gold:C.text} scale={1.15} opacity={enter} state={change>.1?'待确认':''}/>
 <Balance x={1435} y={535} owner="对方账户" value={500} scale={.65} opacity={.6}/>
 <Operate f={f} gutter start={s1*.4} len={50} x={740} y={495} text="−200"/>
 <Path d="M1030 520H1250" p={run} color={f>=failAt?C.red:C.gold}/>
 <Op text="+200" x={mix(1050,1210,run)} y={475} color={f>=failAt?C.red:C.gold} opacity={go(f,s1,12)}/>
 <Cross x={1250} y={520} p={go(f,failAt,14)}/>
 {f>failAt+35&&<Text x={960} y={785} center size={35} color={C.red} opacity={go(f,failAt+35,20)}>应用发现失败</Text>}
 </>}
 if(id===12){const change=go(f,20,40),tryCommit=linear(f,65,75),stopped=f>=s1;return <>
 <Text size={40} opacity={1-go(f,60,20)}>另一笔，尚未提交</Text>
 <Anchor x={740} y={315} value={1000}/>
 <Balance x={740} y={535} owner="你的账户" old={1000} value={800} p={change} scale={1.15} color={C.gold} opacity={stopped?.45:1} state="未提交"/>
 <Balance x={1450} y={535} owner="对方账户" value={500} scale={.48} opacity={.4}/>
 <Path d="M740 425V350" p={Math.min(.45,tryCommit)} color={stopped?C.red:C.gold} opacity={.8}/>
 <Operate f={f} gutter start={8} len={50} x={740} y={495} text="−200"/>
 <Cross x={740} y={390} p={go(f,s1,15)}/>
 {stopped&&<Text x={740} y={760} center size={42} color={C.red} opacity={go(f,s1+14,25)}>提交前中断</Text>}
 </>}
 if(id===13){const scan=linear(f,24,Math.max(70,s1-20)),erase=go(f,Math.max(35,s1*.45),Math.max(45,s1*.55)),settle=go(f,s1+8,60);return <>
 <Text opacity={1-go(f,s1+25,20)}>重启，处理未提交修改</Text>
 <Balance x={mix(740,620,settle)} y={mix(315,535,settle)} owner={settle>.65?'你的账户':''} value={1000} color={settle>.5?C.teal:C.text} scale={mix(.42,1.15,settle)} state={settle>.7?'原余额保留':''}/>
 <Text x={740} y={245} center size={23} color={C.muted} opacity={1-settle}>已确认</Text>
 <Balance x={mix(740,860,erase)} y={mix(535,470,erase)} owner="你的账户" value={800} color={C.gold} scale={mix(1.15,.7,erase)} opacity={.55*(1-erase)} state="未提交"/>
 <Path d="M500 430H970V670H500" p={1-erase} color={C.gold} opacity={.4}/>
 {scan<1&&<div style={{position:'absolute',left:mix(470,1020,scan),top:395,width:2,height:285,background:C.teal,opacity:.7,boxShadow:`0 0 18px ${C.teal}`}}/>}
 <Balance x={mix(1450,1300,settle)} y={535} owner="对方账户" value={500} scale={mix(.48,1.15,settle)} color={settle>.95?C.teal:C.text} opacity={.4+.6*settle}/>
 {settle>.95&&<Check x={960} y={775} p={go(f,s1+70,25)}/>}
 </>}
 if(id===14){const second=go(f,Math.max(60,s1-45),55);return <>
 <Text x={mix(960,500,second)} y={305} center size={38} color={C.teal}>提交</Text>
 <Balance x={mix(620,340,second)} y={535} owner="你的账户" value={800} color={C.teal} scale={mix(1.12,.62,second)}/>
 <Balance x={mix(1300,660,second)} y={535} owner="对方账户" value={700} color={C.teal} scale={mix(1.12,.62,second)}/>
 <div style={{position:'absolute',inset:0,opacity:second}}><Text x={1410} y={305} center size={38}>回滚</Text><Balance x={1245} y={535} owner="你的账户" value={1000} scale={.62}/><Balance x={1565} y={535} owner="对方账户" value={500} scale={.62}/></div>
 <Path d="M960 355V690" p={second} color={C.edge} width={2}/>
 {f>s1+35&&<Text x={960} y={775} center size={37} color={C.teal} opacity={go(f,s1+35,30)}>整笔做成，或整笔撤销</Text>}
 </>}
 if(id===15){const shrink=go(f,0,45),outside=go(f,s1,35);return <>
 <Balance x={mix(620,760,shrink)} y={535} owner="你的账户" value={800} scale={mix(1,.75,shrink)} color={C.teal}/>
 <Balance x={mix(1300,1160,shrink)} y={535} owner="对方账户" value={700} scale={mix(1,.75,shrink)} color={C.teal}/>
 <Scope p={linear(f,25,60)} x={500} y={335} w={920} h={380}/>
 {[{x:250,y:470},{x:1670,y:395},{x:1650,y:680}].map((q,i)=><React.Fragment key={i}><div style={{position:'absolute',left:q.x-9,top:q.y-9,width:18,height:18,borderRadius:'50%',background:C.muted,opacity:outside*.5}}/><Path d={`M${q.x<960?500:1420} ${q.y}H${q.x}`} p={outside} color={C.muted} dash opacity={.4}/></React.Fragment>)}
 {outside>.1&&<Text x={960} y={790} center size={35} color={C.muted} opacity={outside}>真实转账还可能涉及其他系统</Text>}
 </>}
 const stock=go(f,27,30),requests=linear(f,65,70),question=go(f,100,30),brand=go(f,s1,25);return <>
 <div style={{opacity:1-go(f,0,32),transform:`translateY(${-go(f,0,32)*70}px)`}}><Balance x={620} y={535} owner="你的账户" value={800} color={C.teal}/><Balance x={1300} y={535} owner="对方账户" value={700} color={C.teal}/></div>
 <div style={{position:'absolute',left:760,top:330,width:400,textAlign:'center',opacity:stock,transform:`translateY(${(1-stock)*60}px)`}}><div style={{fontSize:30,color:C.muted}}>最后一件库存（示例）</div><div style={{fontSize:210,fontFamily:MONO,color:C.gold,fontWeight:650,lineHeight:1.2}}>1</div></div>
 <Path d="M340 520H745M1580 520H1175" p={requests} color={C.gold} opacity={.7}/>
 <Text x={340} y={575} center size={30} color={C.muted} opacity={go(f,65,25)}>一个人</Text><Text x={1580} y={575} center size={30} color={C.muted} opacity={go(f,65,25)}>另一个人</Text>
 <Text x={960} y={185} center size={57} opacity={question}>两个人同时抢，听谁的？</Text>
 <Text x={960} y={790} center size={34} color={C.muted} opacity={brand}>IT小村 · 原创</Text>
 </>;
};
