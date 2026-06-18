import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  vite: {
    plugins: [tailwindcss()],
  },

  css: ['~/assets/css/main.css'],

  routeRules: {
    '/api/**': { proxy: `${process.env.API_PROXY_TARGET ||  'http://localhost:8000'}/**` },
  },
})
