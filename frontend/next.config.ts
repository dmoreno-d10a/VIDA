import type { NextConfig } from "next";

/**
 * Las llamadas al backend pasan por `/api/...` del propio front y se
 * reescriben hacia FastAPI. Así el navegador habla con un solo origen: la
 * cookie de sesión no cruza sitios y no hace falta CORS.
 *
 * La dirección del backend es configuración (VIDA_API_URL), no un valor fijo.
 */
const direccionDelBackend = process.env.VIDA_API_URL ?? "http://127.0.0.1:8000";

const configuracion: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:ruta*", destination: `${direccionDelBackend}/:ruta*` }];
  },
};

export default configuracion;
