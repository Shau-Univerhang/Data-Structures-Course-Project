/**
 * 西安景点附近美食 Mock 数据集（V3 — 向后兼容包装器）
 * ————————————————————————————————————————————
 * 本文件现在是 xianFoodGenerator.js 的再导出包装器。
 *
 * V3 升级内容：
 *   - 12 个核心景点覆盖（华清宫、兵马俑、骊山、秦陵、回民街、钟楼、鼓楼、
 *     古城墙、永宁门、大雁塔、大唐不夜城、大唐芙蓉园）
 *   - 307 条独特商家模板 → 1,238 条景点级视图
 *   - 每个景点的每个菜系分类均 ≥ 10 条商家
 *   - 地址基于真实西安道路/商圈名称
 *   - 坐标基于 Haversine + 50-1500m 随机偏移
 *   - 全部数据由 generateRealFoodData() 确定性生成，无硬编码
 *
 * 向后兼容：
 *   所有 V2 的公开 API 保持不变，旧代码无需修改即可运行。
 */

import {
  generateRealFoodData,
  getFoodsBySpotName,
  getFoodsByZone,
  getFoodsBySpot,
  getAllFoods,
  getAllCuisineTypes,
  getZoneSizes,
  getSpotSizes,
  getCategoryStats,
  getAllFoodViews,
  SPOTS,
} from './xianFoodGenerator.js'

// 重新导出所有 API
export {
  generateRealFoodData,
  getFoodsBySpotName,
  getFoodsByZone,
  getFoodsBySpot,
  getAllFoods,
  getAllCuisineTypes,
  getZoneSizes,
  getSpotSizes,
  getCategoryStats,
  getAllFoodViews,
  SPOTS,
}

// ═══════════════════════════════════════════════════════════
// 向后兼容：V2 风格的 XIAN_FOOD_BY_ZONE 和 SPOT_ZONE_RULES
// ═══════════════════════════════════════════════════════════

/**
 * V2 兼容：按美食圈访问原始数据
 * @deprecated 推荐使用 getFoodsByZone() / getFoodsBySpotName()
 */
export const XIAN_FOOD_BY_ZONE = generateRealFoodData().byZone

/**
 * V2 兼容：景点→美食圈正则映射规则
 * @deprecated 推荐直接使用 getFoodsBySpotName()
 */
export const SPOT_ZONE_RULES = [
  { pattern: /华清|骊山|临潼|兵马俑|秦俑|秦陵/, zone: 'lintong' },
  { pattern: /回民|钟楼|鼓楼|莲湖|洒金桥|北院门|城墙|永宁|南门|碑林|西羊市|北广济/, zone: 'city_center' },
  { pattern: /大雁塔|曲江|大唐不夜城|大唐芙蓉园|慈恩|雁塔/, zone: 'dayanta' },
  { pattern: /西安|长安/, zone: 'city_center' },
]

/**
 * V2 兼容：根据景点名称解析所属美食圈
 * @deprecated 推荐直接使用 getFoodsBySpotName()
 */
export function resolveZone(spotName) {
  if (!spotName) return null
  for (const rule of SPOT_ZONE_RULES) {
    if (rule.pattern.test(spotName)) return rule.zone
  }
  return null
}

export default XIAN_FOOD_BY_ZONE
