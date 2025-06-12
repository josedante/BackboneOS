# Arquitectura del Sistema BackboneOS

## 🏗️ Arquitectura General

BackboneOS es una aplicación full-stack moderna que combina:

- **Backend**: Django 5.x + Django REST Framework
- **Frontend**: Nuxt.js 3.17.4 + TypeScript 5.8.3
- **Base de Datos**: PostgreSQL 14
- **Caché y Sesiones**: Redis 7 con django-redis
- **Containerización**: Docker + Docker Compose (desarrollo híbrido)

## 🎯 Valor Empresarial del Ecosistema

BackboneOS representa un **ecosistema CRM completo** donde cada aplicación aporta valor específico:

### 🔄 Flujo de Valor Comercial

```
World (Ontología) → Entities (Clientes) → Products (Catálogo) → Offers (Comercialización) → Interactions (Journey)
```

- **World App**: Define el **vocabulario empresarial** para segmentación precisa
- **Entities App**: Gestiona **personas y organizaciones** con perfilado semántico
- **Products App**: Estructura el **catálogo de valor** organizacional
- **Offers App**: Transforma productos en **ofertas comerciales** con pricing dinámico
- **Interactions App**: Registra y optimiza el **customer journey** completo
- **Our Institution App**: Proporciona **contexto organizacional** para todas las operaciones

### 💡 Ventaja Competitiva

La integración semántica entre todas las apps permite:

- **Segmentación Inteligente**: Ofertas dirigidas por industria, función, y perfil semántico
- **Pricing Contextual**: Precios específicos por canal, geografía y audiencia
- **Analytics Integrados**: Insights de performance desde producto hasta conversión
- **Customer Journey Completo**: Tracking desde awareness hasta advocacy
- **Escalabilidad Empresarial**: Arquitectura preparada para crecimiento masivo

## ⚠️ Configuración de Desarrollo Híbrida

**IMPORTANTE**: BackboneOS utiliza una arquitectura híbrida donde el backend y la base de datos están containerizados, pero el frontend se ejecuta localmente para optimizar el desarrollo.

### URLs de Acceso

- **Frontend**: http://localhost:3000 (Nuxt.js local)
- **Backend API**: http://localhost:8000/api/ (Docker)
- **Django Admin**: http://localhost:8000/admin (Docker)

## 🛠️ Stack Tecnológico

### Backend (Django)

- **Framework**: Django 5.x
- **API**: Django REST Framework
- **Base de Datos**: PostgreSQL 14 (Docker)
- **Caché**: Redis 7 con django-redis para optimización de rendimiento
- **Sesiones**: Redis como backend de sesiones con fallback a base de datos
- **Configuración**: python-decouple para variables de entorno
- **Autenticación**: JWT + Token-based (implementado)
- **CORS**: django-cors-headers configurado

### Frontend (Nuxt.js)

- **Framework**: Nuxt.js 3.17.4
- **Lenguaje**: TypeScript 5.8.3
- **UI Framework**: Nuxt UI 3.1.3
- **Módulos**: @nuxt/content, @nuxt/fonts, @nuxt/icon, @nuxt/image, @nuxt/scripts, @nuxt/test-utils
- **Autenticación**: ✅ Sistema completo implementado
- **HTTP Client**: API service con $fetch
- **Linting**: ESLint 9.27.0

## 🔄 Arquitectura de Comunicación

### Flujo de Datos Backend ↔ Frontend

```
Frontend (Nuxt.js) ←→ API REST (Django) ←→ PostgreSQL
     │                    │                   │
   Localhost:3000    Docker:8000/api    Docker:5432
                          │
                       Redis:6379
                    (Caché y Sesiones)
```

### Separación de Responsabilidades

**Backend (Django)** 🎯

- **Lógica de Negocio**: Reglas empresariales y validaciones
- **API REST**: Endpoints estructurados con filtrado avanzado
- **Gestión de Datos**: ORM, migraciones, consultas optimizadas
- **Autenticación**: JWT tokens y middleware de seguridad
- **Admin Interface**: Gestión administrativa completa

**Frontend (Nuxt.js)** 🖥️

- **Interfaz de Usuario**: Componentes Vue.js reactivos
- **Experiencia de Usuario**: Navegación fluida y responsive
- **Estado de Cliente**: Gestión de estado con composables
- **Consumo de API**: Servicios HTTP para comunicación con backend
- **Autenticación Cliente**: Manejo de tokens y sesiones

### Comunicación API-First

El proyecto está diseñado con **arquitectura API-First**:

1. **Backend expone API REST** completa e independiente
2. **Frontend consume API** de manera desacoplada
3. **Documentación API** permite múltiples clientes futuros
4. **Testing independiente** de cada capa
5. **Escalabilidad horizontal** de cada componente

## 🌐 Configuración de Desarrollo

### Ambiente Híbrido Justificado

**¿Por qué Frontend local + Backend containerizado?**

**Ventajas del Frontend Local:**

- ⚡ **Hot Reload Instantáneo**: Cambios inmediatos sin rebuild
- 🛠️ **DevTools Optimizados**: Mejor debugging y desarrollo
- 📦 **Gestión de Dependencias**: npm/pnpm directo sin overhead
- 🔄 **Desarrollo Iterativo**: Ciclo de desarrollo más rápido

**Ventajas del Backend Containerizado:**

- 🔒 **Ambiente Consistente**: PostgreSQL y Django idénticos en todos los ambientes
- 🚀 **Deploy Fácil**: Imagen Docker lista para producción
- 🔧 **Dependencias Aisladas**: Sin conflictos de Python/pip locales
- 📊 **Datos Persistentes**: Base de datos compartida entre desarrolladores
