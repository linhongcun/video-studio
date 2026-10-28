import React from 'react';
import style from './style-v1.json';
import identities from './identities-v1.json';
import {C,FONT} from './theme';
export const LeetcodeBackdrop=()=> <div data-leetcode-canvas="true" aria-hidden="true" style={{position:'absolute',inset:0,width:1920,height:1080,background:C.bg,pointerEvents:'none'}}/>;
type Identity={number:number;method:string};
type HeaderProps={slug:string;detail?:React.ReactNode;compact?:boolean;identity?:Identity};
export const LeetcodeHeader=({slug,detail,compact=false,identity}:HeaderProps)=>{
 const ep=identity??identities.episodes.find(value=>value.slug===slug);
 if(!ep) throw new Error(`Missing frozen LeetCode identity: ${slug}`);
 const top=compact?20:49, height=compact?42:52, pillTop=compact?19:48;
 return <div data-leetcode-header={slug} data-header-compact={compact} style={{position:'absolute',left:0,top:0,width:1920,height:compact?84:150,pointerEvents:'none',fontFamily:FONT}}>
  <div style={{position:'absolute',left:110,top,color:C.text,fontFamily:style.fonts.brand,fontSize:compact?29:36,lineHeight:1.35,fontWeight:750,letterSpacing:-1}}>LeetCode</div>
  <div style={{position:'absolute',left:325,top:pillTop,width:142,height,background:C.gold,borderRadius:12,color:C.bg,fontFamily:style.fonts.brand,fontSize:compact?25:30,lineHeight:`${height}px`,textAlign:'center',fontWeight:750}}>LC.{ep.number}</div>
  <div style={{position:'absolute',left:494,top:top+(compact?5:9),color:C.teal,fontSize:compact?22:26,lineHeight:1.3,fontWeight:600}}>{ep.method}</div>
  <div style={{position:'absolute',right:110,top:top+(compact?5:8),color:C.muted,fontSize:compact?22:26,lineHeight:1.3,fontWeight:600}}>{style.brand}</div>
  {!compact&&detail&&<div data-leetcode-detail="true" style={{position:'absolute',right:110,top:103,maxWidth:1660,color:C.muted,fontSize:20,lineHeight:1.35,textAlign:'right',whiteSpace:'nowrap'}}>{detail}</div>}
  <div style={{position:'absolute',left:110,right:110,top:compact?78:143,height:1,background:C.edge}}/>
 </div>;
};
