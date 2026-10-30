# MQ07 measured-timing handoff

作者已停写Main/模型/文章/图位及生产输入；未freeze、未正式编码。独立跨审可fresh bundle。

- remotion/src/Main.tsx: `d16d892b416ce83689bed0dfb6cff15ad756dea974b6ba9d5a867b3c405c5fa0`
- model.json: `986d0c9c7bd35269e9debe02d2701caa732f89b98c7e0e41a0e51e6709d5da35`
- storyboard.json: `a26c7ac995ac0770eb17272ee7d9a2689b221fcae34622b1ad6c941197c8bb4e`
- voice.wav: `f4f478dcedbd17e10df0f50ed6ae5f724726f5f5ef580f99db4d4fcca49c2803`
- script.md: `2233c8413548fffbd929a57dd0cdec4318ddfb198e46777d981d196a161d5486`
- article-figure-plan.json: `45da3c013ed36cfadbec07276f9bddb3606fd3b276d324a0c6c7dd9879976e5d`

body6058，12镜24句；规范旁白SHA `be954468d143a8907bb9aab1bd07d66dd1bc11f5289b4b9b76648ba61eec148d`。

模型27态/246断言；只有twelve-empty输入成员顺序改变，排序后及其余26态同原模型；独立有界复核qa-editorial/model-sort-correction-independent.json。

实际自审：98PNG、5段真无字幕短窗1610帧；全部视频/AAC完整解码，162顺序解码时点实际打开联系图，四图及5张关键1080p PNG另逐张打开。默认Main字幕仍true，plain selectComposition.props和renderMedia inputProps均false/true。

| 变化 | 首个整数帧 |
| --- | ---: |
| sort-start | 944 |
| sort-ranked | 1013 |
| sort-ranked-visible | 1025 |
| quota-calculated | 1581 |
| assign-P0 | 1926 |
| assign-P1 | 2035 |
| new-arrivals | 2447 |
| fetch-request-start | 2843 |
| fetch-request-arrived | 2893 |
| fetch-response-start | 2910 |
| poll-position-advanced | 2994 |
| business-completed | 3562 |
| growth-step-2 | 3915 |
| growth-step-3 | 3967 |
| growth-step-4 | 4020 |
| growth-step-5 | 4072 |
| drain-step-1 | 5190 |
| drain-step-2 | 5212 |
| drain-step-3 | 5234 |
| drain-step-4 | 5256 |
| drain-step-5 | 5278 |
| drain-step-6 | 5300 |
| drain-step-7 | 5322 |
| drain-step-8 | 5344 |
| drain-step-9 | 5366 |
| drain-step-10 | 5388 |
| after-clear-next-input | 5446 |

四图：2250(assign-second)、3260(first-two-polled)、4320(growth-tick-5)、5418(drain-tick-10)。frame/30及MDX seekTo同步。

连续短窗：sort920–1065、assign1875–2085、fetch-poll2840–3130、business-growth3500–4105、drain5155–5510；全部在本目录，当前源身份不变，可有界复用实际解码时点，不冒充独立重渲。

重点：固定教学排序别名非真实clientId；先比较稳定分工再独立共同起点启动业务；Fetch来自本地分区/初始position0，响应后当前position1而业务done0；E01通知成功才done；五步包含首步；降流交替逐区min，清空后1进1完；片尾原创。

范围：作者自审非独立放行；预演非正式MP4/附录/成片审；无ASR或整轨语义听辨；真实20断言实验不验证教学速率或十二成员通知业务。
