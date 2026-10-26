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

## 第10批参考资料名单与当前入口

本批只在完整原片之后追加`title-author`参考资料名单，每页最多4项、默认5秒。完整body包含原150帧Python解法卡，参考资料从代码卡结束后开始；solution.py/json、分镜、字幕和音轨均不改写。基线`4213a233c4c242b04453b8c1215031dc421c2398`的Git发布原片已绑定原render-result与总帧数，逐字节保存在`revisions/reference-endcards/body.mp4`及同SHA的`remotion/out/body.mp4`；本批直接使用这些原片追加，不寻找旧缓存或重制正文。

原141项历史输入全部现存并按原路径或before快照逐一验证，保留全部原key。当前清单只声明现存真实依赖及本轮资料/入口，不将它当作原MP4已重新编码的证明。旧freezer及清单完整保存在revisions/reference-endcards；旧QA、局部拼接、媒体和算法测试记录保留其历史身份。完整源码入口的静态import、别名及公开音轨核对不依赖缺失缓存，详见[生产入口报告](../../docs/reference-endcards/batch-10/production-entry-check.json)。当前freeze.py保留实质断言，分镜快照/placeholder和代码卡只读核对；不调用原写入型freezer、prepare_code_endcard、装配、TTS或算法测试。

资料负责人停写且来源预检通过后，从仓根执行：

```sh
node site/scripts/check-references.mjs --sources episodes-codex/permutations
python3 episodes-codex/permutations/freeze.py
python3 episodes-codex/permutations/freeze.py --verify
```

默认`npm run render`接共享bibliography wrapper，先核对来源和冻结，再运行`render:body`及附录。`render:body`保留原voice→mix闭环、编码参数和concurrency=2，仅把mix输出改至`out/body.mp4`，完整Python卡仍由现行源码渲染。`npm run render:references`从该完整body单独追加资料；`npm run verify:references`是后续完整交付检查入口。本批只做来源与只读冻结/入口检查，未运行正文、混音或重复完整解码。最终总帧数以新receipt、render-result及发布metadata为准；[本批进度](../../docs/reference-endcards/batch-10/README.md)不预记未完成的媒体或线上通过。
