# App Our Institution

## 🎯 Propósito

La aplicación `our_institution` representa a la organización propietaria de la instancia actual del sistema BackboneOS. Está diseñada para centralizar la identidad institucional, su estructura organizativa, sedes y equipos de trabajo.

---

## 🏗️ Modelos Incluidos

### `OurOrganization`
- Identidad principal de la institución dueña del sistema.
- Permite solo una instancia activa a la vez.
- Campos: nombre, nombre legal, RUC, país, sector, tipo de organización, contacto, sitio web, logo.

### `Seat`
- Sedes físicas de la organización (sede central, oficina, sucursal, local).
- Relacionadas directamente con `OurOrganization`.

### `Unit`
- Unidades organizativas internas.
- Soporte jerárquico con `parent`.

### `Position`
- Cargos dentro de una `Unit`.
- Sirve para mapear estructura funcional.

### `Team`
- Equipos transversales o estructurales dentro de la institución.

---

## ⚙️ Administración

Todos los modelos están registrados en el panel de administración de Django con listas, filtros y campos de búsqueda relevantes.

---

## 🔌 API REST

ViewSets disponibles para todos los modelos con rutas automáticas a través de `DefaultRouter`. Endpoints típicos:

```
GET /api/our-institution/organization/
GET /api/our-institution/seats/
GET /api/our-institution/units/
GET /api/our-institution/positions/
GET /api/our-institution/teams/
```

---

## 🧪 Pruebas

Archivo `tests.py` incluido con pruebas unitarias básicas para validar:
- Unicidad de `OurOrganization` activa
- Relación entre sedes y organización
- Jerarquía de unidades
- Asignación de cargos
- Creación de equipos

Ejecutar pruebas con:

```bash
python manage.py test our_institution
```

---

## 🧱 Datos Iniciales

Fixture disponible:

```bash
python manage.py loaddata our_institution/initial_ourorganization.json
```

---

## 📁 Estructura

```
our_institution/
├── admin.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
├── tests.py
└── initial_ourorganization.json
```

---

## 🔒 Notas

- Solo debe existir una instancia activa de `OurOrganization`.
- Los códigos de `Seat` y `Team` deben ser únicos.
- Preparada para extender con board members, valores institucionales u objetivos estratégicos.

---

© BackboneOS – Propiedad de la instancia garantizada.
