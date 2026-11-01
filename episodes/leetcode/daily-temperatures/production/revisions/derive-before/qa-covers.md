# Daily temperatures 独立封面复验

结论：**PASS。** 新增poster.jpg已实际打开，1080×1440，标题、LC.739水印、五个日期/气温、等4天括号与说明均完整可读。它与已通过独立实际查看的cover-3x4.jpg逐字节一致，完整SHA均为`3d3856cdee62a94700ee1a195c8329e2e289bfafe6f8150b97c38e1561bf7d54`。root通过字节复制补齐既有声明，没有重渲六张封面，也未改covers.json或Cover.tsx。

原“声明poster.jpg不存在”的BLOCK记录保留在revisions/missing-poster-before/qa-covers.md/json，未覆盖。归档JSON SHA：`149e8048d42eedc180eb24c385fb0fdbfe6985d273c6ea7e4aa088d2e445fb23`；归档Markdown SHA：`20736694b19985cdc72b430017be3d590e06173afd8dd28ab88a291b305620af`。本次只定向解除该项阻断。

六张PNG/JPG的完整SHA与首次逐份实际打开时完全相同，复用原视觉结论：第3/4/5/6/7天温度35/31/30/32/36，第7天才首次超过第3天的35，等待7−3=4天。标题、系列文字、水印和图表无裁切或遮挡；4:3两张主体高亮像素范围x346..1080、y149..864，处于x315..1125且y<918。像素测量排除了既定右上水印带，并与实际图像观察结合；没有通过重渲或重做算法补证据。

网站episodes/daily-temperatures/meta.json的poster字段仍明确为cover-16x9.jpg，选择横版封面；制作covers.json另外声明3:4的poster.jpg。二者用途和选择均明确。本次核对元数据与制作资产，不声称站点已经部署或线上媒体已核验。

| 文件 | 实际尺寸 | 完整SHA-256 |
| --- | --- | --- |
| cover-16x9.png | 1920×1080 | `1df2f9e1c91ea49f022ebc408f745b38a534672d455ac9423fef01619c87797a` |
| cover-16x9.jpg | 1920×1080 | `93a4d8be2a855b8dd3eaee04ddff90f0896a39245d10571a83d77ea4e5283947` |
| cover-4x3.png | 1440×1080 | `034697cd70eec43092751f07e6f51af036af29321a5826066c33bfa9e126d926` |
| cover-4x3.jpg | 1440×1080 | `25fa5eff2c622e396aad90bf7ae00373cce2edba717b15df1226148d21073fd0` |
| cover-3x4.png | 1080×1440 | `22eb4a12befe149ad70ea367ee79958d663fd1c59170b819c6763aa994fc9920` |
| cover-3x4.jpg | 1080×1440 | `3d3856cdee62a94700ee1a195c8329e2e289bfafe6f8150b97c38e1561bf7d54` |
| poster.jpg | 1080×1440 | `3d3856cdee62a94700ee1a195c8329e2e289bfafe6f8150b97c38e1561bf7d54` |

当前封面输入身份：

- covers.json：`26ce9fa91e844721f7a7f7512eb3140eb12e1a99ce2c99788b227976c340ce0a`
- remotion/src/Cover.tsx：`31bb148425d50ae93fcbb1fcd4a34d46bd820b4d70f17378dbe702e7abcf92b6`

首次封面审查曾对当时145项冻结清单逐项核对通过，旧清单SHA为`edfb304fb8a2a309e6e36fe3a35d71df36912f877aece9b7b72f5476a5a7ef21`；这是历史身份记录。制作代理目前修改动画Main，本次封面复验只绑定上述未变的封面输入、六张封面和新增海报，不把旧全Main清单称为新冻结或当前动画已验收。

边界：本次只实际重开新增海报，六张封面按完整SHA复用先前实际观察；未重渲、TTS、检查声源或算法，也未检查成片动态、ASR、全听、站点或发布。
