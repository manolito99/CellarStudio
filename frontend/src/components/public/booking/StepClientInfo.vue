<template>
  <div>
    <h3 class="text-2xl font-heading font-bold text-[#1d1d1f] mb-2">Tus datos</h3>
    <p class="text-dark-400 mb-6">Completa tu información para confirmar la cita</p>

    <!-- Saved profile indicator -->
    <Transition name="saved-badge">
      <div
        v-if="isPreFilled"
        class="flex items-center justify-between gap-3 mb-5 px-4 py-3 bg-[#f5f5f7] rounded-2xl"
      >
        <div class="flex items-center gap-2 min-w-0">
          <svg class="w-4 h-4 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
          </svg>
          <span class="text-sm text-[#1d1d1f] font-medium truncate">Datos guardados de tu última visita</span>
        </div>
        <button
          @click="clearSaved"
          class="text-xs text-[#86868b] hover:text-[#1d1d1f] transition-colors flex-shrink-0 underline underline-offset-2"
        >
          Limpiar
        </button>
      </div>
    </Transition>

    <div class="space-y-5 max-w-md">
      <div>
        <label class="block text-sm font-medium text-[#86868b] mb-2">Nombre completo *</label>
        <input
          type="text"
          :value="name"
          @input="$emit('update:name', ($event.target as HTMLInputElement).value)"
          placeholder="Tu nombre"
          autocomplete="name"
          class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-[#1d1d1f] placeholder-gray-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400 transition-colors"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-[#86868b] mb-2">Teléfono *</label>
        <input
          type="tel"
          :value="phone"
          @input="$emit('update:phone', ($event.target as HTMLInputElement).value)"
          placeholder="+34 600 000 000"
          autocomplete="tel"
          class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-[#1d1d1f] placeholder-gray-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400 transition-colors"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-[#86868b] mb-2">Email (opcional)</label>
        <input
          type="email"
          :value="email"
          @input="$emit('update:email', ($event.target as HTMLInputElement).value)"
          placeholder="tu@email.com"
          autocomplete="email"
          class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-[#1d1d1f] placeholder-gray-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400 transition-colors"
        />
        <p class="text-dark-500 text-xs mt-1">Si proporcionas tu email, recibirás una confirmación</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useClientProfile } from '@/composables/useClientProfile'

const props = defineProps<{
  name: string
  phone: string
  email: string
}>()

const emit = defineEmits<{
  'update:name': [value: string]
  'update:phone': [value: string]
  'update:email': [value: string]
}>()

const { clear } = useClientProfile()

// Show the badge when at least name and phone are pre-filled (not empty)
const isPreFilled = computed(() => !!props.name && !!props.phone)

function clearSaved() {
  clear()
  emit('update:name', '')
  emit('update:phone', '')
  emit('update:email', '')
}
</script>

<style scoped>
.saved-badge-enter-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.saved-badge-leave-active {
  transition: all 0.25s ease;
}
.saved-badge-enter-from {
  opacity: 0;
  transform: translateY(-6px);
}
.saved-badge-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
