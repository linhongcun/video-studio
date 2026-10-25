# P05 · 两枚鸡蛋与100层楼

内部EP33，趣味推理P05，对应#209。制作在此目录，发布数据在episodes/egg-drop/，站点读取后者。开工基线和主干隐藏草稿预留见startup.json及PR #270；真实交付状态另记qa-final.md/release.md，不把制作检查写成用户观看认可。

首发[Release v0.67.0](https://github.com/linhongcun/video-studio/releases/tag/v0.67.0)及PR #279交付历史保留：[观看视频与文章](https://linhongcun.github.io/video-studio/episodes/egg-drop/)。用户随后指出方法选择动机不清，并明确要求在开头说明与二分查找不同，见[观看反馈](feedback.md)。本轮只替换03/04四句，当前12镜24句、5569帧／185.6333秒，新正式成片和本地站点检查通过，修订发布及线上结果另见[当前QA](qa-final.md)与[发布记录](release.md)。尚无用户观看本轮修订后的结论。

本片兑现“怎样保证14次以内找到最高安全楼层”：规则后先演50、25两次都碎，0枚蛋但F仍可能0～24，说明不能保证一直二分；再交代第一枚圈范围、最后一枚逐层收尾的目的。固定10层晚碎的19次引出剩余预算；从14次倒推14、27、39的递减间隔，100层封顶。完整F31实例走8次，最后两枚都碎且答案唯一仍成功。严格最优性、完整边界和容量递推只在文章，视频无附录口头入口、代码卡或额外证明尾段。

原题楼层、鸡蛋及已知安全/会碎边界共同承担推理。条件预算分支与完整实例清楚分开，计数和边界只在落地结果确认后提交；最后一枚逐层试，未测楼层不提前显示成已知安全。实际帧、正常配音、候选和能力范围由本期QA记录，不把临时原型当作真实时序通过。

## 实际入口

共享实现保持原样，本期只用薄包装和参数，不复制起音、TTS、装配或混音算法。原20句PCM及句WAV原字节保留，只对03/04四句生成持久mini；新1233帧替原半开[755,1676)的921帧，下游统一移位312帧，无整轨DSP。旧生成来源保留于voice/input-provenance.json，新四句来源与组合证明见voice/binary-input-provenance.json及binary-opening-composition.json。当前只读复核使用build_binary_voice.py --verify；有意重建才运行下列构建并重新验收、冻结。

```sh
python3 episodes-codex/egg-drop/verify_math.py --output /tmp/egg-drop-math-recheck.json
python3 episodes-codex/egg-drop/build_binary_voice.py
python3 episodes-codex/egg-drop/assemble.py
python3 episodes/_shared/place_v2.py --dir episodes-codex/egg-drop --mode whole
python3 episodes/_shared/label_onset_strict.py --dir episodes-codex/egg-drop
python3 episodes-codex/_shared/check_sentence_episode.py episodes-codex/egg-drop
```

原始候选的prep/gen与选take由voice记录；薄包装只调用共享mini build，再按已验证整帧边界组合原PCM，不重做旧20句的DSP。assemble.py先调用共享装配，再在精确PCM／Decimal整数移位前提下保留基线10镜本地voice值；首轮浮点尾差及同规则4336帧完整SVG重验保留。实际依赖见voice/binary-dependencies.json；原件与QA归档revisions/binary-opening/baseline。当前真实0命名cue，不套旧期数量。

Remotion以本期锁文件进行实体npm ci，入口在remotion/package.json。先做真实配音下的关键连续片、实际DOM/文字运动包络及三尺寸封面检查，修正后停写所有生产输入。

冻结和独立verify必须分开成功，再启动正式编码：

```sh
python3 episodes-codex/egg-drop/freeze.py
python3 episodes-codex/egg-drop/freeze.py --verify
```

从remotion/运行本期npm run render，完整编码使用/tmp/video-studio-render.lock及有空间的短TMPDIR。正式媒体另核完整解码、连续PTS、同尺寸关键帧保真、独立实际画面及全轨/逐句选定音源覆盖，不把数值一致性冒充ASR或人工听辨。

正式媒体通过后才接入站点、升实际可用版本并检查双视口、24句字幕、四章、普通文章锚点和独立五课目录。按持续授权合并、附注tag/Release、Release后Pages和线上完整摘要核验；全部完成后以completed关闭#209，将#204更新为完成5题。外部平台投稿不在此授权内。

修订交付的三个助手均需显式--release，例如当前候选v0.68.3；首发firstRelease始终保留v0.67.0。sync_site.py --publish只同步14项发布文件，verify_site.py再传实际本地--base，verify_online.py传真实Release connector证据路径。新证据写revisions/binary-opening及out/binary-opening-site，不覆盖首发报告。创建／首次公开日期保留，修改时间按真实视频完成值与现行ISO毫秒精度记录，不改题目标题、slug或链接。
