# V.I.D.A.

**Vortexbird Intelligent Documentation Assistant**

Plataforma web que apoya a los Requirements Owners (RO) de VortexBird en sus tareas recurrentes. Su primer módulo genera la documentación técnica que se entrega a las fábricas de desarrollo:

- El **administrador** define los tipos de documentación y carga su formato (Word o Excel).
- El **RO** elige el tipo de documentación y carga la información de la actividad, con archivos adjuntos o texto.
- El sistema **analiza** la información, **pregunta** lo que falta y el RO responde o lo deja **pendiente**.
- El sistema **genera** el documento en el formato definido, con los pendientes marcados.

A futuro, la plataforma sumará otros módulos para los RO, como pruebas de carga y análisis de comportamiento de APIs.

## Cómo trabajamos: Spec Driven Development (Spec-First)

```
Constitución → Especificación → Planificación → Tareas → Implementación
```

| Fase | Pregunta que responde | Archivo |
|---|---|---|
| Constitución | ¿Qué principios no se negocian? | `sdd/constitucion.md` (una para todo el proyecto) |
| Especificación | ¿Qué necesitamos y por qué? | `specs/NNN-nombre/spec.md` |
| Planificación | ¿Cómo lo vamos a construir? | `specs/NNN-nombre/plan.md` |
| Tareas | ¿En qué pasos verificables? | `specs/NNN-nombre/tareas.md` |
| Implementación | Construcción tarea por tarea | Código y commits en la rama |

Avanzamos **una funcionalidad a la vez**: no empieza la siguiente hasta que la anterior se integra en `main`.

**Herramientas**
- **Desarrollo:** Claude Code, con los comandos `/sdd-*` de `.claude/commands/`.
- **Modelos en ejecución:** LiteLLM → Vorkan Gateway, con el modelo configurable por tarea.

## Levantar la plataforma

Necesitas **Docker**, **Python 3.12 o superior** y **Node.js 20 o superior**.

### 1. Clonar y configurar

```bash
git clone https://github.com/dmoreno-d10a/VIDA.git
cd vida
cp .env.ejemplo .env
```

Abre `.env` y cambia `VIDA_BD_CONTRASENA` por una contraseña local, y ponla
también dentro de `VIDA_BD_URL`. Las dos tienen que coincidir. `.env` no se
versiona nunca: ahí van las credenciales (Art. X.2 de la constitución).

El archivo trae comentada cada variable. Las que no tienen valor por defecto
hacen fallar el arranque si faltan, en vez de asumir algo.

### 2. Base de datos

```bash
docker compose up -d
```

Levanta PostgreSQL en el puerto `55432` (no el 5432, para no competir con
otros PostgreSQL de tu máquina). Si cambias `VIDA_BD_CONTRASENA` **después**
de la primera vez, la base conserva la anterior: sincronízala con
`alter user vida with password '…'` o recrea el volumen con
`docker compose down -v`.

### 3. Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"   # Linux o macOS: .venv/bin/python
.venv/Scripts/python -m alembic upgrade head      # crea las tablas
```

### 4. El primer Administrador

Solo un Administrador puede crear usuarios, así que el primero se crea por
comando. Define `VIDA_ADMIN_INICIAL` en tu `.env` y ejecuta:

```bash
.venv/Scripts/python -m scripts.crear_admin
```

Si no defines `VIDA_ADMIN_INICIAL_CONTRASENA`, el comando la pide por consola
sin mostrarla. La contraseña debe cumplir la política: mínimo 12 caracteres,
que no sea de uso común y que no contenga tu identificación. Ejecutarlo dos
veces no crea un duplicado.

### 5. Arrancar

En dos terminales:

```bash
cd backend && .venv/Scripts/python -m uvicorn app.main:app --port 8000
cd frontend && npm install && npm run dev
```

Abre **http://127.0.0.1:3000** y entra con el Administrador inicial. Desde
**Administrar usuarios** creas a los RO del área.

### Pruebas

```bash
cd backend  && .venv/Scripts/python -m pytest          # 76 pruebas
cd frontend && npx playwright install chromium         # una sola vez
cd frontend && npx playwright test                     # visibilidad por rol
```

Las pruebas del backend usan una base aparte (`vida_pruebas`), que se crea
sola. Las de extremo a extremo necesitan el front y el backend arriba, y los
usuarios ficticios de `backend/tests/datos_ficticios.py` en la base.

## Trabajar en una funcionalidad nueva

```bash
claude
```

Dentro de Claude Code:

```
/sdd-especificar <descripción de la funcionalidad>
/sdd-aclarar
/sdd-planificar
/sdd-tareas
/sdd-implementar
```

## Estructura actual

```
vida/
├── CLAUDE.md              # Instrucciones permanentes para Claude Code
├── CONTRIBUTING.md        # Ramas, commits y Pull Requests
├── .env.ejemplo           # Plantilla de variables de entorno (sin secretos)
├── docker-compose.yml     # PostgreSQL para desarrollo
├── .claude/commands/      # Comandos /sdd-* del flujo
├── sdd/
│   ├── constitucion.md    # Principios no negociables (v1.0.0)
│   ├── mapa-funcionalidades.md  # Funcionalidades del módulo de documentación (v1.0)
│   └── plantillas/        # spec.md, plan.md, tareas.md
├── specs/                 # Una carpeta por especificación
├── backend/               # FastAPI: toda la lógica y las credenciales (Art. IV)
│   ├── app/
│   │   ├── modelos/       # usuario y sesión
│   │   ├── seguridad/     # contraseñas, sesiones y autorización
│   │   ├── esquemas/      # entradas y salidas de la API
│   │   └── rutas/         # acceso, usuarios y perfil
│   ├── alembic/           # Migraciones
│   ├── scripts/           # crear_admin.py
│   └── tests/             # pytest
├── frontend/              # Next.js: sin lógica de permisos ni credenciales
│   ├── app/               # Pantallas
│   ├── lib/api.ts         # Único punto de llamada al backend
│   └── e2e/               # Playwright
└── scripts/               # nueva-spec.sh
```

## Estado

- [x] Constitución v1.0.0
- [x] Mapa de funcionalidades
- [x] 001 — Acceso y roles
