import Link from "next/link";

import type { Rol } from "@/lib/api";

/**
 * Menú de opciones del rol (RF-04).
 *
 * Ocultar una opción aquí es comodidad, no seguridad: el backend niega igual
 * a quien la pida sin tener el rol (RF-05). Por eso este componente puede ser
 * así de simple.
 */
export function MenuPorRol({ rol }: { rol: Rol }) {
  return (
    <nav aria-label="Opciones disponibles">
      <ul>
        <li>
          <Link href="/inicio">Inicio</Link>
        </li>
        <li>
          <Link href="/perfil/contrasena">Cambiar mi contraseña</Link>
        </li>
        {rol === "ADMINISTRADOR" ? (
          <li>
            <Link href="/administracion/usuarios">Administrar usuarios</Link>
          </li>
        ) : null}
      </ul>
    </nav>
  );
}
