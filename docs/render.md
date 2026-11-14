# 渲染与封面

制作工程在 `episodes/<series>/<slug>/production/`，站点发布副本在 `episodes/<series>/<slug>/publication/`。先按发布 `meta.json.sourcePath` 找到工程，读取当期 README 顶部的当前修订与系列共享入口，再选择实际命令及冻结清单；`remotion/package.json` 可能保留旧正文入口，不能据此覆盖当前视觉修订。参考 [EP.14 工程说明](../episodes/peak/degradation/production/README.md)的当前入口。旧期制作工程已清理，不从站点目录重新渲染。

目录迁移后的源码包含路径适配，旧 `source-sha256.json` 继续证明迁移前的制作输入，不能直接作为新路径代码的编码许可。重新渲染前，在新修订中按本期冻结器记录当前实际输入；原清单与回执保留历史身份，原路径与前后SHA按[迁移记录](archive/2026-11/episode-layout/README.md)追溯。本次目录检查不代表已重新编码或审片。

## 新片默认入口

新片从调研阶段准备 `presentation: title-author` 的 `references.json`，并按[新期模板](../episodes/_template/README.md)接入默认附录流程。原题及其证据必需；有明确公开署名时用非空 `author`，否则省略该字段并显示 `organization`。视频只显原题与作者/机构，完整链接、年份/版本、日期、位置、摘录和内部 `supports` 留文章或研究。正式编码前先做来源预检；正文命令写为本期的 `render:body`，输出独立的 `remotion/out/body.mp4`，其中保留已设计的完整代码卡（如有）。默认入口随后调用 `append_references_bibliography.py` 生成最终 `video.mp4`，不允许只交付 `render:body` 产物。

```sh
node site/scripts/check-references.mjs --sources EPDIR
python3 episodes/_shared/render_with_references.py EPDIR
```

入口先检查资料，再只读核对本期 `source-sha256.json`，随后执行 `npm run render:body` 和新追加器；具体参数与文件约定以[共享入口](../episodes/_shared/README.md)为准。资料清单、文章、原题/署名与实际研究证据、默认入口、新追加器及其保留的旧引擎依赖、实际调用的 `site/scripts/check-references.mjs`、Python/JS路径解析器和所用配置随本期实际输入冻结；旧引擎字节不改，产出的receipt和MP4不作为编码前输入冻结。附录两份receipt复制到制作目录根，其中 `reference-appendix.json` 记录起点、分页、实际原题/署名列表及完整区间；`render-result.json` 记录输出SHA、最终帧数及 `publicationMetadata`。接入站点时复制清单和receipt，按该metadata片段填写 `meta.referenceAppendix`、`meta.finalVideoFrames`，不改写正文的旁白、分镜或 `words.json`。来源尚未核验时应在渲染前失败，避免先做完正文再补片尾。

已完成生成后可用 `python3 episodes/_shared/render_with_references.py EPDIR --verify` 复核资料、冻结和最终媒体；此模式只写QA报告，不重新渲染正文或重写冻结清单。

新模式每页最多4项、默认5秒，采用原题与作者/机构的简洁列表；原题和署名各自检查排版，超限报COPYFIT，不截断或改写成概括。实际检查所有资料页和首/中/末帧、字幕结束及播放器暂停/手机全屏；不叠加摘录、定位、年份/版本、核验日期、链接或提示说明。正文、代码卡和参考资料分别计时，不额外延长旁白或覆盖代码卡。新回执的 `bibliography` 绑定实际 `title` 与 `credit`，`layout` 声明单列、最多4项与只渲染题名/署名，`quotesRendered` 为false；每页5秒由 `inputs.secondsPerPage` 记录。旧原题/摘录模式及旧QA按历史范围保留，不改旧回执追认新列表。

## 既有工程的入口与输出

EP.11–14 当前正文和资料页通过 [peak-video](../episodes/_shared/peak-video/README.md) 生成，实际入口为 `remotion/src/peak-style/index.ts`，媒体和新冻结在 `revisions/peak-style/`；不能通过旧 `npm run render` 覆盖当前发布稿。其他系列的当前入口见下方对应说明及本期 README。

制作根保留的 EP.14 `remotion/package.json` 中，`render` 已调用共享 `render_with_references.py`，并非只有正文：`render:body` 执行 `render:voice` 与 `render:mix`，先生成 `out/voice.mp4`，再混音到 `out/body.mp4`，最后由 wrapper 追加参考资料得到上层 `video.mp4`。这些命令描述原正文与附录流程，不代替当前 `peak-style` 入口。编码器、CRF、并发与浏览器位置以实际执行的入口为准，不把单期参数当成全系列命令。

需要运行本期 Remotion 工程时，先在其实际 `remotion/` 目录按锁文件执行 `npm ci` 和 `npx tsc --noEmit`。旧 EP.14 package 从该目录调用共享混音脚本的相对路径为 `../../../../_shared/music/mix_bgm.py`，背景音乐为 `../../../../_shared/music/Wallpaper.mp3`，参数为 `--mode constant --below 12`，报告为 `out/mix-report.json`。默认响度目标 −16 LUFS、真峰值 −2.0 dBTP；实际值读混音报告，不以配置目标代替成片测量。只替换视觉并保留原AAC的系列修订不重复混音。

人声文件是 `remotion/public/audio/voice.wav`。渲染配置可能在它缺失时仍生成无声画面，渲染前必须确认音轨存在且与冻结输入相同。Remotion bundle 会复制 public 目录，音轨必须是实体文件，不能用相对软链代替。在 remotion 目录检查：

```sh
test -f public/audio/voice.wav && test ! -L public/audio/voice.wav && echo ok
```

仓根可用 `python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole` 校验并按字节复制音轨；`EPDIR` 指制作目录。不要对已冻结工程重跑会写文件的步骤来代替只读检查。

通用新片入口的输出位置（系列派生输出按对应 README）：

- `episodes/<series>/<slug>/production/remotion/out/voice.mp4`：混音前视频。
- `episodes/<series>/<slug>/production/remotion/out/body.mp4`：混音后的正文及已有代码卡。
- `episodes/<series>/<slug>/production/video.mp4`：追加参考资料后的待检查成片。
- `episodes/<series>/<slug>/production/remotion/out/mix-report.json`：响度及真峰值测量。

最终帧数按该期分镜、`meta.finalVideoFrames`、实际片尾实现和编码检查确定。某些工程在正片后保留尾帧，算法片可能有无旁白代码附录；不能统一追加或扣除 60 帧。发布前再把检查通过的产物复制到站点目录，见 [publish.md](publish.md)。

## 静帧与动态复核

EP.14 保留的原正文脚本支持：

```sh
cd episodes/peak/degradation/production/remotion
npm run stills -- /tmp/degradation-stills
```

该入口输出原正文首帧和各镜中段采样，不覆盖当前 `peak-style` 修订；当前系列视觉预检使用对应 README 的 `qa.mjs`。这两类采样都不是完整的动态审片。静帧、运动小样、导航检查的入口与参数以各期 scripts 和 README 为准；没有对应脚本时不要从旧期复制命令。对状态切换、变焦中间态、返回总览和跨情景衔接要看连续片段。

对于实际limitedBT709成片，文章JPEG截图还须明确转换为fullBT601的JPEG像素，例如在精确选帧后加入`scale=in_range=tv:out_range=pc:in_color_matrix=bt709:out_color_matrix=bt601,format=yuvj420p`。按实际输入颜色选择参数；不要仅贴标签。将JPEG在通用解码器中的实际色块与同帧PNG/播放器比较，避免视频颜色正确而配图偏色，见L059。

## 演示页页身色

页身使用 `episodes/_shared/theme/pageTheme.ts` 的 `PAGE`：`bg` 为 `#0F172A`、`ink` 为 `#E5E7EB`。各期 `remotion/src/theme.ts` 从共享模块引入，不能另抄一套色值：

```ts
export {PAGE, pageBg, pageInk} from '../../../../../_shared/theme/pageTheme';
```

组件从本期 theme 引用，页身用 `PAGE.bg` / `PAGE.ink`，输入框、卡片、行底用 `PAGE.field` / `PAGE.row` / `PAGE.border`。浏览器框和 DevTools 按该期主题绘制。禁止大面积纯白页身，检查方法见 [validate.md](validate.md) 的「页身色」。修改共享主题会影响冻结输入，应按实际受影响范围重新检查、冻结和渲染。

## 封面

LeetCode 系列当前封面使用[独立系列模板](../episodes/_shared/leetcode-covers/README.md)，以当前发布元数据核对题号、题名与方法，统一生成三比例，并检查实际字体边界、长标题间距与4:3安全区。各期 `cover-style.json` 记录当前模板及图片SHA；原Remotion封面源与旧冻结清单保持历史身份，不再用旧 `npm run covers` 覆盖现行系列封面。新题沿同一模板扩展目录与题图。

趣味推理系列使用[独立系列模板](../episodes/_shared/puzzles-covers/README.md)，固定紫黑底、P编号与上题下图构图，按发布元数据核对单集身份。三比例检查、安装和SHA记录独立于旧视频工程；新增题沿同一入口扩展。

MySQL系列使用[独立系列模板](../episodes/_shared/mysql-covers/README.md)，沿墨绿/薄荷绿、圆柱与真实EP编号，封面明确MySQL及InnoDB/异步复制边界；旧database-covers保留历史身份。当前正文入口见[MySQL制作说明](../episodes/_shared/mysql-video/README.md)，与新封面读取同一catalog配色。新增单集沿当前入口扩展。

设计模式系列使用[独立系列模板](../episodes/_shared/design-pattern-covers/README.md)，固定暖砂底、靛蓝标题、蓝橙模块标识及D编号。按实际元数据核对EP、D编号/顺序与完整原题，机制图保持策略择一、观察者当前订阅关系及适配器转换委托的职责边界。新增模式沿同一入口扩展。

Kafka消息队列系列使用[独立封面模板](../episodes/_shared/kafka-covers/README.md)，以暖炭灰、橙、冰蓝、Kafka标识和稳定MQ编号区分单集。正文与封面共用不可变style-v1；当前制作修订按meta.sourcePath定位。参考资料通过[Kafka配色入口](../episodes/_shared/kafka-video/README.md)接入原题/机构卡，不改写旧引擎或旧冻结。

Redis系列使用[当前独立模板](../episodes/_shared/redis-covers-v2/README.md)，固定冷银灰底、Redis红、石墨文字、原始Redis标记与真实EP编号。按当前meta.sourcePath定位实际修订安装，封面独立记录输入/产物SHA；旧工程算法编号、covers.json与编码冻结保持历史身份。当前跳表图按前向链接示例表达查55时在40下降、停于50/60之间，不将示意图当作小集合默认内存布局。当前模板复用v1固定样式，默认生成新归入的EP.08/09，将其安装至各自`revisions/redis-style/`与发布根；EP.40封面保持原字节。新增题扩展当前catalog与机制图，不改旧v1输入。

Redis正文沿[独立视觉入口](../episodes/_shared/redis-video/README.md)读取不可变配色快照，当前实际入口为层高修订中的`remotion/src/redis-style/index.ts`，媒体与新冻结独立放`revisions/redis-style/`。保留原分镜、两种层高、完整AAC及旧封面输入，资料页同色；不要用历史`src/index.ts`或原混音命令覆盖新产物。

当前跳表发布片另外通过[BT.709色彩派生](../episodes/_shared/redis-video-bt709/README-v2.md)生成：独立冻结原正文与原清单，将全范围BT.601画面转换为有限范围BT.709，明确逐帧颜色参数，再追加同编码资料页。原视觉产物保持，实际发布使用`revisions/redis-style-bt709-v2/video.mp4`；不能只修改颜色标签。核对原时序、完整AAC与实际网页取色，静帧颜色正确不代表浏览器解码颜色正确。

高并发、高可用、高性能系列使用[独立模板](../episodes/_shared/peak-covers/README.md)，固定深青蓝底、亮青线条、暖黄强调、真实EP与限流/幂等/熔断/降级机制图。按当前meta.sourcePath定位制作根，三比例图与输入SHA独立记录；旧Cover、covers.json和冻结清单保持。后续单集沿同一catalog扩展原题与准确示例，不另起样式。

没有独立系列封面模板的工程，按当期 `remotion/src/Cover.tsx` 和 `covers.json` 生成。EP.14 保留的原封面脚本示例是（当前高并发系列封面使用上面的共享模板，不运行此命令覆盖）：

```sh
cd episodes/peak/degradation/production/remotion
npm run covers
```

该脚本生成上层目录的 `cover-16x9.png/jpg`、`cover-4x3.png/jpg`、`cover-3x4.png/jpg`，并将 3:4 JPG 复制为 `poster.jpg`。其他期以自己的脚本为准。

逐份打开实际产物，检查文字、裁切、水印和 4:3 安全区：内容 x 315..1125、底边 y < 918，且无 `COPYFIT`。水印按该尺寸的 watermarkZone，不能为了塞入内容安全区挪动水印。`meta.poster` 决定站点海报文件，`covers.json` 的 poster 约定也要一起核对。

Redis应用场景EP.08/09使用[独立缓存视觉入口](../episodes/_shared/redis-cache-video/README.md)，新源码在各期`remotion/src/redis-style/`，清单和最终媒体在`revisions/redis-style/`。默认生产先渲染无声画面、真实转换为有限范围BT.709并明确逐帧参数，再完整流拷贝原AAC，追加同编码原题/机构资料页；不用事后改旧冻结。新封面与媒体独立安装，原模型、分镜、文章发布稿、素材身份与两类缓存流程保留。

## 高并发、高可用、高性能正文的当前视觉入口

EP.11–14正文与资料页通过[独立系列入口](../episodes/_shared/peak-video/README.md)延续现行深青蓝、亮青、暖黄封面。新源码在各期`remotion/src/peak-style/`，媒体和47/51/48/50项输入独立冻结在`revisions/peak-style/`；原模型、导航、配音、分镜、文章发布稿、封面和历史清单保持。先逐镜预检，再运行共享`render.py <slug> --freeze / --render / --verify`，不要用旧混音入口覆盖新版。默认流程完成真实limitedBT709像素转换、逐帧颜色参数、完整原AAC流拷贝和同色参考资料；实际网页颜色、字幕与全屏另查。

## 共享工具回归

历史 EP.14 的 20 镜、5152 帧样例只保存在 [固定回归输入](../episodes/_shared/tests/fixtures/degradation-v0.45.0/README.md)，用于共享工具测试，不是现行渲染工程。相关命令见 [validate.md](validate.md) 的「共享工具回归」。

## 趣味推理正文的当前视觉入口

P01–P05按封面的紫黑、浅紫、珊瑚配色使用[独立正文入口](../episodes/_shared/puzzles-video/README.md)。当前画面在各期`remotion/src/cover-continuity/`，输出与独立清单位于`revisions/cover-continuity/`；原src、旧音轨/时序与冻结保留历史身份。当前成片不得通过旧`npm run render`覆盖；使用共享`render.py <slug> --freeze / --render / --verify`，命令、基线声音恢复及实际范围见对应说明。新资料卡通过独立紫色adapter复用既有原题/署名排版，不改旧引擎。

## LeetCode正文的当前视觉入口

现有11题正文沿封面使用[独立视觉入口](../episodes/_shared/leetcode-video/README.md)，新源位于各期`src/leetcode-style/`，当前独立输入/产物位于`revisions/leetcode-style/`。保留原模型、分镜、声音和旧冻结；整片包含原150帧完整Python卡后再追加150帧参考资料。通过共享入口先逐镜/代码预检再freeze/render/verify，不用旧`npm run render`覆盖当前新版；新增题保持不可变样式，身份另传，不修改已编码快照。
