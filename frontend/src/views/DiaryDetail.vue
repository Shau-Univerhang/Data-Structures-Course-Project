<template>
  <div class="diary-detail-page">
    <Navbar />
    
    <main class="page-content">
      <div class="detail-container">
        <!-- 返回按钮 -->
        <button class="back-btn" @click="$router.back()">
          ← 返回
        </button>
        
        <!-- 日记内容 -->
        <article class="diary-article">
          <header class="diary-header">
            <h1 class="diary-title">{{ diary.title }}</h1>
            <div class="diary-meta">
              <span class="meta-item">
                <span class="meta-icon">👤</span>
                {{ diary.username || '作者' }}
              </span>
              <span class="meta-item">
                <span class="meta-icon">📅</span>
                {{ formatDate(diary.created_at) }}
              </span>
              <span class="meta-item">
                <span class="meta-icon">👁️</span>
                {{ diary.view_count || 0 }} 阅读
              </span>
              <span class="meta-item">
                <span class="meta-icon">⭐</span>
                {{ (diary.avg_rating || 0).toFixed(1) }} ({{ diary.rating_count || 0 }})
              </span>
            </div>
          </header>
          
          <div class="diary-images" v-if="diary.images && diary.images.length">
            <div class="image-grid">
              <img 
                v-for="(img, index) in diary.images" 
                :key="index"
                :src="img" 
                :alt="diary.title"
                class="diary-image"
              />
            </div>
          </div>
          
          <div class="diary-body">
            <div class="diary-content" v-html="renderContent(diary.content)"></div>
          </div>
        </article>
        
        <!-- 评论和评分组件 -->
        <CommentsRatings :diary-id="diaryId" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Navbar from '../components/Navbar.vue'
import CommentsRatings from '../components/CommentsRatings.vue'

const route = useRoute()
const diaryId = ref(parseInt(route.params.id))
const diary = ref({
  id: diaryId.value,
  title: '',
  content: '',
  username: '',
  created_at: '',
  view_count: 0,
  avg_rating: 0,
  rating_count: 0,
  images: []
})

// Mock 数据 - 3篇高质量示例日记
const mockDiaries = {
  1: {
    id: 1,
    title: ' Kyoto 京都：千年古都的秋日私语',
    content: `【前言】
京都，这座承载着日本千年历史的古都，每一个角落都散发着独特的魅力。这次秋日的京都之行，让我深深沉醉在红叶与古寺的交织中。

【Day 1 - 初抵京都】
清晨从大阪关西机场出发，乘坐Haruka特急列车，约75分钟便抵达京都站。一出车站，就能感受到这座城市特有的宁静与庄重。

🏨 住宿推荐：
选择了位于祇园附近的传统日式旅馆"花见小路庵"。推开木质拉门，榻榻米的气息扑面而来，窗外是精致的枯山水庭院。

【Day 2 - 清水寺与二年坂】
清晨六点起床，赶在游客大军到来之前前往清水寺。晨光中的清水舞台被红叶环绕，那种美让人屏息。

📸 拍照Tips：
- 清水舞台正面是经典机位，但人太多
- 推荐绕到舞台侧面，可以拍到红叶与建筑的层次感
- 二年坂的清晨几乎没有游客，石板路与传统町家建筑相得益彰

【Day 3 - 岚山竹林与渡月桥】
岚山的竹林小径是此行最期待的景点之一。高耸入云的竹子形成天然的绿色隧道，阳光透过竹叶洒下斑驳光影。

🍜 美食推荐：
- 岚山よしむら：手工荞麦面，窗外就是渡月桥
- % Arabica：网红咖啡店，但景色确实值得

【Day 4 - 金阁寺与龙安寺】
金阁寺的倒影在镜湖池中完美呈现，这座被金箔覆盖的楼阁在阳光下熠熠生辉。

龙安寺的枯山水庭院则是另一种美。十五块石头精心布置在白砂之中，坐在廊下静静凝视，内心逐渐平静。

【实用贴士】
🚇 交通：购买京都巴士一日券（700日元），基本可以覆盖所有景点
💰 预算：4天3夜约8万日元（含住宿、餐饮、交通）
📅 最佳季节：11月中旬至12月上旬（红叶季）

【总结】
京都的美，在于它的克制与留白。无论是枯山水的禅意，还是町家建筑的素雅，都在诉说着一种"少即是多"的美学理念。这座城市值得慢慢品味，而不是匆匆打卡。`,
    username: '旅行摄影师小林',
    created_at: '2024-11-15T08:30:00',
    view_count: 3280,
    avg_rating: 4.9,
    rating_count: 156,
    images: [
      'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80',
      'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800&q=80',
      'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800&q=80'
    ],
    diary_type: 'travel'
  },
  2: {
    id: 2,
    title: '成都美食探店：藏在巷子里的烟火气',
    content: `【探店前言】
成都是一座来了就不想走的城市，而让我留恋的，正是那些藏在巷子深处的美食。这次用三天时间，深度探索了本地人最爱的几家小店。

【第一站：冒椒火辣】
📍 地址：奎星楼街23号
⏰ 营业时间：11:00-22:00
💰 人均：60元

这家串串店藏在奎星楼街的深处，店面不大，但总是排着长队。他们的秘制牛油锅底是灵魂，麻辣鲜香，回味悠长。

🍢 必点推荐：
- 牛肉串：腌制入味，涮烫后嫩滑多汁
- 毛肚：七上八下，口感脆爽
- 脑花：处理得很干净，入口即化
- 兔腰：成都特色，勇敢者必试

【第二站：洞子口张老二凉粉】
📍 地址：文殊院街39号
⏰ 营业时间：08:00-20:00
💰 人均：15元

开了三十多年的老字号，是成都人从小吃到大的味道。黄凉粉和白凉粉各有千秋，配上特制的红油辣椒，简单却让人欲罢不能。

【第三站：陈麻婆豆腐】
📍 地址：西玉龙街197号
⏰ 营业时间：11:00-21:00
💰 人均：50元

麻婆豆腐的发源地，这里的麻婆豆腐堪称教科书级别。豆腐嫩滑，肉末酥香，花椒的麻与辣椒的辣完美融合。

🍲 除了麻婆豆腐，还推荐：
- 夫妻肺片：红油浸润，麻辣鲜香
- 回锅肉：肥而不腻，酱香浓郁
- 宫保鸡丁：酸甜微辣，花生酥脆

【第四站：贺记蛋烘糕】
📍 地址：文庙西街1号附8号
⏰ 营业时间：10:00-21:00
💰 人均：10元

蛋烘糕是成都的传统小吃，贺记是其中的佼佼者。现点现做，外皮金黄酥脆，内里松软香甜。

🥞 口味推荐：
- 肉松沙拉：咸甜交织，层次丰富
- 奶油奥利奥：甜品控必点
- 麻辣牛肉：成都特色，意外的好吃

【第五站：蜀大侠火锅】
📍 地址：春熙路店（多家分店）
⏰ 营业时间：10:00-02:00
💰 人均：120元

来成都怎能不体验火锅？蜀大侠的装修很有特色，江湖气息浓厚。菜品新鲜，服务周到，是游客体验成都火锅的好选择。

🌶️ 锅底选择：
建议选鸳鸯锅，红锅体验正宗麻辣，白锅可以涮蔬菜解辣。

【探店心得】
成都的美食，不在于装修有多豪华，而在于那份烟火气和人情味。老板会热情地跟你聊天，推荐今天的新鲜食材。这种氛围，是连锁餐厅永远给不了的。

【实用信息】
🚇 交通：地铁+共享单车是最佳组合
💰 总预算：3天约800元（纯餐饮）
⚠️ 提醒：成都美食偏辣，肠胃敏感者备好肠胃药`,
    username: '吃货小王',
    created_at: '2024-12-01T14:20:00',
    view_count: 2156,
    avg_rating: 4.8,
    rating_count: 89,
    images: [
      'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&q=80',
      'https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=800&q=80',
      'https://images.unsplash.com/photo-1594007654729-407eedc4be65?w=800&q=80'
    ],
    diary_type: 'food'
  },
  3: {
    id: 3,
    title: '冰岛环岛自驾：追逐极光的14天',
    content: `【行前准备】
冰岛，这个被称为"火与冰之国"的地方，一直是我旅行清单上的必去之地。经过半年的筹备，终于踏上了这片神奇的土地。

✈️ 机票：北京-哥本哈根-雷克雅未克，往返约8000元
🚗 租车：租了辆四驱SUV，14天约12000元（含全险）
🏨 住宿：混合预订了酒店和民宿，平均每晚800元

【Day 1-2 雷克雅未克】
首都雷克雅未克是世界上最北的首都，人口只有12万，却充满了艺术气息。

📍 必去景点：
- 哈尔格林姆教堂：雷克雅未克地标，登顶可俯瞰全城
- 太阳航海者雕塑：海边的不锈钢雕塑，象征着维京人的探索精神
- 彩虹街：色彩斑斓的街道，拍照圣地

【Day 3-4 黄金圈】
黄金圈是冰岛最经典的路线，包含三个主要景点。

🌊 辛格维利尔国家公园：
欧亚板块和北美板块的分界线就在这里，可以清晰地看到板块漂移形成的裂缝。

⛲ 间歇泉：
每隔5-10分钟喷发一次，水柱高达30米。等待喷发的那一刻，所有人都屏住呼吸。

🌈 黄金瀑布：
冰岛最大的断层瀑布，阳光照射下经常出现彩虹。

【Day 5-7 南岸风光】
南岸是冰岛景观最丰富的地区，瀑布、黑沙滩、冰川应有尽有。

💦 塞里雅兰瀑布：
可以走到瀑布后面，从内部欣赏水帘的壮观。

🖤 维克黑沙滩：
黑色的火山沙与白色的海浪形成强烈对比，玄武岩柱群更是拍照的绝佳背景。

🏔️ 瓦特纳冰川：
参加了冰川徒步团，穿上冰爪，在千年冰川上行走，那种震撼难以言表。

【Day 8-10 冰河湖与东部峡湾】
杰古沙龙冰河湖是此行的高潮。蓝色的浮冰漂浮在湖面上，像是大自然雕刻的艺术品。

🦭 幸运的话，还能看到 seals 在冰块上晒太阳。

东部峡湾游客稀少，但风景绝不逊色。蜿蜒的海岸公路，每一个转弯都是一幅画。

【Day 11-12 米湖与北部】
米湖地区有着月球般的地貌，到处都是地热活动和火山岩。

🌋 克拉夫拉火山口：
翠绿色的湖水躺在火山口中央，像是大地的眼睛。

♨️ 米湖温泉：
比蓝湖更小众，但体验同样出色。在零下的气温中泡着温泉，看着周围的雪景，妙不可言。

【Day 13-14 西部与斯奈山半岛】
斯奈山半岛被称为"冰岛的缩影"，因为这里汇集了冰岛几乎所有的地貌特征。

⛰️ 草帽山：
冰岛被拍摄最多的山峰，瀑布与山峰的组合堪称完美。

🌌 极光之夜：
在环岛的最后两晚，终于等来了极光。绿色的光带在夜空中舞动，像是上天的馈赠。

【摄影心得】
📷 设备：
- 相机：Sony A7R4
- 镜头：16-35mm f/2.8（广角必备）、70-200mm f/2.8
- 三脚架：拍摄极光和瀑布必备
- 备用电池：低温下电池消耗很快

🎨 拍摄技巧：
- 瀑布用慢门（1-2秒）拍出丝绸效果
- 极光ISO 1600-3200，曝光5-15秒
- 白天光线变化快，随时注意调整参数

【实用贴士】
💰 总预算：14天约3.5万元（不含装备）
🌡️ 天气：10月的冰岛已经入冬，气温在0-10度之间
👕 穿衣：三层穿衣法，防水外套必备
⛽ 加油：全程自助加油，记得带芯片信用卡

【写在最后】
冰岛教会我敬畏自然。在这片土地上，人类是如此渺小，而自然是如此伟大。那些瀑布、冰川、极光，都是大自然给我们的礼物。希望这片土地能一直保持它的纯净，也希望每一个到访的人都能爱护它。`,
    username: '极地探险者',
    created_at: '2024-10-20T10:00:00',
    view_count: 5620,
    avg_rating: 5.0,
    rating_count: 234,
    images: [
      'https://images.unsplash.com/photo-1531366936337-7c912a4589a7?w=800&q=80',
      'https://images.unsplash.com/photo-1520769945061-0a448c463865?w=800&q=80',
      'https://images.unsplash.com/photo-1476610182048-b716b8518aae?w=800&q=80',
      'https://images.unsplash.com/photo-1518182170546-0766bc6f9213?w=800&q=80'
    ],
    diary_type: 'travel'
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const renderContent = (content) => {
  if (!content) return ''
  // 简单的 Markdown 渲染
  return content
    .replace(/\n/g, '<br/>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

const loadDiary = async () => {
  try {
    // 先尝试从后端获取
    const response = await fetch(`http://localhost:8000/api/diaries/${diaryId.value}`)
    if (response.ok) {
      diary.value = await response.json()
      
      // 增加浏览量
      fetch(`http://localhost:8000/api/diaries/${diaryId.value}/view`, {
        method: 'POST'
      }).catch(() => {})
    } else {
      // 后端没有数据，使用 Mock 数据
      if (mockDiaries[diaryId.value]) {
        diary.value = mockDiaries[diaryId.value]
      } else {
        // 如果 ID 不在 mock 数据中，随机返回一篇
        const randomId = [1, 2, 3][Math.floor(Math.random() * 3)]
        diary.value = { ...mockDiaries[randomId], id: diaryId.value }
      }
    }
  } catch (error) {
    console.error('加载日记失败:', error)
    // 使用 Mock 数据
    if (mockDiaries[diaryId.value]) {
      diary.value = mockDiaries[diaryId.value]
    } else {
      // 如果 ID 不在 mock 数据中，随机返回一篇
      const randomId = [1, 2, 3][Math.floor(Math.random() * 3)]
      diary.value = { ...mockDiaries[randomId], id: diaryId.value }
    }
  }
}

onMounted(() => {
  loadDiary()
})
</script>

<style scoped>
.diary-detail-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.page-content {
  padding: 2rem;
  min-height: calc(100vh - 60px);
}

.detail-container {
  max-width: 900px;
  margin: 0 auto;
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 1.5rem;
  transition: background 0.3s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.diary-article {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.diary-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #f3f4f6;
}

.diary-title {
  font-size: 2rem;
  color: #1f2937;
  margin: 0 0 1rem 0;
  line-height: 1.3;
}

.diary-meta {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.meta-icon {
  font-size: 1.125rem;
}

.diary-images {
  margin-bottom: 2rem;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.diary-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.3s;
}

.diary-image:hover {
  transform: scale(1.05);
}

.diary-body {
  line-height: 1.8;
}

.diary-content {
  color: #374151;
  font-size: 1.0625rem;
  white-space: pre-wrap;
}
</style>
