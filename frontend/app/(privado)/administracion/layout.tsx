import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { pedirApiEnServidor, type Sesion } from "@/lib/api";

/**
 * Capa de administración: solo el rol Administrador pasa de aquí (RF-05).
 *
 * El backend ya niega los datos a un RO, pero eso dejaba ver el cascarón de
 * la pantalla —título y formulario— a quien escribiera la dirección a mano.
 * La spec pide que no se muestre **ninguna** información de la opción, así
 * que aquí se decide antes de renderizar nada.
 *
 * El rol se le pregunta al backend: el front no lo deduce ni lo guarda.
 */
export default async function CapaDeAdministracion({
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

  if (respuesta.datos.rol !== "ADMINISTRADOR") {
    redirect("/inicio");
  }

  return <>{children}</>;
}
