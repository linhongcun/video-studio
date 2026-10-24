import {useEffect} from 'react';

// Opt-in QA only. Measurements come from the actual Chromium SVG/DOM after fonts load.
export const useLayoutAudit=(enabled:boolean,kind:string,frame:number)=>{
 useEffect(()=>{
  if(!enabled)return;
  let disposed=false;
  const run=()=>{
   if(disposed)return;
   const root=document.querySelector(kind==='main'?'[data-audit-scene]':'[data-cover-root]') as SVGElement|HTMLElement|null;
   if(!root)return;
   const base=root.getBoundingClientRect(),width=kind==='main'?1920:Number(root.getAttribute('data-canvas-width')),height=kind==='main'?1080:Number(root.getAttribute('data-canvas-height'));
   const sx=base.width/width,sy=base.height/height;
   const box=(el:Element)=>{const r=el.getBoundingClientRect();return{x:(r.x-base.x)/sx,y:(r.y-base.y)/sy,w:r.width/sx,h:r.height/sy};};
   const opacity=(el:Element)=>{let out=1,node:Element|null=el;while(node&&node!==root.parentElement){out*=Number(getComputedStyle(node).opacity);node=node.parentElement;}return out;};
   const visible=(el:Element)=>opacity(el)>.03;
   const texts=Array.from(root.querySelectorAll('svg text, text, [data-layout-text]')).filter(el=>visible(el)&&(el.textContent??'').trim()&&(!el.hasAttribute('data-layout-text')||Array.from(el.childNodes).some(n=>n.nodeType===Node.TEXT_NODE&&(n.textContent??'').trim()))).map(el=>({text:el.textContent??'',...box(el),kind:el.tagName,horse:el.closest('[data-horse-id]')?.getAttribute('data-horse-id')??null}));
   const nodes=Array.from(root.querySelectorAll('[data-horse-id]')).filter(visible).map(el=>({id:el.getAttribute('data-horse-id'),...box(el.querySelector('rect')??el)}));
   const violations:any[]=[];
   const region=kind==='main'?{left:75,right:1845,top:45,bottom:1040}:kind==='4x3'?{left:315,right:1125,top:0,bottom:918}:kind==='3x4'?{left:95,right:985,top:0,bottom:1224}:{left:140,right:1810,top:0,bottom:918};
   for(const text of texts){if(text.x<region.left-.5||text.x+text.w>region.right+.5||text.y<region.top-.5||text.y+text.h>region.bottom+.5)violations.push({type:'text-outside-safe-region',text,region});
    if(text.horse){const node=nodes.find(n=>n.id===text.horse);if(node&&(text.x<node.x+4||text.x+text.w>node.x+node.w-4||text.y<node.y+4||text.y+text.h>node.y+node.h-4))violations.push({type:'horse-label-copyfit',text,node});}
   }
   for(let i=0;i<nodes.length;i++)for(let j=i+1;j<nodes.length;j++){
    const a=nodes[i],b=nodes[j],w=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),h=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);
    if(w>3&&h>3)violations.push({type:'visible-horse-overlap',a:a.id,b:b.id,w,h});
   }
   const subtitle=document.querySelector('[data-subtitle]');
   const subtitleBox=subtitle?box(subtitle):null;
   const notes=Array.from(root.querySelectorAll('[data-note]')).filter(visible).map(box);
   if(subtitleBox)for(const note of notes)if(note.y+note.h>subtitleBox.y-6)violations.push({type:'note-subtitle-overlap',note,subtitle:subtitleBox});
   console.log('HORSE_LAYOUT_AUDIT '+JSON.stringify({kind,frame,width,height,region,texts,nodes,notes,subtitle:subtitleBox,violations}));
  };
  document.fonts.ready.then(run);
  return()=>{disposed=true;};
 },[enabled,kind,frame]);
};
