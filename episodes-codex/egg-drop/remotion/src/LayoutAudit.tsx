import {useEffect} from 'react';
export const useLayoutAudit=(enabled:boolean,kind:string,frame:number)=>{
 useEffect(()=>{
  if(!enabled)return;let disposed=false;
  document.fonts.ready.then(()=>{
   if(disposed)return;const root=document.querySelector(kind==='main'?'[data-audit-scene]':'[data-cover-root]') as HTMLElement|SVGElement|null;if(!root)return;
   const base=root.getBoundingClientRect(),width=kind==='main'?1920:Number(root.getAttribute('data-canvas-width')),height=kind==='main'?1080:Number(root.getAttribute('data-canvas-height')),sx=base.width/width,sy=base.height/height;
   const box=(el:Element)=>{const r=el.getBoundingClientRect();return{x:(r.x-base.x)/sx,y:(r.y-base.y)/sy,w:r.width/sx,h:r.height/sy};};
   const visible=(el:Element)=>{let alpha=1,n:Element|null=el;while(n&&n!==root.parentElement){alpha*=Number(getComputedStyle(n).opacity);n=n.parentElement;}return alpha>.03;};
   const texts=Array.from(root.querySelectorAll('text,[data-layout-text]')).filter(el=>visible(el)&&(el.textContent??'').trim()).map(el=>({text:el.textContent??'',...box(el),egg:el.closest('[data-egg]')?.getAttribute('data-egg')??null,floor:el.closest('[data-floor-label]')?.getAttribute('data-floor-label')??null}));
   const region=kind==='main'?{left:75,right:1845,top:45,bottom:1040}:kind==='4x3'?{left:315,right:1125,top:0,bottom:918}:kind==='3x4'?{left:95,right:985,top:0,bottom:1224}:{left:140,right:1810,top:0,bottom:918};
   const overlap=(a:any,b:any)=>Math.min(a.x+a.w,b.x+b.w)>Math.max(a.x,b.x)+2&&Math.min(a.y+a.h,b.y+b.h)>Math.max(a.y,b.y)+2;
   const violations:any[]=[];
   for(const t of texts)if(t.x<region.left-.5||t.x+t.w>region.right+.5||t.y<region.top-.5||t.y+t.h>region.bottom+.5)violations.push({type:'text-safe-region',text:t,region});
   for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++)if(overlap(texts[i],texts[j]))violations.push({type:'text-text-overlap',a:texts[i],b:texts[j]});
   const panels=Array.from(root.querySelectorAll('[data-panel]')).map(el=>({body:box(el.querySelector('rect')!),texts:Array.from(el.querySelectorAll('text')).filter(visible).map(el=>({text:el.textContent,...box(el)}))}));
   for(const p of panels)for(const t of p.texts)if(t.x<p.body.x+14||t.x+t.w>p.body.x+p.body.w-14||t.y<p.body.y+10||t.y+t.h>p.body.y+p.body.h-10)violations.push({type:'panel-copyfit',text:t,body:p.body});
   const states=Array.from(root.querySelectorAll('[data-visual-state]')).map(el=>JSON.parse(el.getAttribute('data-visual-state')!));
   const eggs=Array.from(root.querySelectorAll('[data-egg-actor]')).map(el=>({id:Number(el.getAttribute('data-egg-actor')),centerX:Number(el.getAttribute('data-x')),centerY:Number(el.getAttribute('data-y')),holder:el.getAttribute('data-holder')==='true',...box(el.querySelector('[data-egg]')!)}));
   for(const s of states){
    if(s.world.safe<0||s.world.breaking>101||s.world.safe>=s.world.breaking)violations.push({type:'invalid-known-interval',state:s});
    if(s.trial){const t=s.trial;if(t.trial.floor<1||t.trial.floor>100)violations.push({type:'trial-outside-building',state:s});if(t.committed&&!t.landed)violations.push({type:'commit-before-ground',state:s});if(t.landed){const actor=eggs.find(e=>e.id===t.trial.egg);if(actor&&actor.centerY<819)violations.push({type:'landed-above-ground',state:s,actor});}}
   }
   const sub=document.querySelector('[data-subtitle]'),subtitle=sub?box(sub):null,notes=Array.from(root.querySelectorAll('[data-note]')).filter(visible).map(box);if(subtitle)for(const note of notes)if(overlap(note,subtitle))violations.push({type:'note-subtitle-overlap',note,subtitle});
   console.log('EGG_LAYOUT_AUDIT '+JSON.stringify({kind,frame,region,texts,panels,states,eggs,subtitle,notes,violations}));
  });return()=>{disposed=true;};
 },[enabled,kind,frame]);
};
