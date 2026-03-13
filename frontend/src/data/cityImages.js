/**
 * 城市和景点完整图片映射
 * 基于Unsplash真实图片
 */

export const CITY_IMAGES = {
  // 热门城市20个
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
};

// 首页轮播图城市（只用已有的正确图片的城市）
export const CAROUSEL_CITIES = [
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
];

// 城市详情页头部图
export const CITY_HEADER_IMAGES = CITY_IMAGES;

// 景点详细图片 - 每个城市的景点对应真实图片
export const SPOT_IMAGES = {
  // 北京
  '故宫': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
  '故宫博物院': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
  '天坛': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
  '天坛公园': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
  '长城': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
  '八达岭': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800',
  '颐和园': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
  '圆明园': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
  '北海公园': 'https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800',
  '天安门': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800',
  '鸟巢': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800',
  '水立方': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800',
  
  // 上海
  '外滩': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800',
  '东方明珠': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800',
  '陆家嘴': 'https://images.unsplash.com/photo-1474181487882-5abf3f0ba6c2?w=800',
  '豫园': 'https://images.unsplash.com/photo-1521022741625-63f57c752f95?w=800',
  
  // 西安
  '兵马俑': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800',
  '大雁塔': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800',
  '古城墙': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800',
  '钟楼': 'https://images.unsplash.com/photo-1724458589661-a2f42eb58aca?w=800',
  
  // 成都
  '宽窄巷子': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800',
  '锦里': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800',
  '大熊猫': 'https://images.unsplash.com/photo-1622613744987-0e3527fae518?w=800',
  
  // 杭州
  '西湖': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800',
  '灵隐寺': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800',
  '雷峰塔': 'https://images.unsplash.com/photo-1697730047280-01082430a28a?w=800',
  
  // 重庆
  '洪崖洞': 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800',
  '解放碑': 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800',
  '长江索道': 'https://images.unsplash.com/photo-1567014688543-cc4abffb061a?w=800',
  
  // 更多城市景点...
};

// 获取景点图片
export function getSpotImage(spotName, city) {
  // 精确匹配
  if (SPOT_IMAGES[spotName]) {
    return SPOT_IMAGES[spotName];
  }
  
  // 模糊匹配
  for (const [key, url] of Object.entries(SPOT_IMAGES)) {
    if (spotName.includes(key) || key.includes(spotName)) {
      return url;
    }
  }
  
  // 使用城市默认图
  return CITY_IMAGES[city] || 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800';
}
