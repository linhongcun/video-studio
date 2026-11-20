# LC.200 输入网格片头修订

仅改镜01（帧0–394）：先展示真实4×5输入，再在原位置演示第一行第一列的1变成陆地、第一行第三列的0变成海水，最后沿同一张地图说明四邻。保留已发布的旁白、混音、字幕、题意示例与DFS内容。未改EP.18。

同步基线 `821edd3b803fbee61f6537f785f71510b55146d9`。渲染程序使用原分镜时长/字幕、原轨迹输入和原LeetCode地图组件；不覆盖历史制作文件。帧395–499只为衔接下一原有IDR而将原画面重编码；之后保留全部原解码画面，含边界修订、完整Python卡与资料卡。原音轨完整流复制；不重新生成来源卡，也不将本轮视为新的出处调研。

## 重建

在仓库根运行，使用 `source-sha256.json` 绑定的字体、已安装 Pillow 的 Python 环境、Chrome for Testing 与 FFmpeg 7（需支持 `-fps_mode`、framemd5 和 libx264）：

```sh
ep=episodes/leetcode/number-of-islands
npm --prefix "$ep/production/remotion" ci
python "$ep/production/revisions/grid-opening/build.py" --out "$HOME/lc200-grid-opening" --browser /path/to/chrome
```

输出为带原音的完整候选片及18秒审阅片。脚本逐项比对基线与成片的帧时间、音轨、原有资料卡，并量化重编码衔接段的误差。站点只采用 `publication/video.mp4`；本PR不合并、不发布。

[独立编码预览复核](https://app.devin.ai/sessions/18687b4e7a9d4081853b3d2f4afdf6e1)：约2.0秒及3.6秒的海陆对应、5.5秒的同网格过渡、6.5–7.5秒的四邻和13.167秒切入原示例均通过；字幕可读，预览解码音频与基线相同。未做浏览器或线上播放验收。
