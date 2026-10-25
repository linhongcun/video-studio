# EA01 · 一致性哈希

对应[#295](https://github.com/linhongcun/video-studio/issues/295)，内部EP38，制作PR[#304](https://github.com/linhongcun/video-studio/pull/304)。制作目录为本目录，站点读取`episodes/consistent-hashing/`。正式交付与线上证据见后续`release.md`，不以本说明预记上线或用户观看认可。

本片围绕同一次缓存扩容：先认识键与确定性哈希，再看直接对节点数取余为什么改变许多旧归属；由保留已有去向的目标推导固定编号环、顺时针首个节点及回绕。保持A20/B50/C85，加入D70，只接管(50,70]。同一批十个示例键取余改变8个、环改变2个，均为这组输入的结果。虚拟节点另用预先配置的示例，并按物理身份着色，区分分配区间、数据迁移和请求热度。

14镜、28句、4章，1920×1080 / 30fps / 5881帧，约3分16秒。没有代码尾卡，工程机制和完整示例实现分工：视频解释连续因果，文章保留Python和边界。资料来自实际读取的NGINX、Cassandra5.0及Redis官方文档；不冒充完整产品实现。

## 可复现入口

所有配音、装配、起音和混音都调用保留的共享实现；`remotion`在本期实体目录按锁文件独立安装。Python声音工具使用`/workspace/.venvs/video-studio/bin/python`，不把系统Python缺失依赖写成已安装。

```sh
python3 episodes-codex/consistent-hashing/verify_model.py
/workspace/.venvs/video-studio/bin/python episodes-codex/consistent-hashing/assemble.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/place_v2.py --dir episodes-codex/consistent-hashing --mode whole
/workspace/.venvs/video-studio/bin/python episodes/_shared/label_onset_strict.py --dir episodes-codex/consistent-hashing
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/check_sentence_episode.py episodes-codex/consistent-hashing
```

现有音轨从已选择的39份候选中装配，输入请求、原始音频、选段及每句处理证明均在`voice/`。不为复现重新随机请求TTS。句级时序和声学检查不等于逐字ASR、语义听辨或全片人工听辨；本轮没有执行这些能力。

在本期`remotion/`中：

```sh
npm ci --no-audit --no-fund
npx tsc --noEmit
npm run covers
node scripts/qa.mjs out/preview
```

实际`out/timed-preview`使用28句正式时序产出98张PNG、三段无字幕编码片，根与独立审稿的检查范围见`qa-preflight.json`、`qa-motion-independent.md`和`qa-term-onset.json`。封面、标签、物理/虚拟身份的预检失败与定向修订在`qa-revisions/`，不删除失败历史或仅凭静帧宣布整片清楚。

所有写入负责人停止修改，动态检查闭合后，先冻结再独立核对：

```sh
python3 episodes-codex/consistent-hashing/freeze.py
python3 episodes-codex/consistent-hashing/freeze.py --verify
```

正式渲染使用本期`npm run render`，在外层取得`/tmp/video-studio-render.lock`并设置有空间的短`TMPDIR`。编码前后核对同一清单；如果输入改变，先停止排队或编码，重新检查与冻结，不拿新清单追认旧媒体。

正式文件完成后运行共享`check_encoded_episode.py`、本期`verify_encoded_voice.py`和独立`verify_video.py`，实际看图并记录能力范围。网站接入使用同一媒体及冻结字幕，完成桌面/手机播放、全部章节seek、图文与新系列检查后，按持续授权合并、Release、再次部署并核验完整线上SHA。完成后才关闭#295；本轮不发外部平台。
