export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const ease=(f:number,start:number,duration=36)=>{const p=clamp((f-start)/Math.max(1,duration));return p*p*(3-2*p);};
export const lerp=(a:number,b:number,p:number)=>a+(b-a)*p;
