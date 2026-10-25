# EP.31 · D03适配器模式制作说明

2026-10-25（北京时间）。本期全新首发，12镜24句；正文5121帧、Java静卡150帧，最终5271帧/175.7秒，1920×1080/30fps。没有旧视频或旧配音复用。

依据：script `f55d8fa7997c549723cb41ef3c23a9e89cf0f807021570d0be78da8d8ed2adb4`；plan `95b41a121153dcc11959abc16bca9f5eb974e3d08fe57d83b990d6c2bb0d1a3f`；config `df46d127dd4946385983d332732d8ba4aa097ece1076d9f501e2e5c2aa89ac9f`；voice `1fe1778d945488b84d9c41f238df6a71bd9e35e6c0b3b303c8aefdebab441cb8`；words `938c391b65e37aa632845c0c6ab10eada26d60476215e31a2716e5f44ec5b3eb`；storyboard `2d76275e965f3a9b77621a125c42a9bfb40fde99d4c0f90ce4f71a77cefb40fb`；covers `c64980138a776119bacb2d6056d2c1eee7d8b02932db95487bf00d8954b7677a`。

## 同一业务与时间视角

01展示商家订单17详情，点击发送发货提醒，显示已受理、等待送达回执及Q17。02明确转接入前开发视角，03–04逐角色说明业务方、目标通知约定、适配器和它持有的服务；此时没有运行中的消息。05先说明回看，再透视01同一次提交，不能再次点击或发送另一条。

运行时请求直接由业务方到适配器，再由适配器真正调用服务；目标约定是依赖/实现关系，不能画成中转节点。buyer17@shop.example及“订单17已发货”在转换前后保持同一值和业务含义。服务交回已排队和Q17，适配器转换为已受理/Q17，08回到同一页面等待回执；不得变成已送达。09规则说明不改写Q17主线、不发第二条。

10保留目标约定/能力能对应的前提，以及创建/接线/配置仍需变化；11说明直接使用的适用前提和新增转换成本；12回收同一职责与结果，然后切入Java静卡。Java为关键节选/暂停阅读，不逐行教语法。

## 真实时序与画面入口

下表为全局帧；动作窗口由本期remotion/src/motion.ts按真实句界派生，不把角色名称当作逐字ASR时间。最后一镜动作以javaCardFrom作为正文上界，尾卡不拉长正文动作。

| 镜 | visualType | 全局from | 总帧数 | 第二句局部from |
|---|---|---:|---:|---:|
| 01 | product-reminder | 0 | 399 | 183 |
| 02 | incompatible-contracts | 399 | 411 | 134 |
| 03 | roles-and-target | 810 | 383 | 180 |
| 04 | introduce-adapter | 1193 | 473 | 226 |
| 05 | submit-through-target | 1666 | 412 | 187 |
| 06 | convert-and-delegate | 2078 | 426 | 188 |
| 07 | map-acceptance | 2504 | 385 | 191 |
| 08 | accepted-ui | 2889 | 347 | 155 |
| 09 | rejection-and-unknown | 3236 | 463 | 140 |
| 10 | maintenance-scope | 3699 | 420 | 126 |
| 11 | cost-and-simple-option | 4119 | 449 | 186 |
| 12 | idea-recap | 4568 | 703 | 238 |

只有04句首“适配器模式”为正式首现cue：全局1194，声学1194.72，差−0.72帧，至少63帧。其余结构/状态按句级stage及对应动作呈现，不伪造句内字词起音。

Main实际读取visualType、cueFrames、subtitles、durationInFrames/from与javaCardFrom；全轨Audio从0帧播放实体public/audio/voice.wav。通用elements坐标用于分镜声明/起音检查；程序化主体真实几何由components与Main实现。scriptVisual/direction/narration和timing.source是审读/来源信息，不作为另一路音轨或自动图形布局。

## Java尾卡与输入边界

末镜javaCardFrom=553为local；meta.javaEndCard.from=5121为global，duration=150。Voice尾240000样本全零，字幕止于正文；Main先判断尾卡并禁用旧header/字幕。卡来源demo-java与src/java-card.json由Java负责人编译/映射验证，不能把不完整节选说成完整可提交程序。

正文不可变副本在revisions/flow-ui-java/voiced-body，此默认路径不表示旧版返工。Java验证使用现有append_java_endcard.py verify；它临时重建真实正文供旧checker检查，不将final伪标Python卡。whole/strict对final仍用原共享实现。冻结前任何生产改动需重新验证，不能用新清单追认旧编码。

## 封面与页身

页身使用共享pageBg #0F172A与pageInk #E5E7EB；干净canvas，无假浏览器、类图墙或装饰进度条。产品交互页只展示本期提醒功能。正文品牌IT小村，末尾IT小村 · 原创；没有下期预告。

covers.json三比例与meta.covers逐字一致：

- 16x9：1920×1080，content x=130、w=1660；watermark x=130、y=100。
- 4x3：1440×1080，content x=315、w=810；watermark x=315、y=100。
- 3x4：1080×1440，content x=110、w=860；watermark x=110、y=110。

4:3中心安全区x315..1125，bottom15Y918；poster.jpg采用3:4。几何/文案以已定稿covers及Cover.tsx为准，实际COPYFIT与安全区仍须通过预演。

boxShots=[]、mapShots=[]、devtoolsShots=[]；nextEpisode缺省。本期讨论题：外部服务只返回已受理，适配器能把它变成已送达吗？转换和创建接线分别放在哪里？

## 检查与正式编码

本说明记录真实配音/时序装配完成，不预写动画、正式成片或上线通过。按当前package运行类型检查、真实无字幕连续小样和封面；重点看01→02时间视角、04契约不是中继、05同次提交、06转换后真委托、07保持编号与受理语义、08回同页及Java边界。QA events与实际motion同源仍须实际查看中间态。

写入者停写、独立预检闭合后调用本期freeze.py并只读verify，再用共享锁和短TMPDIR正式render。成片核对完整解码、帧数/响度、实际AAC全轨及24句/Wallpaper尾卡一致性与编码状态。无ASR或全片听辨时如实限制；站点和线上核验另记。
