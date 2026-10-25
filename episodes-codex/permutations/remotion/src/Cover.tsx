import React from 'react';
import {C,FONT} from './theme';
export const coverSizes={'16x9':{width:1920,height:1080},'4x3':{width:1440,height:1080},'3x4':{width:1080,height:1440}};
const colors:Record<number,string>={1:C.blue,2:C.gold,3:C.teal};
const Label=({x,y,size=42,fill=C.text,children,weight=600}:any)=><text x={x} y={y} fontFamily={FONT} fontSize={size} fill={fill} fontWeight={weight}>{children}</text>;
const Row=({values,x,y,scale=1}:any)=><g transform={`translate(${x},${y}) scale(${scale})`}>{values.map((n:number,i:number)=><g key={i} transform={`translate(${i*210},0)`}><rect width={160} height={140} rx={19} fill={C.surface} stroke={colors[n]} strokeWidth={4}/><text x={80} y={101} textAnchor="middle" fontFamily={FONT} fontSize={86} fill={colors[n]} fontWeight={750}>{n}</text></g>)}</g>;
const Portrait=()=> <>
 <Label x={120} y={115} size={32} fill={C.muted}>码上分镜 · LC.46</Label>
 <Label x={120} y={240} size={40} fill={C.gold}>怎样排出所有不同顺序？</Label>
 <Label x={120} y={390} size={112} weight={800}>全排列</Label>
 <Label x={120} y={478} size={42}>选一个，退回来，再试</Label>
 <Label x={120} y={590} size={29} fill={C.muted}>先把排满的一份保存</Label>
 <Row values={[1,2,3]} x={120} y={635} scale={1.2}/>
 <path d="M 815 705 Q 915 825 815 925" fill="none" stroke={C.gold} strokeWidth={7}/><path d="M795 899 L815 925 L842 910" fill="none" stroke={C.gold} strokeWidth={7}/>
 <Label x={120} y={865} size={33} fill={C.gold}>撤销后，改走另一条选择</Label>
 <Row values={[1,3,2]} x={120} y={915} scale={1.2}/>
 <Label x={120} y={1190} size={37} fill={C.teal}>保存副本 · 撤销选择 · 找齐六种</Label>
</>;
export const Cover=({size='16x9'}:{size?:keyof typeof coverSizes})=>{
 const {width,height}=coverSizes[size];return <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}><rect width={width} height={height} fill={C.bg}/>
 {size==='16x9'?<>
  <Label x={180} y={135} size={32} fill={C.muted}>码上分镜 · LC.46</Label>
  <Label x={180} y={290} size={43} fill={C.gold}>怎样排出所有不同顺序？</Label>
  <Label x={180} y={468} size={132} weight={800}>全排列</Label>
  <Label x={180} y={570} size={47}>选一个，退回来，再试</Label>
  <Label x={180} y={754} size={38} fill={C.teal}>先存副本，再撤销选择</Label>
  <Label x={1090} y={300} size={29} fill={C.muted}>同一组数字，继续找下一种</Label>
  <Row values={[1,2,3]} x={1090} y={350} scale={1.05}/><Row values={[1,3,2]} x={1090} y={640} scale={1.05}/>
  <path d="M 1390 520 V 600 M 1370 580 L1390 600 L1410 580" stroke={C.gold} strokeWidth={5} fill="none"/>
  <Label x={1090} y={886} size={29} fill={C.muted}>每张恰好一次 · 全部六种顺序</Label>
 </>:<g transform={size==='4x3'?'translate(315,0) scale(.75)':undefined}><Portrait/></g>}
 </svg>;
};
