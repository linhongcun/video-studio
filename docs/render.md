# 渲染与封面

制作工程在 `episodes-codex/<slug>/`，站点发布副本在 `episodes/<slug>/`。按当期 README、`remotion/package.json` 和 `source-sha256.json` 执行；参考实现为 [EP.14 当前工程](../episodes-codex/degradation/README.md)。旧期制作工程已清理，不从站点目录重新渲染。

## 新片默认入口

新片从调研阶段准备 `presentation: original-title-quote` 的 `references.json`，并按[新期模板](../episodes-codex/_template/README.md)接入默认附录流程。原始题名及其证据必需，实际原文短引按需要选择，内部 `supports` 不上屏。正式编码前先做来源预检；正文命令写为本期的 `render:body`，输出独立的 `remotion/out/body.mp4`，其中保留已设计的完整代码卡（如有）。默认入口随后调用 `append_references_original.py` 生成最终 `video.mp4`，不允许只交付 `render:body` 产物。

```sh
node site/scripts/check-references.mjs --sources EPDIR
python3 episodes-codex/_shared/render_with_references.py EPDIR
```

入口先检查资料，再只读核对本期 `source-sha256.json`，随后执行 `npm run render:body` 和新追加器；具体参数与文件约定以[共享入口](../episodes-codex/_shared/README.md)为准。资料清单、文章、题名/短引证据、默认入口、新追加器及其保留的旧引擎依赖、实际调用的 `site/scripts/check-references.mjs` 和所用配置随本期实际输入冻结；旧引擎字节不改，产出的receipt和MP4不作为编码前输入冻结。附录两份receipt复制到制作目录根，其中 `reference-appendix.json` 记录起点、分页、原题/短引及完整区间；`render-result.json` 记录输出SHA、最终帧数及 `publicationMetadata`。接入站点时复制清单和receipt，按该metadata片段填写 `meta.referenceAppendix`、`meta.finalVideoFrames`，不改写正文的旁白、分镜或 `words.json`。来源尚未核验时应在渲染前失败，避免先做完正文再补片尾。

已完成生成后可用 `python3 episodes-codex/_shared/render_with_references.py EPDIR --verify` 复核资料、冻结和最终媒体；此模式只写QA报告，不重新渲染正文或重写冻结清单。

新模式每页最多2项、默认5秒并提示暂停；原始题名和可选「原文摘录」各自检查排版，超限报COPYFIT，不自动截断或改写成概括。实际检查所有资料页和首/中/末帧、字幕结束及播放器暂停/手机全屏，提示与核验日期避开原生底部控件。正文、代码卡和参考资料分别计时，不额外延长旁白或覆盖代码卡。

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

封面由当期 `remotion/src/Cover.tsx` 和 `covers.json` 定义。当前 EP.14 的实际入口是：

```sh
cd episodes-codex/degradation/remotion
npm run covers
```

该脚本生成上层目录的 `cover-16x9.png/jpg`、`cover-4x3.png/jpg`、`cover-3x4.png/jpg`，并将 3:4 JPG 复制为 `poster.jpg`。其他期以自己的脚本为准。

逐份打开实际产物，检查文字、裁切、水印和 4:3 安全区：内容 x 315..1125、底边 y < 918，且无 `COPYFIT`。水印按该尺寸的 watermarkZone，不能为了塞入内容安全区挪动水印。`meta.poster` 决定站点海报文件，`covers.json` 的 poster 约定也要一起核对。

## 共享工具回归

历史 EP.14 的 20 镜、5152 帧样例只保存在 [固定回归输入](../episodes/_shared/tests/fixtures/degradation-v0.45.0/README.md)，用于共享工具测试，不是现行渲染工程。相关命令见 [validate.md](validate.md) 的「共享工具回归」。
