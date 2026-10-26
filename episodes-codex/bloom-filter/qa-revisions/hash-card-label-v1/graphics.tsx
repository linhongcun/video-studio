import React from 'react';
import model from '../../model.json';
import {C,FONT,MONO} from './theme';

export const M:any = model;
export const keyItem=(key:string) => {
  const result=M.items.find((item:any)=>item.key===key);
  if (!result) throw new Error('Unknown model key: '+key);
  return result;
};
export const displayKey=(key:string)=>keyItem(key).display;
export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const ease=(n:number)=>{const t=clamp(n);return t*t*(3-2*t);};
export const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
export const progress=(f:number,a:number,b:number)=>ease((f-a)/Math.max(1,b-a));
export const T=({x,y,size=34,color=C.text,anchor='start',children,mono=false,weight=500,maxWidth,...props}:any)=><text x={x} y={y} fill={color} fontSize={size} fontFamily={mono?MONO:FONT} textAnchor={anchor} fontWeight={weight} data-max-width={maxWidth} {...props}>{children}</text>;
export const Head=({chapter,title,sub}:any)=><>
  <T x={115} y={73} size={24} color={C.teal} weight={700}>布隆过滤器</T>
  <T x={315} y={73} size={24} color={C.muted}>{chapter}</T>
  <T x={1805} y={73} size={25} color={C.muted} anchor="end">IT小村 · 工程算法 02</T>
  <T x={115} y={153} size={49} weight={750} maxWidth={1690}>{title}</T>
  <T x={118} y={211} size={29} color={C.muted}>{sub}</T>
</>;
export const Note=({children,color=C.muted}:any)=><T x={960} y={916} size={25} anchor="middle" color={color}>{children}</T>;
export const Pill=({x,y,label,color=C.teal,w=400,size=32,opacity=1}:any)=><g opacity={opacity}>
  <rect x={x-w/2} y={y-38} width={w} height={76} rx={18} fill={C.surface} stroke={color} strokeWidth={2}/>
  <T x={x} y={y+11} size={size} anchor="middle" color={color} weight={650}>{label}</T>
</g>;
export const Arrow=({x1,y1,x2,y2,color=C.muted,opacity=1,dashed=false}:any)=>{
 const a=Math.atan2(y2-y1,x2-x1),back=14;
 return <g opacity={opacity}><line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={3} strokeDasharray={dashed?'10 8':undefined}/><path d={`M${x2-back*Math.cos(a-.45)} ${y2-back*Math.sin(a-.45)}L${x2} ${y2}L${x2-back*Math.cos(a+.45)} ${y2-back*Math.sin(a+.45)}`} fill="none" stroke={color} strokeWidth={3}/></g>;
};
export const BX=(i:number)=>255+i*94;
export const BIT_TOP=526;
export const SLOTS=[780,1110,1440];
export const BitArray=({ones=[],focus=[],zeroFocus=[],shared=[],opacity=1,showCount=16,label='16位 · 教学示例'}:any)=><g opacity={opacity} data-bits={JSON.stringify(ones)}>
  <T x={118} y={478} size={26} color={C.muted}>{label}</T>
  <T x={118} y={590} size={25} color={C.muted}>标记</T>
  <T x={118} y={681} size={25} color={C.muted}>位置</T>
  {Array.from({length:M.bitCount},(_,i)=>{
    const one=ones.includes(i),active=focus.includes(i),zero=zeroFocus.includes(i),isShared=shared.includes(i);
    const color=zero?C.red:active?C.gold:isShared?C.blue:one?C.teal:C.edge;
    return <g key={i} opacity={i<showCount?1:0} data-bit-index={i} data-bit-value={one?1:0}>
      <rect x={BX(i)-41} y={BIT_TOP} width={82} height={104} rx={14} fill={one?'#173C41':C.surface} stroke={color} strokeWidth={active||zero||isShared?4:2}/>
      <T x={BX(i)} y={595} size={52} anchor="middle" mono color={one?C.teal:zero?C.red:C.muted} weight={750}>{one?'1':'0'}</T>
      <T x={BX(i)} y={681} size={29} anchor="middle" mono color={active||zero?color:C.muted}>{i}</T>
    </g>;
  })}
</g>;
export const HashSlots=({item,visible=3,checked=[],failedAt,active=-1,mode='固定计算',opacity=1}:any)=><g opacity={opacity}>
  <path d="M470 347H560V257H1440" stroke={C.edge} strokeWidth={3} fill="none"/>
  <rect x={205} y={286} width={265} height={124} rx={20} fill={C.surface} stroke={C.text} strokeWidth={2}/>
  <T x={337} y={323} size={26} anchor="middle" color={C.muted}>商品编号</T>
  <T x={337} y={381} size={53} anchor="middle" mono weight={750}>{item.display}</T>
  {item.positions.map((p:number,i:number)=>{
    const checkedHere=checked.includes(p),failed=failedAt===p,color=failed?C.red:active===i?C.gold:checkedHere?C.teal:C.muted;
    return <g key={i} opacity={i<visible?1:0}>
      <Arrow x1={SLOTS[i]} y1={257} x2={SLOTS[i]} y2={286} color={C.edge}/>
      <rect x={SLOTS[i]-118} y={286} width={236} height={124} rx={18} fill={C.surface} stroke={color} strokeWidth={active===i||failed?3:2}/>
      <T x={SLOTS[i]} y={323} size={25} color={C.muted} anchor="middle" maxWidth={214}>第{i+1}路 · {failedAt!==undefined&&!checkedHere?'未探测':mode}</T>
      <T x={SLOTS[i]} y={381} size={49} color={color} anchor="middle" mono weight={700}>{p}</T>
    </g>;
  })}
</g>;
export const Trace=({slot,position,p,color=C.gold,opacity=1}:any)=>{
 const x=SLOTS[slot],endX=BX(position),y=410,endY=BIT_TOP;
 const cpY=470;
 const point=(t:number)=>({x:(1-t)*(1-t)*x+2*(1-t)*t*x+t*t*endX,y:(1-t)*(1-t)*y+2*(1-t)*t*cpY+t*t*endY});
 const tip=point(p);
 return <g opacity={opacity}>
  <path d={`M${x} ${y}Q${x} ${cpY} ${endX} ${endY}`} fill="none" stroke={color} strokeWidth={3} opacity={.35}/>
  {p>0&&p<1&&<circle cx={tip.x} cy={tip.y} r={9} fill={C.text} stroke={color} strokeWidth={2}/>}
 </g>;
};
export const Directory=({x=1535,y=787,records=M.catalogInitially,result='',active=false,unsafe=false,opacity=1}:any)=><g opacity={opacity} data-catalog={JSON.stringify(records)}>
  <rect x={x-242} y={y-79} width={484} height={158} rx={20} fill={C.surface} stroke={unsafe?C.red:active?C.blue:C.edge} strokeWidth={2}/>
  <g transform={`translate(${x-204},${y-42})`} stroke={active?C.blue:C.muted} strokeWidth={2.5} fill={C.surface}>
    <path d="M-17 0V38C-17 49 17 49 17 38V0"/>
    <ellipse cx={0} cy={0} rx={17} ry={8}/><path d="M-17 17C-17 28 17 28 17 17" fill="none"/>
  </g>
  <T x={x+17} y={y-30} size={29} anchor="middle" color={active?C.blue:C.text}>目录数据库</T>
  <T x={x+8} y={y+13} size={26} anchor="middle" mono color={C.muted} maxWidth={410}>收录 {records.map(displayKey).join(' · ')}</T>
  {result&&<T x={x+8} y={y+56} size={28} anchor="middle" color={unsafe?C.red:active?C.gold:C.muted}>{result}</T>}
</g>;
