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
            Tu cita fue registrada exitosamente. Te esperamos en Cellar Studio.
            Si proporcionaste tu email, recibirás una confirmación.
          </p>

          <div class="confirm-entrance confirm-delay-3 flex flex-col gap-3">
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
import { IonPage, IonContent } from '@ionic/vue'
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
