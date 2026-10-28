# MySQL四期正文独立预检

日期：2026-10-28T13:00:57+08:00；执行者：独立代理 `/root/mysql_content_audit`。结论：**通过，可进入冻结与正式编码**。

当前基线HEAD为 `d7a5d7682080232617a03cc988b7c25cb50446f4`，新视觉源和当前产物尚未构成已发布candidate。下列实际源码/报告/PNG SHA绑定本次审查范围。此前只提供过MySQL内容边界建议，未实现本轮UI、共享Frame/theme/identity或预检器；本审没有渲染、安装或改动生产文件。

## 源码范围与不变部分

逐文件读取四期`remotion/src/mysql-style/`与原`src/`的diff，并读共享`_shared/mysql-video/{Frame.tsx,theme.ts,identity.ts}`：差异限于MySQL系列头、静态背景、配色、数据库身份符号、相对导入与新Main-only入口；索引定位说明改为“逻辑定位信息→对应订单记录”，锁SQL处增加显式事务/主键精确查找已存在记录的文字前提。

索引新增可选字幕隐藏props，但正式入口默认showSubtitles=true/hideSubtitles=false，字幕内容与时间判断保持；删除的底部装饰进度线不参与教学机制，其余教学动作公式和逻辑未改变。事务OtherScenes/MotionParts仅调整数据与身份组件导入，事务/复制Scene教学分支原样；锁只追加随既有SQL相同fade入场的范围文字。所有四期继续读取原data、分镜与模型，没有复制或改写算法/时序。

只读比较50份原src及script/storyboard/words/旧source-sha256/references文件，均与当前HEAD逐字节相同。新identity保留原已许可MySQL图像数据，只在静态圆柱中采用同一系列色。

## 索引11镜的有界修正

初次42帧报告保留failed身份：11镜f2764/f2899/f3029两个说明行各距字幕2px，合计6项间距违规。当前源码只在id===11中将两表y398→378、两Subhead y883→868；在内存中精确反向恢复这四处后，其完整SHA严格等于初次采样记录的Main.tsx SHA。其余所有初次采样输入仍与当前字节相同，修正没有越出11镜，因此原索引39个其他帧可有界复用。

修后三个相同全局帧实际重新查看，qa-report为passed、0违规且全部输入SHA当前；说明行CSS包络底908、字幕从925开始，间距17px，索引表上移后说明与表也分开。没有通过放宽规则追认旧失败图。有效范围是其他三期132帧 + 索引39未改帧 + 索引3修后帧 = **174个唯一有效帧**；实际渲染177次采样，其中3张旧失败图继续作历史证据。

## 实际图像审查

本审逐张打开20张PNG：四期首/中/末，索引11修后3点，事务提交及应用回滚中态，锁08新SQL前提，复制接收/应用及新查询主库。墨绿底、薄荷重点、暖白字、圆柱/MySQL标识与已独立审过的现行MySQL封面同家族；未见文字裁切、标题/范围或字幕遮挡。金色待确认/操作、薄荷确认、蓝色请求与珊瑚失败语义保持。

索引明确MySQL8.4/InnoDB与结构示意/非性能实测；事务保留同库教学而非真实支付、待确认与已确认区分；锁明确显式事务内对已存在主键记录加锁读取；复制明确MySQL8.4单主异步，保留“接收后还需应用”及“新查询定向同一已提交主库”的前提。通用“数据库”名词仍用于对象/逻辑范围，不被误当跨产品承诺。

四份原报告中的browserWarnings/browserErrors/bundleErrors/missingAudits/auditParseErrors均为0；每份两条webpack asset/entry体积提示不影响本次离线渲染。索引旧违规只通过上述三帧重采修正，其他三份原报告均passed/0违规。

| 剧集 | 全局帧 / 镜号 | 实际查看PNG SHA-256 |
|---|---|---|
| db-index (preflight) | 0 / 01 | `5b5a60ec67ad6d124d160f951add6d5a2f5d58e0ae50b4c659393c5f5c9e599f` |
| db-index (preflight) | 1952 / 08 | `7db26a348b71fd5c46710bc64c03e12822880d6783bcb374611de5166a267088` |
| db-index (preflight) | 3918 / 14 | `927b9ea8f672584c551d6cce7d21825e691c05e444c6b078177d5b9c02e664aa` |
| db-transaction (preflight) | 0 / 01 | `89ea39ff55793f903102e8d35eca84376e7a2a815384b6c734b65d61aa83fcb6` |
| db-transaction (preflight) | 1863 / 09 | `5601473ae3087b20776cb61b8d05a61a1bb95a1d4d03dcd166aac08bea7a1197` |
| db-transaction (preflight) | 2003 / 09 | `6784f167ca97acc4fbec2b94541cd2bc25a493564eadd065d31ca920a6334abc` |
| db-transaction (preflight) | 2569 / 11 | `d8426dbda85a41284f023e1642813819c5a8096f9e197a2537a4b9c2e9a02d5b` |
| db-transaction (preflight) | 4060 / 16 | `a3f1b465df40c7dd9b681c094a74001a4020ca3e2fb7bf5f674eec41ffa4c2e8` |
| db-lock (preflight) | 0 / 01 | `80efbea8ee1d0f384ffca6f40f49dcbe9d77f4e74f3eddf0bb9edc240ec8159f` |
| db-lock (preflight) | 1675 / 08 | `37e1048faef009e2fd70d46a077e34d8c0a783d1d2f3494090d709f5cea2190a` |
| db-lock (preflight) | 1806 / 08 | `bb5ba9a0c2b2812906efc04c2a02b8c383d91996b599bc3117c9f624b7b8340d` |
| db-lock (preflight) | 3452 / 14 | `e30a8c47a49193464b2785f787fb23db2f9a9e2e23d3dee044fc15d67c3aa546` |
| db-replication (preflight) | 0 / 01 | `c8370ea336f826fc6c5a129e39d5db0f3b54112fba50e6ff49de3d4a0a7816ed` |
| db-replication (preflight) | 1683 / 08 | `56dfc07d66398417090bb30c717ffab01193f483894a9274fb5541daa24c3f4e` |
| db-replication (preflight) | 2285 / 10 | `ddd4a7cf0029062de0e74ee7241263343b2b7df7c708f169e61493573f43cd8e` |
| db-replication (preflight) | 2859 / 12 | `37c44dbb00a2e76329eae9cddfcc7eb5a8fdeb93e9c25b9d1181a53393abe7ef` |
| db-replication (preflight) | 3554 / 14 | `6d92ac077a6ff855ee7d50a9230840892873f6f7f9a4ed42c34117910e0b4c1f` |
| db-index (preflight-corrected) | 2764 / 11 | `1b091b74e95766328d378db53f262ac48aab385d9a5732e9b4c34b7fd4ab77d2` |
| db-index (preflight-corrected) | 2899 / 11 | `ede69e527d179dc2e0adc5e97431c4ee7853bc89cd7fdbbfe5719bb2bb1c494c` |
| db-index (preflight-corrected) | 3029 / 11 | `4a2e21bd0c3ad67ea7bfaef51b250f899091e183907143494477a6101ab47470` |

## 报告及当前源码身份

| 报告 | SHA-256 |
|---|---|
| work/mysql-video-style/preflight/db-index/qa-report.json | `ef95d46cd138a96c85f45a57c4dfdcfb3e7a7838c7622b790ec390e04eeab663` |
| work/mysql-video-style/preflight/db-transaction/qa-report.json | `c987024e109078321589cd9d48bc46fd423e46435c5bd8a70a14592df803f960` |
| work/mysql-video-style/preflight/db-lock/qa-report.json | `bdd4ce5a7f0f4d632536fe358e8ee3692a0a65bde20f212977206fdcbef9c1c0` |
| work/mysql-video-style/preflight/db-replication/qa-report.json | `3b311d0de29c90b4d730338dcade3c50bb2e1e90031646ccff5c90d7b55c1ece` |
| work/mysql-video-style/preflight-corrected/db-index/qa-report.json | `0e461ed07f24aa701ffa73b2382b444457ca110104f19b5e9b2ffbe3e6fd8bd0` |

当前新视觉源及共享UI（审查后未再写入）:

| 文件 | SHA-256 |
|---|---|
| episodes-codex/db-index/remotion/src/mysql-style/Main.tsx | `7126b8545087a170ea2b4902dceb90d22a69ed8db7f4ab3bda2795111e6575a7` |
| episodes-codex/db-index/remotion/src/mysql-style/Root.tsx | `563442a7159d17493e2152913956f245e29777e4d247066974282eca349b87cb` |
| episodes-codex/db-index/remotion/src/mysql-style/index.ts | `f9bc4e836a064aca9c58a681e1dc779b62a4d82894450e8e15d5cdd05840e36e` |
| episodes-codex/db-index/remotion/src/mysql-style/theme.ts | `8b376027d8ee480f8852cb0bea070fbe78a17e0ef8e3e8c60c65ce628552db44` |
| episodes-codex/db-transaction/remotion/src/mysql-style/Main.tsx | `fb17cc64472201c7572b69abd60fdc538b4e71d76ca104fd9a5354b5f4fc1102` |
| episodes-codex/db-transaction/remotion/src/mysql-style/MotionParts.tsx | `cba1cec58673259481cb4e4cad8a8d4000105b2fb3d84b4d2b82ec8564769050` |
| episodes-codex/db-transaction/remotion/src/mysql-style/OtherScenes.tsx | `294515a1f044cdee20916b7cbb89b466d2b34f4a19298887dc6de44f3429569f` |
| episodes-codex/db-transaction/remotion/src/mysql-style/Root.tsx | `563442a7159d17493e2152913956f245e29777e4d247066974282eca349b87cb` |
| episodes-codex/db-transaction/remotion/src/mysql-style/index.ts | `f9bc4e836a064aca9c58a681e1dc779b62a4d82894450e8e15d5cdd05840e36e` |
| episodes-codex/db-transaction/remotion/src/mysql-style/theme.ts | `8b376027d8ee480f8852cb0bea070fbe78a17e0ef8e3e8c60c65ce628552db44` |
| episodes-codex/db-lock/remotion/src/mysql-style/Main.tsx | `02fa78b7fb1bf205afb3b14d7a79cc7eecdb6f5ae559516e2d19e0476f85d4ea` |
| episodes-codex/db-lock/remotion/src/mysql-style/Root.tsx | `ed65482ff872c9c8fb20202b26d8dc49a5eaa76dd9009f13a83b8ef392663c95` |
| episodes-codex/db-lock/remotion/src/mysql-style/index.ts | `f9bc4e836a064aca9c58a681e1dc779b62a4d82894450e8e15d5cdd05840e36e` |
| episodes-codex/db-lock/remotion/src/mysql-style/theme.ts | `8b376027d8ee480f8852cb0bea070fbe78a17e0ef8e3e8c60c65ce628552db44` |
| episodes-codex/db-replication/remotion/src/mysql-style/Main.tsx | `11711232174c6f7439335e7e20a423cfb50c283cc9683c7fae2f2171639a45d0` |
| episodes-codex/db-replication/remotion/src/mysql-style/Root.tsx | `ed65482ff872c9c8fb20202b26d8dc49a5eaa76dd9009f13a83b8ef392663c95` |
| episodes-codex/db-replication/remotion/src/mysql-style/index.ts | `f9bc4e836a064aca9c58a681e1dc779b62a4d82894450e8e15d5cdd05840e36e` |
| episodes-codex/db-replication/remotion/src/mysql-style/theme.ts | `8b376027d8ee480f8852cb0bea070fbe78a17e0ef8e3e8c60c65ce628552db44` |
| episodes-codex/_shared/mysql-video/Frame.tsx | `4d57767217481f39dcb15f7b60c687f2a5d428ee374e612f0f66c2ba4c337bbe` |
| episodes-codex/_shared/mysql-video/theme.ts | `1065c6391daab3fca8fedf1890941fe96cb68d156785ff0b3ad6252d574098e4` |
| episodes-codex/_shared/mysql-video/identity.ts | `adeeb1f4e8b2543e08bac17b7afabbcb98f9d8f398d4308a5694961696126c50` |
| episodes-codex/_shared/mysql-covers/catalog.json | `43f613b6024fa9956c2f2be758a9c468cfa2a19d545854f0b5648bd5a6d48e67` |

本结论是源码和静帧预检，不声称本审运行过TypeScript测试、连续审看全片动画、人工听辨、逐字ASR、验证正式MP4/音轨、资料附录或站点/真机/线上播放。正式编码后仍须按真实媒体与站点记录分别检查；不预记用户已认可新版。
