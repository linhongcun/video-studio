# EP.04《网站怎么记住你已经登录？》分镜（Miyazaki）

- storyboard.json：12 个镜头，3807 帧 @30fps（暂定时长，provisionalTiming=true）
- timing.json / timing.provisional.json：make_timing.py 生成，按第三期 MiMo 冰糖实测校准（557 字→3937 帧）
- 配音到了以后：把 Knoll 的 timing（每章一个镜头，键 stateless-1…recap-1）存为 timing.mimo.json → `python3 map_timing.py && python3 gen.py && python3 validate.py`
- common_split.py：章节 id 与按句拆分（stateless 3+2、set-cookie 1+2、send 2+2、session 2+2、protect 2+1、recap 1+1）
- gen_assets.py → assets/：tag.svg（手牌，id body/hole/numArea/numBars/string）、locker.svg（存包柜，id frame/cell*/openCell/bag/openDoor）、thief.svg（小偷，沿用第二期 eavesdropper 剪影，id figure/mask/eyes/hand）。都没有文字。
- frame.py：预览检查帧 `SB=$PWD/ python3 frame.py <shot>:<frame>` → check-<shot>-<frame>.png
- 复用：浏览器/服务器统一卡片（无窗口圆点、标签 36px）、箭头 drawProgress、字幕层。手牌跟着请求移动：image 的 x 关键帧
