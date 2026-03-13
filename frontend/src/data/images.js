/**
 * 邮游世界 - 城市和景点图片配置
 * 使用正确的Unsplash图片
 */

export const CITY_CONFIG = {
  // 城市头部图片
  header: {
    '北京': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=1200',
    '上海': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=1200',
    '西安': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=1200',
    '成都': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=1200',
    '杭州': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=1200',
    '重庆': 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=1200',
    '青岛': 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=1200',
    '广州': 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=1200',
    '苏州': 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=1200',
    '厦门': 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=1200',
    '南京': 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=1200',
    '武汉': 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=1200',
    '长沙': 'https://images.unsplash.com/photo-1585351363283-95e3d5041053?w=1200',
    '深圳': 'https://images.unsplash.com/photo-1558539320-1c71c5c5d8e8?w=1200',
    '三亚': 'https://images.unsplash.com/photo-1580821810645-11a8fd7c9f37?w=1200',
    '桂林': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=1200',
    '张家界': 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=1200',
    '黄山': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200',
    '九寨沟': 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=1200',
    '大理': 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=1200',
    '丽江': 'https://images.unsplash.com/photo-1529143694754-56f8e0156f33?w=1200',
  },

  // 城市轮播图片
  carousel: [
    { name: '北京', image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800' },
    { name: '上海', image: 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800' },
    { name: '西安', image: 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800' },
    { name: '成都', image: 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800' },
    { name: '杭州', image: 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800' },
    { name: '重庆', image: 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800' },
    { name: '青岛', image: 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=800' },
    { name: '广州', image: 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=800' },
    { name: '苏州', image: 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=800' },
    { name: '厦门', image: 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=800' },
    { name: '南京', image: 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=800' },
    { name: '武汉', image: 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=800' },
    { name: '长沙', image: 'https://images.unsplash.com/photo-1585351363283-95e3d5041053?w=800' },
    { name: '深圳', image: 'https://images.unsplash.com/photo-1558539320-1c71c5c5d8e8?w=800' },
    { name: '三亚', image: 'https://images.unsplash.com/photo-1580821810645-11a8fd7c9f37?w=800' },
    { name: '桂林', image: 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800' },
    { name: '张家界', image: 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=800' },
    { name: '黄山', image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800' },
    { name: '九寨沟', image: 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=800' },
    { name: '大理', image: 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=800' },
  ],

  // 景点详细图片 - 按城市分组
  spots: {
    '北京': [
      { name: '故宫', image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800' },
      { name: '天坛', image: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800' },
      { name: '长城', image: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800' },
      { name: '颐和园', image: 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800' },
      { name: '圆明园', image: 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800' },
      { name: '天安门', image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800' },
      { name: '鸟巢', image: 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800' },
      { name: '水立方', image: 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800' },
    ],
    '上海': [
      { name: '外滩', image: 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800' },
      { name: '东方明珠', image: 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800' },
      { name: '陆家嘴', image: 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800' },
      { name: '豫园', image: 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=800' },
    ],
    '西安': [
      { name: '兵马俑', image: 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800' },
      { name: '大雁塔', image: 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800' },
      { name: '古城墙', image: 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800' },
      { name: '钟楼', image: 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800' },
    ],
    '成都': [
      { name: '宽窄巷子', image: 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800' },
      { name: '锦里', image: 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800' },
      { name: '大熊猫', image: 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800' },
    ],
    '杭州': [
      { name: '西湖', image: 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800' },
      { name: '灵隐寺', image: 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800' },
      { name: '雷峰塔', image: 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800' },
    ],
    '重庆': [
      { name: '洪崖洞', image: 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800' },
      { name: '解放碑', image: 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800' },
    ],
    '青岛': [
      { name: '栈桥', image: 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=800' },
      { name: '八大关', image: 'https://images.unsplash.com/photo-1718085875432-98c61c603b54?w=800' },
    ],
    '广州': [
      { name: '广州塔', image: 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=800' },
      { name: '珠江新城', image: 'https://images.unsplash.com/photo-1559035871-4b9dcf31885c?w=800' },
    ],
    '苏州': [
      { name: '拙政园', image: 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=800' },
      { name: '周庄', image: 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=800' },
    ],
    '厦门': [
      { name: '鼓浪屿', image: 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=800' },
      { name: '厦门大学', image: 'https://images.unsplash.com/photo-1660531141240-d5fb7a955822?w=800' },
    ],
    '南京': [
      { name: '中山陵', image: 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=800' },
      { name: '夫子庙', image: 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=800' },
    ],
    '武汉': [
      { name: '黄鹤楼', image: 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=800' },
      { name: '武汉大学', image: 'https://images.unsplash.com/photo-1596496050827-8299e0220de1?w=800' },
    ],
    '张家界': [
      { name: '天门山', image: 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=800' },
      { name: '武陵源', image: 'https://images.unsplash.com/photo-1565060169194-19fabf63012f?w=800' },
    ],
    '黄山': [
      { name: '光明顶', image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800' },
      { name: '迎客松', image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800' },
    ],
    '九寨沟': [
      { name: '五彩池', image: 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=800' },
      { name: '诺日朗', image: 'https://images.unsplash.com/photo-1574169208507-84376144848b?w=800' },
    ],
    '大理': [
      { name: '洱海', image: 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=800' },
      { name: '大理古城', image: 'https://images.unsplash.com/photo-1580870069867-74c57ee1bb07?w=800' },
    ],
    '丽江': [
      { name: '丽江古城', image: 'https://images.unsplash.com/photo-1529143694754-56f8e0156f33?w=800' },
      { name: '玉龙雪山', image: 'https://images.unsplash.com/photo-1529143694754-56f8e0156f33?w=800' },
    ],
  },

  // 美食图片
  foods: [
    { name: '北京烤鸭', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400' },
    { name: '火锅', image: 'https://images.unsplash.com/photo-1587895929328-6226a77f5c0f?w=400' },
    { name: '麻辣烫', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400' },
    { name: '小笼包', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400' },
    { name: '生煎', image: 'https://images.unsplash.com/photo-1563245372-f21724e3856f?w=400' },
    { name: '早茶', image: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400' },
    { name: '烧烤', image: 'https://images.unsplash.com/photo-1529006557810-274b9b2fc783?w=400' },
    { name: '日料', image: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400' },
    { name: '寿司', image: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400' },
    { name: '牛排', image: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=400' },
  ],

  // 默认图片
  default: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
};

// 获取城市头部图片
export function getCityHeaderImage(cityName) {
  return CITY_CONFIG.header[cityName] || CITY_CONFIG.default;
}

// 获取景点图片
export function getSpotImage(spotName, cityName) {
  const citySpots = CITY_CONFIG.spots[cityName] || [];
  for (const spot of citySpots) {
    if (spot.name.includes(spotName) || spotName.includes(spot.name)) {
      return spot.image;
    }
  }
  return getCityHeaderImage(cityName) || CITY_CONFIG.default;
}

// 获取美食图片
export function getFoodImage(foodName) {
  for (const food of CITY_CONFIG.foods) {
    if (food.name.includes(foodName) || foodName.includes(food.name)) {
      return food.image;
    }
  }
  return CITY_CONFIG.foods[0]?.image || CITY_CONFIG.default;
}
