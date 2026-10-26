"""Check HTTP source-identity assertions using169cb0c's actual component shape.

This is synthetic server HTML, not a browser or a claim that the site is built.
"""
from pathlib import Path
import ast
import hashlib
import html
import importlib.util
import json
import re
import subprocess

A = Path(__file__).resolve().parent
D = A.parents[1]
spec = importlib.util.spec_from_file_location('popover_verify', D / 'verify_published.py')
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
sources = {source['id']: source for filename in ['references.json', 'article-sources.json']
           for source in json.loads((D / filename).read_text())['sources']}
article = (D / 'article.mdx').read_text()
supports = {key: re.search(r'<SourceQuote\s+sourceId="' + key + r'"\s+supports="([^"]+)"', article)[1]
            for key in ['R1', 'A1']}
e = html.escape


def source_html(key):
    source = sources[key]
    panel_id = f'source-redis-skiplist-{key}'
    fixed = source['verification'].get('sourceUrl', source['url'])
    return f'''<div class="source-quote" data-source-quote="{key}">
<span class="source-anchor"><button class="source-trigger" type="button"
popovertarget="{panel_id}" aria-controls="{panel_id}" aria-haspopup="dialog"
data-source-trigger="{key}" aria-label="查看原文与出处：{e(source['title'])}">
<svg aria-hidden="true"><path d="M6 4" /></svg><span>原文</span></button></span>
<aside class="source-panel" id="{panel_id}" popover="auto" role="dialog"
aria-labelledby="{panel_id}-heading" data-source-panel="{key}">
<header class="source-panel-header"><h4 id="{panel_id}-heading">原文与出处</h4>
<button class="source-close" type="button" popovertarget="{panel_id}"
popovertargetaction="hide" aria-label="关闭原文与出处"><svg><path d="m4 4" /></svg></button></header>
<figure class="source-content"><blockquote cite="{e(fixed, quote=True)}"><p>{e(source['quotation']['text'])}</p></blockquote>
<p class="source-support"><strong>编者说明</strong> {e(supports[key])}</p>
<figcaption><cite><a href="{e(source['url'], quote=True)}">{e(source['title'])}</a></cite>
<p class="source-identity">{e(source.get('author', source['organization']))} · {e(source['version'])}</p>
<p class="source-location">原文位置：{e(source['quotation']['locator'])}</p>
<p class="source-access">核验于 <time datetime="{source['verification']['checkedAt']}">{source['verification']['checkedAt']}</time></p>
</figcaption></figure></aside></div>'''


url = '/video-studio/episodes/redis-skiplist/article/height-one.jpg'
figure = f'''<figure data-figure-kind="video"><a href="{url}"><img src="{url}" alt="{verify.ARTICLE_ALT}"></a>
<figcaption>{verify.ARTICLE_CAPTION}<a href="{url}">查看大图</a>
<a href="?t=88.9#player" data-seek-time="88.9">回看</a></figcaption></figure>'''
page = '<div class="site"><div class="article">' + source_html('R1') + source_html('A1') + figure + '</div></div>'
verify.validate_article_page(page, sources)
cases = {
    'quotation-character': ('between 1 and ZSKIPLIST_MAXLEVEL', 'between 2 and ZSKIPLIST_MAXLEVEL'),
    'quotation-newline': ('create.\n * The', 'create. * The'),
    'trigger-target': ('popovertarget="source-redis-skiplist-R1"', 'popovertarget="source-redis-skiplist-A1"'),
    'trigger-controls': ('aria-controls="source-redis-skiplist-R1"', 'aria-controls="wrong"'),
    'trigger-haspopup': ('aria-haspopup="dialog"', 'aria-haspopup="menu"'),
    'panel-id': ('id="source-redis-skiplist-R1"', 'id="wrong"'),
    'panel-popover': ('popover="auto"', 'popover="manual"'),
    'panel-role': ('role="dialog"', 'role="region"'),
    'panel-label': ('aria-labelledby="source-redis-skiplist-R1-heading"', 'aria-labelledby="wrong"'),
    'close-control': ('popovertargetaction="hide"', 'popovertargetaction="toggle"'),
    'credit': ('Redis · Redis8.4.0', 'Wrong · Redis8.4.0'),
    'version': ('Redis8.4.0 · 60ba86f3', 'Redis8.5.0 · 60ba86f3'),
    'location': ('原文位置：zslRandomLevel preceding comment', '原文位置：another comment'),
    'date': ('datetime="2026-10-26"', 'datetime="2026-10-27"'),
    'supports': (e(supports['A1']), '错误的编者说明'),
    'caption': (verify.ARTICLE_CAPTION, '错误的图注'),
    'seek': ('data-seek-time="88.9"', 'data-seek-time="89.0"'),
}
rejected = []
for label, (old, new) in cases.items():
    assert old in page, ('Bad synthetic mutation', label)
    try:
        verify.validate_article_page(page.replace(old, new, 1), sources)
    except AssertionError:
        rejected.append(label)
    else:
        raise AssertionError('Tampered case accepted: ' + label)
for filename in ['sync_site.py', 'verify_published.py']:
    ast.parse((D / filename).read_text())
    subprocess.run(['python3', str(D / filename), '--help'], check=True, capture_output=True, text=True)
print(json.dumps({'status': 'passed-synthetic-native-popover-identity-checks',
                  'sourceIds': ['R1', 'A1'], 'positiveCase': 'exact current source data in169cb0c component server markup with nested page divs',
                  'rejectedTamperedCases': rejected, 'actualHTTPRequests': 0,
                  'actualBrowserChecks': False, 'oldQARewritten': False}, ensure_ascii=False))
