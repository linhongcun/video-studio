# LC.704 制作说明

本期制作目录为`episodes-codex/binary-search/`。同一有序数组演示目标13找到、目标8不存在两条完整轨迹；题意前置、比较依据、排除和边界移动构成主线。真实语音和最终帧数来自共享句级装配，不以临时占位时间作为交付。

## 实际工程

Remotion入口`remotion/src/index.ts`，组合`Main`为1920×1080、30fps；总帧数由`storyboard.json`逐镜相加。`data.ts`只读分镜，`Main.tsx`绘制完整数组、指针、范围和比较，`CodeCard.tsx`读取`solution.json`，`Cover.tsx`绘制三尺寸封面。主题取共享`episodes/_shared/theme/pageTheme.ts`。无装饰进度条、模拟设备或无关应用外壳。

`remotion.config.ts`优先使用真实`../storyboard.json`；缺失时才使用`src/placeholders/storyboard.json`，后者只作未配音开发占位，不是生产时序。正式预演应使用共享装配生成的真实分镜；配音整轨实体副本位于`remotion/public/audio/voice.wav`。

## 时间与动作

每镜使用`cueFrames.sentences`两个实际句首划分动作窗口。首次“二分查找”出现帧从`cueFrames.labels`读取；没有句内字词的推测时间。比较、排除、移动的顺序与具体状态见`visual-direction.md`；末镜正文按`codeCardFrom`截定，不把静态代码卡长度挤入口播动画。

边界运动坐标允许平滑插值，数值状态始终是整数；运动中隐藏正在更新的下标文字，落定后才显示新值。候选范围为空时不绘制区间轮廓。左、右边界同一格时采用分层且错位的箭头，右边界折线路径绕开左标签。

正文只显示一行`while left <= right:`，完整Python卡独立显示150帧。完整程序接口、缩进、左右两分支和末尾`return -1`由同一显示源渲染。字体Noto Sans Mono，35px、40px行高；不滚动、不逐行高亮、没有残留正文字幕。

## 真实命令

在`remotion/`运行`./node_modules/.bin/tsc --noEmit`进行类型检查。`npm run stills -- OUTPUT`调用本期`scripts/qa.mjs`，可以用`QA_STORYBOARD`、`QA_FRAMES`、`QA_SHOTS`、`QA_FRACTIONS`和`QA_CLIPS`限定检查范围；无字幕动态小样由该真实脚本输出。`npm run covers`生成三个尺寸的PNG及JPG。`npm run render`先出`out/voice.mp4`，再调用共享混音脚本产出`../video.mp4`；两并发，Chromium路径`/usr/bin/chromium`。

配音沿用共享prep/gen/build、句级装配、whole铺轨及严格起音检查；本期不复制生成和起音算法。源冻结、正式媒体解码、响度及线上SHA以root制作报告为准。没有实际执行ASR或完整人工听辨时不得记作已完成。

## 预检重点

- 只看01–02能复述输入、升序且无重复、目标、下标从0，以及存在/不存在的返回值。
- 在05能从顺序解释排除0..3的依据；06/11比较文字先可读，动作随后发生。
- 10落定/11首镜仍然有候选下标4；两边界指针不穿字或重叠，11结束才成为左4右3。
- 07返回6，12返回-1，08的目标更换属于独立新示例。
- 复杂度规模示意不冒充实例轨迹；完整代码卡整屏、静态150帧，末return不截断。
- 4:3封面重要文字和示例位于x315..1125、y<918。

检查证据按实际产物另存；此说明不等于已通过成片复核或用户观看。
