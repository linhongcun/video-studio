"""Read fixed public source blobs through the approved GitHub API; no secret access."""
from pathlib import Path
import base64, datetime, hashlib, html, json, re, subprocess
EP=Path(__file__).resolve().parents[1]
TODAY=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).date().isoformat()
def fetch(repo,path,ref):
    response=subprocess.check_output(['gh','api',f'repos/{repo}/contents/{path}','--method','GET','-f',f'ref={ref}'])
    data=json.loads(response);assert data['encoding']=='base64'
    raw=base64.b64decode(data['content']);assert len(raw)==data['size']
    return data,raw
sources=[]
repo='doocs/leetcode';path='solution/0500-0599/0547.Number of Provinces/README_EN.md';ref='42ac9040510ef8711ed8c66a4c9be2e6ffa08f73'
meta,raw=fetch(repo,path,ref);text=raw.decode();lines=text.splitlines()
quote='A province is a group of directly or indirectly connected cities and no other cities outside of the group.'
rendered=html.unescape(re.sub('<[^>]+>','',text));assert quote in rendered
assert '1 &lt;= n &lt;= 200' in text and 'isConnected[i][i] == 1' in text and 'isConnected[i][j] == isConnected[j][i]' in text
assert '# [547. Number of Provinces]' in text
sources.append(dict(id='R1',title='547. Number of Provinces',organization='Doocs',sourceKind='Public problem-statement mirror;not the original official page',repository=repo,path=path,commit=ref,blobSHA1=meta['sha'],fileSHA256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),sourceUrl=meta['html_url'],originalOfficialUrl='https://leetcode.com/problems/number-of-provinces/description/',officialPageDirectlyRead=False,titleEvidence=dict(line=next(i for i,l in enumerate(lines,1) if '# [547. Number of Provinces]' in l),text=next(l for l in lines if '# [547. Number of Provinces]' in l)),creditEvidence='The actually read document is published in the public Doocs repository;Doocs is credited as mirror publisher,not inferred as a person or official LeetCode author.',quotation=dict(text=quote,locator='Description:definition of province',rawParagraph=next(l for l in lines if '<strong>province</strong>' in l)),facts=['n cities;direct and indirect connection form one province','n×n 0/1 symmetric relation matrix;diagonal1','1≤n≤200','return total number of provinces','mirrored problem examples return2 and3'],readScope='Only Description/Examples/Constraints used. Mirror solutions are not cited or copied. Original official domain is absent from current allowlist;no bypass or claim of direct official retrieval.'))
repo='kevin-wayne/algs4';path='src/main/java/edu/princeton/cs/algs4/UF.java';ref='6157ca02644bdc24892ffbac1cf449d5169e71de'
meta,raw=fetch(repo,path,ref);text=raw.decode();lines=text.splitlines()
assert '@author Robert Sedgewick' in text and '@author Kevin Wayne' in text
assert 'path compression by halving' in text and 'rank' in text
quote='The union–find data type models a collection of sets containing n elements, with each element in exactly one set.'
# Render Javadoc prose as visible text; preserve every word and punctuation.
prose=re.sub(r'^\s*\* ?', '',text,flags=re.M)
prose=re.sub(r'\{@code ([^}]+)\}',r'\1',prose)
prose=html.unescape(re.sub('<[^>]+>','',prose));prose=re.sub(r'\s+',' ',prose)
assert quote in prose
sources.append(dict(id='R2',title='UF.java',organization='Princeton University',author='Robert Sedgewick, Kevin Wayne',sourceKind='Official algs4 implementation and Javadoc',repository=repo,path=path,commit=ref,blobSHA1=meta['sha'],fileSHA256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),sourceUrl=meta['html_url'],originalOfficialUrl='https://algs4.cs.princeton.edu/code/edu/princeton/cs/algs4/UF.java.html',titleEvidence=dict(locator='File name and Compilation:javac UF.java header',text=lines[1] if len(lines)>1 else lines[0]),creditEvidence=[l.strip(' *') for l in lines if '@author ' in l],quotation=dict(text=quote,locator='UF class Javadoc:collection of disjoint sets',normalization='Javadoc delimiters,HTML and inline code formatting removed;visible words and punctuation unchanged.'),facts=['Each element belongs to exactly one set;initially n singleton sets','find returns same canonical root iff two elements are in same set','union merges distinct sets;count returns number of sets','Official code uses weighted quick union by rank and path halving','Amortized O(m α(n)) sequence bound stated for weighted rank+halving implementation'],readScope='Class documentation,find,union,count and explicit author tags. The episode uses union by size;the matching size/complexity statement is checked separately inR3,not falsely attributed to this rank implementation.'))
repo='cp-algorithms/cp-algorithms';path='src/data_structures/disjoint_set_union.md';ref='f06f7d5e5630f0b811e37d9e657562ba38c41f6a'
meta,raw=fetch(repo,path,ref);text=raw.decode();lines=text.splitlines()
assert '# Disjoint Set Union' in text and 'Union by size / rank' in text
quote='Both optimizations are equivalent in terms of time and space complexity. So in practice you can use any of them.'
assert quote in text
quote2='As mentioned before, if we combine both optimizations - path compression with union by size / rank - we will reach nearly constant time queries.'
assert quote2 in text
sources.append(dict(id='R3',title='Disjoint Set Union',organization='CP-Algorithms',sourceKind='Maintained original algorithm explanation',repository=repo,path=path,commit=ref,blobSHA1=meta['sha'],fileSHA256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),sourceUrl=meta['html_url'],originalOfficialUrl='https://cp-algorithms.com/data_structures/disjoint_set_union.html',titleEvidence=dict(line=next(i for i,l in enumerate(lines,1) if l.startswith('# Disjoint Set Union')),text=next(l for l in lines if l.startswith('# Disjoint Set Union'))),creditEvidence='CP-Algorithms published source;no explicit individual article byline is inferred from Git maintenance/commit identities.',quotation=dict(text=quote2,locator='Time complexity section',sizeRankEquivalenceQuote=quote),facts=['Attach lower-size root under larger-size root','Union by size and rank have equivalent asymptotic time/space complexity','Combine balancing and path compression for amortized inverse-Ackermann queries','Do not confuse parent implementation links with input graph edges'],readScope='Path compression,union by size/rank and time complexity. No individual author invented.'))
record=dict(schemaVersion=1,episode='number-of-provinces',checkedAt=TODAY,timezone='Asia/Shanghai',accessMethod='Actual GitHub Contents API reads of pinned public source blobs;source bytes decoded and assertions executed. API200 status not independently logged;successful CLI/API responses and blob identities recorded.',networkBoundary='Original LeetCode domains not directly requested;no allowlist bypass. Original official URLs retained as origin pointers rather than successful-visit claims.',sources=sources)
(EP/'research/source-access.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
refs=[]
for s in sources:
    item=dict(id=s['id'],organization=s['organization'],title=s['title'],version='Fixed public source commit '+s['commit'],url=s['sourceUrl'],supports=s['facts'],sections=s['quotation']['locator'],verification=dict(status='verified',checkedAt=TODAY,method=s['readScope'],sourceUrl=s['sourceUrl'],evidence='episodes-codex/number-of-provinces/research/source-access.json',sourceKind=s['sourceKind']),titleEvidence=dict(locator=s['titleEvidence'].get('locator',f"Markdown heading line{s['titleEvidence'].get('line')}"),evidence='episodes-codex/number-of-provinces/research/source-access.json'),quotation=dict(text=s['quotation']['text'],locator=s['quotation']['locator'],evidence='episodes-codex/number-of-provinces/research/source-access.json'))
    if 'author' in s:item['author']=s['author']
    item['alternateOfficialUrl']=s['originalOfficialUrl']
    refs.append(item)
(EP/'references.json').write_text(json.dumps(dict(schemaVersion=1,episode='number-of-provinces',heading='参考资料',presentation='title-author',checkedAt=TODAY,timezone='Asia/Shanghai',sources=refs,scope='Public mirror for problem statement transparently distinguished from direct original-page access;Princeton official source and maintained CP-Algorithms support DSU implementation. One5-second title/credit page,3items.'),ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'read-and-recorded','sources':[(s['id'],s['title'],s['fileSHA256']) for s in sources]},ensure_ascii=False))
