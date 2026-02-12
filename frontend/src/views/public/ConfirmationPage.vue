<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <div class="min-h-screen bg-[#F2F0E9] flex items-center justify-center px-4">
        <div class="text-center max-w-md">
          <!-- Success icon -->
          <div class="w-24 h-24 mx-auto mb-8 rounded-full bg-green-500/10 border-2 border-green-500 flex items-center justify-center">
            <svg class="w-12 h-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>

          <h1 class="text-3xl font-heading font-bold text-[#2B2E2E] mb-4">
            ¡Reserva confirmada!
          </h1>
          <p class="text-[#595959] mb-8 leading-relaxed">
            Tu cita fue registrada exitosamente. Te esperamos en Cellar Studio.
            Si proporcionaste tu email, recibirás una confirmación.
          </p>

          <div class="flex flex-col gap-3">
            <ion-button expand="block" color="warning" router-link="/booking">
              Hacer otra reserva
            </ion-button>
            <ion-button expand="block" fill="outline" color="medium" router-link="/">
              Volver al inicio
            </ion-button>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { IonPage, IonContent, IonButton } from '@ionic/vue'
</script>
