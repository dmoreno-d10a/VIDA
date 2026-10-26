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

## Inicio rápido

```bash
git clone <URL-DEL-REPO>        # PENDIENTE: URL del repositorio
cd vida
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
├── .claude/commands/      # Comandos /sdd-* del flujo
├── sdd/
│   ├── constitucion.md    # Principios no negociables (v1.0.0)
│   └── plantillas/        # spec.md, plan.md, tareas.md
├── specs/                 # Una carpeta por especificación
└── scripts/               # nueva-spec.sh
```

## Estado

- [x] Constitución v1.0.0
- [ ] Mapa de funcionalidades
- [ ] Primera especificación
