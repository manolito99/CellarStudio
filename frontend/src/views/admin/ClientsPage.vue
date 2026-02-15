<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#1d1d1f]">Clientes</h1>
      <button
        @click="exportCSV"
        class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-[#1d1d1f] text-sm font-medium rounded-lg border border-gray-200 transition-colors"
      >
        Exportar CSV
      </button>
    </div>

    <!-- Search -->
    <div class="mb-6">
      <input
        v-model="search"
        @input="debouncedSearch"
        type="text"
        placeholder="Buscar por nombre, teléfono o email..."
        class="w-full max-w-md px-4 py-2 bg-white border border-gray-200 rounded-lg text-[#1d1d1f] placeholder-gray-400 focus:border-brand-400 focus:outline-none"
      />
    </div>

    <!-- Table -->
    <div class="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-200">
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Nombre</th>
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Teléfono</th>
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Email</th>
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Registrado</th>
            <th class="px-4 py-3 text-left text-dark-400 font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="client in clients" :key="client.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 text-[#1d1d1f] font-medium">{{ client.name }}</td>
            <td class="px-4 py-3 text-dark-300">{{ client.phone }}</td>
            <td class="px-4 py-3 text-dark-300">{{ client.email || '-' }}</td>
            <td class="px-4 py-3 text-dark-400">{{ formatDate(client.created_at) }}</td>
            <td class="px-4 py-3">
              <button
                @click="viewHistory(client)"
                class="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-[#86868b] text-xs rounded-lg transition-colors"
              >
                Historial
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="clients.length === 0" class="p-8 text-center text-dark-500">
        No se encontraron clientes
      </div>

      <!-- Pagination -->
      <div class="px-4 py-3 border-t border-gray-200 flex justify-between items-center">
        <button
          :disabled="page <= 1"
          @click="page--; loadClients()"
          class="px-3 py-1 bg-gray-100 text-[#1d1d1f] text-sm rounded-lg disabled:opacity-30"
        >
          Anterior
        </button>
        <span class="text-sm text-dark-400">Página {{ page }}</span>
        <button
          :disabled="clients.length < 20"
          @click="page++; loadClients()"
          class="px-3 py-1 bg-gray-100 text-[#1d1d1f] text-sm rounded-lg disabled:opacity-30"
        >
          Siguiente
        </button>
      </div>
    </div>

    <!-- History Modal -->
    <div v-if="showHistory" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div class="bg-white border border-gray-200 rounded-2xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-[#1d1d1f]">
            Historial - {{ selectedClient?.name }}
          </h2>
          <button @click="showHistory = false" class="p-1 text-[#86868b] hover:text-[#1d1d1f]">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div v-if="clientHistory.length === 0" class="text-dark-500 text-center py-8">
          Sin citas registradas
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="appt in clientHistory"
            :key="appt.id"
            class="p-4 bg-[#f5f5f7] rounded-lg flex items-center justify-between"
          >
            <div>
              <p class="text-[#1d1d1f] font-medium">{{ appt.service.name }}</p>
              <p class="text-dark-400 text-sm">{{ appt.barber.name }} - {{ formatDate(appt.date) }} {{ formatTime(appt.start_time) }}</p>
            </div>
            <span
              class="px-2 py-1 rounded-full text-xs font-medium"
              :class="statusClasses[appt.status] || 'bg-gray-100 text-[#86868b]'"
            >
              {{ appt.status }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { adminApi, type Client, type Appointment } from '@/services/adminApi'

const clients = ref<Client[]>([])
const search = ref('')
const page = ref(1)
const showHistory = ref(false)
const selectedClient = ref<Client | null>(null)
const clientHistory = ref<Appointment[]>([])

let searchTimeout: ReturnType<typeof setTimeout>

const statusClasses: Record<string, string> = {
  pending: 'bg-yellow-500/10 text-yellow-400',
  confirmed: 'bg-blue-500/10 text-blue-400',
  completed: 'bg-green-500/10 text-green-400',
  cancelled: 'bg-red-500/10 text-red-400',
  noshow: 'bg-gray-100 text-[#86868b]',
}

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('es-ES')
}

function formatTime(t: string): string {
  return t.substring(0, 5)
}

async function loadClients() {
  const params: Record<string, string | number> = { page: page.value }
  if (search.value) params.search = search.value
  clients.value = await adminApi.getClients(params)
}

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadClients()
  }, 300)
}

async function viewHistory(client: Client) {
  selectedClient.value = client
  clientHistory.value = await adminApi.getClientAppointments(client.id)
  showHistory.value = true
}

function exportCSV() {
  const header = 'Nombre,Teléfono,Email,Registrado\n'
  const rows = clients.value.map((c) =>
    `"${c.name}","${c.phone}","${c.email || ''}","${formatDate(c.created_at)}"`,
  ).join('\n')
  const blob = new Blob([header + rows], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'clientes_cellarstudio.csv'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(loadClients)
</script>
