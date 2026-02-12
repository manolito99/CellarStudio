import { ref, computed } from 'vue'
import { publicApi, type Service, type Barber, type TimeSlot } from '@/services/publicApi'

export function useBooking() {
  const currentStep = ref(1)
  const totalSteps = 5

  // Step 1: Services
  const services = ref<Service[]>([])
  const selectedService = ref<Service | null>(null)

  // Step 2: Barber
  const barbers = ref<Barber[]>([])
  const selectedBarber = ref<Barber | null>(null)

  // Step 3: Date & Time
  const selectedDate = ref<string>('')
  const availableSlots = ref<TimeSlot[]>([])
  const selectedSlot = ref<TimeSlot | null>(null)
  const loadingSlots = ref(false)

  // Step 4: Client info
  const clientName = ref('')
  const clientPhone = ref('')
  const clientEmail = ref('')

  // Step 5: Notes
  const notes = ref('')

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

  async function loadServices() {
    services.value = await publicApi.getServices()
  }

  async function loadBarbers() {
    barbers.value = await publicApi.getBarbers()
  }

  async function loadAvailability() {
    if (!selectedBarber.value || !selectedDate.value || !selectedService.value) return
    loadingSlots.value = true
    try {
      const result = await publicApi.getAvailability(
        selectedBarber.value.id,
        selectedDate.value,
        selectedService.value.id,
      )
      availableSlots.value = result.slots.filter((s) => s.available)
    } finally {
      loadingSlots.value = false
    }
  }

  async function submitBooking() {
    if (!selectedService.value || !selectedBarber.value || !selectedSlot.value) return

    return await publicApi.createAppointment({
      client_name: clientName.value,
      client_phone: clientPhone.value,
      client_email: clientEmail.value || undefined,
      barber_id: selectedBarber.value.id,
      service_id: selectedService.value.id,
      date: selectedDate.value,
      start_time: selectedSlot.value.start_time,
      notes: notes.value || undefined,
    })
  }

  function nextStep() {
    if (currentStep.value < totalSteps && canGoNext.value) {
      currentStep.value++
    }
  }

  function prevStep() {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  function reset() {
    currentStep.value = 1
    selectedService.value = null
    selectedBarber.value = null
    selectedDate.value = ''
    availableSlots.value = []
    selectedSlot.value = null
    clientName.value = ''
    clientPhone.value = ''
    clientEmail.value = ''
    notes.value = ''
  }

  return {
    currentStep,
    totalSteps,
    services,
    selectedService,
    barbers,
    selectedBarber,
    selectedDate,
    availableSlots,
    selectedSlot,
    loadingSlots,
    clientName,
    clientPhone,
    clientEmail,
    notes,
    canGoNext,
    loadServices,
    loadBarbers,
    loadAvailability,
    submitBooking,
    nextStep,
    prevStep,
    reset,
  }
}
