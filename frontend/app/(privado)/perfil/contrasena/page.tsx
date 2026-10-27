"use client";

import { useState } from "react";

import { pedirApi } from "@/lib/api";

/**
 * Cambio de la propia contraseña (HU-6, RF-17, RF-20).
 *
 * Cambiarla es decisión del usuario: esta pantalla se alcanza cuando él
 * quiere, y nada lo obliga a pasar por aquí. Cuando la contraseña nueva
 * incumple la política, se muestra la regla que falló tal como la informa el
 * backend, que es quien la aplica.
 */
export default function CambiarContrasena() {
  const [actual, setActual] = useState("");
  const [nueva, setNueva] = useState("");
  const [repetida, setRepetida] = useState("");
  const [aviso, setAviso] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function cambiar(evento: React.FormEvent) {
    evento.preventDefault();
    setAviso(null);
    setError(null);

    if (nueva !== repetida) {
      setError("La contraseña nueva y su repetición no coinciden.");
      return;
    }

    setEnviando(true);
    const respuesta = await pedirApi("/perfil/contrasena", {
      metodo: "PATCH",
      cuerpo: { contrasena_actual: actual, contrasena_nueva: nueva },
    });
    setEnviando(false);

    if (!respuesta.ok) {
      setError(respuesta.detalle);
      return;
    }

    setAviso("Tu contraseña quedó cambiada. La anterior ya no sirve.");
    setActual("");
    setNueva("");
    setRepetida("");
  }

  return (
    <section className="contrasena">
      <h1>Cambiar mi contraseña</h1>
      <p>
        Cambiarla es tu decisión: la plataforma no te obliga a hacerlo ni la
        vence por tiempo.
      </p>

      {aviso ? <p role="status" className="aviso">{aviso}</p> : null}
      {error ? <p role="alert" className="error">{error}</p> : null}

      <form onSubmit={cambiar}>
        <label htmlFor="actual">Contraseña actual</label>
        <input
          id="actual"
          type="password"
          autoComplete="current-password"
          value={actual}
          onChange={(e) => setActual(e.target.value)}
          required
        />

        <label htmlFor="nueva">Contraseña nueva</label>
        <input
          id="nueva"
          type="password"
          autoComplete="new-password"
          value={nueva}
          onChange={(e) => setNueva(e.target.value)}
          required
        />

        <label htmlFor="repetida">Repite la contraseña nueva</label>
        <input
          id="repetida"
          type="password"
          autoComplete="new-password"
          value={repetida}
          onChange={(e) => setRepetida(e.target.value)}
          required
        />

        <button type="submit" disabled={enviando}>
          {enviando ? "Cambiando…" : "Cambiar contraseña"}
        </button>
      </form>
    </section>
  );
}
