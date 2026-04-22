// frontend/src/bridge/__tests__/tripDiaryBridge.test.js
// TripDiaryBridge 测试套件

import { useTripDiaryBridge } from '../tripDiaryBridge'
import { useTripStore } from '../../stores/trip'
import { useDiaryStore } from '../../stores/diary'

/**
 * 运行所有测试
 */
export const runBridgeTests = async () => {
  console.log('🧪 开始测试 TripDiaryBridge...\n')

  const bridge = useTripDiaryBridge()
  const tripStore = useTripStore()
  const diaryStore = useDiaryStore()

  let passCount = 0
  let failCount = 0

  const assert = (condition, message) => {
    if (condition) {
      console.log(`  ✅ ${message}`)
      passCount++
    } else {
      console.error(`  ❌ ${message}`)
      failCount++
    }
  }

  // ========== 测试 1: 方法导出检查 ==========
  console.log('测试 1: 方法导出检查')
  assert(typeof bridge.completeTripAndCreateDiary === 'function', 'completeTripAndCreateDiary 是函数')
  assert(typeof bridge.checkExistingDiary === 'function', 'checkExistingDiary 是函数')
  assert(typeof bridge.generateDiaryFromTrip === 'function', 'generateDiaryFromTrip 是函数')

  // ========== 测试 2: 日记内容生成 ==========
  console.log('\n测试 2: 日记内容生成')

  const mockTrip = {
    id: 1,
    title: '北京三日游',
    destination: '北京',
    total_days: 3,
    schedules: [
      {
        day_number: 1,
        spot_name: '故宫',
        spot_image: '/images/gugong.jpg',
        notes: '很壮观，建议早去',
        visit_time_start: '09:00'
      },
      {
        day_number: 1,
        spot_name: '天安门',
        spot_image: '/images/tiananmen.jpg',
        visit_time_start: '14:00'
      },
      {
        day_number: 2,
        spot_name: '长城',
        spot_image: '/images/changcheng.jpg',
        notes: '体力要求高'
      }
    ]
  }

  const content = bridge.generateDiaryFromTrip(mockTrip)
  console.log('  生成的内容预览:\n', content.substring(0, 300), '...\n')

  // 真正的断言验证
  assert(content.includes('北京三日游'), '内容包含行程标题')
  assert(content.includes('故宫'), '内容包含第一天景点 故宫')
  assert(content.includes('天安门'), '内容包含第一天景点 天安门')
  assert(content.includes('长城'), '内容包含第二天景点 长城')
  assert(content.includes('很壮观'), '内容包含景点备注')
  assert(content.includes('第1天'), '内容包含第1天标题')
  assert(content.includes('第2天'), '内容包含第2天标题')
  assert(!content.includes('第3天'), '内容不包含第3天（无景点）')
  assert(content.includes('📍 目的地：北京'), '内容包含目的地')
  assert(content.includes('📅 行程天数：3天'), '内容包含天数')

  // ========== 测试 3: 边界情况处理 ==========
  console.log('\n测试 3: 边界情况处理')

  const emptyContent = bridge.generateDiaryFromTrip({})
  assert(emptyContent.includes('未知行程'), '空数据返回默认标题')
  assert(emptyContent.includes('暂无详细行程'), '空数据提示无行程')

  const nullContent = bridge.generateDiaryFromTrip(null)
  assert(nullContent.includes('暂无内容'), 'null 数据返回提示')

  const noSchedules = bridge.generateDiaryFromTrip({
    title: '测试',
    destination: '测试城市',
    total_days: 1
  })
  assert(noSchedules.includes('暂无详细行程'), '无 schedules 返回提示')

  // ========== 测试 4: API 集成测试（需要后端运行）==========
  console.log('\n测试 4: API 集成测试')
  console.log('  ⚠️  需要后端服务运行在 localhost:8000')

  try {
    const existing = await bridge.checkExistingDiary(1)
    console.log('  checkExistingDiary 结果:', existing ? `找到日记 ID:${existing.id}` : '无日记')
    assert(true, 'checkExistingDiary 调用成功')
  } catch (error) {
    assert(false, `checkExistingDiary 调用失败: ${error.message}`)
  }

  // ========== 测试 5: 完整流程测试（可选）==========
  console.log('\n测试 5: 完整流程测试')
  console.log('  ⚠️  此测试会真实修改数据库，请谨慎运行')
  console.log('  ⏭️  跳过完整流程测试（取消注释以启用）')

  /*
  try {
    // 设置测试用户
    diaryStore.setCurrentUser({ id: 1, username: 'test' })

    // 设置当前行程到 store
    tripStore.currentTrip = { id: 1, status: 'published' }
    tripStore.tripList = [{ id: 1, status: 'published', title: '测试行程' }]

    // 执行完整流程
    const result = await bridge.completeTripAndCreateDiary(mockTrip.id, mockTrip)

    // 断言返回值结构
    assert(result.success === true, '返回 success: true')
    assert(result.tripId === mockTrip.id, '返回正确的 tripId')
    assert(typeof result.diaryId === 'number', `diaryId 是数字: ${result.diaryId}`)
    assert(result.diary && result.diary.id === result.diaryId, '返回的 diary 对象包含正确 id')

    // 断言 store 状态同步
    assert(tripStore.currentTrip?.status === 'completed', 'currentTrip 状态变为 completed')
    const listTrip = tripStore.tripList.find(t => t.id === mockTrip.id)
    assert(listTrip?.status === 'completed', 'tripList 中的行程状态同步更新')

    console.log('  🎉 完整流程测试通过！')

  } catch (error) {
    if (error.message.includes('已有日记')) {
      console.log('  ⚠️  该行程已有日记，跳过创建')
    } else {
      assert(false, `完整流程失败: ${error.message}`)
    }
  }
  */

  // ========== 测试报告 ==========
  console.log('\n========== 测试报告 ==========')
  console.log(`✅ 通过: ${passCount}`)
  console.log(`❌ 失败: ${failCount}`)
  console.log(`📊 总计: ${passCount + failCount}`)

  if (failCount === 0) {
    console.log('\n🎉 所有测试通过！')
  } else {
    console.log('\n⚠️  存在失败的测试，请检查')
  }

  return { passCount, failCount }
}

/**
 * 快速测试内容生成（不调用 API）
 */
export const testGenerateContent = () => {
  const bridge = useTripDiaryBridge()

  const mockTrip = {
    id: 1,
    title: '北京三日游',
    destination: '北京',
    total_days: 3,
    schedules: [
      { day_number: 1, spot_name: '故宫', notes: '很壮观' },
      { day_number: 1, spot_name: '天安门' },
      { day_number: 2, spot_name: '长城' }
    ]
  }

  const content = bridge.generateDiaryFromTrip(mockTrip)
  console.log('生成的日记内容：\n')
  console.log(content)
  console.log('\n--- 内容结束 ---')
  console.log(`总字符数: ${content.length}`)

  return content
}

/**
 * 测试重复创建检查
 */
export const testDuplicateCheck = async () => {
  const bridge = useTripDiaryBridge()

  console.log('测试重复创建检查...')

  try {
    const existing = await bridge.checkExistingDiary(1)
    if (existing) {
      console.log('✅ 正确检测到已有日记:', existing.id)
    } else {
      console.log('✅ 该行程无日记，可以创建')
    }
  } catch (error) {
    console.error('❌ 检查失败:', error)
  }
}

// 默认导出
export default {
  runBridgeTests,
  testGenerateContent,
  testDuplicateCheck
}
