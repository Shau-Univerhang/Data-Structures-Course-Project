<template>
  <div class="spot-recommend-page">
    <!-- 导航栏 -->
    <Navbar />

    <div class="page-content">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">为您推荐 {{ city }} 景点</h1>
        <p class="page-subtitle">根据您的偏好智能排序，点击景点加入行程</p>
      </div>

      <!-- 已选择景点数 -->
      <div class="selected-count" v-if="selectedSpots.length > 0">
        <span>已选择 {{ selectedSpots.length }} 个景点</span>
        <button class="clear-btn" @click="clearSelection">清空</button>
      </div>

      <!-- 景点列表 -->
      <div class="spots-grid">
        <div
          v-for="spot in sortedSpots"
          :key="spot.id"
          class="spot-card"
          :class="{ selected: isSelected(spot.id) }"
          @click="toggleSpot(spot)"
        >
          <div class="spot-image">
            <img :src="spot.images?.[0] || `/images/cities/${getCityImageName(spot.city)}`" :alt="spot.name" />
            <div class="spot-rank" v-if="spot.rank <= 3">
              <span>TOP {{ spot.rank }}</span>
            </div>
            <div class="select-indicator" v-if="isSelected(spot.id)">
              <span>✓</span>
            </div>
          </div>
          
          <div class="spot-info">
            <h3 class="spot-name">{{ spot.name }}</h3>
            
            <!-- 评分和收藏 -->
            <div class="spot-stats">
              <div class="stat-item">
                <span class="stat-icon">⭐</span>
                <span class="stat-value">{{ spot.rating?.toFixed(1) || '4.5' }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-icon">❤️</span>
                <span class="stat-value">{{ formatNumber(spot.favorites || 0) }}</span>
              </div>
            </div>

            <!-- 标签匹配度 -->
            <div class="tag-match" v-if="spot.match_count > 0">
              <span class="match-badge">匹配 {{ spot.match_count }} 个偏好</span>
            </div>

            <!-- 景点标签 -->
            <div class="spot-tags">
              <span v-for="tag in (spot.tags || [])" :key="tag" class="tag">
                {{ tag }}
              </span>
            </div>

            <!-- 推荐理由 -->
            <div class="recommend-reason" v-if="spot.recommendReason">
              <span>💡 {{ spot.recommendReason }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="sortedSpots.length === 0 && !loading" class="empty-state">
        <span class="empty-icon">🔍</span>
        <p>暂无景点数据</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在为您推荐景点...</p>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="bottom-bar" v-if="selectedSpots.length > 0">
      <div class="bar-info">
        <span>已选 {{ selectedSpots.length }} 个景点</span>
        <span class="days-info">{{ days }} 天行程</span>
      </div>
      <button class="create-trip-btn" @click="createTrip">
        生成行程
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Navbar from '../components/Navbar.vue'

const router = useRouter()
const route = useRoute()

// 页面数据
const city = ref('')
const days = ref(3)
const preferences = ref([])
const spots = ref([])
const selectedSpots = ref([])
const loading = ref(false)

// 城市图片映射
const getCityImageName = (cityName) => {
  const cityMap = {
    '北京': 'beijing.jpg', '上海': 'shanghai.jpg', '西安': 'xian.jpg',
    '成都': 'chengdu.jpg', '重庆': 'chongqing.jpg', '杭州': 'hangzhou.jpg',
    '广州': 'guangzhou.jpg', '苏州': 'suzhou.jpg', '厦门': 'xiamen.jpg',
    '三亚': 'sanya.jpg', '青岛': 'qingdao.jpg', '南京': 'nanjing.jpg',
    '武汉': 'wuhan.jpg', '长沙': 'changsha.jpg', '深圳': 'shenzhen.jpg',
    '桂林': 'guilin.jpg', '张家界': 'zhangjiajie.jpg', '黄山': 'huangshan.jpg',
    '九寨沟': 'jiuzhaigou.jpg', '大理': 'dali.jpg', '丽江': 'lijiang.jpg',
  }
  return cityMap[cityName] || 'beijing.jpg'
}

// 格式化数字
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

// 计算标签匹配数量 - 直接使用后端返回的match_count
const getMatchCount = (spot) => {
  return spot.match_count || 0
}

// 排序后的景点列表 - 后端已经排序好，只需添加排名
const sortedSpots = computed(() => {
  // 后端返回的spots已经按分数排序
  return spots.value.map((spot, index) => ({
    ...spot,
    rank: index + 1
  }))
})

// 加载景点数据
const loadSpots = async () => {
  loading.value = true
  try {
    // 构建URL，包含偏好参数
    let url = `http://localhost:8000/api/spots/recommend?city=${encodeURIComponent(city.value)}&limit=50`
    if (preferences.value.length > 0) {
      url += `&preferences=${encodeURIComponent(preferences.value.join(','))}`
    }
    console.log('请求URL:', url)
    const response = await fetch(url)
    const data = await response.json()
    console.log('返回数据前3个:', data.spots?.slice(0, 3).map(s => ({name: s.name, match_count: s.match_count, tags: s.tags})))
    
    if (data.spots) {
      spots.value = data.spots.map(spot => ({
        ...spot,
        // 使用数据库中的真实数据，如果没有则默认为0
        favorites: spot.favorites_count || 0,
        rating: spot.rating || 0
      }))
    } else {
      // 使用模拟数据
      spots.value = getMockSpots()
    }
  } catch (error) {
    console.error('加载景点失败:', error)
    spots.value = getMockSpots()
  } finally {
    loading.value = false
  }
}

// 模拟景点数据
const getMockSpots = () => {
  const mockSpots = [
    // 北京
    { id: 1, name: '故宫博物院', city: '北京', rating: 4.9, favorites: 15234, tags: ['历史', '文化', '建筑', '必玩景点'], images: ['/images/spots/beijing/beijing_gugong_bowuyuan.jpg'] },
    { id: 2, name: '天坛公园', city: '北京', rating: 4.8, favorites: 8932, tags: ['历史', '文化', '建筑'], images: ['/images/spots/beijing/beijing_tiantan_gongyuan.jpg'] },
    { id: 3, name: '颐和园', city: '北京', rating: 4.9, favorites: 12456, tags: ['风景', '名胜', '历史'], images: ['/images/spots/beijing/beijing_yiheyuan.jpg'] },
    { id: 4, name: '长城-八达岭', city: '北京', rating: 4.8, favorites: 18543, tags: ['必玩景点', '地标', '风景'], images: ['/images/spots/beijing/beijing_badaling_changcheng.jpg'] },
    { id: 5, name: '天安门广场', city: '北京', rating: 4.7, favorites: 22341, tags: ['地标', '必玩景点'], images: ['/images/spots/beijing/beijing_tiananmen_guangchang.jpg'] },
    { id: 6, name: '圆明园', city: '北京', rating: 4.6, favorites: 6789, tags: ['历史', '文化', '园林'], images: ['/images/spots/beijing/beijing_yuanmingyuan.jpg'] },
    { id: 7, name: '南锣鼓巷', city: '北京', rating: 4.4, favorites: 15678, tags: ['citywalk', '美食', '市井'], images: ['/images/spots/beijing/beijing_nanluoguxiang.jpg'] },
    { id: 8, name: '北海公园', city: '北京', rating: 4.5, favorites: 7890, tags: ['风景', '休闲', '园林'], images: ['/images/spots/beijing/beijing_beihai_gongyuan.jpg'] },
    { id: 9, name: '北京大学', city: '北京', rating: 4.7, favorites: 9876, tags: ['文化', '学府', '风景'], images: ['/images/spots/beijing/beijing_beijing_daxue.jpg'] },
    { id: 10, name: '清华大学', city: '北京', rating: 4.8, favorites: 8765, tags: ['文化', '学府', '风景'], images: ['/images/spots/beijing/beijing_qinghua_daxue.jpg'] },
    { id: 287, name: '北京邮电大学（本部）', city: '北京', rating: 4.8, favorites: 9321, tags: ['文化', '学府', '导航测试'], images: ['/images/spots/beijing/beijing_beijing_daxue.jpg'] },
    { id: 11, name: '鸟巢', city: '北京', rating: 4.6, favorites: 11234, tags: ['地标', '建筑', '奥运'], images: ['/images/spots/beijing/beijing_niaochao.jpg'] },
    { id: 12, name: '水立方', city: '北京', rating: 4.5, favorites: 9876, tags: ['地标', '建筑', '奥运'], images: ['/images/spots/beijing/beijing_shuilifang.jpg'] },
    { id: 13, name: '什刹海', city: '北京', rating: 4.4, favorites: 13456, tags: ['风景', '休闲', '历史'], images: ['/images/spots/beijing/beijing_shichahai.jpg'] },
    
    // 上海
    { id: 101, name: '外滩', city: '上海', rating: 4.8, favorites: 23456, tags: ['地标', '必玩景点', '夜景'], images: ['/images/spots/shanghai/shanghai_waitan.jpg'] },
    { id: 102, name: '东方明珠', city: '上海', rating: 4.7, favorites: 19876, tags: ['地标', '建筑', '观景'], images: ['/images/spots/shanghai/shanghai_dongfang_mingzhu.jpg'] },
    { id: 103, name: '豫园', city: '上海', rating: 4.5, favorites: 14567, tags: ['园林', '历史', '文化'], images: ['/images/spots/shanghai/shanghai_yuyuan.jpg'] },
    { id: 104, name: '田子坊', city: '上海', rating: 4.3, favorites: 12345, tags: ['citywalk', '艺术', '创意'], images: ['/images/spots/shanghai/shanghai_tianzifang.jpg'] },
    { id: 105, name: '南京路步行街', city: '上海', rating: 4.4, favorites: 18765, tags: ['购物', 'citywalk', '地标'], images: ['/images/spots/shanghai/shanghai_nanjinglu_buxingjie.jpg'] },
    { id: 106, name: '城隍庙', city: '上海', rating: 4.4, favorites: 15678, tags: ['历史', '文化', '美食'], images: ['/images/spots/shanghai/shanghai_chenghuangmiao.jpg'] },
    { id: 107, name: '新天地', city: '上海', rating: 4.5, favorites: 13456, tags: ['citywalk', '时尚', '休闲'], images: ['/images/spots/shanghai/shanghai_xintiandi.jpg'] },
    { id: 108, name: '上海迪士尼', city: '上海', rating: 4.8, favorites: 25678, tags: ['亲子', '娱乐', '必玩景点'], images: ['/images/spots/shanghai/shanghai_shanghai_dishini.jpg'] },
    { id: 109, name: '武康路', city: '上海', rating: 4.6, favorites: 11234, tags: ['citywalk', '历史', '建筑'], images: ['/images/spots/shanghai/shanghai_wukanglu.jpg'] },
    { id: 110, name: '静安寺', city: '上海', rating: 4.5, favorites: 9876, tags: ['历史', '文化', '寺庙'], images: ['/images/spots/shanghai/shanghai_jingansi.jpg'] },
    { id: 111, name: '复旦大学', city: '上海', rating: 4.7, favorites: 8765, tags: ['文化', '学府', '风景'], images: ['/images/spots/shanghai/shanghai_fudan_daxue.jpg'] },
    { id: 112, name: '上海中心大厦', city: '上海', rating: 4.6, favorites: 14567, tags: ['地标', '建筑', '观景'], images: ['/images/spots/shanghai/shanghai_shanghai_zhongxin.jpg'] },
    
    // 西安
    { id: 201, name: '兵马俑', city: '西安', rating: 4.9, favorites: 21345, tags: ['历史', '文化', '必玩景点', '世界遗产'], images: ['/images/spots/xian/xian_bingmayong.jpg'] },
    { id: 202, name: '大雁塔', city: '西安', rating: 4.7, favorites: 16789, tags: ['历史', '文化', '地标'], images: ['/images/spots/xian/xian_dayanta.jpg'] },
    { id: 203, name: '西安城墙', city: '西安', rating: 4.6, favorites: 14567, tags: ['历史', '文化', '地标'], images: ['/images/spots/xian/xian_xian_chengqiang.jpg'] },
    { id: 204, name: '华清宫', city: '西安', rating: 4.5, favorites: 12345, tags: ['历史', '文化', '温泉'], images: ['/images/spots/xian/xian_huaqinggong.jpg'] },
    { id: 205, name: '大唐不夜城', city: '西安', rating: 4.7, favorites: 19876, tags: ['夜景', '文化', '休闲'], images: ['/images/spots/xian/xian_datang_buyecheng.jpg'] },
    { id: 206, name: '回民街', city: '西安', rating: 4.3, favorites: 18765, tags: ['美食', '市井', '文化'], images: ['/images/spots/xian/xian_huiminjie.jpg'] },
    { id: 207, name: '大唐芙蓉园', city: '西安', rating: 4.6, favorites: 13456, tags: ['园林', '文化', '夜景'], images: ['/images/spots/xian/xian_datang_furongyuan.jpg'] },
    { id: 208, name: '钟楼', city: '西安', rating: 4.5, favorites: 15678, tags: ['地标', '历史', '建筑'], images: ['/images/spots/xian/xian_zhonglou.jpg'] },
    { id: 209, name: '陕西历史博物馆', city: '西安', rating: 4.8, favorites: 14567, tags: ['博物馆', '历史', '文化'], images: ['/images/spots/xian/xian_shanxi_lishi_bowuguan.jpg'] },
    { id: 210, name: '小雁塔', city: '西安', rating: 4.5, favorites: 8765, tags: ['历史', '文化', '古迹'], images: ['/images/spots/xian/xian_xiaoyanta.jpg'] },
    { id: 211, name: '西安交通大学', city: '西安', rating: 4.6, favorites: 7654, tags: ['文化', '学府', '风景'], images: ['/images/spots/xian/xian_xian_jiaotong_daxue.jpg'] },
    
    // 成都
    { id: 301, name: '宽窄巷子', city: '成都', rating: 4.5, favorites: 18765, tags: ['citywalk', '历史', '文化'], images: ['/images/spots/chengdu/chengdu_kuanzhai_xiangzi.jpg'] },
    { id: 302, name: '大熊猫繁育研究基地', city: '成都', rating: 4.9, favorites: 28765, tags: ['亲子', '必玩景点', '动物'], images: ['/images/spots/chengdu/chengdu_xiongmao_jidi.jpg'] },
    { id: 303, name: '锦里古街', city: '成都', rating: 4.4, favorites: 16789, tags: ['citywalk', '历史', '美食'], images: ['/images/spots/chengdu/chengdu_jinli_gujie.jpg'] },
    { id: 304, name: '武侯祠', city: '成都', rating: 4.6, favorites: 14567, tags: ['历史', '文化', '古迹'], images: ['/images/spots/chengdu/chengdu_wuhouci.jpg'] },
    { id: 305, name: '杜甫草堂', city: '成都', rating: 4.5, favorites: 12345, tags: ['历史', '文化', '园林'], images: ['/images/spots/chengdu/chengdu_dufu_caotang.jpg'] },
    { id: 306, name: '青城山', city: '成都', rating: 4.7, favorites: 13456, tags: ['风景', '道教', '登山'], images: ['/images/spots/chengdu/chengdu_qingchengshan.jpg'] },
    { id: 307, name: '都江堰', city: '成都', rating: 4.8, favorites: 15678, tags: ['历史', '文化', '世界遗产'], images: ['/images/spots/chengdu/chengdu_dujiangyan.jpg'] },
    { id: 308, name: '春熙路', city: '成都', rating: 4.4, favorites: 17890, tags: ['购物', 'citywalk', '美食'], images: ['/images/spots/chengdu/chengdu_chunxilu.jpg'] },
    { id: 309, name: '文殊院', city: '成都', rating: 4.5, favorites: 9876, tags: ['文化', '寺庙', '历史'], images: ['/images/spots/chengdu/chengdu_wenshuyuan.jpg'] },
    { id: 310, name: '四川大学', city: '成都', rating: 4.6, favorites: 8765, tags: ['文化', '学府', '风景'], images: ['/images/spots/chengdu/chengdu_sichuan_daxue.jpg'] },
    
    // 杭州
    { id: 401, name: '西湖', city: '杭州', rating: 4.9, favorites: 28765, tags: ['风景', '名胜', '必玩景点'], images: ['/images/spots/hangzhou/hangzhou_xihu.jpg'] },
    { id: 402, name: '灵隐寺', city: '杭州', rating: 4.7, favorites: 16789, tags: ['文化', '寺庙', '历史'], images: ['/images/spots/hangzhou/hangzhou_lingyinsi.jpg'] },
    { id: 403, name: '千岛湖', city: '杭州', rating: 4.6, favorites: 14567, tags: ['风景', '休闲', '度假'], images: ['/images/spots/hangzhou/hangzhou_qiandaohu.jpg'] },
    { id: 404, name: '宋城', city: '杭州', rating: 4.5, favorites: 13456, tags: ['文化', '娱乐', '表演'], images: ['/images/spots/hangzhou/hangzhou_songcheng.jpg'] },
    { id: 405, name: '西溪湿地', city: '杭州', rating: 4.6, favorites: 11234, tags: ['自然', '生态', '休闲'], images: ['/images/spots/hangzhou/hangzhou_xixi_shidi.jpg'] },
    { id: 406, name: '雷峰塔', city: '杭州', rating: 4.5, favorites: 15678, tags: ['历史', '文化', '地标'], images: ['/images/spots/hangzhou/hangzhou_leifengta.jpg'] },
    { id: 407, name: '河坊街', city: '杭州', rating: 4.4, favorites: 12345, tags: ['citywalk', '历史', '美食'], images: ['/images/spots/hangzhou/hangzhou_hefangjie.jpg'] },
    { id: 408, name: '断桥残雪', city: '杭州', rating: 4.7, favorites: 18765, tags: ['风景', '文化', '浪漫'], images: ['/images/spots/hangzhou/hangzhou_duanqiao_canxue.jpg'] },
    { id: 409, name: '浙江大学', city: '杭州', rating: 4.6, favorites: 9876, tags: ['文化', '学府', '风景'], images: ['/images/spots/hangzhou/hangzhou_zhejiang_daxue.jpg'] },
    { id: 410, name: '龙井村', city: '杭州', rating: 4.5, favorites: 8765, tags: ['茶文化', '风景', '休闲'], images: ['/images/spots/hangzhou/hangzhou_longjingcun.jpg'] },
    
    // 重庆
    { id: 501, name: '洪崖洞', city: '重庆', rating: 4.7, favorites: 25678, tags: ['夜景', '地标', '必玩景点'], images: ['/images/spots/chongqing/chongqing_hongyadong.jpg'] },
    { id: 502, name: '解放碑', city: '重庆', rating: 4.6, favorites: 19876, tags: ['地标', '历史', '购物'], images: ['/images/spots/chongqing/chongqing_jiefangbei.jpg'] },
    { id: 503, name: '磁器口古镇', city: '重庆', rating: 4.5, favorites: 16789, tags: ['古镇', '历史', '美食'], images: ['/images/spots/chongqing/chongqing_ciqikou.jpg'] },
    { id: 504, name: '长江索道', city: '重庆', rating: 4.6, favorites: 18765, tags: ['观景', '特色交通', '地标'], images: ['/images/spots/chongqing/chongqing_changjiang_suodao.jpg'] },
    { id: 505, name: '武隆天坑', city: '重庆', rating: 4.8, favorites: 14567, tags: ['自然', '风景', '世界遗产'], images: ['/images/spots/chongqing/chongqing_wulong_tiankeng.jpg'] },
    { id: 506, name: '朝天门', city: '重庆', rating: 4.5, favorites: 13456, tags: ['地标', '观景', '历史'], images: ['/images/spots/chongqing/chongqing_chaotianmen.jpg'] },
    { id: 507, name: '李子坝轻轨', city: '重庆', rating: 4.4, favorites: 15678, tags: ['特色交通', '网红', '地标'], images: ['/images/spots/chongqing/chongqing_liziba_qinggui.jpg'] },
    { id: 508, name: '鹅岭二厂', city: '重庆', rating: 4.5, favorites: 11234, tags: ['文创', '艺术', 'citywalk'], images: ['/images/spots/chongqing/chongqing_eling_erchang.jpg'] },
    { id: 509, name: '南山一棵树', city: '重庆', rating: 4.6, favorites: 9876, tags: ['观景', '夜景', '休闲'], images: ['/images/spots/chongqing/chongqing_nanshan_yikeshu.jpg'] },
    { id: 510, name: '三峡博物馆', city: '重庆', rating: 4.5, favorites: 8765, tags: ['博物馆', '历史', '文化'], images: ['/images/spots/chongqing/chongqing_sanxia_bowuguan.jpg'] },
    
    // 广州
    { id: 601, name: '广州塔', city: '广州', rating: 4.7, favorites: 19876, tags: ['地标', '建筑', '观景'], images: ['/images/spots/guangzhou/guangzhou_guangzhouta.jpg'] },
    { id: 602, name: '沙面', city: '广州', rating: 4.6, favorites: 14567, tags: ['历史', '建筑', 'citywalk'], images: ['/images/spots/guangzhou/guangzhou_shamian.jpg'] },
    { id: 603, name: '陈家祠', city: '广州', rating: 4.5, favorites: 11234, tags: ['文化', '建筑', '历史'], images: ['/images/spots/guangzhou/guangzhou_chenjiaci.jpg'] },
    { id: 604, name: '珠江夜游', city: '广州', rating: 4.6, favorites: 16789, tags: ['夜景', '休闲', '必玩景点'], images: ['/images/spots/guangzhou/guangzhou_zhujiang_yeyou.jpg'] },
    { id: 605, name: '白云山', city: '广州', rating: 4.5, favorites: 13456, tags: ['自然', '登山', '休闲'], images: ['/images/spots/guangzhou/guangzhou_baiyunshan.jpg'] },
    { id: 606, name: '越秀公园', city: '广州', rating: 4.4, favorites: 9876, tags: ['公园', '休闲', '历史'], images: ['/images/spots/guangzhou/guangzhou_yuexiu_gongyuan.jpg'] },
    { id: 607, name: '北京路步行街', city: '广州', rating: 4.5, favorites: 15678, tags: ['购物', 'citywalk', '美食'], images: ['/images/spots/guangzhou/guangzhou_beijinglu_buxingjie.jpg'] },
    { id: 608, name: '长隆欢乐世界', city: '广州', rating: 4.7, favorites: 18765, tags: ['亲子', '娱乐', '必玩景点'], images: ['/images/spots/guangzhou/guangzhou_changlong_huanle_shijie.jpg'] },
    { id: 609, name: '中山纪念堂', city: '广州', rating: 4.5, favorites: 8765, tags: ['历史', '文化', '建筑'], images: ['/images/spots/guangzhou/guangzhou_zhongshan_jiniantang.jpg'] },
    { id: 610, name: '中山大学', city: '广州', rating: 4.6, favorites: 7654, tags: ['文化', '学府', '风景'], images: ['/images/spots/guangzhou/guangzhou_zhongshan_daxue.jpg'] },
    
    // 苏州
    { id: 701, name: '拙政园', city: '苏州', rating: 4.8, favorites: 15678, tags: ['园林', '世界遗产', '必玩景点'], images: ['/images/spots/suzhou/suzhou_zhuozhengyuan.jpg'] },
    { id: 702, name: '虎丘', city: '苏州', rating: 4.6, favorites: 12345, tags: ['历史', '文化', '风景'], images: ['/images/spots/suzhou/suzhou_huqiu.jpg'] },
    { id: 703, name: '留园', city: '苏州', rating: 4.7, favorites: 9876, tags: ['园林', '世界遗产', '文化'], images: ['/images/spots/suzhou/suzhou_liuyuan.jpg'] },
    { id: 704, name: '狮子林', city: '苏州', rating: 4.5, favorites: 8765, tags: ['园林', '文化', '历史'], images: ['/images/spots/suzhou/suzhou_shizilin.jpg'] },
    { id: 705, name: '苏州博物馆', city: '苏州', rating: 4.6, favorites: 11234, tags: ['博物馆', '文化', '建筑'], images: ['/images/spots/suzhou/suzhou_suzhou_bowuguan.jpg'] },
    { id: 706, name: '平江路', city: '苏州', rating: 4.5, favorites: 13456, tags: ['citywalk', '历史', '文化'], images: ['/images/spots/suzhou/suzhou_pingjianglu.jpg'] },
    { id: 707, name: '周庄古镇', city: '苏州', rating: 4.6, favorites: 14567, tags: ['古镇', '水乡', '历史'], images: ['/images/spots/suzhou/suzhou_zhouzhuang_guzhen.jpg'] },
    { id: 708, name: '同里古镇', city: '苏州', rating: 4.5, favorites: 9876, tags: ['古镇', '水乡', '文化'], images: ['/images/spots/suzhou/suzhou_tongli_guzhen.jpg'] },
    { id: 709, name: '金鸡湖', city: '苏州', rating: 4.6, favorites: 8765, tags: ['风景', '休闲', '现代'], images: ['/images/spots/suzhou/suzhou_jinjihu.jpg'] },
    { id: 710, name: '寒山寺', city: '苏州', rating: 4.5, favorites: 7654, tags: ['寺庙', '文化', '历史'], images: ['/images/spots/suzhou/suzhou_hanshansi.jpg'] },
    
    // 厦门
    { id: 801, name: '鼓浪屿', city: '厦门', rating: 4.8, favorites: 23456, tags: ['海岛', '世界遗产', '必玩景点'], images: ['/images/spots/xiamen/xiamen_gulangyu.jpg'] },
    { id: 802, name: '厦门大学', city: '厦门', rating: 4.7, favorites: 18765, tags: ['学府', '风景', '文化'], images: ['/images/spots/xiamen/xiamen_xiamen_daxue.jpg'] },
    { id: 803, name: '南普陀寺', city: '厦门', rating: 4.6, favorites: 14567, tags: ['寺庙', '文化', '历史'], images: ['/images/spots/xiamen/xiamen_nanputuosi.jpg'] },
    { id: 804, name: '曾厝垵', city: '厦门', rating: 4.4, favorites: 16789, tags: ['文创', '美食', 'citywalk'], images: ['/images/spots/xiamen/xiamen_zengcuoan.jpg'] },
    { id: 805, name: '环岛路', city: '厦门', rating: 4.6, favorites: 13456, tags: ['风景', '骑行', '休闲'], images: ['/images/spots/xiamen/xiamen_huandaolu.jpg'] },
    { id: 806, name: '中山路步行街', city: '厦门', rating: 4.5, favorites: 15678, tags: ['购物', 'citywalk', '美食'], images: ['/images/spots/xiamen/xiamen_zhongshanlu_buxingjie.jpg'] },
    { id: 807, name: '胡里山炮台', city: '厦门', rating: 4.4, favorites: 8765, tags: ['历史', '军事', '文化'], images: ['/images/spots/xiamen/xiamen_hulishan_paotai.jpg'] },
    { id: 808, name: '集美学村', city: '厦门', rating: 4.5, favorites: 9876, tags: ['学府', '文化', '建筑'], images: ['/images/spots/xiamen/xiamen_jimei_xuecun.jpg'] },
    { id: 809, name: '园林植物园', city: '厦门', rating: 4.6, favorites: 7654, tags: ['自然', '植物', '休闲'], images: ['/images/spots/xiamen/xiamen_yuanlin_zhiwuyuan.jpg'] },
    { id: 810, name: '白城沙滩', city: '厦门', rating: 4.5, favorites: 11234, tags: ['海滩', '休闲', '风景'], images: ['/images/spots/xiamen/xiamen_baicheng_shatan.jpg'] },
    
    // 南京
    { id: 901, name: '中山陵', city: '南京', rating: 4.8, favorites: 18765, tags: ['历史', '文化', '必玩景点'], images: ['/images/spots/nanjing/nanjing_zhongshanling.jpg'] },
    { id: 902, name: '夫子庙', city: '南京', rating: 4.6, favorites: 16789, tags: ['历史', '文化', '美食'], images: ['/images/spots/nanjing/nanjing_fuzimiao.jpg'] },
    { id: 903, name: '秦淮河', city: '南京', rating: 4.7, favorites: 15678, tags: ['夜景', '文化', '历史'], images: ['/images/spots/nanjing/nanjing_qinhuaihe.jpg'] },
    { id: 904, name: '明孝陵', city: '南京', rating: 4.7, favorites: 13456, tags: ['历史', '文化', '世界遗产'], images: ['/images/spots/nanjing/nanjing_mingxiaoling.jpg'] },
    { id: 905, name: '总统府', city: '南京', rating: 4.6, favorites: 14567, tags: ['历史', '文化', '建筑'], images: ['/images/spots/nanjing/nanjing_zongtongfu.jpg'] },
    { id: 906, name: '南京博物院', city: '南京', rating: 4.7, favorites: 11234, tags: ['博物馆', '文化', '历史'], images: ['/images/spots/nanjing/nanjing_nanjing_bowuyuan.jpg'] },
    { id: 907, name: '玄武湖', city: '南京', rating: 4.5, favorites: 9876, tags: ['风景', '休闲', '公园'], images: ['/images/spots/nanjing/nanjing_xuanwuhu.jpg'] },
    { id: 908, name: '鸡鸣寺', city: '南京', rating: 4.6, favorites: 8765, tags: ['寺庙', '文化', '历史'], images: ['/images/spots/nanjing/nanjing_jimingsi.jpg'] },
    { id: 909, name: '侵华日军南京大屠杀遇难同胞纪念馆', city: '南京', rating: 4.8, favorites: 15678, tags: ['历史', '纪念', '教育'], images: ['/images/spots/nanjing/nanjing_nanjing_datusha_jinianguan.jpg'] },
    { id: 910, name: '老门东', city: '南京', rating: 4.5, favorites: 11234, tags: ['citywalk', '历史', '美食'], images: ['/images/spots/nanjing/nanjing_laomendong.jpg'] },
    
    // 武汉
    { id: 1001, name: '黄鹤楼', city: '武汉', rating: 4.7, favorites: 19876, tags: ['历史', '文化', '地标'], images: ['/images/spots/wuhan/wuhan_huanghelou.jpg'] },
    { id: 1002, name: '东湖', city: '武汉', rating: 4.6, favorites: 14567, tags: ['风景', '休闲', '公园'], images: ['/images/spots/wuhan/wuhan_donghu.jpg'] },
    { id: 1003, name: '户部巷', city: '武汉', rating: 4.4, favorites: 16789, tags: ['美食', '市井', '历史'], images: ['/images/spots/wuhan/wuhan_hubuxiang.jpg'] },
    { id: 1004, name: '武汉大学', city: '武汉', rating: 4.8, favorites: 15678, tags: ['学府', '风景', '文化'], images: ['/images/spots/wuhan/wuhan_wuhan_daxue.jpg'] },
    { id: 1005, name: '湖北省博物馆', city: '武汉', rating: 4.7, favorites: 11234, tags: ['博物馆', '文化', '历史'], images: ['/images/spots/wuhan/wuhan_hubei_bowuguan.jpg'] },
    { id: 1006, name: '江汉路步行街', city: '武汉', rating: 4.5, favorites: 13456, tags: ['购物', 'citywalk', '历史'], images: ['/images/spots/wuhan/wuhan_jianghanlu_buxingjie.jpg'] },
    { id: 1007, name: '古琴台', city: '武汉', rating: 4.5, favorites: 8765, tags: ['文化', '历史', '音乐'], images: ['/images/spots/wuhan/wuhan_guqintai.jpg'] },
    { id: 1008, name: '晴川阁', city: '武汉', rating: 4.6, favorites: 7654, tags: ['历史', '文化', '建筑'], images: ['/images/spots/wuhan/wuhan_qingchuange.jpg'] },
    { id: 1009, name: '昙华林', city: '武汉', rating: 4.4, favorites: 9876, tags: ['citywalk', '文创', '历史'], images: ['/images/spots/wuhan/wuhan_tanhualin.jpg'] },
    { id: 1010, name: '汉口江滩', city: '武汉', rating: 4.5, favorites: 11234, tags: ['风景', '休闲', '江景'], images: ['/images/spots/wuhan/wuhan_hankou_jiangtan.jpg'] },
    
    // 长沙
    { id: 1101, name: '岳麓山', city: '长沙', rating: 4.6, favorites: 16789, tags: ['风景', '文化', '登山'], images: ['/images/spots/changsha/changsha_yuelushan.jpg'] },
    { id: 1102, name: '橘子洲', city: '长沙', rating: 4.7, favorites: 18765, tags: ['风景', '历史', '地标'], images: ['/images/spots/changsha/changsha_juzizhou.jpg'] },
    { id: 1103, name: '湖南省博物馆', city: '长沙', rating: 4.7, favorites: 13456, tags: ['博物馆', '文化', '历史'], images: ['/images/spots/changsha/changsha_hunan_bowuguan.jpg'] },
    { id: 1104, name: '太平街', city: '长沙', rating: 4.5, favorites: 15678, tags: ['citywalk', '美食', '历史'], images: ['/images/spots/changsha/changsha_taipingjie.jpg'] },
    { id: 1105, name: '天心阁', city: '长沙', rating: 4.4, favorites: 8765, tags: ['历史', '文化', '建筑'], images: ['/images/spots/changsha/changsha_tianxinge.jpg'] },
    { id: 1106, name: '世界之窗', city: '长沙', rating: 4.5, favorites: 11234, tags: ['娱乐', '亲子', '主题公园'], images: ['/images/spots/changsha/changsha_shijie_zhichuang.jpg'] },
    { id: 1107, name: '烈士公园', city: '长沙', rating: 4.5, favorites: 9876, tags: ['公园', '休闲', '纪念'], images: ['/images/spots/changsha/changsha_lieshi_gongyuan.jpg'] },
    { id: 1108, name: '黄兴路步行街', city: '长沙', rating: 4.4, favorites: 13456, tags: ['购物', 'citywalk', '美食'], images: ['/images/spots/changsha/changsha_huangxinglu_buxingjie.jpg'] },
    { id: 1109, name: '坡子街', city: '长沙', rating: 4.5, favorites: 12345, tags: ['美食', '市井', '历史'], images: ['/images/spots/changsha/changsha_pozijie.jpg'] },
    { id: 1110, name: '爱晚亭', city: '长沙', rating: 4.6, favorites: 8765, tags: ['风景', '文化', '历史'], images: ['/images/spots/changsha/changsha_aiwanting.jpg'] },
    
    // 深圳
    { id: 1201, name: '世界之窗', city: '深圳', rating: 4.5, favorites: 15678, tags: ['主题公园', '娱乐', '微缩景观'], images: ['/images/spots/shenzhen/shenzhen_shijie_zhichuang.jpg'] },
    { id: 1202, name: '欢乐谷', city: '深圳', rating: 4.6, favorites: 16789, tags: ['主题公园', '娱乐', '亲子'], images: ['/images/spots/shenzhen/shenzhen_hualegu.jpg'] },
    { id: 1203, name: '东部华侨城', city: '深圳', rating: 4.5, favorites: 13456, tags: ['度假', '休闲', '风景'], images: ['/images/spots/shenzhen/shenzhen_dongbu_huaqiaocheng.jpg'] },
    { id: 1204, name: '大梅沙', city: '深圳', rating: 4.4, favorites: 14567, tags: ['海滩', '休闲', '度假'], images: ['/images/spots/shenzhen/shenzhen_dameisha.jpg'] },
    { id: 1205, name: '小梅沙', city: '深圳', rating: 4.5, favorites: 11234, tags: ['海滩', '休闲', '度假'], images: ['/images/spots/shenzhen/shenzhen_xiaomeisha.jpg'] },
    { id: 1206, name: '深圳湾公园', city: '深圳', rating: 4.6, favorites: 13456, tags: ['公园', '休闲', '海景'], images: ['/images/spots/shenzhen/shenzhen_shenzhenwan_gongyuan.jpg'] },
    { id: 1207, name: '莲花山公园', city: '深圳', rating: 4.5, favorites: 9876, tags: ['公园', '休闲', '登山'], images: ['/images/spots/shenzhen/shenzhen_lianhuashan_gongyuan.jpg'] },
    { id: 1208, name: '梧桐山', city: '深圳', rating: 4.6, favorites: 8765, tags: ['登山', '自然', '风景'], images: ['/images/spots/shenzhen/shenzhen_wutongshan.jpg'] },
    { id: 1209, name: '中英街', city: '深圳', rating: 4.4, favorites: 7654, tags: ['历史', '边境', '购物'], images: ['/images/spots/shenzhen/shenzhen_zhongyingjie.jpg'] },
    { id: 1210, name: '大鹏所城', city: '深圳', rating: 4.5, favorites: 9876, tags: ['历史', '文化', '古城'], images: ['/images/spots/shenzhen/shenzhen_dapeng_suocheng.jpg'] },
    
    // 青岛
    { id: 1301, name: '栈桥', city: '青岛', rating: 4.6, favorites: 17890, tags: ['地标', '海景', '历史'], images: ['/images/spots/qingdao/qingdao_zhanqiao.jpg'] },
    { id: 1302, name: '八大关', city: '青岛', rating: 4.7, favorites: 15678, tags: ['建筑', '历史', 'citywalk'], images: ['/images/spots/qingdao/qingdao_badaguan.jpg'] },
    { id: 1303, name: '崂山', city: '青岛', rating: 4.8, favorites: 14567, tags: ['登山', '道教', '风景'], images: ['/images/spots/qingdao/qingdao_laoshan.jpg'] },
    { id: 1304, name: '五四广场', city: '青岛', rating: 4.5, favorites: 13456, tags: ['地标', '广场', '海景'], images: ['/images/spots/qingdao/qingdao_wusi_guangchang.jpg'] },
    { id: 1305, name: '青岛啤酒博物馆', city: '青岛', rating: 4.6, favorites: 11234, tags: ['博物馆', '文化', '工业'], images: ['/images/spots/qingdao/qingdao_qingdao_pijiu_bowuguan.jpg'] },
    { id: 1306, name: '金沙滩', city: '青岛', rating: 4.5, favorites: 12345, tags: ['海滩', '休闲', '度假'], images: ['/images/spots/qingdao/qingdao_jinshatan.jpg'] },
    { id: 1307, name: '小鱼山', city: '青岛', rating: 4.4, favorites: 8765, tags: ['登山', '观景', '公园'], images: ['/images/spots/qingdao/qingdao_xiaoyushan.jpg'] },
    { id: 1308, name: '信号山公园', city: '青岛', rating: 4.5, favorites: 9876, tags: ['公园', '观景', '休闲'], images: ['/images/spots/qingdao/qingdao_xinhaoshan_gongyuan.jpg'] },
    { id: 1309, name: '天主教堂', city: '青岛', rating: 4.6, favorites: 7654, tags: ['建筑', '宗教', '历史'], images: ['/images/spots/qingdao/qingdao_tianzhu_jiaotang.jpg'] },
    { id: 1310, name: '奥帆中心', city: '青岛', rating: 4.5, favorites: 11234, tags: ['地标', '奥运', '海景'], images: ['/images/spots/qingdao/qingdao_aofan_zhongxin.jpg'] },
    
    // 三亚
    { id: 1401, name: '亚龙湾', city: '三亚', rating: 4.8, favorites: 23456, tags: ['海滩', '度假', '必玩景点'], images: ['/images/spots/sanya/sanya_yalongwan.jpg'] },
    { id: 1402, name: '天涯海角', city: '三亚', rating: 4.6, favorites: 19876, tags: ['地标', '海景', '文化'], images: ['/images/spots/sanya/sanya_tianyahaijiao.jpg'] },
    { id: 1403, name: '南山寺', city: '三亚', rating: 4.7, favorites: 15678, tags: ['寺庙', '文化', '宗教'], images: ['/images/spots/sanya/sanya_nanshansi.jpg'] },
    { id: 1404, name: '蜈支洲岛', city: '三亚', rating: 4.8, favorites: 18765, tags: ['海岛', '潜水', '度假'], images: ['/images/spots/sanya/sanya_wuzhizhou_dao.jpg'] },
    { id: 1405, name: '大东海', city: '三亚', rating: 4.5, favorites: 14567, tags: ['海滩', '休闲', '游泳'], images: ['/images/spots/sanya/sanya_yalongwan.jpg'] },
    { id: 1406, name: '鹿回头', city: '三亚', rating: 4.6, favorites: 11234, tags: ['风景', '传说', '观景'], images: ['/images/spots/sanya/sanya_luhuitou.jpg'] },
    { id: 1407, name: '三亚湾', city: '三亚', rating: 4.5, favorites: 13456, tags: ['海滩', '休闲', '日落'], images: ['/images/spots/sanya/sanya_sanyawan.jpg'] },
    { id: 1408, name: '海棠湾', city: '三亚', rating: 4.6, favorites: 12345, tags: ['海滩', '度假', '高端'], images: ['/images/spots/sanya/sanya_haitangwan.jpg'] },
    { id: 1409, name: '亚特兰蒂斯水世界', city: '三亚', rating: 4.7, favorites: 15678, tags: ['娱乐', '亲子', '水上'], images: ['/images/spots/sanya/sanya_yatelandisi_shuishijie.jpg'] },
    { id: 1410, name: '千古情', city: '三亚', rating: 4.5, favorites: 9876, tags: ['表演', '文化', '娱乐'], images: ['/images/spots/sanya/sanya_qianguging.jpg'] },
    
    // 桂林
    { id: 1501, name: '漓江', city: '桂林', rating: 4.9, favorites: 25678, tags: ['风景', '山水', '必玩景点'], images: ['/images/spots/guilin/guilin_lijiang.jpg'] },
    { id: 1502, name: '象鼻山', city: '桂林', rating: 4.7, favorites: 18765, tags: ['地标', '风景', '自然'], images: ['/images/spots/guilin/guilin_xiangbishan.jpg'] },
    { id: 1503, name: '阳朔西街', city: '桂林', rating: 4.5, favorites: 16789, tags: ['citywalk', '美食', '夜生活'], images: ['/images/spots/guilin/guilin_yangshuo_xijie.jpg'] },
    { id: 1504, name: '龙脊梯田', city: '桂林', rating: 4.8, favorites: 14567, tags: ['风景', '摄影', '自然'], images: ['/images/spots/guilin/guilin_longji_titian.jpg'] },
    { id: 1505, name: '两江四湖', city: '桂林', rating: 4.6, favorites: 13456, tags: ['夜景', '游船', '城市'], images: ['/images/spots/guilin/guilin_liangjiang_sihu.jpg'] },
    { id: 1506, name: '银子岩', city: '桂林', rating: 4.5, favorites: 11234, tags: ['溶洞', '自然', '奇观'], images: ['/images/spots/guilin/guilin_yinziyan.jpg'] },
    { id: 1507, name: '世外桃源', city: '桂林', rating: 4.6, favorites: 9876, tags: ['风景', '田园', '休闲'], images: ['/images/spots/guilin/guilin_shiwai_taoyuan.jpg'] },
    { id: 1508, name: '十里画廊', city: '桂林', rating: 4.5, favorites: 12345, tags: ['风景', '骑行', '自然'], images: ['/images/spots/guilin/guilin_shili_hualang.jpg'] },
    { id: 1509, name: '遇龙河', city: '桂林', rating: 4.7, favorites: 11234, tags: ['漂流', '风景', '自然'], images: ['/images/spots/guilin/guilin_yulonghe.jpg'] },
    { id: 1510, name: '兴坪古镇', city: '桂林', rating: 4.4, favorites: 8765, tags: ['古镇', '历史', '文化'], images: ['/images/spots/guilin/guilin_xingping_guzhen.jpg'] },
    
    // 丽江
    { id: 1601, name: '丽江古城', city: '丽江', rating: 4.7, favorites: 23456, tags: ['古城', '世界遗产', '必玩景点'], images: ['/images/spots/lijiang/lijiang_lijiang_gucheng.jpg'] },
    { id: 1602, name: '玉龙雪山', city: '丽江', rating: 4.8, favorites: 19876, tags: ['雪山', '自然', '必玩景点'], images: ['/images/spots/lijiang/lijiang_yulong_xueshan.jpg'] },
    { id: 1603, name: '束河古镇', city: '丽江', rating: 4.6, favorites: 14567, tags: ['古镇', '休闲', '文化'], images: ['/images/spots/lijiang/lijiang_shuhe_guzhen.jpg'] },
    { id: 1604, name: '拉市海', city: '丽江', rating: 4.5, favorites: 11234, tags: ['湿地', '骑马', '自然'], images: ['/images/spots/lijiang/lijiang_lashihai.jpg'] },
    { id: 1605, name: '虎跳峡', city: '丽江', rating: 4.7, favorites: 13456, tags: ['峡谷', '徒步', '自然'], images: ['/images/spots/lijiang/lijiang_hutiaoxia.jpg'] },
    { id: 1606, name: '泸沽湖', city: '丽江', rating: 4.8, favorites: 16789, tags: ['湖泊', '风景', '摩梭'], images: ['/images/spots/lijiang/lijiang_luguhu.jpg'] },
    { id: 1607, name: '木府', city: '丽江', rating: 4.5, favorites: 8765, tags: ['历史', '文化', '建筑'], images: ['/images/spots/lijiang/lijiang_mufu.jpg'] },
    { id: 1608, name: '蓝月谷', city: '丽江', rating: 4.7, favorites: 12345, tags: ['风景', '自然', '摄影'], images: ['/images/spots/lijiang/lijiang_lanyuegu.jpg'] },
    { id: 1609, name: '黑龙潭公园', city: '丽江', rating: 4.5, favorites: 7654, tags: ['公园', '风景', '休闲'], images: ['/images/spots/lijiang/lijiang_heilongtan_gongyuan.jpg'] },
    { id: 1610, name: '白沙古镇', city: '丽江', rating: 4.6, favorites: 9876, tags: ['古镇', '文化', '艺术'], images: ['/images/spots/lijiang/lijiang_baisha_guzhen.jpg'] },
    
    // 大理
    { id: 1701, name: '大理古城', city: '大理', rating: 4.6, favorites: 18765, tags: ['古城', '历史', '文化'], images: ['/images/spots/dali/dali_dali_ancient_city.jpg'] },
    { id: 1702, name: '洱海', city: '大理', rating: 4.8, favorites: 23456, tags: ['湖泊', '风景', '必玩景点'], images: ['/images/spots/dali/dali_erhai.jpg'] },
    { id: 1703, name: '苍山', city: '大理', rating: 4.7, favorites: 15678, tags: ['登山', '自然', '风景'], images: ['/images/spots/dali/dali_cangshan.jpg'] },
    { id: 1704, name: '崇圣寺三塔', city: '大理', rating: 4.6, favorites: 13456, tags: ['历史', '文化', '建筑'], images: ['/images/spots/dali/dali_chongshengsi_santa.jpg'] },
    { id: 1705, name: '双廊古镇', city: '大理', rating: 4.5, favorites: 14567, tags: ['古镇', '洱海', '休闲'], images: ['/images/spots/dali/dali_shuanglang_guzhen.jpg'] },
    { id: 1706, name: '喜洲古镇', city: '大理', rating: 4.6, favorites: 11234, tags: ['古镇', '文化', '建筑'], images: ['/images/spots/dali/dali_xizhou_guzhen.jpg'] },
    { id: 1707, name: '蝴蝶泉', city: '大理', rating: 4.4, favorites: 8765, tags: ['自然', '传说', '风景'], images: ['/images/spots/dali/dali_hudiequan.jpg'] },
    { id: 1708, name: '南诏风情岛', city: '大理', rating: 4.5, favorites: 9876, tags: ['岛屿', '文化', '风景'], images: ['/images/spots/dali/dali_nanzhao_fengqing_dao.jpg'] },
    { id: 1709, name: '小普陀', city: '大理', rating: 4.5, favorites: 7654, tags: ['寺庙', '岛屿', '风景'], images: ['/images/spots/dali/dali_xiaoputuo.jpg'] },
    { id: 1710, name: '大理大学', city: '大理', rating: 4.6, favorites: 6543, tags: ['学府', '风景', '文化'], images: ['/images/spots/dali/dali_dali_daxue.jpg'] },
    
    // 张家界
    { id: 1801, name: '张家界国家森林公园', city: '张家界', rating: 4.9, favorites: 25678, tags: ['自然', '风景', '世界遗产'], images: ['/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg'] },
    { id: 1802, name: '天门山', city: '张家界', rating: 4.8, favorites: 19876, tags: ['登山', '风景', '玻璃栈道'], images: ['/images/spots/zhangjiajie/zhangjiajie_tianmenshan.jpg'] },
    { id: 1803, name: '袁家界', city: '张家界', rating: 4.7, favorites: 15678, tags: ['风景', '自然', '摄影'], images: ['/images/spots/zhangjiajie/zhangjiajie_yuanjiajie.jpg'] },
    { id: 1804, name: '杨家界', city: '张家界', rating: 4.6, favorites: 12345, tags: ['风景', '自然', '徒步'], images: ['/images/spots/zhangjiajie/zhangjiajie_yangjiajie.jpg'] },
    { id: 1805, name: '天子山', city: '张家界', rating: 4.7, favorites: 13456, tags: ['风景', '自然', '观景'], images: ['/images/spots/zhangjiajie/zhangjiajie_tianzishan.jpg'] },
    { id: 1806, name: '黄龙洞', city: '张家界', rating: 4.5, favorites: 9876, tags: ['溶洞', '自然', '奇观'], images: ['/images/spots/zhangjiajie/zhangjiajie_huanglongdong.jpg'] },
    { id: 1807, name: '宝峰湖', city: '张家界', rating: 4.6, favorites: 8765, tags: ['湖泊', '风景', '休闲'], images: ['/images/spots/zhangjiajie/zhangjiajie_baofenghu.jpg'] },
    { id: 1808, name: '大峡谷玻璃桥', city: '张家界', rating: 4.7, favorites: 14567, tags: ['刺激', '风景', '玻璃桥'], images: ['/images/spots/zhangjiajie/zhangjiajie_zhangjiajie_forest.jpg'] },
    { id: 1809, name: '十里画廊', city: '张家界', rating: 4.6, favorites: 11234, tags: ['风景', '自然', '观光'], images: ['/images/spots/zhangjiajie/zhangjiajie_shili_hualang.jpg'] },
    { id: 1810, name: '金鞭溪', city: '张家界', rating: 4.7, favorites: 9876, tags: ['溪流', '徒步', '自然'], images: ['/images/spots/zhangjiajie/zhangjiajie_jinbianxi.jpg'] },
    
    // 黄山
    { id: 1901, name: '黄山风景区', city: '黄山', rating: 4.9, favorites: 28765, tags: ['登山', '风景', '世界遗产'], images: ['/images/spots/huangshan/huangshan_huangshan_scenery.jpg'] },
    { id: 1902, name: '宏村', city: '黄山', rating: 4.7, favorites: 18765, tags: ['古村', '徽派', '摄影'], images: ['/images/spots/huangshan/huangshan_hongcun.jpg'] },
    { id: 1903, name: '西递', city: '黄山', rating: 4.6, favorites: 14567, tags: ['古村', '徽派', '文化'], images: ['/images/spots/huangshan/huangshan_xidi.jpg'] },
    { id: 1904, name: '屯溪老街', city: '黄山', rating: 4.5, favorites: 13456, tags: ['citywalk', '历史', '美食'], images: ['/images/spots/huangshan/huangshan_tunxi_laojie.jpg'] },
    { id: 1905, name: '翡翠谷', city: '黄山', rating: 4.6, favorites: 11234, tags: ['风景', '自然', '休闲'], images: ['/images/spots/huangshan/huangshan_feicuigu.jpg'] },
    { id: 1906, name: '呈坎', city: '黄山', rating: 4.5, favorites: 9876, tags: ['古村', '文化', '风水'], images: ['/images/spots/huangshan/huangshan_chenkan.jpg'] },
    { id: 1907, name: '唐模', city: '黄山', rating: 4.4, favorites: 7654, tags: ['古村', '园林', '文化'], images: ['/images/spots/huangshan/huangshan_tangmo.jpg'] },
    { id: 1908, name: '徽州古城', city: '黄山', rating: 4.5, favorites: 11234, tags: ['古城', '历史', '文化'], images: ['/images/spots/huangshan/huangshan_huizhou_gucheng.jpg'] },
    { id: 1909, name: '齐云山', city: '黄山', rating: 4.6, favorites: 8765, tags: ['道教', '登山', '风景'], images: ['/images/spots/huangshan/huangshan_qiyunshan.jpg'] },
    { id: 1910, name: '新安江山水画廊', city: '黄山', rating: 4.7, favorites: 9876, tags: ['风景', '游船', '摄影'], images: ['/images/spots/huangshan/huangshan_xinanjiang_shanshui_hualang.jpg'] },
    
    // 九寨沟
    { id: 2001, name: '九寨沟', city: '九寨沟', rating: 4.9, favorites: 25678, tags: ['自然', '风景', '世界遗产'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_jiuzhaigou_valley.jpg'] },
    { id: 2002, name: '五花海', city: '九寨沟', rating: 4.8, favorites: 18765, tags: ['湖泊', '风景', '摄影'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_wuhuahai.jpg'] },
    { id: 2003, name: '诺日朗瀑布', city: '九寨沟', rating: 4.7, favorites: 15678, tags: ['瀑布', '自然', '壮观'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_nuorilang_pubu.jpg'] },
    { id: 2004, name: '长海', city: '九寨沟', rating: 4.7, favorites: 13456, tags: ['湖泊', '风景', '自然'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_changhai.jpg'] },
    { id: 2005, name: '熊猫海', city: '九寨沟', rating: 4.6, favorites: 11234, tags: ['湖泊', '风景', '自然'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_xiongmaohai.jpg'] },
    { id: 2006, name: '镜海', city: '九寨沟', rating: 4.7, favorites: 9876, tags: ['湖泊', '倒影', '风景'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_jinghai.jpg'] },
    { id: 2007, name: '树正群海', city: '九寨沟', rating: 4.6, favorites: 8765, tags: ['湖泊', '风景', '自然'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_shuzheng_qunhai.jpg'] },
    { id: 2008, name: '珍珠滩瀑布', city: '九寨沟', rating: 4.7, favorites: 11234, tags: ['瀑布', '风景', '自然'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_zhenzhutan_pubu.jpg'] },
    { id: 2009, name: '芦苇海', city: '九寨沟', rating: 4.5, favorites: 7654, tags: ['湖泊', '风景', '自然'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_luweihai.jpg'] },
    { id: 2010, name: '火花海', city: '九寨沟', rating: 4.6, favorites: 8765, tags: ['湖泊', '风景', '自然'], images: ['/images/spots/jiuzhaigou/jiuzhaigou_huohuahai.jpg'] },
  ]
  
  return mockSpots.filter(s => s.city === city.value)
}

// 检查是否已选择
const isSelected = (spotId) => {
  return selectedSpots.value.some(s => s.id === spotId)
}

// 切换选择
const toggleSpot = (spot) => {
  const index = selectedSpots.value.findIndex(s => s.id === spot.id)
  if (index > -1) {
    selectedSpots.value.splice(index, 1)
  } else {
    // 保存完整的景点对象
    selectedSpots.value.push({
      id: spot.id,
      name: spot.name,
      rating: spot.rating,
      favorites: spot.favorites,
      tags: spot.tags,
      image: spot.images?.[0] || `/images/cities/${getCityImageName(spot.city)}`,
      duration: spot.duration || '2小时',
      location: spot.location
    })
  }
}

// 清空选择
const clearSelection = () => {
  selectedSpots.value = []
}

// 创建行程
const createTrip = () => {
  if (selectedSpots.value.length === 0) {
    ElMessage.warning('请至少选择一个景点')
    return
  }
  
  // 保存选择的数据（保存完整的景点对象数组）
  localStorage.setItem('selectedSpots', JSON.stringify(selectedSpots.value))
  localStorage.setItem('tripCity', city.value)
  localStorage.setItem('tripDays', days.value)
  localStorage.setItem('tripPreferences', preferences.value.join(','))
  
  // 跳转到行程详情页，使用 new 作为 id 表示新行程
  router.push(`/trip/new?city=${city.value}&days=${days.value}&preferences=${preferences.value.join(',')}`)
}

// 初始化
onMounted(() => {
  city.value = route.query.city || '北京'
  days.value = parseInt(route.query.days) || 3
  const prefStr = route.query.preferences || ''
  preferences.value = prefStr.split(',').filter(p => p)
  
  console.log('初始化 - 城市:', city.value, '偏好:', preferences.value)
  
  loadSpots()
})

// 当页面重新激活时刷新数据
onActivated(() => {
  // 重新从route获取preferences，防止丢失
  const prefStr = route.query.preferences || ''
  preferences.value = prefStr.split(',').filter(p => p)
  loadSpots()
})
</script>

<style scoped>
.spot-recommend-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
  color: #fff;
  padding-bottom: 100px;
}

.page-content {
  padding: 90px 40px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #00d4ff, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
}

.selected-count {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 12px;
  margin-bottom: 20px;
  border: 1px solid rgba(0, 212, 255, 0.2);
}

.clear-btn {
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: transparent;
  color: #fff;
  font-size: 13px;
  cursor: pointer;
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.spot-card {
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.spot-card:hover {
  transform: translateY(-5px);
  border-color: rgba(0, 212, 255, 0.3);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.15);
}

.spot-card.selected {
  border-color: #00d4ff;
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

.spot-image {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.spot-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.spot-card:hover .spot-image img {
  transform: scale(1.05);
}

.spot-rank {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  color: #000;
}

.select-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #00d4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #fff;
}

.spot-info {
  padding: 16px;
}

.spot-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 10px;
}

.spot-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.stat-icon {
  font-size: 14px;
}

.stat-value {
  font-weight: 600;
}

.tag-match {
  margin-bottom: 10px;
}

.match-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(0, 212, 255, 0.2);
  border-radius: 10px;
  font-size: 12px;
  color: #00d4ff;
}

.spot-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.tag {
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.recommend-reason {
  padding: 8px 12px;
  background: rgba(123, 44, 191, 0.2);
  border-radius: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-icon {
  font-size: 60px;
  display: block;
  margin-bottom: 20px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #00d4ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px 40px;
  background: rgba(10, 10, 26, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(0, 212, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
}

.bar-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bar-info span {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.days-info {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.create-trip-btn {
  padding: 12px 30px;
  background: linear-gradient(135deg, #00d4ff, #7b2cbf);
  border: none;
  border-radius: 25px;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-trip-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
}

@media (max-width: 768px) {
  .page-content {
    padding: 90px 20px 40px;
  }
  
  .spots-grid {
    grid-template-columns: 1fr;
  }
  
  .bottom-bar {
    padding: 15px 20px;
  }
}
</style>
