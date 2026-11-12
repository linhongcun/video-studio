export type Point={x:number;y:number};
export type Layout=Record<number,Point>;
const distance=(a:Point,b:Point)=>Math.hypot(a.x-b.x,a.y-b.y);
const segmentDistance=(p:Point,a:Point,b:Point)=>{
  const length=(b.x-a.x)**2+(b.y-a.y)**2;
  const t=length?Math.max(0,Math.min(1,((p.x-a.x)*(b.x-a.x)+(p.y-a.y)*(b.y-a.y))/length)):0;
  return distance(p,{x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t});
};

/** Route only the puzzle balls. One moving identity at a time avoids crossings. */
const route=(start:Point,end:Point,obstacles:Point[]):Point[]=>{
  if(distance(start,end)<1)return [start,end];
  const clear=(a:Point,b:Point)=>obstacles.every(p=>segmentDistance(p,a,b)>=101);
  if(clear(start,end))return [start,end];
  const step=30,nx=58,ny=19;
  const point=(id:number)=>({x:90+(id%nx)*step,y:280+Math.floor(id/nx)*step});
  const valid=(id:number)=>obstacles.every(p=>distance(p,point(id))>=103);
  const starts=Array.from({length:nx*ny},(_,id)=>id).filter(id=>valid(id)&&distance(start,point(id))<65&&clear(start,point(id)));
  const target=new Set(Array.from({length:nx*ny},(_,id)=>id).filter(id=>valid(id)&&distance(end,point(id))<65&&clear(end,point(id))));
  const previous=new Map<number,number>(),cost=new Map<number,number>();
  const pending=new Set(starts);
  starts.forEach(id=>cost.set(id,distance(start,point(id))));
  let finish=-1;
  while(pending.size){
    let id=-1,best=Infinity;
    pending.forEach(p=>{const score=cost.get(p)!+distance(point(p),end);if(score<best){id=p;best=score;}});
    pending.delete(id);
    if(target.has(id)){finish=id;break;}
    const x=id%nx,y=Math.floor(id/nx);
    const next=[x>0?id-1:-1,x<nx-1?id+1:-1,y>0?id-nx:-1,y<ny-1?id+nx:-1];
    next.filter(n=>n>=0&&valid(n)&&clear(point(id),point(n))).forEach(n=>{
      const c=cost.get(id)!+step;
      if(c<(cost.get(n)??Infinity)){cost.set(n,c);previous.set(n,id);pending.add(n);}
    });
  }
  if(finish<0)throw new Error(`No clear ball route ${JSON.stringify(start)} -> ${JSON.stringify(end)}`);
  const path=[end,point(finish)];
  let at=finish;
  while(previous.has(at)){at=previous.get(at)!;path.push(point(at));}
  path.push(start);path.reverse();
  // Remove unneeded grid bends; the result remains outside every other ball.
  const smooth=[path[0]];
  for(let i=0;i<path.length-1;){let j=path.length-1;while(j>i+1&&!clear(path[i],path[j]))j--;smooth.push(path[j]);i=j;}
  return smooth;
};

export type Move={id:number;path:Point[];distance:number};
export const planMoves=(source:Layout,target:Layout,order:number[]):Move[]=>{
  const positions={...source};
  return order.filter(id=>source[id]&&target[id]&&distance(source[id],target[id])>1).map(id=>{
    const obstacles=Object.entries(positions).filter(([n])=>Number(n)!==id).map(([,p])=>p);
    const path=route(positions[id],target[id],obstacles);
    positions[id]=target[id];
    return {id,path,distance:path.slice(1).reduce((sum,p,i)=>sum+distance(path[i],p),0)};
  });
};
const along=(move:Move,p:number)=>{
  let remaining=move.distance*p;
  for(let i=1;i<move.path.length;i++){
    const a=move.path[i-1],b=move.path[i],length=distance(a,b);
    if(remaining<=length||i===move.path.length-1){const t=length?Math.min(1,remaining/length):1;return {x:a.x+(b.x-a.x)*t,y:a.y+(b.y-a.y)*t};}
    remaining-=length;
  }
  return move.path[move.path.length-1];
};
export const ease=(p:number)=>{p=Math.max(0,Math.min(1,p));return p*p*(3-2*p);};
export const moveLayout=(source:Layout,moves:Move[],progress:number)=>{
  const positions={...source},q=Math.max(0,Math.min(1,progress))*moves.length;
  let moving:number|undefined;
  moves.forEach((move,i)=>{
    const p=Math.max(0,Math.min(1,q-i));
    positions[move.id]=along(move,ease(p));
    if(p>0&&p<1)moving=move.id;
  });
  return {positions,moving,settled:progress>=1};
};
