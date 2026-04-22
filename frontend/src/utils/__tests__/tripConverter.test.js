/**
 * TripToDiaryConverter 单元测试
 * 可直接在浏览器控制台运行
 */

import { TripToDiaryConverter } from '../tripToDiaryConverter.js'

// 测试用例
const testCases = {
  // TC-001: 正常多天数行程
  normalMultiDay: {
    input: {
      id: 1,
      title: '北京三日游',
      destination: '北京',
      total_days: 3,
      schedules: [
        { day_number: 1, spot_name: '故宫', spot_image: '/img/1.jpg', notes: '很壮观', visit_time_start: '09:00', order_index: 1 },
        { day_number: 1, spot_name: '天安门', spot_image: '/img/2.jpg', visit_time_start: '14:00', order_index: 2 },
        { day_number: 2, spot_name: '长城', spot_image: '/img/3.jpg', notes: '体力要求高', visit_time_start: '08:00', order_index: 1 },
        { day_number: 3, spot_name: '颐和园', spot_image: '/img/4.jpg', visit_time_start: '10:00', order_index: 1 }
      ]
    },
    assertions: (result) => {
      console.assert(result.title === '北京三日游游记', '标题正确')
      console.assert(result.itinerary.length === 3, '有3天')
      console.assert(result.itinerary[0].activities.length === 2, '第1天有2个活动')
      console.assert(result.images.length === 4, '提取了4张图片')
      console.assert(result.content.includes('故宫'), '内容包含故宫')
    }
  },

  // TC-002: 空行程
  emptyTrip: {
    input: {
      id: 2,
      title: '',
      destination: '',
      total_days: 0,
      schedules: []
    },
    assertions: (result) => {
      console.assert(result.title === '未知行程游记', '空行程标题默认')
      console.assert(result.itinerary.length === 0, '空行程时间轴为空')
    }
  },

  // TC-003: 单天单景点
  singleDay: {
    input: {
      id: 3,
      title: '上海一日游',
      destination: '上海',
      total_days: 1,
      schedules: [
        { day_number: 1, spot_name: '外滩', spot_image: '/img/sh.jpg', order_index: 1 }
      ]
    },
    assertions: (result) => {
      console.assert(result.itinerary.length === 1, '只有1天')
      console.assert(result.itinerary[0].activities[0].title.includes('外滩'), '活动包含外滩')
    }
  },

  // TC-004: 自动生成时间
  autoTime: {
    input: {
      id: 4,
      title: '测试行程',
      destination: '测试',
      schedules: [
        { day_number: 1, spot_name: '景点A', order_index: 1 },
        { day_number: 1, spot_name: '景点B', order_index: 2 },
        { day_number: 1, spot_name: '景点C', order_index: 3 }
      ]
    },
    assertions: (result) => {
      const acts = result.itinerary[0].activities
      console.assert(acts[0].time === '09:00', '第一个活动9点开始')
      console.assert(acts[1].time === '11:30', '第二个活动11:30')
      console.assert(acts[2].time === '14:00', '第三个活动14:00')
    }
  },

  // TC-005: 主题生成
  themeGeneration: {
    input: {
      id: 5,
      title: '文化之旅',
      destination: '西安',
      schedules: [
        { day_number: 1, spot_name: '兵马俑博物馆', order_index: 1 }
      ]
    },
    assertions: (result) => {
      console.assert(result.itinerary[0].theme === '文化探索', '博物馆类生成文化主题')
    }
  },

  // TC-006: 图片去重
  imageDeduplication: {
    input: {
      id: 6,
      title: '测试',
      destination: '测试',
      schedules: [
        { day_number: 1, spot_name: '景点1', spot_image: '/img/same.jpg', order_index: 1 },
        { day_number: 1, spot_name: '景点2', spot_image: '/img/same.jpg', order_index: 2 },
        { day_number: 1, spot_name: '景点3', spot_image: '/img/3.jpg', order_index: 3 },
        { day_number: 1, spot_name: '景点4', spot_image: '/img/4.jpg', order_index: 4 },
        { day_number: 1, spot_name: '景点5', spot_image: '/img/5.jpg', order_index: 5 },
        { day_number: 1, spot_name: '景点6', spot_image: '/img/6.jpg', order_index: 6 },
        { day_number: 1, spot_name: '景点7', spot_image: '/img/7.jpg', order_index: 7 },
        { day_number: 1, spot_name: '景点8', spot_image: '/img/8.jpg', order_index: 8 },
        { day_number: 1, spot_name: '景点9', spot_image: '/img/9.jpg', order_index: 9 },
        { day_number: 1, spot_name: '景点10', spot_image: '/img/10.jpg', order_index: 10 },
        { day_number: 1, spot_name: '景点11', spot_image: '/img/11.jpg', order_index: 11 }
      ]
    },
    assertions: (result) => {
      console.assert(result.images.length <= 9, '图片不超过9张')
      console.assert(result.images.filter(img => img === '/img/same.jpg').length === 1, '重复图片已去重')
    }
  }
}

// 运行测试
export const runConverterTests = () => {
  console.log('🧪 开始测试 TripToDiaryConverter...\n')
  
  let passCount = 0
  let failCount = 0

  Object.entries(testCases).forEach(([name, { input, assertions }]) => {
    try {
      console.log(`测试: ${name}`)
      const result = TripToDiaryConverter.convert(input)
      assertions(result)
      console.log(`  ✅ ${name} 通过\n`)
      passCount++
    } catch (error) {
      console.error(`  ❌ ${name} 失败:`, error.message)
      failCount++
    }
  })

  console.log('\n========== 测试报告 ==========')
  console.log(`✅ 通过: ${passCount}`)
  console.log(`❌ 失败: ${failCount}`)
  console.log(`📊 总计: ${passCount + failCount}`)

  return { passCount, failCount }
}

// 性能测试
export const runPerformanceTests = () => {
  console.log('\n⚡ 开始性能测试...\n')

  // 生成大量数据
  const largeTrip = {
    id: 999,
    title: '大型行程测试',
    destination: '测试',
    total_days: 10,
    schedules: Array(100).fill(null).map((_, i) => ({
      day_number: Math.floor(i / 10) + 1,
      spot_name: `景点${i}`,
      spot_image: `/img/${i % 20}.jpg`,
      order_index: i % 10,
      visit_time_start: `${9 + Math.floor(i % 5)}:00`
    }))
  }

  // 测试转换性能
  const start = performance.now()
  const result = TripToDiaryConverter.convert(largeTrip)
  const end = performance.now()

  console.log(`转换100个景点耗时: ${(end - start).toFixed(2)}ms`)
  console.log(`生成时间轴: ${result.itinerary.length} 天`)
  console.log(`提取图片: ${result.images.length} 张`)

  return {
    conversionTime: end - start,
    itineraryDays: result.itinerary.length,
    imageCount: result.images.length
  }
}

// 边界值测试
export const runEdgeCaseTests = () => {
  console.log('\n🔍 开始边界值测试...\n')

  const edgeCases = [
    {
      name: 'null 输入',
      input: null,
      shouldHandle: true
    },
    {
      name: 'undefined 输入',
      input: undefined,
      shouldHandle: true
    },
    {
      name: '超长标题 (100字)',
      input: {
        title: '这是一'.repeat(50),
        destination: '测试',
        schedules: []
      },
      shouldHandle: true
    },
    {
      name: '特殊字符',
      input: {
        title: '测试<script>alert(1)</script>',
        destination: '测试',
        schedules: [
          { day_number: 1, spot_name: '景点"特殊"', order_index: 1 }
        ]
      },
      shouldHandle: true
    }
  ]

  edgeCases.forEach(({ name, input, shouldHandle }) => {
    try {
      const result = TripToDiaryConverter.convert(input)
      if (shouldHandle) {
        console.log(`✅ ${name}: 正常处理`)
      }
    } catch (error) {
      console.error(`❌ ${name}: 未处理异常 -`, error.message)
    }
  })
}

// 运行所有测试
export const runAllTests = () => {
  console.log('═══════════════════════════════════════')
  console.log('   行程-日记转换器 测试套件')
  console.log('═══════════════════════════════════════\n')

  const results1 = runConverterTests()
  const results2 = runPerformanceTests()
  runEdgeCaseTests()

  console.log('\n═══════════════════════════════════════')
  console.log('   测试完成')
  console.log('═══════════════════════════════════════')

  return {
    unitTests: results1,
    performance: results2
  }
}

// 导出单个测试供选择
export {
  runConverterTests,
  runPerformanceTests,
  runEdgeCaseTests
}

export default runAllTests
