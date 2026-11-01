import {useEffect} from 'react';
export const useLayoutAudit=(enabled:boolean,kind:string,frame:number)=>{
 useEffect(()=>{
  if(!enabled)return;let disposed=false;
  document.fonts.ready.then(()=>{
   if(disposed)return;
   const root=document.querySelector(kind==='main'?'[data-audit-scene]':'[data-cover-root]') as HTMLElement|SVGElement|null;
   if(!root)return;const base=root.getBoundingClientRect(),width=kind==='main'?1920:Number(root.getAttribute('data-canvas-width')),height=kind==='main'?1080:Number(root.getAttribute('data-canvas-height')),sx=base.width/width,sy=base.height/height;
   const box=(el:Element)=>{const r=el.getBoundingClientRect();return{x:(r.x-base.x)/sx,y:(r.y-base.y)/sy,w:r.width/sx,h:r.height/sy};};
   const visible=(el:Element)=>{let a=1,n:Element|null=el;while(n&&n!==root.parentElement){a*=Number(getComputedStyle(n).opacity);n=n.parentElement;}return a>.03;};
   const texts=Array.from(root.querySelectorAll('text,[data-layout-text]')).filter(el=>visible(el)&&(el.textContent??'').trim()).map(el=>({text:el.textContent??'',...box(el),person:el.closest('[data-person]')?.getAttribute('data-person')??null}));
   const nodes=Array.from(root.querySelectorAll('[data-person]')).filter(visible).map(el=>({id:el.getAttribute('data-person'),...box(el.querySelector('[data-person-body]')??el)}));
   const region=kind==='main'?{left:75,right:1845,top:45,bottom:1040}:kind==='4x3'?{left:315,right:1125,top:0,bottom:918}:kind==='3x4'?{left:95,right:985,top:0,bottom:1224}:{left:140,right:1810,top:0,bottom:918};
   const overlap=(a:any,b:any)=>Math.min(a.x+a.w,b.x+b.w)>Math.max(a.x,b.x)+2&&Math.min(a.y+a.h,b.y+b.h)>Math.max(a.y,b.y)+2;
   const violations:any[]=[];
   for(const t of texts){if(t.x<region.left-.5||t.x+t.w>region.right+.5||t.y<region.top-.5||t.y+t.h>region.bottom+.5)violations.push({type:'text-safe-region',text:t,region});if(t.person){const n=nodes.find(x=>x.id===t.person);if(n&&(t.x<n.x+3||t.x+t.w>n.x+n.w-3||t.y<n.y+3||t.y+t.h>n.y+n.h-3))violations.push({type:'person-copyfit',text:t,node:n});}}
   for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++)if(overlap(nodes[i],nodes[j]))violations.push({type:'person-overlap',a:nodes[i],b:nodes[j]});
   const torchElements=Array.from(root.querySelectorAll('[data-torch]')).filter(visible),torches=torchElements.map(el=>box(el.querySelector('rect')??el));
   if(kind==='main'&&nodes.length&&torches.length!==1)violations.push({type:'unique-torch',count:torches.length});
   for(const torch of torches)for(const node of nodes)if(overlap(torch,node))violations.push({type:'torch-person-overlap',torch,node});
   const sub=document.querySelector('[data-subtitle]'),subtitle=sub?box(sub):null,notes=Array.from(root.querySelectorAll('[data-note]')).filter(visible).map(box);
   if(subtitle)for(const note of notes)if(overlap(note,subtitle))violations.push({type:'note-subtitle-overlap',note,subtitle});
   const bridge=root.querySelector('[data-bridge-state]');
   console.log('BRIDGE_LAYOUT_AUDIT '+JSON.stringify({kind,frame,region,texts,nodes,torches,subtitle,notes,bridgeState:bridge?JSON.parse(bridge.getAttribute('data-bridge-state')??'null'):null,violations}));
  });return()=>{disposed=true;};
 },[enabled,kind,frame]);
};
