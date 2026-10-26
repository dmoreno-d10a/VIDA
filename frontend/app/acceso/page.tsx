"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { pedirApi, type Sesion } from "@/lib/api";

/**
 * Pantalla de identificación (HU-1).
 *
 * El mensaje de error es el que devuelve el backend, tal cual: es él quien
 * decide qué se puede contar. Cuatro de los cinco fallos comparten el mismo
 * texto, y el front no los distingue ni los adorna (RF-09).
 */
export default function Acceso() {
  const router = useRouter();
  const [identificacion, setIdentificacion] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function entrar(evento: React.FormEvent) {
    evento.preventDefault();
    setError(null);
    setEnviando(true);

    const respuesta = await pedirApi<Sesion>("/acceso/entrar", {
      metodo: "POST",
      cuerpo: { identificacion, contrasena },
    });

    setEnviando(false);

    if (!respuesta.ok) {
      setError(respuesta.detalle);
      setContrasena("");
      return;
    }

    router.replace("/inicio");
  }

  return (
    <main className="acceso">
      <h1>V.I.D.A.</h1>
      <p className="subtitulo">Vortexbird Intelligent Documentation Assistant</p>

      <form onSubmit={entrar} noValidate>
        <label htmlFor="identificacion">Identificación</label>
        <input
          id="identificacion"
          name="identificacion"
          type="text"
          autoComplete="username"
          value={identificacion}
          onChange={(e) => setIdentificacion(e.target.value)}
          required
        />

        <label htmlFor="contrasena">Contraseña</label>
        <input
          id="contrasena"
          name="contrasena"
          type="password"
          autoComplete="current-password"
          value={contrasena}
          onChange={(e) => setContrasena(e.target.value)}
          required
        />

        <button type="submit" disabled={enviando}>
          {enviando ? "Validando…" : "Entrar"}
        </button>
      </form>

      {error ? (
        <p role="alert" className="error">
          {error}
        </p>
      ) : null}
    </main>
  );
}
