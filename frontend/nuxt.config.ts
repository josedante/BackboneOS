// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-05-15",
  devtools: { enabled: true },

  modules: [
    "@nuxt/content",
    "@nuxt/eslint",
    "@nuxt/fonts",
    "@nuxt/icon",
    "@nuxt/image",
    "@nuxt/scripts",
    "@nuxt/test-utils",
    "@nuxt/ui",
  ],
  css: ["~/assets/css/main.css"],

  ui: {
    global: true,
    icons: ["heroicons", "simple-icons"],
  },

  colorMode: {
    preference: "light",
  },

  runtimeConfig: {
    // Private keys (only available on server-side)
    apiBase: process.env.NUXT_PRIVATE_API_BASE || "http://localhost:8000",

    // Public keys (exposed to client-side)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://localhost:8000",
      isDevelopment: process.env.NODE_ENV === "development",
    },
  },

  // Optimización para build
  vite: {
    css: {
      devSourcemap: true,
    },
  },

  // Configuración de desarrollo
  sourcemap: {
    server: false,
    client: false,
  },
});
