<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="min-h-screen bg-white flex items-center justify-center px-4">
        <div class="text-center max-w-md">
          <!-- Success icon with draw animation -->
          <div class="confirm-entrance confirm-delay-0 w-24 h-24 mx-auto mb-8 relative">
            <div class="absolute inset-0 rounded-full bg-green-500/10 scale-0 animate-success-ring"></div>
            <div class="absolute inset-0 rounded-full border-2 border-green-500/30 flex items-center justify-center">
              <svg class="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  class="check-draw"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
          </div>

          <h1 class="confirm-entrance confirm-delay-1 text-3xl font-heading font-semibold text-[#1d1d1f] mb-4 tracking-tight">
            ¡Reserva confirmada!
          </h1>
          <p class="confirm-entrance confirm-delay-2 text-[#86868b] mb-10 leading-relaxed">
            Tu cita fue registrada exitosamente. Te esperamos en Cellar Barber Studio.
            Si proporcionaste tu email, recibirás una confirmación.
          </p>

          <div class="confirm-entrance confirm-delay-3 flex flex-col gap-3">

            <!-- Calendar buttons (only shown if booking data is available) -->
            <template v-if="booking">
              <button
                @click="downloadICS"
                class="w-full px-6 py-3.5 bg-[#1d1d1f] text-white font-semibold rounded-2xl flex items-center justify-center gap-2"
              >
                <!-- Apple Calendar icon -->
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                </svg>
                Añadir a Apple Calendar
              </button>

              <a
                :href="googleCalendarUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="w-full px-6 py-3.5 border border-[#d2d2d7] text-[#1d1d1f] font-semibold rounded-2xl flex items-center justify-center gap-2"
              >
                <!-- Google Calendar icon -->
                <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none">
                  <path d="M19.5 3h-2V1.5h-1.5V3h-8V1.5H6.5V3h-2C3.67 3 3 3.67 3 4.5v15c0 .83.67 1.5 1.5 1.5h15c.83 0 1.5-.67 1.5-1.5v-15c0-.83-.67-1.5-1.5-1.5zm0 16.5h-15V9h15v10.5zm0-12h-15V4.5h2V6H8V4.5h8V6h1.5V4.5h2V7.5z" fill="#4285F4"/>
                  <path d="M7.5 11h2v1.5h-2V11zm0 3h2v1.5h-2V14zm3.5-3h2v1.5H11V11zm0 3h2v1.5H11V14zm3.5-3h2v1.5h-2V11zm0 3h2v1.5h-2V14z" fill="#4285F4"/>
                </svg>
                Añadir a Google Calendar
              </a>

              <div class="border-t border-[#e8e8ed] my-1"></div>
            </template>

            <router-link
              to="/booking"
              class="btn-primary w-full px-6 py-3.5 bg-[#1d1d1f] text-white font-semibold rounded-2xl text-center"
            >
              Hacer otra reserva
            </router-link>
            <router-link
              to="/"
              class="btn-secondary w-full px-6 py-3.5 border border-[#d2d2d7] text-[#1d1d1f] font-medium rounded-2xl text-center"
            >
              Volver al inicio
            </router-link>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IonPage, IonContent } from '@ionic/vue'
import { downloadPublicBookingICS, getGoogleCalendarUrl as buildGoogleUrl, type PublicBookingData } from '@/utils/icsExport'

// Data passed via router state from BookingPage
const booking = computed<PublicBookingData | null>(() => {
  const s = history.state
  if (!s?.serviceName || !s?.date || !s?.startTime || !s?.endTime) return null
  return {
    serviceName: s.serviceName,
    barberName:  s.barberName,
    date:        s.date,
    startTime:   s.startTime,
    endTime:     s.endTime,
  }
})

const googleCalendarUrl = computed(() =>
  booking.value ? buildGoogleUrl(booking.value) : '#'
)

function downloadICS() {
  if (booking.value) downloadPublicBookingICS(booking.value)
}
</script>

<style scoped>
ion-content {
  --background: #ffffff;
}

/* Staggered entrance */
.confirm-entrance {
  opacity: 0;
  transform: translateY(30px);
  animation: confirmReveal 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.confirm-delay-0 { animation-delay: 0.1s; }
.confirm-delay-1 { animation-delay: 0.35s; }
.confirm-delay-2 { animation-delay: 0.5s; }
.confirm-delay-3 { animation-delay: 0.65s; }

@keyframes confirmReveal {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Success ring pulse */
@keyframes successRing {
  0% { transform: scale(0); opacity: 1; }
  60% { transform: scale(1.15); opacity: 0.6; }
  100% { transform: scale(1); opacity: 1; }
}
.animate-success-ring {
  animation: successRing 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
}

/* Checkmark draw */
.check-draw {
  stroke-dasharray: 30;
  stroke-dashoffset: 30;
  animation: drawCheck 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.5s forwards;
}
@keyframes drawCheck {
  to { stroke-dashoffset: 0; }
}
</style>
