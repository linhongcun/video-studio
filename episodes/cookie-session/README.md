# EP.04《网站怎么记住你已经登录？》分镜（Miyazaki）

- storyboard.json：11 个镜头，3603 帧 @30fps（Knoll 实测 3423 + extraHold 180，provisionalTiming=false；封面 set-cookie-1 局部 526 = 全局 1181；EP.01 复用画面在 recap-2，全局起点 3345）
- extraHold（Nolan 批准，纯画面停留、配音不动，写在 map_timing.py 的 HOLDS，进 timing.json 的 duration，gen.py 不再叠加）：set-cookie-1 holdAt 341 +45（第二句说完、手牌已落进浏览器框）；session-2 末尾 +45；protect-2 末尾 +45；recap-2 末尾 +45。插入点后的句子与后续镜头顺延，validate.py 校验每句起点 = Knoll + 累计 hold
- Nolan 审定后修改：set-cookie 合并为一个镜头 set-cookie-1；手牌飞进浏览器框、Cookie 标在框内；recap-2 加「接第一期」小字 + EP.01 connect-1@220 占位
- timing.json / timing.provisional.json：make_timing.py 生成，按第三期 MiMo 冰糖实测校准（557 字→3937 帧）
- 配音到了以后：把 Knoll 的 timing（每章一个镜头，键 stateless-1…recap-1）存为 timing.mimo.json → `python3 map_timing.py && python3 gen.py && python3 validate.py`
- common_split.py：章节 id 与按句拆分（stateless 3+2、set-cookie 3、send 2+2、session 2+2、protect 2+1、recap 1+1）
- gen_assets.py → assets/：tag.svg（手牌，id body/hole/numArea/numBars/string）、locker.svg（存包柜，id frame/cell*/openCell/bag/openDoor）、thief.svg（小偷，沿用第二期 eavesdropper 剪影，id figure/mask/eyes/hand）。都没有文字。
- frame.py：预览检查帧 `SB=$PWD/ python3 frame.py <shot>:<frame>` → check-<shot>-<frame>.png
- 复用：浏览器/服务器统一卡片（无窗口圆点、标签 36px）、箭头 drawProgress、字幕层。手牌跟着请求移动：image 的 x 关键帧
