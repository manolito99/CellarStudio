<template>
  <div>
    <h3 class="text-2xl font-heading font-bold text-[#2B2E2E] mb-2">Tus datos</h3>
    <p class="text-dark-400 mb-6">Completá tu información para confirmar la cita</p>

    <div class="space-y-5 max-w-md">
      <div>
        <label class="block text-sm font-medium text-[#595959] mb-2">Nombre completo *</label>
        <input
          type="text"
          :value="name"
          @input="$emit('update:name', ($event.target as HTMLInputElement).value)"
          placeholder="Tu nombre"
          autocomplete="name"
          class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-[#2B2E2E] placeholder-gray-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-[#595959] mb-2">Teléfono *</label>
        <input
          type="tel"
          :value="phone"
          @input="$emit('update:phone', ($event.target as HTMLInputElement).value)"
          placeholder="+54 11 1234-5678"
          autocomplete="tel"
          class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-[#2B2E2E] placeholder-gray-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-[#595959] mb-2">Email (opcional)</label>
        <input
          type="email"
          :value="email"
          @input="$emit('update:email', ($event.target as HTMLInputElement).value)"
          placeholder="tu@email.com"
          autocomplete="email"
          class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-[#2B2E2E] placeholder-gray-400 focus:border-brand-400 focus:outline-none focus:ring-1 focus:ring-brand-400"
        />
        <p class="text-dark-500 text-xs mt-1">Si proporcionás email, recibirás una confirmación</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  name: string
  phone: string
  email: string
}>()

defineEmits<{
  'update:name': [value: string]
  'update:phone': [value: string]
  'update:email': [value: string]
}>()
</script>
