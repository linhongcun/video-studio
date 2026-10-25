# P01 视频内完成最少七场说明

用户已观看v0.55.0并认可主体，唯一反馈是结尾把完整证明推给配套文章，许多人只看视频。本轮保留前17镜与三张封面，替换旧18为18–25，将六场不能保证的论证放进视频。平台新发不在范围。

## 不变部分与来源

- 旧公开视频完整SHA：`d643c1d75a23568e5aed6f25115bdab033e5e4317285e36f4cdc933694e2f59f`。
- 旧未混音Remotion编码SHA：`429f791652167a4b298f3059bfa2dee0349506d16124313fff94c6381230af0d`。
- 前17镜display frame为0–5874，接点5875/30秒。前34句时序及前9,400,000个48k单声道PCM样本保留。
- `before/`只保留解释来源与比较所需的小文件；旧媒体可从v0.55.0生产提交追溯，未重复提交WAV/MP4。
- 该接点非关键帧，附近有B帧引用旧尾；采用准确trim后快速重编码旧画面，明确记录微差，不宣称无损压缩数据复用。

## 新尾段

每镜两句，18–25共16句，约400字，依次解释：未输者仍可能最快；24匹各至少输一次；六场最多24次且无重复余量；任意首场可遇到真一真三在场、真二在外；再次同场则真三重复输；始终不同场则两套从开赛起固定的二三顺序产生相同赛果和后续选择；视频内收束最少七场。

来源与通用下界沿用本期已实际核验的research-math.md和独立数学证明。本轮不新增外部事实，也不把有限程序测试冒充通用证明。

## 检查与发布

共享局部配音与装配已完成：8976帧、299.2秒，25镜50句、7章；新尾3101帧。前34句原PCM与前17镜时序严格保留，见voice/ending-preservation.json。218项冻结、独立真实动态、正式媒体与两视口站点检查已完成，成片完整SHA为334af0a52a6184976e5544f647ec61201368bdc2948bea5addc456f6839cfcf8。PR #228已合并并发布v0.56.4，Release后部署40143372825成功；北京时间07:40:17首轮10个canonical GET核验全部通过，#205已completed关闭。完整结果见本目录online-verification.json与本期release.md，不将用户对旧主体的认可说成已观看新尾段。

## 实际制作命令

在仓根检查配音保留与冻结：

```sh
python3 episodes-codex/horse-racing/revise_ending_voice.py --verify --baseline-wav /workspace/horse-ending-before/voice.wav
python3 episodes-codex/horse-racing/freeze.py --verify
```

原音轨可由`git show v0.55.0:episodes-codex/horse-racing/voice.wav`恢复到已忽略的工作目录；其完整SHA须为`2af8c739a08c2cf9c1972b22a0c31e1dd30cb6260fc92af749dd987a693def66`。尾段复现所需的sents/picks/params/build和输入来源保存在`voice/ending-*`，候选在`voice/takes/`。先用共享build恢复尾声轨，再用薄编排连接旧PCM前缀与尾声轨、调用共享assemble/place/check，不能把整条重新归一化后称为原PCM保留。

本次只渲新尾，封面复用。正式命令：

```sh
TMPDIR=/workspace/horse-tmp flock /tmp/video-studio-render.lock npm --prefix episodes-codex/horse-racing/remotion run render:ending
```

`render:tail`按全局5875–8975渲3101帧，`render:reuse-prefix`从v0.55.0恢复原发布MP4并验证完整SHA，按display frame准确trim旧前5875帧，再与新尾concat、veryfast/CRF18快速重编码。旧片与尾片音轨均丢弃，使用检查过的新整轨；`render:mix-ending`再调用共享混音。输入、命令与完整结果保存在本目录的render/remix小报告，完整运行日志为`/workspace/horse-ending-render.log`。

本轮冻结清单218项；正式渲染与拼接前后均只读核对，不通过改清单追认已编码输入。最终媒体比较使用本目录`verify_encoded_preservation.py`，它是事后只读QA，不参与渲染；原先预设预演平均RGB差上限3.0/255、前段旧新编码上限1.0/255，检查实际差异并保留结果。

## 画面度量的实际诊断

最初43点异分辨率启发式有6点超出3.0，最大3.3415，原始failed报告保留。6点全部以1920同网格复验，原阈值下最大1.81398；统一缩小后的匹配参考最大1.14602，直接960截图与1920截图再缩小本身差2.50–2.70。由qa-raster-diagnostic.json与独立实际成片复核闭合，未改阈值、源码或媒体。verify_raster_diagnostic.py可复算，所需原尺寸参考由QA_SCALE=1的qa.mjs生成。四个原段编码样本均值差最大0.200388/255，原1.0阈值下通过。
