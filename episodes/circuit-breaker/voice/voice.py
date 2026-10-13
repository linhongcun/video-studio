import re,sys,json,subprocess
W='/workspace/vs-work/fix-server-cache-terms/episodes'
src=open('/workspace/sorkin-backup/circuit-breaker/script.md').read()
narr=re.findall(r'- 旁白：(.+)',src);assert len(narr)==6
IDX={'hook':0,'avalanche':1,'breaker':2,'half-open':3,'degrade':4,'recap':5}
ch,tag=sys.argv[1],sys.argv[2]
t=narr[IDX[ch]].replace('这是出 bug 了吗？','这是出故障了吗？')
if tag.startswith('v'): t=t.replace('调用','掉用')
py='/workspace/vs-work/feat-server-cache-voice/episodes/_shared/tts/.venv/bin/python'
subprocess.run([py,W+'/_shared/tts/mimo_say.py','--text',t,'--out',f'{ch}-{tag}.raw.wav','--gap','0.28','--segments',f'{ch}-{tag}.json'],check=True,capture_output=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',f'{ch}-{tag}.raw.wav','-ar','48000','-ac','1',f'{ch}-{tag}.wav'],check=True)
orig=re.findall(r'[^。？！]+[。？！]?',narr[IDX[ch]]);S=json.load(open(f'{ch}-{tag}.json'));assert len(orig)==len(S),(len(orig),len(S))
for s,o in zip(S,orig): s['tts']=s['text'];s['text']=o
json.dump(S,open(f'{ch}-{tag}.json','w'),ensure_ascii=False,indent=1)
print(ch,tag,len(S),flush=True)
