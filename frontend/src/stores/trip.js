// Pinia Store - 行程管理
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTripStore = defineStore('trip', () => {
  // 行程基本信息
  const tripForm = ref({
    destinations: [],
    days: 3,
    preferences: []
  })
  
  // 选中的景点
  const selectedSpots = ref([])
  
  // 当前行程
  const currentTrip = ref(null)
  
  // 行程列表
  const tripList = ref([])
  
  // 计算属性
  const hasTrip = computed(() => currentTrip.value !== null)
  const selectedCount = computed(() => selectedSpots.value.length)
  
  // Actions
  const setTripForm = (form) => {
    tripForm.value = { ...tripForm.value, ...form }
  }
  
  const addSpot = (spot) => {
    if (!selectedSpots.value.find(s => s.id === spot.id)) {
      selectedSpots.value.push(spot)
    }
  }
  
  const removeSpot = (spotId) => {
    const index = selectedSpots.value.findIndex(s => s.id === spotId)
    if (index > -1) {
      selectedSpots.value.splice(index, 1)
    }
  }
  
  const clearSelection = () => {
    selectedSpots.value = []
  }
  
  const setCurrentTrip = (trip) => {
    currentTrip.value = trip
  }
  
  const setTripList = (list) => {
    tripList.value = list
  }
  
  return {
    tripForm,
    selectedSpots,
    currentTrip,
    tripList,
    hasTrip,
    selectedCount,
    setTripForm,
    addSpot,
    removeSpot,
    clearSelection,
    setCurrentTrip,
    setTripList
  }
})
