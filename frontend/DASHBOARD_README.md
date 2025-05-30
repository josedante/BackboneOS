# BackboneOS Dashboard UI

## Descripción

Esta es la nueva interfaz de dashboard para BackboneOS, diseñada como un CRM moderno con una experiencia de usuario profesional usando Tailwind CSS y Nuxt UI.

## Características Implementadas

### 🎨 Diseño y Layout

- **Dashboard Layout**: Layout reutilizable con sidebar y header (`layouts/dashboard.vue`)
- **Sidebar Responsivo**: Navegación lateral que se colapsa en móviles
- **Header Dinámico**: Header con información del usuario y notificaciones
- **Tema Personalizado**: Esquema de colores consistente para toda la aplicación

### 📊 Componentes de Dashboard

#### DashboardStatCard

Componente reutilizable para mostrar métricas clave:

- Título y valor principal
- Indicadores de cambio (incremento/decremento)
- Iconos personalizables
- Colores temáticos

#### ActivityFeed

Componente para mostrar actividad reciente:

- Timeline de actividades
- Iconos y colores por tipo de actividad
- Badges de prioridad
- Formato automático de tiempo

#### QuickActions

Componente para acciones rápidas:

- Botones de acción con iconos
- Badges opcionales
- Enlaces y funciones onClick

### 📱 Páginas Implementadas

#### Dashboard Principal (`/`)

- Métricas clave del negocio
- Actividad reciente
- Acciones rápidas
- Resumen de pipeline de ventas
- Barra de progreso del pipeline

#### Gestión de Usuarios (`/users`)

- Tabla de usuarios con filtros
- Estados de usuarios (activo/inactivo)
- Roles y permisos
- Acciones por usuario (ver, editar, eliminar)

#### Gestión de Leads (`/leads`)

- Lista completa de leads
- Filtros por estado y búsqueda
- Métricas de leads
- Fuentes de leads
- Actividad de leads

### 🎯 Características de UX

#### Navegación

- Navegación principal en sidebar
- Indicador visual de página activa
- Acceso rápido a secciones principales

#### Interactividad

- Hover effects en elementos interactivos
- Transiciones suaves
- Estados de carga
- Feedback visual en acciones

#### Responsividad

- Diseño mobile-first
- Sidebar colapsable en móviles
- Grids responsivos
- Tabla adaptativa

## Estructura de Archivos

```
frontend/
├── layouts/
│   └── dashboard.vue          # Layout principal del dashboard
├── pages/
│   ├── index.vue             # Dashboard principal
│   ├── users/
│   │   └── index.vue         # Gestión de usuarios
│   └── leads/
│       └── index.vue         # Gestión de leads
├── src/components/
│   ├── DashboardStatCard.vue # Tarjetas de estadísticas
│   ├── ActivityFeed.vue      # Feed de actividad
│   ├── QuickActions.vue      # Acciones rápidas
│   └── UserList.vue          # Lista de usuarios (legacy)
├── assets/css/
│   └── main.css              # Estilos globales personalizados
└── app.config.ts             # Configuración de tema
```

## Paleta de Colores

### Colores Primarios

- **Primary 500**: `#3b82f6` (Azul principal)
- **Primary 600**: `#2563eb` (Azul más oscuro)
- **Primary 50**: `#eff6ff` (Azul muy claro)

### Estados

- **Success**: Verde (`#10b981`)
- **Warning**: Amarillo (`#f59e0b`)
- **Error**: Rojo (`#ef4444`)
- **Info**: Azul (`#3b82f6`)

### Grises

- **Gray 50**: `#f9fafb` (Fondo claro)
- **Gray 900**: `#111827` (Texto oscuro)

## Iconografía

Usando Heroicons v2 para consistencia:

- **Leads**: `i-heroicons-user-plus`
- **Deals**: `i-heroicons-banknotes`
- **Reports**: `i-heroicons-chart-bar`
- **Settings**: `i-heroicons-cog-6-tooth`
- **Users**: `i-heroicons-user-group`

## Próximas Implementaciones

### Funcionalidades Pendientes

- [ ] Formularios de creación/edición
- [ ] Gráficos y charts interactivos
- [ ] Sistema de notificaciones avanzado
- [ ] Filtros avanzados
- [ ] Exportación de datos
- [ ] Dark mode toggle
- [ ] Personalización de dashboard

### Páginas por Crear

- [ ] `/opportunities` - Gestión de oportunidades
- [ ] `/deals` - Gestión de deals
- [ ] `/pipeline` - Vista de pipeline
- [ ] `/reports` - Reportes y analytics
- [ ] `/settings` - Configuraciones

## Uso

### Para usar el layout de dashboard:

```vue
<template>
  <NuxtLayout name="dashboard">
    <template #title>Título de la Página</template>
    <!-- Contenido de la página -->
  </NuxtLayout>
</template>
```

### Para crear tarjetas de estadísticas:

```vue
<DashboardStatCard
  title="Total Leads"
  value="2,847"
  change="+12.5% from last month"
  change-type="increase"
  icon="i-heroicons-user-plus"
  icon-bg="bg-blue-100"
  icon-color="text-blue-600"
/>
```

### Para mostrar actividad:

```vue
<ActivityFeed
  title="Recent Activity"
  :activities="activities"
  :loading="false"
  view-all-link="/activity"
  @activity-click="handleActivityClick"
/>
```

## Tecnologías Utilizadas

- **Nuxt.js 3.17.4**: Framework principal
- **Nuxt UI**: Biblioteca de componentes
- **Tailwind CSS**: Framework de CSS
- **Heroicons**: Iconografía
- **TypeScript**: Tipado estático

## Comandos de Desarrollo

```bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build para producción
npm run build

# Preview de build
npm run preview
```

La interfaz está optimizada para una experiencia de CRM profesional con enfoque en usabilidad y rendimiento.
