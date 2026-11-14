const C={bg:'#0F172A',edge:'#30435E',text:'#E5E7EB',muted:'#9CAFC5',gold:'#FFCC70',teal:'#56E4D3'};
const el=(name,attrs,body='')=>'<'+name+Object.entries(attrs).map(([k,v])=>' '+k+'="'+String(v)+'"').join('')+'>'+body+'</'+name+'>';
const txt=(x,y,s,color,size)=>el('text',{x,y,fill:color,'font-size':size,'font-weight':600,'text-anchor':'middle'},s);
const line=(x1,y1,x2,y2,color,w)=>el('line',{x1,y1,x2,y2,stroke:color,'stroke-width':w,'stroke-linecap':'round'});
const dot=(x,y,c)=>el('circle',{cx:x,cy:y,r:8,fill:c,stroke:C.bg,'stroke-width':2});
function mergeIntervals(){
 const x=n=>108+(n-2)*112,a=x(3),b=x(5),c=x(6);
 return txt(300,55,'两端包含 · 端点相接',C.gold,29)+
 line(a,153,b,153,C.teal,10)+dot(a,153,C.teal)+dot(b,153,C.teal)+txt((a+b)/2,126,'I3 [3,5]',C.teal,24)+
 line(b,244,c,244,C.gold,10)+dot(b,244,C.gold)+dot(c,244,C.gold)+txt((b+c)/2,216,'I4 [5,6]',C.gold,24)+
 line(80,310,520,310,C.edge,3)+[3,5,6].map(n=>line(x(n),300,x(n),320,C.text,2)+txt(x(n),350,String(n),C.text,25)).join('');
}
const DRAW=new Map([[56,mergeIntervals]]);
export const SUPPORTED_PROBLEMS=Object.freeze([...DRAW.keys()]);
export function diagram(n){const f=DRAW.get(Number(n));if(!f)throw new RangeError('Unsupported LeetCode problem: '+n);return el('g',{'data-leetcode-diagram':n,'font-family':'Noto Sans CJK SC'},f());}
