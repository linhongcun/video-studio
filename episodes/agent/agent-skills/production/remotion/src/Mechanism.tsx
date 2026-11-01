import React from 'react';
import {C} from './theme';
import {Box,T,Pill,Arrow,Packet,DotPacket,ease} from './primitives';
export type Phase='catalog'|'instructions'|'paths'|'reference'|'script'|'evidence'|'limits';
export const SkillGraph=({phase,p=0,q=0,roles=false}: {phase:Phase;p?:number;q?:number;roles?:boolean})=>{
 const instruction=['instructions','paths','reference','script','evidence','limits'].includes(phase),reference=['script','evidence','limits'].includes(phase)||(phase==='reference'&&p>=.88),result=['evidence','limits'].includes(phase)||(phase==='script'&&q>=.88),showPaths=['paths','reference','script','evidence'].includes(phase),focusRef=phase==='reference',focusScript=phase==='script';
 const toolAlpha=showPaths?1:phase==='limits' ? .35 : 0,metadataOnly=phase==='catalog';
 return <g data-mechanism-state={JSON.stringify({phase,p,q,context:{metadata:true,instructions:instruction,reference,result},scriptSourceInContext:false})}>
  <Box x={120} y={300} w={610} h={526} title={roles?"Skill · 组织工作方法":"可复用的技能包"} color={C.edge}/>
  <T x={150} y={401} size={29} color={C.teal} mono>api-compat-review</T>
  <Pill x={150} y={432} w={550} text="名称 + 描述" color={C.teal}/>
  <Pill x={150} y={524} w={550} text="SKILL.md · 审查步骤" color={instruction?C.gold:C.edge} alpha={metadataOnly ? .45 : 1}/>
  <Pill x={150} y={616} w={550} text="request-fields.md · 规则" color={focusRef?C.teal:C.edge} alpha={metadataOnly ? .35 : 1}/>
  <Pill x={150} y={708} w={550} text="check_fields.py · 检查" color={focusScript?C.blue:C.edge} alpha={metadataOnly ? .35 : 1}/>
  <Box x={1150} y={300} w={650} h={526} title="这次送给模型的内容" color={C.edge}/>
  <Pill x={1180} y={385} w={590} text="当前任务：审查这次接口变更" color={C.text}/>
  <Pill x={1180} y={466} w={590} text={metadataOnly?'候选技能的名称与适用描述':'已选：API 兼容审查'} color={C.teal}/>
  {instruction&&<g opacity={phase==='instructions'?ease((p-.95)/.05):1}><Pill x={1180} y={547} w={590} text={roles?"Prompt · 已加载的审查指令":"审查步骤：比较 → 核验 → 报告"} color={C.gold}/></g>}
  {(reference||focusRef)&&<g opacity={focusRef?ease((p-.88)/.12):1}><Pill x={1180} y={628} w={590} text="规则：新增必填项会影响旧请求" color={C.teal} size={27}/></g>}
  {(result||focusScript)&&<g opacity={focusScript?ease((q-.95)/.05):1}><Pill x={1180} y={709} w={590} text="结果：新增必填 channel" color={C.blue}/></g>}
  {phase==='instructions'&&<><Arrow x1={735} y1={555} x2={1140} y2={577} color={C.gold}/><Packet p={p} from={[735,555]} to={[1140,577]} text="读取审查步骤" color={C.gold} w={310}/></>}
  {showPaths&&<>
   {!focusScript&&<Arrow x1={735} y1={649} x2={1140} y2={658} color={C.teal} dashed={!focusRef}/>}
   {focusRef&&<Packet p={p} from={[735,649]} to={[1140,658]} text="只取所需规则" color={C.teal} w={310}/>}
   <g opacity={toolAlpha}><rect x={778} y={712} width={322} height={112} rx={18} fill={C.surface} stroke={focusScript?C.blue:C.edge} strokeWidth={2}/><T x={939} y={751} size={28} color={focusScript?C.blue:C.text} anchor="middle">{roles?"工具 · 实际执行能力":"宿主工具"}</T><T x={939} y={804} size={27} color={C.muted} anchor="middle">{focusScript?(p<.9?"等待执行":q<.1?"执行中":"运行完成"):"执行脚本"}</T><Arrow x1={735} y1={741} x2={772} y2={760} color={C.blue}/><Arrow x1={1105} y1={760} x2={1140} y2={741} color={C.blue}/></g>
   {phase==='paths'&&<><T x={940} y={621} size={26} color={C.teal} anchor="middle">资料：读取</T><T x={940} y={682} size={25} color={C.blue} anchor="middle">脚本：执行后回结果</T></>}
   {focusScript&&<><T x={939} y={302} size={25} color={C.blue} anchor="middle">检查输入（3份）</T><Pill x={785} y={334} w={310} text="旧接口定义" color={C.muted} size={26}/><Pill x={785} y={425} w={310} text="新接口定义" color={C.muted} size={26}/><Pill x={785} y={516} w={310} text="旧客户端请求" color={C.gold} size={26}/><Arrow x1={939} y1={590} x2={939} y2={698} color={C.blue}/><DotPacket p={p} from={[735,741]} to={[795,760]} color={C.blue}/><DotPacket p={q} from={[1095,760]} to={[1165,741]} color={C.blue}/></>}
  </>}
 </g>;
};
