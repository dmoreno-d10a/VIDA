import { cookies } from "next/headers";

import { pedirApiEnServidor, type Sesion } from "@/lib/api";

/**
 * Pantalla de entrada tras identificarse (HU-1, HU-2 de la 001; HU-5 de la 002).
 *
 * Aquí el RO ve qué puede documentar (RF-16). Cuando no hay ningún tipo
 * disponible se le dice **explícitamente** y se le dice qué hacer, en vez de
 * dejarle una sección vacía que parece una falla de la plataforma.
 */

type TipoDisponible = {
  id: number;
  nombre: string;
  descripcion: string | null;
};

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

  const disponibles = await pedirApiEnServidor<TipoDisponible[]>(
    "/tipos-de-documentacion-disponibles",
    cookieDeSesion,
  );
  const tipos = disponibles.ok ? disponibles.datos : [];

  return (
    <section className="inicio">
      <h1>Bienvenido a V.I.D.A.</h1>

      <h2>Qué puedes documentar</h2>
      {tipos.length === 0 ? (
        <p>
          Todavía no hay ningún tipo de documentación disponible. Solicítale al
          Administrador que registre los tipos que tu área necesita y les cargue
          su formato.
        </p>
      ) : (
        <>
          <p>
            Estos son los tipos de documentación que el Administrador tiene
            disponibles:
          </p>
          <ul className="tipos-disponibles">
            {tipos.map((tipo) => (
              <li key={tipo.id}>
                <strong>{tipo.nombre}</strong>
                {tipo.descripcion ? ` — ${tipo.descripcion}` : null}
              </li>
            ))}
          </ul>
          <p>
            Cargar la información de una actividad se habilita en la siguiente
            entrega.
          </p>
        </>
      )}

      <h2>Lo que puedes hacer con tu rol</h2>
      <ul>
        <li>Cambiar tu propia contraseña.</li>
        {rol === "ADMINISTRADOR" ? (
          <>
            <li>
              Administrar los usuarios de la plataforma: crearlos, cambiarles el
              rol, restablecerles la contraseña y revocarles el acceso.
            </li>
            <li>
              Administrar los tipos de documentación: crearlos, cargarles su
              formato, reemplazarlo y sacarlos de circulación.
            </li>
          </>
        ) : null}
      </ul>
    </section>
  );
}
