export type Door=1|2|3;
export const DOORS:Door[]=[1,2,3];
export type World={id:string;initial:Door;prize:Door;host:Door;target:Door;legalHost:Door[];weight:number};
export const clamp=(v:number)=>Math.max(0,Math.min(1,v));
export const ease=(v:number)=>{v=clamp(v);return v*v*(3-2*v);};
export const mix=(a:number,b:number,p:number)=>a+(b-a)*p;
export const legalHostDoors=(initial:Door,prize:Door)=>DOORS.filter(d=>d!==initial&&d!==prize);
export const createWorld=(prize:Door,initial:Door=1,host?:Door):World=>{
 const legalHost=legalHostDoors(initial,prize),chosen=host??legalHost[legalHost.length-1];
 if(!legalHost.includes(chosen))throw Error('Host must open an unselected empty door');
 return{id:'prize-'+prize,initial,prize,host:chosen,target:DOORS.find(d=>d!==initial&&d!==chosen)!,legalHost,weight:1/3};
};
export const WORLDS=DOORS.map(p=>createWorld(p));
export type Progress={pick:number;host:number;swap:number;reveal:number};
export const CLOSED:Progress={pick:0,host:0,swap:0,reveal:0};
export const PICKED:Progress={pick:1,host:0,swap:0,reveal:0};
export const OFFER:Progress={pick:1,host:1,swap:0,reveal:0};
export const COMPLETE:Progress={pick:1,host:1,swap:1,reveal:1};
export const stateAt=(world:World,p:Progress)=>{
 for(const value of Object.values(p))if(value<0||value>1)throw Error('Progress outside [0,1]');
 if(p.host>0&&p.pick<1)throw Error('Host acts only after initial selection');
 if(p.swap>0&&p.host<1)throw Error('Player switches only after host opens the empty door');
 if(p.reveal>0&&p.swap<1)throw Error('Final door opens only after the player arrives');
 const selection=p.pick<1?null:p.swap>0&&p.swap<1?null:p.swap===1?world.target:world.initial;
 return{...world,progress:p,initialSelected:p.pick===1,hostCommitted:p.host===1,selection,selectionMoving:p.swap>0&&p.swap<1,resultCommitted:p.reveal===1,result:p.reveal===1?(world.target===world.prize?'win':'lose'):null,prizeVisible:p.reveal===1&&world.target===world.prize};
};
export type Layout={xs:number[];y:number;width:number;height:number;small:number};
export const HERO:Layout={xs:[550,960,1370],y:520,width:270,height:330,small:0};
export const ROWS:Layout[]=[390,580,770].map(y=>({xs:[650,960,1270],y,width:180,height:112,small:1}));
export const morphLayout=(a:Layout,b:Layout,p:number):Layout=>({xs:a.xs.map((v,i)=>mix(v,b.xs[i],p)),y:mix(a.y,b.y,p),width:mix(a.width,b.width,p),height:mix(a.height,b.height,p),small:mix(a.small,b.small,p)});
export const selectorAt=(world:World,p:number,l:Layout)=>{
 const from=l.xs[world.initial-1],to=l.xs[world.target-1],baseW=l.width+24,baseH=l.height+24,pillW=mix(164,118,l.small),pillH=mix(64,40,l.small),pillY=l.y+l.height/2+mix(105,24,l.small),baseLabel=l.y+l.height/2+mix(66,46,l.small),pillLabel=pillY+mix(12,9,l.small);
 if(p<.22){const q=ease(p/.22);return{x:from,y:mix(l.y,pillY,q),w:mix(baseW,pillW,q),h:mix(baseH,pillH,q),labelY:mix(baseLabel,pillLabel,q),stage:'contract'};}
 if(p<.78){const q=ease((p-.22)/.56);return{x:mix(from,to,q),y:pillY,w:pillW,h:pillH,labelY:pillLabel,stage:'travel'};}
 const q=ease((p-.78)/.22);return{x:to,y:mix(pillY,l.y,q),w:mix(pillW,baseW,q),h:mix(pillH,baseH,q),labelY:mix(pillLabel,baseLabel,q),stage:'expand'};
};
