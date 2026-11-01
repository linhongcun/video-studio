import {useEffect} from 'react';

/** Actual Chromium text bounds. This is a layout check, not a teaching score. */
export const useLayoutAudit=(enabled:boolean,kind:string,frame:number)=>{
 useEffect(()=>{
  if(!enabled)return;let disposed=false;
  document.fonts.ready.then(()=>{
   if(disposed)return;
   const root=document.querySelector(kind==='main'?'[data-audit-scene]':'[data-cover-root]');if(!root)return;
   const r=root.getBoundingClientRect(),width=kind==='main'?1920:Number(root.getAttribute('data-canvas-width')),height=kind==='main'?1080:Number(root.getAttribute('data-canvas-height'));
   const box=(el:Element)=>{const b=el.getBoundingClientRect();return{x:(b.x-r.x)*width/r.width,y:(b.y-r.y)*height/r.height,w:b.width*width/r.width,h:b.height*height/r.height};};
   const visible=(el:Element)=>{let opacity=1,n:Element|null=el;while(n&&n!==root.parentElement){opacity*=Number(getComputedStyle(n).opacity);n=n.parentElement;}return opacity>.04;};
   const texts=Array.from(root.querySelectorAll('text,[data-layout-text]')).filter(e=>visible(e)&&(e.textContent??'').trim()).map(e=>({text:e.textContent??'',...box(e)}));
   const region=kind==='main'?{left:75,right:1845,top:42,bottom:955}:kind==='4x3'?{left:315,right:1125,top:0,bottom:918}:kind==='3x4'?{left:95,right:985,top:0,bottom:1224}:{left:140,right:1810,top:0,bottom:918};
   const overlap=(a:any,b:any)=>Math.min(a.x+a.w,b.x+b.w)>Math.max(a.x,b.x)+2&&Math.min(a.y+a.h,b.y+b.h)>Math.max(a.y,b.y)+2;
   const violations:any[]=[];
   for(const t of texts)if(t.x<region.left-.5||t.x+t.w>region.right+.5||t.y<region.top-.5||t.y+t.h>region.bottom+.5)violations.push({type:'text-safe-region',text:t,region});
   for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++)if(overlap(texts[i],texts[j]))violations.push({type:'text-text-overlap',a:texts[i],b:texts[j]});
   const state=Array.from(root.querySelectorAll('[data-visual-state]')).map(e=>JSON.parse(e.getAttribute('data-visual-state')!));
   console.log('HASH_LAYOUT_AUDIT '+JSON.stringify({kind,frame,region,texts,state,violations}));
  });return()=>{disposed=true;};
 },[enabled,kind,frame]);
};
