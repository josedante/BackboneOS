# Frontend - BackboneOS

## 🖥️ Frontend Nuxt.js Application

### 📋 Información General

El frontend de BackboneOS está construido con Nuxt.js 3.17.4 + TypeScript, diseñado como una **Single Page Application (SPA)** que consume la API REST del backend Django de manera completamente desacoplada.

## 🛠️ Stack Tecnológico Frontend

### Core Framework

- **Nuxt.js**: 3.17.4 (Framework full-stack Vue.js)
- **Vue.js**: 3.x (Framework reactivo de componentes)
- **TypeScript**: 5.8.3 (Tipado estático para JavaScript)

### UI & Styling

- **Nuxt UI**: 3.1.3 (Biblioteca de componentes UI)
- **Tailwind CSS**: Integrado via Nuxt UI (CSS utility-first)
- **Nuxt Icon**: Iconografía moderna y optimizada
- **Nuxt Fonts**: Gestión optimizada de fuentes web

### Módulos y Extensiones

- **@nuxt/content**: Gestión de contenido markdown/yaml
- **@nuxt/image**: Optimización automática de imágenes
- **@nuxt/scripts**: Gestión optimizada de scripts externos
- **@nuxt/test-utils**: Utilidades para testing

### Herramientas de Desarrollo

- **ESLint**: 9.27.0 (Linting y código limpio)
- **TypeScript Config**: Configuración estricta
- **Hot Module Replacement**: Desarrollo en tiempo real

## 🏗️ Arquitectura Frontend

### Estructura de Carpetas

```
frontend/
├── 📁 assets/              # Recursos estáticos (CSS, imágenes)
├── 📁 components/          # Componentes Vue.js reutilizables
├── 📁 composables/         # Lógica reutilizable de Vue 3
│   └── useAuth.ts         # ✅ Sistema de autenticación
├── 📁 layouts/            # Layouts de página
├── 📁 middleware/         # Middleware de rutas
│   └── auth.ts           # ✅ Middleware de autenticación
├── 📁 pages/              # Páginas de la aplicación (routing automático)
│   ├── index.vue         # Página principal
│   ├── login.vue         # ✅ Página de login
│   ├── analytics/        # 🔄 Páginas de analytics
│   ├── customers/        # 🔄 Gestión de clientes
│   ├── leads/           # 🔄 Gestión de leads
│   ├── products/        # 🔄 Gestión de productos
│   └── reports/         # 🔄 Reportes y dashboards
├── 📁 plugins/            # Plugins de Nuxt.js
│   └── auth.client.ts    # ✅ Plugin de autenticación cliente
├── 📁 server/             # API routes server-side (si es necesario)
├── 📁 src/                # Código fuente adicional
│   ├── components/        # Componentes específicos
│   └── services/          # Servicios de API
│       ├── api.ts        # ✅ Servicio API centralizado
│       └── userService.ts # ✅ Servicio de usuarios
└── 📁 public/             # Archivos públicos estáticos
```

### Sistema de Autenticación

**🔑 Autenticación JWT Completa Implementada**

```typescript
// composables/useAuth.ts - Gestión de estado de autenticación
const { login, logout, user, token, isAuthenticated } = useAuth();

// middleware/auth.ts - Protección de rutas
export default defineNuxtRouteMiddleware((to, from) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated.value) {
    return navigateTo("/login");
  }
});

// plugins/auth.client.ts - Inicialización de autenticación
// Recupera tokens del localStorage al cargar la aplicación
```

### Comunicación con Backend

**🔗 API Service Centralizado**

```typescript
// src/services/api.ts
const api = {
  // Configuración base de la API
  baseURL: 'http://localhost:8000/api/',

  // Métodos HTTP con autenticación automática
  get, post, put, delete,

  // Interceptors para tokens JWT
  // Manejo de errores centralizado
}
```

## 🎯 Páginas y Funcionalidades

### ✅ Implementadas

1. **Página Principal (`index.vue`)**

   - Dashboard principal del CRM
   - Resumen de métricas clave
   - Navegación a módulos principales

2. **Autenticación (`login.vue`)**

   - Login con email/password
   - Integración con JWT backend
   - Redirección automática post-login

3. **Sistema de Autenticación Completo**
   - Middleware de protección de rutas
   - Composable de gestión de estado
   - Plugin de inicialización

### 🔄 En Desarrollo

1. **Analytics Dashboard (`/analytics/`)**

   - Métricas de ventas y CRM
   - Gráficos interactivos
   - Filtros temporales

2. **Gestión de Clientes (`/customers/`)**

   - CRUD de personas y organizaciones
   - Perfilado semántico
   - Historial de interacciones

3. **Gestión de Leads (`/leads/`)**

   - Pipeline de ventas
   - Seguimiento de oportunidades
   - Asignación de responsables

4. **Gestión de Productos (`/products/`)**

   - Catálogo de productos
   - Gestión de categorías
   - Pricing y configuración

5. **Reportes (`/reports/`)**
   - Reportes personalizables
   - Exportación de datos
   - Business Intelligence

## 🚀 Comandos de Desarrollo Frontend

### Ambiente Local (Recomendado)

```bash
cd frontend

# Instalar dependencias
npm install

# Desarrollo con hot reload
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Linting y formato
npm run lint
npm run lint:fix
```

### Desarrollo

```bash
# Ejecutar en modo desarrollo
npm run dev
# Aplicación disponible en: http://localhost:3000

# Desarrollo con inspector Vue
npm run dev -- --inspect

# Desarrollo con puerto específico
npm run dev -- --port 3001
```

### Testing

```bash
# Tests unitarios (cuando se implementen)
npm run test

# Tests E2E (cuando se implementen)
npm run test:e2e

# Coverage de tests
npm run test:coverage
```

## 📱 Diseño Responsive

### Breakpoints Tailwind CSS

```css
/* Mobile First Approach */
sm:   640px   /* Tablet pequeña */
md:   768px   /* Tablet */
lg:   1024px  /* Desktop pequeño */
xl:   1280px  /* Desktop */
2xl:  1536px  /* Desktop grande */
```

### Componentes UI

El frontend utiliza **Nuxt UI** que proporciona:

- ✅ **Componentes prediseñados** con Tailwind CSS
- ✅ **Dark mode** integrado
- ✅ **Accesibilidad** WCAG compliant
- ✅ **Responsive design** automático
- ✅ **Theming** personalizable

## 🔮 Roadmap Frontend

### Próximas Funcionalidades

1. **🔄 Dashboard Principal**

   - Widgets personalizables
   - Métricas en tiempo real
   - Notificaciones push

2. **👥 CRM Completo**

   - Gestión de contactos avanzada
   - Timeline de interacciones
   - Segmentación de clientes

3. **📊 Analytics Avanzados**

   - Gráficos interactivos con Chart.js
   - Filtros dinámicos
   - Exportación de reportes

4. **📱 Progressive Web App (PWA)**

   - Funcionamiento offline
   - Notificaciones push
   - Instalación en dispositivos

5. **🌐 Internacionalización (i18n)**
   - Múltiples idiomas
   - Formatos de fecha/moneda
   - RTL support

## 🔧 Configuración y Personalización

### Variables de Entorno

```bash
# .env
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/
NUXT_PUBLIC_APP_NAME=BackboneOS
NUXT_PUBLIC_VERSION=1.0.0
```

### Configuración Nuxt

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // Configuración de módulos
  modules: ["@nuxt/ui", "@nuxt/content", "@nuxt/image"],

  // Configuración CSS
  css: ["~/assets/css/main.css"],

  // Configuración de runtime
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE_URL,
    },
  },
});
```

## 🔗 Integración con Backend

### Consumo de API

El frontend está diseñado para consumir todos los endpoints de la API REST del backend:

```typescript
// Ejemplos de consumo de API
const { data: users } = await api.get("/users/");
const { data: products } = await api.get("/products/products/");
const { data: offers } = await api.get("/offers/offerings/");
const { data: interactions } = await api.get("/interactions/interactions/");
```

### Sincronización de Datos

- **Estado reactivo** con refs y computed
- **Cache inteligente** para datos frecuentes
- **Actualizaciones en tiempo real** (futuro: WebSockets)
- **Optimistic updates** para mejor UX

## 📚 Documentación Específica

- **[README.md](../frontend/README.md)** - Guía de inicio rápido
- **[DASHBOARD_README.md](../frontend/DASHBOARD_README.md)** - Documentación del dashboard
- **[TROUBLESHOOTING.md](../frontend/TROUBLESHOOTING.md)** - Solución de problemas comunes

---

> **Frontend BackboneOS** - Interfaz moderna y escalable para el ecosistema CRM
