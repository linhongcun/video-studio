# P09 独立流程审查

本次只读审查基线为草稿 `72c8f03a5`。实际通过来源字段/证据/原题与文章链接预检（2项）和实体目录检查（62组、11系列）。这不是来源重新实读、动态、音频、编码或站点验收。完整输入SHA与实际范围在同名JSON。

当前草稿有两处 `Figure seekTo={0}`，须在冻结前换成真实音轨中的稳定时点：四人局通过后的 `99,0,1,0`、五人局投票确认后的 `98,0,1,0,1`。Figure的图注、alt与所属章已经写出具体图义；最终图片尚未生成，不能把组件存在记为有效成片配图通过。两项SourceQuote分别使用R2投票门槛与R1倒推关系，source gate已核对本仓连续原文证据与完整链接。

README和episode-config仍标静态草稿/环境中断；恢复后应追加实际恢复与当前生产状态，保留中断的历史事实。`model-verification.json`目前真实身份是V8执行，后续Node复验另存结果，不改称原先已在Node运行。

## 可复用入口及必须适配之处

P07当前 `production/{prepare.py,assemble.py,freeze.py,render.py,normalize-color.py,references-adapter.py,verify.py,render-final.sh}` 是安全的薄包装参考。共享配音、裁尾、起音、句级装配、混音与附录引擎不另抄算法。`freeze_navigation_episode.py`要求branch-map源码，不因有“倒推”就给本期选用该冻结器；P07的本地freeze薄包装委托共享 `freeze_sentence_episode.py` 更合适。

复制后必须先改本期package/锁文件根身份、Remotion注册的composition ID、render.py的birthday路径守卫与references-adapter中的birthday模型PROVENANCE。P07帧数、音轨、takes、媒体、source-sha256、附录回执和QA都不成为P09的已验收产物。Remotion新锁须在本期 `npm ci`，真实 `public/audio/voice.wav` 必须是实体副本。

本期现有freeze-inputs已包括 `model-data.json`、`model-verification.json`、`verify_model.mjs`、`research-evidence.json`；不要因P07薄包装默认只识别model.json而漏冻本期模型。另纳入references、article、原题/署名/短引证据、默认入口、紫色adapter、通用附录三个引擎、色彩转换、所有真实共享导入、封面动态文件与锁。停写后再冻结；最后生成的MP4和附录回执不作为编码前输入。目录/题库扩容可能改变共享catalog整份SHA，应先完成封面与模型，再冻结同一份输入，不改旧P07清单追认新源。

以下是**本期包装实现后**的准确命令约定，当前草稿尚不存在的本地命令不能提前记为已执行：

```bash
P09_DIR=episodes/puzzles/pirate-gold/production
node site/scripts/check-references.mjs --sources "$P09_DIR"
python3 "$P09_DIR/prepare.py"
python3 episodes/_shared/voice/gen.py --dir "$P09_DIR"
python3 episodes/_shared/voice/build.py --dir "$P09_DIR"
python3 "$P09_DIR/assemble.py"
python3 episodes/_shared/place_v2.py --dir "$P09_DIR" --mode whole
python3 episodes/_shared/label_onset_strict.py --dir "$P09_DIR"
python3 "$P09_DIR/verify.py"
```

本期14镜28句、4章，plan.cues为空，因此声学句界可以核对，但没有词级对齐或标签起音任务；零cue检查不能声称已核对未存在的词级标签。关键连续无字幕小样应确认：假设局不变成实际出局复活；拟分配不提前变成已收钱；三人/四人门槛正确；最终1/3/5号投票达3票后才确认98/0/1/0/1。

独立动态、声音边界、COPYFIT和三比例封面均接受、各写入者停写后，再执行：

```bash
python3 "$P09_DIR/freeze.py"
python3 "$P09_DIR/freeze.py" --verify
npm --prefix "$P09_DIR/remotion" run check:types
bash "$P09_DIR/render-final.sh"
python3 "$P09_DIR/verify.py" --final
python3 "$P09_DIR/render.py" "$P09_DIR" --verify
```

默认render必须经过来源/同一冻结清单→完整新声轨正文→fullBT.601到limitedBT.709的实际像素转换→共享混音→同色资料列表。资料卡只显示原题与作者/机构；本期2项应是一页、5秒、30fps时150帧，无原文摘录、日期、链接或额外提示。最终片首/中/末资料帧、正文字幕边界、原生暂停/全屏及配色仍需实际看。通用共享render入口会选择通用配色，不能绕开本期紫色adapter去渲染或验错另一套回执。

## 图文、元数据与站点发布

草稿 `meta.json` 目前合理：EP54无其他条目占用、series=puzzles、draft=true，未填不存在的video/poster，也未预填首发日期。`sourcePath`目前真实指向文稿目录；动画建立后，发布时改到本期实际remotion入口。

不存在可假定使用的Astro content.config JSONSchema；实际合同来自 `site/src/lib/episodes.ts`、`scripts/check-layout.py`、dates/references/articles校验器与真实媒体回执。首次公开保留createdAt，填写真实publishedAt/firstRelease/current updatedAt；ISO时间带时区、秒或最多毫秒。媒体video/poster指真实文件；finalVideoFrames和referenceAppendix逐项使用 `render-result.json.publicationMetadata`，本期最终应为实测正文帧加150，不能沿用P07的3681/3831。实际确有烧录字幕后写 `burnedInCaptions:true`，避免播放器重复显示，仍须保留正确VTT与章节。

成片后按已冻结时点生成两幅图；从limitedBT709导JPEG要实际转换到fullBT601，不只贴颜色标签。若调整图位或文字，保留冻结制作稿，另记站点派生稿的前后SHA。接入publication时复制最终video、海报、article、script、storyboard、sources/evidence与两份附录回执；配音WAV不作为发布副本。

```bash
python3 scripts/check-layout.py
npm --prefix site run check:dates
npm --prefix site run check:references
npm --prefix site run check:articles
npm --prefix site run build
```

draft=true会使references/articles门槛跳过本期，不能把全站通过记成本期成片已验。最终published条目实际通过后，还要桌面/触屏模拟播放器与章节、烧录/原生字幕状态、Reference首中末帧、SourceQuote悬停/点击/键盘/关闭/来源入口、亮暗主题和Figure回看/原图检查。PR合并、附注tag/Release、**Release后再部署Pages**，随后核对canonical线上完整媒体SHA、海报、28条字幕/四章与真实更新日志；这些完成后才以completed关闭#213并同步#204。本轮限GitHub与本站，平台新发没有新增授权。
