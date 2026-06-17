import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/ConfigPage.vue')
  },
  {
    path: '/preview',
    name: 'Preview',
    component: () => import('@/views/PreviewPage.vue')
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/TaskPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
