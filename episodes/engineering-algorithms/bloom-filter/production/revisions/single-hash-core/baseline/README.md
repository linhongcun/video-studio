# 布隆过滤器制作工程

工程算法第二期，EP39，slug `bloom-filter`，对应选题 [#300](https://github.com/linhongcun/video-studio/issues/300)；EA06是既有策划检索编号。

本期从商品目录的不存在查询切入，用同一位数组连续解释写入、确定排除、假阳性和回源确认。资料、真实配音、动态和正式成片检查已完成，150项实际输入已冻结；网站验收及上线结果见release.md。开工基线与真实时间见startup.json。

本次按现行流程制作原始题名/原文参考资料附录，完成全部检查后发布GitHub站点。

## 真实配音与装配

本期13镜26句按审核后的脚本文本真实生成，最终选择22a、3b、1c。31个候选、早期警告、选段与能力限制见`voice/substitutions.md`及`qa-voice.md`；不复制上一期音源。正文5741帧、约3分11秒，资料附录由默认入口在后续编码时自动生成。

```sh
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/prep.py --dir episodes-codex/bloom-filter
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/gen.py --dir episodes-codex/bloom-filter --jobs /workspace/video-studio/episodes-codex/bloom-filter/voice/jobs-a.json
/workspace/.venvs/video-studio/bin/python episodes-codex/bloom-filter/voice/audit_takes.py
/workspace/.venvs/video-studio/bin/python episodes/_shared/voice/build.py --dir episodes-codex/bloom-filter
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/bloom-filter
/workspace/.venvs/video-studio/bin/python episodes/_shared/place_v2.py --dir episodes-codex/bloom-filter --mode whole
/workspace/.venvs/video-studio/bin/python episodes/_shared/label_onset_strict.py --dir episodes-codex/bloom-filter
/workspace/.venvs/video-studio/bin/python episodes-codex/_shared/check_sentence_episode.py episodes-codex/bloom-filter
/workspace/.venvs/video-studio/bin/python episodes-codex/bloom-filter/voice/audit_track.py
```

上述命令记录本期实际制作顺序；已有合格音源后不为普通复核重新请求非确定性TTS。生成器已有文件会跳过，定向补选使用jobs-b/jobs-c和picks。初次依赖安装与后来React18类型修正分别保留在`qa-dependencies.json`及其归档，当前package/lock/config才是后续真实冻结输入。

## 正式成片与交付

默认入口实际生成5891帧、约3分16秒成片，含150帧原始题名/原文资料卡；完整SHA-256为`5b95e463dc5d95e7666de2c6fdf1c4c482bcdb6ca47faec835b040b917307143`。正文5741帧与全部8972个AAC包在追加前后保持，最终150项输入只读复核通过。

```sh
PATH=/workspace/.venvs/video-studio/bin:$PATH /workspace/.venvs/video-studio/bin/python episodes-codex/bloom-filter/freeze.py --verify
PATH=/workspace/.venvs/video-studio/bin:$PATH flock /tmp/video-studio-render.lock npm --prefix episodes-codex/bloom-filter/remotion run render
PATH=/workspace/.venvs/video-studio/bin:$PATH /workspace/.venvs/video-studio/bin/python episodes-codex/_shared/render_with_references.py episodes-codex/bloom-filter --verify
```

以上render是本期实际正式入口，普通核验使用verify，不为核验重渲或重新合成。制作输入见source-sha256.json；独立实际38张MP4图/完整解码与PTS见qa-video-independent，编码声音来源及数值范围见qa-encoded-voice-content。未执行逐字ASR、语义或全片人工听辨，也未把抽帧检查写成实时全片观看。

站点复制使用sync_site.py的已审完整媒体SHA门禁，实际12文件身份见delivery-copy.json；只在线发布video与16:9海报，另两比例封面留Git。正式版本与实际部署/线上核验在release.md和publication-evidence.json续记，本次仅GitHub站点。
