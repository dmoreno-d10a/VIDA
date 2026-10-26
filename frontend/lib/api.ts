/**
 * Único punto desde donde el front llama al backend.
 *
 * Aquí no hay ninguna decisión de permisos ni ninguna credencial: eso vive en
 * el backend (Art. IV de la constitución). Este archivo solo traslada
 * peticiones y devuelve lo que el backend responda.
 */

/** Respuesta del backend ya interpretada. */
export type RespuestaApi<T> =
  | { ok: true; datos: T }
  | { ok: false; estado: number; detalle: string };

const MENSAJE_SIN_RESPUESTA =
  "No se pudo contactar la plataforma. Intenta de nuevo en un momento.";

async function interpretar<T>(respuesta: Response): Promise<RespuestaApi<T>> {
  if (respuesta.status === 204) {
    return { ok: true, datos: undefined as T };
  }

  let cuerpo: unknown = null;
  try {
    cuerpo = await respuesta.json();
  } catch {
    cuerpo = null;
  }

  if (respuesta.ok) {
    return { ok: true, datos: cuerpo as T };
  }

  const detalle =
    cuerpo && typeof cuerpo === "object" && "detalle" in cuerpo
      ? String((cuerpo as { detalle: unknown }).detalle)
      : MENSAJE_SIN_RESPUESTA;

  return { ok: false, estado: respuesta.status, detalle };
}

/** Llama al backend desde el navegador, enviando la cookie de sesión. */
export async function pedirApi<T>(
  ruta: string,
  opciones: { metodo?: string; cuerpo?: unknown } = {},
): Promise<RespuestaApi<T>> {
  const { metodo = "GET", cuerpo } = opciones;

  try {
    const respuesta = await fetch(`/api${ruta}`, {
      method: metodo,
      credentials: "same-origin",
      headers: cuerpo ? { "Content-Type": "application/json" } : undefined,
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
      cache: "no-store",
    });
    return await interpretar<T>(respuesta);
  } catch {
    return { ok: false, estado: 0, detalle: MENSAJE_SIN_RESPUESTA };
  }
}

/**
 * Llama al backend desde el servidor (componentes de servidor), trasladando
 * la cookie de sesión del usuario.
 */
export async function pedirApiEnServidor<T>(
  ruta: string,
  cookieDeSesion: string,
): Promise<RespuestaApi<T>> {
  const direccionDelBackend =
    process.env.VIDA_API_URL ?? "http://127.0.0.1:8000";

  try {
    const respuesta = await fetch(`${direccionDelBackend}${ruta}`, {
      headers: { Cookie: cookieDeSesion },
      cache: "no-store",
    });
    return await interpretar<T>(respuesta);
  } catch {
    return { ok: false, estado: 0, detalle: MENSAJE_SIN_RESPUESTA };
  }
}

/** Rol vigente del usuario, tal como lo informa el backend. */
export type Rol = "RO" | "ADMINISTRADOR";

export type Sesion = {
  identificacion: string;
  rol: Rol;
};
