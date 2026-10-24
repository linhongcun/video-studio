# 历史品牌参数兼容

`spec.json` 保留旧版片尾帧数参数，供站点时长回退和帧数检查使用。它不要求当前制作工程额外追加 60 帧片尾；实际帧数以每期 `meta.json.finalVideoFrames`、冻结分镜和渲染结果为准。

当前水印和结尾由各期 `episodes-codex/<slug>/remotion/src/` 实现，制作规则见 [现行规范](../../../docs/RULES.md)。旧共享品牌组件及其字体子集已随旧动画工程移除；历史参数说明可在 [清理前版本](https://github.com/linhongcun/video-studio/blob/686473df4fe89f6083a2386a8631d5dc32f4c04a/episodes/_shared/branding/spec.md) 查阅。
