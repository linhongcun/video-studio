# TCC：制作说明

2026-10-24。真实配音3618帧、120.6秒；14镜28句，5章。分镜000a9b63，voice 2063df3b，words 616766e6。本期首次新增，冻结由root统一执行，不自行开始全片编码。

## 主体和数量

全片同一示例订单8124/商品7042，购买1件。除开场明示错误直接售出外，正确基线4/0/0，预留3/1/0，确认3/0/1；取消分支明确从4/0/0重演，预留后释放回4/0/0。数量槽固定x430/960/1490，字面标签可用/本单预留/正式售出，字号29；主数124，单件数量标记从来源退出后沿弧线移动，落点后提交新数，避免两个同一件。

## 布局与节奏

标题x130/y190，字号46；上下文/重置提示y280，字号23；请求与决定带y315..385，避开数量标签y429。数量y470，条形单位y674；操作状态y735。说明线y806、说明字y832，字号29；字幕y925，字号38。右上品牌和示例数据分开。全部干净深色canvas，无物理设备、假窗口或浏览器。

预留镜04的资源变化与操作记录同一帧保存，局部本地事务边界同包；不是数改完才另写操作标记。确认/取消均以同一业务操作号引用有效预留，二者不在一个未重置分支顺序执行。08/12重复请求有沿路径移动的请求，值不再改变，不能只靠说明文字表示请求抵达。

## 时序动作

- problem：绝对起点0帧。
- reserve：绝对起点492帧。
- confirm：绝对起点1214帧。
- cancel：绝对起点1950帧。
- boundary：绝对起点2992帧。
- 镜01 hook：from 0，duration 242；order-refused@local 145/global 145。
- 镜02 tcc-intro：from 242，duration 250；按真实句级区间安排渐进揭示。
- 镜03 initial：from 492，duration 226；按真实句级区间安排渐进揭示。
- 镜04 reserve-save：from 718，duration 270；reservation-committed@local 95/global 813；local-save-explained@local 172/global 890。
- 镜05 reserved-is-owned：from 988，duration 226；按真实句级区间安排渐进揭示。
- 镜06 decide-confirm：from 1214，duration 236；confirm-decision-durable@local 153/global 1367。
- 镜07 confirm-apply：from 1450，duration 274；reservation-to-sale-committed@local 76/global 1526。
- 镜08 confirm-retry：from 1724，duration 226；reply-lost@local 37/global 1761；same-confirm-arrives@local 137/global 1861；confirmed-no-extra-effect@local 174/global 1898。
- 镜09 cancel-reset：from 1950，duration 245；second-branch-reservation@local 164/global 2114；other-side-refused@local 200/global 2150。
- 镜10 decide-cancel：from 2195，duration 272；cancel-decision-durable@local 66/global 2261。
- 镜11 cancel-apply：from 2467，duration 268；reservation-released-committed@local 80/global 2547。
- 镜12 cancel-retry：from 2735，duration 257；same-cancel-arrives@local 95/global 2830；cancelled-no-extra-effect@local 191/global 2926。
- 镜13 boundary：from 2992，duration 288；按真实句级区间安排渐进揭示。
- 镜14 recap：from 3280，duration 338；show-confirm-outcome@local 92/global 3372；switch-to-separate-cancel-outcome@local 149/global 3429。

## 封面与起音

主标题先预留/再确认，副标题留住一件，失败怎样放回；三数量3/1/0为示例，构图与正片统一。三尺寸，4:3核心x315..1125，末文y859+45=904<918；poster与3:4 JPEG逐字节相同。首现TCC在镜02句首，字幕保留TCC，送模T C C，严格声学起音0失败、无例外。其他英文接口名留文章不在正片堆名词。

## 复核范围

真实多阶段/相邻帧与无字幕连续片先检查，再统一停写freeze。计数与状态看点由同一motion.ts导出events，预演脚本记录Main等完整SHA。最终MP4仍需实际解码、媒体格式/响度与编码抽帧核对；本说明不把预演当成成片审，也不冒称ASR或全片听辨。

## 导航修订补充（2026-10-24）

旧v0.47局部布局与事件记录保留作对照；本轮采用共享branch-map将预留→决策→确认/释放放进同一张真实业务图，配置在remotion/src/branch-map.ts，运镜和互斥/回看说明见navigation.md。原3618帧、声轨、字幕、业务事实均不变。07确认单件移动由旧9→76平移为34→99（global1484→1549），11释放由旧9→80平移为35→103（global2502→2570），让相机在30帧结束后完整展示数量动作；新正式QA以这两个落点99/103为准。
