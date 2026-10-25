export const clamp=(n:number)=>Math.max(0,Math.min(1,n));
export const ease=(n:number)=>{const p=clamp(n);return p*p*(3-2*p);};
export const lerp=(a:number,b:number,p:number)=>a+(b-a)*clamp(p);
