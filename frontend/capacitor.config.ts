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
      backgroundColor: '#ffffff',
      showSpinner: true,
      spinnerColor: '#000000',
    },
    StatusBar: {
      style: 'LIGHT',
      backgroundColor: '#ffffff',
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
  },
}

export default config
