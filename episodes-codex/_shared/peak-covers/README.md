# 高并发、高可用、高性能系列封面

固定深青蓝底、亮青、暖黄、白字和IT小村标识，使用真实EP编号与完整原问题区分限流、幂等、熔断和降级。顶部三线栅格是本模板自绘的抽象系列标识，不是产品Logo或具体系统拓扑。后续新增视频扩展catalog和对应机制图，不新造另一套风格或改变旧输入。

当前四片只统一封面，不改视频、声音、文章、元数据、日期或首发身份。catalog必须与全部已发布peak单集、真实EP、完整原题和meta.sourcePath精确相符，生产根由当前sourcePath定位，不能默认覆盖旧修订。

图义沿当前实际文章：限流采用容量2的教学额度，先扣再放行、无额度拒绝，不把令牌桶当并发上限；幂等使用同一支付7042和30元，重复请求复用已有结果，业务效果不增加；熔断暂停异常的可选运费险调用，库存等必要校验保留，不能承诺修好故障；降级展示商品7042的搜索199元未计红包，结算核验红包后确认179元，不跳过正确性校验。所有数值只表示本片教学示例。

背景图由图像生成工具制作，仅有无文字、无事实的边角装饰。文字、标识及机制图由确定SVG生成。style-v1保存固定配色与字体；新增题只扩目录/题图。8个实际仓内输入与2个实际Noto字体文件分别记录完整SHA，不冒称第三方品牌许可或真实压测。

尺寸为1920×1080、1080×1440和1440×1080。横版左文右图，竖版上文下图；4:3将完整竖版以0.75倍居中在x315..1125，重要内容底边y<918。逐份检查实际文字、图形和组间距；安全边界不保证每种原生播放器控件状态无遮挡。9份合成长文字/三位EP压力图只检查排版，不是未来选题或成片。

仓根运行，需要Node、Python Playwright/Pillow、系统Chromium与Noto Sans CJK SC：

```bash
python3 episodes-codex/_shared/peak-covers/render.py --out-dir /workspace/work/peak-cover-candidate
```

逐份查看真实三比例图后安装：

```bash
python3 episodes-codex/_shared/peak-covers/render.py --out-dir /workspace/work/peak-cover-candidate --install
```

安装再次核对输入、字体、全部SVG/PNG/JPG和meta绑定，先解析全部已跟踪冻结清单，目标不得与冻结输入相交。四片各向当前生产根安装6张PNG/JPG、3:4 JPG别名poster.jpg，向发布根安装3张JPG与同款poster.jpg，成对cover-style.json记录身份，共44图/8清单。站点meta.poster保持原cover-16x9.jpg，原covers.json和封面源码不改。README属于输入，发布状态另存任务归档，不在渲染后改写本文件。
