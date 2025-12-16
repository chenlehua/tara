import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台' }
      },
      {
        path: 'generator',
        name: 'ReportGenerator',
        component: () => import('@/views/ReportGenerator.vue'),
        meta: { title: '一键生成报告' }
      },
      {
        path: 'projects',
        name: 'ProjectList',
        component: () => import('@/views/projects/ProjectList.vue'),
        meta: { title: '项目管理' }
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/projects/ProjectDetail.vue'),
        meta: { title: '项目详情' }
      },
      {
        path: 'assets',
        name: 'AssetList',
        component: () => import('@/views/assets/AssetList.vue'),
        meta: { title: '资产识别' }
      },
      {
        path: 'threats',
        name: 'ThreatList',
        component: () => import('@/views/threats/ThreatList.vue'),
        meta: { title: '威胁分析' }
      },
      {
        path: 'risks',
        name: 'RiskList',
        component: () => import('@/views/risks/RiskList.vue'),
        meta: { title: '风险评估' }
      },
      {
        path: 'measures',
        name: 'MeasureList',
        component: () => import('@/views/measures/MeasureList.vue'),
        meta: { title: '安全措施' }
      },
      {
        path: 'reports',
        name: 'ReportList',
        component: () => import('@/views/reports/ReportList.vue'),
        meta: { title: '报告中心' }
      },
      {
        path: 'reports/:id',
        name: 'ReportDetail',
        component: () => import('@/views/reports/ReportDetail.vue'),
        meta: { title: '报告详情' }
      },
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: () => import('@/views/knowledge/KnowledgeBase.vue'),
        meta: { title: '知识库' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guard for authentication
router.beforeEach((to, _from, next) => {
  // Update document title
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - TARA Pro`
  }
  
  // Check authentication (skip for login page)
  if (to.name !== 'Login') {
    // For now, allow all access
    // In production, add token check here
    next()
  } else {
    next()
  }
})

export default router
