<template>
  <div>
    <h1 class="text-2xl font-bold text-[#2B2E2E] mb-6">Configuración</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Business Info -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-bold text-[#2B2E2E] mb-4">Datos del negocio</h2>
        <form class="space-y-4">
          <div>
            <label class="block text-sm text-dark-300 mb-1">Nombre</label>
            <input
              v-model="business.name"
              class="w-full px-3 py-2 bg-[#F2F0E9] border border-gray-200 rounded-lg text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-dark-300 mb-1">Dirección</label>
            <input
              v-model="business.address"
              class="w-full px-3 py-2 bg-[#F2F0E9] border border-gray-200 rounded-lg text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-dark-300 mb-1">Teléfono</label>
            <input
              v-model="business.phone"
              class="w-full px-3 py-2 bg-[#F2F0E9] border border-gray-200 rounded-lg text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-dark-300 mb-1">Email</label>
            <input
              v-model="business.email"
              type="email"
              class="w-full px-3 py-2 bg-[#F2F0E9] border border-gray-200 rounded-lg text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
            />
          </div>
          <button
            type="button"
            class="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors"
          >
            Guardar cambios
          </button>
        </form>
      </div>

      <!-- App Settings -->
      <div class="space-y-6">
        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <h2 class="text-lg font-bold text-[#2B2E2E] mb-4">Configuración de slots</h2>
          <div>
            <label class="block text-sm text-dark-300 mb-2">Duración de slots (minutos)</label>
            <select
              v-model="slotDuration"
              class="px-3 py-2 bg-[#F2F0E9] border border-gray-200 rounded-lg text-[#2B2E2E] focus:border-brand-400 focus:outline-none"
            >
              <option :value="15">15 minutos</option>
              <option :value="20">20 minutos</option>
              <option :value="30">30 minutos</option>
            </select>
          </div>
        </div>

        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <h2 class="text-lg font-bold text-[#2B2E2E] mb-4">Cuenta administrador</h2>
          <div class="space-y-3">
            <div>
              <label class="block text-sm text-dark-300 mb-1">Email actual</label>
              <p class="text-[#2B2E2E]">{{ user?.email }}</p>
            </div>
            <button
              class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-[#2B2E2E] text-sm font-medium rounded-lg border border-gray-200 transition-colors"
            >
              Cambiar contraseña
            </button>
          </div>
        </div>

        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <h2 class="text-lg font-bold text-[#2B2E2E] mb-4">Información del sistema</h2>
          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-dark-400">Versión</span>
              <span class="text-[#2B2E2E]">1.0.0</span>
            </div>
            <div class="flex justify-between">
              <span class="text-dark-400">API</span>
              <span class="text-green-400">Conectado</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const user = computed(() => authStore.user)

const business = reactive({
  name: 'Cellar Studio',
  address: 'Av. Corrientes 1234, CABA',
  phone: '+54 11 1234-5678',
  email: 'info@cellarstudio.com',
})

const slotDuration = ref(15)
</script>
