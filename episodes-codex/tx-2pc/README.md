# EP.21 · 2PC：两阶段提交，两个库怎么共同确认？

用户要求把方案拆为独立短片，本集只讲两阶段提交：可靠准备→可靠共同决定→分别落实，不并列其他方案；XA接口区别放文章。14镜28句、4章、3398帧，约113.267秒，不加速。

统一订单8124买商品7042一件，原库存4、拟改3均为示例。准备好的状态尚未提交；决定先可靠保存，参与方先后落实；拒绝和失联分支明确重置，未知决定不能自行猜回滚。原记录在恢复后继续有效，等待会占锁和资源。

- script.md/research.md/article.mdx/pronunciation.md：锁定旁白、实际打开的官方正文、四章文章和读音。
- plan.json/episode-config.json：镜头、章节及三个句首术语配置。
- voice/qa-v1.json与qa-independent-inputs.json：制作方声学/来源检查及root独立输入审计；最终选择25b+2c+1d，音轨SHA34253603c648ec9f45da93d2bf0c856c33ff377e397072c6cb97d0460a14572c。
- qa-motion-samples.json：最终同bundle的116张有字幕真实时序图；qa-continuous-samples.json：三段关键无字幕MP4及与最终图的主体一致性检查。
- knoll-props.md/visual-direction.md：状态含义、实际帧和布局。

共享语音/起音/混音均使用episodes/_shared，通用句级装配与冻结在episodes-codex/_shared。不要复制算法或按字数重排字幕。

```sh
python3 episodes-codex/_shared/assemble_sentence_episode.py episodes-codex/tx-2pc
python3 episodes/_shared/place_v2.py --dir episodes-codex/tx-2pc --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/tx-2pc
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/tx-2pc
```

Remotion目录npm ci后npx tsc --noEmit；node scripts/qa.mjs生成多阶段图，--shots=04,07,12 --motion --no-captions仅生成关键连续小样。正式视频由root在所有输入停写并独立检查后用共享freeze_sentence_episode.py冻结，再按/tmp/video-studio-render.lock串行编码；此目录不自行启动全片渲染。

三构图PNG/JPEG与poster已生成。4:3内容x315..1125、末文字底904<918；16:9副标题y520与两行主标题分开；poster为3:4 JPEG副本。配乐Wallpaper/CC BY 4.0，片尾已含总帧数，不追加全局片尾。

官方medium缓存不可用（LocalEntryNotFoundError），无逐字ASR、句内词级对齐或全片人工听辨结论；句内字符仅保存句包络，只有句首cue实测声学起音。用户尚未观看本集，独立检查不等于用户认可。最终编码/发布结果由root后续记录。


## 成片与发布记录

v0.50.3流程导航修订已完成正式编码与独立媒体复核，完整SHA见[render-result.json](render-result.json)，实际范围/限制见[qa-final.md](qa-final.md)。原v0.47.0已被用户观看并提出结构反馈，旧输入通过[历史索引](revisions/v0.47.0.json)追溯；本版不预记用户认可。GitHub发布与线上核验后按#152收尾。
