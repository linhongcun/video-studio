#!/usr/bin/env python3
"""Exact-SHA technical approval for three changed narration sentences only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sentences(path):
    out=[]
    for block in re.split(r'(?=^### )',path.read_text(),flags=re.M):
        heading=re.match(r'### (\d+) ([a-z-]+)',block)
        if not heading:continue
        line=re.search(r'^旁白：(.*)$',block,re.M).group(1)
        for i,text in enumerate(p for p in re.split(r'(?<=[。！？])',line) if p):out.append({'id':f'{heading[1]}-{heading[2]}-{i+1}','text':text,'textSHA256':hashlib.sha256(text.encode()).hexdigest()})
    return out
def main():
    expected={'script.md':'d967f35deb07e6e3d1b19fddabfc3a3be970649f0a2a438336a2c4e31e9a0420','plan.json':'cd3f7cb8c112113cdd7a666cbb462eab8390b03c9eb091a65c56d493f0c86637','height-options.json':'ca0abf5dcef32e4cb96cd5912530a6b922a66894461a21d1a6b5be47b0700e50','model.json':'7f614b6796e74e8a58c786bcb09cd26ffec9e5cb134611c550a565fbe763167b'}
    for p,h in expected.items():assert sha(D/p)==h,(p,'approval candidate changed')
    modelqa=load(D/'qa-height-options-independent.json')
    assert modelqa['status']=='passed' and modelqa['formalHeightOptionsSHA256']==expected['height-options.json']
    assert modelqa['checkerSHA256']==sha(D/'qa-height-options-independent.py')
    source=D/'research/sources/t_zset.c';text=source.read_text();assert sha(source)=='216e757ebd39efcf1d53ff6c576d8a850c6382104be39d4195f1050543e48e0b'
    needles=['int level = 1;','level = zslRandomLevel();','x = zslCreateNode(zsl,level,score,ele);','for (i = 0; i < level; i++) {','x->level[i].forward = update[i]->level[i].forward;','update[i]->level[i].forward = x;','for (i = level; i < zsl->level; i++) {','update[i]->level[i].span++;','x->backward = (update[0] == zsl->header) ? NULL : update[0];','zsl->length++;']
    evidence=[]
    for needle in needles:
        assert needle in text; evidence.append({'exactText':needle,'line':text[:text.index(needle)].count('\n')+1})
    start=text.index('zskiplistNode *zslInsert(')
    assert text.index('level = zslRandomLevel();',start)<text.index('x = zslCreateNode(zsl,level,score,ele);',start)<text.index('for (i = 0; i < level; i++) {',start)
    sourceqa={'status':'passed','checkedAtUTC':datetime.now(timezone.utc).isoformat(),'scope':'Read fixed official local Redis8.4 source bytes, identical to previously API-verified pinned official source; no fresh network fetch claimed.','sourceSHA256':sha(source),'officialURL':'https://github.com/redis/redis/blob/60ba86f3c8b4e1ec96451171753a0a38e5c45a0c/src/t_zset.c','freshFetchPerformed':False,'localPinnedBytesMatchPriorVerifiedOfficialSource':True,'lineEvidence':evidence,'facts':['Level1 is a valid result: the random-level function starts at1.','The chosen level is known before creating the node and before any new forward-pointer write.','Only levels i<level get the new-node successor and predecessor-splice writes, in bottom-to-top order.','A level1 node does not receive an upper forward link; existing upper forward links remain.','After these forward writes Redis still maintains untouched spans, backward pointers, length and possibly tail. The video is a forward-link illustration, not an exhaustive zslInsert trace.']}
    write(D/'qa-height-source-independent.json',sourceqa)
    old=sentences(D/'provenance/clear-parts/script.md');new=sentences(D/'script.md');assert len(old)==len(new)==20
    changed=[];reused=[]
    for a,b in zip(old,new):
        assert a['id']==b['id']
        (changed if a['text']!=b['text'] else reused).append(b)
    assert [r['id'] for r in changed]==['07-height-1','07-height-2','09-splice-upper-1'] and len(reused)==17
    plan=load(D/'plan.json');assert next(p for p in plan if p['id']=='07')['cues']==[{'term':'层高','sentence':0}]
    s=D.joinpath('script.md').read_text();assert '全跳表仍有两层；仅新55的层高不同。' in s
    assert '不能把已接好的1层55临时升级为2层' in s and '共同before' in s
    assert changed[0]['text'].startswith('层高，') and '只有一层，接好底层就结束' in changed[0]['text']
    assert '接入前，Redis会随机确定层高' in changed[1]['text'] and '本例预先选两层' in changed[1]['text'] and '回到未插入的状态' in changed[1]['text']
    assert changed[2]['text'].startswith('本例选了两层，所以还要接上层')
    assert '不是Redis随机抽样或插完后升层' in s
    review=[
      {'shots':['07'],'claim':'层高是新节点自身的链接层数；height1不是整张跳表只剩一层','basis':'Formal height1 node has one base port; shared head and original40/70 retain height2 and upper chain.','verdict':'accurate'},
      {'shots':['07'],'claim':'55若height1，接好底层便完成本图的forward接线；上层仍40→70且没有55端口','basis':'Formal height1 allocation/two writes/after audited against independent construction and actual forward traversals. zslInsert writes only i<level.','verdict':'accurate within explicit forward-link scope'},
      {'shots':['07'],'claim':'Redis在接线前随机确定层高；本例预先选2，明确回共同before再看两层接法','basis':'Pinned source chooses level, creates node(level), then writes. Script visual direction explicitly resets the legal alternative to the common uninserted state; fixed selection is not RNG replay.','verdict':'accurate; prevents a false late-upgrade story'},
      {'shots':['08','09'],'claim':'只有主线预选2，底层写完之后才需要继续两次上层forward写','basis':'Formal height2 already has two slots at allocation; four snapshots match the old main model exactly.09 condition explicitly names the choice.','verdict':'accurate'},
      {'shots':['07','09'],'claim':'结束/完成限定本片的前向接线示意','basis':'height-options.forwardLinksOnly and hiddenRedisSpanUpdatesAreNotClaimedUnchanged are true. No narration or script says span/backward/length stay unchanged; actual remaining metadata maintenance is recorded in sourceQA.','verdict':'accurate scope; no exhaustive-Redis-function claim'}
    ]
    report={'status':'approved-for-tts','readyForTTSFromThisReview':True,'approvedForTTS':True,'checkedAtUTC':datetime.now(timezone.utc).isoformat(),'scriptSHA256':sha(D/'script.md'),'inputs':{p:sha(D/p) for p in ['script.md','plan.json','height-options.json','model.json','pronunciation.md','references.json']},'modelQA':{'path':'qa-height-options-independent.json','sha256':sha(D/'qa-height-options-independent.json'),'assertionsExecuted':modelqa['assertionsExecuted'],'actualFormalSerializedStatesAudited':modelqa['actualFormalSerializedStatesAudited'],'actualGraphNeighborQueries':modelqa['actualGraphNeighborQueries']},'sourceQA':{'path':'qa-height-source-independent.json','sha256':sha(D/'qa-height-source-independent.json'),'freshOfficialFiles':0,'mode':'exact pinned local official bytes verified; no new fetch claim'},'shots':10,'sentences':20,'approvedFreshSentenceIds':[r['id'] for r in changed],'approvedFreshSentences':changed,'verifiedUnchangedReuseSentenceIds':[r['id'] for r in reused],'verifiedUnchangedReuseCount':17,'baselineScriptSHA256':sha(D/'provenance/clear-parts/script.md'),'technicalReview':review,'blockingIssues':[],'nonBlockingNotes':['The two legal choices share an unmodified before; height1 completion must never be animated as the starting point of a late height2 upgrade.','Formal07 direction requires a readable reset to original8 nodes before showing the preselected height2 allocated node.','Actual fresh3 TTS quality, cue alignment, new storyboard windows and actual DOM/media require later checks.'],'limits':['This approves technical content for exactly the bound full script and the listed three fresh sentences; no TTS call has been made by this reviewer.','The remaining17 texts are verified identical, but their actual physical audio reuse must still be proven by the pipeline.','No animation, final encoded film, publication or human full-listening conclusion.'],'checkerSHA256':sha(__file__)}
    for p,h in expected.items():assert sha(D/p)==h,'candidate mutated during review'
    write(D/'qa-technical-independent.json',report)
    (D/'qa-technical-independent.md').write_text('技术脚本审批通过，可对绑定的3句进行新TTS；其余17句文本已核对保持。当前完整script SHA为'+report['scriptSHA256']+'。\n\n实际正式height-options经1,952断言、11个序列化快照和333个实际图邻接查询独立通过。height1仅55自身一层，整个跳表仍两层；它只需要底层两次forward写即可完成本图接线。主线height2在分配前选定，底层完成后仍需上层两写，不能解释为临时升层。07明确展示合法height1完成对照后回共同before，再预选2；09明确以预选2为继续接上层的条件。\n\n固定Redis源码先随机层高、按level创建、仅i<level逐层接forward；未触碰上层span和backward/length等维护仍存在。片中结束/完成是forward示意语境，没有宣称真实Redis函数省去这些更新。实际新配音、句窗、DOM转场和最终成片尚待后续QA。\n')
    print(json.dumps({'status':report['status'],'scriptSHA256':report['scriptSHA256'],'freshSentences':report['approvedFreshSentenceIds'],'reuseCount':17,'modelAssertions':modelqa['assertionsExecuted'],'reportSHA256':sha(D/'qa-technical-independent.json')}))
if __name__=='__main__':main()
