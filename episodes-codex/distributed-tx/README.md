# EP.21《下单成功了，库存怎么没扣？》

按用户批量重制与自主GitHub发布授权完成本期，对应[#73](https://github.com/linhongcun/video-studio/issues/73)。只讲可靠消息一条线：同库保存订单和待发事件、恢复重试、库存侧同事务扣减及记录已处理、重复不多扣、最终一致及失败边界。站点接入与发布由主任务统一完成。

- research.md为五份原始/官方资料实际阅读记录与边界；article.mdx保留实现条件和片外补充。
- script.md为14镜28句旁白；pronunciation.md列出多音字。visual-direction.md和knoll-props.md说明连续动作。
- storyboard.json与sha8副本为冻结时序，words.json为实测TTS句界/共享句首起音兼容格式，不是逐字ASR。
- video.mp4为成片，三尺寸JPG/PNG为封面，source-sha256.json记录实际输入，render-result.json和mix-report.json记录实际媒体检查。
- qa-motion.md与qa-final.md写明实际检查范围，不将多阶段截图或机器通过冒称完整人工审片/听辨。

重现：从仓根用共享voice/prep.py、gen.py、build.py加--dir episodes-codex/distributed-tx，再运行本期assemble.py；随后共享selfcheck.py、place_v2.py --mode whole及label_onset_strict.py。保留选定takes避免重新请求非确定性TTS。Python环境/workspace/.venvs/video-studio；TTS线程2，密钥仅环境变量。

进入remotion：npm ci、npx tsc --noEmit、npm run stills、npm run covers、npm run render。工作区node_modules软链不入库，独立安装用锁文件。需要FFmpeg、/usr/bin/chromium、Noto Sans CJK SC。完整渲染通过共享锁flock /tmp/video-studio-render.lock调度。

动态预演：node scripts/motion-qa.mjs /tmp/ep21-motion --shots=04,06,09,10,11,12 --flow=08-11。预演关闭字幕和声音，用于观察对象与状态，不能代替成片媒体检查。

配乐为仓库共享Kevin MacLeod《Wallpaper》，CC BY 4.0。混音目标−16 LUFS，真峰值上限−2 dBTP；实际值见报告。
