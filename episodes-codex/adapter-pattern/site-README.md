# D03站点接入与核验

本期只发布检查通过的`adapter-pattern`。内部EP和标题读取当前`episode-config.json`；lessonOrder为3，源码指向当前制作目录。首发版本由根任务在最终同步主干、核对tag后宣布，脚本不写死计划版本。发布日期默认执行接入时的北京时间日期；跨日发布时根任务用实际首发日传`--published-at`。

媒体仍在制作时只准备工具，不复制MP4、伪填时长或构建页面。正式媒体通过后：

1. `python3 episodes-codex/adapter-pattern/site-integrate.py --approved --release vX.Y.Z`：复制同SHA成片、三JPG、原生SVG文章、脚本/分镜/字幕/调研/发音及当前source/render/mix报告；不复制WAV、PNG或制作源码。D01/D02元数据和核心文件在接入前后逐字节保持。
2. `node episodes-codex/adapter-pattern/site-qa.cjs`：当前稳定树上一次生产build、一次当前历史路径回归；1440浅色/390深色全部章节实际跳转及短静音播放、24句字幕文字/时序、无溢出、原生SVG computed字号/锚点/文字范围、#java与完整Java源链接。Java卡150帧，首中尾三个时间点必须是完整载入且showing的字幕轨、0活动cue；真实解码后暂停并导出卡帧。播放器截图恢复字幕默认状态。
3. 同一构建核对D01→D02→D03目录、D02前后课、D01/D02原数据、首页/资料库/RSS及已撤下Agent状态；发布页总数从当前元数据读取，不把旧数量写成固定要求。实际打开截图后单独记录准确查看范围。
4. 只有浏览器阶段需要恢复且输入/构建产物指纹均未变时，可`--reuse-build`。不同版本已有通过报告时应先明确归档旧候选，不能覆盖后把新图当旧证据。
5. Release之后Pages工作流成功，再运行`python3 episodes-codex/adapter-pattern/site-verify-online.py`：11个普通canonical GET，完整视频流SHA而不保存远端媒体；海报/VTT/章节、Java及源码入口、D01/D02更新后的目录、系列/资料库/RSS/真实Release条目，继续核对已撤下Agent入口不恢复。

本地浏览器的短静音播放不代表全片听辨、ASR、用户认可或学习效果测量。未执行的检查不预填通过。构建日志保存原始gzip和只清尾空格的可读副本。

候选首发冲突时，先从已提交候选精确归档旧QA输出/路径/SHA和旧meta。只有根任务明确确认尚未发布的新D03，可传`--replace-unpublished-candidate <旧候选版本>`受控替换首发身份；不用于已发布课程的改版。Agent系列按当前真实已发布内容检查，允许新Skills，继续排除已退两期，不机械要求Agent系列为空。
