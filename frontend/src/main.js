import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import Home from './views/Home.vue'
import CreateTrip from './views/CreateTrip.vue'
import SpotRecommend from './views/SpotRecommend.vue'
import TripDetail from './views/TripDetail.vue'
import RoutePlan from './views/RoutePlan.vue'
import Diary from './views/Diary.vue'
import DiaryDetail from './views/DiaryDetail.vue'
import City from './views/City.vue'
import SpotDetail from './views/SpotDetail.vue'
import AIAssistant from './views/AIAssistant.vue'
import Trips from './views/Trips.vue'
import Profile from './views/Profile.vue'
import Food from './views/Food.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import Setting from './views/Setting.vue'
import Photos from './views/Photos.vue'
import Collection from './views/Collection.vue'
import Explore from './views/Explore.vue'
import AmapExample from './components/AmapExample.vue'

// 路由配置
const routes = [
  { path: '/map-test', name: 'MapTest', component: AmapExample },
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/create-trip', name: 'CreateTrip', component: CreateTrip },
  { path: '/spot-recommend', name: 'SpotRecommend', component: SpotRecommend },
  { path: '/trip', name: 'TripDetail', component: TripDetail },
  { path: '/trips', name: 'Trips', component: Trips },
  { path: '/route/:id', name: 'RoutePlan', component: RoutePlan },
  { path: '/diary', name: 'Diary', component: Diary },
  { path: '/diary/:id', name: 'DiaryDetail', component: DiaryDetail },
  { path: '/city', name: 'City', component: City },
  { path: '/spot', name: 'SpotDetail', component: SpotDetail },
  { path: '/ai', name: 'AIAssistant', component: AIAssistant },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/food', name: 'Food', component: Food },
  { path: '/explore', name: 'Explore', component: Explore },
  { path: '/setting', name: 'Setting', component: Setting },
  { path: '/photos', name: 'Photos', component: Photos },
  { path: '/collection', name: 'Collection', component: Collection },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查是否需要登录
const publicRoutes = ['/', '/login', '/register', '/city', '/spot']

router.beforeEach((to, from, next) => {
  const userId = localStorage.getItem('userId')

  // 如果访问的是公开路由，直接放行
  if (publicRoutes.includes(to.path)) {
    next()
    return
  }

  // 如果用户已登录，放行
  if (userId) {
    next()
    return
  }

  // 未登录，跳转到登录页
  next('/login')
})

const pinia = createPinia()
const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(pinia)
app.use(ElementPlus)
app.mount('#app')
