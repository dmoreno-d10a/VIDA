import { NextResponse, type NextRequest } from "next/server";

/**
 * Sin cookie de sesión no se renderiza ninguna pantalla privada: se redirige
 * a la pantalla de acceso antes de producir HTML (RF-01, HU-3).
 *
 * Esto es comodidad, no seguridad: la barrera de verdad está en el backend,
 * que decide en cada petición (RF-05). Aquí solo se evita mostrar el cascarón
 * de una pantalla que después no tendría datos.
 */

const COOKIE_SESION = "vida_sesion";

/** Rutas que se pueden ver sin sesión. */
const RUTAS_PUBLICAS = ["/acceso"];

export function middleware(peticion: NextRequest) {
  const { pathname } = peticion.nextUrl;

  const esPublica = RUTAS_PUBLICAS.some(
    (ruta) => pathname === ruta || pathname.startsWith(`${ruta}/`),
  );
  const tieneCookie = peticion.cookies.has(COOKIE_SESION);

  if (!esPublica && !tieneCookie) {
    const destino = peticion.nextUrl.clone();
    destino.pathname = "/acceso";
    destino.search = "";
    return NextResponse.redirect(destino);
  }

  // Quien ya tiene sesión no necesita volver a la pantalla de acceso.
  if (esPublica && tieneCookie) {
    const destino = peticion.nextUrl.clone();
    destino.pathname = "/inicio";
    destino.search = "";
    return NextResponse.redirect(destino);
  }

  return NextResponse.next();
}

export const config = {
  // Todo menos las llamadas al backend y los archivos estáticos de Next.
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
