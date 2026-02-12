import { createRouter, createWebHistory } from '@ionic/vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  // Public routes
  {
    path: '/',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/public/HomePage.vue'),
      },
      {
        path: 'booking',
        name: 'booking',
        component: () => import('@/views/public/BookingPage.vue'),
      },
      {
        path: 'confirmation',
        name: 'confirmation',
        component: () => import('@/views/public/ConfirmationPage.vue'),
      },
    ],
  },
  // Auth
  {
    path: '/admin/login',
    name: 'login',
    component: () => import('@/views/admin/LoginPage.vue'),
  },
  // Admin routes
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/admin/DashboardPage.vue'),
      },
      {
        path: 'appointments',
        name: 'appointments',
        component: () => import('@/views/admin/AppointmentsPage.vue'),
      },
      {
        path: 'services',
        name: 'services',
        component: () => import('@/views/admin/ServicesPage.vue'),
      },
      {
        path: 'barbers',
        name: 'barbers',
        component: () => import('@/views/admin/BarbersPage.vue'),
      },
      {
        path: 'clients',
        name: 'clients',
        component: () => import('@/views/admin/ClientsPage.vue'),
      },
      {
        path: 'schedule',
        name: 'schedule',
        component: () => import('@/views/admin/SchedulePage.vue'),
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/admin/SettingsPage.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    const authStore = useAuthStore()
    if (!authStore.isAuthenticated) {
      await authStore.fetchUser()
    }
    if (!authStore.isAuthenticated) {
      next({ name: 'login' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
