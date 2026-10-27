import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { BarraDeSesion } from "@/app/componentes/barra-de-sesion";
import { MenuPorRol } from "@/app/componentes/menu-por-rol";
import { pedirApiEnServidor, type Sesion } from "@/lib/api";

/**
 * Capa autenticada (HU-2, HU-4, RF-04, RF-08).
 *
 * El rol no se adivina ni se guarda en el navegador: se le pregunta al
 * backend en cada carga, y con eso se arma el menú. Si el backend dice que no
 * hay sesión válida —vencida, revocada o sin rol—, se vuelve a la pantalla de
 * acceso sin renderizar nada de la plataforma.
 */
export default async function CapaPrivada({
  children,
}: {
  children: React.ReactNode;
}) {
  const almacen = await cookies();
  const cookieDeSesion = almacen
    .getAll()
    .map((c) => `${c.name}=${c.value}`)
    .join("; ");

  const respuesta = await pedirApiEnServidor<Sesion>(
    "/acceso/sesion-actual",
    cookieDeSesion,
  );

  if (!respuesta.ok) {
    redirect("/acceso");
  }

  const sesion = respuesta.datos;

  return (
    <div className="plataforma">
      <header>
        <strong>V.I.D.A.</strong>
        <BarraDeSesion sesion={sesion} />
      </header>

      <MenuPorRol rol={sesion.rol} />

      <main>{children}</main>
    </div>
  );
}
