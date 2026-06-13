/**
 * 西安景点附近美食 Mock 数据集（V4 — 多城市兼容层）
 * ————————————————————————————————————————————————————————
 * V4 升级：本文件现在是 xianFoodGenerator + multiCityFoodData 的统一出口。
 *
 * 数据源路由逻辑：
 *   1. 西安 → xianFoodGenerator.js（307 条模板，1000+ 景点视图，数据最丰富）
 *   2. 其他 20 城 → multiCityFoodData.js（程序化生成，每城 60-100 条）
 *
 * 所有 API 保持向后兼容，旧代码无需修改即可运行。
 * 新代码可通过 getFoodsForCitySpot(city, spotName, location) 获取任意城市数据。
 */

import {
  generateRealFoodData,
  getFoodsBySpotName as _xianGetBySpotName,
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

import {
  generateCityFoodData,
  getFoodsForCitySpot,
  getAllFoodsForCity,
  getCuisineTypesForCity,
} from './multiCityFoodData.js'

import { getCityCuisineTags } from './cityCuisineConfig.js'

// 重新导出所有 V3 API（向后兼容）
export {
  generateRealFoodData,
  getFoodsByZone,
  getFoodsBySpot,
  getAllFoods,
  getAllCuisineTypes,
  getZoneSizes,
  getSpotSizes,
  getCategoryStats,
  getAllFoodViews,
  SPOTS,
  // ★ V4 新 API ★
  getFoodsForCitySpot,
  generateCityFoodData,
  getAllFoodsForCity,
  getCuisineTypesForCity,
  getCityCuisineTags,
}

/**
 * 根据景点名称获取该景点的美食（V4 增强版）
 * — 西安走原有生成器，其他城市走 multiCityFoodData
 *
 * @param {string} spotName - e.g. '华清宫', '故宫博物院', '春熙路'
 * @param {string} cityName - 可选，城市名称
 * @param {[number,number]} location - 可选，景点坐标 [lng, lat]
 * @returns {Array}
 */
export function getFoodsBySpotName(spotName, cityName = '', location = null) {
  // 西安数据优先走原有生成器
  if (!cityName || cityName === '西安' || cityName.includes('西安')) {
    const xianResult = _xianGetBySpotName(spotName)
    if (xianResult.length > 0) return xianResult
  }

  // 其他城市：走多城市生成器
  if (cityName) {
    return getFoodsForCitySpot(cityName, spotName, location)
  }

  return []
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
