<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="min-h-screen bg-[#fafafa] flex items-center justify-center px-4">
        <div class="w-full max-w-md login-entrance">
          <div class="text-center mb-8">
            <div class="login-item login-delay-0">
              <h1 class="text-3xl font-heading font-semibold text-[#1d1d1f] mb-2 tracking-tight">Cellar Studio</h1>
              <p class="text-[#86868b]">Panel de administración</p>
            </div>
          </div>

          <form
            @submit.prevent="handleLogin"
            class="login-item login-delay-1 bg-white border border-[#e8e8ed] rounded-2xl p-6 sm:p-8 shadow-sm"
          >
            <h2 class="text-xl font-semibold text-[#1d1d1f] mb-6">Iniciar sesión</h2>

            <Transition name="error-slide">
              <div v-if="error" class="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                {{ error }}
              </div>
            </Transition>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-[#86868b] mb-2">Email</label>
                <input
                  v-model="email"
                  type="email"
                  required
                  autocomplete="email"
                  placeholder="admin@cellarstudio.com"
                  class="w-full px-4 py-3 bg-[#f5f5f7] border border-[#e8e8ed] rounded-xl text-[#1d1d1f] placeholder-[#86868b]/50 focus:border-[#1d1d1f] focus:outline-none focus:ring-1 focus:ring-[#1d1d1f] transition-all duration-300"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-[#86868b] mb-2">Contraseña</label>
                <input
                  v-model="password"
                  type="password"
                  required
                  autocomplete="current-password"
                  placeholder="Tu contraseña"
                  class="w-full px-4 py-3 bg-[#f5f5f7] border border-[#e8e8ed] rounded-xl text-[#1d1d1f] placeholder-[#86868b]/50 focus:border-[#1d1d1f] focus:outline-none focus:ring-1 focus:ring-[#1d1d1f] transition-all duration-300"
                />
              </div>
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="btn-primary w-full mt-6 px-4 py-3.5 bg-[#1d1d1f] disabled:opacity-50 text-white font-semibold rounded-xl"
            >
              {{ loading ? 'Ingresando...' : 'Ingresar' }}
            </button>
          </form>

          <div class="login-item login-delay-2 text-center mt-6">
            <router-link to="/" class="text-sm text-[#86868b] hover:text-[#1d1d1f] transition-colors duration-300">
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
import { IonPage, IonContent } from '@ionic/vue'
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
ion-content {
  --background: #fafafa;
}

/* Staggered entrance */
.login-item {
  opacity: 0;
  transform: translateY(25px);
  animation: loginReveal 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.login-delay-0 { animation-delay: 0.1s; }
.login-delay-1 { animation-delay: 0.3s; }
.login-delay-2 { animation-delay: 0.5s; }

@keyframes loginReveal {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Error slide transition */
.error-slide-enter-active,
.error-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.error-slide-enter-from,
.error-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
