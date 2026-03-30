<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button default-href="/" text="" color="dark" />
        </ion-buttons>
        <ion-title class="font-semibold text-[#1d1d1f]">Mis reservas</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding">
      <div class="max-w-2xl mx-auto pb-20 pt-2">

        <!-- LOOKUP FORM -->
        <Transition name="fade" mode="out-in">
          <div v-if="!appointments" key="form">
            <!-- Header -->
            <div class="text-center mb-10">
              <div class="w-16 h-16 rounded-3xl bg-[#f5f5f7] flex items-center justify-center mx-auto mb-5">
                <svg class="w-8 h-8 text-[#1d1d1f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 class="text-2xl font-heading font-semibold text-[#1d1d1f] mb-2">Consulta tus citas</h2>
              <p class="text-[#6e6e73] text-sm leading-relaxed">
                Introduce el teléfono y correo que usaste al reservar<br class="hidden sm:block" />
                para ver y gestionar tus próximas citas.
              </p>
            </div>

            <!-- Form -->
            <div class="bg-white border border-[#e8e8ed] rounded-3xl p-6 shadow-sm space-y-4">
              <div>
                <label class="block text-xs font-semibold text-[#1d1d1f] uppercase tracking-wider mb-2">Teléfono</label>
                <input
                  v-model="lookupPhone"
                  type="tel"
                  placeholder="Ej: 612 345 678"
                  autocomplete="tel"
                  class="w-full px-4 py-3.5 bg-[#f5f5f7] border border-transparent rounded-2xl text-[#1d1d1f] placeholder-[#b0b0b5] focus:outline-none focus:ring-2 focus:ring-[#1d1d1f]/20 focus:border-[#1d1d1f] transition-all text-base"
                  @keyup.enter="lookupAppointments"
                />
              </div>
              <div>
                <label class="block text-xs font-semibold text-[#1d1d1f] uppercase tracking-wider mb-2">Correo electrónico</label>
                <input
                  v-model="lookupEmail"
                  type="email"
                  placeholder="Ej: nombre@correo.com"
                  autocomplete="email"
                  class="w-full px-4 py-3.5 bg-[#f5f5f7] border border-transparent rounded-2xl text-[#1d1d1f] placeholder-[#b0b0b5] focus:outline-none focus:ring-2 focus:ring-[#1d1d1f]/20 focus:border-[#1d1d1f] transition-all text-base"
                  @keyup.enter="lookupAppointments"
                />
              </div>

              <!-- Error -->
              <div v-if="lookupError" class="flex items-center gap-2.5 p-3.5 bg-red-50 border border-red-100 rounded-2xl">
                <svg class="w-4 h-4 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <span class="text-sm text-red-600">{{ lookupError }}</span>
              </div>

              <button
                @click="lookupAppointments"
                :disabled="!lookupPhone || !lookupEmail || loading"
                class="w-full py-4 bg-[#1d1d1f] text-white font-semibold rounded-2xl disabled:opacity-30 transition-all active:scale-[0.98] mt-2"
              >
                <span v-if="loading" class="flex items-center justify-center gap-2">
                  <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                  Buscando...
                </span>
                <span v-else>Ver mis citas</span>
              </button>
            </div>
          </div>

          <!-- APPOINTMENTS LIST -->
          <div v-else key="list">
            <!-- Header with back button -->
            <div class="flex items-center justify-between mb-6">
              <div>
                <h2 class="text-xl font-heading font-semibold text-[#1d1d1f]">Tus próximas citas</h2>
                <p class="text-sm text-[#86868b] mt-0.5">{{ appointments.length }} {{ appointments.length === 1 ? 'cita encontrada' : 'citas encontradas' }}</p>
              </div>
              <button
                @click="appointments = null; lookupError = ''"
                class="text-sm text-[#86868b] hover:text-[#1d1d1f] transition-colors px-3 py-1.5 rounded-xl hover:bg-[#f5f5f7]"
              >
                Cambiar datos
              </button>
            </div>

            <!-- Empty state -->
            <div v-if="appointments.length === 0" class="text-center py-16">
              <div class="w-16 h-16 rounded-3xl bg-[#f5f5f7] flex items-center justify-center mx-auto mb-4">
                <svg class="w-8 h-8 text-[#86868b]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p class="text-[#1d1d1f] font-semibold mb-1">Sin citas próximas</p>
              <p class="text-[#86868b] text-sm mb-6">No tienes citas futuras en este momento.</p>
              <router-link to="/booking" class="inline-block px-6 py-3 bg-[#1d1d1f] text-white font-semibold rounded-2xl">
                Reservar ahora
              </router-link>
            </div>

            <!-- Appointment cards -->
            <div v-else class="space-y-4">
              <div
                v-for="appt in appointments"
                :key="appt.id"
                class="bg-white border border-[#e8e8ed] rounded-3xl overflow-hidden shadow-sm"
              >
                <!-- Card header: service + status -->
                <div class="flex items-center justify-between px-5 pt-5 pb-3 border-b border-[#f5f5f7]">
                  <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-2xl bg-[#f5f5f7] flex items-center justify-center flex-shrink-0">
                      <svg class="w-5 h-5 text-[#1d1d1f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z"/>
                      </svg>
                    </div>
                    <div>
                      <p class="font-semibold text-[#1d1d1f] text-sm leading-tight">{{ appt.service.name }}</p>
                      <p class="text-xs text-[#86868b]">con {{ appt.barber.name }}</p>
                    </div>
                  </div>
                  <span :class="statusBadgeClass(appt.status)" class="text-xs font-semibold px-2.5 py-1 rounded-full">
                    {{ statusLabel(appt.status) }}
                  </span>
                </div>

                <!-- Card body: date + time -->
                <div class="px-5 py-4 flex items-center gap-6">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-[#86868b] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                    <span class="text-sm font-medium text-[#1d1d1f]">{{ formatDate(appt.date) }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-[#86868b] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                    <span class="text-sm font-medium text-[#1d1d1f]">{{ appt.start_time.slice(0, 5) }}</span>
                  </div>
                  <div v-if="appt.service.duration_minutes > 0" class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-[#86868b] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                    </svg>
                    <span class="text-sm text-[#86868b]">{{ formatDuration(appt.service.duration_minutes) }}</span>
                  </div>
                </div>

                <!-- Card actions -->
                <div class="px-5 pb-5 flex gap-3">
                  <button
                    @click="openModify(appt)"
                    class="flex-1 py-2.5 border border-[#d2d2d7] text-[#1d1d1f] text-sm font-semibold rounded-2xl hover:bg-[#f5f5f7] transition-colors active:scale-[0.98]"
                  >
                    Modificar
                  </button>
                  <button
                    @click="confirmCancel(appt)"
                    class="flex-1 py-2.5 border border-red-200 text-red-500 text-sm font-semibold rounded-2xl hover:bg-red-50 transition-colors active:scale-[0.98]"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>

            <!-- Book another -->
            <div v-if="appointments.length > 0" class="mt-6 text-center">
              <router-link to="/booking" class="inline-flex items-center gap-2 text-sm text-[#86868b] hover:text-[#1d1d1f] transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                </svg>
                Reservar otra cita
              </router-link>
            </div>
          </div>
        </Transition>
      </div>
    </ion-content>

    <!-- ===================== CANCEL CONFIRMATION MODAL ===================== -->
    <Transition name="modal">
      <div v-if="cancelTarget" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4" @click.self="cancelTarget = null">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="cancelTarget = null"></div>
        <div class="relative w-full max-w-sm bg-white rounded-3xl p-6 shadow-2xl">
          <div class="w-12 h-12 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-[#1d1d1f] text-center mb-1">¿Cancelar esta cita?</h3>
          <p class="text-sm text-[#86868b] text-center mb-6 leading-relaxed">
            {{ cancelTarget?.service?.name }} · {{ formatDate(cancelTarget?.date) }} a las {{ cancelTarget?.start_time?.slice(0,5) }}<br/>
            Esta acción no se puede deshacer.
          </p>
          <div class="flex gap-3">
            <button
              @click="cancelTarget = null"
              class="flex-1 py-3 border border-[#d2d2d7] text-[#1d1d1f] font-semibold rounded-2xl hover:bg-[#f5f5f7] transition-colors"
            >
              Volver
            </button>
            <button
              @click="executeCancel"
              :disabled="actionLoading"
              class="flex-1 py-3 bg-red-500 text-white font-semibold rounded-2xl hover:bg-red-600 transition-colors disabled:opacity-50"
            >
              {{ actionLoading ? 'Cancelando...' : 'Sí, cancelar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ===================== MODIFY MODAL ===================== -->
    <Transition name="modal">
      <div v-if="modifyTarget" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center" @click.self="closeModify">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeModify"></div>
        <div class="relative w-full max-w-lg bg-white rounded-t-3xl sm:rounded-3xl shadow-2xl max-h-[90vh] overflow-y-auto">
          <!-- Modal header -->
          <div class="sticky top-0 bg-white/95 backdrop-blur-sm px-6 pt-6 pb-4 border-b border-[#f5f5f7] rounded-t-3xl sm:rounded-t-3xl">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-[#1d1d1f]">Modificar cita</h3>
              <button @click="closeModify" class="w-8 h-8 rounded-full bg-[#f5f5f7] flex items-center justify-center hover:bg-[#e8e8ed] transition-colors">
                <svg class="w-4 h-4 text-[#1d1d1f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="px-6 py-5 space-y-6">

            <!-- Service selector -->
            <div>
              <label class="block text-xs font-semibold text-[#1d1d1f] uppercase tracking-wider mb-3">Servicio</label>
              <div class="grid grid-cols-1 gap-2">
                <button
                  v-for="svc in allServices"
                  :key="svc.id"
                  @click="modifyServiceId = svc.id; modifyBarberId = ''; modifyDate = ''; modifySlot = null; modifySlots = []"
                  :class="[
                    'flex items-center gap-3 p-3.5 rounded-2xl border-2 transition-all text-left',
                    modifyServiceId === svc.id
                      ? 'border-[#1d1d1f] bg-[#1d1d1f] text-white'
                      : 'border-[#e8e8ed] bg-white text-[#1d1d1f] hover:border-[#86868b]'
                  ]"
                >
                  <span class="font-medium text-sm flex-1">{{ svc.name }}</span>
                  <span :class="modifyServiceId === svc.id ? 'text-white/70' : 'text-[#86868b]'" class="text-xs">
                    {{ svc.duration_minutes > 0 ? formatDuration(svc.duration_minutes) : 'Consultar' }}
                  </span>
                </button>
              </div>
            </div>

            <!-- Barber selector -->
            <div v-if="modifyServiceId">
              <label class="block text-xs font-semibold text-[#1d1d1f] uppercase tracking-wider mb-3">Barbero</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="barber in filteredBarbers"
                  :key="barber.id"
                  @click="modifyBarberId = barber.id; modifyDate = ''; modifySlot = null; modifySlots = []"
                  :class="[
                    'flex flex-col items-center gap-2 p-3.5 rounded-2xl border-2 transition-all',
                    modifyBarberId === barber.id
                      ? 'border-[#1d1d1f] bg-[#1d1d1f] text-white'
                      : 'border-[#e8e8ed] bg-white text-[#1d1d1f] hover:border-[#86868b]'
                  ]"
                >
                  <div class="w-10 h-10 rounded-2xl overflow-hidden bg-[#e8e8ed] flex-shrink-0">
                    <img v-if="barber.photo_url" :src="barber.photo_url" :alt="barber.name" class="w-full h-full object-cover"/>
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <svg class="w-5 h-5 text-[#86868b]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                      </svg>
                    </div>
                  </div>
                  <span class="text-xs font-medium text-center leading-tight">{{ barber.name }}</span>
                </button>
              </div>
            </div>

            <!-- Date selector -->
            <div v-if="modifyBarberId">
              <label class="block text-xs font-semibold text-[#1d1d1f] uppercase tracking-wider mb-3">Nueva fecha</label>
              <input
                type="date"
                v-model="modifyDate"
                :min="minDate"
                :max="maxDate"
                @change="loadModifySlots"
                class="w-full px-4 py-3.5 bg-[#f5f5f7] border border-transparent rounded-2xl text-[#1d1d1f] focus:outline-none focus:ring-2 focus:ring-[#1d1d1f]/20 focus:border-[#1d1d1f] transition-all text-base"
              />
            </div>

            <!-- Time slots -->
            <div v-if="modifyDate">
              <label class="block text-xs font-semibold text-[#1d1d1f] uppercase tracking-wider mb-3">
                Hora disponible
                <span v-if="loadingModifySlots" class="ml-2 text-[#86868b] normal-case font-normal">Cargando...</span>
              </label>
              <div v-if="!loadingModifySlots && modifySlots.length === 0" class="text-center py-6 text-sm text-[#86868b]">
                No hay huecos disponibles para este día. Prueba otra fecha.
              </div>
              <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-2">
                <button
                  v-for="slot in modifySlots"
                  :key="slot.start_time"
                  @click="modifySlot = slot"
                  :class="[
                    'py-3 rounded-2xl border-2 text-sm font-semibold transition-all',
                    modifySlot?.start_time === slot.start_time
                      ? 'border-[#1d1d1f] bg-[#1d1d1f] text-white'
                      : 'border-[#e8e8ed] text-[#1d1d1f] hover:border-[#86868b]'
                  ]"
                >
                  {{ slot.start_time.slice(0, 5) }}
                </button>
              </div>
            </div>

            <!-- Error -->
            <div v-if="modifyError" class="flex items-center gap-2.5 p-3.5 bg-red-50 border border-red-100 rounded-2xl">
              <svg class="w-4 h-4 text-red-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
              <span class="text-sm text-red-600">{{ modifyError }}</span>
            </div>

            <!-- Save button -->
            <button
              @click="executeModify"
              :disabled="!modifySlot || actionLoading"
              class="w-full py-4 bg-[#1d1d1f] text-white font-semibold rounded-2xl disabled:opacity-30 transition-all active:scale-[0.98]"
            >
              {{ actionLoading ? 'Guardando...' : 'Guardar cambios' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </ion-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { IonPage, IonContent, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton } from '@ionic/vue'
import { publicApi, type Barber, type Service, type TimeSlot } from '@/services/publicApi'
import { useClientProfile } from '@/composables/useClientProfile'

// ---- Types ----
interface AppointmentFull {
  id: string
  date: string
  start_time: string
  end_time: string
  status: string
  service: Service
  barber: Barber
  client: { id: string; name: string; phone: string; email: string | null }
}

// ---- Lookup — pre-filled from saved profile ----
const { load: loadProfile } = useClientProfile()
const _savedProfile = loadProfile()
const lookupPhone = ref(_savedProfile?.phone ?? '')
const lookupEmail = ref(_savedProfile?.email ?? '')
const lookupError = ref('')
const loading = ref(false)
const appointments = ref<AppointmentFull[] | null>(null)

async function lookupAppointments() {
  if (!lookupPhone.value || !lookupEmail.value) return
  lookupError.value = ''
  loading.value = true
  try {
    const result = await publicApi.lookupMyAppointments(lookupPhone.value.trim(), lookupEmail.value.trim())
    appointments.value = result
  } catch (err: any) {
    const msg = err?.response?.data?.detail
    lookupError.value = msg || 'No encontramos ninguna cuenta con esos datos.'
  } finally {
    loading.value = false
  }
}

// ---- Cancel ----
const cancelTarget = ref<AppointmentFull | null>(null)
const actionLoading = ref(false)

function confirmCancel(appt: AppointmentFull) {
  cancelTarget.value = appt
}

async function executeCancel() {
  if (!cancelTarget.value) return
  actionLoading.value = true
  try {
    await publicApi.cancelMyAppointment(cancelTarget.value.id, lookupPhone.value.trim(), lookupEmail.value.trim())
    // Remove from list
    appointments.value = appointments.value?.filter(a => a.id !== cancelTarget.value!.id) ?? []
    cancelTarget.value = null
  } catch (err: any) {
    const msg = err?.response?.data?.detail
    alert(msg || 'Error al cancelar. Inténtalo de nuevo.')
  } finally {
    actionLoading.value = false
  }
}

// ---- Modify ----
const modifyTarget = ref<AppointmentFull | null>(null)
const allServices = ref<Service[]>([])
const allBarbers = ref<Barber[]>([])
const modifyServiceId = ref('')
const modifyBarberId = ref('')
const modifyDate = ref('')
const modifySlots = ref<TimeSlot[]>([])
const modifySlot = ref<TimeSlot | null>(null)
const loadingModifySlots = ref(false)
const modifyError = ref('')

const filteredBarbers = computed(() => {
  if (!modifyServiceId.value) return allBarbers.value
  return allBarbers.value.filter(b => b.services.some(s => s.id === modifyServiceId.value))
})

const minDate = computed(() => {
  const d = new Date()
  return d.toISOString().split('T')[0]
})

const maxDate = computed(() => {
  const d = new Date()
  d.setMonth(d.getMonth() + 3)
  return d.toISOString().split('T')[0]
})

function openModify(appt: AppointmentFull) {
  modifyTarget.value = appt
  modifyServiceId.value = appt.service.id
  modifyBarberId.value = appt.barber.id
  modifyDate.value = ''
  modifySlot.value = null
  modifySlots.value = []
  modifyError.value = ''
}

function closeModify() {
  modifyTarget.value = null
  modifyError.value = ''
}

async function loadModifySlots() {
  if (!modifyBarberId.value || !modifyDate.value || !modifyServiceId.value) return
  loadingModifySlots.value = true
  modifySlot.value = null
  modifySlots.value = []
  try {
    const result = await publicApi.getAvailability(modifyBarberId.value, modifyDate.value, modifyServiceId.value)
    modifySlots.value = result.slots.filter(s => s.available)
  } finally {
    loadingModifySlots.value = false
  }
}

async function executeModify() {
  if (!modifyTarget.value || !modifySlot.value) return
  actionLoading.value = true
  modifyError.value = ''
  try {
    const updated = await publicApi.modifyMyAppointment(
      modifyTarget.value.id,
      lookupPhone.value.trim(),
      lookupEmail.value.trim(),
      modifyServiceId.value,
      modifyBarberId.value,
      modifyDate.value,
      modifySlot.value.start_time,
    )
    // Update in list
    if (appointments.value) {
      const idx = appointments.value.findIndex(a => a.id === modifyTarget.value!.id)
      if (idx !== -1) appointments.value[idx] = updated
    }
    closeModify()
  } catch (err: any) {
    modifyError.value = err?.response?.data?.detail || 'Error al modificar. Inténtalo de nuevo.'
  } finally {
    actionLoading.value = false
  }
}

// ---- Helpers ----
function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr + 'T12:00:00')
  return d.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })
}

function formatDuration(minutes: number): string {
  if (minutes === 0) return 'Consultar'
  if (minutes % 60 === 0) return `${minutes / 60}h`
  if (minutes < 60) return `${minutes} min`
  return `${Math.floor(minutes / 60)}h ${minutes % 60}min`
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    pending: 'Pendiente',
    confirmed: 'Confirmada',
    completed: 'Completada',
    cancelled: 'Cancelada',
    noshow: 'No presentado',
  }
  return labels[status] ?? status
}

function statusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    pending: 'bg-amber-50 text-amber-600',
    confirmed: 'bg-green-50 text-green-600',
    completed: 'bg-[#f5f5f7] text-[#86868b]',
    cancelled: 'bg-red-50 text-red-500',
    noshow: 'bg-red-50 text-red-500',
  }
  return classes[status] ?? 'bg-[#f5f5f7] text-[#86868b]'
}

onMounted(async () => {
  const [s, b] = await Promise.all([publicApi.getServices(), publicApi.getBarbers()])
  allServices.value = s
  allBarbers.value = b

  // Auto-lookup if we already have phone + email saved
  if (lookupPhone.value && lookupEmail.value) {
    lookupAppointments()
  }
})
</script>

<style scoped>
ion-toolbar {
  --background: #ffffff;
  --border-color: #e8e8ed;
}
ion-content {
  --background: #f5f5f7;
}

/* Fade transition */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from { opacity: 0; transform: translateY(8px); }
.fade-leave-to { opacity: 0; transform: translateY(-8px); }

/* Modal transition */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}
.modal-enter-active .relative, .modal-leave-active .relative {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-enter-from { opacity: 0; }
.modal-enter-from .relative { transform: translateY(40px); }
.modal-leave-to { opacity: 0; }
</style>
