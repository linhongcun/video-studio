// Lookup table so storyboard map points may name a city instead of giving lon/lat.
// Values are approximate city-centre coordinates (degrees, WGS84). Storyboard lon/lat always wins.
export const CITIES: Record<string, {lon: number; lat: number}> = {
  上海: {lon: 121.47, lat: 31.23}, 北京: {lon: 116.40, lat: 39.90}, 杭州: {lon: 120.16, lat: 30.27}, 南京: {lon: 118.80, lat: 32.06},
  苏州: {lon: 120.59, lat: 31.30}, 广州: {lon: 113.26, lat: 23.13}, 深圳: {lon: 114.06, lat: 22.54}, 香港: {lon: 114.17, lat: 22.32},
  东京: {lon: 139.69, lat: 35.69}, 首尔: {lon: 126.98, lat: 37.57}, 新加坡: {lon: 103.82, lat: 1.35}, 孟买: {lon: 72.88, lat: 19.08},
  迪拜: {lon: 55.27, lat: 25.20}, 悉尼: {lon: 151.21, lat: -33.87}, 伦敦: {lon: -0.13, lat: 51.51}, 法兰克福: {lon: 8.68, lat: 50.11},
  巴黎: {lon: 2.35, lat: 48.86}, 约翰内斯堡: {lon: 28.05, lat: -26.20}, 圣保罗: {lon: -46.63, lat: -23.55}, 纽约: {lon: -74.01, lat: 40.71},
  芝加哥: {lon: -87.63, lat: 41.88}, 达拉斯: {lon: -96.80, lat: 32.78}, 洛杉矶: {lon: -118.24, lat: 34.05}, 旧金山: {lon: -122.42, lat: 37.77},
  西雅图: {lon: -122.33, lat: 47.61},
  // 脚本口径：「服务器在美国西海岸」，出处为 WonderNetwork Shanghai → Los Angeles，故取洛杉矶坐标。
  美国西海岸: {lon: -118.24, lat: 34.05},
};
