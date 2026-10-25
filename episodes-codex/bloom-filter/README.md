# 布隆过滤器制作工程

工程算法第二期，EP39，slug `bloom-filter`，对应选题 [#300](https://github.com/linhongcun/video-studio/issues/300)；EA06是既有策划检索编号。

本期从商品目录的不存在查询切入，用同一位数组连续解释写入、确定排除、假阳性和回源确认。资料、独立编辑、真实配音及动态预检已完成，150项实际输入已冻结；正式成片与上线结果按release.md逐阶段补充。开工基线与真实时间见startup.json。

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
