<template>
  <!-- Teleport a <body>: dentro de <ion-content> el modal queda atrapado en el
       contexto de apilamiento de .ion-page (Ionic le pone contain:layout), y la
       tab bar del AdminLayout lo pinta por encima. Subir el z-index NO sirve
       (el modal de edicion lo intento con z-[200] y seguia tapado): hay que
       salir del arbol. Ver CLAUDE.md > "Modales del admin".
       max-h en dvh, no vh: dvh sigue al viewport visible, asi que al abrirse el
       teclado el modal encoge y los botones siguen a la vista. -->
  <Teleport to="body">
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 pb-[max(1rem,env(safe-area-inset-bottom))]" @click.self="$emit('close')">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')" />

    <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[92dvh] overflow-y-auto">

      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200 sticky top-0 bg-white z-10 rounded-t-2xl">
        <h2 class="text-lg font-bold text-gray-900">Nueva cita</h2>
        <button
          @click="$emit('close')"
          class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="p-4 space-y-4">

        <!-- ── Client search ──────────────────────────────────── -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Cliente</label>

          <!-- Already selected -->
          <div
            v-if="selectedClient"
            class="flex items-center justify-between px-3 py-2.5 bg-gray-100 rounded-lg"
          >
            <div class="min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate">{{ selectedClient.name }}</p>
              <p class="text-xs text-gray-500">{{ selectedClient.phone }}</p>
            </div>
            <button
              @click="clearClient"
              class="ml-3 flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Search input + dropdown -->
          <div v-else class="relative">
            <input
              v-model="clientSearch"
              type="text"
              placeholder="Buscar por nombre o teléfono..."
              class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:border-black focus:outline-none transition-colors"
              autocomplete="off"
            />
            <!-- Dropdown results -->
            <div
              v-if="clientSearch.length >= 2 && filteredClients.length > 0"
              class="absolute top-full left-0 right-0 z-20 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto"
            >
              <button
                v-for="c in filteredClients"
                :key="c.id"
                @click="selectClient(c)"
                class="w-full text-left px-3 py-2.5 text-sm hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0"
              >
                <span class="font-medium text-gray-800">{{ c.name }}</span>
                <span class="text-gray-400 ml-2 text-xs">{{ c.phone }}</span>
              </button>
            </div>
            <!-- No results -->
            <p
              v-if="clientSearch.length >= 2 && filteredClients.length === 0"
              class="mt-1.5 text-xs text-gray-400"
            >
              No se encontró ningún cliente con ese nombre o teléfono.
            </p>
          </div>
        </div>

        <!-- ── Service ──────────────────────────────────────────── -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Servicio</label>
          <select
            v-model="form.service_id"
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 focus:border-black focus:outline-none transition-colors"
          >
            <option value="" disabled>Selecciona un servicio</option>
            <option v-for="s in services" :key="s.id" :value="s.id">
              {{ s.name }}
            </option>
          </select>
        </div>

        <!-- ── Barber ───────────────────────────────────────────── -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Barbero</label>
          <select
            v-model="form.barber_id"
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 focus:border-black focus:outline-none transition-colors"
          >
            <option value="" disabled>Selecciona un barbero</option>
            <option v-for="b in barbers" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>

        <!-- ── Date ────────────────────────────────────────────── -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Fecha</label>
          <input
            v-model="form.date"
            type="date"
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 focus:border-black focus:outline-none transition-colors"
          />
        </div>

        <!-- ── Start time ──────────────────────────────────────── -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Hora de inicio</label>
          <input
            v-model="form.start_time"
            type="time"
            step="900"
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 focus:border-black focus:outline-none transition-colors"
          />
        </div>

        <!-- ── Notes ──────────────────────────────────────────── -->
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Notas <span class="font-normal text-gray-400">(opcional)</span></label>
          <textarea
            v-model="form.notes"
            rows="2"
            placeholder="Notas internas sobre la cita..."
            class="w-full px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:border-black focus:outline-none transition-colors resize-none"
          />
        </div>

      </div>

      <!-- Error banner -->
      <div
        v-if="errorMsg"
        class="mx-4 mb-4 px-3 py-2.5 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600"
      >
        {{ errorMsg }}
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-end gap-2 p-4 border-t border-gray-200 sticky bottom-0 bg-white rounded-b-2xl">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-sm font-medium text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
        >
          Cancelar
        </button>
        <button
          @click="handleCreate"
          :disabled="!isValid || saving"
          class="px-5 py-2 text-sm font-semibold text-white bg-black rounded-lg hover:bg-gray-800 active:bg-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {{ saving ? 'Creando...' : 'Crear cita' }}
        </button>
      </div>

    </div>
  </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { adminApi } from '@/services/adminApi'
import type { Client } from '@/services/adminApi'

const emit = defineEmits<{ close: []; saved: [] }>()

// ── Remote data ───────────────────────────────────────────────────────────────
const services   = ref<{ id: string; name: string; price: number }[]>([])
const barbers    = ref<{ id: string; name: string }[]>([])
const allClients = ref<Client[]>([])

// ── Client search ─────────────────────────────────────────────────────────────
const clientSearch   = ref('')
const selectedClient = ref<Client | null>(null)

const filteredClients = computed(() => {
  if (clientSearch.value.length < 2) return []
  const q = clientSearch.value.toLowerCase()
  return allClients.value
    .filter(c =>
      c.name.toLowerCase().includes(q) ||
      c.phone.includes(clientSearch.value)
    )
    .slice(0, 8)
})

function selectClient(c: Client) {
  selectedClient.value = c
  clientSearch.value   = ''
}

function clearClient() {
  selectedClient.value = null
  clientSearch.value   = ''
}

// ── Form ──────────────────────────────────────────────────────────────────────
function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const form = reactive({
  service_id: '',
  barber_id:  '',
  date:       todayStr(),
  start_time: '10:00',
  notes:      '',
})

const saving    = ref(false)
const errorMsg  = ref('')

const isValid = computed(() =>
  !!selectedClient.value &&
  !!form.service_id &&
  !!form.barber_id &&
  !!form.date &&
  !!form.start_time
)

async function handleCreate() {
  if (!isValid.value || saving.value) return
  saving.value   = true
  errorMsg.value = ''
  try {
    await adminApi.createAppointment({
      client_id:  selectedClient.value!.id,
      barber_id:  form.barber_id,
      service_id: form.service_id,
      date:       form.date,
      start_time: form.start_time + ':00',
      notes:      form.notes || null,
    })
    emit('saved')
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    errorMsg.value = typeof detail === 'string'
      ? detail
      : 'Error al crear la cita. Comprueba los datos e inténtalo de nuevo.'
  } finally {
    saving.value = false
  }
}

// ── Mount: load selects + clients ─────────────────────────────────────────────
onMounted(async () => {
  try {
    const [s, b, c] = await Promise.all([
      adminApi.getServices(),
      adminApi.getBarbers(),
      adminApi.getClients(),
    ])
    services.value   = s
    barbers.value    = b
    // Handle both plain array and paginated responses
    allClients.value = Array.isArray(c) ? c : (c?.items ?? c?.clients ?? [])
  } catch {
    // Non-critical — selects will just be empty
  }
})
</script>
