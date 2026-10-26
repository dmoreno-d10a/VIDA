import { expect, test } from "@playwright/test";

/**
 * HU-2 y HU-4: cada rol ve solo sus opciones, y todos ven quién son.
 *
 * Estas pruebas miran la pantalla. La barrera de verdad está en el backend y
 * se prueba con pytest; aquí se comprueba que el menú no ofrezca lo que el rol
 * no puede usar, y que sin sesión no se renderice nada de la plataforma.
 *
 * Los usuarios son los mismos ficticios de backend/tests/datos_ficticios.py,
 * y deben existir en la base antes de correr estas pruebas (Art. X.3).
 */

const RO = {
  identificacion: "ro.prueba@ejemplo.local",
  contrasena: "prueba-ro-acceso-7318",
};

const ADMINISTRADOR = {
  identificacion: "admin.prueba@ejemplo.local",
  contrasena: "prueba-admin-acceso-9542",
};

const OPCION_ADMINISTRACION = /usuarios/i;

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

test("sin sesión no se renderiza ninguna pantalla privada", async ({ page }) => {
  await page.goto("/inicio");

  await expect(page).toHaveURL(/\/acceso/);
  await expect(page.getByRole("button", { name: /entrar/i })).toBeVisible();
});

test("el RO ve sus opciones y no la administración de usuarios", async ({
  page,
}) => {
  await entrar(page, RO);

  await expect(page.getByText(RO.identificacion)).toBeVisible();
  await expect(page.getByText(/^RO$/)).toBeVisible();

  const menu = page.getByRole("navigation");
  await expect(menu.getByRole("link", { name: OPCION_ADMINISTRACION })).toHaveCount(0);
});

test("el Administrador ve la administración de usuarios y lo del RO", async ({
  page,
}) => {
  await entrar(page, ADMINISTRADOR);

  await expect(page.getByText(ADMINISTRADOR.identificacion)).toBeVisible();
  await expect(page.getByText(/administrador/i).first()).toBeVisible();

  const menu = page.getByRole("navigation");
  await expect(menu.getByRole("link", { name: OPCION_ADMINISTRACION })).toBeVisible();
  await expect(menu.getByRole("link", { name: /contrase/i })).toBeVisible();
});

test("al cerrar sesión hay que identificarse de nuevo", async ({ page }) => {
  await entrar(page, RO);

  await page.getByRole("button", { name: /cerrar sesi/i }).click();

  await expect(page).toHaveURL(/\/acceso/);
  await page.goto("/inicio");
  await expect(page).toHaveURL(/\/acceso/);
});
