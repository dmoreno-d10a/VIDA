# Cómo levantar y probar esto: Tipos de documentación

**Spec:** [`spec.md`](./spec.md) · **Plan:** [`plan.md`](./plan.md)
**Rama:** `feature/002-tipos-de-documentacion`
**Fecha:** 2026-11-03

Guía para verificar la funcionalidad de punta a punta. No trae código de implementación: eso
sale de `tasks.md`.

---

## 1. El entorno

Si vas a trabajar esta funcionalidad en paralelo con otra, móntala en su propio worktree, con
sus puertos y su base aparte:

```bash
bash scripts/nuevo-worktree.sh 002 --con-base
cd ../vida-worktrees/002-tipos-de-documentacion
bash scripts/apuntar-spec.sh      # deja .specify/feature.json apuntando a esta spec
```

Si prefieres trabajarla en el checkout principal, basta lo de siempre:

```bash
docker compose up -d
cd backend && .venv/Scripts/python -m alembic upgrade head
```

En ambos casos hace falta un Administrador, porque toda la administración de tipos lo exige:

```bash
cd backend && .venv/Scripts/python -m scripts.crear_admin
```

## 2. Las variables nuevas

Se agregan a `.env.ejemplo` (uno de los archivos que todas las ramas tocan: al resolver el
conflicto se conservan las dos partes):

```bash
# --- Formatos de los tipos de documentación (spec 002) ---

# Carpeta donde se guardan los archivos de formato que carga el Administrador.
# Relativa a la raíz del repositorio. Está dentro de uploads/, que .gitignore
# excluye: ningún archivo cargado puede llegar al repositorio (Art. X.2).
VIDA_ALMACEN_FORMATOS=uploads/formatos

# Tamaño máximo de un archivo de formato, en megabytes (RF-18).
VIDA_FORMATO_MB_MAX=25

# Extensiones admitidas, separadas por coma (RF-04). Los formatos antiguos de
# Office (.doc, .xls) no se admiten: ver la decisión 2 de research.md.
VIDA_FORMATO_EXTENSIONES=docx,xlsx
```

Las tres tienen valor por defecto, así que un `.env` de la 001 sigue funcionando sin tocarlo.

## 3. Arrancar

```bash
cd backend  && .venv/Scripts/python -m uvicorn app.main:app --port 8000
cd frontend && npm run dev
```

Entra como Administrador en **http://127.0.0.1:3000** y busca **Tipos de documentación** en el
menú de administración.

## 4. Generar los formatos de prueba

Los tres casos son ficticios y se generan; no hay binarios en el repositorio, y el formato real
del cliente no entra (Art. X.3, decisión 9 de `research.md`):

```bash
cd backend && .venv/Scripts/python -m scripts.generar_formatos_de_prueba
```

Deja tres archivos en una carpeta temporal y escribe en pantalla dónde quedaron:

| Archivo | Qué contiene | Para qué |
|---|---|---|
| `referencia-adapter-reverso.docx` | La estructura del Adapter Reverso, con contenido ficticio | El formato que el área usa hoy |
| `generalizacion-word.docx` | Otra jerarquía, dos títulos con el mismo nombre, uno sin texto | Art. VIII y los casos borde |
| `generalizacion-excel.xlsx` | Tres hojas, encabezados en la fila 3 en una de ellas, dos columnas con el mismo nombre | Art. VIII en la rama de Excel |

## 5. El recorrido que prueba la funcionalidad

Cada paso corresponde a una historia de usuario de la spec.

**HU-1 — Crear un tipo.** Crea «Adapter Reverso». Debe aparecer en el listado como
**incompleto**, con el aviso de que todavía no se puede usar. Intenta crear otro con el mismo
nombre en minúsculas: debe rechazarlo.

**HU-2 — Cargar el formato.** Carga `referencia-adapter-reverso.docx`. El tipo pasa a **activo**.
Después prueba los rechazos, y comprueba que en los cuatro el tipo **queda como estaba**:

| Qué cargas | Qué debe pasar |
|---|---|
| Un `.pdf` o un `.txt` | Rechazo, indicando que solo se admiten `.docx` y `.xlsx` |
| Un `.doc` renombrado a `.docx` | Rechazo: la firma del archivo no corresponde (decisión 4 de `research.md`) |
| Un archivo de más de 25 MB | Rechazo indicando el límite, **mientras** se recibe |
| Un `.docx` sin ningún estilo de título | Rechazo: no se reconoció estructura, diciendo qué se esperaba |

**HU-3 — Confirmar la estructura.** Abre el detalle del tipo y compara con el archivo abierto al
lado. Lo que hay que verificar es que **no sobre, no falte y no esté reordenado nada**. Con
`generalizacion-word.docx`, los dos títulos repetidos deben aparecer **los dos**, y el título sin
texto debe aparecer sin nombre inventado. Con `generalizacion-excel.xlsx`, las hojas en el orden
del libro, los encabezados de la hoja que los tiene en la fila 3 bien leídos, y las dos columnas
de nombre repetido presentes las dos.

Vuelve a abrir el detalle: debe mostrar exactamente lo mismo, sin volver a procesar el archivo
(Art. VI, RF-07).

**HU-4 — Versionado.** Reemplaza el formato por `generalizacion-word.docx`. Verifica que:

- La estructura vigente es la del archivo nuevo.
- El historial muestra **dos** versiones, con la nueva marcada como vigente y su fecha.
- Consultar la versión 1 sigue devolviendo **su** estructura, la original.

Repite el reemplazo con el mismo archivo otra vez: debe crear una versión 3, sin comparar
contenidos para decidir si «cambió» (sección 6 de la spec).

Después desactiva el tipo, reactívalo, e intenta eliminarlo: debe negarse y ofrecerte
desactivarlo.

**HU-5 — La vista del RO.** Entra como RO (desde otro navegador o una ventana privada, para no
perder la sesión de Administrador):

- Debe ver los tipos **activos** con nombre y descripción, y nada más.
- **No** debe ver los incompletos ni los desactivados.
- Escribe a mano la dirección de la administración de tipos: debe negarle el paso, y el menú no
  debe mostrarle la opción.
- Desactiva todos los tipos y vuelve a consultar: debe salir el mensaje explícito de que no hay
  tipos disponibles, no una pantalla vacía.

## 6. Las pruebas automáticas

```bash
cd backend  && .venv/Scripts/python -m pytest
cd frontend && npx playwright test
```

Lo que se agrega:

| Archivo | Qué cubre |
|---|---|
| `backend/tests/test_tipos_de_documentacion.py` | Crear, listar, modificar, desactivar, eliminar, y que un RO no alcance ninguna de esas rutas |
| `backend/tests/test_reconocimiento_de_formato.py` | La estructura reconocida de los tres casos, comparada contra la esperada; y los cuatro rechazos |
| `backend/tests/test_versiones_de_formato.py` | Tres reemplazos seguidos conservan las tres versiones anteriores con su archivo y su estructura |
| `frontend/e2e/tipos-de-documentacion.spec.ts` | El recorrido del Administrador y que el RO no vea la opción |

Las pruebas del backend usan la base `vida_pruebas`, que se crea sola, y los usuarios ficticios
de `backend/tests/datos_ficticios.py`, como las de la 001.

**La prueba que más importa** es la de `test_reconocimiento_de_formato.py`: compara la estructura
reconocida contra la que el script generador sabe que escribió. Es la única forma de verificar el
Art. I sin que sea una opinión, y por eso la estructura esperada vive al lado del código que
genera el archivo.

## 7. Qué debería quedar cierto al terminar

Son los criterios medibles de la sección 8 de la spec, en orden de verificación:

- [ ] 0 diferencias entre la estructura reconocida y la del archivo, en los tres casos
- [ ] 0 elementos inventados: ninguna sección, hoja o columna que el archivo no traiga
- [ ] 1 solo análisis por formato: reabrir el detalle no reprocesa el archivo
- [ ] 0 opciones de administración alcanzables para un RO, incluyendo la dirección escrita a mano
- [ ] 100 % de las cargas inválidas rechazadas con motivo, dejando el tipo como estaba
- [ ] 0 tipos incompletos o desactivados visibles para un RO
- [ ] 0 pérdidas al reemplazar: tras tres reemplazos, las tres versiones anteriores siguen enteras
- [ ] Cambiar extensiones y tamaño máximo sin tocar código
