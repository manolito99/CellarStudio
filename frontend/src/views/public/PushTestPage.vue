<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/" text="" />
        </ion-buttons>
        <ion-title class="text-[#1d1d1f] font-semibold">Notificaciones</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true">
      <div class="max-w-lg mx-auto px-4 py-6">

        <!-- Push permission card -->
        <div class="mb-6 p-4 rounded-2xl border border-[#e8e8ed] bg-[#fafafa]">
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-full bg-[#1d1d1f] flex items-center justify-center flex-shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-[#1d1d1f] mb-0.5">Recordatorios push</p>
              <p class="text-xs text-[#86868b] leading-relaxed mb-3">
                Recibe un aviso en tu dispositivo 4 horas antes de cada cita.
              </p>

              <template v-if="!profile">
                <p class="text-xs text-[#86868b] italic">Reserva una cita para activar las notificaciones.</p>
              </template>

              <template v-else-if="pushPermission === 'denied'">
                <p class="text-xs text-red-500">Notificaciones bloqueadas. Actívalas en los ajustes de tu navegador.</p>
              </template>

              <template v-else-if="pushSubscribed">
                <div class="flex items-center gap-2">
                  <span class="inline-block w-2 h-2 rounded-full bg-green-500"></span>
                  <span class="text-xs text-green-700 font-medium">Activadas</span>
                </div>
              </template>

              <template v-else>
                <button
                  @click="subscribe"
                  :disabled="subscribing"
                  class="px-4 py-2 bg-[#1d1d1f] text-white text-xs font-semibold rounded-full disabled:opacity-50"
                >
                  {{ subscribing ? 'Activando...' : 'Activar notificaciones' }}
                </button>
              </template>
            </div>
          </div>
        </div>

        <!-- Notifications list -->
        <div v-if="!profile" class="text-center py-16">
          <svg class="w-16 h-16 mx-auto text-[#d2d2d7] mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
            <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
          </svg>
          <p class="text-[#86868b] text-sm">Reserva tu primera cita para ver tus notificaciones.</p>
          <router-link to="/booking" class="inline-block mt-4 px-5 py-2.5 bg-[#1d1d1f] text-white text-sm font-semibold rounded-full">
            Reservar cita
          </router-link>
        </div>

        <template v-else>
          <div v-if="loading" class="flex justify-center py-16">
            <svg class="w-8 h-8 animate-spin text-[#86868b]" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
          </div>

          <div v-else-if="notifications.length === 0" class="text-center py-16">
            <svg class="w-16 h-16 mx-auto text-[#d2d2d7] mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
              <path stroke-linecap="round" stroke-linejoin="round" d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5m6 4.125 2.25 2.25m0 0 2.25 2.25M12 13.875l2.25-2.25M12 13.875l-2.25 2.25M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" />
            </svg>
            <p class="text-[#86868b] text-sm">Aún no tienes notificaciones.</p>
            <p class="text-[#b0b0b5] text-xs mt-1">Aparecerán cuando reserves o recibas un recordatorio.</p>
          </div>

          <div v-else>
            <!-- Mark all as read -->
            <div v-if="unreadCount > 0" class="flex justify-between items-center mb-4">
              <span class="text-xs text-[#86868b]">{{ unreadCount }} sin leer</span>
              <button @click="markAllRead" class="text-xs text-[#1d1d1f] font-medium hover:underline">
                Marcar todas como leídas
              </button>
            </div>

            <div class="space-y-2">
              <div
                v-for="n in notifications"
                :key="n.id"
                @click="markRead(n)"
                class="p-4 rounded-2xl border transition-colors cursor-pointer"
                :class="n.read
                  ? 'border-[#e8e8ed] bg-white'
                  : 'border-[#d2d2d7] bg-[#fafafa]'"
              >
                <div class="flex items-start gap-3">
                  <div
                    class="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0"
                    :class="n.icon === 'booking' ? 'bg-green-100' : 'bg-blue-100'"
                  >
                    <!-- Booking icon -->
                    <svg v-if="n.icon === 'booking'" class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                    </svg>
                    <!-- Reminder icon -->
                    <svg v-else class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between gap-2">
                      <p class="text-sm font-semibold text-[#1d1d1f]" :class="{ 'font-normal text-[#86868b]': n.read }">
                        {{ n.title }}
                      </p>
                      <span v-if="!n.read" class="w-2 h-2 rounded-full bg-[#1d1d1f] flex-shrink-0"></span>
                    </div>
                    <p class="text-xs text-[#86868b] mt-0.5 leading-relaxed">{{ n.body }}</p>
                    <p class="text-[10px] text-[#b0b0b5] mt-1.5">{{ formatTime(n.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- Test push button (dev only, small and subtle) -->
        <div v-if="pushSubscribed && profile" class="mt-8 pt-6 border-t border-[#e8e8ed]">
          <button
            @click="sendTestPush"
            :disabled="testSending"
            class="w-full px-4 py-3 border border-dashed border-[#d2d2d7] rounded-xl text-xs text-[#86868b] font-medium flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
            </svg>
            {{ testSending ? 'Enviando...' : testResult || 'Enviar push de prueba' }}
          </button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { IonPage, IonContent, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton } from '@ionic/vue'
import { useClientProfile } from '@/composables/useClientProfile'
import { isPushSupported, subscribeToPush } from '@/services/pushNotifications'
import api from '@/services/api'

interface NotifItem {
  id: string
  title: string
  body: string
  icon: string
  read: boolean
  created_at: string
}

const { load: loadProfile } = useClientProfile()
const profile = ref(loadProfile())

const loading = ref(false)
const notifications = ref<NotifItem[]>([])
const pushPermission = ref('default')
const pushSubscribed = ref(false)
const subscribing = ref(false)
const testSending = ref(false)
const testResult = ref('')

const unreadCount = computed(() => notifications.value.filter((n) => !n.read).length)

function formatTime(iso: string): string {
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return 'Ahora'
  if (diffMin < 60) return `Hace ${diffMin} min`
  const diffH = Math.floor(diffMin / 60)
  if (diffH < 24) return `Hace ${diffH}h`
  const diffD = Math.floor(diffH / 24)
  if (diffD === 1) return 'Ayer'
  if (diffD < 7) return `Hace ${diffD} días`
  return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

async function loadNotifications() {
  if (!profile.value) return
  loading.value = true
  try {
    const { data } = await api.post('/public/notifications', { phone: profile.value.phone })
    notifications.value = data
  } catch {
    // ignore
  }
  loading.value = false
}

async function subscribe() {
  if (!profile.value) return
  subscribing.value = true
  const ok = await subscribeToPush(profile.value.phone)
  pushSubscribed.value = ok
  pushPermission.value = 'Notification' in window ? Notification.permission : 'default'
  subscribing.value = false
}

async function markRead(n: NotifItem) {
  if (n.read) return
  n.read = true
  await api.patch(`/public/notifications/${n.id}/read`).catch(() => {})
}

async function markAllRead() {
  if (!profile.value) return
  notifications.value.forEach((n) => (n.read = true))
  await api.patch('/public/notifications/read-all', { phone: profile.value.phone }).catch(() => {})
}

async function sendTestPush() {
  if (!profile.value) return
  testSending.value = true
  testResult.value = ''
  try {
    const { data } = await api.post('/public/push/test', { client_phone: profile.value.phone })
    testResult.value = data.ok ? 'Enviada!' : 'Sin suscripciones'
  } catch {
    testResult.value = 'Error'
  }
  testSending.value = false
  setTimeout(() => { testResult.value = '' }, 3000)
}

onMounted(async () => {
  pushPermission.value = 'Notification' in window ? Notification.permission : 'default'

  if (isPushSupported() && 'serviceWorker' in navigator) {
    try {
      const reg = await navigator.serviceWorker.getRegistration()
      if (reg) {
        const sub = await reg.pushManager.getSubscription()
        pushSubscribed.value = !!sub
      }
    } catch {
      // ignore
    }
  }

  await loadNotifications()

  // Auto-request push permission when the user enters the panel: surfaces the
  // browser's native permission dialog without requiring an extra click.
  // Triggered by the navigation gesture, so modern browsers allow it.
  // No-op when there's no profile, permission was already decided (granted
  // or denied), or the device is already subscribed.
  if (
    profile.value &&
    isPushSupported() &&
    pushPermission.value === 'default' &&
    !pushSubscribed.value &&
    !subscribing.value
  ) {
    subscribe()
  }
})
</script>

<style scoped>
ion-toolbar { --background: #ffffff; --border-color: #e8e8ed; }
ion-content { --background: #ffffff; }
</style>
