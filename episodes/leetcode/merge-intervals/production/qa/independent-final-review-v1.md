# LC.56《合并区间》实际成片复核

**日期：** 2026-11-15　**执行者：** Devin  
**Session：** `ef027da0ba0a4431bfe7a5483b0338b5`  
**URL：** https://app.devin.ai/sessions/ef027da0ba0a4431bfe7a5483b0338b5  
**结论：BLOCKED。** 已观察到影响理解的发音疑点和明确的结束扫描/close 状态回退；需修正或由制作方复核后再放行。本结论不代表整体质量通过。

## 身份与范围

- 实际审查附件：`/home/ubuntu/attachments/a5c3629f-9a60-4178-bfca-2cb2a1b7a460/video.mp4`，SHA-256 `cf27d4baf4fc817f1af84a80edaf23fa4d49530051018ecd65418ca394df74b6`，6,052,392 字节。ffprobe：H.264、1920×1080、30 fps、4538 帧、151.267 秒；AAC 双声道、48 kHz、约146.2827秒。
- **视频制作源**为 detached worktree HEAD `78c3b3b2c086d4626f14796d18c55752b4206491`；本轮按时序和片尾文字有限查看制作稿/冻结元数据，不等于动画源码或算法实现全面审查。
- **发布静态资产**单独来自 detached worktree HEAD `0d7ec4b38bfb13cee75e00dd40254272c5c115f6`。此 worktree 含三比例封面及文章 SVG，不含 MP4；未据此声称视频由该提交生成，也未独立比较该提交中的视频文件。
- QA 依据为 `/home/ubuntu/repos/video-studio` HEAD `77d91e03c88e3bc7bc67465f645f2c2825ce3403` 的 `docs/qa.md` 和 `docs/validate.md`。

## 阻塞项

1. **区间端点发音影响辨认。** 本审读会话直接调用 `describe_audio` 的三次独立描述（48–54秒 mono、50–56秒 stereo、全轨）均输出“一到地/1到D”。对48–54秒片段的定向调用另返回`一、D`，与该方向相符，但不足以判定精确音素。多次直接工具描述支持末端“四”辨认不稳，列为阻塞；这是工具输出，不是人耳结论，也不提供源 WAV 的逐样本边界。盲听片段：`/home/ubuntu/lc56-final-review-v1/audio/blind_48.000-54.000_mono16k.wav`。
2. **合并规则的情态词改变。** 本审读会话直接调用 `describe_audio` 的三次独立描述（79–87秒 mono、81–87秒 stereo、全轨）均输出“允许合并”，而目标表达是“仍须合并”，改变了规则强度。本审读会话对79–87秒片段的定向调用也返回`00:02-00:03处：允许合并`，与三次描述一致。以上是音频描述工具输出，不写成人耳结论。盲听片段：`/home/ubuntu/lc56-final-review-v1/audio/blind_79.000-87.000_mono16k.wav`。
3. **09结束扫描动作迟于画面字幕。** 对视频原始帧号执行一次精确 `select=eq(n,...)`，覆盖 PTS 111.3–113.8 秒、间隔0.2秒并保留 `showinfo`。111.7秒起的画面字幕已是“已经没有下一段了，扫描结束时再把当前的十二到十四写入结果”，但到113.7秒抽样，画面仍为 `[8,10]` 当前、`[12,14]` 下一段；113.8秒才看到 `[8,10]` 完成、`[12,14]` 当前。状态变化仅能界定在113.7–113.8秒样帧之间；未用 ASR 的113.8时间去推断音素或口播起点。证据：`frames/audit-09-transition-contact.png`、`audit-09-transition-showinfo.log`。
4. **close镜确有完成状态回退。** 新增117.0–120.0秒精确帧号抽样，间隔0.1秒。PTS 117.0、117.4秒帧（源解码帧 n=3510、3522）均显示 `[1,6]`、`[8,10]`、`[12,14]` 三段青色完成；到了117.5秒（n=3525）切入“两条规则与最终结果”后，`[12,14]` 又变成黄色当前段，并持续至120.0秒。此前只抽到116.8秒，不能排除这次短暂完成，故现已确认先完成后回退。前后全分辨率帧：`frames/audit-close-117-120-004.png`（117.4）、`frames/audit-close-117-120-005.png`（117.5）；完整抽样表与原始PTS日志为 `frames/audit-close-117-120-contact.png`、`audit-close-117-120-showinfo.log`。这是独立于音频/ASR的可见状态问题。

## 其他观察与建议（不混入阻塞项）

- **开场映射不是阻塞。** 画面在6.667、6.700秒只映射 I0，7.033秒已显示六段；制作要求是先映射第一项、再显示全组，这一安排本身合理。若想更顺滑，可让第二句开始时逐步展开其余映射；不据此制造 blocker。
- **其他已查看的动作样帧（均为抽样，不是逐帧验收）。** 排序段28–40秒以0.2秒间隔查看（`frames/dense-sort-28-40s.png`）：I0–I5编号与身份色在抽样位置保持对应，排序后顺序为I1、I2、I3、I4、I0、I5；样帧未见ID/颜色错配，但不能证明未抽中的每一帧连续。嵌套段54–64秒（`frames/audit-nested-contact.png`）显示[2,3]位于[1,4]内，当前终点保持4、未缩短。间隙段82–96秒（`frames/audit-gap-contact.png`）显示[1,6]作为已完成段保留，同时处理[8,10]。端点相接关系在已查看的全片PTS联系表（0–150秒、每5秒抽样）及排序样帧中可见：[3,5]与[5,6]共用端点5，示例结果为[1,6]；这些样帧未精确定位相接动画的逐帧边界。证据表：`frames/contact-every-5s-pts-verified.png`、`frames/dense-sort-28-40s.png`。
- **字幕样帧边界。** 约53秒样帧字幕显示“一到四”，约84秒显示“仍须合并”；对应视觉样帧只核实屏幕文字，不证明配音实际发音或字幕精确起止。09段111.3–113.8秒精确PTS抽样显示字幕在111.7秒样帧已进入结束扫描句，而图形状态至113.7秒仍未分离、113.8秒才变化。代码卡相关抽样为141.233–146.233秒；上述均是离散样帧，未做全片逐帧COPYFIT验收。
- 本审读会话直接调用 `describe_audio` 对108–120秒切片的描述为“8到10因此独立成段。好。已经没有下一段了。扫描结束时再把当前的12到14写入结果”。多出的“好”可作为删减口头填充词的建议，非阻塞；描述文字不等于逐样本语音对齐。
- 本审读会话直接调用 `describe_audio` 对实际 MP4 音轨139–146.282秒 stereo 切片作定向描述：末句“随区间数线性增长”约在片段起点后1.8秒结束，起点后2.267秒仅有底乐。代码卡画面首现于141.233秒（元数据标记141.267秒），据该直接音频描述，**代码卡覆盖末句旁白的疑点关闭**；这不是5秒数字静音。MP4解码音轨在141.267–146.267秒仍有能量（mono16k RMS −32.07 dBFS、峰值 −18.90 dBFS），与底乐相符。此描述不是源 WAV 的逐样本语音边界。标题—作者附录从146.267秒持续至视频151.267秒；AAC轨在146.282688秒结束，其后约4.984秒无音轨覆盖，是否延续音乐属于制作选择，不列阻塞。
- 旧 `contact-every-5s.png` 尾部时间标签不可信：标140秒的格子显示代码卡，标145秒的格子显示附录；与精确 PTS 145、150秒的实际画面相符，内容约比标签晚5秒。旧生成命令未留存，不能断定是 `-ss` 或 PTS/标签重置导致。该旧表已弃用；可信全片表由无 `-ss` 的单次 `select=eq(n,0)+eq(n,150)+...+eq(n,4500)` 抽帧并记录原始PTS生成：`frames/contact-every-5s-pts-verified.png` 及同名 `-showinfo.log`。

## 片尾与静态资产检查

- 全分辨率 `view_image` 核查代码卡和附录：代码卡约为141.233–146.267秒，附录为146.267–151.267秒。代码内容在抽查帧中完整、可读，未见画布边界裁切；这不等于逐帧字幕 COPYFIT 通过。关键帧：`frames/audit-landmarks-25.png`（141.233）、`-26.png`（141.267）、`-29.png`（146.233）、`-30.png`（146.267）、`-31.png`（150）。
- 实际附录文字为`《Merge Intervals》 LeetCode`、`《Built-in functions》 Python Software Foundation`；原题大小写在全分辨率帧中可读（`Built-in`首字母大写，`functions`小写）。与制作提交的 `reference-appendix.json` 对照一致。这只是片尾文字/版面核查，不是本轮重新核实官方来源。
- 三张封面直接查看原图：16:9（1920×1080）、3:4（1080×1440）、4:3（1440×1080）；题名、标签及 `[3,5]` 与 `[5,6]` 在5处相接均可辨，未见明显裁切。文章 SVG 做本地静态检查：复用预览 `/home/ubuntu/lc56-review-evidence/article-01-df13a3e-preview.png`，其源 SVG 与0d7提交中的 SVG SHA 相同，结果文字可读。`publication/meta.json` 为 `draft:true`；未运行站点构建或网页/UI。

## 音频及审查边界

- 已导出的 mono16k PCM：`blind_48.000-54.000_mono16k.wav`（6秒）、`blind_79.000-87.000_mono16k.wav`（8秒）、`blind_108.000-120.000_mono16k.wav`（12秒）、`blind_111.500-116.500_mono16k.wav`（经 WAV 头校验为5秒/80,000帧）及 `full_track_mono16k.wav`（2,340,523帧、146.282688秒、4,681,232字节）。本审读会话直接调用 `describe_audio` 对111.5–116.5秒片段曾只返回约0.12秒音乐；与已核验的5秒文件长度不符，故该次响应已弃用，不作为证据，也不据此推断片段内容。
- 实际 `voice.wav` 不在已查的78c3提交或附件中，不能独立测源 WAV 的最后非零语音样本；构建元数据不替代源 WAV。未重查算法实现/官方来源、未逐帧审完全片、未做浏览器、播放器暂停/全屏、网站或线上验收。未运行测试、未安装依赖、未修改仓库、未 commit/push；新增报告与抽帧/音频证据在仓库外。各既有 worktree 状态为干净。

## SHA-256 清单

下表为自动读取 `sha256sum` 的审阅输入与本报告引用的关键证据；报告写成后逐项对文件复核。视频制作源与发布静态资产分列，避免混为同一提交。

| 文件 | SHA-256 |
|---|---|
| `/home/ubuntu/attachments/a5c3629f-9a60-4178-bfca-2cb2a1b7a460/video.mp4` | `cf27d4baf4fc817f1af84a80edaf23fa4d49530051018ecd65418ca394df74b6` |
| `/home/ubuntu/repos/video-studio/docs/qa.md` | `5b8b88e2ff04733cfa828d6b9c2966f272cda4826ed4c91209a08315c69862db` |
| `/home/ubuntu/repos/video-studio/docs/validate.md` | `99eb15d680c50f12ea13a46b7c88f950acd7109605071be405819caf845c4102` |
| `/home/ubuntu/repos/video-studio-review-78c3b3b/episodes/leetcode/merge-intervals/production/script.md` | `b64372f6215c841522b08be26c3ce7c5b90001e3df1655714d4b51e77f4abb16` |
| `/home/ubuntu/repos/video-studio-review-78c3b3b/episodes/leetcode/merge-intervals/production/storyboard-design.md` | `4a262240da44fdcbe6247856f8ff9ee07ac6ffd2dd35c059e19196cf03bd5c85` |
| `/home/ubuntu/repos/video-studio-review-78c3b3b/episodes/leetcode/merge-intervals/production/storyboard.json` | `b340748696a79f83be912a73811184591d59d0aa75ce78ff8320e6c5c667eccb` |
| `/home/ubuntu/repos/video-studio-review-78c3b3b/episodes/leetcode/merge-intervals/production/voice/params.json` | `8d8b3b3401a2c2f32a6589f3bb9e40c7c0ab57c23cd752f3253ab7bc88fbb8d1` |
| `/home/ubuntu/repos/video-studio-review-78c3b3b/episodes/leetcode/merge-intervals/production/voice/build.json` | `5b28bee2384ef6e1a5132c5f16ca173ac8840610cc872e518fa4363343d1d356` |
| `/home/ubuntu/repos/video-studio-review-78c3b3b/episodes/leetcode/merge-intervals/production/words.json` | `43cb5ffab86a81a124257ae404e11a2767061ab4cd78a012afbad4c915190352` |
| `/home/ubuntu/repos/video-studio-review-78c3b3b/episodes/leetcode/merge-intervals/production/references.json` | `b05d6ff63450f1ddaf817ea8986d8f6e84c340902defec46d19b564aa001de49` |
| `/home/ubuntu/repos/video-studio-review-78c3b3b/episodes/leetcode/merge-intervals/production/reference-appendix.json` | `7e6eafce20fccb1bbd4bc7b357ab55189c10e600767d1e8fa908f9111552943b` |
| `/home/ubuntu/repos/video-studio-review-78c3b3b/episodes/leetcode/merge-intervals/production/research/source-evidence.json` | `ed903ca1a2c25d147ad8d7787af02151efdf541e4f400fffe5ec5db5962089ae` |
| `/home/ubuntu/repos/video-studio-review-0d7ec4b/episodes/leetcode/merge-intervals/publication/meta.json` | `4d9e7667e6a7176d9e5cdbd46ef96c76c1a3a54fa2f13280c2e289cd27134602` |
| `/home/ubuntu/repos/video-studio-review-0d7ec4b/episodes/leetcode/merge-intervals/publication/cover-16x9.jpg` | `247ec14aaeb57df4385174a3b82d6532d4628b461abb06287925bd174c3a87e7` |
| `/home/ubuntu/repos/video-studio-review-0d7ec4b/episodes/leetcode/merge-intervals/publication/cover-3x4.jpg` | `35c4be4acda1d86e999cd613b93f504ac87a797a4935a2f044a50278a1506d8f` |
| `/home/ubuntu/repos/video-studio-review-0d7ec4b/episodes/leetcode/merge-intervals/publication/cover-4x3.jpg` | `ec426d57f8b9d90c838b28e3dfccccbdc884bfee596e324cabf37b85f499f4d6` |
| `/home/ubuntu/repos/video-studio-review-0d7ec4b/episodes/leetcode/merge-intervals/publication/article/01.svg` | `0813a71545638b45659261589e076fc255318ade7cf401a4a4a77cbfdf8dbadf` |
| `/home/ubuntu/lc56-review-evidence/article-01-df13a3e-preview.png` | `107405920be31dc7753de333c523c39d9e240441f582046cf61dc4b34fce0165` |
| `/home/ubuntu/lc56-final-review-v1/frames/contact-every-5s-pts-verified.png` | `3cdc46caf40209baac742b2788706559756f7a2a63cf656fc0269094acba8de2` |
| `/home/ubuntu/lc56-final-review-v1/frames/contact-every-5s-pts-verified-showinfo.log` | `eb70ee4fc7c7b7f13d9b81c08dd1015efaeffb4002e15d1a4f196790f1e55b8e` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-close-117-120-contact.png` | `294b5aaaab1ef67bb2cdffb7c271c10dd1084a6acc6847fa43e0440609a50d6e` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-close-117-120-showinfo.log` | `80ee073ce6d8efb04d001a53f40eaa4ebddc677daec47ac71a04c7ffbdec6538` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-close-117-120-003.png` | `409ec8a4d5d85388bcd29eee8d86e1452e00a1cc2d74017b51785eff0c03c086` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-close-117-120-004.png` | `f42f7c8b501ec3dbe6d0bb59c9a85c20851b6a97865d2914322e90cfa18ef334` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-close-117-120-005.png` | `1a651b05fbae0faebb3f95ea62d6163322429c5459bb5fdc07981151f2201826` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-09-transition-contact.png` | `e1bd6066318e5f1c947859268565d7ede6031a5f6b42acc6456a824bcdb7e374` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-09-transition-showinfo.log` | `7bf7fae0c421c0a389b2c0c6d1c947246fa30c2ed351a3cba68a5848ba063a89` |
| `/home/ubuntu/lc56-final-review-v1/frames/dense-sort-28-40s.png` | `acae1801e99cbe763401b0c7d9c8d69f840e6937125a5fcc9f55207273757f63` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-nested-contact.png` | `81130fabc287201cc36ef2a38125e04af37aab2886d7f95e89965b5ef472447b` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-gap-contact.png` | `30ea0805b20a8544f93e33cde649cef85983c40c1fda3f1cca02f03a8b0cfff2` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-flush-contact.png` | `fd147323d7450f2f85701809e73d9a9c8d7a68569141b737de86166908ee13d0` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-close-transition-contact.png` | `db3b0085ae7212901ddfee0d2fa6e226ce033b48e3b246968e568822cd7d9d16` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit_close_000.png` | `31964f67691bde1a7df2deb90fe7ae7c61ca672cb5fe4ad00ba3b797e91b295f` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit_close_004.png` | `e6b8385cd07a3ed227b98b2b734c6713df7a069c1ab1c58e1c5f1b62f32adb96` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-landmarks-25.png` | `36aace7ee56ee0f95346937f56d14bc431a0626c4e4d3e1664ad2d8bee8e7825` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-landmarks-30.png` | `4ac64cbebc4cd0bd851fb0b3d423127e208251d2c6e604d52b3c922dbc65589c` |
| `/home/ubuntu/lc56-final-review-v1/frames/audit-appendix-150-text-full.png` | `ce15519ccf9982c39640477b0b59b7f1b6e99e3b427c7cdfdf6e0eaf2f1651ee` |
| `/home/ubuntu/lc56-final-review-v1/audio/blind_48.000-54.000_mono16k.wav` | `d6ff8c966b49f409a46cdd8c38add852c7b925bc471bc31e3701296e45ae4d53` |
| `/home/ubuntu/lc56-final-review-v1/audio/blind_79.000-87.000_mono16k.wav` | `5fe71d0d8623d5bd7a830a7160e329aff0cb0e080ca141cda052350e9dbdaebf` |
| `/home/ubuntu/lc56-final-review-v1/audio/blind_108.000-120.000_mono16k.wav` | `340fe4ee92d16a7eb413cd297af285327c8b4e72febcc1e8b6dc4291bba69787` |
| `/home/ubuntu/lc56-final-review-v1/audio/blind_111.500-116.500_mono16k.wav` | `b03d00b4afa4f7810380b218f02db6d93d5918b16a391b2dc8d881b39c159b54` |
| `/home/ubuntu/lc56-final-review-v1/audio/full_track_mono16k.wav` | `29e2c616412c5eda0d7d3c0680dd822792b4096e26a087e65825de3f819baa4f` |
