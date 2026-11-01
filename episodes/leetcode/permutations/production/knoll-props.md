# LC.46 制作说明

本阶段为phase1文稿与源码，尚无音轨、静帧、视频或冻结。14镜28句4章，暂定5255帧约2分55秒，当前时序显式provisionalTiming/pendingAudio；真实音轨可能改变时长，正常语速与动作停留优先。

Main读取storyboard及lesson.json。solution.py是唯一执行源；research/verify_solution.py用独立itertools oracle验证1229例，并对原AST插入观察生成83事件。数值卡按相邻真实path快照连续移动；选择树只显示当前必要分叉，结果副本不会随撤销消失。无浏览器壳、DevTools、无关实物或装饰进度线。

待独立编辑/算法审闭合后再启动共享TTS、测起音、句级装配与prepare_code_endcard.py，接真实音轨后进行动态实看与封面安全区预检。未来媒体操作统一flock /tmp/video-studio-render.lock，短TMPDIR=/workspace/perms-tmp，Chromium=/usr/bin/chromium，Python=/workspace/.venvs/video-studio/bin/python。禁止把占位时序记为真实预检，不伪称ASR或全片人工听辨。

片尾由同源solution.json显示22行完整Python，固定36px、35px行距，最终150帧无旁白/正文字幕，供暂停。三封面由Cover组件产出，4:3所有关键内容落在x315..1125且y<918。

第一阶段验证记录：research/solution-verification.json；本地TypeScript检查后记录stage1.json。发布接入、冻结、实际媒体及线上检查由root后续统一安排，外部平台未授权。
