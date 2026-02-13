<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#1d1d1f]">Servicios</h1>
      <button
        @click="openModal()"
        class="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors"
      >
        + Nuevo servicio
      </button>
    </div>

    <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200">
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Nombre</th>
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Precio</th>
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Duración</th>
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Estado</th>
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="service in services" :key="service.id" class="hover:bg-gray-50">
            <td class="px-4 py-3">
              <p class="text-[#1d1d1f] font-medium">{{ service.name }}</p>
              <p class="text-dark-500 text-xs">{{ service.description }}</p>
            </td>
            <td class="px-4 py-3 text-brand-400 font-bold">${{ service.price.toLocaleString() }}</td>
            <td class="px-4 py-3 text-[#1d1d1f]">{{ service.duration_minutes }} min</td>
            <td class="px-4 py-3">
              <button
                @click="toggleActive(service)"
                class="px-3 py-1 rounded-full text-xs font-medium transition-colors"
                :class="service.is_active ? 'bg-green-500/10 text-green-400' : 'bg-gray-100 text-[#86868b]'"
              >
                {{ service.is_active ? 'Activo' : 'Inactivo' }}
              </button>
            </td>
            <td class="px-4 py-3">
              <div class="flex gap-1">
                <button @click="openModal(service)" class="p-1.5 rounded-lg hover:bg-gray-100 text-[#86868b] hover:text-[#1d1d1f] transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                </button>
                <button @click="deleteService(service.id)" class="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-400 hover:text-red-400 transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div class="bg-white border border-gray-200 rounded-2xl w-full max-w-lg p-6">
        <h2 class="text-xl font-bold text-[#1d1d1f] mb-6">
          {{ editing ? 'Editar servicio' : 'Nuevo servicio' }}
        </h2>
        <form @submit.prevent="saveService" class="space-y-4">
          <div>
            <label class="block text-sm text-dark-300 mb-1">Nombre</label>
            <input v-model="form.name" required class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-brand-400 focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm text-dark-300 mb-1">Descripción</label>
            <textarea v-model="form.description" rows="2" class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-brand-400 focus:outline-none resize-none" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-dark-300 mb-1">Precio ($)</label>
              <input v-model.number="form.price" type="number" step="0.01" required class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-brand-400 focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm text-dark-300 mb-1">Duración (min)</label>
              <input v-model.number="form.duration_minutes" type="number" required class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-brand-400 focus:outline-none" />
            </div>
          </div>
          <div class="flex gap-3 pt-2">
            <button type="submit" class="flex-1 px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white font-medium rounded-lg transition-colors">
              {{ editing ? 'Guardar' : 'Crear' }}
            </button>
            <button type="button" @click="showModal = false" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-[#1d1d1f] rounded-lg transition-colors">
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
import type { Service } from '@/services/publicApi'

const services = ref<Service[]>([])
const showModal = ref(false)
const editing = ref<string | null>(null)
const form = reactive({
  name: '',
  description: '',
  price: 0,
  duration_minutes: 30,
})

async function loadServices() {
  services.value = await adminApi.getServices()
}

function openModal(service?: Service) {
  if (service) {
    editing.value = service.id
    form.name = service.name
    form.description = service.description || ''
    form.price = service.price
    form.duration_minutes = service.duration_minutes
  } else {
    editing.value = null
    form.name = ''
    form.description = ''
    form.price = 0
    form.duration_minutes = 30
  }
  showModal.value = true
}

async function saveService() {
  if (editing.value) {
    await adminApi.updateService(editing.value, { ...form })
  } else {
    await adminApi.createService({ ...form })
  }
  showModal.value = false
  await loadServices()
}

async function toggleActive(service: Service) {
  await adminApi.updateService(service.id, { is_active: !service.is_active })
  await loadServices()
}

async function deleteService(id: string) {
  if (!confirm('¿Eliminar este servicio?')) return
  await adminApi.deleteService(id)
  await loadServices()
}

onMounted(loadServices)
</script>
