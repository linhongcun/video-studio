# P06 · 12球称重趣味短片重构

任务 [#484](https://github.com/linhongcun/video-studio/issues/484)，基线 `ed088d557e59512c8b27946af4c3d39f91c48e16`。本修订按趣味解题短片定位重写叙事与动画，先具体称球、排除与一个完整实例，再简洁补足必要分支；24候选容量分析及完整构造留文章。旧媒体、冻结和来源核验日期保持历史身份，不把新稿或检查记录写成已获用户观看认可。

上一线上媒体完整SHA为`7ee68c46527cfe4b20ad5c76eb0a5dd4f7626227401f96f9cfd4cf95096e1f2b`，236.7秒。输入来源和不变封面逐SHA绑定见`input-provenance.json`。同题面、主例与完整三称模型的适用范围须由独立稿审核对，不能仅凭复制旧验证报告认定新版画面正确。

## 依赖和当前入口

Node依赖位于本目录`remotion/node_modules`，由本轮`package-lock.json`实际执行`npm ci --no-audit --no-fund`安装。使用系统`/usr/bin/chromium`与Noto CJK字体，不依赖已删除旧工程的ignored目录。

本轮Python位于`/workspace/work/twelve-balls-simple-20261112/.venv/bin/python`，venv按`--system-site-packages`建立，并单独安装缺失的soundfile和共享参考卡锁。它不复制系统numpy或改共享算法。执行全流程前把该venv的bin放到PATH首位，保证npm中的`python3`及Python子进程`sys.executable`使用同一运行环境。

```sh
export PATH="/workspace/work/twelve-balls-simple-20261112/.venv/bin:$PATH"
BALLS_EP_DIR=episodes/puzzles/twelve-balls/production/revisions/simple-20261112/twelve-balls
```

下列步骤必须在当前脚本、分镜计划和配套文章独立审读通过后执行；本说明不预记完成。每镜保持两句，因为当前共享句级装配及检查器固定每镜两句；镜数由最终`episode-config.json`和`plan.json`共同确定。

```sh
node site/scripts/check-references.mjs --sources "$BALLS_EP_DIR"
python3 "$BALLS_EP_DIR/prepare.py"
python3 episodes/_shared/voice/gen.py --dir "$BALLS_EP_DIR"
python3 episodes/_shared/voice/build.py --dir "$BALLS_EP_DIR"
python3 "$BALLS_EP_DIR/assemble.py"
python3 episodes/_shared/place_v2.py --dir "$BALLS_EP_DIR" --mode whole
python3 "$BALLS_EP_DIR/verify.py"
python3 "$BALLS_EP_DIR/make-props.py"
npm --prefix "$BALLS_EP_DIR/remotion" run check:types
```

`prepare.py`及`assemble.py`是原本期薄包装，仅调用当前共享prep/装配，并写明紫色canvas元数据。gen/build直接用共享实现，不保留上一修订只允许改第12镜的限制。原句字幕、送模文本、take选择与实际句界各自记录；声学句界不等于逐字ASR或全片语义听辨。

## 冻结、完整渲染和检查

真实音轨、最终动画、文章图位、独立动态检查及来源检查完成后，全体写入负责人停写，再执行：

```sh
python3 "$BALLS_EP_DIR/freeze.py"
python3 "$BALLS_EP_DIR/freeze.py" --verify
bash "$BALLS_EP_DIR/render-final.sh"
python3 "$BALLS_EP_DIR/verify.py" --final
python3 "$BALLS_EP_DIR/render.py" "$BALLS_EP_DIR" --verify
python3 "$BALLS_EP_DIR/export-article.py"
```

默认完整渲染持有`/tmp/video-studio-render.lock`，先来源和冻结核对，再Remotion正文、实际full601→limited709像素转换、共享-16 LUFS混音，最后5秒原题/署名参考资料页。最终交付是本目录`video.mp4`，不得以`remotion/out/body.mp4`代替。不得重写旧revision或旧冻结追认新媒体。

冻结器记录本轮源码闭包、共享配音/混音/附录引擎、资料原文证据与媒体脚本，并校验不变封面与上一修订完整SHA。`make-props.py`只根据本轮实测时序生成制作说明，不硬编码旧15镜的讲解顺序。`export-article.py`从冻结文章的Figure/seekTo选取准确整数帧，实际转换limited709到full601 JPEG，写到本修订`publication-stage/article/`；最终图另需实际查看。

正式媒体解码、响度、字幕、关键连续动作、资料卡、桌面/手机播放器暂停与全屏、文章引用/回看及上线完整HTTPS SHA分别实际检查，并记录执行者和能力边界。站点元数据用实际`render-result.json`的帧数与附录范围；沿GitHub持续授权交付，外部平台未获本轮新发授权。
