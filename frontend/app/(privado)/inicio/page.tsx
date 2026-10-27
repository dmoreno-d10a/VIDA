import { cookies } from "next/headers";

import { pedirApiEnServidor, type Sesion } from "@/lib/api";

/**
 * Pantalla de entrada tras identificarse (HU-1, HU-2).
 *
 * No muestra nada de las funcionalidades que todavía no existen: dice qué
 * puede hacer el rol hoy, y nada más.
 */
export default async function Inicio() {
  const almacen = await cookies();
  const cookieDeSesion = almacen
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ");

  const respuesta = await pedirApiEnServidor<Sesion>(
    "/acceso/sesion-actual",
    cookieDeSesion,
  );
  const rol = respuesta.ok ? respuesta.datos.rol : null;

  return (
    <section className="inicio">
      <h1>Bienvenido a V.I.D.A.</h1>
      <p>
        Esta es la base de acceso de la plataforma. Las funcionalidades de
        documentación se habilitan en las siguientes entregas.
      </p>

      <h2>Lo que puedes hacer con tu rol</h2>
      <ul>
        <li>Cambiar tu propia contraseña.</li>
        {rol === "ADMINISTRADOR" ? (
          <li>
            Administrar los usuarios de la plataforma: crearlos, cambiarles el
            rol, restablecerles la contraseña y revocarles el acceso.
          </li>
        ) : null}
      </ul>
    </section>
  );
}
