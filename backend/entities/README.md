# BackboneOS: Aplicación `entities`

## 🌟 Propósito

La aplicación `entities` contiene los modelos base que representan **personas naturales** y **organizaciones**, concebidas como entidades del mundo real, no como clientes, usuarios o cuentas.

Este enfoque busca preservar una perspectiva **humanista**, enfocada en las identidades en sí mismas, antes de considerar su participación en ciclos de vida comerciales.

---

## 📁 Contenido

### 👩 `Person`

Representa una persona natural. Incluye:

- Nombres y apellidos
- Fecha de nacimiento
- Género y estado civil
- Nacionalidad
- Documento de identidad
- Fotografía opcional

### 📢 `ContactDetail`

Medios de contacto vinculados a una persona. Permite:

- Múltiples emails o teléfonos
- Marcar uno como principal
- Indicar verificación

### 🏫 `IndividualProfile`

Perfil semántico de la persona. Incluye:

- Industrias, funciones y habilidades relacionadas
- Nivel académico
- Preferencias de contacto y consentimiento

---

### 🏢 `Organization`

Representa una entidad jurídica u organización. Contempla:

- Nombre comercial y razón social
- Tipo, industria y país
- Documento legal

### 📍 `PhysicalAddress`

Direcciones físicas, asociables tanto a personas como organizaciones. Soporta:

- Varias direcciones por entidad
- Marcado de principal y uso para facturación

---

## 🔄 Relación con otras apps

Esta app **no maneja cuentas de usuario ni roles de acceso**, lo cual se tratará en una capa distinta. La evolución de estas entidades como clientes también se definirá en otro espacio.

La app `entities` se conecta con modelos semánticos definidos en la app `world`, como:

- `Country`
- `Industry`
- `FunctionOrResponsibility`
- `Skill`
- `AcademicDegree`

---

## 📊 Ventajas

- Evita ambigüedades con sistemas de autenticación (`accounts`, `users`, etc.)
- Escalable hacia una representación rica de identidades
- Alineado con un diseño centrado en personas

---

## 📚 Futuras extensiones sugeridas

- Agregar verificación documental o facial
- Relacionar con eventos o interacciones
- Enlazar con "clientes" u "oportunidades" en apps de ciclo de vida

---

## 🔗 Recomendado para

Cualquier módulo que necesite referenciar a una persona o una organización sin suponer que son usuarios, cuentas, clientes o leads activos.
