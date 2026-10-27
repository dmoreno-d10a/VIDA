"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { pedirApi, type Sesion } from "@/lib/api";

/** Quién soy, con qué rol entré, y cómo salir (HU-4, RF-08). */
export function BarraDeSesion({ sesion }: { sesion: Sesion }) {
  const router = useRouter();
  const [saliendo, setSaliendo] = useState(false);

  const nombreDelRol = sesion.rol === "ADMINISTRADOR" ? "Administrador" : "RO";

  async function salir() {
    setSaliendo(true);
    await pedirApi("/acceso/salir", { metodo: "POST" });
    router.replace("/acceso");
  }

  return (
    <div className="sesion">
      <span className="identificacion">{sesion.identificacion}</span>
      <span className="rol" title="Rol con el que entraste">
        {nombreDelRol}
      </span>
      <button type="button" onClick={salir} disabled={saliendo}>
        {saliendo ? "Cerrando…" : "Cerrar sesión"}
      </button>
    </div>
  );
}
