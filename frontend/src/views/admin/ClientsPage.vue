<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-[#1d1d1f]">Clientes</h1>
      <div class="flex gap-2">
        <button
          @click="exportCSV"
          :disabled="exporting"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-[#1d1d1f] text-sm font-medium rounded-lg border border-gray-200 transition-colors"
        >
          {{ exporting ? 'Exportando...' : 'Exportar CSV' }}
        </button>
        <button
          @click="openCreate"
          class="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors"
        >
          Nuevo cliente
        </button>
      </div>
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

    <div v-if="listError" class="mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-600">
      {{ listError }}
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

    <!-- Nuevo cliente. Teleport a <body> + dvh: dentro de <ion-content> la tab bar
         del AdminLayout tapa los botones cuando se abre el teclado. Mismo patron
         que AppointmentEditModal.vue. -->
    <Teleport to="body">
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 pb-[max(1rem,env(safe-area-inset-bottom))]">
      <div class="bg-white border border-gray-200 rounded-2xl w-full max-w-lg p-6 max-h-[90dvh] overflow-y-auto">
        <h2 class="text-xl font-bold text-[#1d1d1f] mb-6">Nuevo cliente</h2>
        <form @submit.prevent="saveClient()" class="space-y-4">
          <div>
            <label class="block text-sm text-dark-300 mb-1">Nombre</label>
            <input
              v-model="form.name"
              required
              maxlength="255"
              class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-dark-300 mb-1">Teléfono</label>
            <input
              v-model="form.phone"
              type="tel"
              required
              maxlength="50"
              class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
            />
            <p class="text-xs text-dark-500 mt-1">
              Identifica al cliente: sus reservas y notificaciones se enlazan por este número.
            </p>
          </div>
          <div>
            <label class="block text-sm text-dark-300 mb-1">Email (opcional)</label>
            <input
              v-model="form.email"
              type="email"
              maxlength="255"
              class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-brand-400 focus:outline-none"
            />
          </div>
          <div>
            <label class="block text-sm text-dark-300 mb-1">Notas (opcional)</label>
            <textarea
              v-model="form.notes"
              rows="3"
              maxlength="2000"
              class="w-full px-3 py-2 bg-[#f5f5f7] border border-gray-200 rounded-lg text-[#1d1d1f] focus:border-brand-400 focus:outline-none resize-none"
            />
          </div>

          <p v-if="createError" class="text-sm text-red-500">{{ createError }}</p>

          <!-- Acciones ancladas: con el teclado abierto el panel scrollea y los
               botones quedarian por debajo del corte. -->
          <div class="flex gap-3 pt-3 sticky bottom-0 bg-white -mx-6 px-6 pb-1 border-t border-gray-100">
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 px-4 py-2 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-medium rounded-lg transition-colors"
            >
              {{ saving ? 'Creando...' : 'Crear' }}
            </button>
            <button
              type="button"
              :disabled="saving"
              @click="showCreate = false"
              class="px-4 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-[#1d1d1f] rounded-lg transition-colors"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
    </Teleport>

    <!-- History Modal -->
    <Teleport to="body">
    <div v-if="showHistory" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 pb-[max(1rem,env(safe-area-inset-bottom))]">
      <div class="bg-white border border-gray-200 rounded-2xl w-full max-w-2xl p-6 max-h-[80dvh] overflow-y-auto">
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
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { adminApi, type Client, type Appointment } from '@/services/adminApi'
import { errorCode, errorMessage } from '@/utils/apiError'

const clients = ref<Client[]>([])
const search = ref('')
const page = ref(1)
const showCreate = ref(false)
const saving = ref(false)
const exporting = ref(false)
const createError = ref('')
const form = reactive({ name: '', phone: '', email: '', notes: '' })
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

const listError = ref('')

async function loadClients() {
  const params: Record<string, string | number> = { page: page.value }
  if (search.value) params.search = search.value
  try {
    clients.value = await adminApi.getClients(params)
    listError.value = ''
  } catch (err) {
    // Without this an expired session renders "No se encontraron clientes",
    // which is indistinguishable from an empty database.
    listError.value = errorMessage(err, 'No se pudo cargar el listado de clientes.')
  }
}

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    loadClients()
  }, 300)
}

function openCreate() {
  form.name = ''
  form.phone = ''
  form.email = ''
  form.notes = ''
  createError.value = ''
  saving.value = false
  showCreate.value = true
}

async function saveClient(restoreHidden = false) {
  if (saving.value) return
  createError.value = ''

  const name = form.name.trim()
  const phone = form.phone.trim()
  if (!name || !phone) {
    createError.value = 'El nombre y el teléfono son obligatorios.'
    return
  }

  saving.value = true
  let created: Client
  try {
    // Empty strings are not valid emails for the API: send null instead.
    created = await adminApi.createClient({
      name,
      phone,
      email: form.email.trim() || null,
      notes: form.notes.trim() || null,
      restore_hidden: restoreHidden,
    })
  } catch (err) {
    saving.value = false
    // The phone belongs to a hidden client: reusing that record keeps its
    // appointment history and push subscriptions, so it needs a conscious yes.
    if (errorCode(err) === 'hidden_client') {
      const message = errorMessage(err, 'Ese teléfono pertenece a un cliente oculto.')
      if (confirm(`${message}\n\n¿Restaurar esa ficha con los datos nuevos?`)) {
        await saveClient(true)
      }
      return
    }
    createError.value = errorMessage(err, 'No se pudo crear el cliente. Inténtalo de nuevo.')
    return
  }

  saving.value = false
  showCreate.value = false

  // Filter by the phone that was just registered. Sorting is by created_at
  // desc, so a restored client keeps its old date and would otherwise land
  // pages deep — the admin would see no error and no client.
  search.value = created.phone
  page.value = 1
  await loadClients()
}

async function viewHistory(client: Client) {
  try {
    clientHistory.value = await adminApi.getClientAppointments(client.id)
  } catch (err) {
    alert(errorMessage(err, 'No se pudo cargar el historial del cliente.'))
    return
  }
  selectedClient.value = client
  showHistory.value = true
}

async function deleteClient(id: string) {
  if (!confirm('¿Ocultar este cliente? Dejará de aparecer en el listado, pero se conservará su historial de citas.')) return
  try {
    await adminApi.deleteClient(id)
    await loadClients()
  } catch (err) {
    alert(errorMessage(err, 'No se pudo ocultar el cliente.'))
  }
}

function csvCell(value: string | null): string {
  const text = value || ''
  // Client names come from the public booking form, so an anonymous visitor
  // can choose them. A leading =, +, - or @ makes Excel/LibreOffice execute
  // the cell as a formula on open; prefixing a quote neutralises it.
  const safe = /^[=+\-@\t\r]/.test(text) ? `'${text}` : text
  // RFC 4180: escape by doubling the quotes, or a name containing " shifts
  // every following column.
  return `"${safe.replace(/"/g, '""')}"`
}

async function exportCSV() {
  if (exporting.value) return
  exporting.value = true
  try {
    // The table only holds the current page. Walk every page, otherwise the
    // owner silently gets 20 clients and believes it is the full list.
    const all: Client[] = []
    const perPage = 100
    for (let p = 1; ; p++) {
      const params: Record<string, string | number> = { page: p, per_page: perPage }
      if (search.value) params.search = search.value
      const batch = await adminApi.getClients(params)
      all.push(...batch)
      if (batch.length < perPage || p > 200) break
    }

    const header = 'Nombre,Teléfono,Email,Registrado\n'
    const rows = all
      .map((c) =>
        [csvCell(c.name), csvCell(c.phone), csvCell(c.email), csvCell(formatDate(c.created_at))].join(','),
      )
      .join('\r\n')
    // BOM so Excel on Windows reads it as UTF-8 instead of mangling accents.
    const blob = new Blob(['﻿' + header + rows], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'clientes_cellarstudio.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) {
    alert(errorMessage(err, 'No se pudo exportar el listado.'))
  } finally {
    exporting.value = false
  }
}

onMounted(loadClients)
</script>
