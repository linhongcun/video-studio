import {useEffect} from 'react';
export const useLayoutAudit=(enabled:boolean,kind:string,frame:number)=>{
 useEffect(()=>{
  if(!enabled)return;let disposed=false;
  document.fonts.ready.then(()=>{
   if(disposed)return;
   const root=document.querySelector(kind==='main'?'[data-audit-scene]':'[data-cover-root]');if(!root)return;
   const r=root.getBoundingClientRect(),w=kind==='main'?1920:Number(root.getAttribute('data-canvas-width')),h=kind==='main'?1080:Number(root.getAttribute('data-canvas-height'));
   const box=(el:Element)=>{const b=el.getBoundingClientRect();return{x:(b.x-r.x)*w/r.width,y:(b.y-r.y)*h/r.height,w:b.width*w/r.width,h:b.height*h/r.height};};
   const visible=(el:Element)=>{let opacity=1,n:Element|null=el;while(n&&n!==root.parentElement){opacity*=Number(getComputedStyle(n).opacity);n=n.parentElement;}return opacity>.04;};
   const labels=(e:Element)=>Array.from(e.querySelectorAll('text')).filter(visible).map(v=>v.textContent??'');
   const geometry=(e:Element)=>Array.from(e.querySelectorAll('path,line,circle')).filter(visible).map(v=>({tag:v.tagName,d:v.getAttribute('d'),x1:v.getAttribute('x1'),y1:v.getAttribute('y1'),x2:v.getAttribute('x2'),y2:v.getAttribute('y2'),cx:v.getAttribute('cx'),cy:v.getAttribute('cy'),r:v.getAttribute('r'),fill:getComputedStyle(v).fill,stroke:getComputedStyle(v).stroke,...box(v)}));
   const texts=Array.from(root.querySelectorAll('text,[data-layout-text]')).filter(e=>visible(e)&&(e.textContent??'').trim()).map(e=>({text:e.textContent??'',maxWidth:e.hasAttribute('data-max-width')?Number(e.getAttribute('data-max-width')):undefined,...box(e)}));
   const region=kind==='main'?{left:75,right:1845,top:42,bottom:955}:kind==='4x3'?{left:315,right:1125,top:0,bottom:918}:kind==='3x4'?{left:95,right:985,top:0,bottom:1224}:{left:140,right:1810,top:0,bottom:918};
   const overlap=(a:any,b:any)=>Math.min(a.x+a.w,b.x+b.w)>Math.max(a.x,b.x)+2&&Math.min(a.y+a.h,b.y+b.h)>Math.max(a.y,b.y)+2;
   const violations:any[]=[];
   for(const t of texts){if(t.maxWidth!==undefined&&t.w>t.maxWidth+.5)violations.push({type:'text-max-width',text:t});if(t.x<region.left-.5||t.x+t.w>region.right+.5||t.y<region.top-.5||t.y+t.h>region.bottom+.5)violations.push({type:'text-safe-region',text:t,region});}
   for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++)if(overlap(texts[i],texts[j]))violations.push({type:'text-text-overlap',a:texts[i],b:texts[j]});
   const bits=Array.from(root.querySelectorAll('[data-bit-index]')).filter(visible).map(e=>{const t=labels(e);return{index:Number(e.getAttribute('data-bit-index')),value:Number(e.getAttribute('data-bit-value')),bitValueText:t[0]??'',indexText:t[1]??'',...box(e)};});
   const members=Array.from(root.querySelectorAll('[data-members]')).filter(visible).map(e=>({keys:JSON.parse(e.getAttribute('data-members')!),actualTexts:labels(e),...box(e)}));
   const flows=Array.from(root.querySelectorAll('[data-algorithm-flow]')).filter(visible).map(e=>({kind:e.getAttribute('data-algorithm-flow'),element:e.getAttribute('data-flow-element'),position:Number(e.getAttribute('data-flow-position')),slot:Number(e.getAttribute('data-flow-slot')),elementGlyph:e.querySelector('[data-element-text]')?.textContent??'',positionGlyph:e.querySelector('[data-position-text]')?.textContent??'',actualTexts:labels(e),geometry:geometry(e),...box(e)}));
   const results=Array.from(root.querySelectorAll('[data-result-kind]')).filter(visible).map(e=>({kind:e.getAttribute('data-result-kind'),actualTexts:labels(e),...box(e)}));
   const state=Array.from(root.querySelectorAll('[data-visual-state]')).map(e=>JSON.parse(e.getAttribute('data-visual-state')!));
   const captions=Array.from(root.parentElement?.querySelectorAll('[data-subtitle]')??[]).filter(visible).map(e=>({text:e.textContent??'',...box(e)}));
   console.log('BLOOM_LAYOUT_AUDIT '+JSON.stringify({kind,frame,region,texts,bits,members,flows,results,captions,state,measurements:{textCount:texts.length,bitCount:bits.length,memberCount:members.length,flowCount:flows.length,resultCount:results.length,captionCount:captions.length},violations}));
  });return()=>{disposed=true;};
 },[enabled,kind,frame]);
};
