<template>
  <ion-page>
    <ion-header class="ion-no-border">
      <ion-toolbar color="dark">
        <ion-buttons slot="start">
          <ion-back-button default-href="/" text="" color="light" />
        </ion-buttons>
        <ion-title class="text-[#1d1d1f]">Reserva tu cita</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content :fullscreen="true" class="ion-padding">
      <div class="max-w-3xl mx-auto pb-20">
        <!-- Progress bar -->
        <div class="mb-10">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-[#86868b]">Paso {{ currentStep }} de {{ totalSteps }}</span>
            <span class="text-sm text-[#1d1d1f] font-medium">{{ stepLabels[currentStep - 1] }}</span>
          </div>
          <div class="w-full h-1 bg-[#e8e8ed] rounded-full overflow-hidden">
            <div
              class="h-full bg-[#1d1d1f] rounded-full transition-all duration-800 ease-out-expo"
              :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
            />
          </div>
        </div>

        <!-- Steps -->
        <Transition name="step" mode="out-in">
          <div class="mb-8" :key="currentStep">
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
        </Transition>

        <!-- Navigation -->
        <div class="flex items-center justify-between gap-4">
          <button
            v-if="currentStep > 1"
            @click="currentStep--"
            class="btn-secondary px-6 py-3 rounded-2xl border border-[#d2d2d7] text-[#1d1d1f] font-medium"
          >
            Anterior
          </button>
          <div v-else></div>

          <button
            v-if="currentStep < totalSteps"
            :disabled="!canGoNext"
            @click="currentStep++"
            class="btn-primary px-6 py-3 rounded-2xl bg-[#1d1d1f] text-white font-semibold disabled:opacity-30"
          >
            Siguiente
          </button>
          <button
            v-else
            :disabled="submitting"
            @click="confirmBooking"
            class="btn-primary px-6 py-3 rounded-2xl bg-[#1d1d1f] text-white font-semibold disabled:opacity-50"
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
  --background: #ffffff;
  --border-color: #e8e8ed;
}
ion-content {
  --background: #ffffff;
}
</style>
