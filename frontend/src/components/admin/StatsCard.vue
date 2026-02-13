<template>
  <div class="bg-white border border-gray-200 rounded-xl p-5 hover:border-gray-300 transition-colors">
    <div class="flex items-center justify-between mb-3">
      <span class="text-sm text-dark-400">{{ label }}</span>
      <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="iconBg">
        <span v-html="icon" class="w-5 h-5" :class="iconColor"></span>
      </div>
    </div>
    <p class="text-2xl font-bold text-[#1d1d1f]">{{ formattedValue }}</p>
    <p v-if="subtitle" class="text-xs text-dark-500 mt-1">{{ subtitle }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: number | string
  icon: string
  iconBg?: string
  iconColor?: string
  subtitle?: string
  prefix?: string
}>()

const formattedValue = computed(() => {
  if (props.prefix && typeof props.value === 'number') {
    return `${props.prefix}${props.value.toLocaleString()}`
  }
  return typeof props.value === 'number' ? props.value.toLocaleString() : props.value
})
</script>
