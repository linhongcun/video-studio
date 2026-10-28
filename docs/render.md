# 渲染与封面

制作工程在 `episodes-codex/<slug>/`，站点发布副本在 `episodes/<slug>/`。按当期 README、`remotion/package.json` 和 `source-sha256.json` 执行；参考实现为 [EP.14 当前工程](../episodes-codex/degradation/README.md)。旧期制作工程已清理，不从站点目录重新渲染。

## 新片默认入口

新片从调研阶段准备 `presentation: title-author` 的 `references.json`，并按[新期模板](../episodes-codex/_template/README.md)接入默认附录流程。原题及其证据必需；有明确公开署名时用非空 `author`，否则省略该字段并显示 `organization`。视频只显原题与作者/机构，完整链接、年份/版本、日期、位置、摘录和内部 `supports` 留文章或研究。正式编码前先做来源预检；正文命令写为本期的 `render:body`，输出独立的 `remotion/out/body.mp4`，其中保留已设计的完整代码卡（如有）。默认入口随后调用 `append_references_bibliography.py` 生成最终 `video.mp4`，不允许只交付 `render:body` 产物。

```sh
node site/scripts/check-references.mjs --sources EPDIR
python3 episodes-codex/_shared/render_with_references.py EPDIR
```

入口先检查资料，再只读核对本期 `source-sha256.json`，随后执行 `npm run render:body` 和新追加器；具体参数与文件约定以[共享入口](../episodes-codex/_shared/README.md)为准。资料清单、文章、原题/署名与实际研究证据、默认入口、新追加器及其保留的旧引擎依赖、实际调用的 `site/scripts/check-references.mjs` 和所用配置随本期实际输入冻结；旧引擎字节不改，产出的receipt和MP4不作为编码前输入冻结。附录两份receipt复制到制作目录根，其中 `reference-appendix.json` 记录起点、分页、实际原题/署名列表及完整区间；`render-result.json` 记录输出SHA、最终帧数及 `publicationMetadata`。接入站点时复制清单和receipt，按该metadata片段填写 `meta.referenceAppendix`、`meta.finalVideoFrames`，不改写正文的旁白、分镜或 `words.json`。来源尚未核验时应在渲染前失败，避免先做完正文再补片尾。

已完成生成后可用 `python3 episodes-codex/_shared/render_with_references.py EPDIR --verify` 复核资料、冻结和最终媒体；此模式只写QA报告，不重新渲染正文或重写冻结清单。

新模式每页最多4项、默认5秒，采用原题与作者/机构的简洁列表；原题和署名各自检查排版，超限报COPYFIT，不截断或改写成概括。实际检查所有资料页和首/中/末帧、字幕结束及播放器暂停/手机全屏；不叠加摘录、定位、年份/版本、核验日期、链接或提示说明。正文、代码卡和参考资料分别计时，不额外延长旁白或覆盖代码卡。新回执的 `bibliography` 绑定实际 `title` 与 `credit`，`layout` 声明单列、最多4项与只渲染题名/署名，`quotesRendered` 为false；每页5秒由 `inputs.secondsPerPage` 记录。旧原题/摘录模式及旧QA按历史范围保留，不改旧回执追认新列表。

## 现行旧期正文入口参考

以下命令使用当前 EP.14 的实际入口。运行前先完成 [校验](validate.md) 与冻结核对；换期应先读该期 README。

```sh
cd episodes-codex/degradation/remotion
npm ci
npx tsc --noEmit
npm run render
```

当前 EP.14 的 `render` 先执行 `render:voice` 生成 `out/voice.mp4`，再执行 `render:mix`，通过共享混音脚本生成上层 `video.mp4`。编码器、CRF、并发、浏览器位置以各期 package.json 为准，不把单期参数当成全系列命令。

共享混音从该制作目录调用 `../../../episodes/_shared/music/mix_bgm.py`，输入 `out/voice.mp4`、背景音乐 `../../../episodes/_shared/music/Wallpaper.mp3`，以 `--mode constant --below 12` 输出上层 `video.mp4`，报告写入 `out/mix-report.json`。默认响度目标 −16 LUFS、真峰值 −2.0 dBTP；实际值读混音报告，不以配置目标代替成片测量。

人声文件是 `remotion/public/audio/voice.wav`。渲染配置可能在它缺失时仍生成无声画面，渲染前必须确认音轨存在且与冻结输入相同。Remotion bundle 会复制 public 目录，音轨必须是实体文件，不能用相对软链代替。在 remotion 目录检查：

```sh
test -f public/audio/voice.wav && test ! -L public/audio/voice.wav && echo ok
```

仓根可用 `python3 episodes/_shared/place_v2.py --dir EPDIR --mode whole` 校验并按字节复制音轨；`EPDIR` 指制作目录。不要对已冻结工程重跑会写文件的步骤来代替只读检查。

输出位置：

- `episodes-codex/<slug>/remotion/out/voice.mp4`：混音前视频。
- `episodes-codex/<slug>/video.mp4`：待检查的成片。
- `episodes-codex/<slug>/remotion/out/mix-report.json`：响度及真峰值测量。

最终帧数按该期分镜、`meta.finalVideoFrames`、实际片尾实现和编码检查确定。某些工程在正片后保留尾帧，算法片可能有无旁白代码附录；不能统一追加或扣除 60 帧。发布前再把检查通过的产物复制到站点目录，见 [publish.md](publish.md)。

## 静帧与动态复核

当前 EP.14 支持：

```sh
cd episodes-codex/degradation/remotion
npm run stills -- /tmp/degradation-stills
```

该入口输出首帧和各镜中段采样，不是完整的溢出或动态审片。静帧、运动小样、导航检查的入口与参数以各期 scripts 和 README 为准；没有对应脚本时不要从旧期复制命令。对状态切换、变焦中间态、返回总览和跨情景衔接要看连续片段。

## 演示页页身色

页身使用 `episodes/_shared/theme/pageTheme.ts` 的 `PAGE`：`bg` 为 `#0F172A`、`ink` 为 `#E5E7EB`。各期 `remotion/src/theme.ts` 从共享模块引入，不能另抄一套色值：

```ts
export {PAGE, pageBg, pageInk} from '../../../../episodes/_shared/theme/pageTheme';
```

组件从本期 theme 引用，页身用 `PAGE.bg` / `PAGE.ink`，输入框、卡片、行底用 `PAGE.field` / `PAGE.row` / `PAGE.border`。浏览器框和 DevTools 按该期主题绘制。禁止大面积纯白页身，检查方法见 [validate.md](validate.md) 的「页身色」。修改共享主题会影响冻结输入，应按实际受影响范围重新检查、冻结和渲染。

## 封面

LeetCode 系列当前封面使用[独立系列模板](../episodes-codex/_shared/leetcode-covers/README.md)，以当前发布元数据核对题号、题名与方法，统一生成三比例，并检查实际字体边界、长标题间距与4:3安全区。各期 `cover-style.json` 记录当前模板及图片SHA；原Remotion封面源与旧冻结清单保持历史身份，不再用旧 `npm run covers` 覆盖现行系列封面。新题沿同一模板扩展目录与题图。

趣味推理系列使用[独立系列模板](../episodes-codex/_shared/puzzles-covers/README.md)，固定紫黑底、P编号与上题下图构图，按发布元数据核对单集身份。三比例检查、安装和SHA记录独立于旧视频工程；新增题沿同一入口扩展。

MySQL系列使用[独立系列模板](../episodes-codex/_shared/mysql-covers/README.md)，沿墨绿/薄荷绿、圆柱与真实EP编号，封面明确MySQL及InnoDB/异步复制边界；旧database-covers保留历史身份。当前正文入口见[MySQL制作说明](../episodes-codex/_shared/mysql-video/README.md)，与新封面读取同一catalog配色。新增单集沿当前入口扩展。

设计模式系列使用[独立系列模板](../episodes-codex/_shared/design-pattern-covers/README.md)，固定暖砂底、靛蓝标题、蓝橙模块标识及D编号。按实际元数据核对EP、D编号/顺序与完整原题，机制图保持策略择一、观察者当前订阅关系及适配器转换委托的职责边界。新增模式沿同一入口扩展。

Kafka消息队列系列使用[独立封面模板](../episodes-codex/_shared/kafka-covers/README.md)，以暖炭灰、橙、冰蓝、Kafka标识和稳定MQ编号区分单集。正文与封面共用不可变style-v1；当前制作修订按meta.sourcePath定位。参考资料通过[Kafka配色入口](../episodes-codex/_shared/kafka-video/README.md)接入原题/机构卡，不改写旧引擎或旧冻结。

Redis系列使用[独立模板](../episodes-codex/_shared/redis-covers/README.md)，固定冷银灰底、Redis红、石墨文字、原始Redis标记与真实EP编号。按当前meta.sourcePath定位实际修订安装，封面独立记录输入/产物SHA；旧工程算法编号、covers.json与编码冻结保持历史身份。当前跳表图按前向链接示例表达查55时在40下降、停于50/60之间，不将示意图当作小集合默认内存布局。新增题扩展同一catalog与机制图，不另起一套风格。

Redis正文沿[独立视觉入口](../episodes-codex/_shared/redis-video/README.md)读取不可变配色快照，当前实际入口为层高修订中的`remotion/src/redis-style/index.ts`，媒体与新冻结独立放`revisions/redis-style/`。保留原分镜、两种层高、完整AAC及旧封面输入，资料页同色；不要用历史`src/index.ts`或原混音命令覆盖新产物。

其他系列封面由当期 `remotion/src/Cover.tsx` 和 `covers.json` 定义。当前 EP.14 的实际入口是：

```sh
cd episodes-codex/degradation/remotion
npm run covers
```

该脚本生成上层目录的 `cover-16x9.png/jpg`、`cover-4x3.png/jpg`、`cover-3x4.png/jpg`，并将 3:4 JPG 复制为 `poster.jpg`。其他期以自己的脚本为准。

逐份打开实际产物，检查文字、裁切、水印和 4:3 安全区：内容 x 315..1125、底边 y < 918，且无 `COPYFIT`。水印按该尺寸的 watermarkZone，不能为了塞入内容安全区挪动水印。`meta.poster` 决定站点海报文件，`covers.json` 的 poster 约定也要一起核对。

## 共享工具回归

历史 EP.14 的 20 镜、5152 帧样例只保存在 [固定回归输入](../episodes/_shared/tests/fixtures/degradation-v0.45.0/README.md)，用于共享工具测试，不是现行渲染工程。相关命令见 [validate.md](validate.md) 的「共享工具回归」。

## 趣味推理正文的当前视觉入口

P01–P05按封面的紫黑、浅紫、珊瑚配色使用[独立正文入口](../episodes-codex/_shared/puzzles-video/README.md)。当前画面在各期`remotion/src/cover-continuity/`，输出与独立清单位于`revisions/cover-continuity/`；原src、旧音轨/时序与冻结保留历史身份。当前成片不得通过旧`npm run render`覆盖；使用共享`render.py <slug> --freeze / --render / --verify`，命令、基线声音恢复及实际范围见对应说明。新资料卡通过独立紫色adapter复用既有原题/署名排版，不改旧引擎。

## LeetCode正文的当前视觉入口

现有11题正文沿封面使用[独立视觉入口](../episodes-codex/_shared/leetcode-video/README.md)，新源位于各期`src/leetcode-style/`，当前独立输入/产物位于`revisions/leetcode-style/`。保留原模型、分镜、声音和旧冻结；整片包含原150帧完整Python卡后再追加150帧参考资料。通过共享入口先逐镜/代码预检再freeze/render/verify，不用旧`npm run render`覆盖当前新版；新增题保持不可变样式，身份另传，不修改已编码快照。
