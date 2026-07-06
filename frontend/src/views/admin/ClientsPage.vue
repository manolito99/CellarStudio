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

    <!-- Escritorio: tabla -->
    <div class="hidden md:block bg-white border border-gray-200 rounded-xl overflow-x-auto">
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
              <div class="flex gap-1">
                <button
                  @click="viewHistory(client)"
                  class="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-[#86868b] text-xs rounded-lg transition-colors"
                >
                  Historial
                </button>
                <button
                  @click="deleteClient(client.id)"
                  class="flex items-center gap-1 px-3 py-1 rounded-lg text-red-500 hover:bg-red-50 text-xs font-medium transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  Ocultar
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="clients.length === 0" class="p-8 text-center text-dark-500">
        No se encontraron clientes
      </div>
    </div>

    <!-- Móvil: tarjetas -->
    <div class="md:hidden space-y-3">
      <div
        v-for="client in clients"
        :key="client.id"
        class="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm"
      >
        <div class="min-w-0">
          <p class="text-[#1d1d1f] font-semibold text-base truncate">{{ client.name }}</p>
          <p class="text-dark-400 text-xs mt-0.5">Registrado {{ formatDate(client.created_at) }}</p>
        </div>

        <div class="mt-2 space-y-1 text-sm">
          <p class="text-dark-300 flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5 shrink-0 text-[#86868b]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
            {{ client.phone }}
          </p>
          <p v-if="client.email" class="text-dark-300 flex items-center gap-1.5 truncate">
            <svg class="w-3.5 h-3.5 shrink-0 text-[#86868b]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
            <span class="truncate">{{ client.email }}</span>
          </p>
        </div>

        <div class="flex gap-2 mt-4">
          <button
            @click="viewHistory(client)"
            class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 text-[#1d1d1f] text-sm font-semibold transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            Historial
          </button>
          <button
            @click="deleteClient(client.id)"
            class="flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl border border-red-200 text-red-500 hover:bg-red-50 text-sm font-semibold transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            Ocultar
          </button>
        </div>
      </div>

      <div v-if="clients.length === 0" class="bg-white border border-gray-200 rounded-2xl p-8 text-center text-dark-500">
        No se encontraron clientes
      </div>
    </div>

    <!-- Paginación -->
    <div class="mt-3 bg-white border border-gray-200 rounded-xl px-4 py-3 flex justify-between items-center">
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

async function deleteClient(id: string) {
  if (!confirm('¿Ocultar este cliente? Dejará de aparecer en el listado, pero se conservará su historial de citas.')) return
  try {
    await adminApi.deleteClient(id)
    await loadClients()
  } catch (err) {
    const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    alert(typeof detail === 'string' ? detail : 'No se pudo ocultar el cliente.')
  }
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
