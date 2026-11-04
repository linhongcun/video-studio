# P08 · 100人猜帽子

本期从主干 `60f92e6f7550b1ef4a450b6ebdae67d1888733f2` 开工，选择 [#212](https://github.com/linhongcun/video-studio/issues/212)，EP55 / 趣味推理P08 / `hat-parity`。1号在队尾先答、面朝右；固定五人帽色为白黑白黑黑。首句黑词编码奇、白词编码偶，后续词才是本人帽色。研究证据和模型执行记录均为本期新建，不继承旧片媒体或QA身份。

本期复用共享TTS、句级声学装配、起音、铺轨、混音、冻结及原题/作者资料列表。正常复核保留既定takes，不重复请求非确定性TTS。根目录入口如下：

```bash
node site/scripts/check-references.mjs --sources episodes/puzzles/hat-parity/production
python3 episodes/puzzles/hat-parity/production/verify_protocol.py
python3 episodes/puzzles/hat-parity/production/prepare.py
python3 episodes/_shared/voice/gen.py --dir episodes/puzzles/hat-parity/production
python3 episodes/_shared/voice/build.py --dir episodes/puzzles/hat-parity/production
python3 episodes/puzzles/hat-parity/production/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes/puzzles/hat-parity/production --mode whole
python3 episodes/puzzles/hat-parity/production/verify.py
```

配音schema适配按本期voice/input-provenance.json与schema-adaptation.json记录执行。句级声学包络不代表逐字ASR或全片语义听辨；本期真实执行能力以QA为准。实际声音就位、画面定稿、独立动态/COPYFIT/三比例封面检查通过，所有输入负责人停写后才冻结：

```bash
python3 episodes/puzzles/hat-parity/production/freeze.py
python3 episodes/puzzles/hat-parity/production/freeze.py --verify
npm --prefix episodes/puzzles/hat-parity/production/remotion run check:types
bash episodes/puzzles/hat-parity/production/render-final.sh
python3 episodes/puzzles/hat-parity/production/verify.py --final
python3 episodes/puzzles/hat-parity/production/export-article.py
```

Composition `HatParity`，1920×1080、30fps；新Remotion依本期锁文件执行npm ci。默认完整渲染使用 /tmp/video-studio-render.lock，先来源和冻结检查，再渲染正文，实际full601→limited709像素转换，共享混音，自动追加5秒原题/作者资料列表。交付为最终video.mp4，正文out/body.mp4不是完整交付。Figure两图时间须按真实稳定画面写入文章并在编码前冻结；成片后从同一准确整数帧做limited709→full601 JPEG导出。

发布复制最终video、三比例JPG、文章、字幕、分镜、来源及附录回执。metadata附录区间取render-result.json实际字段；已烧录字幕事实须在成片确认后记录burnedInCaptions。只上GitHub站点，外平台本轮未获新发授权。所有实际预检、成片、网页与上线结果分别留证，不由本说明预记通过。

## 本期交付

本期已按v0.103.0上线，完整5026帧／167.533秒，#212已completed关闭，总览8/10。正式媒体及本地／线上真实检查范围见[qa-final.md](qa-final.md)、[交付记录](release.md)与[机器回执](publication.json)。暂停原生控件黑渐变压暗底部字幕的观察与正常播放控件收起后的清晰视图均保留，不声称实体手机、逐字ASR或用户观看认可。
