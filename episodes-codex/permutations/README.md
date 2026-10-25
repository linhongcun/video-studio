# 全排列：怎样排出所有不同顺序？

## 当前交付状态

真实配音与分镜已冻结，141项输入逐项核对；正式成片5613帧/187.100秒，完整SHA `dbbc28347c93e6667934ff691ff27aebcc007597ae4d2e5ca9fd9cf2a222e2c9`。算法、审稿、真实动态及六封面、正式MP4独立视觉与媒体检查均已通过，最后150帧为5秒完整Python暂停卡。实际范围与能力限制见`qa-preflight.md`、`qa-audio-preflight.md`、`qa-final.md`与`qa-media-independent.md`。网站发布状态统一见[批次记录](../../docs/leetcode-batch-next/README.md)。本轮未发外部平台，尚无新片用户观看结论。

以下保留阶段1制作交接记录，开发占位分镜和未生成配音的说明只适用于当时，不是当前状态。

开工基线8d037aa3e05ce1ed992df6b758b9b2227dd8b18b，issue #84，LC.46，内部EP36。本期完成phase1文稿、独立程序验证与原创动画源码，配音、真实动态预检、成片及发布阶段尚未执行。

14镜28句4章，846字。storyboard当前5255帧约2分55秒，仅布局用provisionalTiming/pendingAudio；真实音轨后应重新装配，不得当实计时预检。正文从题意推导“逐位选未用数字→排满存副本→撤销后再试”，随后命名回溯。三张原题数字卡沿真实83事件保持身份，输出副本独立保留；used只指当前路径，撤销后可重用。

唯一执行源solution.py，solution.json和文章完整代码块与它同源。运行：

```sh
/workspace/.venvs/video-studio/bin/python episodes-codex/permutations/research/verify_solution.py
```

独立itertools oracle1229个合法输入、输出唯一、每行独立副本、输入保持等检查通过；AST只给原算法插入快照，不包含替代求解器。证据research/solution-verification.json；实际资料访问research/source-access.json。程序完整22行，末150帧独立卡固定36px/35px，供暂停查看。

本地TypeScript：在remotion目录执行`npx tsc --noEmit`。依赖在本期remotion/node_modules，root以当前锁图独立npm ci，无已删除旧工程依赖。phase1未生成TTS/PNG/MP4，不声称ASR、声学或全片人工听辨通过。

独立文稿/算法审通过后，使用episodes/_shared/voice流程生成take、选段、整轨；调用prepare_code_endcard.py（转发共享句级装配），再执行共享铺轨/起音/句级检查。实际动态和封面安全区检查闭合后才freeze.py、编码、媒体复核与网站接入。未来所有渲染用`flock /tmp/video-studio-render.lock`、`TMPDIR=/workspace/perms-tmp`、`/usr/bin/chromium`，避免并行争抢。

完整源码入口remotion/src/Main.tsx、data.ts、CodeCard.tsx、Cover.tsx；画面只读lesson.json。Cover16x9/Cover4x3/Cover3x4共用同组件，4:3纵版0.75缩放居中x315，关键内容x405..1035且底900<918。封面生成脚本仍需实际渲染验证，此处是布局设计声明。

预计与同批v0.69.0接入，实际首发由root按最新上游统一复核。GitHub发布在持续授权内，外部平台本批未授权。没有预记冻结、预检、成片或线上通过。
