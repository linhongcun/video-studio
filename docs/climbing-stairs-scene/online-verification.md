# LC.70 楼梯场景返工：线上核验

实际检查：2026-10-25T02:59:13.578761+00:00。显式修订 v0.61.1，结果通过；实际[手动部署](https://github.com/linhongcun/video-studio/actions/runs/40156242220)的 head 为 `3da47c21c3daa512826093670333e4029501ebd1`，与本次附注标签身份核对，没有用后来 main 的 package 版本替代。

LC.70 完整视频/海报与正式制作、canonical和标签完整SHA一致；4779帧，原24句文字及帧时保留，四章、源码、完整Python、原生控件和5秒无cue静卡均通过。首页算法方向经学习入口可达系列和资料库，RSS正确；该补丁自身更新日志仅关联LC.70。

其余canonical与基线 `4a00d8a0f84b0d20eb1a87fbd6fb87a6b870a6f0` 保持；五条其他LeetCode逐文件完整SHA及其线上视频/海报一致。撤下的两期Agent页面/视频/海报/字幕仍为404。本次完成 28 次完整HTTPS响应读取、57055342 字节。

机器记录见[online-verification.json](online-verification.json)，部署记录见[deployment.json](deployment.json)，每次真实运行的成功/失败及到达阶段见[attempts](online-verification-attempts.json)。本记录不声称全片听辨、ASR、用户认可或学习效果；实际本地播放器交互和截图范围另见qa-site。
