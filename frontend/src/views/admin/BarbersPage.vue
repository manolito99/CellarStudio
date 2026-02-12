<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#2B2E2E]">Barberos</h1>
      <button
        @click="openModal()"
        class="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors"
      >
        + Nuevo barbero
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="barber in barbers"
        :key="barber.id"
        class="bg-white border border-gray-200 rounded-xl p-5 hover:border-gray-300 transition-colors"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-gradient-to-br from-brand-400 to-brand-600 p-0.5 flex-shrink-0">
              <div class="w-full h-full rounded-full bg-[#F2F0E9] flex items-center justify-center">
                <span class="text-lg font-bold text-brand-400">{{ barber.name.charAt(0) }}</span>
              </div>
            </div>
            <div>
              <h3 class="text-[#2B2E2E] font-bold">{{ barber.name }}</h3>
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :class="barber.is_active ? 'bg-green-500/10 text-green-400' : 'bg-gray-100 text-[#595959]'"
              >
                {{ barber.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
          </div>
          <div class="flex gap-1">
            <button @click="openModal(barber)" class="p-1.5 rounded-lg hover:bg-gray-100 text-[#595959] hover:text-[#2B2E2E] transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
            </button>
            <button @click="deleteBarber(barber.id)" class="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-400 hover:text-red-400 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </div>
        <p class="text-dark-400 text-sm mb-3">{{ barber.bio }}</p>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="svc in barber.services"
            :key="svc.id"
            class="px-2 py-0.5 bg-gray-100 text-[#595959] text-xs rounded-full"
          >
            {{ svc.name }}
          </span>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div class="bg-white border border-gray-200 rounded-2xl w-full max-w-lg p-6">
        <h2 class="text-xl font-bold text-[#2B2E2E] mb-6">
          {{ editing ? 'Editar barbero' : 'Nuevo barbero' }}
        </h2>
        <form @submit.prevent="saveBarber" class="space-y-4">
          <div>
            <label class="block text-sm text-dark-300 mb-1">Nombre</label>
            <input v-model="form.name" required class="w-full px-3 py-2 bg-[#F2F0E9] border border-gray-200 rounded-lg text-[#2B2E2E] focus:border-brand-400 focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm text-dark-300 mb-1">Bio</label>
            <textarea v-model="form.bio" rows="2" class="w-full px-3 py-2 bg-[#F2F0E9] border border-gray-200 rounded-lg text-[#2B2E2E] focus:border-brand-400 focus:outline-none resize-none" />
          </div>
          <div>
            <label class="block text-sm text-dark-300 mb-2">Servicios</label>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <label
                v-for="svc in allServices"
                :key="svc.id"
                class="flex items-center gap-2 cursor-pointer"
              >
                <input
                  type="checkbox"
                  :value="svc.id"
                  v-model="form.service_ids"
                  class="rounded border-gray-300 text-brand-500 focus:ring-brand-400"
                />
                <span class="text-sm text-[#2B2E2E]">{{ svc.name }}</span>
              </label>
            </div>
          </div>
          <div class="flex gap-3 pt-2">
            <button type="submit" class="flex-1 px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg transition-colors">
              {{ editing ? 'Guardar' : 'Crear' }}
            </button>
            <button type="button" @click="showModal = false" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-[#2B2E2E] rounded-lg transition-colors">
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { adminApi } from '@/services/adminApi'
import type { Barber, Service } from '@/services/publicApi'

const barbers = ref<Barber[]>([])
const allServices = ref<Service[]>([])
const showModal = ref(false)
const editing = ref<string | null>(null)
const form = reactive({
  name: '',
  bio: '',
  service_ids: [] as string[],
})

async function loadData() {
  const [b, s] = await Promise.all([adminApi.getBarbers(), adminApi.getServices()])
  barbers.value = b
  allServices.value = s
}

function openModal(barber?: Barber) {
  if (barber) {
    editing.value = barber.id
    form.name = barber.name
    form.bio = barber.bio || ''
    form.service_ids = barber.services.map((s: Service) => s.id)
  } else {
    editing.value = null
    form.name = ''
    form.bio = ''
    form.service_ids = []
  }
  showModal.value = true
}

async function saveBarber() {
  if (editing.value) {
    await adminApi.updateBarber(editing.value, { ...form })
  } else {
    await adminApi.createBarber({ ...form })
  }
  showModal.value = false
  await loadData()
}

async function deleteBarber(id: string) {
  if (!confirm('¿Eliminar este barbero?')) return
  await adminApi.deleteBarber(id)
  await loadData()
}

onMounted(loadData)
</script>
