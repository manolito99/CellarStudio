<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/" text="" color="medium" />
        </ion-buttons>
        <ion-title class="text-[#2B2E2E]">Admin</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding">
      <div class="min-h-full flex items-center justify-center">
        <div class="w-full max-w-md">
          <div class="text-center mb-8">
            <h1 class="text-3xl font-heading font-bold text-brand-400 mb-2">Cellar Studio</h1>
            <p class="text-[#595959]">Panel de administración</p>
          </div>

          <form @submit.prevent="handleLogin" class="bg-white border border-gray-200 rounded-2xl p-6 sm:p-8">
            <h2 class="text-xl font-bold text-[#2B2E2E] mb-6">Iniciar sesión</h2>

            <div v-if="error" class="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
              {{ error }}
            </div>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-[#595959] mb-2">Email</label>
                <input
                  v-model="email"
                  type="email"
                  required
                  autocomplete="email"
                  placeholder="admin@cellarstudio.com"
                  class="w-full px-4 py-3 bg-[#F2F0E9] border border-gray-300 rounded-xl text-[#2B2E2E] placeholder-gray-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-[#595959] mb-2">Contraseña</label>
                <input
                  v-model="password"
                  type="password"
                  required
                  autocomplete="current-password"
                  placeholder="Tu contraseña"
                  class="w-full px-4 py-3 bg-[#F2F0E9] border border-gray-300 rounded-xl text-[#2B2E2E] placeholder-gray-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400"
                />
              </div>
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="w-full mt-6 px-4 py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-semibold rounded-xl transition-colors active:bg-brand-700"
            >
              {{ loading ? 'Ingresando...' : 'Ingresar' }}
            </button>
          </form>

          <div class="text-center mt-6">
            <router-link to="/" class="text-sm text-[#595959] hover:text-[#4A5D66] transition-colors">
              Volver al sitio
            </router-link>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { IonPage, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton, IonContent } from '@ionic/vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/admin')
  } catch (e: unknown) {
    error.value = 'Email o contraseña incorrectos'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
ion-toolbar {
  --background: #F2F0E9;
  --border-color: transparent;
}
ion-content {
  --background: #F2F0E9;
}
</style>
