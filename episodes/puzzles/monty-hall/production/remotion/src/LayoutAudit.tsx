import {useEffect} from 'react';
export const useLayoutAudit=(enabled:boolean,kind:string,frame:number)=>{
 useEffect(()=>{
  if(!enabled)return;let disposed=false;
  document.fonts.ready.then(()=>{
   if(disposed)return;const root=document.querySelector(kind==='main'?'[data-audit-scene]':'[data-cover-root]') as HTMLElement|SVGElement|null;if(!root)return;
   const base=root.getBoundingClientRect(),width=kind==='main'?1920:Number(root.getAttribute('data-canvas-width')),height=kind==='main'?1080:Number(root.getAttribute('data-canvas-height')),sx=base.width/width,sy=base.height/height;
   const box=(el:Element)=>{const r=el.getBoundingClientRect();return{x:(r.x-base.x)/sx,y:(r.y-base.y)/sy,w:r.width/sx,h:r.height/sy};};
   const visible=(el:Element)=>{let alpha=1,n:Element|null=el;while(n&&n!==root.parentElement){alpha*=Number(getComputedStyle(n).opacity);n=n.parentElement;}return alpha>.03;};
   const texts=Array.from(root.querySelectorAll('text,[data-layout-text]')).filter(el=>visible(el)&&(el.textContent??'').trim()).map(el=>({text:el.textContent??'',...box(el),door:el.closest('[data-door]')?.getAttribute('data-door')??null,world:el.closest('[data-world]')?.getAttribute('data-world')??null}));
   const region=kind==='main'?{left:75,right:1845,top:45,bottom:1040}:kind==='4x3'?{left:315,right:1125,top:0,bottom:918}:kind==='3x4'?{left:95,right:985,top:0,bottom:1224}:{left:140,right:1810,top:0,bottom:918};
   const overlap=(a:any,b:any)=>Math.min(a.x+a.w,b.x+b.w)>Math.max(a.x,b.x)+2&&Math.min(a.y+a.h,b.y+b.h)>Math.max(a.y,b.y)+2;
   const violations:any[]=[];
   for(const t of texts)if(t.x<region.left-.5||t.x+t.w>region.right+.5||t.y<region.top-.5||t.y+t.h>region.bottom+.5)violations.push({type:'text-safe-region',text:t,region});
   const doors=Array.from(root.querySelectorAll('[data-door]')).filter(visible).map(el=>({id:el.getAttribute('data-door'),world:el.closest('[data-world]')?.getAttribute('data-world'),number:Number(el.getAttribute('data-door-number')),openBy:el.getAttribute('data-open-by'),openProgress:Number(el.getAttribute('data-open-progress')),prize:el.getAttribute('data-is-prize')==='true',...box(el.querySelector('[data-door-body]')??el)}));
   for(const t of texts){if(t.door){const d=doors.find(d=>d.id===t.door);if(d&&(t.x<d.x+2||t.x+t.w>d.x+d.w-2||t.y<d.y+2||t.y+t.h>d.y+d.h-2))violations.push({type:'door-text-copyfit',text:t,door:d});}}
   const prizeIcons=Array.from(root.querySelectorAll('[data-prize-icon]')).filter(visible).map(el=>({door:el.closest('[data-door]')?.getAttribute('data-door'),...box(el)}));
   for(const star of prizeIcons)for(const t of texts)if(t.door===star.door&&overlap(star,t))violations.push({type:'prize-icon-text-overlap',star,text:t});
   const worlds=Array.from(root.querySelectorAll('[data-world-state]')).filter(visible).map(el=>JSON.parse(el.getAttribute('data-world-state')??'null'));
   for(const s of worlds){if(s.host===s.prize||s.host===s.initial)violations.push({type:'illegal-host',world:s.id});if(s.progress.reveal>0&&s.progress.swap<1)violations.push({type:'early-final-reveal',world:s.id});if(s.resultCommitted&&s.selection!==s.target)violations.push({type:'early-result',world:s.id});}
   for(const d of doors)if(d.openBy==='host'&&d.prize)violations.push({type:'host-opens-prize',door:d});
   const selectors=Array.from(root.querySelectorAll('[data-player-selector]')).filter(visible).map(el=>({world:el.closest('[data-world]')?.getAttribute('data-world'),stage:el.getAttribute('data-selector-stage'),...box(el.querySelector('[data-selector-body]')??el)}));
   for(const a of selectors)if(a.stage==='travel')for(const d of doors)if(d.id?.startsWith(a.world??'')&&overlap(a,d))violations.push({type:'travel-selector-crosses-door',selector:a,door:d});
   for(const a of texts)for(const b of texts){if(a===b)continue;if(a.world&&b.world&&a.world!==b.world&&overlap(a,b))violations.push({type:'cross-row-label-overlap',a,b});}
   for(const text of texts)if(text.world)for(const door of doors)if(door.world!==text.world&&overlap(text,door))violations.push({type:'cross-row-label-door-overlap',text,door});
   const weights=Array.from(root.querySelectorAll('[data-case-weight]')).filter(visible).map(el=>({prize:Number(el.getAttribute('data-case-weight')),...box(el)}));if(weights.length>3)violations.push({type:'too-many-weighted-cases',weights});
   const sub=document.querySelector('[data-subtitle]'),subtitle=sub?box(sub):null,notes=Array.from(root.querySelectorAll('[data-note]')).filter(visible).map(box);if(subtitle)for(const note of notes)if(overlap(note,subtitle))violations.push({type:'note-subtitle-overlap',note,subtitle});
   console.log('MONTY_LAYOUT_AUDIT '+JSON.stringify({kind,frame,region,texts,doors,worlds,selectors,prizeIcons,weights,subtitle,notes,violations}));
  });return()=>{disposed=true;};
 },[enabled,kind,frame]);
};
