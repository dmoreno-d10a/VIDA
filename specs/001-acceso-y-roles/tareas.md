# Tareas: Acceso y roles

**Spec:** [`spec.md`](./spec.md) · **Plan:** [`plan.md`](./plan.md)
**Rama:** `feature/001-acceso-y-roles`

> Reglas:
> - Cada tarea es pequeña, verificable y tiene un criterio de terminado.
> - `[P]` indica que la tarea puede hacerse en paralelo con otras `[P]` de la misma fase.
> - Se marca `[x]` solo cuando el criterio de terminado se cumple.
> - Un commit por tarea, con el ID en el mensaje: `T003: descripción`.

---

## Fase 1 — Preparación

- [x] **T001** Crear la base del repositorio para desarrollo: `.gitignore` (ignora `.env`, artefactos de build y dependencias), `.env.ejemplo` con las diez variables del plan y sin ningún secreto real, y `docker-compose.yml` con PostgreSQL para desarrollo.
  - Terminado cuando: `docker compose up` levanta PostgreSQL, `git status` no muestra `.env` como archivo nuevo, y `.env.ejemplo` está versionado con valores de ejemplo.
  - Cubre: RF-10, Art. X.2

- [x] **T002** [P] Crear el esqueleto del backend: `backend/pyproject.toml` con las dependencias (FastAPI, SQLAlchemy, Alembic, Pydantic, argon2-cffi, pytest) y `backend/app/main.py` que arranque y responda en una ruta de salud.
  - Terminado cuando: el backend arranca localmente y responde a esa ruta.
  - Cubre: Art. IV

- [x] **T003** [P] Crear el esqueleto del front: `frontend/package.json`, `frontend/app/layout.tsx` con el idioma del documento en español y una página mínima.
  - Terminado cuando: el front arranca localmente, muestra esa página y el documento declara `lang="es"`.
  - Cubre: Art. XII

- [ ] **T004** Implementar `backend/app/configuracion.py`: lee del entorno los diez parámetros del plan, con los valores por defecto definidos, y **falla al arrancar** si falta alguno de los que no tienen valor por defecto.
  - Terminado cuando: arrancar sin `VIDA_BD_URL` falla con un mensaje claro en español, y cambiar `VIDA_SESION_MINUTOS` o `VIDA_CONTRASENA_MIN` por entorno cambia el valor leído, sin tocar código.
  - Cubre: RF-07, RF-20, RF-22, RF-23

- [ ] **T005** Implementar `backend/app/bd.py` (conexión y sesión de base de datos) e inicializar Alembic con `alembic.ini` y su entorno.
  - Terminado cuando: `alembic current` responde contra la base de datos de desarrollo sin error.
  - Cubre: RF-10

- [ ] **T006** [P] Incorporar `backend/app/datos/contrasenas-comunes.txt` con una lista pública de contraseñas de uso común, y dejar su ruta configurable.
  - Terminado cuando: el archivo existe, está versionado, contiene solo contraseñas públicas de uso común —ningún dato de persona ni de cliente— y la ruta se lee de `VIDA_CONTRASENAS_COMUNES`.
  - Cubre: RF-20, Art. X.3

## Fase 2 — Casos de prueba primero

> Las pruebas de esta fase se escriben **antes** de construir y deben fallar al terminar la fase. Todos los usuarios son ficticios (Art. X.3).

- [ ] **T007** Definir los usuarios ficticios de prueba en `backend/tests/datos_ficticios.py`: un RO activo, un Administrador activo, un segundo Administrador, un usuario autenticado sin rol y un usuario con el acceso revocado.
  - Terminado cuando: los cinco usuarios están definidos, ninguno corresponde a una persona real, y cubren los cinco casos de acceso de la sección 8 de la spec.
  - Cubre: Art. VIII, Art. X.3

- [ ] **T008** [P] Escribir `backend/tests/test_acceso.py` con la respuesta esperada de: entrar con credenciales correctas, entrar con credenciales incorrectas, entrar sin rol asignado, entrar con acceso revocado, cerrar sesión, sesión vencida, y bloqueo tras los intentos fallidos configurados.
  - Terminado cuando: las pruebas existen, fallan, y la respuesta esperada de todos los casos negativos es **idéntica** entre sí (no permite distinguir si el usuario existe, si está bloqueado ni qué dato falló).
  - Cubre: HU-1, HU-3, RF-09, RF-22

- [ ] **T009** [P] Escribir `backend/tests/test_autorizacion.py` con la respuesta esperada de: petición sin sesión, petición con sesión válida, y petición de un RO a cada ruta de administración, incluido el acceso directo sin pasar por el menú.
  - Terminado cuando: las pruebas existen, fallan, y la respuesta esperada para el RO sobre rutas de administración no incluye ningún dato de usuarios.
  - Cubre: HU-2, RF-01, RF-04, RF-05, RF-06

- [ ] **T010** [P] Escribir `backend/tests/test_usuarios.py` con la respuesta esperada de las seis acciones de administración: listar, crear (incluida identificación repetida), cambiar rol, restablecer contraseña, revocar, eliminar, y el intento de dejar la plataforma sin Administrador activo —que debe fallar siempre, incluso sobre la propia cuenta—.
  - Terminado cuando: las pruebas existen y fallan, con un caso por cada acción y uno por cada forma de quedarse sin Administrador (revocar, eliminar y cambiar de rol al último).
  - Cubre: HU-5, RF-11, RF-12, RF-13, RF-14, RF-15, RF-16

- [ ] **T011** [P] Escribir `backend/tests/test_contrasenas.py` con la respuesta esperada de la política en los tres puntos donde se fija una contraseña (creación por el Administrador, cambio por el usuario, restablecimiento): longitud mínima y máxima, sin composición obligatoria, rechazo de contraseñas comunes y de las que contienen la identificación, rechazo de la anterior, cambio sin acertar la actual, y ausencia de vencimiento por tiempo.
  - Terminado cuando: las pruebas existen, fallan, incluyen un caso que verifica que ninguna respuesta ni registro devuelve la contraseña, y un caso que cambia los límites por configuración y comprueba que la validación los sigue.
  - Cubre: HU-6, RF-17, RF-19, RF-20, RF-21, RF-23

- [ ] **T012** [P] Escribir `frontend/e2e/visibilidad-por-rol.spec.ts` con lo esperado en pantalla: el RO ve sus opciones y no la administración de usuarios; el Administrador ve ambas; ambos ven su identificación y su rol; sin sesión no se renderiza ninguna pantalla privada.
  - Terminado cuando: la prueba existe y falla.
  - Cubre: HU-2, HU-4, RF-04, RF-08

## Fase 3 — Construcción

- [ ] **T013** Implementar `backend/app/modelos/usuario.py`: identificación única, rol (`RO` / `ADMINISTRADOR`), hash de contraseña, estado del acceso, contador de intentos fallidos, bloqueo vigente y fechas de creación y actualización.
  - Terminado cuando: el modelo existe, solo admite los dos roles, y no tiene ningún campo que guarde la contraseña en forma legible.
  - Cubre: RF-02, RF-03, RF-10, RF-19

- [ ] **T014** Implementar `backend/app/modelos/sesion.py`: identificador opaco, usuario, creación y expiración.
  - Terminado cuando: el modelo existe y permite borrar todas las sesiones de un usuario en una operación.
  - Cubre: RF-07, RF-15

- [ ] **T015** Crear la migración inicial de Alembic con las tablas de usuario y sesión.
  - Terminado cuando: `alembic upgrade head` crea el esquema desde cero sobre una base vacía, y `alembic downgrade` lo revierte.
  - Cubre: RF-10

- [ ] **T016** Implementar `backend/app/seguridad/contrasena.py`: hash y verificación con Argon2id, y validación de la política vigente leída de configuración.
  - Terminado cuando: pasan las pruebas de T011 que no dependen de rutas, y el hash de una misma contraseña es distinto en dos cálculos.
  - Cubre: RF-19, RF-20, RF-23

- [ ] **T017** Implementar `backend/app/seguridad/sesiones.py`: crear, validar y terminar sesiones, aplicando la expiración configurada y rechazando las de usuarios revocados o eliminados.
  - Terminado cuando: pasan los casos de sesión vencida y de acceso revocado de T008.
  - Cubre: RF-01, RF-07, RF-15

- [ ] **T018** Implementar `backend/app/seguridad/autorizacion.py`: dependencia que resuelve el usuario y su rol vigente en cada petición y exige el rol requerido, negando sin devolver datos.
  - Terminado cuando: pasan las pruebas de T009, y el rol se lee de la base de datos en cada petición (cambiarlo aplica de inmediato sobre una sesión abierta).
  - Cubre: RF-01, RF-03, RF-05, RF-06

- [ ] **T019** [P] Implementar los esquemas de entrada y salida en `backend/app/esquemas/acceso.py` y `backend/app/esquemas/usuarios.py`.
  - Terminado cuando: ningún esquema de salida contiene un campo de contraseña.
  - Cubre: RF-08, RF-11, RF-19

- [ ] **T020** Implementar `backend/app/rutas/acceso.py`: entrar, cerrar sesión y consultar la sesión actual con identificación y rol vigente, con la misma respuesta para todos los casos negativos.
  - Terminado cuando: pasan los casos de T008 salvo el de bloqueo, y los mensajes de los casos negativos son indistinguibles entre sí.
  - Cubre: HU-1, HU-3, HU-4, RF-01, RF-08, RF-09

- [ ] **T021** Agregar al acceso el conteo de intentos fallidos y el bloqueo temporal con los valores de configuración, que se levanta por tiempo sin intervención del Administrador.
  - Terminado cuando: pasa el caso de bloqueo de T008, el bloqueo se levanta solo al pasar el tiempo configurado, y cambiar `VIDA_INTENTOS_MAX` cambia el comportamiento sin tocar código.
  - Cubre: RF-22, RF-23

- [ ] **T022** Implementar en `backend/app/rutas/usuarios.py` el listado y la creación de usuarios, solo para el rol Administrador, rechazando identificaciones repetidas y aplicando la política a la contraseña inicial.
  - Terminado cuando: pasan los casos de listar y crear de T010, y el listado muestra identificación, rol y estado del acceso, sin contraseñas.
  - Cubre: HU-5, RF-11, RF-12, RF-20

- [ ] **T023** Agregar a `backend/app/rutas/usuarios.py` el cambio de rol, el restablecimiento de contraseña y la revocación y eliminación del acceso, terminando las sesiones abiertas del usuario afectado.
  - Terminado cuando: pasan esos casos de T010, la contraseña anterior deja de servir tras un restablecimiento, y un usuario revocado o eliminado no puede seguir usando una sesión ya abierta.
  - Cubre: RF-13, RF-14, RF-15

- [ ] **T024** Implementar la regla que impide dejar la plataforma sin ningún Administrador activo, en las tres acciones que podrían causarlo y también cuando el Administrador las ejecuta sobre su propia cuenta.
  - Terminado cuando: pasan los tres casos de T010 correspondientes, cada uno con un mensaje en español que explica el motivo.
  - Cubre: RF-16

- [ ] **T025** Implementar `backend/app/rutas/perfil.py`: cambio de la propia contraseña acreditando la actual, sin obligación de cambiarla y sin vencimiento por tiempo.
  - Terminado cuando: pasan los casos de T011 que dependen de rutas, y un usuario que nunca cambia su contraseña inicial sigue entrando sin interrupción.
  - Cubre: HU-6, RF-17, RF-21

- [ ] **T026** Implementar `backend/scripts/crear_admin.py`: crea el Administrador inicial tomando la contraseña del entorno o pidiéndola por consola sin mostrarla, y no hace nada si ya existe un Administrador activo.
  - Terminado cuando: sobre una base vacía el comando crea un Administrador que puede entrar; la contraseña no aparece en el código, en el repositorio ni en la salida del comando; y ejecutarlo dos veces no crea un duplicado.
  - Cubre: RF-18, Art. X.2

- [ ] **T027** Implementar `frontend/lib/api.ts` (único punto de llamada al backend, con la cookie de sesión) y `frontend/middleware.ts`, que redirige a la pantalla de acceso cualquier ruta privada sin cookie, sin renderizar nada.
  - Terminado cuando: abrir una ruta privada sin sesión no muestra ningún dato ni esqueleto de la plataforma, y `api.ts` no contiene ninguna decisión de permisos.
  - Cubre: RF-01, HU-3, Art. IV

- [ ] **T028** [P] Implementar `frontend/app/acceso/page.tsx`: identificación y mensajes de acceso negado, en español y sin revelar detalles.
  - Terminado cuando: credenciales incorrectas, usuario inexistente, usuario sin rol, revocado y bloqueado muestran el mismo mensaje en pantalla.
  - Cubre: HU-1, RF-09

- [ ] **T029** Implementar `frontend/app/(privado)/layout.tsx`: consulta la sesión actual, muestra identificación y rol vigente, y arma el menú solo con las opciones del rol.
  - Terminado cuando: el menú del RO no contiene la administración de usuarios, el del Administrador sí, y ambos muestran identificación y rol en cualquier pantalla.
  - Cubre: HU-2, HU-4, RF-04, RF-08

- [ ] **T030** [P] Implementar `frontend/app/(privado)/inicio/page.tsx` con las opciones del rol del usuario y la opción de cerrar sesión.
  - Terminado cuando: tras identificarse, cada rol llega a esta pantalla y ve solo sus opciones; cerrar sesión obliga a identificarse de nuevo.
  - Cubre: HU-1, HU-2

- [ ] **T031** Implementar `frontend/app/(privado)/administracion/usuarios/page.tsx` con el listado y las seis acciones, incluida la advertencia cuando una acción dejaría la plataforma sin Administrador.
  - Terminado cuando: un Administrador completa las seis acciones desde la pantalla, y la que dejaría la plataforma sin Administrador se informa sin ejecutarse.
  - Cubre: HU-5, RF-11 a RF-16

- [ ] **T032** [P] Implementar `frontend/app/(privado)/perfil/contrasena/page.tsx` para el cambio de la propia contraseña, informando la regla incumplida cuando corresponda.
  - Terminado cuando: un usuario cambia su contraseña desde la pantalla, y una contraseña que incumple la política se rechaza indicando qué regla falló.
  - Cubre: HU-6, RF-17, RF-20

## Fase 4 — Validación

- [ ] **T033** Ejecutar el caso de referencia y registrar el puntaje: recorrido completo del **RO** (entra, ve solo sus opciones, cambia su contraseña, no alcanza la administración ni por menú ni por acceso directo).
  - Terminado cuando: el recorrido pasa completo y queda registrado en `tareas.md` cuántos de sus criterios de aceptación se cumplieron, sobre el total.
  - Cubre: HU-1, HU-2, HU-6

- [ ] **T034** Ejecutar el caso de generalización y registrar el puntaje: recorrido del **Administrador** más los tres casos que no son un usuario normal (autenticado sin rol, acceso revocado, persona sin sesión).
  - Terminado cuando: los cuatro pasan completos, quedan registrados igual que T033, y ninguno usa el caso de referencia del proyecto (Art. VIII).
  - Cubre: HU-3, HU-5, Art. VIII

- [ ] **T035** Barrer **todas** las rutas del backend y **todas** las pantallas del front, verificando que ninguna responda datos ni se renderice sin sesión válida, y que ninguna de administración responda a un rol RO.
  - Terminado cuando: existe la lista completa de rutas y pantallas con su resultado, y no hay ninguna excepción. Se verifica la lista completa, no una muestra.
  - Cubre: RF-01, RF-05

- [ ] **T036** Verificar que no haya ninguna contraseña legible ni ningún secreto: revisar respuestas, registros de la aplicación y el diff completo de la rama.
  - Terminado cuando: ninguna respuesta ni registro contiene una contraseña, el diff no contiene credenciales, keys ni tokens, y `.env` no está versionado.
  - Cubre: RF-19, Art. X.2

- [ ] **T037** Verificar que no haya datos inventados (Art. II): que el sistema no asigne rol por defecto, no deduzca el rol de la identificación ni de ningún otro dato, y niegue el acceso a quien no tiene rol.
  - Terminado cuando: un usuario creado sin rol no entra, y no existe en el código ningún valor de rol asumido por omisión.
  - Cubre: RF-06, Art. II

## Fase 5 — Cierre

- [ ] **T038** Actualizar documentación: en `README.md`, cómo levantar base de datos, backend y front, las variables de entorno necesarias y cómo crear el Administrador inicial; y marcar "Primera especificación" en la sección de estado.
  - Terminado cuando: alguien que clona el repositorio llega a entrar a la plataforma siguiendo solo el `README`, sin preguntar nada.
  - Cubre: Art. XII

- [ ] **T039** Abrir el Pull Request hacia `main` con la checklist obligatoria de `CONTRIBUTING.md` completa.
  - Terminado cuando: el PR está abierto, todas las tareas de este archivo están en `[x]`, y los seis puntos de la checklist están marcados y son verdaderos.
  - Cubre: Art. XI

---

## Cobertura: RF / HU → tareas

| RF / HU | Tareas |
|---|---|
| RF-01 — Autenticación para todo | T009, T017, T018, T020, T027, T035 |
| RF-02 — Exactamente dos roles | T013 |
| RF-03 — Rol vigente por sesión | T013, T018 |
| RF-04 — Solo las opciones del rol | T009, T012, T029 |
| RF-05 — Negar la opción ajena al rol | T009, T018, T035 |
| RF-06 — Sin rol, sin acceso | T009, T018, T037 |
| RF-07 — Cerrar sesión y expiración configurable | T004, T014, T017, T020 |
| RF-08 — Mostrar identificación y rol | T012, T019, T020, T029 |
| RF-09 — Fallos sin revelar detalles | T008, T020, T028 |
| RF-10 — Cuentas propias de la plataforma | T001, T005, T013, T015 |
| RF-11 — Pantalla de administración de usuarios | T010, T019, T022, T031 |
| RF-12 — Crear usuario | T010, T022, T031 |
| RF-13 — Cambiar rol | T010, T023, T031 |
| RF-14 — Restablecer contraseña | T010, T023, T031 |
| RF-15 — Revocar y eliminar acceso | T010, T014, T017, T023, T031 |
| RF-16 — Nunca sin Administrador activo | T010, T024, T031 |
| RF-17 — Cambiar su propia contraseña, opcional | T011, T025, T032 |
| RF-18 — Administrador inicial | T026 |
| RF-19 — Ninguna contraseña legible | T011, T013, T016, T019, T036 |
| RF-20 — Política de contraseñas | T004, T006, T011, T016, T022, T032 |
| RF-21 — Sin vencimiento periódico | T011, T025 |
| RF-22 — Bloqueo por intentos fallidos | T004, T008, T021 |
| RF-23 — Política y bloqueo como configuración | T004, T011, T016, T021 |
| HU-1 — Entrar a la plataforma | T008, T020, T028, T030, T033 |
| HU-2 — Ver solo lo que me corresponde | T009, T012, T029, T030, T033 |
| HU-3 — Mantener fuera a quien no tiene acceso | T008, T020, T027, T034 |
| HU-4 — Saber con qué rol trabajo | T012, T020, T029 |
| HU-5 — Administrar los usuarios | T010, T022, T023, T024, T031, T034 |
| HU-6 — Cambiar mi contraseña | T011, T025, T032, T033 |

**Totales:** 39 tareas — Fase 1: 6 · Fase 2: 6 · Fase 3: 20 · Fase 4: 5 · Fase 5: 2.
Los 23 requerimientos funcionales y las 6 historias de usuario tienen al menos una tarea.
