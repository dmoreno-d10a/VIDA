# Especificación: Acceso y roles

**ID:** 001
**Rama:** `feature/001-acceso-y-roles`
**Autor:** Diego Moreno
**Fecha:** 2026-10-25
**Estado:** En revisión

> Una spec describe **qué** se necesita y **por qué**. No incluye tecnologías, librerías, estructura de código ni prompts. Eso va en `plan.md`.

---

## 1. Contexto y problema

V.I.D.A. va a manejar información de las actividades que los Requirements Owners (RO) de VortexBird documentan para las fábricas de desarrollo: archivos cargados, texto de contexto y documentos generados. Esa información no es pública y no debe quedar al alcance de cualquiera que abra la dirección de la plataforma.

Hoy no existe ninguna barrera de acceso: no hay forma de saber quién entra, ni de distinguir a quien solo genera documentación de quien configura la plataforma. Sin esa distinción, las funcionalidades siguientes no tienen sobre qué decidir quién puede hacer qué: la gestión de tipos de documentación y sus formatos (funcionalidad 002) y los parámetros del sistema —rúbrica, pesos, puntaje mínimo, iteraciones y modelo por tarea— (funcionalidad 007) son tareas del Administrador, mientras cargar información y generar documentos son tareas del RO. Mezclar ambas en un mismo acceso expone la configuración de la plataforma a cambios accidentales y rompe el Artículo X de la constitución, que exige usuarios autenticados y dos roles.

V.I.D.A. administra sus propias cuentas: no depende de la identidad corporativa de VortexBird. Por eso esta funcionalidad incluye también la pantalla con la que el Administrador crea y mantiene los usuarios de la plataforma; sin ella, nadie podría entrar.

Esta funcionalidad es la primera del mapa porque todas las demás dependen de ella: deja lista la base de acceso, sin construir todavía nada de lo que irá encima.

## 2. Usuarios

- **RO (Requirements Owner).** Usa la plataforma para cargar la información de sus actividades y generar la documentación técnica. No configura la plataforma ni administra usuarios.
- **Administrador.** Hace todo lo que hace un RO y, además, administra los usuarios de la plataforma y —en funcionalidades posteriores— los tipos de documentación, sus formatos y los parámetros del sistema.
- **Administrador inicial.** El Administrador que existe desde la puesta en marcha de la plataforma, creado fuera de sus pantallas, porque sin él no habría quien creara al primer usuario.
- **Usuario sin acceso.** Cualquier persona que llegue a la plataforma sin estar autenticada, sin un rol asignado o con su acceso revocado. No es un usuario de la plataforma; aparece aquí porque el sistema debe tratarla explícitamente.

## 3. Historias de usuario

### HU-1: Entrar a la plataforma
**Como** usuario de V.I.D.A. (RO o Administrador), **quiero** autenticarme para entrar, **para** que mi trabajo y la información de las actividades no queden expuestos a quien no debe verlos.

**Criterios de aceptación:**
- **Dado** un usuario autorizado que no ha iniciado sesión, **cuando** se identifica correctamente, **entonces** entra a la plataforma y el sistema lo reconoce con su rol durante toda la sesión.
- **Dado** un usuario autorizado, **cuando** se identifica con credenciales incorrectas, **entonces** el sistema no lo deja entrar y le indica que no pudo validarse, sin revelar si el usuario existe ni cuál de los datos falló.
- **Dado** un usuario que entró a la plataforma, **cuando** cierra su sesión, **entonces** vuelve a quedar sin acceso y debe identificarse de nuevo para entrar.

### HU-2: Ver solo lo que me corresponde
**Como** RO, **quiero** ver únicamente las opciones de mi rol, **para** no equivocarme entrando a la configuración de la plataforma ni perder tiempo entre opciones que no puedo usar.

**Criterios de aceptación:**
- **Dado** un RO autenticado, **cuando** entra a la plataforma, **entonces** ve las opciones de su rol y **no** ve las opciones de administración.
- **Dado** un Administrador autenticado, **cuando** entra a la plataforma, **entonces** ve las opciones de administración **y** las opciones propias del RO.
- **Dado** un RO autenticado, **cuando** intenta llegar directamente a una opción de administración sin pasar por el menú, **entonces** el sistema se lo impide y no le muestra ninguna información de esa opción.

### HU-3: Mantener fuera a quien no tiene acceso
**Como** responsable del proyecto, **quiero** que nadie sin acceso vea pantallas ni información, **para** cumplir el Artículo X de la constitución y proteger la información de las actividades.

**Criterios de aceptación:**
- **Dado** una persona sin sesión iniciada, **cuando** intenta abrir cualquier pantalla de la plataforma, **entonces** el sistema no le muestra ninguna pantalla ni dato y la lleva a identificarse.
- **Dado** un usuario que se identifica correctamente pero no tiene ningún rol asignado, **cuando** intenta entrar, **entonces** el sistema no le da acceso y le indica que solicite autorización, sin mostrarle ninguna pantalla ni información de la plataforma.
- **Dado** un usuario con sesión vencida, **cuando** intenta usar cualquier opción, **entonces** el sistema lo trata como sin acceso y le pide identificarse de nuevo.
- **Dado** un usuario con el acceso revocado por el Administrador, **cuando** intenta entrar, **entonces** el sistema no lo deja y no le muestra ninguna pantalla ni dato.

### HU-4: Saber con qué rol estoy trabajando
**Como** usuario de V.I.D.A., **quiero** ver quién soy y con qué rol entré, **para** confirmar que estoy en la cuenta correcta antes de cargar información o cambiar configuración.

**Criterios de aceptación:**
- **Dado** un usuario autenticado, **cuando** está en cualquier pantalla de la plataforma, **entonces** ve su identificación y su rol vigente.
- **Dado** un usuario autenticado, **cuando** su rol cambia, **entonces** las opciones visibles corresponden al rol nuevo sin necesidad de intervención técnica.

### HU-5: Administrar los usuarios de la plataforma
**Como** Administrador, **quiero** crear y mantener los usuarios de la plataforma, **para** dar acceso a los RO del área y quitárselo a quien ya no debe tenerlo, sin depender de nadie más.

**Criterios de aceptación:**
- **Dado** un Administrador autenticado, **cuando** abre la administración de usuarios, **entonces** ve los usuarios existentes con su identificación, su rol y si su acceso está activo o revocado.
- **Dado** un Administrador en la administración de usuarios, **cuando** crea un usuario indicando su identificación, su rol y una contraseña inicial, **entonces** ese usuario queda habilitado y puede entrar con esa contraseña.
- **Dado** un Administrador, **cuando** intenta crear un usuario con una identificación que ya existe, **entonces** el sistema no lo crea y le indica el motivo.
- **Dado** un usuario existente, **cuando** el Administrador le cambia el rol, **entonces** ese usuario pasa a ver solo las opciones del rol nuevo, sin intervención técnica.
- **Dado** un usuario que olvidó su contraseña, **cuando** el Administrador se la restablece, **entonces** el usuario entra con la contraseña nueva y la anterior deja de servir.
- **Dado** un usuario al que el Administrador le revoca o elimina el acceso, **cuando** ese usuario intenta entrar, **entonces** el sistema lo trata como usuario sin acceso.
- **Dado** un Administrador, **cuando** intenta revocar, eliminar o cambiar de rol al único Administrador activo —incluido él mismo—, **entonces** el sistema no lo permite y le indica que la plataforma no puede quedar sin Administrador.
- **Dado** un RO autenticado, **cuando** intenta abrir la administración de usuarios, **entonces** el sistema se lo impide y no le muestra ningún dato de los usuarios.

### HU-6: Cambiar mi contraseña
**Como** usuario de V.I.D.A., **quiero** cambiar la contraseña que me asignó el Administrador, **para** que mi acceso sea solo mío y nadie más conozca con qué entro.

**Criterios de aceptación:**
- **Dado** un usuario autenticado, **cuando** cambia su contraseña indicando la actual y la nueva, **entonces** el sistema la actualiza y en adelante solo sirve la nueva.
- **Dado** un usuario autenticado, **cuando** intenta cambiar su contraseña sin acertar la actual, **entonces** el sistema no la cambia y le indica que no pudo validarse.
- **Dado** un usuario que nunca cambió la contraseña que le asignó el Administrador, **cuando** entra a la plataforma, **entonces** el sistema lo deja trabajar normalmente: cambiarla es su decisión, no una obligación.
- **Dado** un usuario autenticado, **cuando** intenta fijar una contraseña que no cumple la política vigente, **entonces** el sistema no la acepta y le indica qué regla incumplió.
- **Dado** un usuario autenticado, **cuando** intenta fijar como nueva la misma contraseña que tiene, **entonces** el sistema no la acepta.

## 4. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| RF-01 | El sistema debe exigir autenticación para cualquier pantalla, opción o dato de la plataforma: no existe contenido accesible sin sesión iniciada. |
| RF-02 | El sistema debe reconocer exactamente dos roles: **RO** y **Administrador**. No existen otros roles ni permisos individuales por usuario. |
| RF-03 | El sistema debe asociar a cada usuario autenticado un rol vigente y usarlo para decidir qué puede ver y hacer durante la sesión. |
| RF-04 | El sistema debe mostrar a cada usuario únicamente las opciones de su rol. El rol Administrador incluye todas las opciones del rol RO. |
| RF-05 | El sistema debe negar el acceso a una opción que no corresponde al rol del usuario, incluso cuando se intente llegar a ella sin pasar por el menú, y no debe mostrar ninguna información de esa opción al negarla. |
| RF-06 | El sistema debe negar el acceso al usuario que se autentica correctamente pero no tiene rol asignado, y debe indicarle que solicite autorización. |
| RF-07 | El sistema debe permitir al usuario cerrar su sesión, y debe terminar la sesión por expiración. La duración de la sesión es configuración, no un valor fijo. |
| RF-08 | El sistema debe mostrar en todo momento al usuario autenticado su identificación y su rol vigente. |
| RF-09 | El sistema debe informar los accesos fallidos sin revelar si el usuario existe, ni cuál de los datos ingresados fue incorrecto. |
| RF-10 | El sistema debe administrar sus propias cuentas de usuario: la plataforma no depende de un servicio de identidad externo para saber quién entra. |
| RF-11 | El sistema debe ofrecer al Administrador una pantalla de administración de usuarios, accesible solo para ese rol, donde vea los usuarios existentes con su identificación, su rol y el estado de su acceso. |
| RF-12 | El sistema debe permitir al Administrador **crear** un usuario indicando su identificación, su rol y una contraseña inicial, y debe rechazar identificaciones ya existentes. |
| RF-13 | El sistema debe permitir al Administrador **cambiar el rol** de un usuario existente, sin recrear la cuenta y sin cambios en el código. |
| RF-14 | El sistema debe permitir al Administrador **restablecer la contraseña** de un usuario, dejando sin efecto la anterior. |
| RF-15 | El sistema debe permitir al Administrador **revocar el acceso** de un usuario y **eliminarlo**, dejándolo en adelante como usuario sin acceso. |
| RF-16 | El sistema debe impedir toda acción que deje la plataforma sin ningún Administrador activo, incluso cuando el Administrador la ejecute sobre su propia cuenta. |
| RF-17 | El sistema debe permitir a cada usuario **cambiar su propia contraseña** acreditando la actual. Cambiarla es opcional: no se obliga al usuario a hacerlo. |
| RF-18 | El sistema debe contar con un **Administrador inicial** desde la puesta en marcha de la plataforma, creado fuera de sus pantallas, sin que ninguna credencial quede en el repositorio (Art. X). |
| RF-19 | El sistema no debe guardar ni mostrar nunca las contraseñas de los usuarios en forma legible, a nadie, incluido el Administrador. |
| RF-20 | El sistema debe exigir que toda contraseña —inicial, cambiada o restablecida— cumpla la política vigente: mínimo **12** caracteres, máximo **64**, sin exigir combinaciones obligatorias de tipos de carácter, y rechazando las contraseñas de uso común y las que contengan la identificación del usuario. Al cambiarla o restablecerla, no debe aceptarse la inmediatamente anterior. |
| RF-21 | El sistema no debe vencer las contraseñas por tiempo: solo cambian por decisión del usuario (RF-17) o por restablecimiento del Administrador (RF-14). |
| RF-22 | El sistema debe bloquear temporalmente el acceso de una cuenta tras **5** intentos fallidos seguidos, durante **15** minutos, informándolo sin revelar si el usuario existe. |
| RF-23 | Todos los valores de la política de contraseñas y del bloqueo por intentos fallidos (RF-20 a RF-22) deben ser configuración: cambiarlos no debe requerir cambios en el código. |

## 5. Entradas y salidas

| Tipo | Elemento | Formato | Origen / destino |
|---|---|---|---|
| Entrada | Identificación y contraseña de quien quiere entrar | Datos ingresados en la pantalla de acceso | La persona que intenta entrar (RO o Administrador) |
| Entrada | Datos de un usuario nuevo: identificación, rol y contraseña inicial | Datos ingresados en la administración de usuarios | El Administrador |
| Entrada | Cambios sobre un usuario existente: rol, contraseña restablecida, acceso revocado o eliminación | Acciones en la administración de usuarios | El Administrador |
| Entrada | Contraseña actual y nueva del propio usuario | Datos ingresados en la plataforma | El usuario autenticado |
| Entrada | Administrador inicial | Puesta en marcha de la plataforma, fuera de sus pantallas | Responsable del proyecto |
| Salida | Sesión activa con rol vigente | Estado de la sesión del usuario en la plataforma | El propio usuario, y las funcionalidades 002 a 007, que deciden con base en él |
| Salida | Opciones visibles según el rol | Pantalla de la plataforma | El usuario autenticado |
| Salida | Listado de usuarios con su rol y el estado de su acceso | Pantalla de administración de usuarios | El Administrador |
| Salida | Negación de acceso con su motivo | Mensaje en pantalla | La persona que intentó entrar o abrir una opción que no le corresponde |

## 6. Casos borde y errores

- **Usuario autenticado sin rol asignado:** no entra. El sistema no le muestra pantallas ni información y le indica que solicite autorización (RF-06).
- **Intento de acceso directo a una opción ajena al rol:** se niega sin mostrar nada de su contenido, igual que si no existiera para ese usuario (RF-05). Aplica en particular a la administración de usuarios frente a un RO.
- **Sesión vencida mientras el usuario trabaja:** se trata como sin acceso y se le pide identificarse de nuevo. Esta spec no define qué pasa con el trabajo en curso, porque todavía no existe trabajo que preservar: lo definirá la funcionalidad que lo introduzca (003).
- **Credenciales incorrectas:** se niega el acceso con un mensaje que no revela si el usuario existe ni qué dato falló (RF-09).
- **Rol cambiado mientras el usuario tiene sesión abierta:** el rol vigente se aplica sin intervención técnica; el momento exacto en que toma efecto (de inmediato o al volver a entrar) se define en el plan, siempre que no quede fijo en el código.
- **Acceso revocado o usuario eliminado mientras tiene sesión abierta:** deja de poder usar la plataforma; el plan define si la sesión termina de inmediato o en su siguiente acción, pero en ningún caso conserva el acceso indefinidamente.
- **Identificación repetida al crear un usuario:** no se crea y se indica el motivo (RF-12).
- **Último Administrador activo:** no se puede revocar, eliminar ni cambiar de rol, aunque sea el propio Administrador quien lo intente sobre su cuenta (RF-16).
- **Contraseña inicial que el usuario nunca cambia:** sigue sirviendo; el sistema no lo obliga a cambiarla (RF-17).
- **Cambio de contraseña con la actual equivocada:** no se cambia y se informa sin más detalle (HU-6).
- **Contraseña que no cumple la política:** se rechaza indicando la regla incumplida, tanto si la fija el usuario como si la define el Administrador al crear la cuenta o al restablecerla (RF-20).
- **Intentos fallidos repetidos sobre una cuenta:** tras cinco seguidos, la cuenta queda bloqueada quince minutos; el mensaje no revela si el usuario existe ni si está bloqueado por esta causa (RF-22). El bloqueo se levanta por tiempo, sin intervención del Administrador.
- **Usuario que olvidó su contraseña:** la única vía prevista es que el Administrador la restablezca (RF-14); no hay recuperación autónoma (ver sección 7).
- **Servicio de acceso no disponible:** nadie entra. El sistema informa que el acceso no está disponible en ese momento y no concede acceso parcial ni rol por defecto.

## 7. Fuera de alcance

- La **gestión de tipos de documentación** y la carga de sus formatos Word o Excel (funcionalidad 002). Esta spec solo deja definido que esa opción será exclusiva del Administrador.
- La **carga de información de una actividad** y todo lo que sigue: análisis, preguntas, generación, evaluación, historial y descarga (funcionalidades 003 a 006).
- La **administración de los parámetros del sistema** —rúbrica, pesos, puntaje mínimo, iteraciones y modelo por tarea— (funcionalidad 007). Esta spec solo deja definido quién tendrá derecho a tocarlos.
- Las **pantallas propias de cada rol más allá de su menú de opciones.** Esta spec define qué ve cada rol, no el contenido de opciones que aún no existen.
- Roles adicionales, permisos por usuario, grupos o jerarquías: solo existen RO y Administrador (RF-02).
- **Recuperación autónoma de contraseña** por parte del usuario (por correo o preguntas de seguridad): quien la olvide depende del Administrador.
- **Autenticación con la identidad corporativa de VortexBird** o con cualquier proveedor externo: la plataforma administra sus propias cuentas (RF-10).
- **Vencimiento periódico de contraseñas** y exigencia de cambio al primer ingreso (RF-21, RF-17).
- **Segundo factor de autenticación** y bloqueo permanente de cuentas por intentos fallidos: el bloqueo es temporal y se levanta por tiempo (RF-22).
- **Registro de auditoría** de accesos y cambios de rol: no se requiere por ahora. Se podrá agregar más adelante sin rehacer lo que define esta spec.
- La **retención y eliminación de la información de acceso**, pendiente abierto del Artículo X de la constitución.

## 8. Criterios de éxito medibles

- **0 pantallas y 0 datos** de la plataforma accesibles sin sesión iniciada, verificado sobre todas las rutas y opciones existentes al cerrar esta funcionalidad.
- **0 opciones de administración** visibles o alcanzables para un usuario con rol RO, incluyendo intentos de acceso directo a la administración de usuarios.
- Las cinco situaciones de acceso quedan verificadas con al menos un caso cada una: usuario con rol RO, usuario con rol Administrador, usuario autenticado sin rol, usuario con acceso revocado y persona sin sesión. Ninguna de ellas es el caso de referencia del proyecto (Art. VIII).
- Las **seis acciones de la administración de usuarios** quedan verificadas: crear, cambiar rol, restablecer contraseña, revocar acceso, eliminar e intentar dejar la plataforma sin Administrador (esta última debe fallar siempre).
- **100 % de las negaciones de acceso** se informan sin revelar si el usuario existe ni cuál dato falló.
- **0 contraseñas legibles** en pantallas, listados o registros, para cualquier rol.
- **0 contraseñas aceptadas** que incumplan la política vigente, verificado en los tres puntos donde se fija una: creación del usuario, cambio por el propio usuario y restablecimiento por el Administrador.
- Cambiar el rol de un usuario, la duración de la sesión y cualquier valor de la política de contraseñas o del bloqueo por intentos fallidos se logran **sin modificar código**.

## 9. Pendientes y preguntas abiertas

> Todo lo que no se sabe se marca aquí como `[NECESITA ACLARACIÓN: ...]`. La spec no pasa a planificación con aclaraciones abiertas que afecten el alcance.

- **Sin aclaraciones abiertas que afecten el alcance.** Las tres marcas iniciales quedaron resueltas: ver *Registro de aclaraciones*.
- **Política de contraseñas: definida** (RF-20 a RF-23), con los valores recomendados y aprobados el 2026-10-25. Todos son configuración, de modo que ajustarlos no exige tocar código.
- **PENDIENTE (constitución, Art. X.4)** — tiempo de retención y eliminación de los archivos que cargan los RO. Fuera del alcance de esta spec; se registra porque toca la misma información de acceso.

## 10. Verificación contra la constitución

- [x] Respeta la estructura de los formatos definidos (Art. I) — no aplica: esta funcionalidad no lee ni genera documentos, y no toca ningún formato.
- [x] No exige completar datos que no estén en los insumos ni en las respuestas del RO (Art. II y III) — ningún dato de acceso se deduce ni se completa por cuenta del sistema: sin rol asignado no hay rol por defecto, se niega el acceso.
- [x] Contempla al menos un caso distinto al de referencia (Art. VIII) — se verifica con los cinco casos de acceso y las seis acciones de administración de la sección 8, ninguno ligado al caso de referencia (Adapter Reverso).
- [x] No define tecnologías ni implementación (Art. XI) — no se menciona ningún mecanismo de autenticación, almacenamiento ni estructura de código; el *cómo* queda para `plan.md`.
- [x] Ningún secreto ni credencial en el repositorio (Art. X.2) — el Administrador inicial se crea en la puesta en marcha, fuera de las pantallas y sin credenciales versionadas (RF-18).

## Registro de aclaraciones

| Fecha | Pregunta | Respuesta |
|---|---|---|
| 2026-10-25 | ¿De dónde salen las identidades de los usuarios: identidad corporativa de VortexBird o cuentas propias de V.I.D.A.? | V.I.D.A. administra sus propias cuentas. El Administrador crea los usuarios y sus contraseñas. (RF-10, RF-12) |
| 2026-10-25 | ¿Quién provisiona los usuarios y asigna los roles? ¿Esta funcionalidad incluye una pantalla de administración de usuarios? | Sí, incluye la pantalla de administración de usuarios para el Administrador. (RF-11, HU-5) |
| 2026-10-25 | ¿Se requiere registro de auditoría de accesos y cambios de rol? | No por ahora. Queda fuera de alcance. |
| 2026-10-25 | ¿Qué debe poder hacer el Administrador en esa pantalla? | Crear usuarios con rol y contraseña inicial, cambiar el rol, restablecer la contraseña, y revocar o eliminar el acceso. (RF-12 a RF-15) |
| 2026-10-25 | En esa misma respuesta se mencionó "crear la opción de documentar con su respectivo formato". ¿Entra en la 001? | No: es la funcionalidad 002 del mapa y se especifica aparte. La 001 solo define que esa opción será exclusiva del Administrador. |
| 2026-10-25 | ¿Qué puede hacer el usuario con la contraseña que le asignó el Administrador? | Cambiarla cuando quiera, sin obligación de hacerlo al primer ingreso. (RF-17) |
| 2026-10-25 | ¿Cómo entra el primer Administrador, si solo un Administrador puede crear usuarios? | Se crea al instalar la plataforma, fuera de sus pantallas. (RF-18) |
| 2026-10-25 | ¿Cuál es la política de contraseñas? | Se adopta la recomendación alineada con NIST SP 800-63B: mínimo 12 y máximo 64 caracteres, sin composición obligatoria, rechazando contraseñas comunes y las que contengan la identificación del usuario, sin repetir la anterior, sin vencimiento periódico, y con bloqueo temporal de 15 minutos tras 5 intentos fallidos. Todo configurable. (RF-20 a RF-23) |
