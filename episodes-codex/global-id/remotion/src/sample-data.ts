// Teaching examples: relative milliseconds, generator identity, per-millisecond sequence.
// Never convert a composed ID through Number: the examples intentionally exceed 2^53-1.
export const TIME=4000000000n;
export function makeId(time:bigint,worker:bigint,sequence:bigint):string {
 if(time<0n||time>=(1n<<41n)||worker<0n||worker>=1024n||sequence<0n||sequence>=4096n)throw new Error('Demo field out of range');
 return ((time<<22n)|(worker<<12n)|sequence).toString();
}
export const IDS={base:makeId(TIME,7n,0n),worker:makeId(TIME,9n,0n),sequence:makeId(TIME,7n,1n),time:makeId(TIME+1n,7n,0n)};
