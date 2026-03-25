<template>
  <div>
    <h1 class="text-2xl font-bold text-[#1d1d1f] mb-6">Configuración</h1>

    <!-- Toast notification -->
    <Transition name="toast">
      <div
        v-if="toast.visible"
        class="fixed top-5 right-5 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium"
        :class="toast.type === 'success' ? 'bg-[#1d1d1f] text-white' : 'bg-[#ff3b30] text-white'"
      >
        <svg v-if="toast.type === 'success'" class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
        </svg>
        <svg v-else class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"/>
        </svg>
        {{ toast.message }}
      </div>
    </Transition>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- Business Info -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-bold text-[#1d1d1f] mb-4">Datos del negocio</h2>
        <form @submit.prevent="saveBusiness" class="space-y-4">
          <div>
            <label class="block text-sm text-[#86868b] mb-1">Nombre</label>
            <input
              v-model="business.name"
              class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-[#86868b] mb-1">Dirección</label>
            <input
              v-model="business.address"
              class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-[#86868b] mb-1">Teléfono</label>
            <input
              v-model="business.phone"
              class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-[#86868b] mb-1">Email</label>
            <input
              v-model="business.email"
              type="email"
              class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
            />
          </div>
          <button
            type="submit"
            :disabled="savingBusiness"
            class="px-4 py-2 bg-[#1d1d1f] hover:bg-[#3a3a3c] text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {{ savingBusiness ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </form>
      </div>

      <!-- Right column -->
      <div class="space-y-6">

        <!-- Admin account -->
        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <h2 class="text-lg font-bold text-[#1d1d1f] mb-4">Cuenta administrador</h2>

          <div class="space-y-3">
            <div>
              <label class="block text-sm text-[#86868b] mb-1">Nombre</label>
              <p class="text-[#1d1d1f] text-sm font-medium">{{ user?.name }}</p>
            </div>
            <div>
              <label class="block text-sm text-[#86868b] mb-1">Email</label>
              <p class="text-[#1d1d1f] text-sm font-medium">{{ user?.email }}</p>
            </div>
          </div>

          <!-- Toggle password form -->
          <button
            v-if="!showPasswordForm"
            @click="showPasswordForm = true"
            class="mt-4 px-4 py-2 bg-[#f5f5f7] hover:bg-[#e8e8ed] text-[#1d1d1f] text-sm font-medium rounded-lg border border-gray-200 transition-colors"
          >
            Cambiar contraseña
          </button>

          <!-- Password form -->
          <form v-else @submit.prevent="changePassword" class="mt-4 space-y-3">
            <div>
              <label class="block text-sm text-[#86868b] mb-1">Contraseña actual</label>
              <input
                v-model="passwords.current"
                type="password"
                autocomplete="current-password"
                placeholder="••••••••"
                class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm text-[#86868b] mb-1">Nueva contraseña</label>
              <input
                v-model="passwords.new"
                type="password"
                autocomplete="new-password"
                placeholder="Mínimo 6 caracteres"
                class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
              />
            </div>
            <div>
              <label class="block text-sm text-[#86868b] mb-1">Confirmar nueva contraseña</label>
              <input
                v-model="passwords.confirm"
                type="password"
                autocomplete="new-password"
                placeholder="Repetir contraseña"
                class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-[#1d1d1f] focus:outline-none"
              />
            </div>

            <!-- Inline error -->
            <p v-if="passwordError" class="text-xs text-[#ff3b30]">{{ passwordError }}</p>

            <div class="flex gap-2 pt-1">
              <button
                type="submit"
                :disabled="changingPassword"
                class="px-4 py-2 bg-[#1d1d1f] hover:bg-[#3a3a3c] text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
              >
                {{ changingPassword ? 'Guardando...' : 'Guardar contraseña' }}
              </button>
              <button
                type="button"
                @click="cancelPasswordForm"
                :disabled="changingPassword"
                class="px-4 py-2 bg-[#f5f5f7] hover:bg-[#e8e8ed] text-[#1d1d1f] text-sm font-medium rounded-lg border border-gray-200 transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>

        <!-- System info -->
        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <h2 class="text-lg font-bold text-[#1d1d1f] mb-4">Información del sistema</h2>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-[#86868b]">Versión</span>
              <span class="text-[#1d1d1f]">1.0.0</span>
            </div>
            <div class="flex justify-between">
              <span class="text-[#86868b]">API</span>
              <span class="text-green-500 font-medium">Conectado</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/services/authApi'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

// ── Business info (persisted in localStorage) ─────────────────────────────────
const BUSINESS_KEY = 'cellar_business_info'

const business = reactive({
  name: 'Cellar Barber Studio',
  address: '',
  phone: '',
  email: '',
})

const savingBusiness = ref(false)

onMounted(() => {
  const saved = localStorage.getItem(BUSINESS_KEY)
  if (saved) {
    try {
      Object.assign(business, JSON.parse(saved))
    } catch {
      // ignore corrupt data
    }
  }
})

async function saveBusiness() {
  savingBusiness.value = true
  try {
    // Simulate async save (persisted locally — no backend table for business info yet)
    await new Promise(r => setTimeout(r, 300))
    localStorage.setItem(BUSINESS_KEY, JSON.stringify({ ...business }))
    showToast('Datos del negocio guardados', 'success')
  } catch {
    showToast('Error al guardar', 'error')
  } finally {
    savingBusiness.value = false
  }
}

// ── Password change ───────────────────────────────────────────────────────────
const showPasswordForm = ref(false)
const changingPassword = ref(false)
const passwordError = ref('')

const passwords = reactive({
  current: '',
  new: '',
  confirm: '',
})

function cancelPasswordForm() {
  showPasswordForm.value = false
  passwords.current = ''
  passwords.new = ''
  passwords.confirm = ''
  passwordError.value = ''
}

async function changePassword() {
  passwordError.value = ''

  if (!passwords.current || !passwords.new || !passwords.confirm) {
    passwordError.value = 'Completá todos los campos'
    return
  }
  if (passwords.new.length < 6) {
    passwordError.value = 'La nueva contraseña debe tener al menos 6 caracteres'
    return
  }
  if (passwords.new !== passwords.confirm) {
    passwordError.value = 'Las contraseñas nuevas no coinciden'
    return
  }

  changingPassword.value = true
  try {
    await authApi.changePassword({
      current_password: passwords.current,
      new_password: passwords.new,
    })
    cancelPasswordForm()
    showToast('Contraseña actualizada correctamente', 'success')
  } catch (err: any) {
    const msg = err?.response?.data?.detail ?? 'Error al cambiar la contraseña'
    passwordError.value = msg
  } finally {
    changingPassword.value = false
  }
}

// ── Toast ─────────────────────────────────────────────────────────────────────
const toast = reactive({ visible: false, message: '', type: 'success' as 'success' | 'error' })
let toastTimer: ReturnType<typeof setTimeout> | null = null

function showToast(message: string, type: 'success' | 'error') {
  if (toastTimer) clearTimeout(toastTimer)
  toast.message = message
  toast.type = type
  toast.visible = true
  toastTimer = setTimeout(() => { toast.visible = false }, 3000)
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
