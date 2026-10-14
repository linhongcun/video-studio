// 把 ../assets/*.svg 打包成 src/assets.gen.ts（键 = 分镜里的 asset 路径，如 "assets/postcard.svg"），供 Main.tsx 内联渲染。
// 内联而不是 <Img>：这样 tamperStrip / drawCheck / badgeDanger / tint 等动画属性能按 SVG 里的 <g id> 做局部样式。
// 生成文件不进仓库；typecheck / still / render 前自动运行。
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here = path.dirname(fileURLToPath(import.meta.url));
const dir = path.join(here, '..', 'assets');
const files = fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => f.endsWith('.svg')).sort() : [];
const map = Object.fromEntries(files.map((f) => [`assets/${f}`, fs.readFileSync(path.join(dir, f), 'utf8')]));
fs.writeFileSync(path.join(here, 'src', 'assets.gen.ts'),
  `// 自动生成（sync_assets.mjs），勿手改\nconst ASSETS: Record<string, string> = ${JSON.stringify(map, null, 1)};\nexport default ASSETS;\n`);
console.log(`assets.gen.ts: ${files.length} svg${files.length ? '' : '（../assets 不存在，图片元素会显示占位框）'}`);
