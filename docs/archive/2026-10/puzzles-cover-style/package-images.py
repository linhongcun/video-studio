from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib
r=Path('/workspace/video-studio');d=r/'design/puzzles-covers-20261027';src=Path('/workspace/work/puzzles-cover-final-player-safe');cat=json.loads((r/'episodes-codex/_shared/puzzles-covers/catalog.json').read_text())
pack=d/'puzzles-covers-5-episodes.zip'
with ZipFile(pack,'w',ZIP_DEFLATED) as z:
 for e in cat['episodes']:
  for p in (src/e['slug']).glob('cover-*'):
   if p.suffix in ['.png','.jpg']:z.write(p,e['number']+'-'+e['slug']+'/'+p.name)
 z.write(src/'contact-sheet.jpg','preview.jpg')
 z.writestr('使用说明.txt','趣味推理5期统一封面\n横版1920×1080；4:3 1440×1080；竖版1080×1440。每题含PNG/JPG，可直接使用。\n4:3完整容纳竖版并保留中心裁切安全区。可复用模板及矢量生成源位于仓库episodes-codex/_shared/puzzles-covers。\n本次更新站点及素材，未修改外平台作品封面。\n')
with ZipFile(pack) as z:
 assert z.testzip() is None
 for e in cat['episodes']:
  for size in ['16x9','4x3','3x4']:
   for ext in ['png','jpg']:
    name=f'cover-{size}.{ext}';assert z.read(e['number']+'-'+e['slug']+'/'+name)==(src/e['slug']/name).read_bytes()
p=r/'docs/archive/2026-10/puzzles-cover-style/publication.json';v=json.loads(p.read_text());v['assetFiles']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in d.iterdir() if p.suffix in ['.png','.zip']};p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print('30 packaged images match final checked files; ZIP valid',pack.stat().st_size)
