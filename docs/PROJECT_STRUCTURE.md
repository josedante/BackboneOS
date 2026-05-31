# Estructura del Proyecto - BackboneOS

## Estructura principal

```
BackboneOS/
├── backend/
│   ├── README.md              # Punto de entrada (arranque, tests, apps)
│   ├── manage.py
│   ├── requirements.txt
│   ├── run_tests.sh
│   ├── run_tests_docker.sh
│   ├── backend/               # Proyecto Django (settings/, urls.py)
│   ├── core/                  # Comandos de gestión compartidos
│   ├── users/
│   ├── world/
│   ├── entities/
│   ├── our_institution/
│   ├── products/
│   ├── interactions/
│   ├── offers/
│   ├── campaigns/
│   ├── websites/
│   ├── connectors/
│   ├── dashboard/
│   ├── sales/                 # No en INSTALLED_APPS (planificado)
│   ├── templates/             # CRM (base_dashboard.html, registration/)
│   └── static/                # Tailwind → dist/styles.css
├── docs/
│   ├── README.md
│   ├── backend/               # websites.md, connectors.md, interactions.md
│   ├── tracking/README.md     # Guía canónica de tracking
│   ├── operations/
│   ├── ai/
│   └── ...
├── docker-compose.yml
└── README.md
```

> El paquete Next.js `frontend/` se eliminó en la Fase 6. Ver [consolidation/FRONTEND_CONSOLIDATION.md](consolidation/FRONTEND_CONSOLIDATION.md).

## Patrón de apps con CRM HTML

`products`, `entities`, `interactions`, `offers`, `campaigns` comparten:

- `selectors.py`, `services.py`, `forms.py`
- `template_views.py`, `template_urls.py`, `templates/<app>/`
- `tests.py`, `tests_template_views.py`, `test_factories.py` (donde aplique)

## Documentación

| Tema | Ubicación |
|------|-----------|
| Índice | [docs/README.md](README.md), [NAVIGATION.md](NAVIGATION.md) |
| Backend | [BACKEND.md](BACKEND.md), [backend/README.md](../backend/README.md) |
| Apps | [APPS.md](APPS.md) + `backend/<app>/README.md` |
| Tracking web | [backend/websites.md](backend/websites.md), [tracking/README.md](tracking/README.md) |
| Connectors | [backend/connectors.md](backend/connectors.md) |
| Índices DB | [DATABASE_INDEXES.md](DATABASE_INDEXES.md) |
| Tests | [TESTING.md](TESTING.md) |

## Referencias técnicas

- [docs/ai/CLAUDE.md](ai/CLAUDE.md)
- [docs/operations/COMMANDS.md](operations/COMMANDS.md)
- [docs/operations/DEPLOYMENT.md](operations/DEPLOYMENT.md)
- [docs/reports/SECURITY_AUDIT_REPORT.md](reports/SECURITY_AUDIT_REPORT.md)
