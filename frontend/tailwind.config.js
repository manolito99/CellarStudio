/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#fdf8f0',
          100: '#f0ddd0',
          200: '#d4a889',
          300: '#c08b6a',
          400: '#A66B4C',
          500: '#A66B4C',
          600: '#8B5A3E',
          700: '#704832',
          800: '#5a3a28',
          900: '#3d2719',
          950: '#2a1a10',
        },
        dark: {
          50: '#f6f6f6',
          100: '#e7e7e7',
          200: '#d1d1d1',
          300: '#595959',
          400: '#595959',
          500: '#7a7a7a',
          600: '#5d5d5d',
          700: '#d1d1d1',
          800: '#F2F0E9',
          900: '#F2F0E9',
          950: '#F2F0E9',
        },
      },
      fontFamily: {
        heading: ['Playfair Display', 'serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
