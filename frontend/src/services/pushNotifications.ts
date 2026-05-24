import api from './api'

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

export function isPushSupported(): boolean {
  return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window
}

export function isPWA(): boolean {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (navigator as any).standalone === true
  )
}

export async function subscribeToPush(clientPhone: string): Promise<boolean> {
  if (!isPushSupported()) return false

  try {
    if (Notification.permission === 'denied') return false
    if (Notification.permission !== 'granted') {
      const permission = await Notification.requestPermission()
      if (permission !== 'granted') return false
    }

    const registration = await navigator.serviceWorker.ready

    const { data } = await api.get('/public/push/vapid-key')
    if (!data.public_key) return false

    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(data.public_key),
    })

    const subJson = subscription.toJSON()

    await api.post('/public/push/subscribe', {
      endpoint: subJson.endpoint,
      p256dh_key: subJson.keys?.p256dh,
      auth_key: subJson.keys?.auth,
      client_phone: clientPhone,
    })

    return true
  } catch (err) {
    console.error('Push subscription failed:', err)
    return false
  }
}
