# EP.05 cdn-v1 · WorldMap 准备说明（Knoll，2026-10-20）

## 底图来源与许可
- 数据：Natural Earth 1:110m Physical Vectors · Land（`ne_110m_land`）
- 下载地址：https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson （2026-10-20 下载，sha256 前 8 位 `9e0729ee`，原件存 `data/ne_110m_land.geojson`）
- 许可：公有领域（Public Domain）。https://www.naturalearthdata.com/about/terms-of-use/ ；仓库 LICENSE.md：“All versions of Natural Earth raster + vector map data … are in the public domain.” 无需署名（可选署名：Made with Natural Earth）。
- 转换：`python3 scripts/build-land.py` → `public/assets/ne_110m_land.svg`（静态 SVG 资产）+ `src/components/worldLand.ts`（同一条 path，组件内联绘制以便按主题上色）。投影：等距圆柱（equirectangular），x = lon+180，y = 90−lat，1 单位 = 1 度。
- 注意：110m 精度在放大到约 20° 跨度以内（镜 8 上海一带）时海岸线较粗；如分镜要更细，可换 50m 数据，同一脚本即可。

## 组件
- `WorldMapPage`：全屏浏览器网页（与 cookie-v1 同一个 BrowserChrome、同一深色主题）＝ 页标题行 + 角标 + 地图。
- `WorldMap`：只有地图，填满所在元素框（用于商店页下半部分的小地图，镜 1/17/18）。
- 两者都已注册进 StoryboardComponent，分镜元素 `component: "WorldMapPage" | "WorldMap"` 即可；所有帧号都是镜内局部帧（与其他组件一致）。
- 预览：`npx remotion still src/index.ts MapGallery out.png --frame=70`（示例数据，不是分镜）。
- 分镜冻结前：`@storyboard` / `@covers` 自动解析到 `src/placeholders/*.json`；`../storyboard.json`、`../covers.json` 一出现即自动改用（remotion.config.ts 与 tsconfig paths）。

## 元素字段（分镜直接写这些字段；类型见 src/components/WorldMap.tsx）
- 公共：`id x y w h z appearFrame disappearFrame stateKeyframes`（同其他组件）
- WorldMapPage 额外：`url title showPadlock pageTitle pageTitleColor badges: string[]`
- 视图：`view {centerLon, centerLat, lonSpan}`（centerLon 同时是中央经线，默认 150＝太平洋居中）或 `viewKeyframes [{frame, centerLon, centerLat, lonSpan, easing?}]`（缩放按对数插值）
- `dots[]`：`id, lon/lat 或 city, label, labelPos(top|bottom|left|right), labelColor, labelSize, labelAppearFrame, color, size(px 半径,默认12), ring, appearFrame, appearFrames, disappearFrame, pulse, pulsePeriod(45), pulseStartFrame, pulseEndFrame, colorKeyframes[{frame,color,fadeFrames}], highlightFrame, dimFrame, dimOpacity, undimFrame`
- `lines[]`：`id, from, to`（dot id / CITIES 城市名 / {lon,lat}），`startFrame, drawFrames(20), color, width(4), dashed, bulge(0.18,向北弯), label, labelColor, labelSize, labelAt(0..1), labelDx, labelDy, labelAppearFrame, colorKeyframes, dimFrame, dimOpacity, disappearFrame, packets[]`
- `packets[]`（光点）：`startFrame, travelFrames(20), mode(go|return|roundtrip), repeat(1), everyFrames, color, size`
- `labels[]`：`id, text, at, dx, dy, anchor(center|left|right), appearFrame, disappearFrame, color, size, weight, background, strike, strikeFrame`
- 颜色可写主题名 primary/secondary/success/danger/accent/text/text2/muted 或 #hex。
