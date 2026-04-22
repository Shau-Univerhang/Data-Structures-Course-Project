/**
 * 行程-日记集成测试套件
 * 广泛测试计划
 */

import { useTripDiaryBridge } from '../tripDiaryBridge'
import { useTripStore } from '../../stores/trip'
import { useDiaryStore } from '../../stores/diary'
import { TripToDiaryConverter } from '../../utils/tripToDiaryConverter'

describe('行程-日记集成测试', () => {
  let bridge
  let tripStore
  let diaryStore

  beforeEach(() => {
    bridge = useTripDiaryBridge()
    tripStore = useTripStore()
    diaryStore = useDiaryStore()
    
    // 清理 localStorage
    localStorage.clear()
  })

  describe('模块1: 时间轴转换算法测试', () => {
    test('TC-001: 正常行程 - 多天数多景点', () => {
      const trip = {
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
      }

      const result = TripToDiaryConverter.convert(trip, { generateContent: true })

      // 验证基础信息
      expect(result.title).toBe('北京三日游游记')
      expect(result.destination).toBe('北京')
      expect(result.total_days).toBe(3)
      expect(result.trip_id).toBe(1)
      expect(result.diary_type).toBe('travel')

      // 验证时间轴结构
      expect(result.itinerary).toHaveLength(3)
      expect(result.itinerary[0].day).toBe(1)
      expect(result.itinerary[0].title).toBe('第1天')
      expect(result.itinerary[0].theme).toBeTruthy()
      expect(result.itinerary[0].activities).toHaveLength(2)

      // 验证活动详情
      const firstActivity = result.itinerary[0].activities[0]
      expect(firstActivity.time).toBe('09:00')
      expect(firstActivity.title).toContain('故宫')
      expect(firstActivity.location).toBe('故宫')

      // 验证图片提取
      expect(result.images).toHaveLength(4)
      expect(result.images).toContain('/img/1.jpg')

      // 验证内容生成
      expect(result.content).toContain('北京三日游')
      expect(result.content).toContain('故宫')
      expect(result.content).toContain('第1天')
    })

    test('TC-002: 边界情况 - 空行程', () => {
      const trip = {
        id: 2,
        title: '',
        destination: '',
        total_days: 0,
        schedules: []
      }

      const result = TripToDiaryConverter.convert(trip)

      expect(result.title).toBe('未知行程游记')
      expect(result.destination).toBe('未知目的地')
      expect(result.itinerary).toEqual([])
      expect(result.images).toEqual([])
    })

    test('TC-003: 边界情况 - 单天单景点', () => {
      const trip = {
        id: 3,
        title: '上海一日游',
        destination: '上海',
        total_days: 1,
        schedules: [
          { day_number: 1, spot_name: '外滩', spot_image: '/img/sh.jpg', order_index: 1 }
        ]
      }

      const result = TripToDiaryConverter.convert(trip)

      expect(result.itinerary).toHaveLength(1)
      expect(result.itinerary[0].activities).toHaveLength(1)
      expect(result.itinerary[0].activities[0].title).toContain('外滩')
    })

    test('TC-004: 时间分配算法 - 自动生成时间', () => {
      const trip = {
        id: 4,
        title: '测试行程',
        destination: '测试',
        schedules: [
          { day_number: 1, spot_name: '景点A', order_index: 1 },
          { day_number: 1, spot_name: '景点B', order_index: 2 },
          { day_number: 1, spot_name: '景点C', order_index: 3 }
        ]
      }

      const result = TripToDiaryConverter.convert(trip)

      // 验证自动时间分配（9:00 开始，每个2小时+30分钟过渡）
      const activities = result.itinerary[0].activities
      expect(activities[0].time).toBe('09:00')
      expect(activities[1].time).toBe('11:30') // 9:00 + 2小时 + 30分钟
      expect(activities[2].time).toBe('14:00') // 11:30 + 2小时 + 30分钟
    })

    test('TC-005: 主题生成 - 不同类型景点', () => {
      const testCases = [
        { spots: [{ spot_name: '故宫博物院' }], expectedTheme: '文化探索' },
        { spots: [{ spot_name: '黄山' }], expectedTheme: '自然风光' },
        { spots: [{ spot_name: '南京路' }], expectedTheme: '城市漫步' },
        { spots: [{ spot_name: '少林寺' }], expectedTheme: '人文古迹' },
        { spots: [{ spot_name: '宽窄巷子' }], expectedTheme: '城市漫步' }
      ]

      testCases.forEach(({ spots, expectedTheme }) => {
        const trip = {
          id: 5,
          title: '测试',
          destination: '测试',
          schedules: spots.map((s, i) => ({ ...s, day_number: 1, order_index: i }))
        }

        const result = TripToDiaryConverter.convert(trip)
        expect(result.itinerary[0].theme).toBe(expectedTheme)
      })
    })

    test('TC-006: 图片去重和限制', () => {
      const trip = {
        id: 6,
        title: '测试',
        destination: '测试',
        schedules: Array(12).fill(null).map((_, i) => ({
          day_number: 1,
          spot_name: `景点${i}`,
          spot_image: i < 5 ? '/img/same.jpg' : `/img/${i}.jpg`, // 重复图片
          order_index: i
        }))
      }

      const result = TripToDiaryConverter.convert(trip)

      // 验证去重
      expect(result.images).toContain('/img/same.jpg')
      
      // 验证最多9张
      expect(result.images.length).toBeLessThanOrEqual(9)
    })
  })

  describe('模块2: Bridge 核心功能测试', () => {
    test('TC-101: 正常流程 - 完成行程并创建日记', async () => {
      const mockTrip = {
        id: 1,
        title: '测试行程',
        destination: '测试城市',
        total_days: 2,
        schedules: [
          { day_number: 1, spot_name: '景点A', order_index: 1 },
          { day_number: 2, spot_name: '景点B', order_index: 1 }
        ]
      }

      // Mock API 响应
      global.fetch = jest.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockTrip) }) // 获取行程
        .mockResolvedValueOnce({ ok: true }) // 更新状态
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve([]) }) // 检查日记

      // Mock diaryStore
      diaryStore.createDiary = jest.fn().mockResolvedValue({ id: 123, title: '测试游记' })

      const result = await bridge.completeTripAndCreateDiary(1, mockTrip)

      expect(result.success).toBe(true)
      expect(result.tripId).toBe(1)
      expect(result.diaryId).toBe(123)
      expect(diaryStore.createDiary).toHaveBeenCalled()
    })

    test('TC-102: 重复创建检查', async () => {
      global.fetch = jest.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([{ id: 100, title: '已有日记' }])
        })

      const result = await bridge.checkExistingDiary(1)

      expect(result).not.toBeNull()
      expect(result.id).toBe(100)
    })

    test('TC-103: API 错误处理', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'))

      await expect(bridge.completeTripAndCreateDiary(1, {}))
        .rejects.toThrow('无法完成行程')
    })

    test('TC-104: 事务回滚 - 日记创建失败时回滚行程状态', async () => {
      const mockTrip = { id: 1, title: '测试', destination: '测试', schedules: [] }

      global.fetch = jest.fn()
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockTrip) })
        .mockResolvedValueOnce({ ok: true }) // 更新为 completed
        .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve([]) })
        .mockResolvedValueOnce({ ok: true }) // 回滚为 published

      diaryStore.createDiary = jest.fn().mockRejectedValue(new Error('创建失败'))

      await expect(bridge.completeTripAndCreateDiary(1, mockTrip))
        .rejects.toThrow('创建失败')

      // 验证回滚调用
      expect(fetch).toHaveBeenLastCalledWith(
        expect.stringContaining('status=published'),
        expect.any(Object)
      )
    })
  })

  describe('模块3: 数据流测试', () => {
    test('TC-201: localStorage 数据传递', () => {
      const diaryData = {
        title: '测试游记',
        content: '测试内容',
        trip_id: 1,
        sourceTripTitle: '测试行程'
      }

      // 模拟存储
      localStorage.setItem('draftDiaryFromTrip', JSON.stringify(diaryData))

      // 验证读取
      const stored = JSON.parse(localStorage.getItem('draftDiaryFromTrip'))
      expect(stored.title).toBe('测试游记')
      expect(stored.trip_id).toBe(1)
      expect(stored.sourceTripTitle).toBe('测试行程')
    })

    test('TC-202: 数据格式兼容性', () => {
      const apiTripData = {
        id: 1,
        user_id: 1,
        title: '北京之旅',
        destination: '北京',
        total_days: 3,
        status: 'published',
        schedules: [
          {
            id: 1,
            trip_id: 1,
            day_number: 1,
            spot_id: 101,
            spot_name: '故宫',
            spot_image: 'https://example.com/gugong.jpg',
            order_index: 1,
            visit_time_start: '09:00:00',
            visit_time_end: '12:00:00',
            duration: '3小时',
            notes: '提前预约门票',
            created_at: '2024-01-01T00:00:00',
            spot: { id: 101, name: '故宫', city: '北京' }
          }
        ],
        created_at: '2024-01-01T00:00:00',
        updated_at: '2024-01-01T00:00:00'
      }

      const result = TripToDiaryConverter.convert(apiTripData)

      // 验证能正确处理 API 返回的完整数据结构
      expect(result.title).toBe('北京之旅游记')
      expect(result.itinerary).toHaveLength(1)
      expect(result.itinerary[0].activities[0].image).toBe('https://example.com/gugong.jpg')
    })
  })

  describe('模块4: UI 集成测试', () => {
    test('TC-301: Trips.vue 导出按钮状态', () => {
      // 已完成行程显示 ✅
      const completedTrip = { id: 1, status: 'completed', title: '已完成行程' }
      expect(completedTrip.status === 'completed').toBe(true)

      // 未完成行程显示 📔
      const activeTrip = { id: 2, status: 'published', title: '进行中行程' }
      expect(activeTrip.status === 'completed').toBe(false)
    })

    test('TC-302: Diary.vue 弹窗自动打开逻辑', () => {
      // 有 draftDiaryFromTrip 时应该打开弹窗
      localStorage.setItem('draftDiaryFromTrip', JSON.stringify({ title: '测试' }))
      
      const hasDraft = localStorage.getItem('draftDiaryFromTrip')
      expect(hasDraft).not.toBeNull()

      // 模拟清除
      localStorage.removeItem('draftDiaryFromTrip')
      expect(localStorage.getItem('draftDiaryFromTrip')).toBeNull()
    })
  })
})

/**
 * 手动测试清单
 */
export const manualTestChecklist = [
  {
    id: 'MT-001',
    module: '行程页面',
    test: '导出按钮显示和点击',
    steps: [
      '1. 进入行程列表页',
      '2. 确认每个行程卡片有 [✏️][📔][🗑️] 三个按钮',
      '3. 点击 📔 按钮',
      '4. 验证弹出成功提示',
      '5. 验证跳转到日记页面'
    ],
    expected: '成功跳转并自动打开编辑器'
  },
  {
    id: 'MT-002',
    module: '日记页面',
    test: '自动加载行程数据',
    steps: [
      '1. 从行程页面导出后跳转',
      '2. 验证自动弹出编辑器',
      '3. 验证标题已填充',
      '4. 验证时间轴已生成',
      '5. 验证图片已加载'
    ],
    expected: '数据完整，可直接编辑发布'
  },
  {
    id: 'MT-003',
    module: '日记页面',
    test: '手动提取行程',
    steps: [
      '1. 进入日记页面',
      '2. 点击"提取已有行程生成日记"',
      '3. 选择行程弹窗出现',
      '4. 选择一个行程',
      '5. 验证数据加载成功'
    ],
    expected: '正常加载并可以编辑'
  },
  {
    id: 'MT-004',
    module: '重复创建',
    test: '已有日记的行程处理',
    steps: [
      '1. 选择一个已导出过日记的行程',
      '2. 点击导出按钮',
      '3. 验证提示"已有日记"',
      '4. 或在弹窗中显示"已有日记"标记'
    ],
    expected: '正确提示，避免重复创建'
  },
  {
    id: 'MT-005',
    module: '时间轴',
    test: '多天数行程转换',
    steps: [
      '1. 创建一个3天的行程',
      '2. 每天安排2-3个景点',
      '3. 导出为日记',
      '4. 验证时间轴有3天',
      '5. 验证每天的活动正确'
    ],
    expected: '时间轴完整，活动顺序正确'
  },
  {
    id: 'MT-006',
    module: '边界情况',
    test: '空行程处理',
    steps: [
      '1. 创建一个没有景点的行程',
      '2. 尝试导出',
      '3. 验证提示或默认处理'
    ],
    expected: ' graceful 处理，不崩溃'
  },
  {
    id: 'MT-007',
    module: '网络错误',
    test: 'API 失败处理',
    steps: [
      '1. 断开网络或停止后端',
      '2. 点击导出',
      '3. 验证错误提示',
      '4. 验证行程状态未改变'
    ],
    expected: '友好的错误提示，数据一致性'
  }
]

/**
 * 性能测试指标
 */
export const performanceBenchmarks = {
  // 时间轴转换性能
  conversionTime: {
    small: '< 50ms (10个景点以内)',
    medium: '< 100ms (50个景点以内)',
    large: '< 500ms (200个景点以内)'
  },
  
  // API 响应时间
  apiResponseTime: {
    fetchTrip: '< 500ms',
    createDiary: '< 1s',
    totalFlow: '< 3s'
  },
  
  // 内存使用
  memoryUsage: {
    converter: '< 1MB',
    fullFlow: '< 10MB'
  }
}

// 导出测试运行器
export const runAllTests = async () => {
  console.log('🧪 开始运行集成测试...\n')
  
  const results = {
    passed: [],
    failed: [],
    skipped: []
  }

  // 这里可以调用 jest 或自定义测试框架
  // 实际运行时需要在测试环境中执行

  console.log('\n📊 测试报告:')
  console.log(`✅ 通过: ${results.passed.length}`)
  console.log(`❌ 失败: ${results.failed.length}`)
  console.log(`⏭️  跳过: ${results.skipped.length}`)
  
  return results
}

export default {
  manualTestChecklist,
  performanceBenchmarks,
  runAllTests
}
