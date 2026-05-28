# Estructura del Proyecto - BackboneOS

## 📁 Estructura Completa

```
BackboneOS/
├── backend/                    # Backend Django
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── backend/               # Configuración Django
│   │   ├── settings.py        # python-decouple, CORS
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── users/                 # App de usuarios y autenticación
│   │   ├── models.py          # ExampleModel implementado
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── serializers.py
│   ├── entities/              # ✅ Sistema de Gestión de Entidades (COMPLETA)
│   │   ├── models.py          # Person, Organization, ContactDetail, IndividualProfile
│   │   ├── views.py           # ViewSets con perfilado semántico
│   │   ├── serializers.py     # Serializers optimizados para CRM
│   │   ├── admin.py           # Interface administrativa completa
│   │   ├── urls.py            # API endpoints de entidades
│   │   ├── migrations/        # Migraciones con índices estratégicos
│   │   ├── INDEX_OPTIMIZATION.md  # Documentación de performance
│   │   └── README.md          # Documentación completa de la app
│   ├── our_institution/       # ✅ Sistema de Estructura Organizacional (COMPLETA)
│   │   ├── models.py          # OurOrganization, Division, Unit, Position, Team, Seat
│   │   ├── views.py           # ViewSets con jerarquía organizacional optimizada
│   │   ├── serializers.py     # Serializers con información contextual
│   │   ├── admin.py           # Interface administrativa para estructura organizacional
│   │   ├── urls.py            # API endpoints de estructura organizacional
│   │   ├── tests.py           # Tests unitarios completos (14 tests exitosos)
│   │   ├── migrations/        # Migraciones con constraints e índices
│   │   ├── management/        # Comandos de gestión automatizada
│   │   ├── COMPLETION_REPORT.md  # Reporte de implementación completa
│   │   └── README.md          # Documentación técnica completa
│   ├── world/                 # ✅ Campo Semántico Empresarial (COMPLETA)
│   │   ├── models.py          # 15+ modelos de ontología empresarial
│   │   ├── views.py           # ViewSets con filtrado/búsqueda semántica
│   │   ├── serializers.py     # Serializers completos + choice
│   │   ├── admin.py           # Interface administrativa optimizada
│   │   ├── urls.py            # API endpoints estructurados
│   │   ├── migrations/        # Migraciones con índices optimizados
│   │   └── INDEX_OPTIMIZATION.md  # Documentación de performance
│   ├── products/              # ✅ Sistema de Gestión de Productos (COMPLETA)
│   │   ├── models.py          # Division, ProductCategory, Product, Modality
│   │   ├── views.py           # ViewSets con filtrado/búsqueda avanzada
│   │   ├── serializers.py     # Serializers optimizados (list/detail/create)
│   │   ├── admin.py           # Interface administrativa con optimizaciones
│   │   ├── urls.py            # API endpoints + analytics
│   │   ├── analytics.py       # Dashboard y analytics comerciales
│   │   ├── migrations/        # Migraciones con constraints e índices
│   │   └── tests.py           # Tests unitarios
│   ├── interactions/          # ✅ Sistema de Interacciones (COMPLETA)
│   │   ├── models.py          # Medium, Channel, Agent, Session, Touchpoint, Interaction
│   │   ├── views.py           # ViewSets con analytics y framework JTBD
│   │   ├── serializers.py     # Serializers contextuales para customer journey
│   │   ├── admin.py           # Interface administrativa optimizada
│   │   ├── urls.py            # 27 API endpoints funcionales
│   │   ├── migrations/        # Migraciones con índices para performance
│   │   └── README.md          # Documentación completa del sistema
│   └── offers/                # ✅ Sistema de Ofertas Comerciales (COMPLETA)
│       ├── models.py          # ProductOffering con segmentación semántica avanzada
│       ├── views.py           # ViewSets con analytics empresariales y filtros avanzados
│       ├── serializers.py     # Serializers contextuales para ofertas comerciales
│       ├── admin.py           # Interface administrativa con acciones en lote
│       ├── urls.py            # 10 API endpoints con analytics y duplicación
│       ├── migrations/        # Migraciones con índices optimizados
│       ├── COMPLETION_REPORT.md  # Reporte de implementación completa
│       └── README.md          # Documentación técnica completa
├── backend/templates/         # Operator CRM (Django HTML; Next.js removed Phase 6)
│   ├── composables/
│   │   └── useAuth.ts        # ✅ Sistema auth JWT completo
│   ├── src/
│   │   ├── components/
│   │   │   └── UserList.vue
│   │   └── services/
│   │       ├── api.ts        # ✅ API service centralizado
│   │       └── userService.ts
│   ├── pages/
│   │   ├── index.vue
│   │   ├── login.vue         # ✅ Autenticación implementada
│   │   ├── analytics/        # Páginas de analytics
│   │   ├── customers/        # Gestión de clientes
│   │   ├── leads/           # Gestión de leads
│   │   ├── products/        # Gestión de productos
│   │   └── reports/         # Reportes y dashboards
│   ├── middleware/
│   │   └── auth.ts           # ✅ Middleware de autenticación
│   ├── plugins/
│   │   └── auth.client.ts    # ✅ Plugin cliente
│   ├── nuxt.config.ts        # ✅ Configuración completa
│   └── package.json          # ✅ Nuxt 3.17.4 + TypeScript 5.8.3
├── docs/                     # 📚 Documentación modular
│   ├── README.md             # Índice por categoría
│   ├── ai/                   # Guías para asistentes IA
│   ├── operations/           # Docker, deployment, comandos
│   ├── reports/              # Auditorías y reportes
│   ├── tracking/             # Historial de implementación tracking
│   ├── ARCHITECTURE.md       # Arquitectura del sistema
│   ├── APPS.md              # Documentación de aplicaciones Django
│   ├── API.md               # Referencia de API
│   ├── USE_CASES.md         # Casos de uso del sistema
│   ├── PROJECT_STATUS.md    # Estado del proyecto
│   └── PROJECT_STRUCTURE.md # Este archivo
├── docker-compose.yml        # ⚠️ Frontend ejecuta localmente
├── .env                      # Variables de entorno
└── README.md                 # README principal (punto de entrada)
```

## 📚 Documentación Adicional

- **docs/ai/CLAUDE.md**: Guía técnica completa del proyecto
- **docs/operations/COMMANDS.md**: Lista de comandos de desarrollo
- **docs/operations/DEPLOYMENT.md**: Guía de deployment y producción
- **world/INDEX_OPTIMIZATION.md**: Optimización de consultas semánticas
- **entities/INDEX_OPTIMIZATION.md**: Optimización de performance para entidades
- **our_institution/README.md**: Documentación completa del sistema organizacional
- **our_institution/COMPLETION_REPORT.md**: Reporte de implementación y tests
- **products/README.md**: Documentación del sistema de productos
- **interactions/README.md**: Documentación del framework de interacciones
- **offers/README.md**: Documentación del sistema de ofertas comerciales
- **offers/COMPLETION_REPORT.md**: Reporte de implementación completa y funcionalidades
- **docs/reports/SECURITY_AUDIT_REPORT.md**: Reporte de auditoría de seguridad
