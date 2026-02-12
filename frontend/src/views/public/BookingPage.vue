<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar color="dark">
        <ion-buttons slot="start">
          <ion-back-button default-href="/" text="" color="light" />
        </ion-buttons>
        <ion-title class="text-[#2B2E2E]">Reserva tu cita</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding">
      <div class="max-w-3xl mx-auto pb-20">
        <!-- Progress bar -->
        <div class="mb-8">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm text-dark-400">Paso {{ currentStep }} de {{ totalSteps }}</span>
            <span class="text-sm text-brand-400 font-medium">{{ stepLabels[currentStep - 1] }}</span>
          </div>
          <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              class="h-full bg-gradient-to-r from-brand-500 to-brand-400 rounded-full transition-all duration-500"
              :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
            />
          </div>
        </div>

        <!-- Steps -->
        <div class="mb-8">
          <StepServices
            v-if="currentStep === 1"
            :services="services"
            :selected="selectedService"
            @select="selectedService = $event"
          />
          <StepBarber
            v-else-if="currentStep === 2"
            :barbers="filteredBarbers"
            :selected="selectedBarber"
            @select="selectedBarber = $event"
          />
          <StepDateTime
            v-else-if="currentStep === 3"
            :selectedDate="selectedDate"
            :slots="availableSlots"
            :selectedSlot="selectedSlot"
            :loading="loadingSlots"
            @selectDate="onDateChange"
            @selectSlot="selectedSlot = $event"
          />
          <StepClientInfo
            v-else-if="currentStep === 4"
            v-model:name="clientName"
            v-model:phone="clientPhone"
            v-model:email="clientEmail"
          />
          <StepConfirm
            v-else-if="currentStep === 5"
            :service="selectedService"
            :barber="selectedBarber"
            :date="selectedDate"
            :slot="selectedSlot"
            :clientName="clientName"
            :clientPhone="clientPhone"
          />
        </div>

        <!-- Navigation -->
        <div class="flex items-center justify-between gap-4">
          <button
            v-if="currentStep > 1"
            @click="currentStep--"
            class="px-5 py-3 rounded-xl border border-gray-200 text-[#2B2E2E] font-medium active:bg-gray-100 transition-colors"
          >
            Anterior
          </button>
          <div v-else></div>

          <button
            v-if="currentStep < totalSteps"
            :disabled="!canGoNext"
            @click="currentStep++"
            class="px-5 py-3 rounded-xl bg-brand-500 text-white font-semibold disabled:opacity-30 active:bg-brand-600 transition-colors"

          >
            Siguiente
          </button>
          <button
            v-else
            :disabled="submitting"
            @click="confirmBooking"
            class="px-5 py-3 rounded-xl bg-brand-500 text-white font-semibold disabled:opacity-50 active:bg-brand-600 transition-colors"

          >
            {{ submitting ? 'Reservando...' : 'Confirmar reserva' }}
          </button>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { IonPage, IonContent, IonHeader, IonToolbar, IonTitle, IonButtons, IonBackButton } from '@ionic/vue'
import { publicApi, type Service, type Barber, type TimeSlot } from '@/services/publicApi'
import StepServices from '@/components/public/booking/StepServices.vue'
import StepBarber from '@/components/public/booking/StepBarber.vue'
import StepDateTime from '@/components/public/booking/StepDateTime.vue'
import StepClientInfo from '@/components/public/booking/StepClientInfo.vue'
import StepConfirm from '@/components/public/booking/StepConfirm.vue'

const router = useRouter()
const submitting = ref(false)

const currentStep = ref(1)
const totalSteps = 5
const stepLabels = ['Servicio', 'Barbero', 'Fecha y hora', 'Tus datos', 'Confirmación']

// Step 1
const services = ref<Service[]>([])
const selectedService = ref<Service | null>(null)

// Step 2
const barbers = ref<Barber[]>([])
const selectedBarber = ref<Barber | null>(null)

// Step 3
const selectedDate = ref('')
const availableSlots = ref<TimeSlot[]>([])
const selectedSlot = ref<TimeSlot | null>(null)
const loadingSlots = ref(false)

// Step 4
const clientName = ref('')
const clientPhone = ref('')
const clientEmail = ref('')

const filteredBarbers = computed(() => {
  if (!selectedService.value) return barbers.value
  return barbers.value.filter((b) =>
    b.services.some((s) => s.id === selectedService.value!.id),
  )
})

const canGoNext = computed(() => {
  switch (currentStep.value) {
    case 1: return !!selectedService.value
    case 2: return !!selectedBarber.value
    case 3: return !!selectedDate.value && !!selectedSlot.value
    case 4: return !!clientName.value && !!clientPhone.value
    case 5: return true
    default: return false
  }
})

async function onDateChange(date: string) {
  selectedDate.value = date
  selectedSlot.value = null
  if (!selectedBarber.value || !selectedService.value) return
  loadingSlots.value = true
  try {
    const result = await publicApi.getAvailability(
      selectedBarber.value.id,
      date,
      selectedService.value.id,
    )
    availableSlots.value = result.slots.filter((s) => s.available)
  } finally {
    loadingSlots.value = false
  }
}

async function confirmBooking() {
  if (!selectedService.value || !selectedBarber.value || !selectedSlot.value) return
  submitting.value = true
  try {
    await publicApi.createAppointment({
      client_name: clientName.value,
      client_phone: clientPhone.value,
      client_email: clientEmail.value || undefined,
      barber_id: selectedBarber.value.id,
      service_id: selectedService.value.id,
      date: selectedDate.value,
      start_time: selectedSlot.value.start_time,
    })
    router.push('/confirmation')
  } catch {
    alert('Error al crear la reserva. Intentá de nuevo.')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const [s, b] = await Promise.all([publicApi.getServices(), publicApi.getBarbers()])
  services.value = s
  barbers.value = b
})
</script>

<style scoped>
ion-toolbar {
  --background: #F2F0E9;
  --border-color: #e5e7eb;
}
ion-content {
  --background: #F2F0E9;
}
</style>
