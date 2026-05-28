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
│   ├── offers/                # ✅ Sistema de Ofertas Comerciales (COMPLETA)
│   │   ├── models.py          # ProductOffering con segmentación semántica avanzada
│   │   ├── views.py           # ViewSets con analytics empresariales y filtros avanzados
│   │   ├── serializers.py     # Serializers contextuales para ofertas comerciales
│   │   ├── admin.py           # Interface administrativa con acciones en lote
│   │   ├── urls.py            # 10 API endpoints con analytics y duplicación
│   │   ├── migrations/        # Migraciones con índices optimizados
│   │   ├── COMPLETION_REPORT.md  # Reporte de implementación completa
│   │   └── README.md          # Documentación técnica completa
│   ├── campaigns/             # ✅ Campañas Comerciales (COMPLETA) + CRM HTML
│   │   ├── models.py          # Campaign, CampaignTouchpoint con targeting semántico
│   │   ├── selectors.py       # Lecturas compartidas (hub, detalle, analytics)
│   │   ├── services.py        # Escrituras compartidas (CRUD, duplicate, validate_*)
│   │   ├── serializers.py     # DRF (sin lógica de escritura)
│   │   ├── views.py           # ViewSets DRF (delegan en selectors/services)
│   │   ├── forms.py           # Formularios del CRM
│   │   ├── template_views.py  # Vistas HTML del CRM
│   │   ├── template_urls.py   # URLconf HTML (namespace campaigns_html)
│   │   └── templates/campaigns/  # Plantillas que extienden base_dashboard.html
│   └── dashboard/             # ✅ Home del CRM y layout compartido
│       ├── selectors.py       # get_home_context()
│       └── template_views.py  # Vista home
│
│   # Las apps products, entities, interactions y offers siguen el mismo patrón
│   # de módulos: selectors.py · services.py · forms.py · template_views.py ·
│   # template_urls.py · templates/<app>/ · tests_template_views.py · test_factories.py
│
├── backend/templates/         # Plantillas raíz compartidas del CRM
│   ├── base_dashboard.html    # Layout base (extends por todas las páginas)
│   ├── dashboard/home.html    # Home del CRM
│   ├── includes/              # header.html, sidebar.html
│   └── registration/login.html# Login de sesión
├── backend/static/            # src/input.css (fuente Tailwind) → dist/styles.css (build, gitignored)
├── backend/package.json       # Toolchain Tailwind (tailwind:build / tailwind:watch)
├── backend/tailwind.config.js # Configuración de Tailwind
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
├── docker-compose.yml        # Backend + PostgreSQL + Redis + Celery (single-process backend)
├── .env                      # Variables de entorno
└── README.md                 # README principal (punto de entrada)
```

> El paquete Next.js `frontend/` se eliminó en la Fase 6 de la [consolidación del frontend](consolidation/FRONTEND_CONSOLIDATION.md). El CRM de operador se sirve ahora como plantillas Django desde el propio backend.

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
- **campaigns/README.md**: Documentación del sistema de campañas comerciales
- **docs/consolidation/FRONTEND_CONSOLIDATION.md**: Handoff de la migración del CRM a plantillas Django
- **docs/reports/SECURITY_AUDIT_REPORT.md**: Reporte de auditoría de seguridad
