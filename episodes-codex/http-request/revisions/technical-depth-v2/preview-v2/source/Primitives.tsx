import React,{useEffect,useRef} from 'react';
import {useCurrentFrame} from 'remotion';
import {C,FONT,MONO} from './theme';
export const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const go=(f:number,a:number,n=35)=>{const p=clamp((f-a)/n);return p*p*(3-2*p)};
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
export const T:React.FC<{children:React.ReactNode;x?:number;y?:number;size?:number;color?:string;alpha?:number;center?:boolean;w?:number;mono?:boolean}>=({children,x=130,y=175,size=52,color=C.text,alpha=1,center=false,w,mono=false})=>{
 const ref=useRef<HTMLDivElement>(null);useEffect(()=>{const el=ref.current;if(el&&el.scrollWidth>el.clientWidth+2)console.error('COPYFIT overflow',el.textContent,el.scrollWidth,el.clientWidth)},[children]);
 return <div ref={ref} data-copy style={{position:'absolute',left:x,top:y,width:w,color,fontSize:size,opacity:alpha,fontFamily:mono?MONO:FONT,whiteSpace:'nowrap',fontWeight:600,lineHeight:1.35,textAlign:center?'center':'left',transform:center?'translateX(-50%)':undefined}}>{children}</div>;
};
export const Node:React.FC<{x:number;y?:number;label:string;value?:string;color?:string;alpha?:number;w?:number;active?:boolean}>=({x,y=455,label,value,color=C.blue,alpha=1,w=330,active=false})=><div style={{position:'absolute',left:x-w/2,top:y-85,width:w,height:205,opacity:alpha,borderTop:`3px solid ${color}`,borderBottom:`1px solid ${C.edge}`,background:active?`${color}12`:C.surface,textAlign:'center',paddingTop:30,borderRadius:4}}>
 <div style={{fontSize:40,fontWeight:650,color}}>{label}</div><div style={{marginTop:20,fontSize:25,color:C.muted}}>{value}</div>
 </div>;
export const Link:React.FC<{x1:number;x2:number;y?:number;p:number;color?:string;alpha?:number;dashed?:boolean}>=({x1,x2,y=500,p,color=C.teal,alpha=1,dashed=false})=><svg width="1920" height="1080" style={{position:'absolute',inset:0,opacity:alpha,pointerEvents:'none'}}>
 <path d={`M${x1} ${y}L${x2} ${y}`} stroke={C.edge} strokeWidth="2" strokeDasharray={dashed?'10 12':undefined}/><path d={`M${x1} ${y}L${x2} ${y}`} stroke={color} strokeWidth="4" pathLength="1" strokeDasharray="1" strokeDashoffset={1-clamp(p)}/>
 {p>0&&p<1&&<circle cx={mix(x1,x2,p)} cy={y} r={9} fill={color}/>}
 </svg>;
export const Packet:React.FC<{text:string;x1:number;x2:number;p:number;y?:number;color?:string;always?:boolean}>=({text,x1,x2,p,y=420,color=C.gold,always=false})=>(always||(p>0&&p<1))?<div style={{position:'absolute',left:mix(x1+Math.sign(x2-x1)*Math.min(180,Math.abs(x2-x1)/3),x2-Math.sign(x2-x1)*Math.min(180,Math.abs(x2-x1)/3),p),top:y-28*Math.sin(p*Math.PI),transform:'translateX(-50%)',padding:'17px 28px',fontSize:31,fontFamily:FONT,fontWeight:700,color,background:C.bg,border:`2px solid ${color}`,borderRadius:14,whiteSpace:'nowrap'}}>{text}</div>:null;
export const Result:React.FC<{children:React.ReactNode;color?:string;alpha?:number;y?:number}>=({children,color=C.teal,alpha=1,y=800})=><T x={960} y={y} center size={35} color={color} alpha={alpha}>{children}</T>;
export const Spinner:React.FC<{x:number;y:number;size?:number;color?:string}>=({x,y,size=50,color=C.blue})=>{const f=useCurrentFrame();return <div style={{position:'absolute',left:x-size/2,top:y-size/2,width:size,height:size,border:`4px solid ${C.edge}`,borderTopColor:color,borderRadius:'50%',transform:`rotate(${f*5}deg)`}}/>};
export const Page:React.FC<{x?:number;y?:number;w?:number;h?:number;progress?:number;loading?:boolean;login?:boolean;url?:string;scale?:number;alpha?:number;image?:number}>=({x=310,y=300,w=1300,h=490,progress=0,loading=true,login=false,url='https://shop.example/products/42',scale=1,alpha=1,image=0})=><div style={{position:'absolute',left:x,top:y,width:w,height:h,border:`2px solid ${C.edge}`,borderRadius:20,overflow:'hidden',background:C.bg,transform:`scale(${scale})`,transformOrigin:'center',opacity:alpha}}>
 <div style={{height:77,background:'#17243A',borderBottom:`1px solid ${C.edge}`,display:'flex',alignItems:'center',padding:'0 27px',gap:22}}><span style={{color:C.muted,fontSize:23}}>网页</span><div style={{height:44,background:'#0B1323',borderRadius:8,color:C.muted,fontSize:25,fontFamily:MONO,padding:'5px 23px',flex:1}}>{url}</div></div>
 {progress===0&&loading&&<Spinner x={w/2} y={h*.57}/>}
 {progress>0&&<div style={{position:'absolute',left:55,top:112,right:55,bottom:35}}>
  {login?<><div style={{fontSize:35,color:C.text,fontWeight:650}}>登录示例网站</div><div style={{marginTop:22,padding:'13px 20px',border:`2px solid ${C.edge}`,color:C.muted,fontSize:25,width:Math.min(580,w-180)}}>账号　青禾</div><div style={{marginTop:15,padding:'13px 20px',border:`2px solid ${C.edge}`,color:C.text,fontSize:25,width:Math.min(580,w-180)}}>密码　••••••••</div><div style={{marginTop:22,width:190,padding:'13px 0',textAlign:'center',fontSize:26,color:C.bg,background:C.teal,borderRadius:8}}>登录</div></>:<>
   <div style={{width:w*.28,height:h*.49,float:'left',border:`2px solid ${progress<.6?C.edge:C.blue}`,borderRadius:14,position:'relative',background:progress<.6?C.bg:'#213C54'}}>
    {image>0?<><div style={{position:'absolute',left:'18%',right:'18%',top:'25%',height:'40%',background:C.blue,opacity:image,borderRadius:30}}/><div style={{position:'absolute',left:'25%',right:'25%',top:'67%',height:10,background:C.edge,opacity:image}}/></>:<div style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',fontSize:25,color:C.muted}}>{progress>.6?'图片加载中':'图片区域'}</div>}
   </div>
   <div style={{marginLeft:w*.34,fontSize:37,fontWeight:650,color:progress>.3?C.text:C.muted}}>示例商品</div>
   <div style={{marginLeft:w*.34,marginTop:24,fontSize:48,fontFamily:MONO,color:progress>.5?C.gold:C.muted}}>199 元</div>
   <div style={{marginLeft:w*.34,marginTop:24,width:220,padding:'15px 0',textAlign:'center',fontSize:27,color:progress>.75?C.bg:C.muted,background:progress>.75?C.teal:C.surface,borderRadius:9,border:`1px solid ${C.edge}`}}>{progress>.75?'加入购物车':'按钮区域'}</div>
  </>}
 </div>}
 </div>;
export const CaptionlessBrand:React.FC<{alpha:number}>=({alpha})=><T x={960} y={860} size={26} center alpha={alpha}>IT小村 · 原创</T>;
