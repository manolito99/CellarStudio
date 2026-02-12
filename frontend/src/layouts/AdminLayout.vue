<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <button
            @click="sidebarOpen = !sidebarOpen"
            class="p-2 rounded-lg hover:bg-gray-200 text-[#595959] hover:text-[#2B2E2E] lg:hidden"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </ion-buttons>
        <ion-title>
          <span class="text-brand-400 font-heading font-bold">Cellar Studio</span>
          <span class="text-[#595959] text-sm ml-2">Admin</span>
        </ion-title>
        <ion-buttons slot="end">
          <div class="flex items-center gap-2 pr-2">
            <span class="text-sm text-[#595959] hidden sm:inline">{{ user?.name }}</span>
            <div class="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-sm font-bold">
              {{ user?.name?.charAt(0)?.toUpperCase() }}
            </div>
          </div>
        </ion-buttons>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <div class="flex h-full">
        <!-- Sidebar desktop -->
        <aside
          :class="[
            'fixed inset-y-0 left-0 z-50 flex flex-col bg-white border-r border-gray-200 transition-all duration-300',
            'lg:static lg:w-56',
            sidebarOpen ? 'w-64 translate-x-0' : '-translate-x-full lg:translate-x-0',
          ]"
          style="top: 0;"
        >
          <div class="flex items-center h-14 px-4 border-b border-gray-200 lg:hidden">
            <h1 class="text-xl font-heading font-bold text-brand-400">Cellar Studio</h1>
            <button @click="sidebarOpen = false" class="ml-auto p-2 text-[#595959]">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <nav class="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              @click="isMobile && (sidebarOpen = false)"
              class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
              :class="[
                isActive(item.path)
                  ? 'bg-brand-500/10 text-brand-400'
                  : 'text-[#595959] hover:bg-gray-100 hover:text-[#2B2E2E]',
              ]"
            >
              <span v-html="item.icon" class="w-5 h-5 flex-shrink-0"></span>
              <span>{{ item.label }}</span>
            </router-link>
          </nav>

          <div class="p-4 border-t border-gray-200">
            <button
              @click="logout"
              class="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Cerrar sesión</span>
            </button>
          </div>
        </aside>

        <!-- Overlay mobile -->
        <div
          v-if="sidebarOpen && isMobile"
          @click="sidebarOpen = false"
          class="fixed inset-0 bg-black/50 z-40 lg:hidden"
        />

        <!-- Main content -->
        <main class="flex-1 overflow-y-auto p-4 md:p-6">
          <router-view />
        </main>
      </div>
    </ion-content>

    <!-- Bottom tab bar (mobile only) -->
    <ion-footer class="ion-no-border lg:hidden">
      <div class="flex items-center justify-around bg-white border-t border-gray-200 safe-bottom" style="padding-bottom: env(safe-area-inset-bottom, 0px);">
        <router-link
          v-for="tab in bottomTabs"
          :key="tab.path"
          :to="tab.path"
          class="flex flex-col items-center gap-0.5 py-2 px-3 min-w-[60px]"
          :class="isActive(tab.path) ? 'text-brand-400' : 'text-[#595959]'"
        >
          <span v-html="tab.icon" class="w-5 h-5"></span>
          <span class="text-[10px] font-medium">{{ tab.label }}</span>
        </router-link>
      </div>
    </ion-footer>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonContent, IonFooter } from '@ionic/vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const sidebarOpen = ref(false)
const isMobile = ref(false)

const user = computed(() => authStore.user)

function isActive(path: string): boolean {
  if (path === '/admin') return route.path === '/admin'
  return route.path.startsWith(path)
}

const navItems = [
  {
    path: '/admin',
    label: 'Dashboard',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>',
  },
  {
    path: '/admin/appointments',
    label: 'Citas',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
  },
  {
    path: '/admin/services',
    label: 'Servicios',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z"/></svg>',
  },
  {
    path: '/admin/barbers',
    label: 'Barberos',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>',
  },
  {
    path: '/admin/clients',
    label: 'Clientes',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>',
  },
  {
    path: '/admin/schedule',
    label: 'Horarios',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
  },
  {
    path: '/admin/settings',
    label: 'Configuración',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>',
  },
]

const bottomTabs = [
  {
    path: '/admin',
    label: 'Inicio',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>',
  },
  {
    path: '/admin/appointments',
    label: 'Citas',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>',
  },
  {
    path: '/admin/clients',
    label: 'Clientes',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>',
  },
  {
    path: '/admin/settings',
    label: 'Más',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>',
  },
]

function logout() {
  authStore.logout()
  router.push('/admin/login')
}

function checkMobile() {
  isMobile.value = window.innerWidth < 1024
  if (isMobile.value) sidebarOpen.value = false
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})
</script>

<style scoped>
ion-toolbar {
  --background: #ffffff;
  --border-color: #e5e5e5;
}
ion-content {
  --background: #F2F0E9;
}
ion-footer {
  --background: transparent;
}
</style>
