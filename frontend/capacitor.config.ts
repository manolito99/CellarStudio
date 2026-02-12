import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.cellarstudio.app',
  appName: 'Cellar Studio',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    // Para desarrollo: descomentar y poner la IP local de tu PC
    // url: 'http://192.168.x.x:8090',
    // cleartext: true,
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#F2F0E9',
      showSpinner: true,
      spinnerColor: '#A66B4C',
    },
    StatusBar: {
      style: 'LIGHT',
      backgroundColor: '#F2F0E9',
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
  },
}

export default config
