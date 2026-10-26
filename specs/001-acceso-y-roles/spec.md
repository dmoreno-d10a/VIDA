# Especificación: Acceso y roles

**ID:** 001
**Rama:** `feature/001-acceso-y-roles`
**Autor:** Diego Moreno
**Fecha:** 2026-10-25
**Estado:** Borrador

> Una spec describe **qué** se necesita y **por qué**. No incluye tecnologías, librerías, estructura de código ni prompts. Eso va en `plan.md`.

---

## 1. Contexto y problema

V.I.D.A. va a manejar información de las actividades que los Requirements Owners (RO) de VortexBird documentan para las fábricas de desarrollo: archivos cargados, texto de contexto y documentos generados. Esa información no es pública y no debe quedar al alcance de cualquiera que abra la dirección de la plataforma.

Hoy no existe ninguna barrera de acceso: no hay forma de saber quién entra, ni de distinguir a quien solo genera documentación de quien configura la plataforma. Sin esa distinción, las funcionalidades siguientes no tienen sobre qué decidir quién puede hacer qué: la gestión de tipos de documentación y sus formatos (funcionalidad 002) y los parámetros del sistema —rúbrica, pesos, puntaje mínimo, iteraciones y modelo por tarea— (funcionalidad 007) son tareas del Administrador, mientras cargar información y generar documentos son tareas del RO. Mezclar ambas en un mismo acceso expone la configuración de la plataforma a cambios accidentales y rompe el Artículo X de la constitución, que exige usuarios autenticados y dos roles.

Esta funcionalidad es la primera del mapa porque todas las demás dependen de ella: deja lista la base de acceso, sin construir todavía nada de lo que irá encima.

## 2. Usuarios

- **RO (Requirements Owner).** Usa la plataforma para cargar la información de sus actividades y generar la documentación técnica. No configura la plataforma.
- **Administrador.** Hace todo lo que hace un RO y, además, gestiona los tipos de documentación, sus formatos y los parámetros del sistema.
- **Usuario sin acceso.** Cualquier persona que llegue a la plataforma sin estar autenticada o sin un rol asignado. No es un usuario de la plataforma; aparece aquí porque el sistema debe tratarla explícitamente.

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

### HU-4: Saber con qué rol estoy trabajando
**Como** usuario de V.I.D.A., **quiero** ver quién soy y con qué rol entré, **para** confirmar que estoy en la cuenta correcta antes de cargar información o cambiar configuración.

**Criterios de aceptación:**
- **Dado** un usuario autenticado, **cuando** está en cualquier pantalla de la plataforma, **entonces** ve su identificación y su rol vigente.
- **Dado** un usuario autenticado, **cuando** su rol cambia, **entonces** las opciones visibles corresponden al rol nuevo sin necesidad de intervención técnica.

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
| RF-10 | El sistema debe tomar el rol de cada usuario de la información de acceso administrada fuera del código: cambiar el rol de un usuario no debe requerir cambios en el código. |

## 5. Entradas y salidas

| Tipo | Elemento | Formato | Origen / destino |
|---|---|---|---|
| Entrada | Identificación del usuario que quiere entrar | Datos de identificación ingresados en la plataforma | La persona que intenta entrar (RO o Administrador) |
| Entrada | Usuarios autorizados y rol de cada uno | Registro de acceso administrado fuera del código | Por definir: ver segunda aclaración de la sección 9 |
| Salida | Sesión activa con rol vigente | Estado de la sesión del usuario en la plataforma | El propio usuario, y las funcionalidades 002 a 007, que deciden con base en él |
| Salida | Opciones visibles según el rol | Pantalla de la plataforma | El usuario autenticado |
| Salida | Negación de acceso con su motivo | Mensaje en pantalla | La persona que intentó entrar o abrir una opción que no le corresponde |

## 6. Casos borde y errores

- **Usuario autenticado sin rol asignado:** no entra. El sistema no le muestra pantallas ni información y le indica que solicite autorización (RF-06).
- **Intento de acceso directo a una opción ajena al rol:** se niega sin mostrar nada de su contenido, igual que si no existiera para ese usuario (RF-05).
- **Sesión vencida mientras el usuario trabaja:** se trata como sin acceso y se le pide identificarse de nuevo. Esta spec no define qué pasa con el trabajo en curso, porque todavía no existe trabajo que preservar: lo definirá la funcionalidad que lo introduzca (003).
- **Credenciales incorrectas:** se niega el acceso con un mensaje que no revela si el usuario existe ni qué dato falló (RF-09).
- **Rol cambiado mientras el usuario tiene sesión abierta:** el rol vigente se aplica sin intervención técnica; el momento exacto en que toma efecto (de inmediato o al volver a entrar) se define en el plan, siempre que no quede fijo en el código.
- **Servicio de identidad no disponible:** nadie entra. El sistema informa que el acceso no está disponible en ese momento y no concede acceso parcial ni rol por defecto.
- **Usuario que ya no debe tener acceso:** al quedar sin rol o sin autorización, vuelve a ser un usuario sin acceso en los términos de HU-3.

## 7. Fuera de alcance

- La **gestión de tipos de documentación** y la carga de sus formatos (funcionalidad 002).
- La **carga de información de una actividad** y todo lo que sigue: análisis, preguntas, generación, evaluación, historial y descarga (funcionalidades 003 a 006).
- La **administración de los parámetros del sistema** —rúbrica, pesos, puntaje mínimo, iteraciones y modelo por tarea— (funcionalidad 007). Esta spec solo deja definido quién tendrá derecho a tocarlos.
- Las **pantallas propias de cada rol más allá de su menú de opciones.** Esta spec define qué ve cada rol, no el contenido de opciones que aún no existen.
- Roles adicionales, permisos por usuario, grupos o jerarquías: solo existen RO y Administrador (RF-02).
- La **retención y eliminación de la información de acceso**, pendiente abierto del Artículo X de la constitución.

## 8. Criterios de éxito medibles

- **0 pantallas y 0 datos** de la plataforma accesibles sin sesión iniciada, verificado sobre todas las rutas y opciones existentes al cerrar esta funcionalidad.
- **0 opciones de administración** visibles o alcanzables para un usuario con rol RO, incluyendo intentos de acceso directo.
- Las cuatro situaciones de acceso quedan verificadas con al menos un caso cada una: usuario con rol RO, usuario con rol Administrador, usuario autenticado sin rol y persona sin sesión. Ninguna de ellas es el caso de referencia del proyecto (Art. VIII).
- **100 % de las negaciones de acceso** se informan sin revelar si el usuario existe ni cuál dato falló.
- Cambiar el rol de un usuario y cambiar la duración de la sesión se logran **sin modificar código**.

## 9. Pendientes y preguntas abiertas

> Todo lo que no se sabe se marca aquí como `[NECESITA ACLARACIÓN: ...]`. La spec no pasa a planificación con aclaraciones abiertas que afecten el alcance.

- `[NECESITA ACLARACIÓN: de dónde salen las identidades de los usuarios — ¿se usa la identidad corporativa de VortexBird que ya tienen los RO, o V.I.D.A. administra sus propias cuentas y contraseñas? Cambia el alcance: con identidad corporativa esta funcionalidad no incluye registro, cambio ni recuperación de contraseña; con cuentas propias, sí.]`
- `[NECESITA ACLARACIÓN: quién provisiona los usuarios y asigna los roles, y si esta funcionalidad debe incluir una pantalla de administración de usuarios para el Administrador o la asignación se hace fuera de la plataforma. Si incluye pantalla, el alcance crece; si no, hay que definir quién lo hace y cómo.]`
- `[NECESITA ACLARACIÓN: si se requiere registro de auditoría de accesos y de cambios de rol (quién entró, cuándo, intentos fallidos, quién cambió qué rol). Afecta el alcance de esta funcionalidad y se relaciona con los pendientes de retención del Artículo X de la constitución.]`

## 10. Verificación contra la constitución

- [x] Respeta la estructura de los formatos definidos (Art. I) — no aplica: esta funcionalidad no lee ni genera documentos, y no toca ningún formato.
- [x] No exige completar datos que no estén en los insumos ni en las respuestas del RO (Art. II y III) — ningún dato de acceso se deduce ni se completa por cuenta del sistema: sin rol asignado no hay rol por defecto, se niega el acceso.
- [x] Contempla al menos un caso distinto al de referencia (Art. VIII) — se verifica con los cuatro casos de acceso de la sección 8, ninguno ligado al caso de referencia (Adapter Reverso).
- [x] No define tecnologías ni implementación (Art. XI) — no se menciona ningún mecanismo de autenticación, almacenamiento ni estructura de código; el *cómo* queda para `plan.md`.
