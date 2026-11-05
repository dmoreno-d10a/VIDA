import { expect, test } from "@playwright/test";

/**
 * HU-1 a HU-5 de la 002: el recorrido completo del Administrador, y lo que un
 * RO no alcanza (CE-05).
 *
 * Lo que estas pruebas aportan sobre las de pytest es la pantalla: que la
 * estructura reconocida se **vea** de forma comparable con el archivo, y que
 * el RO no llegue ni escribiendo la dirección. La barrera de verdad está en el
 * backend y se prueba allá; aquí se comprueba que el front no la contradiga.
 *
 * Front y backend deben estar arriba, con los usuarios ficticios de
 * `backend/tests/datos_ficticios.py` en la base (Art. X.3). El formato de
 * prueba se genera con:
 *
 *     cd backend && .venv/Scripts/python -m scripts.generar_formatos_de_prueba
 *
 * y su ruta se le pasa a Playwright en `VIDA_FORMATO_DE_PRUEBA`. Sin esa
 * variable, las pruebas que cargan un archivo se omiten en vez de fallar: el
 * archivo no está en el repositorio a propósito.
 */

const RO = {
  identificacion: "ro.prueba@ejemplo.local",
  contrasena: "prueba-ro-acceso-7318",
};

const ADMINISTRADOR = {
  identificacion: "admin.prueba@ejemplo.local",
  contrasena: "prueba-admin-acceso-9542",
};

const TIPOS = "/administracion/tipos-de-documentacion";

/** El formato de prueba generado, si quien corre las pruebas lo preparó. */
const formatoDePrueba = process.env.VIDA_FORMATO_DE_PRUEBA;

/** Un nombre distinto por corrida: los tipos no se pueden repetir (RF-02). */
function nombreUnico(prefijo: string): string {
  return `${prefijo} ${Date.now()}`;
}

async function entrar(
  page: import("@playwright/test").Page,
  usuario: { identificacion: string; contrasena: string },
) {
  await page.goto("/acceso");
  await page.getByLabel(/identificaci/i).fill(usuario.identificacion);
  await page.getByLabel(/contrase/i).fill(usuario.contrasena);
  await page.getByRole("button", { name: /entrar/i }).click();
  await expect(page).toHaveURL(/\/inicio/);
}

async function crearTipo(
  page: import("@playwright/test").Page,
  nombre: string,
): Promise<void> {
  await page.goto(TIPOS);
  await page.getByLabel("Nombre").fill(nombre);
  await page.getByRole("button", { name: /crear tipo/i }).click();
  await expect(page.getByRole("status")).toContainText(nombre);
}

test("el Administrador ve la opción en el menú y llega al listado", async ({
  page,
}) => {
  await entrar(page, ADMINISTRADOR);

  await page
    .getByRole("link", { name: /tipos de documentaci/i })
    .first()
    .click();

  await expect(page).toHaveURL(new RegExp(TIPOS));
  await expect(
    page.getByRole("heading", { name: /tipos de documentaci/i }),
  ).toBeVisible();
});

test("un tipo nuevo aparece como sin formato y los RO no lo ven", async ({
  page,
}) => {
  const nombre = nombreUnico("Tipo recién creado");
  await entrar(page, ADMINISTRADOR);
  await crearTipo(page, nombre);

  const fila = page.getByRole("row").filter({ hasText: nombre });
  await expect(fila).toContainText(/sin formato/i);
  await expect(fila).toContainText(/no lo ven/i);
});

test("el RO no ve la opción ni alcanza la dirección escrita a mano", async ({
  page,
}) => {
  await entrar(page, RO);

  await expect(
    page.getByRole("link", { name: /tipos de documentaci/i }),
  ).toHaveCount(0);

  // Escrita a mano: la barrera está en el backend, así que la pantalla no
  // puede mostrar el listado aunque se llegue a su dirección.
  await page.goto(TIPOS);
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(page.getByRole("table")).toHaveCount(0);
});

test("el RO ve el mensaje explícito cuando no hay tipos que documentar", async ({
  page,
}) => {
  await entrar(page, RO);

  const seccion = page.getByRole("heading", { name: /qué puedes documentar/i });
  await expect(seccion).toBeVisible();
  // Sea que haya tipos o no, nunca queda una sección vacía: o lista los tipos
  // o dice qué hacer (HU-5).
  await expect(
    page.getByText(/solicítale al administrador|tipos de documentación que/i),
  ).toBeVisible();
});

test.describe("con un formato de prueba generado", () => {
  test.skip(
    !formatoDePrueba,
    "Falta VIDA_FORMATO_DE_PRUEBA: genera los formatos con scripts.generar_formatos_de_prueba",
  );

  test("cargar el formato muestra la estructura y activa el tipo", async ({
    page,
  }) => {
    const nombre = nombreUnico("Con formato");
    await entrar(page, ADMINISTRADOR);
    await crearTipo(page, nombre);

    await page.getByRole("link", { name: nombre }).click();
    await expect(page.getByRole("heading", { name: nombre })).toBeVisible();

    await page.setInputFiles("#archivo-de-formato", formatoDePrueba!);
    await page.getByRole("button", { name: /^cargar$/i }).click();

    // El análisis puede tardar hasta medio minuto (CE-09).
    await expect(page.getByRole("status").first()).toContainText(/versión 1/i, {
      timeout: 40_000,
    });
    await expect(
      page.getByRole("heading", { name: /estructura reconocida/i }),
    ).toBeVisible();
    await expect(page.getByText(/activo/i).first()).toBeVisible();
  });

  test("reemplazar el formato crea la versión 2 y conserva la 1", async ({
    page,
  }) => {
    const nombre = nombreUnico("Con dos versiones");
    await entrar(page, ADMINISTRADOR);
    await crearTipo(page, nombre);
    await page.getByRole("link", { name: nombre }).click();

    for (const version of [1, 2]) {
      await page.setInputFiles("#archivo-de-formato", formatoDePrueba!);
      await page.getByRole("button", { name: /^cargar$/i }).click();
      await expect(page.getByRole("status").first()).toContainText(
        new RegExp(`versión ${version}`, "i"),
        { timeout: 40_000 },
      );
    }

    // El historial conserva las dos y dice cuál está vigente (RF-21).
    await expect(
      page.getByRole("heading", { name: /historial de formatos/i }),
    ).toBeVisible();
    const historial = page.getByRole("table").last();
    await expect(historial.getByRole("row")).toHaveCount(3); // encabezado + 2

    // Y la estructura de la versión 1 sigue consultable.
    await historial
      .getByRole("row")
      .filter({ hasText: "1" })
      .getByRole("button", { name: /ver/i })
      .click();
    await expect(
      page.getByRole("heading", { name: /estructura de la versión 1/i }),
    ).toBeVisible();
  });

  test("eliminar un tipo con formato ofrece desactivarlo", async ({ page }) => {
    const nombre = nombreUnico("No se puede eliminar");
    await entrar(page, ADMINISTRADOR);
    await crearTipo(page, nombre);
    await page.getByRole("link", { name: nombre }).click();
    await page.setInputFiles("#archivo-de-formato", formatoDePrueba!);
    await page.getByRole("button", { name: /^cargar$/i }).click();
    await expect(page.getByRole("status").first()).toContainText(/versión 1/i, {
      timeout: 40_000,
    });

    await page.goto(TIPOS);
    page.once("dialog", (dialogo) => dialogo.accept());
    await page
      .getByRole("row")
      .filter({ hasText: nombre })
      .getByRole("button", { name: /eliminar/i })
      .click();

    // El mensaje del backend, con la alternativa en la misma frase (RF-15).
    await expect(page.getByRole("alert")).toContainText(/desactivarlo/i);
  });
});
