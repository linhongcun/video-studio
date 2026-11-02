# Redis Cluster / EP51 制作输入

《Redis Cluster：一个副本，怎样获得接管哈希槽的授权？》，issue #297。基线`01cd181caf24d4a8ce846c0eb8faeeab8f0054e2`，当前系列实体目录与sourcePath为本目录及remotion；从当前保留MQ15锁文件冷安装依赖，不运行或依赖其他单期的生产脚本。

固定Redis8.4.0源码commit`60ba86f3c8b4e1ec96451171753a0a38e5c45a0c`；来源原文、原题证据、许可与实际GET保存在sources。官方docs未标个人作者，使用Redis机构。源代码与文档各自许可保留，不把产品源码说成图标的MIT许可。

主线沿三主三副本中的主甲失联，先本地PFAIL、近期多数报告确认FAIL，随后合格甲副本提高选举轮次、获得乙丙两票才晋升并传播新槽归属。少数对照重新从参选前开始；数据边界回成功分支解释异步复制。具体消息顺序、轮次5→6、末条未复制是教学示意，不冒充产品运行回放。

`model.py`产生16教学状态和3345有限断言，覆盖角色/新旧轮次/原三主门槛/少数无晋升/不凭授权补数据。它不是Redis实现、真实网络或全部故障路径；正常单票抽象来自投票人lastVoteEpoch约束，不声明真实接收端有该模型的去重集合。

`actual-runtime.py`使用共享工作目录下固定源码编译的真实redis-server/redis-cli，端口16600–16605与bus26600–26605。当前`examples/actual-runtime/result.json`及完整日志保存两项实际结果：正常自动晋升并收敛原0–5460槽归属、已确认FAIL后只剩乙可授权时候选仍为slave。成功分支WAIT后才故障，只核实已复制值保留，未做未复制写入损失实验。少数对照通过候选SIGSTOP、两主确认FAIL、丙退出、候选恢复来门控，非一般网络分区或断电实验。首轮脚本把fail?误匹配fail，旧脚本/全部日志/false结果整体保存于`examples/actual-runtime-attempt1-preserved`，新执行用精确flags，未重写旧失败证据。重复运行前必须为输出目录另起版本，不能覆写已记录实验。

根已批准叙事与技术审读后，使用共享prep/gen/build生成24句实际冰糖旁白：正文4466帧、148.8666667秒，voice SHA256 `e06448212adacb48ec97fd09b48c4ef955e6ddcd9c00e06a46d2d5038d4c5a23`。选定全部首轮a，公开voice实体一致；句级时序不是逐字ASR。初始独立声音信号检查-16LUFS、约-2.20024dBTP，24句PCM及间隙通过；这不作为语义或完整人工听辨结论。

作者真实时序动态输入、修前失败及定向修后样本保存在qa-self。正式冻结/全片编码只由根在独立动态与图文闸门完成后授权；本README为编码输入，后续状态记录到批次归档，不为更新进度改写已冻结输入。

```bash
export PATH=/workspace/.venvs/video-studio/bin:$PATH
python3 assemble.py
python3 fonts.py --verify
node check-references.mjs --sources "$PWD"
python3 verify.py
```

首次字体账本使用`python3 fonts.py`，既有账本只读`--verify`；覆盖依赖、字体与原题证据全部纳入实际清单。根确认`freeze-inputs.json`及全部写入停止后才运行：

```bash
python3 freeze.py
python3 freeze.py --verify
bash render-final.sh
python3 verify.py --final
```

默认渲染包含资料页，不能交付`remotion/out/body.mp4`。预期正文4466+资料150=4616帧，最终以实际回执为准。文章图位要在编码前绑定实际整数帧，编码后从最终video.mp4取对应JPEG并核对；最终截图、全部资料首中末、原生播放器/字幕/全屏及线上完整SHA属于另行成片与网站验收，不在此预记通过。
