import React from 'react';
import style from './style-v1.json';
import {C,FONT} from './theme';
/** Exact original logo bytes; provenance and SHA live in style-v1.json. */
const REDIS_MARK="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMjggMTI4Ij48cGF0aCBmaWxsPSIjQTQxRTExIiBkPSJNMTIxLjggOTMuMWMtNi43IDMuNS00MS40IDE3LjctNDguOCAyMS42LTcuNCAzLjktMTEuNSAzLjgtMTcuMyAxUzEzIDk4LjEgNi4zIDk0LjljLTMuMy0xLjYtNS0yLjktNS00LjJWNzhzNDgtMTAuNSA1NS44LTEzLjJjNy44LTIuOCAxMC40LTIuOSAxNy0uNXM0Ni4xIDkuNSA1Mi42IDExLjl2MTIuNWMwIDEuMy0xLjUgMi43LTQuOSA0LjR6Ii8+PHBhdGggZmlsbD0iI0Q4MkMyMCIgZD0iTTEyMS44IDgwLjVDMTE1LjEgODQgODAuNCA5OC4yIDczIDEwMi4xYy03LjQgMy45LTExLjUgMy44LTE3LjMgMS01LjgtMi44LTQyLjctMTcuNy00OS40LTIwLjlDLS4zIDc5LS41IDc2LjggNiA3NC4zYzYuNS0yLjYgNDMuMi0xNyA1MS0xOS43IDcuOC0yLjggMTAuNC0yLjkgMTctLjVzNDEuMSAxNi4xIDQ3LjYgMTguNWM2LjcgMi40IDYuOSA0LjQuMiA3Ljl6Ii8+PHBhdGggZmlsbD0iI0E0MUUxMSIgZD0iTTEyMS44IDcyLjVDMTE1LjEgNzYgODAuNCA5MC4yIDczIDk0LjFjLTcuNCAzLjgtMTEuNSAzLjgtMTcuMyAxQzQ5LjkgOTIuMyAxMyA3Ny40IDYuMyA3NC4yYy0zLjMtMS42LTUtMi45LTUtNC4yVjU3LjNzNDgtMTAuNSA1NS44LTEzLjJjNy44LTIuOCAxMC40LTIuOSAxNy0uNXM0Ni4xIDkuNSA1Mi42IDExLjlWNjhjMCAxLjMtMS41IDIuNy00LjkgNC41eiIvPjxwYXRoIGZpbGw9IiNEODJDMjAiIGQ9Ik0xMjEuOCA1OS44Yy02LjcgMy41LTQxLjQgMTcuNy00OC44IDIxLjYtNy40IDMuOC0xMS41IDMuOC0xNy4zIDFDNDkuOSA3OS42IDEzIDY0LjcgNi4zIDYxLjVzLTYuOC01LjQtLjMtNy45YzYuNS0yLjYgNDMuMi0xNyA1MS0xOS43IDcuOC0yLjggMTAuNC0yLjkgMTctLjVzNDEuMSAxNi4xIDQ3LjYgMTguNWM2LjcgMi40IDYuOSA0LjQuMiA3Ljl6Ii8+PHBhdGggZmlsbD0iI0E0MUUxMSIgZD0iTTEyMS44IDUxYy02LjcgMy41LTQxLjQgMTcuNy00OC44IDIxLjYtNy40IDMuOC0xMS41IDMuOC0xNy4zIDFDNDkuOSA3MC45IDEzIDU2IDYuMyA1Mi44Yy0zLjMtMS42LTUuMS0yLjktNS4xLTQuMlYzNS45czQ4LTEwLjUgNTUuOC0xMy4yYzcuOC0yLjggMTAuNC0yLjkgMTctLjVzNDYuMSA5LjUgNTIuNiAxMS45djEyLjVjLjEgMS4zLTEuNCAyLjYtNC44IDQuNHoiLz48cGF0aCBmaWxsPSIjRDgyQzIwIiBkPSJNMTIxLjggMzguM0MxMTUuMSA0MS44IDgwLjQgNTYgNzMgNTkuOWMtNy40IDMuOC0xMS41IDMuOC0xNy4zIDFTMTMgNDMuMyA2LjMgNDAuMXMtNi44LTUuNC0uMy03LjljNi41LTIuNiA0My4yLTE3IDUxLTE5LjcgNy44LTIuOCAxMC40LTIuOSAxNy0uNXM0MS4xIDE2LjEgNDcuNiAxOC41YzYuNyAyLjQgNi45IDQuNC4yIDcuOHoiLz48cGF0aCBmaWxsPSIjZmZmIiBkPSJNODAuNCAyNi4xbC0xMC44IDEuMi0yLjUgNS44LTMuOS02LjUtMTIuNS0xLjEgOS4zLTMuNC0yLjgtNS4yIDguOCAzLjQgOC4yLTIuN0w3MiAyM3pNNjYuNSA1NC41bC0yMC4zLTguNCAyOS4xLTQuNHoiLz48ZWxsaXBzZSBmaWxsPSIjZmZmIiBjeD0iMzguNCIgY3k9IjM1LjQiIHJ4PSIxNS41IiByeT0iNiIvPjxwYXRoIGZpbGw9IiM3QTBDMDAiIGQ9Ik05My4zIDI3LjdsMTcuMiA2LjgtMTcuMiA2Ljh6Ii8+PHBhdGggZmlsbD0iI0FEMjExNSIgZD0iTTc0LjMgMzUuM2wxOS03LjZ2MTMuNmwtMS45Ljh6Ii8+PC9zdmc+";
export const RedisBackdrop=()=> <g data-redis-canvas="true" aria-hidden="true">
 <rect width="1920" height="1080" fill="transparent"/>
 <g fill="none" stroke={C.edge} strokeWidth="1" opacity=".34">
  <path d="M1640 0L1920 280M1770 0L1920 150M0 870L210 1080M0 1000L80 1080"/>
 </g>
</g>;
export const RedisHeader=({ep,title,chapter=''}:{ep:number;title:string;chapter?:string})=> {
 if(!Number.isInteger(ep)||ep<1)throw Error('RedisHeader requires a real episode number');
 return <g data-redis-header="true" fontFamily={FONT}>
  <image data-redis-mark="true" href={REDIS_MARK} x="113" y="35" width="58" height="58"/>
  <text x="189" y="79" fontSize="34" fill={C.redDark} fontWeight="800">{style.seriesLabel}</text>
  <rect x="416" y="43" width="127" height="47" rx="10" fill={C.red}/>
  <text x="479.5" y="76" fontFamily={style.fonts.brand} fontSize="26" fill={C.surface} fontWeight="750" textAnchor="middle">EP.{String(ep).padStart(2,'0')}</text>
  <text data-redis-subject="true" x="570" y="77" fontSize="26" fill={C.text} fontWeight="650">{title}</text>
  {chapter&&<text data-redis-chapter="true" x="768" y="77" fontSize="24" fill={C.muted}>{chapter}</text>}
  <text x="1805" y="77" fontSize="25" fill={C.muted} fontWeight="650" textAnchor="end">{style.brand}</text>
  <path d="M115 111H1805" fill="none" stroke={C.edge} strokeWidth="1.5"/>
 </g>;
};
