# P09 海盗分金币 · 2026-11-06 清晰度修订

本修订从 `4e9f846f2c70509f7fd98fc5b4d7d7ab77182386` 的已发布 P09 建立，回应观众对视频推理不够直观的反馈。保留原 14 镜、28 句旁白、4801 帧正文、研究资料、固定投票规则与三比例封面，改进否决后所得、当前报价和投票之间的视觉因果。原 `production/` 的冻结清单、媒体与 QA 保留历史身份；本目录未复制或沿用旧 QA 结论。

`input-provenance.json` 保存复制输入的原始 SHA、基线提交与原冻结身份。`voice.wav` 与实体 `remotion/public/audio/voice.wav` 沿用同一份已检查字节，本轮不请求 TTS。所选 takes 及整轨记录仅用于追溯，未重新生成。原脚本和 `words.json` 保留其完整 SHA 对应，修订的实际视觉以本目录 `remotion/src/Main.tsx`、`model.ts` 和新 QA 为准。复制的旧视觉说明只记录原稿意图，不能作为本轮已实现或验收的证明。

封面 JPG 原样复用；`cover-style.json` 的来源哈希仍说明它们当时的生成输入，不表示用后续已经扩充的共享题库重新渲染。新冻结器核对复用的实际封面字节与原冻结身份，冻结当前实际视频输入和参考列表引擎，不改写旧清单。

## 默认命令

从本目录运行。首次安装依赖使用现有锁文件：

```sh
npm --prefix remotion ci --no-audit --no-fund
npm --prefix remotion run check:types
npm --prefix remotion run check:references
python3 verify.py
```

视觉、时序和所有预检完成、输入停写后，才生成本目录新冻结清单。冻结会保存本目录分镜快照，不修改旧目录：

```sh
python3 freeze.py
python3 freeze.py --verify
bash render-final.sh
python3 verify.py --final
python3 render.py . --verify
```

`render-final.sh` 使用仓库唯一高清编码锁 `/tmp/video-studio-render.lock`，默认执行真实 Remotion 正文、full-range BT.601→limited BT.709 像素转换、共享背景音乐混音，再追加紫色原题/机构参考资料列表，最终输出本目录 `video.mp4`。`remotion/out/body.mp4` 不是发布文件。参考列表默认 150 帧（5 秒），最终 4951 帧；实际范围与完整 SHA 以本轮 `render-result.json` 为准。

新冻结前若需再改输入，可修订后重做本轮预检；产生本轮 `video.mp4` 后，冻结器拒绝重写清单。编码失败的中间输出与正式验收结论分别记录，不能用重写清单追认变更后的源。

## 资料和发布

`references.json` 原样沿用 R1、R2 的原题、机构与实际核验记录，证据引用仍准确指向原 `episodes/puzzles/pirate-gold/production/research-evidence.json`。冻结同时包含该证据文件。不将资料 JSON 字段检查宣称为本轮重新阅读原网站。

视频、资料列表、字幕和播放器实际复核完成后，按仓库持续授权更新原 `publication/`。只复制本修订检查通过的最终媒体及附录回执，`meta.sourcePath` 指向本目录 `remotion`；保留原 EP、slug、标题、创建和首发时间，实质修改只更新 `updatedAt`。文章截图如重新导出，必须来自本轮精确帧，并记录 limited709→full601 JPEG 的实际像素转换。单片修订使用站点补丁版本，发布前再次同步主干并核对版本占用。

GitHub 交付包括主干合并、附注 tag/Release、Release 后 Pages 部署、线上完整资产 SHA 与页面检查；不扩展为外部平台重发。实际执行结果及能力限制待本轮 QA 与发布记录填写，本文不预记通过或用户认可。
