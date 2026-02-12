import { computed } from 'vue'
import { isPlatform } from '@ionic/vue'

export function usePlatform() {
  const isNative = computed(() => isPlatform('capacitor'))
  const isIOS = computed(() => isPlatform('ios'))
  const isAndroid = computed(() => isPlatform('android'))
  const isWeb = computed(() => !isNative.value)
  const isMobile = computed(() => isPlatform('mobile'))

  return { isNative, isIOS, isAndroid, isWeb, isMobile }
}
