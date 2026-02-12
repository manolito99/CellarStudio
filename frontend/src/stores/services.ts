import { defineStore } from 'pinia'
import { ref } from 'vue'
import { publicApi, type Service } from '@/services/publicApi'

export const useServicesStore = defineStore('services', () => {
  const services = ref<Service[]>([])
  const loading = ref(false)

  async function fetchServices() {
    loading.value = true
    try {
      services.value = await publicApi.getServices()
    } finally {
      loading.value = false
    }
  }

  return { services, loading, fetchServices }
})
