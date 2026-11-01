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
   const labels=(el:Element)=>Array.from(el.querySelectorAll('text')).filter(visible).map(v=>v.textContent??'');
   const geometry=(el:Element)=>Array.from(el.querySelectorAll('path,line,circle,rect')).filter(visible).map(v=>({tag:v.tagName,d:v.getAttribute('d'),x1:v.getAttribute('x1'),y1:v.getAttribute('y1'),x2:v.getAttribute('x2'),y2:v.getAttribute('y2'),cx:v.getAttribute('cx'),cy:v.getAttribute('cy'),r:v.getAttribute('r'),fill:getComputedStyle(v).fill,stroke:getComputedStyle(v).stroke,strokeDasharray:getComputedStyle(v).strokeDasharray,opacity:getComputedStyle(v).opacity,...box(v)}));
   const texts=Array.from(root.querySelectorAll('text,[data-layout-text]')).filter(e=>visible(e)&&(e.textContent??'').trim()).map(e=>({text:e.textContent??'',maxWidth:e.hasAttribute('data-max-width')?Number(e.getAttribute('data-max-width')):undefined,...box(e)}));
   const region=kind==='main'?{left:75,right:1845,top:42,bottom:955}:kind==='4x3'?{left:315,right:1125,top:0,bottom:918}:kind==='3x4'?{left:95,right:985,top:0,bottom:1224}:{left:140,right:1810,top:0,bottom:918};
   const overlap=(a:any,b:any)=>Math.min(a.x+a.w,b.x+b.w)>Math.max(a.x,b.x)+2&&Math.min(a.y+a.h,b.y+b.h)>Math.max(a.y,b.y)+2;
   const violations:any[]=[];
   for(const t of texts){if(t.maxWidth!==undefined&&t.w>t.maxWidth+.5)violations.push({type:'text-max-width',text:t});if(t.x<region.left-.5||t.x+t.w>region.right+.5||t.y<region.top-.5||t.y+t.h>region.bottom+.5)violations.push({type:'text-safe-region',text:t,region});}
   for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++)if(overlap(texts[i],texts[j]))violations.push({type:'text-text-overlap',a:texts[i],b:texts[j]});
   const nodes=Array.from(root.querySelectorAll('[data-node-id]')).filter(visible).map(e=>({id:e.getAttribute('data-node-id'),value:e.getAttribute('data-node-value'),height:Number(e.getAttribute('data-node-height')),inserted:e.getAttribute('data-node-inserted'),actualTexts:labels(e),ports:Array.from(e.querySelectorAll('[data-port-level]')).filter(visible).map(p=>({level:Number(p.getAttribute('data-port-level')),value:p.getAttribute('data-port-value'),next:p.getAttribute('data-port-next'),actualTexts:labels(p),geometry:geometry(p),...box(p)})),...box(e)}));
   const ports=Array.from(root.querySelectorAll('[data-port-level]')).filter(visible).map(e=>({node:e.getAttribute('data-port-node')??e.closest('[data-node-id]')?.getAttribute('data-node-id'),level:Number(e.getAttribute('data-port-level')),value:e.getAttribute('data-port-value'),next:e.getAttribute('data-port-next'),actualTexts:labels(e),geometry:geometry(e),...box(e)}));
   const edges=Array.from(root.querySelectorAll('[data-edge-from]')).filter(visible).map(e=>({from:e.getAttribute('data-edge-from'),to:e.getAttribute('data-edge-to'),level:Number(e.getAttribute('data-edge-level')),kind:e.getAttribute('data-edge-kind')??'actual',geometry:geometry(e),...box(e)}));
   const cursors=Array.from(root.querySelectorAll('[data-cursor-node]')).filter(visible).map(e=>({node:e.getAttribute('data-cursor-node'),level:Number(e.getAttribute('data-cursor-level')),geometry:geometry(e),...box(e)}));
   const motions=Array.from(root.querySelectorAll('[data-motion-kind]')).filter(visible).map(e=>({kind:e.getAttribute('data-motion-kind'),from:e.getAttribute('data-motion-from'),to:e.getAttribute('data-motion-to'),level:Number(e.getAttribute('data-motion-level')),toLevel:e.hasAttribute('data-motion-to-level')?Number(e.getAttribute('data-motion-to-level')):undefined,progress:Number(e.getAttribute('data-motion-progress')),geometry:geometry(e),...box(e)}));
   const comparisons=Array.from(root.querySelectorAll('[data-comparison]')).filter(visible).map(e=>({current:e.getAttribute('data-current'),candidate:e.getAttribute('data-candidate'),target:e.getAttribute('data-target'),canAdvance:e.getAttribute('data-can-advance'),actualTexts:labels(e),...box(e)}));
   const results=Array.from(root.querySelectorAll('[data-result-kind]')).filter(visible).map(e=>({kind:e.getAttribute('data-result-kind'),actualTexts:labels(e),...box(e)}));
   const captions=Array.from(root.parentElement?.querySelectorAll('[data-subtitle]')??[]).filter(visible).map(e=>({text:e.textContent??'',...box(e)}));
   console.log('SKIPLIST_LAYOUT_AUDIT '+JSON.stringify({kind,frame,region,texts,nodes,ports,edges,cursors,motions,comparisons,results,captions,measurements:{textCount:texts.length,nodeCount:nodes.length,portCount:ports.length,edgeCount:edges.length,cursorCount:cursors.length,motionCount:motions.length,comparisonCount:comparisons.length,captionCount:captions.length},violations}));
  });return()=>{disposed=true;};
 },[enabled,kind,frame]);
};
