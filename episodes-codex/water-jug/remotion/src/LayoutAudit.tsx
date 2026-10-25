import {useEffect} from 'react';
export const useLayoutAudit=(enabled:boolean,kind:string,frame:number)=>{
 useEffect(()=>{
  if(!enabled)return;let disposed=false;
  document.fonts.ready.then(()=>{
   if(disposed)return;const root=document.querySelector(kind==='main'?'[data-audit-scene]':'[data-cover-root]') as HTMLElement|SVGElement|null;if(!root)return;
   const base=root.getBoundingClientRect(),width=kind==='main'?1920:Number(root.getAttribute('data-canvas-width')),height=kind==='main'?1080:Number(root.getAttribute('data-canvas-height')),sx=base.width/width,sy=base.height/height;
   const box=(el:Element)=>{const r=el.getBoundingClientRect();return{x:(r.x-base.x)/sx,y:(r.y-base.y)/sy,w:r.width/sx,h:r.height/sy};};
   const visible=(el:Element)=>{let alpha=1,n:Element|null=el;while(n&&n!==root.parentElement){alpha*=Number(getComputedStyle(n).opacity);n=n.parentElement;}return alpha>.03;};
   const texts=Array.from(root.querySelectorAll('text,[data-layout-text]')).filter(el=>visible(el)&&(el.textContent??'').trim()).map(el=>({text:el.textContent??'',...box(el)}));
   const region=kind==='main'?{left:75,right:1845,top:45,bottom:1040}:kind==='4x3'?{left:315,right:1125,top:0,bottom:918}:kind==='3x4'?{left:95,right:985,top:0,bottom:1224}:{left:140,right:1810,top:0,bottom:918};
   const violations:any[]=[];for(const text of texts)if(text.x<region.left-.5||text.x+text.w>region.right+.5||text.y<region.top-.5||text.y+text.h>region.bottom+.5)violations.push({type:'text-safe-region',text,region});
   const node=root.querySelector('[data-water-state]'),waterState=node?JSON.parse(node.getAttribute('data-water-state')??'null'):null;
   const containers=Array.from(root.querySelectorAll('[data-container]')).map(el=>{const liquid=el.querySelector('[data-liquid]')!,body=el.querySelector('[data-capacity-body]')!,reading=el.querySelector('[data-reading]')!;return{id:Number(el.getAttribute('data-container')),volume:Number(el.getAttribute('data-volume')),capacity:Number(el.getAttribute('data-capacity')),mode:el.getAttribute('data-reading-mode'),body:box(body),liquid:box(liquid),reading:{text:reading.textContent,...box(reading)}};});
   if(waterState){
    for(const c of containers){if(c.volume<-.00001||c.volume>c.capacity+.00001)violations.push({type:'capacity-range',container:c});if(Math.abs(c.liquid.h-c.volume*waterState.pixelsPerLiter)>.5)violations.push({type:'liquid-unit-scale',container:c});if(Math.abs(c.body.h-c.capacity*waterState.pixelsPerLiter)>.5)violations.push({type:'capacity-unit-scale',container:c});if(c.mode==='moving'&&/\d/.test(c.reading.text??''))violations.push({type:'moving-precise-reading',container:c});}
    const v=waterState.view;if(v){const expected=v.start[0]+v.start[1]+v.externalIn-v.externalOut;if(Math.abs(waterState.total-expected)>1e-8)violations.push({type:'water-balance',actual:waterState.total,expected});if(waterState.historyCount!==v.index+1+(v.complete?1:0))violations.push({type:'history-commit'});if(v.complete&&v.op.kind==='pour'&&v.volume[v.op.from]>1e-8&&Math.abs(v.volume[v.op.to]-waterState.capacity[v.op.to])>1e-8)violations.push({type:'illegal-pour-stop'});}
   }
   const overlap=(a:any,b:any)=>Math.min(a.x+a.w,b.x+b.w)>Math.max(a.x,b.x)+2&&Math.min(a.y+a.h,b.y+b.h)>Math.max(a.y,b.y)+2;
   const flowTips=Array.from(root.querySelectorAll('[data-flow-tip]')).filter(visible).map(box);for(const tip of flowTips)for(const text of texts)if(overlap(tip,text))violations.push({type:'flow-arrow-text-overlap',tip,text});
   const sub=document.querySelector('[data-subtitle]'),subtitle=sub?box(sub):null,notes=Array.from(root.querySelectorAll('[data-note]')).filter(visible).map(box);if(subtitle)for(const note of notes)if(overlap(note,subtitle))violations.push({type:'note-subtitle-overlap',note,subtitle});
   console.log('JUG_LAYOUT_AUDIT '+JSON.stringify({kind,frame,region,texts,containers,flowTips,waterState,subtitle,notes,violations}));
  });return()=>{disposed=true;};
 },[enabled,kind,frame]);
};
