import { defineConfig, devices } from "@playwright/test";

/**
 * Pruebas de extremo a extremo: cubren lo único que no se puede verificar
 * desde el backend, que es lo que cada rol ve en pantalla (HU-2, HU-4).
 *
 * Front y backend deben estar arriba. La dirección se puede cambiar con
 * VIDA_FRONT_URL sin tocar este archivo.
 */
const direccionDelFront = process.env.VIDA_FRONT_URL ?? "http://127.0.0.1:3000";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  reporter: [["list"]],
  use: {
    baseURL: direccionDelFront,
    locale: "es-CO",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
